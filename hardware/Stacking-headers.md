# 2×7 stacking headers

__The part everything else assumes and nobody has confirmed.__

## What they do

Each XIAO mounts on a pair of __2×7 headers with ~14 mm standoff__, the expansion board — Sense or Wio-SX1262 — __hanging in the gap__ beneath it. Total stack is ~__15 mm__ above the carrier.

That standoff is not a convenience. It is the reason the carrier is a single centre-plane card at all:

```text
at the XIAO's edge (x = ±8.75 from centre):
  available depth = sqrt(19.7² − 8.75²) = 17.6 mm each side

two stacks + carrier = 15 + 1.0 + 15 = 31.0 mm
available            = 2 × 17.6       = 35.2 mm     fits, ~2 mm margin
```

__Two millimetres of margin__ is the whole budget, and it is the same margin the L76K's stack collision eats into.

## They are not a generic part

[BOM.md](../docs/BOM.md) flags this explicitly: __stock 2×7 headers are far shorter__ than the ~14 mm needed. A drawer full of ordinary 2×7 strip does not satisfy this.

[BOM.md](../docs/BOM.md) carries the row as __`unverified`__.

__The mated height sets two things:__ whether the stack fits the bore at all, against the ~2 mm margin above, and where the camera lens ends up.

__Solder or clamp them — no loose sockets.__ [design.md](../docs/design.md)'s shock rule.

---

Part numbers, vendors and masses live in [BOM.md](../docs/BOM.md), which is the single source of truth for both. Purchase history is in [shopping-list.md](../docs/shopping-list.md); the reasoning is in [design.md](../docs/design.md).
