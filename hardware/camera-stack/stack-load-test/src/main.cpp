// stack-load-test -- XIAO-ESP32S3-cam (mj-cam) + Sense board at flight load
//
//     pio run -t upload && pio device monitor
//
// bringup-cam proved each part alone. In flight they run together, and
// design.md's Verification item 4 asks the question this answers: with the
// camera recording to the card, does the sampler drop anything?
//
// For TEST_SECONDS, three tasks run at once:
//   core 1  IMU  -- LSM6DSO32 accel AND gyro at 833 Hz into its FIFO (a worst
//                   case: flight wants ~500 Hz), drained into a PSRAM log, plus
//                   the BMP388 read at 25 Hz on the same bus
//   core 0  cam  -- 800x600 JPEG frames into a queue of FB_COUNT PSRAM buffers
//   core 0  sd   -- drains the queue to /stack.mjpeg, SD over SPI at 20 MHz
// Then, as a flight would after landing, the IMU and baro logs are flushed to
// the card and the IMU log read back.
//
// What counts:
//   IMU  -- FIFO overrun is the definitive "samples lost"; bad tags and bus
//           errors are the other two ways data goes missing. Max FIFO depth
//           says how close it came
//   video -- the largest gap between consecutive frames' capture timestamps
//           (a stall long enough to empty the queue shows up here), and the
//           worst single card write
//
// Not flight firmware. Ran 2026-09-12, 60 s: zero dropped IMU samples, 4.8% of
// frames dropped on purpose, worst card stall 1 191 ms -- camera-stack.md.

#include <Arduino.h>
#include <Wire.h>
#include <SPI.h>
#include "SD.h"
#include "esp_camera.h"

#ifndef TEST_SECONDS
#define TEST_SECONDS 20
#endif
#ifndef FB_COUNT
#define FB_COUNT 16
#endif

static const char *DEVICE_NAME = "mj-cam";

// ---- pins: as bringup-cam, confirmed on the part (module-pinouts.md) --------
static const int PIN_SDA = 5, PIN_SCL = 6;                       // D4, D5
static const int SD_SCK = 7, SD_MISO = 8, SD_MOSI = 9, SD_CS = 21;
static const uint32_t SD_HZ = 20000000;                          // microSD.md
#define CAM_PIN_XCLK 10
#define CAM_PIN_SIOD 40
#define CAM_PIN_SIOC 39
#define CAM_PIN_D7 48
#define CAM_PIN_D6 11
#define CAM_PIN_D5 12
#define CAM_PIN_D4 14
#define CAM_PIN_D3 16
#define CAM_PIN_D2 18
#define CAM_PIN_D1 17
#define CAM_PIN_D0 15
#define CAM_PIN_VSYNC 38
#define CAM_PIN_HREF 47
#define CAM_PIN_PCLK 13

// ---- sensors ---------------------------------------------------------------
static const uint8_t LSM = 0x6A, BMP = 0x77;
// LSM6DSO32: CTRL1_XL 0x74 = 833 Hz, FS 01 = +/-32 g (NOT the LSM6DSO's code).
// CTRL2_G 0x7C = 833 Hz, 2000 dps. FIFO_CTRL3 0x77 = batch both at 833 Hz.
static const uint8_t LSM_CTRL1_XL = 0x10, LSM_CTRL2_G = 0x11, LSM_CTRL3_C = 0x12;
static const uint8_t LSM_FIFO_CTRL3 = 0x09, LSM_FIFO_CTRL4 = 0x0A;
static const uint8_t LSM_FIFO_STATUS1 = 0x3A, LSM_FIFO_OUT = 0x78;
static const uint8_t TAG_GYRO = 0x01, TAG_ACCEL = 0x02;          // TAG_SENSOR[7:3]
// BMP388: PWR_CTRL 0x1B = 0x33 (press + temp, normal mode), ODR 0x1D = 0x02
// (50 Hz), data 0x04..0x09 = press[3] temp[3].
static const uint8_t BMP_PWR_CTRL = 0x1B, BMP_OSR = 0x1C, BMP_ODR = 0x1D, BMP_DATA = 0x04;

static bool wr8(uint8_t a, uint8_t r, uint8_t v) {
  Wire.beginTransmission(a); Wire.write(r); Wire.write(v);
  return Wire.endTransmission() == 0;
}
static bool rd(uint8_t a, uint8_t r, uint8_t *b, size_t n) {
  Wire.beginTransmission(a); Wire.write(r);
  if (Wire.endTransmission(false) != 0) return false;
  if (Wire.requestFrom((int)a, (int)n) != (int)n) return false;
  for (size_t i = 0; i < n; i++) b[i] = Wire.read();
  return true;
}

// ---- shared state: each counter has one writer, so plain globals; flags volatile
static volatile bool running = false, imuDone = false, camDone = false, sdDone = false;

static uint8_t *imuBuf, *baroBuf;
static size_t imuCap, imuUsed, baroCap, baroUsed;
static uint32_t nAccel, nGyro, badTag, i2cErr, fifoMax, loopMaxUs, baroReads;
static volatile bool overrun = false, imuFull = false;

static QueueHandle_t frameQ;
static File vid;
static uint32_t framesCap, framesWritten, framesQFull, writeErr, qMax, gapMaxMs, wMaxUs;
static uint64_t wSumUs, bytesVid;

// ---- tasks -----------------------------------------------------------------
static void imuTask(void *) {
  uint32_t last = micros(), nextBaro = millis();
  while (running) {
    uint32_t now = micros();
    if (now - last > loopMaxUs) loopMaxUs = now - last;
    last = now;
    uint8_t st[2];
    if (!rd(LSM, LSM_FIFO_STATUS1, st, 2)) { i2cErr++; continue; }
    if (st[1] & 0x48) overrun = true;              // FIFO_OVR_IA | OVR_LATCHED
    uint16_t n = ((uint16_t)(st[1] & 0x03) << 8) | st[0];
    if (n > fifoMax) fifoMax = n;
    while (n--) {
      if (imuUsed + 7 > imuCap) { imuFull = true; break; }
      if (!rd(LSM, LSM_FIFO_OUT, imuBuf + imuUsed, 7)) { i2cErr++; break; }
      uint8_t tag = imuBuf[imuUsed] >> 3;
      if (tag == TAG_ACCEL) nAccel++; else if (tag == TAG_GYRO) nGyro++; else badTag++;
      imuUsed += 7;
    }
    if ((int32_t)(millis() - nextBaro) >= 0 && baroUsed + 10 <= baroCap) {
      nextBaro += 40;                                // 25 Hz
      uint32_t t = millis();
      memcpy(baroBuf + baroUsed, &t, 4);
      if (rd(BMP, BMP_DATA, baroBuf + baroUsed + 4, 6)) { baroUsed += 10; baroReads++; }
      else i2cErr++;
    }
    vTaskDelay(1);                                   // 1 ms: let the FIFO fill, yield
  }
  imuDone = true;
  vTaskDelete(NULL);
}

static void camTask(void *) {
  int64_t lastUs = 0;
  while (running) {
    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) { vTaskDelay(1); continue; }
    int64_t us = (int64_t)fb->timestamp.tv_sec * 1000000 + fb->timestamp.tv_usec;
    if (lastUs) {
      uint32_t gap = (uint32_t)((us - lastUs) / 1000);
      if (gap > gapMaxMs) gapMaxMs = gap;
    }
    lastUs = us;
    framesCap++;
    if (xQueueSend(frameQ, &fb, 0) != pdTRUE) { esp_camera_fb_return(fb); framesQFull++; }  // dropped
    UBaseType_t d = uxQueueMessagesWaiting(frameQ);
    if (d > qMax) qMax = d;
  }
  camDone = true;
  vTaskDelete(NULL);
}

static void sdTask(void *) {
  camera_fb_t *fb;
  while (running || uxQueueMessagesWaiting(frameQ)) {
    if (xQueueReceive(frameQ, &fb, pdMS_TO_TICKS(50)) != pdTRUE) continue;
    uint32_t t0 = micros();
    size_t n = vid.write(fb->buf, fb->len);
    uint32_t w = micros() - t0;
    size_t len = fb->len;
    esp_camera_fb_return(fb);
    if (n != len) { writeErr++; continue; }
    framesWritten++; bytesVid += n; wSumUs += w;
    if (w > wMaxUs) wMaxUs = w;
    // Yield every frame. Draining a backlog back-to-back starved IDLE0 for 5 s
    // and the task watchdog reset the board (2026-09-12) -- which in flight
    // would erase the PSRAM log. The recorder (#24) needs the same rule.
    vTaskDelay(1);
  }
  sdDone = true;
  vTaskDelete(NULL);
}

// ---- setup -----------------------------------------------------------------
static bool fail(const char *why) { Serial.printf("  SETUP FAILED: %s\n", why); return false; }

static bool setupAll() {
  Wire.begin(PIN_SDA, PIN_SCL, 400000);
  uint8_t id = 0;
  if (!rd(LSM, 0x0F, &id, 1) || id != 0x6C) return fail("LSM6DSO32 not at 0x6A (WHO_AM_I 0x6C)");
  if (!rd(BMP, 0x00, &id, 1) || id != 0x50) return fail("BMP388 not at 0x77 (chip id 0x50)");

  wr8(LSM, LSM_CTRL3_C, 0x01); delay(20);            // software reset
  wr8(LSM, LSM_CTRL3_C, 0x44);                       // BDU, IF_INC
  wr8(LSM, LSM_CTRL1_XL, 0x74);
  wr8(LSM, LSM_CTRL2_G, 0x7C);
  wr8(LSM, LSM_FIFO_CTRL3, 0x77);
  wr8(LSM, LSM_FIFO_CTRL4, 0x00);                    // bypass: empty it
  wr8(BMP, BMP_OSR, 0x00);
  wr8(BMP, BMP_ODR, 0x02);
  wr8(BMP, BMP_PWR_CTRL, 0x33);

  if (!psramFound()) return fail("no PSRAM -- build_flags must carry -DBOARD_HAS_PSRAM");
  imuCap = 2 * 1024 * 1024;  imuBuf = (uint8_t *)ps_malloc(imuCap);
  baroCap = 64 * 1024;       baroBuf = (uint8_t *)ps_malloc(baroCap);
  if (!imuBuf || !baroBuf) return fail("ps_malloc for the logs");

  camera_config_t c = {};
  c.ledc_channel = LEDC_CHANNEL_0; c.ledc_timer = LEDC_TIMER_0;
  c.pin_d0 = CAM_PIN_D0; c.pin_d1 = CAM_PIN_D1; c.pin_d2 = CAM_PIN_D2; c.pin_d3 = CAM_PIN_D3;
  c.pin_d4 = CAM_PIN_D4; c.pin_d5 = CAM_PIN_D5; c.pin_d6 = CAM_PIN_D6; c.pin_d7 = CAM_PIN_D7;
  c.pin_xclk = CAM_PIN_XCLK; c.pin_pclk = CAM_PIN_PCLK;
  c.pin_vsync = CAM_PIN_VSYNC; c.pin_href = CAM_PIN_HREF;
  c.pin_sccb_sda = CAM_PIN_SIOD; c.pin_sccb_scl = CAM_PIN_SIOC;
  c.pin_pwdn = -1; c.pin_reset = -1;
  c.xclk_freq_hz = 20000000;
  c.frame_size = FRAMESIZE_SVGA;
  c.pixel_format = PIXFORMAT_JPEG;
  c.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
  c.fb_location = CAMERA_FB_IN_PSRAM;
  c.jpeg_quality = 12;
  c.fb_count = FB_COUNT;
  if (esp_camera_init(&c) != ESP_OK) return fail("camera init -- Sense board seated?");

  SPI.begin(SD_SCK, SD_MISO, SD_MOSI, SD_CS);
  if (!SD.begin(SD_CS, SPI, SD_HZ)) return fail("microSD did not mount");
  vid = SD.open("/stack.mjpeg", FILE_WRITE);
  if (!vid) return fail("could not open /stack.mjpeg");

  // The queue holds at most FB_COUNT - 2 frames, so the camera driver always has
  // two buffers to fill. Holding all of them starved its cam_task, which spun
  // on FB-OVF until the task watchdog reset the board (2026-09-12). When the
  // card falls behind, frames are dropped on purpose and counted -- a gap in
  // the video, not a reset that erases the PSRAM log.
  frameQ = xQueueCreate(FB_COUNT - 2, sizeof(camera_fb_t *));
  return frameQ != nullptr;
}

static uint32_t flush(const char *path, const uint8_t *buf, size_t n, bool verify) {
  File f = SD.open(path, FILE_WRITE);
  if (!f) { Serial.printf("    could not open %s\n", path); return 0; }
  uint32_t t0 = millis(); size_t w = f.write(buf, n); f.close();
  uint32_t ms = millis() - t0;
  Serial.printf("    %s: %u bytes in %u ms\n", path, (unsigned)w, (unsigned)ms);
  if (verify) {
    f = SD.open(path, FILE_READ);
    static uint8_t chunk[4096]; size_t got = 0, same = 0;
    while (f && got < n) {
      size_t r = f.read(chunk, sizeof chunk); if (!r) break;
      for (size_t i = 0; i < r && got + i < n; i++) same += chunk[i] == buf[got + i];
      got += r;
    }
    if (f) f.close();
    Serial.printf("    read back %u bytes, %u match\n", (unsigned)got, (unsigned)same);
    return same == n && w == n;
  }
  return w == n;
}

void setup() {
  Serial.begin(115200);
  delay(2000);
  Serial.printf("\n=== %s -- stack-load-test: everything at once for %d s, %d frame buffers ===\n",
                DEVICE_NAME, TEST_SECONDS, FB_COUNT);
  if (!setupAll()) return;

  running = true;
  wr8(LSM, LSM_FIFO_CTRL4, 0x06);                    // continuous: sampling starts now
  uint32_t t0 = millis();
  xTaskCreatePinnedToCore(imuTask, "imu", 4096, nullptr, 5, nullptr, 1);
  xTaskCreatePinnedToCore(camTask, "cam", 4096, nullptr, 4, nullptr, 0);
  xTaskCreatePinnedToCore(sdTask,  "sd",  8192, nullptr, 3, nullptr, 0);

  for (int s = 5; s <= TEST_SECONDS; s += 5) {
    delay(5000);
    Serial.printf("  %2d s  imu %u+%u words  frames %u captured %u written  fifo max %u\n",
                  s, nAccel, nGyro, framesCap, framesWritten, fifoMax);
  }
  running = false;
  float secs = (millis() - t0) / 1000.0f;           // the run itself, not the drain after
  while (!(imuDone && camDone && sdDone)) delay(10);
  vid.close();

  Serial.println(F("\n[IMU] LSM6DSO32 accel + gyro at 833 Hz, BMP388 at 25 Hz, while recording"));
  Serial.printf("    accel %u = %.0f Hz, gyro %u = %.0f Hz (bench alone: 816 Hz)\n",
                nAccel, nAccel / secs, nGyro, nGyro / secs);
  Serial.printf("    FIFO overrun %s, bad tags %u, bus errors %u, log full %s\n",
                overrun ? "YES -- SAMPLES LOST" : "no", badTag, i2cErr, imuFull ? "YES" : "no");
  Serial.printf("    FIFO max depth %u words; slowest loop %.1f ms\n", fifoMax, loopMaxUs / 1000.0f);
  Serial.printf("    baro reads %u = %.1f Hz\n", baroReads, baroReads / secs);

  Serial.println(F("\n[VIDEO] 800x600 JPEG to /stack.mjpeg"));
  Serial.printf("    %u captured, %u written = %.1f fps, %.0f KB/s; dropped (queue full) %u, write errors %u\n",
                framesCap, framesWritten, framesWritten / secs, bytesVid / 1024.0 / secs, framesQFull, writeErr);
  Serial.printf("    queue max %u of %d; largest frame gap %u ms\n", qMax, FB_COUNT - 2, gapMaxMs);
  if (framesWritten)
    Serial.printf("    card write per frame: mean %.1f ms, worst %.1f ms\n",
                  wSumUs / 1000.0 / framesWritten, wMaxUs / 1000.0f);

  Serial.println(F("\n[FLUSH] logs to the card, as after landing"));
  bool imuOk = flush("/stack-imu.bin", imuBuf, imuUsed, true);
  flush("/stack-baro.bin", baroBuf, baroUsed, false);

  bool zeroDrop = !overrun && badTag == 0 && i2cErr == 0 && !imuFull && imuOk;
  Serial.println(F("\n=== verdict ==="));
  Serial.printf("  zero dropped IMU samples while recording   %s\n", zeroDrop ? "PASS" : "FAIL");
  Serial.printf("  no reset, every frame accounted for        %s\n",
                (writeErr == 0 && framesWritten + framesQFull == framesCap) ? "PASS" : "FAIL");
  Serial.printf("  frames dropped when the card fell behind   %u of %u\n", framesQFull, framesCap);
  Serial.printf("  largest video gap                          %u ms\n", gapMaxMs);
  Serial.println(F("\nRecord the result on #7 / #24. Numbers, not just the verdict."));
}

void loop() { delay(10000); }
