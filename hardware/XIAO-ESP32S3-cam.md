# XIAO ESP32S3 — cam

__The MCU of the [recorder](README.md#the-two-assemblies).__ The copy that arrived in the Sense kit.

__This one has no headers soldered on.__ The Sense kit ships its two 7-pin strips loose. That is the only physical difference from [the lora copy](XIAO-ESP32S3-lora.md).

## What is mated to it

- __[Sense camera board](Sense-camera-board.md)__ — OV3660 camera and the microSD slot

Sensors reach it over __I2C on D4/D5__; the buzzer is __PWM on D0__. Firmware is __custom and not yet started__.

## Height

Measured as part of the recorder stack — __10.7 mm__, mounting surface to tallest point with the camera excluded. See [Sense-camera-board.md](Sense-camera-board.md#the-stack).

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
