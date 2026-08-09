# Bill of materials

Every part the avionics sled needs. **Nothing here is required to fly the rocket** — [js-rocket](https://github.com/jwilleke/js-rocket) flies with ballast alone and the sled is payload.

This page owns the engineering facts: what each part is, which board it serves, what it weighs, and why it beat the alternatives. **What was actually bought, what it cost and where it is now is in [shopping-list.md](shopping-list.md).**

**Where things live.** The *design record* — every decision and the reasoning behind it — is [`js-rocket/docs/planing/electronics-plan.md`](https://github.com/jwilleke/js-rocket/blob/main/docs/planing/electronics-plan.md). The *printed sled* that carries these boards is a rocket part and stays there too, as is the [PayloadAdapter](https://github.com/jwilleke/js-rocket/blob/main/docs/3d-printed-parts/payload-adapter.md) the sled loads through. The carrier PCB, its Gerbers and the firmware are here.

**The mass budget is the hard constraint.** Target is **~50 g of nose mass** including the printed sled; past ~65 g the rocket goes over-stable and weathercocks. A payload gram displaces only **0.78 g** of ballast, so overruns cost more than they look — see [payload-ballast.md](https://github.com/jwilleke/js-rocket/blob/main/docs/payload-ballast.md).

## The two boards

| Board | MCU | Role | Firmware |
|---|---|---|---|
| **A** | XIAO ESP32S3 (plain) | **Recovery beacon** — GPS position over LoRa | **Stock Meshtastic, pre-flashed by Seeed. None written** |
| **B** | XIAO ESP32S3 **Sense** | **Flight recorder** — camera, IMU, barometer, PSRAM log | Custom, and not yet started |

Both ride one carrier PCB, on opposite faces. **Two MCUs, not one**, so the beacon is not gated on flight firmware being finished — the beacon *is* the recovery system, and a boot-loop at the pad cannot be fixed with the nose assembled.

## Parts

**Mass is an estimate unless the row says measured.** The one estimate replaced by a scale so far came in **80% heavy** — the BMP388 was budgeted at 1.0 g and weighs 1.8. The other eleven rows are still guesses, so treat the 51.4 g total as optimistic.

| Part | Board | Mass (g) | Size (mm) | Why this part |
|---|---|---|---|---|
| **XIAO ESP32S3** (plain) | A | 3.5 | 21 × 17.5 | Beacon MCU. Bought as a kit with the radio below |
| **Wio-SX1262** LoRa, B2B kit version | A | 4.5 | same outline, hangs under the XIAO | Supported Meshtastic device out of the box. **Must be the matched B2B kit variant** |
| **U.FL 82 mm whip** | A | 1.0 | — | LoRa antenna, runs forward up the ogive. **Included in the kit** |
| **L76K GNSS for XIAO** | A | 5.0 | 18 × 21 | **Active antenna included.** Plugs onto the XIAO's own 14 pads and talks UART on D6/D7 — so it needs **no carrier footprint**. Replaced a MAX-M10S that was 44.2 × 30.5 mm and ~$60 |
| **XIAO ESP32S3 Sense** | B | 7.5 | 21 × 17.5 + expansion | Recorder MCU. Carries the **OV2640 camera** and microSD slot on its expansion board |
| **LSM6DSO32** 6-DoF (Adafruit 4692) | B | 1.0 | 25.5 × 17.8 | **±32 g.** Boost peaks at **17.6 g**, so every ±16 g part on the market clips — and a clipped boost integral destroys the velocity estimate for the whole flight. Has a 9 KB **FIFO**, which is a hard requirement. **Measure it; do not trust the datasheet dimensions** |
| **BMP388** barometer, STEMMA QT | B | **1.8 measured** | 25.5 × 17.8, **4.79 thick** | Unported: only jobs are timestamping ejection and detecting landing. Address **0x77**, no clash with the IMU. **Do not re-specify a BMP390** — same driver, and the 390 has an 8–12 week lead |
| **Passive piezo buzzer** (Adafruit 160, PS1240) | B | 2.0 | — | PWM from D0. **Passive, not active** — a real GPIO can drive multiple tones, so beep patterns read as distinct status codes |
| **Carrier PCB**, 4-layer, 1.0 mm | both | 4.3 | **24 × 95 × 1.0** | The sled's structural span. See [README](../README.md) for the frozen interface |
| 2× 2×7 stacking headers, ~14 mm | both | 1.0 | — | The expansion board hangs in the gap; **15 mm** total stack above the carrier |
| **LiPo 500 mAh** (Adafruit 1578) | shared | 9.0 | — | One cell feeds both MCUs. Over an hour against ~300 mA |
| Reed switch, pigtails, wiring | shared | 1.5 | — | Arming switch sits **in the battery line**, not on a GPIO — physically cuts power, zero pins, no hole in the nose |
| **microSD**, A1/A2 or industrial pSLC | B | — | — | Video only. **Buy a good card** — a cheap one's worst-case write latency is 100–250 ms |
| | | | | |
| **Avionics subtotal** | | **42.1** | | |
| ElectronicsSled, PLA — **measured** | | **9.3** | ≤ 39.4 × 39.4 × 134 | Printed part, lives in the rocket repo |
| **Nose total** | | **51.4** | | Against a ~50 g target |

**Buy the Seeed kit rather than the two parts separately** — it guarantees the matched B2B variant and arrives pre-flashed with Meshtastic, which is the entire premise of board A.

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

## The BMP388, measured off the part

The only part that has been through the confirmation below. **In hand and measured 2026-08-08.** 25.5 × 17.8 mm, address **0x77** (ADDR jumper for 0x76), two Qwiic cables included at **110 mm** each. Pin order confirmed from the part:

```text
1 VIN   2 3Vo   3 GND   4 SCL   5 SDO   6 SDA   7 CS   8 INT
```

**We use 1, 3, 4, 6.** Header ships **loose**, which keeps the mounting orientation open. Measured: **1.8 g**, **4.79 mm** thick over the Qwiic connectors, mounting holes **Ø2.35 mm at 20.58 mm spacing** on the edge opposite the header — so **M2, not M2.5**, and Adafruit's own figure is 2.5. Photos: [front](https://github.com/jwilleke/js-rocket/blob/main/docs/resources/PXL_20260808_193009460.jpg), [back](https://github.com/jwilleke/js-rocket/blob/main/docs/resources/PXL_20260808_192959846.jpg).

Three cautions on that board, each of which has cost someone an evening:

- **Power to VIN, never 3Vo.** `3Vo` is the on-board regulator's *output*; back-feeding it kills the LDO. **The board in hand is marked 3 V, not the `3-5VDC` the listing claims** — that figure is Adafruit's text, which the listing copies. **Treat it as a 3.3 V part** and do not feed it 5 V until the back silkscreen is read cleanly. The design runs it at +3V3 either way, so nothing changes except the assumption that 5 V was available as a fallback.
- **The seller's wiring diagram is SPI, not I2C.** It wires SCL/SDO/SDA/CS to Arduino 13/12/11/10 — SCK, MISO, MOSI, SS. On BMP3xx the pins are dual-purpose; this design uses I2C, four wires.
- **If it does not enumerate at 0x77, check CS first.** CS low selects SPI; it must be HIGH for I2C.

**Qwiic cables are bench-only.** They make breadboarding solder-free, but JST-SH is friction-fit and will shake loose under boost — the flight build solders to the 0.1 in header holes.

## Before designing a footprint round any of these

**Confirm the silicon matches the label.** Clone listings copy Adafruit's product text verbatim and the chip does not always match.

- BMP3xx `reg 0x00` → **0x50 = BMP388**, 0x60 = BMP390. A **BMP280** answers **0x58** at `reg 0xD0`.
- **Photograph the header pin order** with the part in front of you. That order is the footprint input, and getting it wrong scraps a board rather than costing a re-solder.

**Only the BMP388 has been through this.** Everything else is a datasheet figure until the part is on the bench — and this board already disagreed with Adafruit's dimensions in two places.
