# Wio-SX1262 — LoRa radio

__The link that gets the rocket found.__ Sits beneath the plain XIAO on XIAO-ESP32S3-lora's stack and carries its own U.FL connector.

## What it is for

GPS position out over LoRa, on stock Meshtastic. No firmware is written for it, and that is deliberate — see [XIAO-ESP32S3-lora.md](../XIAO-ESP32S3-lora/XIAO-ESP32S3-lora.md).

## Buy it as the kit, never as two boards

[BOM.md](../../docs/BOM.md) is emphatic: __must be the matched B2B kit variant__ — buy the kit SKU, __never the two boards separately__. The kit is a supported Meshtastic device and __arrives pre-flashed__, which is the entire premise of XIAO-ESP32S3-lora. Bought separately, the radio ends up on non-standard pins and stock Meshtastic can no longer be flashed as a rescue.

## Photograph

![Wio-SX1262 on the measurement grid](Wio-SX1262-LoRa.jpg)

Silkscreen: __`Wio-SX1262`, `FCC ID: Z4T-WIO-SX1262`__, CE and MIC marks. Outline is the XIAO's ~__17.5 × 21 mm__ with 14 castellated pads, 7 a side, and the __U.FL connector is on the module__.

> __A 2×5 header is currently fitted, standing off one edge.__ That is bench kit, not the flight fit: the flight connection is __two 1×7 strips, one down each long edge__ — see [Stacking-headers.md](../Stacking-headers/Stacking-headers.md), which owns the part and the standoff.
>
> __This line previously called for a "2×7, ~14 mm standoff" stack and both halves were wrong.__ There is no 2×7 part — the XIAO's rows are 17.0 mm apart, not 2.54, so a dual-row header never fits. And the ~14 mm standoff came from a retracted revision of [design.md](../../docs/design.md) that had the expansion board hanging *below* the XIAO; the kit's standard ~2.50 mm headers are the flight part and no tall stacking headers are needed.

## Interfaces

| | |
|---|---|
| Connection | __B2B__ beneath the XIAO ESP32S3 (plain), in the same stack as the L76K |
| Antenna | __U.FL on the module itself__ — 82 mm whip, up the ogive |
| Carrier | __Nothing.__ No footprint, no RF across the board |
| Height added to a XIAO | __4.79 mm__ — 9.32 mm for the pair against 4.53 bare |

__No RF crosses the carrier at all.__ Both antennas leave via U.FL on their own modules, which is what makes the carrier a purely digital and power board and the layout tractable.

## Things that will catch you

__Antenna separation is a design rule, not a preference: ≥50 mm__ between the LoRa whip and the GPS patch. 915 MHz TX desenses a 1575 MHz front end __by broadband noise, not harmonics__ — 2 × 915 = 1830 MHz, clear of GPS — so the mechanism is not one a filter fixes. [design.md](../../docs/design.md) calls desense something that *"cannot be reasoned away on paper."*

---

Part numbers, vendors and masses live in [BOM.md](../../docs/BOM.md), which is the single source of truth for both. Purchase history is in [shopping-list.md](../../docs/shopping-list.md); the reasoning is in [design.md](../../docs/design.md).
