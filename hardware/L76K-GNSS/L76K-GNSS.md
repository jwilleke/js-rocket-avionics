# L76K GNSS

__Position for XIAO-ESP32S3-lora.__ Ships with an active antenna. __It mounts flat on the carrier, on its own footprint__ (operator, 2026-09-09) — it *can* plug onto a XIAO-ESP32S3-x's own 14 pads, and that is how it was planned until the stack was looked at.

## Specification

| | |
|---|---|
| Module | ≈__20 × 17 mm__, `QUECTEL L76K` |
| Interface | UART on __D6/D7__ |
| Mounting | __flat on the carrier, own footprint__ — top face, ~21 mm |
| Antenna | active patch, ≈__25 × 25 mm__, U.FL, __`ANT 50mA MAX`__ |

Why this module rather than a MAX-M10S is in [design.md](../../docs/design.md#the-gps-is-an-l76k-not-a-max-m10s).

## Photograph, on the grid

![L76K and its patch antenna on the measurement grid](L76K-GNSS.jpg)

Read off the grid — [module-pinouts.md](../../docs/module-pinouts.md#how-these-are-measured--photograph-on-the-grid-not-calipers):

| | Size |
|---|---|
| __L76K module__ | ≈ __20 × 17 mm__ |
| __Patch antenna__ | ≈ __25 × 25 mm__, on a flying U.FL lead |

Silkscreen: `QUECTEL L76K`, a U.FL connector, and __`ANT 50mA MAX`__ — the active antenna's current budget. __The outline now matters__, because the module takes a footprint: ~20 × 17 mm against the top face's free 74 mm.

## The antenna is the part worth looking at

> __The patch is ≈25 mm square — wider than the 24 mm carrier__, and it is the only part of this module that has to be placed rather than stacked. It is fine in a 40 mm bore, but it lands at the sled's forward end facing up, where it competes for the same space as the ballast.

__It is also the obvious candidate for the module's mass overrun.__ A 25 mm ceramic patch on a coax lead is not a rounding error against a ≈20 × 17 mm board. [BOM.md](../../docs/BOM.md) carries the open action: __weigh the module without its active antenna__. If the patch is most of the mass, the antenna is a separable choice.

## It needs no carrier footprint

Because it rides the XIAO stack, `GPS_TX`/`GPS_RX` stay in the netlist — the same node the module meets in the stack — but __nothing is placed for them__.

> __Riding the stack traded a footprint for an unmeasured mechanical unknown, and the trade was reversed.__ Whether this module cleared the [Wio-SX1262](../Wio-SX1262-LoRa/Wio-SX1262-LoRa.md) on the B2B had never been tested — the parcels arrived weeks apart — and the arrangement put the GPS, the radio and the MCU in one cantilevered column on header pins. __Flat on the carrier deletes the question instead of answering it.__ The mechanical half of [#6](https://github.com/jwilleke/js-rocket-avionics/issues/6) is closed by that decision rather than by a measurement.

## Antenna

__Active patch on U.FL__, at the sled's forward end, __facing up__, satisfying the "no metal above the patch" rule. Keep it __≥50 mm__ from the LoRa whip — see [Antennas.md](../Antennas/Antennas.md).

## The mass problem

__This module is the entire nose-mass overrun.__ It was specced light and weighs far more — heavier than the battery, and larger than the next two BOM rows combined. Four other parts came in under estimate and still did not cover it. Figures are in [BOM.md](../../docs/BOM.md), which owns them.

__Open action, from [BOM.md](../../docs/BOM.md): weigh it without its active antenna.__ If the antenna is most of the mass this is a separable choice; if it is not, the part was mis-specced roughly threefold.

---

Part numbers, vendors and masses live in [BOM.md](../../docs/BOM.md), which is the single source of truth for both. Purchase history is in [shopping-list.md](../../docs/shopping-list.md); the reasoning is in [design.md](../../docs/design.md).
