# Bill of materials

**Single source of truth for parts, part numbers and weights.** Anything else that quotes a part number or a mass is wrong — link here instead.

- **What to buy, order status and cost** → [shopping-list.md](shopping-list.md)
- **Pin order and caliper readings** → [module-pinouts.md](module-pinouts.md)
- **Why it is built this way** → [design.md](design.md)

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
| **Avionics subtotal** | | | | **45.4** |
| ElectronicsSled, PLA | v7.7.0 | printed | — | **9.3?** |
| **Nose total** | | | | **54.7** |

Also in the kit, **does not fly**: 2.4G A-02 antenna, 0.3 g — the XIAO's WiFi/BLE antenna.

**The sled's 9.3 g is disputed.** The rocket repo weighed it at **7.1 g** on 2026-08-07 ([sections.md](https://github.com/jwilleke/js-rocket/blob/main/docs/sections.md) note 6) and both figures claim the scale. Its geometry moved at v7.7.0, which may or may not explain 2.2 g. **Reweigh it** — nose total is **52.5** if 7.1 is right.

## Mass budget

| | g |
|---|---|
| Nose total | **54.7** |
| Target | ~50 |
| Weathercock limit | ~65 |

**Over target, under the limit** — a budget problem, not a grounding. 38.6 g of the total is weighed, 6.8 g still estimated. A payload gram displaces only **0.75 g** of ballast, so overruns cost more than they look — see [payload-ballast.md](https://github.com/jwilleke/js-rocket/blob/main/docs/payload-ballast.md).

**The L76K is the whole overrun.** Estimated 5.0 g, weighs **14.2** — heavier than the battery, and larger than the next two rows combined. Four rows came in *light* (Sense −3.5, Wio-SX1262 −2.4, buzzer −1.4, XIAO −0.6) and still did not cover it. **Weigh the module without its active antenna**: if the antenna is most of the mass this is a separable choice; if not, it was mis-specced 3×.

**Both Adafruit STEMMA QT sensors are 1.8 g against a 1.0 g estimate, +80% each.** The BMP388's overrun was not a fluke — that is what the form factor weighs.

**Nothing here is required to fly the rocket.** [js-rocket](https://github.com/jwilleke/js-rocket) flies on ballast alone; the sled is payload.

## The two boards

| Board | MCU | Role | Firmware |
|---|---|---|---|
| **A** | XIAO ESP32S3 (plain) | **Recovery beacon** — GPS position over LoRa | **Stock Meshtastic, pre-flashed by Seeed. None written** |
| **B** | XIAO ESP32S3 **Sense** | **Flight recorder** — camera, IMU, barometer, PSRAM log | Custom, and not yet started |

Both ride one carrier PCB, on opposite faces. **Two MCUs, not one**, so the beacon is not gated on flight firmware being finished — the beacon *is* the recovery system, and a boot-loop at the pad cannot be fixed with the nose assembled.

## Why each part

| Part | Why this one |
|---|---|
| **XIAO ESP32S3 + Wio-SX1262** | Supported Meshtastic device out of the box. **Must be the matched B2B kit variant** — buy SKU 102010611 as a kit, never the two boards separately. It arrives pre-flashed, which is the entire premise of board A |
| **U.FL 82 mm whip** | LoRa antenna, runs forward up the ogive. Included in the kit |
| **L76K GNSS** | **Active antenna included.** Plugs onto the XIAO's own 14 pads and talks UART on D6/D7 — **no carrier footprint needed**. Replaced a MAX-M10S that was 44.2 × 30.5 mm and ~$60 |
| **XIAO ESP32S3 Sense** | Recorder MCU. Carries the **OV2640 camera** and microSD slot on its expansion board |
| **LSM6DSO32** | **±32 g.** Boost peaks at **17.6 g**, so every ±16 g part on the market clips — and a clipped boost integral destroys the velocity estimate for the whole flight. 9 KB **FIFO** is a hard requirement |
| **BMP388** | Unported: only jobs are timestamping ejection and detecting landing. Address **0x77**, no clash with the IMU. **Do not re-specify a BMP390** — same driver, 8–12 week lead |
| **Piezo buzzer** | PWM from D0. **Passive, not active** — a real GPIO can drive multiple tones, so beep patterns read as distinct status codes |
| **Carrier PCB** | The sled's structural span. See [README](../README.md) for the frozen interface. **Blocked behind breadboarding, deliberately** — a layout error costs ~$33 and two weeks |
| **2×7 stacking headers** | The expansion board hangs in the gap; **15 mm** total stack above the carrier. **Not a generic part** — stock 2×7 headers are far shorter. Believed held; **verify before assuming** |
| **LiPo 500 mAh** | One cell feeds both MCUs. Over an hour against ~300 mA |
| **Arming switch** | Sits **in the battery line**, not on a GPIO — physically cuts power, zero pins. **No longer a reed switch**: superseded 2026-08-15 by a **pull-pin plus a subminiature microswitch**. Nothing bought, no part number; the 1.5 g is inherited from the reed-switch design |
| **microSD** | **Video only, and in hand.** The old A1/A2 / pSLC requirement was written when the sampler wrote to the card in flight; **PSRAM buffering removed that**. What is left is sequential video write — a speed-class question, not a random-IOPS one |

## Deliberately excluded

| Not used | Why |
|---|---|
| **Magnetometer** | Motor and battery currents corrupt it, and gyro drift over 30 s is small |
| **Barometric static port** | No legal location — the longest straight run above the sled is **0.33 caliber** against the 1 cal a port needs. And nothing consumes the number: ejection is the motor delay, not a pyro channel |
| **MPU6050, LSM6DS3, ICM-20948, ICM-42688-P, ADXL345** | All **±16 g**. All clip against 17.6 g. Cheap and unusable |
| **DFRobot Gravity 10DOF** and similar integrated modules | Its BMI323 is ±16 g; also 32 × 27 mm, wider than the 24 mm carrier |
| **TeleMega** | 31.75 mm will not enter the 40 mm bore with its battery. ~$400. Six pyro channels this rocket cannot use, and 70 cm telemetry needs an amateur licence |
| **LILYGO T-Beam** | 33 mm wide × ~30 mm with the 18650 holder, against 22.6 mm of available depth at that width |
| **18650 cell** | Would put nose mass near 65 g |
| **Second cell for isolation** | +8 g the budget cannot afford. Cost: a camera brownout on B can disturb A |
| **Self-powered beeper** | ~5 g, zero pins, and immune to MCU failure — but the buzzer already shares B's MCU. Revisit if recovery confidence outranks grams |

## Fallbacks worth remembering

- **IMU unobtainable** → **BMI088** (±24 g, ~$12, widely stocked) or split the job: **MPU6050 + ADXL375**. The split costs **+1 g and one I2C address, no extra pins** — everything shares the bus.
- **Barometer unobtainable** → any BMP3xx, or a generic **BMP280**. It is not the altimeter.

## Dimensions are not in this table

**Only the BMP388 has been measured with calipers.** Every part now has a weight; every *size* except the BMP388's is still a datasheet figure. That one board disagreed with Adafruit's published dimensions in two places, and the **LSM6DSO32 is the last part blocking sensor footprints** — in hand since 2026-08-10, still unmeasured. Readings and pin order go in [module-pinouts.md](module-pinouts.md).

**Qwiic cables are bench-only.** Both sensors ship with them, so breadboarding needs no soldering — but JST-SH is friction-fit and will shake loose under boost. The flight build solders to the 0.1 in header holes, so the cables are not in any weight above.
