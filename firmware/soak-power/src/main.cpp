// soak-power -- the load half of #8, on XIAO-ESP32S3-cam + Sense-camera-board
// https://github.com/jwilleke/js-rocket-avionics/issues/8
//
// NOT FLIGHT FIRMWARE, and not a bring-up either -- run bringup-cam first and
// get four PASSes out of it. This project assumes the parts are known good and
// asks one question instead: what does the shared battery do when the camera is
// working, and does XIAO-ESP32S3-lora survive it.
//
// #8 exists because BOM.md accepts "a camera brownout on B can disturb A" in
// writing and nobody has ever seen it happen. The scope answer is better; this
// is what to run when the scope is not there, and it is worth running anyway
// because it logs for an hour and a scope trace does not.
//
// WHAT IT DOES
//   Drives the worst load the flight build can produce -- capture, then an SD
//   write burst, as fast as the card takes it -- and appends ONE CSV LINE PER
//   CYCLE to the card. The record is on the card rather than in RAM or on the
//   serial port precisely because the event being hunted is a reset.
//
// THE TRAP THAT WOULD WASTE THE SESSION
//   USB-C powers the board. A run with the monitor attached is a run on the
//   bench supply, and it measures nothing about the battery. Flash over USB,
//   UNPLUG, then run from the battery and read the card afterwards.
//
// WHAT COMES OUT
//   /soak-power.csv, one line per cycle plus a line per boot. Every boot line
//   carries esp_reset_reason(), so a brownout names itself: the ESP32-S3's own
//   detector fires before the CPU misbehaves, and ESP_RST_BROWNOUT in that
//   column is the observation #8 is missing. Count the boot lines, read the
//   last uptime before each, and the endurance question falls out of the same
//   file -- see the header comment in soak_open_log() for the columns.
//
// WIRING
//   Nothing is required beyond a card in the slot. The optional battery divider
//   -- see platformio.ini -- adds the voltage columns, which turn "it reset"
//   into "it reset at 3.1 V during a 42 ms write". Without it the reset is
//   still caught and still attributed; only the shape of the sag is missing.

#include <Arduino.h>
#include <esp_system.h>
#include "esp_camera.h"
#include "FS.h"
#include <SPI.h>
#include "SD.h"
#include <Preferences.h>

// ---- configuration, all overridable from platformio.ini --------------------
#ifndef SOAK_FRAMESIZE
#define SOAK_FRAMESIZE FRAMESIZE_SVGA   // matches bringup-cam. UXGA is harsher
#endif
#ifndef SOAK_PERIOD_MS
#define SOAK_PERIOD_MS 0                // 0 = flat out, which is the worst case
#endif
#ifndef SOAK_BEEP_EVERY
#define SOAK_BEEP_EVERY 0               // chirp every N cycles; 0 = silent
#endif

// Frames go round-robin into a fixed set of files. The write burst is the load;
// keeping every frame would only fill the card and stop the run early.
static const int   SOAK_FRAME_FILES = 16;
static const char *LOG_PATH = "/soak-power.csv";

// ---- pins, from docs/module-pinouts.md and bringup-cam ---------------------
static const int PIN_BUZZER = 1;                 // D0
// Sense microSD over SPI, CS on GPIO21 -- Seeed's wiring, proven by bringup-cam
// on 2026-09-12. SD_MMC 1-bit on 7/9/8 was never run and leaves CS to chance.
static const int SD_SCK = 7, SD_MISO = 8, SD_MOSI = 9, SD_CS = 21;

#define CAM_PIN_XCLK   10
#define CAM_PIN_SIOD   40
#define CAM_PIN_SIOC   39
#define CAM_PIN_D7     48
#define CAM_PIN_D6     11
#define CAM_PIN_D5     12
#define CAM_PIN_D4     14
#define CAM_PIN_D3     16
#define CAM_PIN_D2     18
#define CAM_PIN_D1     17
#define CAM_PIN_D0     15
#define CAM_PIN_VSYNC  38
#define CAM_PIN_HREF   47
#define CAM_PIN_PCLK   13

// ---- state that outlives a reset -------------------------------------------
// RTC memory survives a software reset and deep sleep. It may NOT survive a
// brownout, which is the case this firmware is built around -- so it is a
// convenience for the serial line, and the CSV on the card is the real record.
// Do not compute endurance from these; count boot lines in the file.
RTC_NOINIT_ATTR static uint32_t rtc_magic;
RTC_NOINIT_ATTR static uint32_t rtc_boots;
static const uint32_t RTC_MAGIC = 0x50575231;   // "PWR1"

// ---- reset history in NVS, independent of the card --------------------------
// Bench, 2026-09-12: a reset in the middle of a card write left the card
// unmountable until its power was cut. The event this project hunts is a reset,
// so the card cannot be the only record of it. Every boot appends its reset
// reason, and the uptime the previous boot reached, to a 32-entry ring in NVS;
// every boot prints the ring. Uptime is saved every 30 s -- ~120 NVS writes an
// hour, nothing against the flash's endurance.
static Preferences nvs;
struct BootRec { uint8_t reason; uint32_t prev_up_s; };
static const int HIST = 32;
static uint32_t last_up_save = 0;

static uint32_t boot_id  = 0;
static uint32_t cycle    = 0;
static bool     have_sd  = false;
static bool     have_cam = false;

// ---- optional battery sampling ---------------------------------------------
// A blocking SD write cannot sample its own supply, so when a divider is fitted
// a second task on the other core samples continuously and keeps a min/max
// window that the main loop drains once per cycle. That window is what catches
// inrush sag: an average across a cycle hides exactly the dip being looked for.
#ifdef SOAK_VBAT_PIN
static volatile int v_min_mv = INT32_MAX;
static volatile int v_max_mv = 0;

static int vbat_mv() {
  return (int)(analogReadMilliVolts(SOAK_VBAT_PIN) * (float)SOAK_VBAT_DIVIDER);
}

static void vbat_task(void *) {
  for (;;) {
    int mv = vbat_mv();
    if (mv < v_min_mv) v_min_mv = mv;
    if (mv > v_max_mv) v_max_mv = mv;
    vTaskDelay(1);                  // ~1 kHz, fast enough for an SD write burst
  }
}

// Returns the window and starts a fresh one.
static void vbat_window(int *lo, int *hi) {
  *lo = (v_min_mv == INT32_MAX) ? 0 : v_min_mv;
  *hi = v_max_mv;
  v_min_mv = INT32_MAX;
  v_max_mv = 0;
}
#endif

// ---- reset reason ----------------------------------------------------------
// ESP_RST_BROWNOUT is the whole point of this firmware. The others are here so
// that a reset which is NOT a brownout cannot be mistaken for one -- a panic
// caused by a bug in this file would otherwise read as evidence about the battery.
static const char *reset_name(esp_reset_reason_t r) {
  switch (r) {
    case ESP_RST_POWERON:  return "POWERON";
    case ESP_RST_EXT:      return "EXT";
    case ESP_RST_SW:       return "SW";
    case ESP_RST_PANIC:    return "PANIC";
    case ESP_RST_INT_WDT:  return "INT_WDT";
    case ESP_RST_TASK_WDT: return "TASK_WDT";
    case ESP_RST_WDT:      return "WDT";
    case ESP_RST_DEEPSLEEP:return "DEEPSLEEP";
    case ESP_RST_BROWNOUT: return "BROWNOUT";
    case ESP_RST_SDIO:     return "SDIO";
    default:               return "UNKNOWN";
  }
}

// ---- logging ---------------------------------------------------------------
// Opened and closed per line. A file held open across the run would lose its
// tail to the reset being measured, and the tail is the interesting part.
static void log_line(const String &line) {
  Serial.println(line);
  if (!have_sd) return;
  File f = SD.open(LOG_PATH, FILE_APPEND);
  if (!f) { have_sd = false; return; }
  f.println(line);
  f.close();
}

static void soak_open_log() {
  if (!have_sd) return;
  if (SD.exists(LOG_PATH)) return;
  File f = SD.open(LOG_PATH, FILE_WRITE);
  if (!f) { have_sd = false; return; }
  // boot      increments once per power-up or reset, from RTC memory when it
  //           survived; count the rows to get the true number
  // cycle     0 on a boot row, then 1.. for each capture+write
  // uptime_ms millis() at the row -- resets to 0 on every boot line
  // reset     esp_reset_reason() for this boot. BROWNOUT is the finding
  // vbat/vmin/vmax_mv  battery voltage, and the min/max seen across the cycle.
  //           Empty when no divider is fitted
  // cap_ms    esp_camera_fb_get()
  // write_ms  the SD burst alone -- this is where the current spike lives
  // bytes     JPEG size, so a degrading write rate can be read against it
  f.println(F("boot,cycle,uptime_ms,reset,vbat_mv,vmin_mv,vmax_mv,cap_ms,write_ms,bytes,heap,psram"));
  f.close();
}

// ---- buzzer ----------------------------------------------------------------
// An unmonitored run is silent, and silence and "dead" look identical. The
// chirp is also load, which is honest -- the flight build beeps on the same
// rail while the camera runs.
static void chirp() {
  ledcAttach(PIN_BUZZER, 3000, 10);
  ledcWrite(PIN_BUZZER, 512);
  delay(40);
  ledcWrite(PIN_BUZZER, 0);
  ledcDetach(PIN_BUZZER);
}

// ---- camera ----------------------------------------------------------------
static bool camera_start() {
  camera_config_t c = {};
  c.ledc_channel = LEDC_CHANNEL_0;
  c.ledc_timer   = LEDC_TIMER_0;
  c.pin_d0 = CAM_PIN_D0;  c.pin_d1 = CAM_PIN_D1;
  c.pin_d2 = CAM_PIN_D2;  c.pin_d3 = CAM_PIN_D3;
  c.pin_d4 = CAM_PIN_D4;  c.pin_d5 = CAM_PIN_D5;
  c.pin_d6 = CAM_PIN_D6;  c.pin_d7 = CAM_PIN_D7;
  c.pin_xclk  = CAM_PIN_XCLK;   c.pin_pclk = CAM_PIN_PCLK;
  c.pin_vsync = CAM_PIN_VSYNC;  c.pin_href = CAM_PIN_HREF;
  c.pin_sccb_sda = CAM_PIN_SIOD;
  c.pin_sccb_scl = CAM_PIN_SIOC;
  c.pin_pwdn = -1; c.pin_reset = -1;
  c.xclk_freq_hz = 20000000;
  c.frame_size   = SOAK_FRAMESIZE;
  c.pixel_format = PIXFORMAT_JPEG;
  c.grab_mode    = CAMERA_GRAB_WHEN_EMPTY;
  c.fb_location  = CAMERA_FB_IN_PSRAM;
  c.jpeg_quality = 12;
  c.fb_count     = 2;
  return esp_camera_init(&c) == ESP_OK;
}

void setup() {
  Serial.begin(115200);
  delay(1500);                       // USB CDC, when a monitor is attached

  esp_reset_reason_t why = esp_reset_reason();
  if (rtc_magic != RTC_MAGIC) {      // cold, or RTC memory did not survive
    rtc_magic = RTC_MAGIC;
    rtc_boots = 0;
  }
  boot_id = ++rtc_boots;

  // NVS history first -- before the card, which may not come back after a reset
  nvs.begin("soak", false);
  BootRec hist[HIST] = {};
  nvs.getBytes("hist", hist, sizeof hist);
  uint32_t head = nvs.getUInt("head", 0);
  uint32_t prev_up = nvs.getUInt("up_s", 0);
  hist[head % HIST] = { (uint8_t)why, prev_up };
  nvs.putBytes("hist", hist, sizeof hist);
  nvs.putUInt("head", head + 1);
  nvs.putUInt("up_s", 0);

  Serial.println(F("\n=== soak-power : shared-battery load test, #8 ==="));
  Serial.println(F("NVS reset history, oldest first (reason, uptime the boot before reached):"));
  for (uint32_t i = (head + 1 > HIST ? head + 1 - HIST : 0); i <= head; i++) {
    const BootRec &r = hist[i % HIST];
    Serial.printf("  #%-4u %-9s previous boot ran %u s\n", (unsigned)i,
                  reset_name((esp_reset_reason_t)r.reason), (unsigned)r.prev_up_s);
  }
  Serial.printf("reset reason %s, boot %u\n", reset_name(why), (unsigned)boot_id);
  if (why == ESP_RST_BROWNOUT) {
    Serial.println(F("*** BROWNOUT. That is the finding #8 is looking for. ***"));
  }
  Serial.println(F("USB-C powers the board -- a monitored run measures the bench,"));
  Serial.println(F("not the battery. Unplug and read /soak-power.csv afterwards."));

#ifdef SOAK_VBAT_PIN
  analogSetPinAttenuation(SOAK_VBAT_PIN, ADC_11db);   // full range to ~3.1 V in
  xTaskCreatePinnedToCore(vbat_task, "vbat", 2048, nullptr, 1, nullptr, 0);
#endif

  SPI.begin(SD_SCK, SD_MISO, SD_MOSI, SD_CS);
  // A card caught mid-write by a reset can refuse to mount for a while; retry
  // before giving up, and say so -- a run without the card is serial-only.
  for (int tries = 0; tries < 5 && !have_sd; tries++) {
    if (tries) { SD.end(); delay(1000); }
    have_sd = SD.begin(SD_CS, SPI, 20000000);   // 20 MHz: 475 KB/s on the bench; the 4 MHz default managed 123
  }
  if (!have_sd) {
    Serial.println(F("microSD did not mount -- serial only, so a reset loses"));
    Serial.println(F("the run. Fix the card before spending a charge on this."));
  }
  soak_open_log();

  have_cam = camera_start();
  if (!have_cam) {
    Serial.println(F("camera init failed -- is the Sense board seated? Without"));
    Serial.println(F("it there is no load, and no load means no test."));
  }

  int lo = 0, hi = 0, now_mv = 0;
#ifdef SOAK_VBAT_PIN
  now_mv = vbat_mv();
  vbat_window(&lo, &hi);
#endif
  String s = String(boot_id) + ",0," + String(millis()) + "," + reset_name(why) + ",";
#ifdef SOAK_VBAT_PIN
  s += String(now_mv) + "," + String(lo) + "," + String(hi);
#else
  s += ",,";
#endif
  s += ",,,," + String(ESP.getFreeHeap()) + "," + String(ESP.getFreePsram());
  log_line(s);
  if (prev_up) log_line("# previous boot ran " + String(prev_up) + " s before a " + reset_name(why) + " reset");
}

void loop() {
  if (!have_cam) { delay(5000); return; }

  uint32_t t0 = millis();
  camera_fb_t *fb = esp_camera_fb_get();
  uint32_t cap_ms = millis() - t0;
  if (!fb) { delay(100); return; }

  char path[24];
  snprintf(path, sizeof(path), "/soak-%02u.jpg",
           (unsigned)(cycle % SOAK_FRAME_FILES));

  uint32_t t1 = millis();
  size_t wrote = 0;
  if (have_sd) {
    File f = SD.open(path, FILE_WRITE);
    if (f) { wrote = f.write(fb->buf, fb->len); f.close(); }
  }
  uint32_t write_ms = millis() - t1;
  size_t len = fb->len;
  esp_camera_fb_return(fb);

  cycle++;
  if (millis() - last_up_save >= 30000) {       // uptime for the next boot to report
    last_up_save = millis();
    nvs.putUInt("up_s", millis() / 1000);
  }

  int lo = 0, hi = 0, now_mv = 0;
#ifdef SOAK_VBAT_PIN
  now_mv = vbat_mv();
  vbat_window(&lo, &hi);
#endif

  String s = String(boot_id) + "," + String(cycle) + "," + String(millis()) + ",,";
#ifdef SOAK_VBAT_PIN
  s += String(now_mv) + "," + String(lo) + "," + String(hi);
#else
  s += ",,";
#endif
  s += "," + String(cap_ms) + "," + String(write_ms) + "," + String((unsigned)len)
     + "," + String(ESP.getFreeHeap()) + "," + String(ESP.getFreePsram());
  log_line(s);

  if (have_sd && wrote != len) {
    Serial.printf("short write: %u of %u bytes -- card or rail\n",
                  (unsigned)wrote, (unsigned)len);
  }

#if SOAK_BEEP_EVERY > 0
  if (cycle % SOAK_BEEP_EVERY == 0) chirp();
#endif

#if SOAK_PERIOD_MS > 0
  uint32_t spent = millis() - t0;
  if (spent < SOAK_PERIOD_MS) delay(SOAK_PERIOD_MS - spent);
#endif
}
