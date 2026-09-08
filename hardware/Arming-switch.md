# Arming switch

__Flight 3 flies without one__ (operator, 2026-09-08). In the battery line, not on a GPIO, whenever a flight does carry one. Nothing was chosen, nothing was bought, and nothing was waiting on it.

> __So flight 3 has no arming device at all__ — the part named by this page is the arming device, and it is deferred rather than replaced. __Nothing else is promoted into the role.__ Power is made and broken by plugging and unplugging the [battery](LiPo-500mAh.md)'s JST, which is a __connector__ and stays one; giving it a second name would put a safety role on a part that was never designed to carry it, and this project keeps one name per part.
>
> __What that costs is turnaround, not safety.__ This payload has no pyro, so an "armed" rocket here is one that is recording video. The switch only ever bought a faster way to reach the disconnect; the argument below is unchanged and kept for whenever a flight wants it.
>
> __What it buys back, today:__ the 80 mm battery lead no longer has to carry an inline switch, so __the JST's position is decided on its own__ rather than jointly — see [LiPo-500mAh.md](LiPo-500mAh.md). One less coupling in [#14](https://github.com/jwilleke/js-rocket-avionics/issues/14) stage 2c.
>
> __The pad procedure this forces:__ runtime is ~100 minutes from the moment the battery is connected and it cannot be managed in firmware, so __the JST goes on last__, on the pad, and the clock starts there.
>
> __What would overrule it__ is unchanged and still unchecked: a club or field rule requiring a visible external arming switch for any powered electronics. A rule beats an argument.

## It is not a safety device on this rocket, and calling it one drove requirements it does not need

__An arming switch exists to stop a flight computer firing an ejection charge on the ground.__ That is why NAR and Tripoli require them and why they are normally non-negotiable.

__This payload has no pyro.__ [design.md](../docs/design.md) is explicit: *"No pyro channels; ejection is the motor delay. Apogee is data, not deployment."* The avionics __cannot actuate anything__. An "armed" rocket here is a rocket that is recording video.

So the sentence this page used to carry — *a welded switch is an armed rocket that cannot be safed, the failure mode that matters because it happens on the pad with people nearby* — __described a hazard this design does not have__. It was inherited from rocketry convention rather than derived from this rocket, and it is what produced the MOSFET, the welding analysis and the demand for a hole in the Nosecone collar.

__What is real is runtime.__ 500 mAh against ~300 mA is roughly __100 minutes__ from the moment the battery is connected, and it cannot be managed in firmware: [XIAO-ESP32S3-lora](XIAO-ESP32S3-lora.md) runs __stock Meshtastic with no code written__, which was a deliberate choice and means it cannot sleep. It draws from the instant it has power.

__So a disconnect is needed. A switch in the nose wall is not.__ The JST already is one; the only question is when it can be reached:

| | Cost of a launch delay past ~100 minutes |
|---|---|
| No switch — connect the JST last | Pull the M3 × 55 and extract the sled. That pin also anchors the recovery cord, so it is a nose teardown plus a re-rig |
| Switch in the nose wall | Flip it |

__That difference is the whole value of the switch: turnaround, not safety.__ It is worth having against the *"rapidly reusable rocket flown by a 14-year-old"* objective, and it is not worth blocking an airframe part for.

__What would overrule this:__ a club or field rule requiring a visible external arming switch for any powered electronics, regardless of deployment. A rule beats an argument. Not checked.

## The old framing, kept for what it got right

Once the nose is assembled __there is no way in__: USB is unreachable, Wi-Fi is off, and the status LED is sealed inside. A slide switch would need another hand-drilled hole in a part with no generator.

Whatever the mechanism, the architecture is settled and worth restating because it is the part that survives every revision below: __the switch sits in series in the battery line, between the battery and the carrier's JST.__ That means it __physically cuts power__ rather than setting a firmware state a boot-loop could defeat, it costs __zero GPIO__, and it __cuts both XIAOs at once__ — arming is all-or-nothing, __including the radio__.

## A pull-pin and a subminiature microswitch

__Smallest hole, snap action, no printed mechanism.__ Reasoning in the [arming brainstorm](../docs/resources/2026-08-15-arming-and-access-brainstorm.md).

> __An earlier note here said [design.md](../docs/design.md)'s locked-decisions table still named a reed switch.__ It does not, and had already stopped by the time this was read again — that row names the architecture and points here for the mechanism, which is the right division. Checked 2026-09-08.

__Nothing has been bought and no part has been chosen.__ The mass in [BOM.md](../docs/BOM.md) is inherited from the reed-switch design.

## The live constraint: contact rating against camera inrush

__Polarity is not a question with a pull-pin__ — the pin is in, the rocket is safe, and the pin doubles as a visible remove-before-flight tag. What does apply to any switch chosen:

- __Contact rating against camera inrush.__ Steady draw is ~300 mA, which is comfortable, but __the camera powering up is the question__: small contacts can weld under inrush, and __a welded switch is an armed rocket that cannot be safed__ — the failure mode that matters, because it happens on the pad with people nearby

> __The MOSFET is dropped__ (2026-09-08). It existed to stop a welded contact leaving the rocket armed. Without pyro, a welded contact means *the camera will not turn off*, which is a bench problem. __[#14](https://github.com/jwilleke/js-rocket-avionics/issues/14) no longer waits on this__, and no footprint is needed.
>
> The brainstorm had already reached the same place by a different route: many subminiature microswitches are rated __3–5 A__ against a ~300 mA draw, so the switch could carry the load directly anyway.

## Where the pin enters

__If one is ever cut, it should share [#1](https://github.com/jwilleke/js-rocket-avionics/issues/1)'s opening rather than buy a second hole.__ That issue already wants a USB-C aperture for charging, data and status, and the measurements are done — ~9 × 3.2 mm fits the exposed band of the PayloadAdapter. One hole, three jobs, plus this one.

__An earlier note here said the entry point was "set by the sled's clocking, [js-rocket#90](https://github.com/jwilleke/js-rocket/issues/90)" and could not be chosen until the sled's azimuth was fixed. That overstated what #90 delivered.__ The loop stops the sled turning freely, but a __180° flip still threads the same pin__ — a featureless rod on a diameter is symmetric — so the switch could still face either side. The `PORT` engraving is a label, not a key.

---

Part numbers, vendors and masses live in [BOM.md](../docs/BOM.md), which is the single source of truth for both. Purchase history is in [shopping-list.md](../docs/shopping-list.md); the reasoning is in [design.md](../docs/design.md).
