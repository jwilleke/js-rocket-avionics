# Headers

__Two 7-pin strips per XIAO__, one down each long edge, connecting the XIAO's 14 castellated pads to the carrier.

## What is in the kit

The XIAO ESP32S3 Sense kit ships __`7 Pin Header × 2`__ — one pair, for one XIAO. Two XIAOs need __four strips__.

__They are standard male headers: the board sits ~2.50 mm above whatever they are soldered to.__

## The pad geometry they have to match

The XIAO presents __14 pads, two rows of 7__, rows __17.0 mm apart__, pitch __2.54 mm__.

> __A dual-row `2×7` header does not fit and never could__ — its two rows are 2.54 mm apart, not 17.0. The part is __two separate 1×7 strips__, spaced by the board. Where a document says "2×7", it means two 7-pin headers.

## The gap under the XIAO is the open question

The expansion board — Sense camera or Wio-SX1262 — mates to the XIAO's __B2B connector on its underside__ and therefore hangs __below__ the XIAO. Whatever the headers stand the XIAO off by has to clear it.

__2.50 mm of standard header does not.__ [design.md](../docs/design.md) assumes ~14 mm of standoff for exactly this reason, and the kit part does not supply it.

__Solder or clamp them — no loose sockets.__ [design.md](../docs/design.md)'s shock rule.

---

Part numbers, vendors and masses live in [BOM.md](../docs/BOM.md), which is the single source of truth for both. Purchase history is in [shopping-list.md](../docs/shopping-list.md); the reasoning is in [design.md](../docs/design.md).
