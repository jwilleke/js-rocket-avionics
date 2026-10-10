# LiPo charger

__The battery is charged at its own plug, below the sled, with the sled left in the nose.__ Unplug the [LiPo-500mAh](../LiPo-500mAh/LiPo-500mAh.md) from the XIAOs' harness, plug it into this charger, and plug the charger into USB. Nothing on the carrier charges the battery, and nothing else draws from it while it charges (operator, 2026-10-10; [#30](https://github.com/jwilleke/js-rocket-avionics/issues/30)).

Part number and vendor are in [BOM.md](../../docs/BOM.md).

## What it is

| | |
|---|---|
| Form | A USB lead ending in a __JST-PH 2.0__ socket, with a light in the lead. Two in the pack: one for the bench, one for the field box |
| Output | __4.2 V, 0.5 A__ by the listing — the battery's maker's limit is "500mA or less" (Adafruit 1578) |
| Input | 5 V from any USB port, phone charger or power bank |
| Light | __red while charging, off when full__ |

## Where the battery is unplugged

__The battery's plug is reached through the nosecone adapter, slightly below the sled.__ On the rocket as built, the battery's lead goes to a Y-connector, and each branch goes to a JST soldered to one XIAO's underside BAT pads. The battery comes off the Y there. __The sled is not pulled to charge.__

## Check the polarity before the first charge

__JST-PH 2.0 plugs are wired both ways, and a reversed LiPo can be damaged or catch fire.__ The listing gives the check:

1. Hold the charger's socket __groove side up__: its __left__ pin is negative, its __right__ pin positive
2. Hold the battery's plug facing it, __convex side up__
3. The __black__ wire must be on the __left__ and the __red__ on the __right__

__If they do not match, do not plug it in.__ Once a charger has passed, mark its `+` side so the check is not repeated.

## Charging

1. Unplug the battery from the harness, below the sled. Pull the plug housing, never the wires
2. Plug the battery into the charger, then the charger into USB. The light goes red
3. __Light off: full.__ Unplug the charger from USB, then the battery from the charger
4. Read the resting voltage against the table in [LiPo-500mAh.md](../LiPo-500mAh/LiPo-500mAh.md), and plug the battery back into the harness only when the rocket should be on — plugging it in is "on"

__Do not leave it charging unattended__, and do not charge a battery that is puffed or damaged.

__USB into a XIAO is not a way to charge.__ With the battery on the harness, XIAO-ESP32S3-cam's built-in charger does run — it cannot be turned off — but at ~115 mA it loses to XIAO-ESP32S3-lora's draw, and the battery goes down, not up ([Two chargers on one battery](../LiPo-500mAh/LiPo-500mAh.md#two-chargers-on-one-battery)). That is harmless, and it is not charging.
