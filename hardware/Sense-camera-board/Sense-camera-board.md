# Sense camera board

__The expansion board that carries the OV3660 camera and the microSD slot.__ Mates to [XIAO-ESP32S3-cam](../XIAO-ESP32S3-cam/XIAO-ESP32S3-cam.md) via its B2B connector and sits __above__ it.

## What it is for

Camera and card. It is XIAO-ESP32S3-cam's only payload; everything else on that side — IMU, barometer, buzzer — sits on the carrier beside the XIAO, not on this board.

## Interfaces

| | |
|---|---|
| Carrier face | XIAO-ESP32S3-cam's — with LSM6DSO32, BMP388 and the buzzer |
| Position | __centred at carrier y = 18 mm__, which is what puts the camera at nose z 30..45 |
| Camera | __OV3660__ on a __DVP parallel bus__ — 14 GPIO plus I2C/SCCB for control. Frames land in PSRAM by DMA |
| microSD | SPI, on the expansion board — SCK GPIO7, MISO GPIO8, MOSI GPIO9, __CS GPIO21__ (shared with the user LED). Seeed's wiring, and what works: [microSD.md](../microSD/microSD.md#on-the-bench) |
| PSRAM | __8 MB__ on the XIAO (ESP32-S3R8) — where frames land |

__On the bench, 2026-09-12__ ([#7](https://github.com/jwilleke/js-rocket-avionics/issues/7)): the camera answers __PID `0x3660`__ over SCCB — the OV3660, read off the part, not the listing — and `bringup-cam` captured an __800 × 600 JPEG, 18 320 bytes__, and wrote it to the card. Without this board fitted, the camera driver reports `Detected camera not supported` (`0x106`) rather than "not found".

__Which carrier face is which sled azimuth is unsettled__, and it now matters: the Nosecone port is at azimuth 270° ([#13](https://github.com/jwilleke/js-rocket-avionics/issues/13)).

## Photographs

| [Expansion board](XIAO-ESP32S3-Sense-expansion.jpg) | [MCU module](../../docs/resources/XIAO-ESP32S3-module.jpg) |
|---|---|
| ![Sense expansion board with the camera fitted](XIAO-ESP32S3-Sense-expansion.jpg) | ![XIAO ESP32S3 module](../../docs/resources/XIAO-ESP32S3-module.jpg) |

| [Stack, side](../camera-stack/XIAO-ESP32S3-Sense-stack-side.jpg) | [Stack, end](../camera-stack/XIAO-ESP32S3-Sense-stack-end.jpg) |
|---|---|
| ![Assembled stack from the side](../camera-stack/XIAO-ESP32S3-Sense-stack-side.jpg) | ![Assembled stack end-on](../camera-stack/XIAO-ESP32S3-Sense-stack-end.jpg) |

## The stack

From the mounting surface up: __7-pin headers → [XIAO](../XIAO-ESP32S3-cam/XIAO-ESP32S3-cam.md) → this board → FPC connector__, with the camera on a __flexible ribbon__ above it.

| | |
|---|---|
| Height, __bottom of the XIAO's PCB__ to tallest point, camera excluded | __8.22 mm__ |
| Above the carrier, headers included | __10.72 mm__ |
| What this board adds to a bare XIAO | __3.69 mm__ |
| Header standoff | ~2.50 mm, the kit's standard 7-pin headers |
| This board | __above__ the XIAO |
| Camera | on a flexible ribbon — __its position is not fixed by the stack__ |

### The camera module

| | |
|---|---|
| Module body | __8 × 8 mm__ |
| Thickness | __5.52 mm__ — base, including its adhesive pad, to the top of the lens |
| Lens barrel | __6.9 mm OD at the base__, stepped to __~5 mm__ at the top |
| Glass, __across__ | __~3.5 mm__ — the clear aperture, and what sizes the port |
| Glass, __recess__ | __0.5–1.0 mm__ back inside the barrel. __A bracket, not a measurement__ — a depth down a 5 mm barrel is not a caliper reading and no point value is obtainable |
| Mounting | __adhesive pad on the module's base__ — the face opposite the lens |
| Ribbon, free length | __~8.5 mm__ — connector face to the module edge |

__The module's own thickness covers most of the gap.__ The connector sits ~__r 11.2 mm__ from the airframe axis and the bore wall is at __r 20.0__. With the barrel seated in the port's counterbore the module's base sits at __r 16.086__ (nose z 43.435), so the ribbon travels __4.886 mm__ radially against 8.5 mm free. Comfortable.

> __Read `r 14.48` in an older revision of this page as wrong.__ It assumed a *radial* port and no counterbore: 20.0 − 5.52. The port is tilted 30° aft, so the module's thickness costs only 5.52·cos 30 = 4.78 mm of radius, and the 1.0 mm counterbore puts the barrel a further 0.87 mm out.

__It is adhesive-backed__, so the 5.52 mm includes the pad and retention can be the pad plus a pocket lip.

> __The port is sized by the glass, not by the barrel.__ Light leaves only through the glass, so the barrel's 6.9 mm base and ~5 mm top are what a __pocket__ has to clear, not what the __hole__ has to be. Across a 4.2 mm collar wall a 25° half-angle cone widens by __3.92 mm__; on the tilted axis the path is 4.85 mm and it widens by 4.52.
>
> With a 3.5 mm glass that gives a port of __Ø4.0 at the bore face opening to Ø8.423 × 10.258 at the collar__ ([js-rocket#88](https://github.com/jwilleke/js-rocket/issues/88), cut 2026-09-06).
>
> __The recess is taken up by a counterbore, so it never reaches the cone.__ Every 1 mm the glass sits back would otherwise add 0.93 mm to the outer diameter — at the top of the bracket that is a cone short 0.93 mm at *both* faces, clipping the corners of the frame. Instead the port is counterbored __Ø7.2 × 1.0 mm__ at the bore face to receive the barrel's ~5 mm top step, cut for the top of the bracket so a 0.5 mm part just leaves the glass 0.5 mm outboard of the floor. The bracket stops mattering.
>
> __The counterbore floor is also what locates the camera__, and this page used to credit the bore wall. That was true while the port was radial; a barrel on a 30°-tilted axis meets the *cylindrical* bore on an ellipse and rocks on it. The counterbore floor is normal to the port axis, so the barrel seats flat — no clamp, nothing proud.

__The flex is not to be extended__ — the DVP bus runs a ~20 MHz XCLK. What is available is what is there.

### Optics

| | Active area | Diagonal |
|---|---|---|
| __OV3660__, 2048 × 1536 at 1.75 µm | 3.584 × 2.688 mm | __4.480 mm__ |

__The focal length of the fitted lens is not known__, and it is what sets the field of view — the sensor's format barely moves it. At f 4.8 the diagonal cone is 50.0°, at f 4.0 it is 58.5°, at f 3.0 it is 73.5°.

__The sensor reports PID `0x3660`__ over I2C at registers 0x300A/0x300B, which is how its identity is established from the die rather than from a label. An OV2640 reports `0x26`. It also does __QXGA 2048 × 1536__, where an OV2640 tops out at UXGA 1600 × 1200.

__Focus is adjustable__ via the M5/M6 lens thread. Hyperfocal at f/2.8 with a ~4.4 µm circle of confusion is ~1.9 m, so everything past ~1 m is sharp.

## Specification

[Seeed product page](https://www.seeedstudio.com/XIAO-ESP32S3-Sense-p-5639.html)

### What is in the kit, and what flies

| In the box | Flies | |
|---|---|---|
| XIAO ESP32-S3 × 1 | __yes__ | [XIAO-ESP32S3-cam](../XIAO-ESP32S3-cam/XIAO-ESP32S3-cam.md) |
| Plug-in camera sensor board × 1 | __yes__ | __this board__ |
| 7-pin header × 2 | __yes__ | loose in this kit — the cam XIAO has none soldered |
| Antenna × 1 — 2.4G A-02, WiFi/BLE | __no__ | [Antennas.md](../Antennas/Antennas.md) |
| __Aluminium heat sink for XIAO × 2__ | __no__ | see below |

> Seeed's note: *from 2 Sep 2024 the Sense (113991115) ships with 2 heat sinks from the China warehouse; US and Germany warehouses ship the new version from 2025.*

__The heat sinks are not used, and nothing in the design calls for them.__ Two reasons, both structural rather than thermal:

- __The face they are made for is occupied.__ They adhere to the module can on the XIAO's top face, and that is the face the expansion board mates to
- __A sealed PLA nose has no airflow.__ Fin area does nothing without convection; what a lump of aluminium would actually contribute is thermal __mass__, and the nose budget is already over target

If heat becomes a real question it will show up at bench bring-up, where both boards run on one battery with the camera active ([#8](https://github.com/jwilleke/js-rocket-avionics/issues/8)). Until then they stay in the box.

The BAT-pad and one-USB-at-a-time rules are on [XIAO-ESP32S3-cam.md](../XIAO-ESP32S3-cam/XIAO-ESP32S3-cam.md).

## Things that will catch you

__Do not extend the camera flex__ — the DVP bus runs a ~20 MHz XCLK. The camera may be __repositioned within the ribbon's existing reach__; it may not be given a longer one.

__Do not fit the wide-angle lens.__ The 120–160° M7 option cannot match the sensor's 25° chief ray angle, giving severe corner vignetting and colour crosstalk, and it would need a far larger hole in a load-bearing collar.

---

Part numbers, vendors and masses live in [BOM.md](../../docs/BOM.md), which is the single source of truth for both. Purchase history is in [shopping-list.md](../../docs/shopping-list.md); the reasoning is in [design.md](../../docs/design.md).
