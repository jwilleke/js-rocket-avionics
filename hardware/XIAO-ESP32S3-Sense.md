# XIAO ESP32S3 Sense — board B

__The flight recorder's MCU.__ Same module as board A plus the Sense expansion board, which carries the __OV2640 camera__ and the __microSD__ slot.

## What it is for

Board B does the work that cannot be bought pre-flashed: camera, IMU, barometer, PSRAM logging. Its firmware is __custom and not yet started__.

Splitting it from board A buys failure isolation, and dissolves two problems as a side effect ([design.md](../docs/design.md)): board B sheds LoRa and the GPS UART, so __an I2C GPIO expander is no longer needed__, and its SPI carries only the microSD, so __no "do not transmit while recording" scheduling rule is required__ — different MCU, different bus.

## Photographs

| [Expansion board, camera fitted](../docs/resources/XIAO-ESP32S3-Sense-expansion.jpg) | [MCU module](../docs/resources/XIAO-ESP32S3-module.jpg) |
|---|---|
| ![Sense expansion board with the camera fitted](../docs/resources/XIAO-ESP32S3-Sense-expansion.jpg) | ![XIAO ESP32S3 module](../docs/resources/XIAO-ESP32S3-module.jpg) |

The pair is the whole of board B: the MCU module, and the Sense expansion board carrying the camera and the microSD slot. The expansion shot shows the FPC connector, the folded camera ribbon, and __the lens barrel standing proud of the board__ — which is the dimension [#9](https://github.com/jwilleke/js-rocket-avionics/issues/9) needs and which __this photograph cannot give__: standoff is a height, so it wants an __edge-on__ shot against the grid, with the stack assembled on its headers.

> __Verify which sensor this is before trusting any field-of-view number.__ The camera ribbon appears to carry an __`OV36…`__ marking rather than `OV2640`. It is partly obscured by the fold and I would not act on it from this image — __but if the part is an OV3660, every figure in the camera analysis moves__: the 4.482 mm active-area diagonal, the f = 4.8 mm lens, the __50.1° cone__, and therefore the port sizing in [js-rocket#88](https://github.com/jwilleke/js-rocket/issues/88) and the shelf radius in [js-rocket#89](https://github.com/jwilleke/js-rocket/issues/89). This repo already has the rule — *confirm the silicon matches the label* — and it has caught two parts already. __Read the marking with the ribbon unfolded, or query the sensor ID over I2C during [#7](https://github.com/jwilleke/js-rocket-avionics/issues/7).__

## Interfaces

| | |
|---|---|
| Carrier face | __Bottom__, per [design.md](../docs/design.md) — with LSM6DSO32, BMP388 and the buzzer |
| Position | __Centred at carrier y = 18 mm__, which is what puts the camera at nose z 30..45 |
| Sensors | I2C on __D4/D5__ |
| Buzzer | PWM on __D0__ |
| Camera | __DVP parallel bus__, 14 GPIO, plus I2C/SCCB for control. Frames land in PSRAM by DMA |
| microSD | on SPI, on the Sense expansion board |
| PSRAM | __8 MB__ (ESP32-S3R8) |

## Why the log lives in PSRAM

Neither storage medium can be written during flight:

- __SD latency is unbounded__ — wear-levelling and garbage collection make a normally-2 ms write take __100–250 ms__, spec-legally
- __Internal flash is worse__ — writing it __disables the instruction cache__, and a 4 KB erase at ~20–40 ms stalls code executing from flash, including ISRs not marked `IRAM_ATTR`. At 500 Hz that silently drops __10–20 samples__, during boost

So: buffer in PSRAM, flush after landing. `500 Hz × ~30 B × 60 s = 900 KB` against 8 MB — the whole flight fits about nine times over.

> __A PSRAM-only log is lost if board B resets.__ Nothing is on non-volatile media until the landing flush, so a brownout, watchdog reset or hard landing costs the entire telemetry set while the SD video survives. [design.md](../docs/design.md) suggests checkpoint flushes during the low-rate descent phase, never during boost.

## Things that will catch you

__Do not extend the camera flex__ — the DVP bus runs a ~20 MHz XCLK. Board B's position on the carrier is what places the camera, not a longer ribbon.

__Do not fit the wide-angle lens.__ The 120–160° M7 option cannot match the sensor's 25° chief ray angle, giving severe corner vignetting and colour crosstalk, and it would need a far larger hole in a load-bearing collar.

The BAT-pad and one-USB-at-a-time rules from [XIAO-ESP32S3.md](XIAO-ESP32S3.md) apply identically here.

## Open

- __Which carrier face is 270°.__ [design.md](../docs/design.md) says board B is on the "bottom" face and never says which sled azimuth that is. The Nosecone port is at __azimuth 270°__ and the sled's web faces are 90°/270°, so this is now a flight constraint — [#13](https://github.com/jwilleke/js-rocket-avionics/issues/13)
- __The lens standoff has never been measured__, and it decides whether the camera sees 50° or 23–30° — [#9](https://github.com/jwilleke/js-rocket-avionics/issues/9)
- __Nothing has been brought up__ — [#7](https://github.com/jwilleke/js-rocket-avionics/issues/7)
- __Firmware is not started__, and the flight profile it must handle is now two burns, not one — [#12](https://github.com/jwilleke/js-rocket-avionics/issues/12)

---

Part numbers, vendors and masses live in [BOM.md](../docs/BOM.md), which is the single source of truth for both. Purchase history is in [shopping-list.md](../docs/shopping-list.md); the reasoning is in [design.md](../docs/design.md).
