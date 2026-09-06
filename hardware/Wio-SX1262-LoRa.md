# Wio-SX1262 — LoRa radio

__The link that gets the rocket found.__ Sits beneath the plain XIAO on board A's stack and carries its own U.FL connector.

## What it is for

GPS position out over LoRa, on stock Meshtastic. No firmware is written for it, and that is deliberate — see [XIAO-ESP32S3.md](XIAO-ESP32S3.md).

## Buy it as the kit, never as two boards

[BOM.md](../docs/BOM.md) is emphatic: __must be the matched B2B kit variant__ — buy the kit SKU, __never the two boards separately__. The kit is a supported Meshtastic device and __arrives pre-flashed__, which is the entire premise of board A. Bought separately, the radio ends up on non-standard pins and stock Meshtastic can no longer be flashed as a rescue.

## Photograph

![Wio-SX1262 on the measurement grid](../docs/resources/Wio-SX1262-LoRa.jpg)

Silkscreen confirms the genuine Seeed part — __`Wio-SX1262`, `FCC ID: Z4T-WIO-SX1262`__, CE and MIC marks — which is the check that matters here, because [BOM.md](../docs/BOM.md) requires the __matched kit__ and a separately-bought radio defeats board A's whole premise. The __U.FL connector is on the module__, as the design assumes, and the outline is the XIAO's ~17.5 × 21 mm with 14 castellated pads, 7 a side.

> __A 2×5 header is fitted to it, standing off one edge.__ That is not the __2×7, ~14 mm standoff__ stack the carrier is designed around ([Stacking-headers.md](Stacking-headers.md)), so it is presumably bench kit rather than the flight fit. Worth confirming before [#10](https://github.com/jwilleke/js-rocket-avionics/issues/10) concludes what is held.

## Interfaces

| | |
|---|---|
| Connection | __B2B__ beneath the XIAO ESP32S3 (plain), in the same stack as the L76K |
| Antenna | __U.FL on the module itself__ — 82 mm whip, up the ogive |
| Carrier | __Nothing.__ No footprint, no RF across the board |

__No RF crosses the carrier at all.__ Both antennas leave via U.FL on their own modules, which is what makes the carrier a purely digital and power board and the layout tractable.

## Things that will catch you

__Antenna separation is a design rule, not a preference: ≥50 mm__ between the LoRa whip and the GPS patch. 915 MHz TX desenses a 1575 MHz front end __by broadband noise, not harmonics__ — 2 × 915 = 1830 MHz, clear of GPS — so the mechanism is not one a filter fixes. [design.md](../docs/design.md) calls desense something that *"cannot be reasoned away on paper."*

## Open

- __The stack has never been assembled.__ Whether the L76K and this module coexist on the B2B is open, against ~2 mm of bore margin — [#6](https://github.com/jwilleke/js-rocket-avionics/issues/6)
- __Link range untested__ — [#6](https://github.com/jwilleke/js-rocket-avionics/issues/6). The beacon is the recovery system; an untested link is an untested recovery
- __Only the sustainer carries it.__ The booster has no beacon — [#12](https://github.com/jwilleke/js-rocket-avionics/issues/12)

---

Part numbers, vendors and masses live in [BOM.md](../docs/BOM.md), which is the single source of truth for both. Purchase history is in [shopping-list.md](../docs/shopping-list.md); the reasoning is in [design.md](../docs/design.md).
