# XIAO ESP32S3 (plain) — board A

__The recovery beacon's MCU.__ Runs stock Meshtastic and carries the LoRa radio and the GNSS module in its own stack.

## What it is for

Board A exists so that __recovery does not depend on firmware anyone here has written__. [design.md](../docs/design.md) is blunt about why: a single-MCU design gates the first flight on custom firmware being *finished*, and *"the beacon __is__ the recovery system."*

It arrives __pre-flashed as a supported Meshtastic device__ when bought as the matched kit, so nothing is written for it. That is the whole premise of the board, and it is why the kit SKU matters more than the individual parts — see [Wio-SX1262-LoRa.md](Wio-SX1262-LoRa.md).

## Photograph

![XIAO ESP32S3 module on the measurement grid](../docs/resources/XIAO-ESP32S3-module.jpg)

__`Model: XIAO-ESP32-S3`, `FCC ID: Z4T-XIAOESP32S3`__, and the outline reads ~__17.5 × 21 mm__ on the grid, matching Seeed's package spec that the carrier's footprint was drawn from. Visible on the part: USB-C, the __U.FL connector__, the B2B connector along the bottom edge, and 14 castellated pads, 7 a side.

## Height

| | |
|---|---|
| Board, tallest point | __9.32 mm__ |
| Header standoff | __2.50 mm__ — the kit's standard 7-pin headers |
| __Above the carrier__ | __11.82 mm__ |

Board B's stack is [10.7 mm](XIAO-ESP32S3-Sense.md#the-stack) on the same basis. Two stacks plus a 1.0 mm carrier is __26.0 mm__ against __35.3 mm__ available at the XIAO's edge — `2 × √(19.7² − 8.75²)` — leaving __9.3 mm__.

## Interfaces

| | |
|---|---|
| Footprint | __14 pads, 3 × 2 mm__, rows 17.0 mm apart, pad inner edges at ±7.0, y −7.62..+7.62, 2.54 mm pitch. Board 17.5 × 21 mm |
| Stack | Mounts on __2×7 headers, ~14 mm standoff__, expansion board hanging in the gap — __~15 mm total__ above the carrier |
| Carrier face | __Top__, per [design.md](../docs/design.md) — with the Wio-SX1262 beneath it and the L76K in the same stack |
| GNSS | UART on __D6/D7__ |
| Power | __BAT+/BAT− are underside pads__ (footprint pads 16/17, 2.3 × 1.3 mm at x = −4.5) |

## Things that will catch you

__The BAT pads are not on the castellated edge__, so the cell cannot reach this board through the headers. A soldered pigtail runs from the carrier's JST to those pads — and [design.md](../docs/design.md) warns to __solder the pigtails before fitting the expansion board__, because Seeed's wiki implies the pads are inaccessible afterwards.

__On battery power there is no voltage on the 5V pin__, so nothing can be fed from this board's 5V rail.

__Both XIAO chargers sit in parallel on one cell — charge through one USB port at a time.__

__Reversing a LiPo into a XIAO destroys it.__ [design.md](../docs/design.md) requires the pigtail polarity be silkscreened on the carrier.

__The expansion board is the same outline as the XIAO__ (±8.75 mm against pads at ±8.5), which is what killed the twin-PCB plan: any cutout wide enough to clear it removes the copper the pads solder to.

---

Part numbers, vendors and masses live in [BOM.md](../docs/BOM.md), which is the single source of truth for both. Purchase history is in [shopping-list.md](../docs/shopping-list.md); the reasoning is in [design.md](../docs/design.md).
