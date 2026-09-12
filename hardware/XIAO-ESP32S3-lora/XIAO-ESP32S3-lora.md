# XIAO ESP32S3 — lora

__The XIAO that carries the radio.__ The copy that arrived in the Wio-SX1262 kit.

## Which XIAO is this one

__You cannot tell by looking.__ It arrived with its 7-pin headers soldered on and [the cam copy](../XIAO-ESP32S3-cam/XIAO-ESP32S3-cam.md) did not; now both have them, and the two are the same part. __The only difference is what is loaded on them__ — and they have already been swapped once on the bench (2026-09-11, [#6](https://github.com/jwilleke/js-rocket-avionics/issues/6)): the Meshtastic XIAO sat on the cam breadboard, and the Wio-SX1262 on the one with Seeed's factory demo.

__Plug it into the Mac alone and read the port name:__

```sh
ls /dev/cu.usbmodem*
```

| | This one — XIAO-ESP32S3-lora | [The cam copy](../XIAO-ESP32S3-cam/XIAO-ESP32S3-cam.md#on-the-bench) |
|---|---|---|
| __Chip MAC__ — the one sure test | __`68:ee:8f:60:ca:48`__ | __`e0:72:a1:fa:41:30`__ |
| Runs | __stock Meshtastic__, as the kit shipped it | `bringup-cam` since 2026-09-12. Before that, Seeed's factory demo: `Hello from Seeed Studio XIAO ESP32-S3 Sense`, then a camera error |
| Port name | __long, letters and digits__, ending `CA481` — its serial number `…CA48` plus `1` | __short, digits only__, e.g. `usbmodem31101` — it changes with the USB socket |
| USB calls itself | `seeed_xiao_s3` | `USB JTAG_serial debug unit` |
| Phone app | shows up on Bluetooth | nothing |

__Not in bootloader mode.__ While being flashed, __any__ XIAO shows up as `USB JTAG_serial debug unit` on a short port — including this one — so the port name is no guide then. __The chip's MAC is__: the upload tool prints it first, and this one is __`68:ee:8f:60:ca:48`__. Check it before writing anything.

__Mark it__ — a dot on the XIAO's shield — once the Wio-SX1262 is on it, so the question does not come back. The cam copy's identity lasts only until `bringup-cam` is loaded onto it, which replaces the demo.

## What is mated to it

- __[Wio-SX1262](../Wio-SX1262-LoRa/Wio-SX1262-LoRa.md)__ — the LoRa radio board
- __[L76K GNSS](../L76K-GNSS/L76K-GNSS.md)__ — UART on __D6/D7__

Runs __stock Meshtastic__, pre-flashed. No firmware is written for it. Version and settings as delivered: [Wio-SX1262-LoRa.md](../Wio-SX1262-LoRa/Wio-SX1262-LoRa.md#meshtastic-as-the-kit-delivered-it).

## Firmware — stock Meshtastic only, updated on purpose, frozen for flight

__The rule__ (operator, 2026-09-12; it replaces "must never be reflashed"): this XIAO carries __only official Meshtastic releases__ for its board, `seeed-xiao-s3` — never our code, never a build of our own. The point is the one it always was: __a recovery beacon our bugs cannot break.__ Updating stock firmware does not threaten that; writing firmware for it would.

- __Update on purpose__, not because the phone app offers one — and not mid-test: a bench check runs on the version it started on
- __Freeze for flight.__ Pick the version before the flight, put the same one on the ground receiver ([#23](https://github.com/jwilleke/js-rocket-avionics/issues/23)), and do not touch either until after it

__How it is updated__ — the official release bundle and Meshtastic's own update step, done from the Mac:

1. __Back up the settings__: `meshtastic --export-config > private/meshtastic-ca48-config-<version>.yaml`. It holds the channel key, so it goes in `private/`, which git ignores
2. __Download the release__ from [meshtastic/firmware](https://github.com/meshtastic/firmware/releases): `firmware-esp32s3-<version>.zip`. Take `firmware-seeed-xiao-s3-<version>.bin` and check its MD5 against the bundle's `.mt.json`
3. __Into bootloader mode__ by a 1200-baud touch on its port, then __check the MAC is `68:ee:8f:60:ca:48`__ — see [which XIAO is this one](#which-xiao-is-this-one)
4. __Write the program slot only__ — `esptool write-flash 0x10000 firmware-seeed-xiao-s3-<version>.bin`, which is what the bundle's `device-update.sh` does. Settings survive
5. __Read back__ the version, region, channel and GPS mode. If it boot-loops instead, the fallback is a full erase and install, then `meshtastic --configure` from the backup

__Its memory layout is older than current releases.__ The on-board partition table dates from the version it shipped with (a 2.4 MB program slot); 2.7.26 is built for a 3.3 MB one. The update still fits, and worked. If a future release outgrows the old slot, the update step will not do and a full install is needed — check the `.bin` size against the slot first.

| Date | From → to | How | Result |
|---|---|---|---|
| 2026-09-12 | `2.7.15.567b8ea` → __`2.7.26.54e0d8d`__ | program slot only, from the Mac | boots; region, channel, key, Bluetooth and GPS settings all kept. Backup: `private/meshtastic-ca48-config-2.7.15.yaml` |

## Heights

__Datum: the bottom of the XIAO's PCB.__ Headers add __2.50 mm__ below it. Camera excluded.

| | Height | Above the carrier |
|---|---|---|
| A bare XIAO, to the top of the USB-C | __4.53 mm__ | 7.03 mm |
| __XIAO-ESP32S3-cam__ + [Sense camera board](../Sense-camera-board/Sense-camera-board.md) | __8.22 mm__ | __10.72 mm__ |
| __XIAO-ESP32S3-lora__ + [Wio-SX1262](../Wio-SX1262-LoRa/Wio-SX1262-LoRa.md) | __9.32 mm__ | __11.82 mm__ |

So the Sense camera board adds __3.69 mm__ to a XIAO and the Wio-SX1262 adds __4.79 mm__.

```text
XIAO-ESP32S3-cam 10.72 + carrier 1.00 + XIAO-ESP32S3-lora 11.82 = 23.54 mm
available = 2 x sqrt(19.7^2 - 8.75^2)                           = 35.30 mm

11.76 mm spare
```

## Photograph

![XIAO ESP32S3 module on the measurement grid](../../docs/resources/XIAO-ESP32S3-module.jpg)

## The module

Both copies are the same part — `Model: XIAO-ESP32-S3`, `FCC ID: Z4T-XIAOESP32S3` — and identical electrically. They differ only in what has been done to them and what is mated to them.

| | |
|---|---|
| Outline | __17.5 × 21 mm__ |
| Pads | __14 castellated__, two rows of 7, rows __17.0 mm apart__, pitch __2.54 mm__, pads 3 × 2 mm |
| Connectors | USB-C, __U.FL__, and the B2B connector an expansion board mates to |
| PSRAM | __8 MB__ (ESP32-S3R8) |
| Battery | __BAT+/BAT− are underside pads__ (footprint pads 16/17, 2.3 × 1.3 mm at x = −4.5), __not on the castellated edge__ |

## Things that will catch you

__The BAT pads are not on the castellated edge__, so the battery cannot reach this board through the headers. A soldered pigtail runs from the carrier's JST to those pads — and __solder the pigtail before the expansion board goes on__, because the pads are inaccessible afterwards.

__On battery power there is no voltage on the 5V pin__, so nothing can be fed from this board's 5V rail.

__Both XIAO chargers sit in parallel on one battery — charge through one USB port at a time.__

> __This module's USB-C is not used in the flight build__ (operator, 2026-09-08). Charging and service go through the [Sense stack](../XIAO-ESP32S3-cam/XIAO-ESP32S3-cam.md) instead, because __this module runs stock Meshtastic and nothing else__ ([the firmware rule](#firmware--stock-meshtastic-only-updated-on-purpose-frozen-for-flight)) — which is the whole reason there are two of them. Its port is reachable only by taking the nose apart. See [PCB-carrier.md](../PCB-carrier/PCB-carrier.md#charge-through-the-sense-stack-and-only-that-one).

__Reversing a LiPo into a XIAO destroys it.__ The carrier silkscreens the pigtail polarity.

__The expansion board is the same outline as the XIAO__ (±8.75 mm against pads at ±8.5), which is why no carrier cutout can clear one: any hole wide enough removes the copper the pads solder to.

---

Part numbers, vendors and masses live in [BOM.md](../../docs/BOM.md), which is the single source of truth for both. Purchase history is in [shopping-list.md](../../docs/shopping-list.md); the reasoning is in [design.md](../../docs/design.md).
