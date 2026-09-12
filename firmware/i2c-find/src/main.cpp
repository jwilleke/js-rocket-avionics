#include <Arduino.h>
#include <Wire.h>
// i2c-find -- which XIAO pins carry external pull-ups (the I2C lines), and on
// which pin pair the sensors answer. Reads pins and drives nothing but I2C.
//
// Expected, correctly wired: pull-ups on D4 and D5 only, and
//     SDA=D4 SCL=D5 -> device 0x6A   (LSM6DSO32)
//     SDA=D4 SCL=D5 -> device 0x77   (BMP388)
// "HELD LOW" on a pin means something drags it to ground -- a short, or an
// unpowered breakout whose pull-ups go to a dead VIN.
struct P { const char *name; int gpio; };
static const P pins[] = {{"D0",1},{"D1",2},{"D2",3},{"D3",4},{"D4",5},{"D5",6},
                         {"D6",43},{"D7",44},{"D8",7},{"D9",8},{"D10",9}};
static const int N = sizeof(pins) / sizeof(pins[0]);
void setup() {
  Serial.begin(115200); delay(2500);
  Serial.println("\n=== i2c diagnostic ===");
  bool pulled[N];
  for (int i = 0; i < N; i++) {
    pinMode(pins[i].gpio, INPUT_PULLDOWN); delay(5);
    int withDown = digitalRead(pins[i].gpio);
    pinMode(pins[i].gpio, INPUT_PULLUP); delay(5);
    int withUp = digitalRead(pins[i].gpio);
    pinMode(pins[i].gpio, INPUT);
    pulled[i] = withDown == 1;
    Serial.printf("  %-3s GPIO%-2d  pulldown->%d pullup->%d  %s\n", pins[i].name, pins[i].gpio,
                  withDown, withUp,
                  withDown ? "EXTERNAL PULL-UP (I2C line?)" : (withUp ? "" : "HELD LOW (short to GND?)"));
  }
  Serial.println("  scanning pin pairs with pull-ups...");
  int hits = 0;
  for (int a = 0; a < N; a++) for (int b = 0; b < N; b++) {
    if (a == b || !pulled[a] || !pulled[b]) continue;
    Wire.begin(pins[a].gpio, pins[b].gpio, 100000);
    for (uint8_t ad = 0x08; ad < 0x78; ad++) {
      Wire.beginTransmission(ad);
      if (Wire.endTransmission() == 0) {
        Serial.printf("  SDA=%s SCL=%s -> device 0x%02X\n", pins[a].name, pins[b].name, ad); hits++;
      }
    }
    Wire.end();
  }
  if (!hits) Serial.println("  no device on any pulled-up pair");
  Serial.println("=== done ===");
}
void loop() { delay(10000); }
