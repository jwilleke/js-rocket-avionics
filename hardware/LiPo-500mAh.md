# LiPo cell

__One cell feeds both MCUs.__ Over an hour against a ~300 mA draw.

## Distribution

The cell lands on a __JST-PH on the carrier__, and short __soldered pigtails__ run to each XIAO's underside BAT pads. That indirection is forced, not chosen: __BAT+/BAT− are not on the castellated edge__, so the cell cannot reach a XIAO through the headers.

- __Solder the pigtails before fitting the expansion board.__ Seeed's wiki implies the pads are inaccessible afterwards
- __Both XIAO chargers sit in parallel on one cell — charge through one USB port at a time.__ This avoids adding a charge IC
- __On battery power there is no voltage on the 5V pin__
- __Reversing a LiPo into a XIAO destroys it__ — [design.md](../docs/design.md) requires the pigtail polarity be silkscreened
- __The battery straps to the sled, never hangs off the JST__

## The known risk, still unobserved

[BOM.md](../docs/BOM.md) accepts a coupling failure in writing: __*"a camera brownout on B can disturb A."*__ [design.md](../docs/design.md) repeats it — separate cells would isolate the boards but cost ~8 g the mass budget cannot afford.

__That is a prediction, not a measurement, and the thing it threatens is the recovery beacon.__ A camera write that resets board A mid-descent costs the rocket, not the video. Settling it is [#8](https://github.com/jwilleke/js-rocket-avionics/issues/8) — run both boards off one cell with the camera active, on a __partially discharged cell__ where sag is worst, and produce a verdict: acceptable, needs decoupling on the carrier, or needs the second cell after all.

__If decoupling is the answer it lands in the layout before the board is ordered__, not after.

## Rejected

__An 18650__ would put nose mass near the ~65 g weathercock limit.

## Open

- __The brownout verdict__ — [#8](https://github.com/jwilleke/js-rocket-avionics/issues/8)
- __Actual current draw and endurance unmeasured__ against the ~300 mA / over-an-hour claim
- __No JST footprint on the carrier yet__ — `VBAT` is marked *"footprint not yet placed"*, [#14](https://github.com/jwilleke/js-rocket-avionics/issues/14)

---

Part numbers, vendors and masses live in [BOM.md](../docs/BOM.md), which is the single source of truth for both. Purchase history is in [shopping-list.md](../docs/shopping-list.md); the reasoning is in [design.md](../docs/design.md).
