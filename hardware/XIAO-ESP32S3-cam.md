# XIAO ESP32S3 — cam

__The XIAO that carries the camera.__ The copy that arrived in the Sense kit.

__This one has no headers soldered on.__ The Sense kit ships its two 7-pin strips loose. That is the only physical difference from [the lora copy](XIAO-ESP32S3-lora.md).

## What is mated to it

- __[Sense camera board](Sense-camera-board.md)__ — OV3660 camera and the microSD slot

Sensors reach it over __I2C on D4/D5__; the buzzer is __PWM on D0__. Firmware is __custom and not yet started__.

## Heights

__Datum: the bottom of the XIAO's PCB.__ Headers add __2.50 mm__ below it. Camera excluded.

| | Height | Above the carrier |
|---|---|---|
| A bare XIAO, to the top of the USB-C | __4.53 mm__ | 7.03 mm |
| __XIAO-ESP32S3-cam__ + [Sense camera board](Sense-camera-board.md) | __8.22 mm__ | __10.72 mm__ |
| __XIAO-ESP32S3-lora__ + [Wio-SX1262](Wio-SX1262-LoRa.md) | __9.32 mm__ | __11.82 mm__ |

So the Sense camera board adds __3.69 mm__ to a XIAO and the Wio-SX1262 adds __4.79 mm__.

```text
XIAO-ESP32S3-cam 10.72 + carrier 1.00 + XIAO-ESP32S3-lora 11.82 = 23.54 mm
available = 2 x sqrt(19.7^2 - 8.75^2)                           = 35.30 mm

11.76 mm spare
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

__The BAT pads are not on the castellated edge__, so the battery cannot reach this board through the headers. A soldered pigtail runs from the carrier's JST to those pads — and __solder the pigtail before the expansion board goes on__, because the pads are inaccessible afterwards.

__On battery power there is no voltage on the 5V pin__, so nothing can be fed from this board's 5V rail.

__Both XIAO chargers sit in parallel on one battery — charge through one USB port at a time.__

__Reversing a LiPo into a XIAO destroys it.__ The carrier silkscreens the pigtail polarity.

__The expansion board is the same outline as the XIAO__ (±8.75 mm against pads at ±8.5), which is why no carrier cutout can clear one: any hole wide enough removes the copper the pads solder to.

---

Part numbers, vendors and masses live in [BOM.md](../docs/BOM.md), which is the single source of truth for both. Purchase history is in [shopping-list.md](../docs/shopping-list.md); the reasoning is in [design.md](../docs/design.md).
