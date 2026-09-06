# XIAO ESP32S3 — lora

__The MCU of the [beacon](README.md#the-two-assemblies).__ The copy that arrived in the Wio-SX1262 kit.

__This one has its 7-pin headers already soldered on.__ That is the only physical difference from [the cam copy](XIAO-ESP32S3-cam.md).

## What is mated to it

- __[Wio-SX1262](Wio-SX1262-LoRa.md)__ — the LoRa radio board
- __[L76K GNSS](L76K-GNSS.md)__ — UART on __D6/D7__

Runs __stock Meshtastic__, pre-flashed. No firmware is written for it.

## Heights

__Datum: the bottom of the XIAO's PCB.__ Headers add __2.50 mm__ below it.

| | Height | Above the carrier |
|---|---|---|
| Bare module, to the top of the USB-C | __4.53 mm__ | 7.03 mm |
| __beacon__ — XIAO + [Wio-SX1262](Wio-SX1262-LoRa.md) | __9.32 mm__ | __11.82 mm__ |
| __recorder__ — XIAO + [camera board](Sense-camera-board.md), camera excluded | __10.70 mm__ | __13.20 mm__ |

So the radio board adds __4.79 mm__ to a XIAO and the camera board adds __6.17 mm__.

```text
beacon 11.82 + carrier 1.00 + recorder 13.20 = 26.02 mm
available = 2 x sqrt(19.7^2 - 8.75^2)        = 35.30 mm     9.3 mm spare
```

## Photograph

![XIAO ESP32S3 module on the measurement grid](../docs/resources/XIAO-ESP32S3-module.jpg)

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

__The BAT pads are not on the castellated edge__, so the cell cannot reach this board through the headers. A soldered pigtail runs from the carrier's JST to those pads — and __solder the pigtail before the expansion board goes on__, because the pads are inaccessible afterwards.

__On battery power there is no voltage on the 5V pin__, so nothing can be fed from this board's 5V rail.

__Both XIAO chargers sit in parallel on one cell — charge through one USB port at a time.__

__Reversing a LiPo into a XIAO destroys it.__ The carrier silkscreens the pigtail polarity.

__The expansion board is the same outline as the XIAO__ (±8.75 mm against pads at ±8.5), which is why no carrier cutout can clear one: any hole wide enough removes the copper the pads solder to.

---

Part numbers, vendors and masses live in [BOM.md](../docs/BOM.md), which is the single source of truth for both. Purchase history is in [shopping-list.md](../docs/shopping-list.md); the reasoning is in [design.md](../docs/design.md).
