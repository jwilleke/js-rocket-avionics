---
title: The charging bench — the charger chip and the lora cut-off switch
description: Step by step, the carrier's charging circuit built on a breadboard with both XIAOs and the battery, before any of it goes into copper.
---

# The charging bench — the charger chip and the lora cut-off switch

__This page proves the carrier's charging circuit on a breadboard before it is drawn in copper__ — [#30](https://github.com/jwilleke/js-rocket-avionics/issues/30), which blocks the carrier order ([#11](https://github.com/jwilleke/js-rocket-avionics/issues/11)). The circuit, its parts and its values are owned by [PCB-carrier.md → Charging](../../hardware/PCB-carrier/PCB-carrier.md#charging); this page is the procedure. The parts bought for it are in [shopping-list.md](../shopping-list.md#the-charging-bench-30--ordered).

## What it must show

| | Pass |
|---|---|
| __No USB__ | both XIAOs run on the battery |
| __USB in XIAO-ESP32S3-cam__ | XIAO-ESP32S3-lora goes dark; XIAO-ESP32S3-cam keeps running, from USB; the charger chip and XIAO-ESP32S3-cam's built-in charger both charge the battery |
| __Charging__ | the charger chip's current as [PCB-carrier.md](../../hardware/PCB-carrier/PCB-carrier.md#charging) gives it for the resistor fitted; __the total into the battery under 500 mA__; the `5V` pin holds up; the time from ~3.7 V to full |
| __USB out again__ | XIAO-ESP32S3-lora boots; XIAO-ESP32S3-cam carries on |

## The circuit

Four points on the breadboard, each a row or a rail. __Every wire below joins two of these, and nothing else joins them.__

```text
                     lora cut-off switch (AO3401A)      to XIAO-ESP32S3-lora's
  battery + ---+---- S          D ----------------------  BAT+ pigtail
   (BATT)      |          G
               |          |
               |   GATE --+-- XIAO-ESP32S3-cam 5V pin --+-- charger pin 4 VDD
               |          |                             |
               |        100k                         4.7 uF
               |          |                             |
               |         GND                           GND
               |
               +---- XIAO-ESP32S3-cam's BAT+ pigtail
               |
               +---- charger pin 3 VBAT   charger chip (MCP73831T-2ACI/OT)
               |                          pin 2 VSS  -- GND
             4.7 uF                       pin 5 PROG -- resistor, see below -- GND
               |                          pin 1 STAT -- not connected
              GND

  GND rail: battery -, both XIAOs' BAT- pigtails, XIAO-ESP32S3-cam's GND pin, charger pin 2, the 100k, the PROG resistor, both 4.7 uF
```

- __The `PROG` resistor sets the charger chip's current__ — the value and why are on [PCB-carrier.md → Charging](../../hardware/PCB-carrier/PCB-carrier.md#charging). __Never fit a single 2.7 kΩ.__ With XIAO-ESP32S3-cam's built-in charger charging alongside, it can put more than 500 mA into the battery. The bench order bought 2.7 kΩ only: __two 2.7 kΩ in series__ (5.4 kΩ, ~185 mA) is safe until the carrier's value is in hand, but it tests the `5V` pin at about half the carrier's current
- __The cut-off switch's source is on the battery__, so its body diode cannot feed XIAO-ESP32S3-lora from the battery. Fit it the other way round and step 2 catches it
- __XIAO-ESP32S3-cam's `GND` pin goes to the GND rail.__ The charger's current returns to USB through it; the thin pigtail is not meant to carry that

## 1 — Build the parts onto adapters

The FET and the charger chip are SOT-23 parts, too small for a breadboard. Each goes onto a SOT-23-to-DIP adapter with header pins, so it plugs in like any other part. __This is also the rehearsal for the carrier__, which is hand-soldered and will carry the same two parts.

- __AO3401A__ — pin 1 `G`, pin 2 `S`, pin 3 `D`. Pins 1 and 2 are on one long side; the dot on the top is by pin 1 (AOS datasheet)
- __MCP73831T-2ACI/OT__ — pin 1 `STAT`, 2 `VSS`, 3 `VBAT`, 4 `VDD`, 5 `PROG`. Pins 1–3 are on one long side, 4 and 5 on the other (Microchip datasheet, table 3-1)
- __After soldering, find which header pin is which with the meter's continuity beep__, part leg to header pin, and write it on the adapter. The adapter's own labels are for its pads, not for this part

## 2 — Look before power

- __Battery unplugged. No USB anywhere.__
- __XIAO-ESP32S3-lora stays off USB for this whole page.__ Its own charger would join in, spoil every current reading, and take the total past 500 mA. And never upload firmware with it on USB — [XIAO-ESP32S3-lora.md](../../hardware/XIAO-ESP32S3-lora/XIAO-ESP32S3-lora.md) says why
- __Every new JST pigtail checked with the meter__, red positive — [the battery's JST and the XIAOs' are wired opposite ways](../../hardware/LiPo-500mAh/LiPo-500mAh.md#on-the-bench--the-join-harness). The join harness is not used on this page; the breadboard replaces it
- __The cut-off switch's source on the battery row.__ Check it against the drawing, by the marks from step 1, then __prove it with the meter's diode setting__, battery and both XIAO pigtails unplugged:

  | Red probe | Black probe | Reads |
  |---|---|---|
  | switch's XIAO-ESP32S3-lora side | battery row | ~0.5–0.7 V — its body diode |
  | battery row | switch's XIAO-ESP32S3-lora side | `OL` |

  Anything else, the FET is in backwards
- __The `PROG` resistor is not a single 2.7 kΩ__ — read it with the meter
- __The USB meter is between USB and XIAO-ESP32S3-cam__ — it is the only current reading this page uses
- __XIAO-ESP32S3-cam runs [`soak-power`](../../firmware/soak-power/)__. It prints its NVS reset history at every boot, so a reset at a USB change that nobody saw still shows, with its reason, the next time it is on USB
- __Stay with it.__ A LiPo is never charged unattended; charge on a hard, non-flammable surface

## 3 — No USB: both run on the battery

1. Plug the battery in
2. __Both boot__ — XIAO-ESP32S3-lora's node appears in the Meshtastic app; XIAO-ESP32S3-cam runs whatever it carries
3. With the meter, __battery + to XIAO-ESP32S3-lora's BAT+ pigtail__: a few tens of millivolts at most. That is the switch's on-resistance. More than ~0.1 V means it is not fully on — stop and check its gate reads 0 V

## 4 — USB in, charger chip disconnected: the cut-off switch alone

Pull the charger chip's `VDD` wire out first, so the only charger in the circuit is XIAO-ESP32S3-cam's own.

1. __USB into XIAO-ESP32S3-cam__
2. __XIAO-ESP32S3-lora goes dark__ — its "last heard" in the Meshtastic app stops advancing, and XIAO-ESP32S3-lora's BAT+ pigtail reads near 0 V. __This is the cut-off switch working__
3. __XIAO-ESP32S3-cam keeps running__, now from USB
4. __Read the USB meter__ — XIAO-ESP32S3-cam's draw plus its built-in charger. Then unplug XIAO-ESP32S3-cam's BAT pigtail and read it again — __XIAO-ESP32S3-cam's own draw__ alone. The difference is the built-in charger's current. Plug the pigtail back in
5. __Unplug USB.__ XIAO-ESP32S3-lora boots again; XIAO-ESP32S3-cam carries on

Write down all three: the two readings from step 4 and the difference.

## 5 — The charger chip

Start with the battery partly run down — __~3.7 V resting__ — so there is a full-current stretch to see. Running both XIAOs on it for half an hour or so does that.

1. Put the charger chip's `VDD` wire back. Plug USB into XIAO-ESP32S3-cam
2. __Total into the battery = USB meter reading − XIAO-ESP32S3-cam's own draw__ from step 4. __It must be under 500 mA__ — if not, unplug USB and stop. __The charger chip alone = USB meter reading − step 4's first reading__, taken straight after step 4 so the battery voltage has barely moved
3. __XIAO-ESP32S3-cam's `5V` pin to `GND`__, with the meter, while it charges. This is the check that the XIAO's internal path from its USB-C to that pin carries the load — Seeed's schematic shows it as bare copper, no fuse or diode, with no rating written. Write the reading down, and the resistor it was taken with
4. __Read the current at 1, 5, 15 and 30 minutes__, and the battery voltage at the breadboard's battery row. __A current that falls while the battery is still well under 4.1 V is the chip protecting itself from heat__ — thermal regulation, not a fault. On a small adapter with little copper it will throttle more than it will on the carrier; write down that it did, and when
5. __Touch-test the chip__ — carefully, with a fingertip on the adapter beside it. Hot to the touch is expected. Too hot to hold means it is throttling, which step 4 will already show
6. __Full is when the USB meter falls back to XIAO-ESP32S3-cam's own draw__ — both chargers stopped. Write down the time
7. __Unplug USB.__ XIAO-ESP32S3-lora boots; XIAO-ESP32S3-cam carries on. Ten minutes later, the battery's resting voltage

## 6 — Power down

Unplug the battery. __A battery left on both XIAOs drains past its safe limit overnight__ — [LiPo-500mAh.md](../../hardware/LiPo-500mAh/LiPo-500mAh.md).

## Record on #30

| | Reading |
|---|---|
| `PROG` resistor fitted | |
| Diode check, two readings (step 2) | |
| Battery to XIAO-ESP32S3-lora's BAT+ pigtail, no USB (step 3) | |
| XIAO-ESP32S3-lora dark with USB in (step 4) | yes / no |
| USB meter, pigtail in and out, and the built-in charger's current (step 4) | |
| Total into the battery, and the charger chip alone (step 5) | |
| `5V` pin while charging (step 5) | |
| Charge current at 1, 5, 15, 30 min, with battery voltage (step 5) | |
| Throttled? When? (step 5) | |
| Start voltage → full, and the time (step 5) | |
| Resting voltage 10 min after (step 5) | |
| XIAO-ESP32S3-cam reset at any USB change? | |
