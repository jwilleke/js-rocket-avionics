# XIAO ESP32S3 Sense — board B

__The flight recorder's MCU.__ Same module as board A plus the Sense expansion board, which carries the camera — an __OV3660__ — and the __microSD__ slot.

## What it is for

Board B does the work that cannot be bought pre-flashed: camera, IMU, barometer, PSRAM logging. Its firmware is __custom and not yet started__.

Splitting it from board A buys failure isolation, and dissolves two problems as a side effect ([design.md](../docs/design.md)): board B sheds LoRa and the GPS UART, so __an I2C GPIO expander is no longer needed__, and its SPI carries only the microSD, so __no "do not transmit while recording" scheduling rule is required__ — different MCU, different bus.

## Photographs

| [Expansion board](../docs/resources/XIAO-ESP32S3-Sense-expansion.jpg) | [MCU module](../docs/resources/XIAO-ESP32S3-module.jpg) |
|---|---|
| ![Sense expansion board with the camera fitted](../docs/resources/XIAO-ESP32S3-Sense-expansion.jpg) | ![XIAO ESP32S3 module](../docs/resources/XIAO-ESP32S3-module.jpg) |

| [Stack, side](../docs/resources/XIAO-ESP32S3-Sense-stack-side.jpg) | [Stack, end](../docs/resources/XIAO-ESP32S3-Sense-stack-end.jpg) |
|---|---|
| ![Assembled stack from the side](../docs/resources/XIAO-ESP32S3-Sense-stack-side.jpg) | ![Assembled stack end-on](../docs/resources/XIAO-ESP32S3-Sense-stack-end.jpg) |

## The stack

From the mounting surface up: __7-pin headers → XIAO → Sense expansion board → FPC connector__, with the camera on a __flexible ribbon__ above it.

| | |
|---|---|
| Height, mounting surface to tallest point, __camera excluded__ | __10.7 mm__ |
| Header standoff | ~2.50 mm, the kit's standard 7-pin headers |
| Expansion board | __above__ the XIAO |
| Camera | on a flexible ribbon — __its position is not fixed by the stack__ |

The MCU module and the Sense expansion board carrying the camera and the microSD slot.

### Optics

| | Active area | Diagonal |
|---|---|---|
| __OV3660__, 2048 × 1536 at 1.75 µm | 3.584 × 2.688 mm | __4.480 mm__ |

__The focal length of the fitted lens is not known__, and it is what sets the field of view — the sensor's format barely moves it. At f 4.8 the diagonal cone is 50.0°, at f 4.0 it is 58.5°, at f 3.0 it is 73.5°.

__The sensor reports PID `0x3660`__ over I2C at registers 0x300A/0x300B, which is how its identity is established from the die rather than from a label. An OV2640 reports `0x26`. It also does __QXGA 2048 × 1536__, where an OV2640 tops out at UXGA 1600 × 1200.

__Focus is adjustable__ via the M5/M6 lens thread. Hyperfocal at f/2.8 with a ~4.4 µm circle of confusion is ~1.9 m, so everything past ~1 m is sharp.

## Things that will catch you

__Do not extend the camera flex__ — the DVP bus runs a ~20 MHz XCLK. Board B's position on the carrier is what places the camera, not a longer ribbon.

__Do not fit the wide-angle lens.__ The 120–160° M7 option cannot match the sensor's 25° chief ray angle, giving severe corner vignetting and colour crosstalk, and it would need a far larger hole in a load-bearing collar.

## Specification

[Specifications](https://www.seeedstudio.com/XIAO-ESP32S3-Sense-p-5639.html?srsltid=AfmBOoqlnJHk4DPgMnXNXsylaaDgI12FxYe6sk9a7pb1amkIAesnmNpG)

Kit includes:

- XIAO ESP32-S3 x1
- Plug-in camera sensor board x1
- Aluminum Heat Sink For XIAO x2
- 7 Pin Header x2
- Antenna x1

The BAT-pad and one-USB-at-a-time rules from [XIAO-ESP32S3.md](XIAO-ESP32S3.md) apply identically here.

- XIAO ESP32-S3 x1
- Plug-in camera sensor board x1
- Aluminum Heat Sink For XIAO x2
- 7 Pin Header x2
- Antenna x1

Note: From Sep 2, 2024, XIAO ESP32S3 Sense (113991115) ships with 2 heat sinks in China Warehouse. US&Germany warehouses ships new version from 2025.

Part numbers, vendors and masses live in [BOM.md](../docs/BOM.md), which is the single source of truth for both. Purchase history is in [shopping-list.md](../docs/shopping-list.md); the reasoning is in [design.md](../docs/design.md).
