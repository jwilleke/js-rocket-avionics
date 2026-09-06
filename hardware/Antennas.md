# Antennas

__Both leave via U.FL on the modules themselves__, so __no RF crosses the carrier at all__. That is what makes the carrier a purely digital and power board, and the layout tractable.

## The two

| | Where | Rule |
|---|---|---|
| __LoRa, `860-930M A-03`__ — a flat flexible-PCB strip ≈40 × 10 mm on an ~82 mm U.FL lead, __not a wire whip__ | U.FL on the Wio-SX1262, run forward __up the ogive__ | Included in the kit |
| __GPS active patch__ | U.FL on the L76K, at the sled's __forward end, facing up__ | Satisfies the "no metal above the patch" rule |

A GPS patch needs a __30–40 mm ground plane__ and a 24 mm board never will be — which is why the patch is off-board rather than on the carrier.

## Photograph — and the LoRa antenna is not a whip

![Both Seeed antennas on the measurement grid](../docs/resources/Wio-SX1262-LoRa-antennas.jpg)

> __The "82 mm whip" is a flat flexible-PCB strip, roughly 40 × 10 mm, on a coaxial lead.__ [BOM.md](../docs/BOM.md) calls it a *"U.FL 82 mm whip"* and this page repeated it; the photograph shows __`seeed studio 860-930M A-03`__ — a printed antenna on a thin flexible substrate, not a wire. __The 82 mm is the U.FL lead, not the radiator.__

That changes how it is fitted rather than whether it works. A wire whip can be stood up the ogive; __a flat strip has to lie against something__, and it wants that surface to be non-conductive and clear of the GPS patch. It is also far less likely to foul the payload bore than a stiff wire — which is a point in its favour, once the routing is drawn rather than assumed.

The other strip, __`seeed studio 2.4G A-02`__ (~37 × 23 mm), is the XIAO's WiFi/BLE antenna and __does not fly__.

## The one hard rule: ≥50 mm apart

__915 MHz TX desenses a 1575 MHz GPS front end by broadband noise, not harmonics__ — 2 × 915 = 1830 MHz, comfortably clear of GPS — so this is not a problem a filter solves. Separation is the mitigation, and [design.md](../docs/design.md) is candid that desense __*"cannot be reasoned away on paper"*__: the bench is the proof.

The separation must survive __routing and placement__, not just the placement stage — it is a constraint on [#14](https://github.com/jwilleke/js-rocket-avionics/issues/14) and [#15](https://github.com/jwilleke/js-rocket-avionics/issues/15) both.

## Does not fly

The kit's __2.4G A-02 antenna__ — the XIAO's WiFi/BLE antenna — is in the box and is not part of the flight build.

## Open

- __Desense never observed__, in either direction — [#6](https://github.com/jwilleke/js-rocket-avionics/issues/6)
- __Whip routing up the ogive is untested__ against a Nosecone that has never been printed at its current revision
- __LoRa range unmeasured.__ The beacon is the recovery system

---

Part numbers, vendors and masses live in [BOM.md](../docs/BOM.md), which is the single source of truth for both. Purchase history is in [shopping-list.md](../docs/shopping-list.md); the reasoning is in [design.md](../docs/design.md).
