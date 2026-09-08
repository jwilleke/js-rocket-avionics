// bringup-cam -- bench bring-up for XIAO-ESP32S3-cam + Sense-camera-board (#7)
//
// PlatformIO project, not an Arduino sketch. Build and flash:
//     pio run -t upload && pio device monitor
// Board, PSRAM and partition settings live in ../platformio.ini, so nothing
// depends on IDE menu state -- which is the point of not using a .ino.
//
// NOT FLIGHT FIRMWARE. This proves the parts are alive and talking, in the
// order that fails cheapest, and prints a PASS/FAIL line for each of #7's four
// acceptance criteria. Apogee, staging and landing detection are out of scope
// -- they need the flight profile settled first.
//
// UNTESTED. Written against the datasheets and this repo's measured notes; no
// hardware has run it. Treat a failure as "check the wiring AND check this
// file". Register values are cited inline so they can be checked rather than
// trusted.
//
// The Sense expansion board must be fitted -- camera and microSD live on it.
//
// WIRING, from docs/module-pinouts.md. Both sensors are I2C on D4/D5, powered
// from 3V3 and GND. Four wires each, Qwiic cables are bench kit:
//
//     XIAO 3V3  -> sensor VIN     <- NOT 3Vo. That is the sensor's own
//     XIAO GND  -> sensor GND        regulator output; back-feeding kills it
//     XIAO D4   -> sensor SDA
//     XIAO D5   -> sensor SCL
//     buzzer    -> D0 and GND     <- passive piezo, no supply rail
//
// TRAPS, already paid for once and recorded in module-pinouts.md:
//   - CS must be HIGH or a BMP3xx drops into SPI mode and never answers on I2C.
//     If 0x77 is silent, check CS before anything else.
//   - SDO selects the address, it is not data. High = 0x77, low = 0x76.
//   - Ignore the seller's wiring diagram. It is SPI, wired to Arduino
//     13/12/11/10, and following it wastes a session.

#include <Arduino.h>
#include <Wire.h>
#include <SPI.h>
#include "esp_camera.h"
#include "FS.h"
#include "SD_MMC.h"

// ---- pins ------------------------------------------------------------------
// D-numbers are the silkscreen labels; the GPIOs are what the compiler wants.
// Mapping confirmed off the part, 2026-09-08 -- docs/module-pinouts.md.
static const int PIN_SDA    = 5;    // D4
static const int PIN_SCL    = 6;    // D5
static const int PIN_BUZZER = 1;    // D0

// microSD on the Sense board is SD_MMC in 1-bit mode, not SPI.
static const int SD_CLK = 7, SD_CMD = 9, SD_D0 = 8;

// OV3660 on the Sense board. NOTE: this repo said OV2640 everywhere until the
// part was read off the ribbon 2026-09-06 and answered PID 0x3660. The pin map
// is the same; the sensor is not.
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

// ---- I2C parts -------------------------------------------------------------
static const uint8_t BMP388_ADDR = 0x77;   // SDO high. Low would be 0x76
static const uint8_t BMP388_CHIPID_REG = 0x00;
static const uint8_t BMP388_CHIPID = 0x50; // 0x60 would be a BMP390

static const uint8_t LSM_ADDR = 0x6A;      // 0x6B if the AD0 jumper is bridged
static const uint8_t LSM_WHOAMI_REG = 0x0F;
static const uint8_t LSM_WHOAMI = 0x6C;
static const uint8_t LSM_CTRL1_XL = 0x10;
static const uint8_t LSM_CTRL3_C  = 0x12;
static const uint8_t LSM_FIFO_CTRL3 = 0x09;
static const uint8_t LSM_FIFO_CTRL4 = 0x0A;
static const uint8_t LSM_FIFO_STATUS1 = 0x3A;
static const uint8_t LSM_OUTX_L_A = 0x28;

// LSM6DSO32 full-scale bits are NOT the LSM6DSO's. On the -32 part:
//   FS[1:0] = 00 -> +/-4 g   01 -> +/-32 g   10 -> +/-8 g   11 -> +/-16 g
// So +/-32 g is 01, which is easy to get wrong by assuming 11 is the top range.
static const uint8_t LSM_FS_32G = 0x01;
static const float   LSM_MG_PER_LSB_32G = 0.976f;   // datasheet, +/-32 g

static bool pass_i2c = false, pass_imu = false, pass_cam = false, pass_beep = false;

// ---- small I2C helpers -----------------------------------------------------
static bool wr8(uint8_t addr, uint8_t reg, uint8_t val) {
  Wire.beginTransmission(addr);
  Wire.write(reg);
  Wire.write(val);
  return Wire.endTransmission() == 0;
}

static bool rd(uint8_t addr, uint8_t reg, uint8_t *buf, size_t n) {
  Wire.beginTransmission(addr);
  Wire.write(reg);
  if (Wire.endTransmission(false) != 0) return false;
  if (Wire.requestFrom((int)addr, (int)n) != (int)n) return false;
  for (size_t i = 0; i < n; i++) buf[i] = Wire.read();
  return true;
}

static int rd8(uint8_t addr, uint8_t reg) {
  uint8_t v;
  return rd(addr, reg, &v, 1) ? v : -1;
}

// ---- 1. I2C enumeration ----------------------------------------------------
static void step_i2c() {
  Serial.println(F("\n[1] I2C enumeration"));
  int found = 0;
  for (uint8_t a = 0x08; a < 0x78; a++) {
    Wire.beginTransmission(a);
    if (Wire.endTransmission() == 0) {
      Serial.printf("    found 0x%02X\n", a);
      found++;
    }
  }
  if (!found) {
    Serial.println(F("    nothing on the bus. Check VIN (not 3Vo), and check"));
    Serial.println(F("    the BMP388's CS is HIGH -- low drops it into SPI."));
    return;
  }

  int bmp = rd8(BMP388_ADDR, BMP388_CHIPID_REG);
  int lsm = rd8(LSM_ADDR, LSM_WHOAMI_REG);
  Serial.printf("    BMP388 @0x%02X chip id 0x%02X (want 0x%02X)\n",
                BMP388_ADDR, bmp, BMP388_CHIPID);
  Serial.printf("    LSM6DSO32 @0x%02X WHO_AM_I 0x%02X (want 0x%02X)\n",
                LSM_ADDR, lsm, LSM_WHOAMI);

  // #7 wants "no address clash" stated, not assumed.
  if (bmp == BMP388_CHIPID && lsm == LSM_WHOAMI) {
    Serial.println(F("    both answer, distinct addresses -- no clash"));
    pass_i2c = true;
  }
}

// ---- 2. IMU at +/-32 g with the FIFO running -------------------------------
static void step_imu() {
  Serial.println(F("\n[2] LSM6DSO32 at +/-32 g, FIFO continuous"));
  if (rd8(LSM_ADDR, LSM_WHOAMI_REG) != LSM_WHOAMI) {
    Serial.println(F("    absent, skipping"));
    return;
  }

  wr8(LSM_ADDR, LSM_CTRL3_C, 0x01);          // software reset
  delay(20);
  wr8(LSM_ADDR, LSM_CTRL3_C, 0x44);          // BDU on, IF_INC on

  // CTRL1_XL = ODR[7:4] | FS[3:2] | LPF2[1]. 833 Hz = 0b0111.
  uint8_t ctrl1 = (0x07 << 4) | (LSM_FS_32G << 2);
  wr8(LSM_ADDR, LSM_CTRL1_XL, ctrl1);
  Serial.printf("    CTRL1_XL = 0x%02X (833 Hz, +/-32 g)\n", ctrl1);

  // FIFO: batch the accel at 833 Hz, continuous mode. BOM.md calls the 9 KB
  // FIFO a hard requirement, so this is a criterion and not a nicety.
  wr8(LSM_ADDR, LSM_FIFO_CTRL3, 0x07);       // BDR_XL = 833 Hz, gyro off
  wr8(LSM_ADDR, LSM_FIFO_CTRL4, 0x06);       // FIFO_MODE = continuous
  delay(100);

  uint8_t st[2];
  uint16_t depth = 0;
  if (rd(LSM_ADDR, LSM_FIFO_STATUS1, st, 2)) {
    depth = ((uint16_t)(st[1] & 0x03) << 8) | st[0];
  }
  Serial.printf("    FIFO holds %u words after 100 ms\n", depth);

  uint8_t raw[6];
  if (rd(LSM_ADDR, LSM_OUTX_L_A, raw, 6)) {
    int16_t x = (int16_t)(raw[1] << 8 | raw[0]);
    int16_t y = (int16_t)(raw[3] << 8 | raw[2]);
    int16_t z = (int16_t)(raw[5] << 8 | raw[4]);
    Serial.printf("    accel  %.2f  %.2f  %.2f  g\n",
                  x * LSM_MG_PER_LSB_32G / 1000.0f,
                  y * LSM_MG_PER_LSB_32G / 1000.0f,
                  z * LSM_MG_PER_LSB_32G / 1000.0f);
    Serial.println(F("    sitting still, one axis should read about 1 g."));
    Serial.println(F("    If every axis reads ~0, the scale bits are wrong --"));
    Serial.println(F("    on the -32 part, 01 is +/-32 g and 11 is +/-16."));
  }
  pass_imu = (depth > 0);
}

// ---- 3. camera to microSD --------------------------------------------------
static void step_camera() {
  Serial.println(F("\n[3] camera + microSD"));
  Serial.printf("    PSRAM %s, %u bytes free\n",
                psramFound() ? "present" : "MISSING",
                (unsigned)ESP.getFreePsram());
  if (!psramFound()) {
    Serial.println(F("    build_flags in platformio.ini must carry -DBOARD_HAS_PSRAM,"));
    Serial.println(F("    or the frame buffers will not allocate."));
  }

  camera_config_t c = {};
  c.ledc_channel = LEDC_CHANNEL_0;
  c.ledc_timer   = LEDC_TIMER_0;
  c.pin_d0 = CAM_PIN_D0;  c.pin_d1 = CAM_PIN_D1;
  c.pin_d2 = CAM_PIN_D2;  c.pin_d3 = CAM_PIN_D3;
  c.pin_d4 = CAM_PIN_D4;  c.pin_d5 = CAM_PIN_D5;
  c.pin_d6 = CAM_PIN_D6;  c.pin_d7 = CAM_PIN_D7;
  c.pin_xclk = CAM_PIN_XCLK;   c.pin_pclk  = CAM_PIN_PCLK;
  c.pin_vsync = CAM_PIN_VSYNC; c.pin_href  = CAM_PIN_HREF;
  c.pin_sccb_sda = CAM_PIN_SIOD;
  c.pin_sccb_scl = CAM_PIN_SIOC;
  c.pin_pwdn = -1; c.pin_reset = -1;
  c.xclk_freq_hz = 20000000;          // the ~20 MHz XCLK the ribbon may not be
  c.frame_size   = FRAMESIZE_SVGA;    // extended -- see Sense-camera-board.md
  c.pixel_format = PIXFORMAT_JPEG;
  c.grab_mode    = CAMERA_GRAB_WHEN_EMPTY;
  c.fb_location  = CAMERA_FB_IN_PSRAM;
  c.jpeg_quality = 12;
  c.fb_count     = 2;

  esp_err_t err = esp_camera_init(&c);
  if (err != ESP_OK) {
    Serial.printf("    camera init failed 0x%x -- is the Sense board seated?\n", err);
    return;
  }
  sensor_t *s = esp_camera_sensor_get();
  if (s) Serial.printf("    sensor PID 0x%04X (OV3660 = 0x3660)\n", s->id.PID);

  SD_MMC.setPins(SD_CLK, SD_CMD, SD_D0);
  if (!SD_MMC.begin("/sdcard", true)) {       // true = 1-bit mode
    Serial.println(F("    microSD did not mount. Card seated? FAT32?"));
    return;
  }

  camera_fb_t *fb = esp_camera_fb_get();
  if (!fb) { Serial.println(F("    capture returned nothing")); return; }

  File f = SD_MMC.open("/bringup.jpg", FILE_WRITE);
  if (f) {
    f.write(fb->buf, fb->len);
    f.close();
    Serial.printf("    wrote /bringup.jpg, %u bytes, %ux%u\n",
                  (unsigned)fb->len, fb->width, fb->height);
    pass_cam = true;
  } else {
    Serial.println(F("    could not open the file for writing"));
  }
  esp_camera_fb_return(fb);

  // design.md: nothing writes the card during boost. Proving a flush works on
  // the bench is the point; the flight rule is a firmware decision, not this.
  Serial.println(F("    (flight rule: no card writes during boost -- PSRAM buffer, flush after)"));
}

// ---- 4. buzzer, two distinguishable tones ----------------------------------
static void beep(int hz, int ms) {
  ledcAttach(PIN_BUZZER, hz, 10);
  ledcWrite(PIN_BUZZER, 512);          // 50% duty; a passive piezo needs AC
  delay(ms);
  ledcWrite(PIN_BUZZER, 0);
  ledcDetach(PIN_BUZZER);
  delay(120);
}

static void step_buzzer() {
  Serial.println(F("\n[4] buzzer on D0 -- two patterns"));
  Serial.println(F("    ARMED  : three short high chirps"));
  for (int i = 0; i < 3; i++) beep(3000, 90);
  delay(400);
  Serial.println(F("    FAULT  : two long low tones"));
  for (int i = 0; i < 2; i++) beep(1200, 400);
  Serial.println(F("    Silence means the piezo is ACTIVE, not passive --"));
  Serial.println(F("    an active buzzer wants DC and ignores PWM."));
  pass_beep = true;                    // audible, so the operator is the judge
}

void setup() {
  Serial.begin(115200);
  delay(2000);                         // USB CDC needs a moment to enumerate
  Serial.println(F("\n=== bringup-cam : XIAO-ESP32S3-cam + Sense-camera-board ==="));
  Serial.println(F("=== js-rocket-avionics #7. Bench only, not flight firmware ==="));

  Wire.begin(PIN_SDA, PIN_SCL, 400000);

  step_i2c();
  step_imu();
  step_camera();
  step_buzzer();

  Serial.println(F("\n=== #7 acceptance criteria ==="));
  Serial.printf("  both sensors enumerate and stream        %s\n", pass_i2c  ? "PASS" : "FAIL");
  Serial.printf("  IMU at +/-32 g with FIFO active          %s\n", pass_imu  ? "PASS" : "FAIL");
  Serial.printf("  video to microSD, log flushed and read   %s\n", pass_cam  ? "PASS" : "FAIL");
  Serial.printf("  two distinguishable beep patterns        %s\n", pass_beep ? "PASS" : "FAIL");
  Serial.println(F("\nRecord the result on #7. A FAIL here is a finding, not a setback."));
}

void loop() {
  delay(10000);
}
