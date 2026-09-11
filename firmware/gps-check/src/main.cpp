// gps-check -- read the L76K-GNSS directly, with Meshtastic out of the loop (#6)
//
// PlatformIO project. Build, flash and watch:
//     pio run -t upload && pio device monitor
//
// FLASH ONTO XIAO-ESP32S3-cam ONLY -- never XIAO-ESP32S3-lora, which runs stock
// Meshtastic and must not be reflashed. Unplug the lora board before uploading.
//
// WHY: #6 asks whether the lora board's GPS gets a fix. If Meshtastic shows no
// position, this separates "the module, antenna or wiring is bad" from "stock
// Meshtastic is not reading D6/D7". Same four wires, a board we may reflash.
//
// NOT FLIGHT FIRMWARE. UNTESTED -- no hardware has run it.
//
// WIRING -- the same four jumpers as the lora bench board, each L76K pad to the
// XIAO pin of the SAME NAME. Wire by position, never by Seeed's RX/TX labels:
//
//     XIAO 3V3 -> L76K 3V3    <- the module runs from 3V3 alone; 5V is dead
//     XIAO GND -> L76K GND
//     XIAO D6  -> L76K D6     <- XIAO transmits (GPIO43), the module listens
//     XIAO D7  <- L76K D7     <- the module talks, XIAO receives (GPIO44)
//
// The GNSS antenna on the module's U.FL, face to the sky. A fix wants outdoors
// or a window; indoors you may see satellites in view and never get one.
//
// OUTPUT: one line every 2 s -- fix type, satellites used and in view, best
// signal-to-noise, HDOP -- and a FIRST FIX line with the time from power-up.
// The summary never prints a position. Press `r` to toggle the raw NMEA stream,
// which DOES carry latitude and longitude: do not paste it into an issue or a
// commit. This repo is public.

#include <Arduino.h>

static const uint32_t GPS_BAUD  = 9600;   // L76K default
static const uint32_t REPORT_MS = 2000;
static const uint32_t SILENT_MS = 3000;   // no bytes this long = say so
static const uint32_t VIEW_MS   = 5000;   // a talker's GSV count goes stale

static char     line[128];
static size_t   len      = 0;
static bool     overflow = false;
static bool     raw      = false;

static uint32_t bootMs, lastByteMs, lastReportMs;
static uint32_t bytes = 0, good = 0, bad = 0;

static int      fixQ    = -1;             // GGA quality; -1 = no GGA yet
static int      used    = 0;
static char     hdop[8] = "-";
static int      bestSnr = -1;             // this report window
static bool     fixed   = false;          // first fix already reported
static char     lastTxt[64] = "";

// Satellites in view, per constellation talker (GP GPS, GL GLONASS, GB/BD
// BeiDou, GA Galileo, GQ QZSS), summed over talkers heard recently.
struct View { char id[3]; int n; uint32_t at; };
static View views[6];

static bool checksumOk(const char *s) {
  const char *star = strchr(s, '*');
  if (!star || !isxdigit(star[1]) || !isxdigit(star[2])) return false;
  uint8_t x = 0;
  for (const char *p = s + 1; p < star; ++p) x ^= (uint8_t)*p;
  return x == (uint8_t)strtoul(star + 1, nullptr, 16);
}

// Split in place on commas, dropping the checksum. Empty fields become "".
static int split(char *s, char **f, int max) {
  char *star = strchr(s, '*');
  if (star) *star = '\0';
  int n = 0;
  f[n++] = s;
  for (char *p = s; *p && n < max; ++p)
    if (*p == ',') { *p = '\0'; f[n++] = p + 1; }
  return n;
}

static void noteView(const char *talker, int n) {
  View *slot = nullptr;
  for (auto &v : views) {
    if (v.id[0] && strncmp(v.id, talker, 2) == 0) { slot = &v; break; }
    if (!v.id[0] && !slot) slot = &v;
  }
  if (!slot) return;
  memcpy(slot->id, talker, 2);
  slot->id[2] = '\0';
  slot->n  = n;
  slot->at = millis();
}

static void sentence(char *s) {
  if (!checksumOk(s)) { ++bad; return; }
  ++good;

  char talker[3] = { s[1], s[2], '\0' };
  char *f[24];
  int n = split(s, f, 24);
  const char *type = f[0] + 3;            // "$GNGGA" -> "GGA"

  if (strcmp(type, "GGA") == 0 && n > 8) {
    fixQ = *f[6] ? atoi(f[6]) : 0;
    used = atoi(f[7]);
    snprintf(hdop, sizeof hdop, "%s", *f[8] ? f[8] : "-");
    if (fixQ > 0 && !fixed) {
      fixed = true;
      Serial.printf("\n>>> FIRST FIX at %.1f s after power-up, %d satellites used\n\n",
                    (millis() - bootMs) / 1000.0, used);
    }
  } else if (strcmp(type, "GSV") == 0 && n > 3) {
    noteView(talker, atoi(f[3]));
    for (int i = 7; i < n; i += 4)        // PRN, elevation, azimuth, SNR
      if (*f[i]) bestSnr = max(bestSnr, atoi(f[i]));
  } else if (strcmp(type, "TXT") == 0 && n > 4) {
    // Module status text -- antenna state on some firmware. Print on change.
    if (strcmp(lastTxt, f[4]) != 0) {
      snprintf(lastTxt, sizeof lastTxt, "%s", f[4]);
      Serial.printf("L76K says: %s\n", lastTxt);
    }
  }
}

static void feed(char c) {
  if (c == '$') { len = 0; overflow = false; }
  if (c == '\r' || c == '\n') {
    if (len && line[0] == '$') {
      if (overflow) ++bad;
      else { line[len] = '\0'; sentence(line); }
    }
    len = 0;
    return;
  }
  if (len < sizeof line - 1) line[len++] = c;
  else overflow = true;
}

static const char *fixName(int q) {
  switch (q) {
    case -1: return "no GGA yet";
    case 0:  return "none";
    case 1:  return "GPS";
    case 2:  return "DGPS";
    case 6:  return "estimated";
    default: return "other";
  }
}

static void report() {
  uint32_t now = millis();
  float t = (now - bootMs) / 1000.0;

  if (bytes == 0) {
    if (now - bootMs > SILENT_MS)
      Serial.printf("%6.1f s  NO DATA from the L76K -- check 3V3 and GND, and that "
                    "the module's D7 pad goes to XIAO D7\n", t);
    return;
  }
  if (now - lastByteMs > SILENT_MS) {
    Serial.printf("%6.1f s  DATA STOPPED -- nothing for %.1f s\n", t,
                  (now - lastByteMs) / 1000.0);
    return;
  }

  int inView = 0;
  for (auto &v : views)
    if (v.id[0] && now - v.at < VIEW_MS) inView += v.n;

  char snr[8] = "-";
  if (bestSnr >= 0) snprintf(snr, sizeof snr, "%d", bestSnr);

  Serial.printf("%6.1f s  fix %-10s used %2d  in view %2d  best SNR %3s dB  "
                "HDOP %-5s  bad %lu/%lu\n",
                t, fixName(fixQ), used, inView, snr, hdop,
                (unsigned long)bad, (unsigned long)(good + bad));

  if (good == 0 && bad > 3)
    Serial.println("          every sentence fails its checksum -- wrong baud?");
  bestSnr = -1;
}

void setup() {
  Serial.begin(115200);
  uint32_t t0 = millis();
  while (!Serial && millis() - t0 < 3000) {}

  // Serial1.begin(baud, config, RX, TX)
  Serial1.begin(GPS_BAUD, SERIAL_8N1, D7, D6);
  bootMs = lastReportMs = millis();

  Serial.println("\ngps-check -- L76K-GNSS on D6/D7 at 9600 baud");
  Serial.println("summary every 2 s, no position printed. `r` toggles raw NMEA,");
  Serial.println("which DOES carry your position -- never paste it into the public repo.\n");
}

void loop() {
  while (Serial1.available()) {
    char c = Serial1.read();
    ++bytes;
    lastByteMs = millis();
    if (raw) Serial.write(c);
    feed(c);
  }
  while (Serial.available()) {
    char c = Serial.read();
    if (c == 'r' || c == 'R') {
      raw = !raw;
      Serial.printf("\n--- raw NMEA %s ---\n", raw ? "ON" : "OFF");
    }
  }
  if (millis() - lastReportMs >= REPORT_MS) {
    lastReportMs = millis();
    if (!raw) report();
  }
}
