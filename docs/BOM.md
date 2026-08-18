# Bill of materials

__Single source of truth for parts, part numbers and weights.__ Anything else that quotes a part number or a mass is wrong — link here instead.

- __What to buy, order status and cost__ → [shopping-list.md](shopping-list.md)
- __Pin order and caliper readings__ → [module-pinouts.md](module-pinouts.md)
- __Why it is built this way__ → [design.md](design.md)

## Parts

Weights measured 2026-08-17 unless the row says `est`.

| Part | Part number | Vendor | Board | Weight (g) |
|---|---|---|---|---|
| XIAO ESP32S3 (plain) | 102010611 (kit) | Seeed | A | 2.9 |
| Wio-SX1262 LoRa | 102010611 (kit) | Seeed | A | 2.1 |
| U.FL 82 mm whip, 860-930M A-03 | 102010611 (kit) | Seeed | A | 0.4 |
| L76K GNSS for XIAO | 109100021 | Seeed | A | 14.2 |
| XIAO ESP32S3 Sense | 113991115 | Seeed | B | 4.0 |
| LSM6DSO32 6-DoF IMU | 4692 | Adafruit | B | 1.8 |
| BMP388 barometer | B0GSYYT1K5 | DIYmall | B | 1.8 |
| Piezo buzzer PS1240 | 160 | Adafruit | B | 0.6 |
| LiPo 3.7 V 500 mAh | 1578 | Adafruit | shared | 10.8 |
| microSD card | — held | — | B | est ~0.4 |
| Carrier PCB, 4-layer 1.0 mm, 24 × 95 | — not ordered | OSH Park | both | est 4.3 |
| 2× 2×7 stacking header, ~14 mm | — unverified | — | both | est 1.0 |
| Arming switch + wiring | — not bought | — | shared | est 1.5 |
| __Avionics subtotal__ | | | | __45.4__ |
| ElectronicsSled, PLA | v7.7.0 | printed | — | __9.3?__ |
| __Nose total__ | | | | __54.7__ |

Also in the kit, __does not fly__: 2.4G A-02 antenna, 0.3 g — the XIAO's WiFi/BLE antenna.

__The sled's 9.3 g is disputed.__ The rocket repo weighed it at __7.1 g__ on 2026-08-07 ([sections.md](https://github.com/jwilleke/js-rocket/blob/main/docs/sections.md) note 6) and both figures claim the scale. Its geometry moved at v7.7.0, which may or may not explain 2.2 g. __Reweigh it__ — nose total is __52.5__ if 7.1 is right.

## Mass budget

| | g |
|---|---|
| Nose total | __54.7__ |
| Target | ~50 |
| Weathercock limit | ~65 |

__Over target, under the limit__ — a budget problem, not a grounding. 38.6 g of the total is weighed, 6.8 g still estimated. A payload gram displaces only __0.75 g__ of ballast, so overruns cost more than they look — see [payload-ballast.md](https://github.com/jwilleke/js-rocket/blob/main/docs/payload-ballast.md).

__The L76K is the whole overrun.__ Estimated 5.0 g, weighs __14.2__ — heavier than the battery, and larger than the next two rows combined. Four rows came in *light* (Sense −3.5, Wio-SX1262 −2.4, buzzer −1.4, XIAO −0.6) and still did not cover it. __Weigh the module without its active antenna__: if the antenna is most of the mass this is a separable choice; if not, it was mis-specced 3×.

__Both Adafruit STEMMA QT sensors are 1.8 g against a 1.0 g estimate, +80% each.__ The BMP388's overrun was not a fluke — that is what the form factor weighs.

__Nothing here is required to fly the rocket.__ [js-rocket](https://github.com/jwilleke/js-rocket) flies on ballast alone; the sled is payload.

## The two boards

| Board | MCU | Role | Firmware |
|---|---|---|---|
| __A__ | XIAO ESP32S3 (plain) | __Recovery beacon__ — GPS position over LoRa | __Stock Meshtastic, pre-flashed by Seeed. None written__ |
| __B__ | XIAO ESP32S3 __Sense__ | __Flight recorder__ — camera, IMU, barometer, PSRAM log | Custom, and not yet started |

Both ride one carrier PCB, on opposite faces. __Two MCUs, not one__, so the beacon is not gated on flight firmware being finished — the beacon *is* the recovery system, and a boot-loop at the pad cannot be fixed with the nose assembled.

## Why each part

| Part | Why this one |
|---|---|
| __XIAO ESP32S3 + Wio-SX1262__ | Supported Meshtastic device out of the box. __Must be the matched B2B kit variant__ — buy SKU 102010611 as a kit, never the two boards separately. It arrives pre-flashed, which is the entire premise of board A |
| __U.FL 82 mm whip__ | LoRa antenna, runs forward up the ogive. Included in the kit |
| __L76K GNSS__ | __Active antenna included.__ Plugs onto the XIAO's own 14 pads and talks UART on D6/D7 — __no carrier footprint needed__. Replaced a MAX-M10S that was 44.2 × 30.5 mm and ~$60 |
| __XIAO ESP32S3 Sense__ | Recorder MCU. Carries the __OV2640 camera__ and microSD slot on its expansion board |
| __LSM6DSO32__ | __±32 g.__ Boost peaks at __17.6 g__, so every ±16 g part on the market clips — and a clipped boost integral destroys the velocity estimate for the whole flight. 9 KB __FIFO__ is a hard requirement |
| __BMP388__ | Unported: only jobs are timestamping ejection and detecting landing. Address __0x77__, no clash with the IMU. __Do not re-specify a BMP390__ — same driver, 8–12 week lead |
| __Piezo buzzer__ | PWM from D0. __Passive, not active__ — a real GPIO can drive multiple tones, so beep patterns read as distinct status codes |
| __Carrier PCB__ | The sled's structural span. See [README](../README.md) for the frozen interface. __Blocked behind breadboarding, deliberately__ — a layout error costs ~$33 and two weeks |
| __2×7 stacking headers__ | The expansion board hangs in the gap; __15 mm__ total stack above the carrier. __Not a generic part__ — stock 2×7 headers are far shorter. Believed held; __verify before assuming__ |
| __LiPo 500 mAh__ | One cell feeds both MCUs. Over an hour against ~300 mA |
| __Arming switch__ | Sits __in the battery line__, not on a GPIO — physically cuts power, zero pins. __No longer a reed switch__: superseded 2026-08-15 by a __pull-pin plus a subminiature microswitch__. Nothing bought, no part number; the 1.5 g is inherited from the reed-switch design |
| __microSD__ | __Video only, and in hand.__ The old A1/A2 / pSLC requirement was written when the sampler wrote to the card in flight; __PSRAM buffering removed that__. What is left is sequential video write — a speed-class question, not a random-IOPS one |

## Deliberately excluded

| Not used | Why |
|---|---|
| __Magnetometer__ | Motor and battery currents corrupt it, and gyro drift over 30 s is small |
| __Barometric static port__ | No legal location — the longest straight run above the sled is __0.33 caliber__ against the 1 cal a port needs. And nothing consumes the number: ejection is the motor delay, not a pyro channel |
| __MPU6050, LSM6DS3, ICM-20948, ICM-42688-P, ADXL345__ | All __±16 g__. All clip against 17.6 g. Cheap and unusable |
| __DFRobot Gravity 10DOF__ and similar integrated modules | Its BMI323 is ±16 g; also 32 × 27 mm, wider than the 24 mm carrier |
| __TeleMega__ | 31.75 mm will not enter the 40 mm bore with its battery. ~$400. Six pyro channels this rocket cannot use, and 70 cm telemetry needs an amateur licence |
| __LILYGO T-Beam__ | 33 mm wide × ~30 mm with the 18650 holder, against 22.6 mm of available depth at that width |
| __18650 cell__ | Would put nose mass near 65 g |
| __Second cell for isolation__ | +8 g the budget cannot afford. Cost: a camera brownout on B can disturb A |
| __Self-powered beeper__ | ~5 g, zero pins, and immune to MCU failure — but the buzzer already shares B's MCU. Revisit if recovery confidence outranks grams |

## Fallbacks worth remembering

- __IMU unobtainable__ → __BMI088__ (±24 g, ~$12, widely stocked) or split the job: __MPU6050 + ADXL375__. The split costs __+1 g and one I2C address, no extra pins__ — everything shares the bus.
- __Barometer unobtainable__ → any BMP3xx, or a generic __BMP280__. It is not the altimeter.

## Dimensions are not in this table

__Only the BMP388 has been measured with calipers.__ Every part now has a weight; every *size* except the BMP388's is still a datasheet figure. That one board disagreed with Adafruit's published dimensions in two places, and the __LSM6DSO32 is the last part blocking sensor footprints__ — in hand since 2026-08-10, still unmeasured. Readings and pin order go in [module-pinouts.md](module-pinouts.md).

__Qwiic cables are bench-only.__ Both sensors ship with them, so breadboarding needs no soldering — but JST-SH is friction-fit and will shake loose under boost. The flight build solders to the 0.1 in header holes, so the cables are not in any weight above.
