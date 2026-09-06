# Arming switch

__In the battery line, not on a GPIO.__ The one part in the flight build that is still neither chosen nor bought.

## The problem it solves is access, not convenience

Once the nose is assembled __there is no way in__: USB is unreachable, Wi-Fi is off, and the status LED is sealed inside. A slide switch would need another hand-drilled hole in a part with no generator.

Whatever the mechanism, the architecture is settled and worth restating because it is the part that survives every revision below: __the switch sits in series in the battery line, between the cell and the carrier's JST.__ That means it __physically cuts power__ rather than setting a firmware state a boot-loop could defeat, it costs __zero GPIO__, and it __cuts both XIAOs at once__ — arming is all-or-nothing, __including the radio__.

## A pull-pin and a subminiature microswitch

__Smallest hole, snap action, no printed mechanism.__ Reasoning in the [arming brainstorm](../docs/resources/2026-08-15-arming-and-access-brainstorm.md).

> [design.md](../docs/design.md)'s locked-decisions table still names a reed switch. __That row is wrong__ and is tracked for correction.

__Nothing has been bought and no part has been chosen.__ The mass in [BOM.md](../docs/BOM.md) is inherited from the reed-switch design.

## The live constraint: contact rating against camera inrush

__Polarity is not a question with a pull-pin__ — the pin is in, the rocket is safe, and the pin doubles as a visible remove-before-flight tag. What does apply to any switch chosen:

- __Contact rating against camera inrush.__ Steady draw is ~300 mA, which is comfortable, but __the camera powering up is the question__: small contacts can weld under inrush, and __a welded switch is an armed rocket that cannot be safed__ — the failure mode that matters, because it happens on the pad with people nearby

__The fix is standard and cheap: let the switch drive a MOSFET rather than the load.__ The switch carries milliamps into the gate; the FET carries the current. One extra part, and the concern disappears — __but it adds a footprint, so it must be decided before the carrier is routed.__

## Where the pin enters

__Set by the sled's clocking__, [js-rocket#90](https://github.com/jwilleke/js-rocket/issues/90). Until the sled's azimuth is fixed the entry point cannot be, because the sled can rotate in a round bore.

---

Part numbers, vendors and masses live in [BOM.md](../docs/BOM.md), which is the single source of truth for both. Purchase history is in [shopping-list.md](../docs/shopping-list.md); the reasoning is in [design.md](../docs/design.md).
