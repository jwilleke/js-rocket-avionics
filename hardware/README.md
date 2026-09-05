# Hardware

__One page per part.__ What it is, what it is for, the interfaces, and the traps — the things that are true about the physical object rather than about the design as a whole.

__These pages hold no part numbers and no masses.__ [BOM.md](../docs/BOM.md) owns both and says so: *"anything else that quotes a part number or a mass is wrong — link here instead."* A number in two places is a number that will disagree with itself.

| | Page | Board | Role |
|---|---|---|---|
| MCU | [XIAO-ESP32S3.md](XIAO-ESP32S3.md) | __A__ | Recovery beacon. Stock Meshtastic, no firmware written |
| MCU | [XIAO-ESP32S3-Sense.md](XIAO-ESP32S3-Sense.md) | __B__ | Flight recorder. Camera, microSD, PSRAM log |
| Radio | [Wio-SX1262-LoRa.md](Wio-SX1262-LoRa.md) | A | LoRa. Buy as the matched kit, never separately |
| GNSS | [L76K-GNSS.md](L76K-GNSS.md) | A | Position. Rides the XIAO stack, no carrier footprint |
| Sensor | [LSM6DSO32.md](LSM6DSO32.md) | B | ±32 g IMU. __The part blocking every footprint__ |
| Sensor | [BMP388-barometer.md](BMP388-barometer.md) | B | Unported barometer. The only module measured off the part |
| Output | [PS1240-buzzer.md](PS1240-buzzer.md) | B | Passive piezo. The only status channel on the pad |
| Power | [LiPo-500mAh.md](LiPo-500mAh.md) | shared | One cell, both MCUs |
| Power | [Arming-switch.md](Arming-switch.md) | shared | In the battery line. __Not chosen, not bought__ |
| Storage | [microSD.md](microSD.md) | B | Video only |
| RF | [Antennas.md](Antennas.md) | A | Both off-board on U.FL. ≥50 mm apart |
| Mechanical | [Stacking-headers.md](Stacking-headers.md) | both | ~14 mm standoff. __Unverified__ |
| Mechanical | [PCB-carrier.md](PCB-carrier.md) | both | The board, and the sled's structural span |

## What is not here

- __KiCad sources__ — `carrier/`
- __Generators__ — `scripts/`, including `gen_carrier.py`
- __Measured pin order and caliper readings__ — [module-pinouts.md](../docs/module-pinouts.md)
- __Why it is built this way__ — [design.md](../docs/design.md)

## The three things not bought

Everything ordered is in hand. Three items are not:

- __The carrier PCB__ — deliberately, behind [#4](https://github.com/jwilleke/js-rocket-avionics/issues/4)
- __The 2×7 stacking headers__ — believed held, __unverified__, and not a generic part
- __The arming switch__ — no part chosen

---

Part numbers, vendors and masses live in [BOM.md](../docs/BOM.md), which is the single source of truth for both. Purchase history is in [shopping-list.md](../docs/shopping-list.md); the reasoning is in [design.md](../docs/design.md).
