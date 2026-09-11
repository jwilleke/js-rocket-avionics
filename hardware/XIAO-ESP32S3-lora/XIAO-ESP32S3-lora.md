# XIAO ESP32S3 — lora

__The XIAO that carries the radio.__ The copy that arrived in the Wio-SX1262 kit.

## Which XIAO is this one

__You cannot tell by looking.__ It arrived with its 7-pin headers soldered on and [the cam copy](../XIAO-ESP32S3-cam/XIAO-ESP32S3-cam.md) did not; now both have them, and the two are the same part. __The only difference is what is loaded on them__ — and they have already been swapped once on the bench (2026-09-11, [#6](https://github.com/jwilleke/js-rocket-avionics/issues/6)): the Meshtastic XIAO sat on the cam breadboard, and the Wio-SX1262 on the one with Seeed's factory demo.

__Plug it into the Mac alone and read the port name:__

```sh
ls /dev/cu.usbmodem*
```

| | This one — XIAO-ESP32S3-lora | The cam copy, as delivered |
|---|---|---|
| Runs | __stock Meshtastic__, as the kit shipped it | Seeed's factory demo: prints `Hello from Seeed Studio XIAO ESP32-S3 Sense`, then a camera error |
| Port name | __long, letters and digits__, ending `CA481` — its serial number `…CA48` plus `1` | __short, digits only__, e.g. `usbmodem31101` — it changes with the USB socket |
| USB calls itself | `seeed_xiao_s3` | `USB JTAG_serial debug unit` |
| Phone app | shows up on Bluetooth | nothing |

__Mark it__ — a dot on the XIAO's shield — once the Wio-SX1262 is on it, so the question does not come back. The cam copy's identity lasts only until `bringup-cam` is loaded onto it, which replaces the demo.

## What is mated to it

- __[Wio-SX1262](../Wio-SX1262-LoRa/Wio-SX1262-LoRa.md)__ — the LoRa radio board
- __[L76K GNSS](../L76K-GNSS/L76K-GNSS.md)__ — UART on __D6/D7__

Runs __stock Meshtastic__, pre-flashed. No firmware is written for it.

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

> __This module's USB-C is not used in the flight build__ (operator, 2026-09-08). Charging and service go through the [Sense stack](../XIAO-ESP32S3-cam/XIAO-ESP32S3-cam.md) instead, because __this module runs stock Meshtastic and must never be reflashed__ — which is the whole reason there are two of them. Its port is reachable only by taking the nose apart. See [PCB-carrier.md](../PCB-carrier/PCB-carrier.md#charge-through-the-sense-stack-and-only-that-one).

__Reversing a LiPo into a XIAO destroys it.__ The carrier silkscreens the pigtail polarity.

__The expansion board is the same outline as the XIAO__ (±8.75 mm against pads at ±8.5), which is why no carrier cutout can clear one: any hole wide enough removes the copper the pads solder to.

---

Part numbers, vendors and masses live in [BOM.md](../../docs/BOM.md), which is the single source of truth for both. Purchase history is in [shopping-list.md](../../docs/shopping-list.md); the reasoning is in [design.md](../../docs/design.md).
