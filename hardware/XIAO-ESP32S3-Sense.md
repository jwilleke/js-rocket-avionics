# XIAO ESP32S3 Sense — board B

__The flight recorder's MCU.__ Same module as board A plus the Sense expansion board, which carries the camera — an __OV3660__, confirmed off the ribbon 2026-09-06, where every document here had assumed an OV2640 — and the __microSD__ slot.

## What it is for

Board B does the work that cannot be bought pre-flashed: camera, IMU, barometer, PSRAM logging. Its firmware is __custom and not yet started__.

Splitting it from board A buys failure isolation, and dissolves two problems as a side effect ([design.md](../docs/design.md)): board B sheds LoRa and the GPS UART, so __an I2C GPIO expander is no longer needed__, and its SPI carries only the microSD, so __no "do not transmit while recording" scheduling rule is required__ — different MCU, different bus.

## Photographs

| [Expansion board, camera fitted](../docs/resources/XIAO-ESP32S3-Sense-expansion.jpg) | [MCU module](../docs/resources/XIAO-ESP32S3-module.jpg) |
|---|---|
| ![Sense expansion board with the camera fitted](../docs/resources/XIAO-ESP32S3-Sense-expansion.jpg) | ![XIAO ESP32S3 module](../docs/resources/XIAO-ESP32S3-module.jpg) |

The pair is the whole of board B: the MCU module, and the Sense expansion board carrying the camera and the microSD slot. The expansion shot shows the FPC connector, the folded camera ribbon, and __the lens barrel standing proud of the board__ — which is the dimension [#9](https://github.com/jwilleke/js-rocket-avionics/issues/9) needs and which __this photograph cannot give__: standoff is a height, so it wants an __edge-on__ shot against the grid, with the stack assembled on its headers.

> __It is an OV3660, not an OV2640.__ Read off the camera ribbon, 2026-09-06. Every camera figure in this project was written for an OV2640, so the correction propagates — but __it changes far less than it looks like it should__, for the reason below.

### The sensor swap is almost irrelevant. The lens is what matters

| | Active area | Diagonal |
|---|---|---|
| OV2640, as [design.md](../docs/design.md) states it | 3.590 × 2.684 mm | __4.482 mm__ |
| __OV3660__, 2048 × 1536 at 1.75 µm | 3.584 × 2.688 mm | __4.480 mm__ |

__Two microns apart.__ The two sensors are effectively the same optical format, so swapping one for the other moves the cone by nothing measurable. __What sets the cone is the focal length__, and a 3 MP module is often shipped with a shorter lens than a 2 MP one:

| f | Diagonal FOV |
|---|---|
| 4.8 mm — the figure in [design.md](../docs/design.md) | 50.0° |
| 4.0 mm | 58.5° |
| 3.6 mm | 63.8° |
| 3.0 mm | 73.5° |

__A wider cone makes the port harder, not easier.__ At a lens sitting on the board (r 9) the full cone needs Ø14.2 mm outside the collar at 50°, Ø17.6 at 60° and Ø21.3 at 70° — against a collar 15.0 mm tall. It was unbuildable at 50° and it gets worse.

__And the conclusion is unchanged at every one of those angles.__ With the lens brought out to r 19 the port stays small — Ø4.9 outside at 50°, Ø6.0 at 60°, Ø7.3 at 70° — so __the standoff fix works across the whole plausible range__, which is exactly why it was the right answer rather than a bigger hole. [js-rocket#88](https://github.com/jwilleke/js-rocket/issues/88) and [js-rocket#89](https://github.com/jwilleke/js-rocket/issues/89) stand as written; only the arithmetic behind them is re-derived.

> __Do not look the focal length up. Measure the cone.__ Photograph a ruler at a known distance and compute the angle actually captured. That gives the __real__ figure for the __real__ lens — settling the 50°-versus-68° argument that this project has already had once with a datasheet, and giving [#9](https://github.com/jwilleke/js-rocket-avionics/issues/9) a number nobody has to defend. One frame at bring-up ([#7](https://github.com/jwilleke/js-rocket-avionics/issues/7)).

### How to confirm a camera's identity without reading a ribbon

The ribbon settled it this time, but it is the weakest of the four:

- __Query the sensor over I2C.__ Decisive, because it reads the die: OV2640 reports PID __0x26__, OV3660 reports __0x3660__ (registers 0x300A/0x300B). Under `esp32-camera` that is `esp_camera_sensor_get()->id.PID`, and the stock Arduino examples print it at boot
- __Try the largest frame size.__ An OV2640 tops out at __UXGA 1600 × 1200__; an OV3660 does __QXGA 2048 × 1536__. If QXGA returns a frame, it is not a 2640
- __Check the vendor's SKU for the batch__ — Seeed has shipped both on this expansion board
- __Read the ribbon__, as here — fine when it is legible and unfolded, and it was neither until it was

## Interfaces

| | |
|---|---|
| Carrier face | __Bottom__, per [design.md](../docs/design.md) — with LSM6DSO32, BMP388 and the buzzer |
| Position | __Centred at carrier y = 18 mm__, which is what puts the camera at nose z 30..45 |
| Sensors | I2C on __D4/D5__ |
| Buzzer | PWM on __D0__ |
| Camera | __OV3660__ (not OV2640 — confirmed 2026-09-06). __DVP parallel bus__, 14 GPIO, plus I2C/SCCB for control. Frames land in PSRAM by DMA |
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
