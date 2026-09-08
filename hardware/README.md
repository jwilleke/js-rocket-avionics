# Hardware

__One page per part, and the source of truth for the hardware in use.__ What each part is, its interfaces and dimensions, and the traps that are properties of the object.

__These pages are not a history and not a task list.__ They say what is, not what changed or what to do next. Decisions and open work live in [issues](https://github.com/jwilleke/js-rocket-avionics/issues); what happened in a session lives in `private/project_log.md`; the reasoning behind the design lives in [design.md](../docs/design.md).

__These pages also fix the vocabulary.__ A part is called by the name of its page here — [XIAO-ESP32S3-cam](XIAO-ESP32S3-cam.md) and [XIAO-ESP32S3-lora](XIAO-ESP32S3-lora.md), never "board A" and "board B" — and where a page has a plain-English word for the thing, that word is the one to use. __The [LiPo-500mAh](LiPo-500mAh.md) is the battery.__ It is not "the cell": that is a word from datasheets, it reads as jargon to everyone who has to work on this, and one battery made of one cell gains nothing by the distinction.

__These pages hold no part numbers and no masses.__ [BOM.md](../docs/BOM.md) owns both and says so: *"anything else that quotes a part number or a mass is wrong — link here instead."* A number in two places is a number that will disagree with itself.

| | Page | Goes with | Photos | What it is |
|---|---|---|---|---|
| MCU | [XIAO-ESP32S3-lora.md](XIAO-ESP32S3-lora.md) | — | grid | The MCU module. __Headers already soldered on__ |
| MCU | [XIAO-ESP32S3-cam.md](XIAO-ESP32S3-cam.md) | — | grid | The MCU module. __No headers soldered__ |
| Payload | [Sense-camera-board.md](Sense-camera-board.md) | XIAO-ESP32S3-cam | grid ×2 | OV3660 camera and the microSD slot |
| Radio | [Wio-SX1262-LoRa.md](Wio-SX1262-LoRa.md) | XIAO-ESP32S3-lora | grid | LoRa. Buy as the matched kit, never separately |
| GNSS | [L76K-GNSS.md](L76K-GNSS.md) | XIAO-ESP32S3-lora | grid | Position. Rides the XIAO stack, no carrier footprint |
| Sensor | [LSM6DSO32.md](LSM6DSO32.md) | carrier | grid + back | ±32 g IMU with a 9 KB FIFO |
| Sensor | [BMP388-barometer.md](BMP388-barometer.md) | carrier | grid + 2 close | Unported barometer, 0x77 |
| Output | [PS1240-buzzer.md](PS1240-buzzer.md) | carrier | __none__ | Passive piezo. The only status channel on the pad |
| Power | [LiPo-500mAh.md](LiPo-500mAh.md) | carrier | __none__ | One battery, both XIAOs |
| Power | [Arming-switch.md](Arming-switch.md) | carrier | __n/a__ | Pull-pin and microswitch, in the battery line |
| Storage | [microSD.md](microSD.md) | Sense camera board | __none__ | Video only |
| RF | [Antennas.md](Antennas.md) | Wio-SX1262, L76K | grid | Both off-board on U.FL. ≥50 mm apart |
| Mechanical | [Stacking-headers.md](Stacking-headers.md) | both XIAOs | __none__ | 7-pin strips, ~2.50 mm standoff |
| Mechanical | [PCB-carrier.md](PCB-carrier.md) | everything | __n/a__ | The board, and the sled's structural span |

## Photographs

Every image lives in [`docs/resources/`](../docs/resources/) and is embedded on the part page above. __Shot on the printed measurement grid__ — part flat, square-on, calibration bar in frame. Method and its precision: [module-pinouts.md](../docs/module-pinouts.md#how-these-are-measured--photograph-on-the-grid-not-calipers).

| Image | Part | What it is for |
|---|---|---|
| [`BMP388-front-grid.jpg`](../docs/resources/BMP388-front-grid.jpg) | BMP388 | __Dimensional record.__ Header row along the bottom, mounting holes at the top corners |
| [`BMP388-front.jpg`](../docs/resources/BMP388-front.jpg) | BMP388 | Close-up. Confirms pin order on the silkscreen |
| [`BMP388-back.jpg`](../docs/resources/BMP388-back.jpg) | BMP388 | Close-up. Address jumper, `3 V` marking |
| [`LSM6DSO32-front.jpg`](../docs/resources/LSM6DSO32-front.jpg) | LSM6DSO32 | __Dimensional record.__ Both header rows and both mounting holes |
| [`LSM6DSO32-back.jpg`](../docs/resources/LSM6DSO32-back.jpg) | LSM6DSO32 | Close-up. `ST LSM6DSO32`, ±32 g, `0x6A` |
| [`L76K-GNSS.jpg`](../docs/resources/L76K-GNSS.jpg) | L76K | Module and its ≈25 mm patch antenna, to scale |
| [`Wio-SX1262-LoRa.jpg`](../docs/resources/Wio-SX1262-LoRa.jpg) | Wio-SX1262 | FCC ID, U.FL, and the 2×5 header currently fitted |
| [`Wio-SX1262-LoRa-antennas.jpg`](../docs/resources/Wio-SX1262-LoRa-antennas.jpg) | Antennas | Both Seeed strips, to scale |
| [`XIAO-ESP32S3-module.jpg`](../docs/resources/XIAO-ESP32S3-module.jpg) | XIAO ×2 | The MCU board. USB-C, U.FL, B2B, 14 pads |
| [`XIAO-ESP32-S3-bottom.jpg`](../docs/resources/XIAO-ESP32-S3-bottom.jpg) | XIAO ×2 | __The pin labels.__ Underside, where the silkscreen is — the only reading that confirms pad 1 is `D0`. See [module-pinouts.md](../docs/module-pinouts.md#xiao-esp32s3--read-off-the-underside-2026-09-08) |
| [`XIAO-ESP32S3-Sense-expansion.jpg`](../docs/resources/XIAO-ESP32S3-Sense-expansion.jpg) | Sense | Camera and microSD board |

## The two stacks

__Name everything by its page.__ There is no "board A", no "board B", and no functional nickname — the two MCU modules are told apart by which expansion board is on them, which is what their filenames say.

| | Mated to it | Firmware |
|---|---|---|
| __XIAO-ESP32S3-lora__ | [Wio-SX1262](Wio-SX1262-LoRa.md) radio, [L76K](L76K-GNSS.md) GNSS | __none written__ — stock Meshtastic, pre-flashed |
| __XIAO-ESP32S3-cam__ | [Sense camera board](Sense-camera-board.md) | custom, not started |

__The two XIAO modules are the same part but not interchangeable in practice__ — the lora one arrived with its 7-pin headers soldered on, the cam one did not.

Both ride the one [carrier PCB](PCB-carrier.md), on opposite faces. The IMU, barometer and buzzer sit on the carrier itself, not on either expansion board.

## Fasteners — M2 everywhere

__Every board mounting screw on this payload is M2.__ Decided by the operator on 2026-09-05, and it is a standard rather than a per-board reading:

- __M3 does not fit these breakouts.__ There is no version of this where a 3 mm screw goes through a STEMMA QT mounting hole
- __Nothing 2.5 mm is being bought.__ Adafruit publishes 2.5 mm holes on parts whose holes actually measure __Ø2.35__ — an M2.5 does not pass, and stocking a second size to chase a datasheet figure buys nothing

So a board's measured hole diameter is __not__ an input to the footprint; it only has to clear an M2. What still matters per board is __hole spacing__, which no standard can supply.

__Printed bosses are modelled oversize.__ A hole modelled at nominal prints undersize by ~0.3 mm on the P2S, so sled bosses are drawn for M2 clearance rather than to a measured 2.35 — the same rule as the anchor bore in the rocket repo.

## What is not here

- __KiCad sources__ — `carrier/`
- __Generators__ — `scripts/`, including `gen_carrier.py`
- __Measured pin order and caliper readings__ — [module-pinouts.md](../docs/module-pinouts.md)
- __Why it is built this way__ — [design.md](../docs/design.md)

---

Part numbers, vendors and masses live in [BOM.md](../docs/BOM.md), which is the single source of truth for both. Purchase history is in [shopping-list.md](../docs/shopping-list.md); the reasoning is in [design.md](../docs/design.md).
