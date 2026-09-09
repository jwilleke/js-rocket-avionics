# Hardware

__One page per part, and the source of truth for the hardware in use.__ What each part is, its interfaces and dimensions, and the traps that are properties of the object.

__These pages are not a history and not a task list.__ They say what is, not what changed or what to do next. Decisions and open work live in [issues](https://github.com/jwilleke/js-rocket-avionics/issues); what happened in a session lives in `private/project_log.md`; the reasoning behind the design lives in [design.md](../docs/design.md).

__These pages also fix the vocabulary.__ A part is called by the name of its page here — [XIAO-ESP32S3-cam](XIAO-ESP32S3-cam/XIAO-ESP32S3-cam.md) and [XIAO-ESP32S3-lora](XIAO-ESP32S3-lora/XIAO-ESP32S3-lora.md), never "board A" and "board B" — and where a page has a plain-English word for the thing, that word is the one to use. __The [LiPo-500mAh](LiPo-500mAh/LiPo-500mAh.md) is the battery.__ It is not "the cell": that is a word from datasheets, it reads as jargon to everyone who has to work on this, and one battery made of one cell gains nothing by the distinction.

## The names, and where they live

__One folder per part. The folder, the page inside it and the part all carry the same name.__ Adopted 2026-09-09. `hardware/BMP388-barometer/BMP388-barometer.md` — not `README.md`, because a folder that already names the part does not need a second word for it. __A part's own photographs live in its folder__, beside its page.

__These are the names. Nothing else is a name for these things:__

| Folder and page | Is |
|---|---|
| `XIAO-ESP32S3-cam` | The MCU module carrying the camera. Never "board B", never "the Sense one" |
| `XIAO-ESP32S3-lora` | The MCU module carrying the radio. Never "board A" |
| `Sense-camera-board` | The expansion board on XIAO-ESP32S3-cam |
| `Wio-SX1262-LoRa` | The LoRa radio |
| `L76K-GNSS` | The GNSS module |
| `LSM6DSO32` | The IMU |
| `BMP388-barometer` | The barometer |
| `PS1240-buzzer` | The buzzer |
| `LiPo-500mAh` | __The battery.__ Never "the cell" |
| `Arming-switch` | The arming switch. __Not the JST__, which is a connector |
| `Stacking-headers` | The 7-pin strips |
| `Antennas` | Both U.FL antennas |
| `microSD` | The card |
| `PCB-carrier` | The carrier board |
| `camera-stack` | XIAO-ESP32S3-cam __with__ its Sense board — the assembly, not either part |
| `GNSS-stack` | __A rejected arrangement, not a thing that exists.__ Kept so it is not proposed again |

__Where a part has no folder here, it is not a part of this payload.__ "XIAO" on its own is not a name: there are two of them and they are not interchangeable.

__Two exceptions to "photographs live with the part".__ [`docs/resources/`](../docs/resources/) keeps the images that belong to __both__ XIAO modules — the front and back pinouts, the module and underside shots — because they document the model rather than either role, and a second copy is a copy that drifts. [`docs/bench-work/`](../docs/bench-work/) keeps what belongs to no part at all: the breadboard drawing, the bench photograph and the measurement grid.

__These pages hold no part numbers and no masses.__ [BOM.md](../docs/BOM.md) owns both and says so: *"anything else that quotes a part number or a mass is wrong — link here instead."* A number in two places is a number that will disagree with itself.

| | Page | Goes with | Photos | What it is |
|---|---|---|---|---|
| MCU | [XIAO-ESP32S3-lora.md](XIAO-ESP32S3-lora/XIAO-ESP32S3-lora.md) | — | grid | The MCU module. __Headers already soldered on__ |
| MCU | [XIAO-ESP32S3-cam.md](XIAO-ESP32S3-cam/XIAO-ESP32S3-cam.md) | — | grid | The MCU module. __No headers soldered__ |
| Payload | [Sense-camera-board.md](Sense-camera-board/Sense-camera-board.md) | XIAO-ESP32S3-cam | grid ×2 | OV3660 camera and the microSD slot |
| Radio | [Wio-SX1262-LoRa.md](Wio-SX1262-LoRa/Wio-SX1262-LoRa.md) | XIAO-ESP32S3-lora | grid | LoRa. Buy as the matched kit, never separately |
| GNSS | [L76K-GNSS.md](L76K-GNSS/L76K-GNSS.md) | XIAO-ESP32S3-lora | grid | Position. __Flat on the carrier's top face__, own footprint |
| Sensor | [LSM6DSO32.md](LSM6DSO32/LSM6DSO32.md) | carrier | grid + back | ±32 g IMU with a 9 KB FIFO |
| Sensor | [BMP388-barometer.md](BMP388-barometer/BMP388-barometer.md) | carrier | grid + 2 close | Unported barometer, 0x77 |
| Output | [PS1240-buzzer.md](PS1240-buzzer/PS1240-buzzer.md) | carrier | __none__ | Passive piezo. The only status channel on the pad |
| Power | [LiPo-500mAh.md](LiPo-500mAh/LiPo-500mAh.md) | carrier | __none__ | One battery, both XIAOs |
| Power | [Arming-switch.md](Arming-switch/Arming-switch.md) | battery lead | __n/a__ | In the battery line. __Flight 3 carries none__ |
| Storage | [microSD.md](microSD/microSD.md) | Sense camera board | __none__ | Video only |
| RF | [Antennas.md](Antennas/Antennas.md) | Wio-SX1262, L76K | grid | Both off-board on U.FL. ≥50 mm apart |
| Mechanical | [Stacking-headers.md](Stacking-headers/Stacking-headers.md) | both XIAOs | __none__ | 7-pin strips, ~2.50 mm standoff |
| Mechanical | [PCB-carrier.md](PCB-carrier/PCB-carrier.md) | everything | __n/a__ | The board, and the sled's structural span |
| Assembly | [camera-stack.md](camera-stack/camera-stack.md) | — | end + side | XIAO-ESP32S3-cam with its Sense board, as one object |
| Assembly | [GNSS-stack.md](GNSS-stack/GNSS-stack.md) | — | __none__ | __Rejected.__ Why the L76K is not in a stack |

## Photographs

__Each part's images live in that part's folder__, beside its page; the two shared XIAO images stay in [`docs/resources/`](../docs/resources/). Every one is embedded on the page above. __Shot on the printed measurement grid__ — part flat, square-on, calibration bar in frame. Method and its precision: [module-pinouts.md](../docs/module-pinouts.md#how-these-are-measured--photograph-on-the-grid-not-calipers).

| Image | Part | What it is for |
|---|---|---|
| [`BMP388-front-grid.jpg`](BMP388-barometer/BMP388-front-grid.jpg) | BMP388 | __Dimensional record.__ Header row along the bottom, mounting holes at the top corners |
| [`BMP388-front.jpg`](BMP388-barometer/BMP388-front.jpg) | BMP388 | Close-up. Confirms pin order on the silkscreen |
| [`BMP388-back.jpg`](BMP388-barometer/BMP388-back.jpg) | BMP388 | Close-up. Address jumper, `3 V` marking |
| [`LSM6DSO32-front.jpg`](LSM6DSO32/LSM6DSO32-front.jpg) | LSM6DSO32 | __Dimensional record.__ Both header rows and both mounting holes |
| [`LSM6DSO32-back.jpg`](LSM6DSO32/LSM6DSO32-back.jpg) | LSM6DSO32 | Close-up. `ST LSM6DSO32`, ±32 g, `0x6A` |
| [`L76K-GNSS.jpg`](L76K-GNSS/L76K-GNSS.jpg) | L76K | Module and its ≈25 mm patch antenna, to scale |
| [`Wio-SX1262-LoRa.jpg`](Wio-SX1262-LoRa/Wio-SX1262-LoRa.jpg) | Wio-SX1262 | FCC ID, U.FL, and the 2×5 header currently fitted |
| [`Wio-SX1262-LoRa-antennas.jpg`](Wio-SX1262-LoRa/Wio-SX1262-LoRa-antennas.jpg) | Antennas | Both Seeed strips, to scale |
| [`XIAO-ESP32S3-module.jpg`](../docs/resources/XIAO-ESP32S3-module.jpg) | XIAO ×2 | The MCU board. USB-C, U.FL, B2B, 14 pads |
| [`XIAO-ESP32-S3-bottom.jpg`](../docs/resources/XIAO-ESP32-S3-bottom.jpg) | XIAO ×2 | __The pin labels.__ Underside, where the silkscreen is — the only reading that confirms pad 1 is `D0`. See [module-pinouts.md](../docs/module-pinouts.md#xiao-esp32s3--read-off-the-underside-2026-09-08) |
| [`XIAO-ESP32S3-Sense-expansion.jpg`](Sense-camera-board/XIAO-ESP32S3-Sense-expansion.jpg) | Sense | Camera and microSD board |
| [`XIAO-ESP32S3-Sense-stack-end.jpg`](camera-stack/XIAO-ESP32S3-Sense-stack-end.jpg) | camera-stack | __End-on.__ Settled that the expansion board mates to the front face and sits above |
| [`XIAO-ESP32S3-Sense-stack-side.jpg`](camera-stack/XIAO-ESP32S3-Sense-stack-side.jpg) | camera-stack | The same assembly from the side |

## The two stacks

__Name everything by its page.__ There is no "board A", no "board B", and no functional nickname — the two MCU modules are told apart by which expansion board is on them, which is what their filenames say.

| | Mated to it | Firmware |
|---|---|---|
| __XIAO-ESP32S3-lora__ | [Wio-SX1262](Wio-SX1262-LoRa/Wio-SX1262-LoRa.md) radio, [L76K](L76K-GNSS/L76K-GNSS.md) GNSS | __none written__ — stock Meshtastic, pre-flashed |
| __XIAO-ESP32S3-cam__ | [Sense camera board](Sense-camera-board/Sense-camera-board.md) | custom, not started |

__The two XIAO modules are the same part but not interchangeable in practice__ — the lora one arrived with its 7-pin headers soldered on, the cam one did not.

Both ride the one [carrier PCB](PCB-carrier/PCB-carrier.md), on opposite faces. The IMU, barometer and buzzer sit on the carrier itself, not on either expansion board.

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
- __Bench drawings and the measurement grid__ — [`docs/bench-work/`](../docs/bench-work/)

---

Part numbers, vendors and masses live in [BOM.md](../docs/BOM.md), which is the single source of truth for both. Purchase history is in [shopping-list.md](../docs/shopping-list.md); the reasoning is in [design.md](../docs/design.md).
