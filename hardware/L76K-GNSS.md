# L76K GNSS

__Position for the beacon.__ Plugs onto the XIAO's own 14 pads rather than presenting a header to the carrier, and ships with an active antenna.

## Why this one

The __MAX-M10S was rejected on 2026-08-06__: 44.2 × 30.5 mm — wider than the 24 mm carrier — and ~$60. The L76K is 18 × 21 mm, talks UART on __D6/D7__ (already in the netlist), and includes the active antenna.

## Photograph, on the grid

![L76K and its patch antenna on the measurement grid](../docs/resources/L76K-GNSS.jpg)

Read off the grid, __±0.2–0.3 mm__ — see [module-pinouts.md](../docs/module-pinouts.md#how-these-are-measured--photograph-on-the-grid-not-calipers):

| | Size |
|---|---|
| __L76K module__ | ≈ __20 × 17 mm__ |
| __Patch antenna__ | ≈ __25 × 25 mm__, on a flying U.FL lead |

The module reads slightly under the __18 × 21 mm__ quoted in [design.md](../docs/design.md) — within the method's error either way, and it does not matter, because __the module needs no carrier footprint at all__. Silkscreen confirms `QUECTEL L76K`, a U.FL connector, and __`ANT 50mA MAX`__ — the active antenna's current budget, which had not been recorded anywhere.

## The antenna is the part worth looking at

> __The patch is ≈25 mm square — wider than the 24 mm carrier__, and it is the only part of this module that has to be placed rather than stacked. It is fine in a 40 mm bore, but it lands at the sled's forward end facing up, where it competes for the same space as the ballast.

__It is also the obvious candidate for the mass overrun.__ [BOM.md](../docs/BOM.md)'s open action is to __weigh the module without its active antenna__, and the photograph makes the reason plain: a 25 mm ceramic patch on a coax lead is not a rounding error against the module's ≈20 × 17 mm board. If the patch is most of the mass, this is a separable choice rather than a mis-spec.

## It needs no carrier footprint

Because it rides the XIAO stack, `GPS_TX`/`GPS_RX` stay in the netlist — the same node the module meets in the stack — but __nothing is placed for them__.

> __That moves the risk from layout to stack height.__ Whether the L76K clears the Wio-SX1262 on the B2B is open, against ~2 mm of bore margin. __If it cannot ride the stack it comes back to the carrier as a footprint__, needing ~21 mm the 95 mm board has. [design.md](../docs/design.md) says settle it at the breadboard stage — [#6](https://github.com/jwilleke/js-rocket-avionics/issues/6).

## Antenna

__Active patch on U.FL__, at the sled's forward end, __facing up__, satisfying the "no metal above the patch" rule. Keep it __≥50 mm__ from the LoRa whip — see [Antennas.md](Antennas.md).

## The mass problem

__This module is the entire nose-mass overrun.__ It was specced light and weighs far more — heavier than the battery, and larger than the next two BOM rows combined. Four other parts came in under estimate and still did not cover it. Figures are in [BOM.md](../docs/BOM.md), which owns them.

__Open action, from [BOM.md](../docs/BOM.md): weigh it without its active antenna.__ If the antenna is most of the mass this is a separable choice; if it is not, the part was mis-specced roughly threefold.

## Open

- __Stack collision with the Wio-SX1262__ — [#6](https://github.com/jwilleke/js-rocket-avionics/issues/6)
- __Weigh it without the antenna__, and record the result in [BOM.md](../docs/BOM.md)
- __Time-to-first-fix unmeasured__

---

Part numbers, vendors and masses live in [BOM.md](../docs/BOM.md), which is the single source of truth for both. Purchase history is in [shopping-list.md](../docs/shopping-list.md); the reasoning is in [design.md](../docs/design.md).
