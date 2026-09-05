# Arming switch

__In the battery line, not on a GPIO.__ The one part in the flight build that is still neither chosen nor bought.

## The problem it solves is access, not convenience

Once the nose is assembled __there is no way in__: USB is unreachable, Wi-Fi is off, and the status LED is sealed inside. A slide switch would need another hand-drilled hole in a part with no generator.

Whatever the mechanism, the architecture is settled and worth restating because it is the part that survives every revision below: __the switch sits in series in the battery line, between the cell and the carrier's JST.__ That means it __physically cuts power__ rather than setting a firmware state a boot-loop could defeat, it costs __zero GPIO__, and it __cuts both boards at once__ — arming is all-or-nothing, __including the beacon__.

## It is no longer a reed switch

[design.md](../docs/design.md)'s locked-decisions table still says *"reed switch in the battery line"* and __that row is stale__. [BOM.md](../docs/BOM.md) and [shopping-list.md](../docs/shopping-list.md) record it as __superseded on 2026-08-15 by a pull-pin plus a subminiature microswitch__ — smallest hole, snap action, no printed mechanism. See the [arming brainstorm](../docs/resources/2026-08-15-arming-and-access-brainstorm.md).

__Nothing has been bought and no part has been chosen.__ The mass in [BOM.md](../docs/BOM.md) is inherited from the reed-switch design.

## What the reed switch taught, and what still applies

The reed design left two open questions. The pull-pin answers the first outright and __the second survives the change of part__:

- __Polarity — does the magnet arm or safe?__ Dead with the reed switch. A pull-pin is unambiguous: the pin is in, the rocket is safe, and the pin doubles as a visible remove-before-flight tag
- __Contact rating against camera inrush — still live.__ Steady draw is ~300 mA, which is comfortable, but __the OV2640 powering up is the question__: small contacts can weld under inrush, and __a welded switch is an armed rocket that cannot be safed__ — the failure mode that matters, because it happens on the pad with people nearby

__The fix is standard and cheap: let the switch drive a MOSFET rather than the load.__ The switch carries milliamps into the gate; the FET carries the current. One extra part, and the concern disappears — __but it adds a footprint, so it must be decided before the carrier is routed.__

## Where the pin enters — no longer open

[shopping-list.md](../docs/shopping-list.md) blocks the purchase partly on *"the sled can rotate, so where the pin enters is unresolved."*

__That is being fixed on the rocket side.__ [js-rocket#89](https://github.com/jwilleke/js-rocket/issues/89) adds a clocking notch keyed to the M3 × 55 joint pin, fixing the sled's azimuth. The entry point becomes a known location rather than an open question.

## Open

- __Choose the part and the switching topology__ — direct or MOSFET-gated — [#2](https://github.com/jwilleke/js-rocket-avionics/issues/2)
- __Correct [design.md](../docs/design.md)'s locked table__, which still names the reed switch
- __Route it__, once the topology is settled — [#14](https://github.com/jwilleke/js-rocket-avionics/issues/14)
- Not needed for bench bring-up; the bench runs without it

---

Part numbers, vendors and masses live in [BOM.md](../docs/BOM.md), which is the single source of truth for both. Purchase history is in [shopping-list.md](../docs/shopping-list.md); the reasoning is in [design.md](../docs/design.md).
