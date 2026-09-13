---
title: The charging bench — Q1, Q2 and the charger chip
description: Step by step, the carrier's charging circuit built on a breadboard with both XIAOs and the battery, before any of it goes into copper.
---

# The charging bench — Q1, Q2 and the charger chip

__This page proves the carrier's charging circuit on a breadboard before it is drawn in copper__ — [#30](https://github.com/jwilleke/js-rocket-avionics/issues/30), which blocks the carrier order ([#11](https://github.com/jwilleke/js-rocket-avionics/issues/11)). Why the circuit exists and what each part is, is owned by [PCB-carrier-design.md](../../hardware/PCB-carrier/PCB-carrier-design.md#charging-on-the-carrier--q1-the-charge-isolation-fet-and-a-charger-chip--decided-not-yet-in-the-generator); this page is the procedure. The parts to buy are in [shopping-list.md](../shopping-list.md#the-charging-bench-30--ordered).

## What it must show

| | Pass |
|---|---|
| __No USB__ | both XIAOs run on the battery, as today |
| __USB in XIAO-ESP32S3-cam__ | XIAO-ESP32S3-lora goes dark; XIAO-ESP32S3-cam keeps running, from USB; __only the charger chip__ charges the battery |
| __Charging__ | ~333–407 mA into the battery, from XIAO-ESP32S3-cam's `5V` pin; the `5V` pin holds up; the time from ~3.7 V to full |
| __USB out again__ | XIAO-ESP32S3-lora boots; XIAO-ESP32S3-cam never resets |

## The circuit

Four points on the breadboard, each a row or a rail. __Every wire below joins two of these, and nothing else joins them.__

```text
                     Q1 (AO3401A)                       to XIAO-ESP32S3-lora's
  battery + ---+---- S          D ----------------------  BAT+ pigtail
   (BATT)      |          G
               |          |
               +---- D          S ----------------------  to XIAO-ESP32S3-cam's
               |     Q2 (AO3401A)                         BAT+ pigtail
               |          G
               |          |
               |   GATE --+-- XIAO-ESP32S3-cam 5V pin --+-- U1 pin 4 VDD
               |          |                             |
               |        100k                         4.7 uF
               |          |                             |
               |         GND                           GND
               |
               +---- U1 pin 3 VBAT        U1 (MCP73831T-2ACI/OT)
               |                          pin 2 VSS  -- GND
             4.7 uF                       pin 5 PROG -- 2.7k -- GND
               |                          pin 1 STAT -- not connected
              GND

  GND rail: battery -, both XIAOs' BAT- pigtails, XIAO-ESP32S3-cam's GND pin, U1 pin 2, the 100k, the 2.7k, both 4.7 uF
```

- __Q2 is recommended, not yet decided__ ([#30](https://github.com/jwilleke/js-rocket-avionics/issues/30)). The bench builds it in. Do not run U1 without it at 2.7 kΩ: two chargers together can pass the battery's 500 mA
- __Q1 and Q2 face opposite ways, and that is the point.__ Q1's source is on the battery, so its body diode cannot feed XIAO-ESP32S3-lora. Q2's __drain__ is on the battery, so its body diode cannot let XIAO-ESP32S3-cam's own charger into the battery — the reason Q2 exists. Swap either one and the test below catches it
- __XIAO-ESP32S3-cam's `GND` pin goes to the GND rail.__ The charger's current returns to USB through it; the thin pigtail is not meant to carry that
- __The 2.7 kΩ sets the charge current__: 1000 V ÷ 2.7 kΩ = 370 mA, and the datasheet's ±10% makes it 333–407 mA — under the battery's 500 mA limit even at the top

## 1 — Build the parts onto adapters

The FETs and the charger are SOT-23 parts, too small for a breadboard. Each goes onto a SOT-23-to-DIP adapter with header pins, so it plugs in like any other part. __This is also the rehearsal for the carrier__, which is hand-soldered and will carry the same three parts.

- __AO3401A__ — pin 1 `G`, pin 2 `S`, pin 3 `D`. Pins 1 and 2 are on one long side; the dot on the top is by pin 1 (AOS datasheet)
- __MCP73831T-2ACI/OT__ — pin 1 `STAT`, 2 `VSS`, 3 `VBAT`, 4 `VDD`, 5 `PROG`. Pins 1–3 are on one long side, 4 and 5 on the other (Microchip datasheet, table 3-1)
- __After soldering, find which header pin is which with the meter's continuity beep__, part leg to header pin, and write it on the adapter. The adapter's own labels are for its pads, not for this part
- __Mark Q1 and Q2 on their adapters.__ They are the same part in opposite directions; unmarked, they get swapped

## 2 — Look before power

- __Battery unplugged. No USB anywhere.__
- __XIAO-ESP32S3-lora stays off USB for this whole page.__ Its own charger would join in and spoil every current reading. And never upload firmware with it on USB — [XIAO-ESP32S3-lora.md](../../hardware/XIAO-ESP32S3-lora/XIAO-ESP32S3-lora.md) says why
- __Every new JST pigtail checked with the meter__, red positive — [the battery's JST and the XIAOs' are wired opposite ways](../../hardware/LiPo-500mAh/LiPo-500mAh.md#on-the-bench--the-join-harness). The join harness is not used on this page; the breadboard replaces it
- __Q1's source and Q2's drain both on the battery row.__ Check it against the drawing, by the marks from step 1, then __prove it with the meter's diode setting__, battery and both XIAO pigtails unplugged:

  | Red probe | Black probe | Reads |
  |---|---|---|
  | Q1's XIAO-ESP32S3-lora side | battery row | ~0.5–0.7 V — Q1's body diode |
  | battery row | Q1's XIAO-ESP32S3-lora side | `OL` |
  | battery row | Q2's XIAO-ESP32S3-cam side | ~0.5–0.7 V — Q2's body diode |
  | Q2's XIAO-ESP32S3-cam side | battery row | `OL` |

  Anything else, a FET is in backwards. __This is the only step that catches a backwards Q2__ — powered, it shows only when the battery is nearly flat
- __The USB meter is between USB and XIAO-ESP32S3-cam__ — it is the only current reading this page uses
- __XIAO-ESP32S3-cam runs [`soak-power`](../../firmware/soak-power/)__. It prints its NVS reset history at every boot, so a reset at a USB change that nobody saw still shows, with its reason, the next time it is on USB. __Unplugging USB is the moment a reset is most likely__ — [PCB-carrier-design.md](../../hardware/PCB-carrier/PCB-carrier-design.md#q2--xiao-esp32s3-cams-charger-off-the-battery--recommended-needs-the-operators-ok) says why
- __Stay with it.__ A LiPo is never charged unattended; charge on a hard, non-flammable surface

## 3 — No USB: both run on the battery

1. Plug the battery in
2. __Both boot__ — XIAO-ESP32S3-lora's node appears in the Meshtastic app; XIAO-ESP32S3-cam runs whatever it carries
3. With the meter, __battery + to each XIAO's BAT+ pigtail__: a few tens of millivolts at most. That is each FET's on-resistance. More than ~0.1 V means a FET is not fully on — stop and check its gate reads 0 V

## 4 — USB in, charger disconnected: Q1 and Q2 alone

Pull U1's `VDD` wire out first, so the only charger in the circuit is XIAO-ESP32S3-cam's own.

1. __USB into XIAO-ESP32S3-cam__
2. __XIAO-ESP32S3-lora goes dark__ — its "last heard" in the Meshtastic app stops advancing, and XIAO-ESP32S3-lora's BAT+ pigtail reads near 0 V. __This is Q1 working__
3. __XIAO-ESP32S3-cam keeps running__, now from USB
4. __Read the USB meter.__ Then unplug XIAO-ESP32S3-cam's BAT pigtail and read it again. __The two should be the same__ — with Q2 off, XIAO-ESP32S3-cam's own charger has nowhere to go. Plug the pigtail back in
5. __Unplug USB.__ XIAO-ESP32S3-lora boots again; XIAO-ESP32S3-cam does not reset

Write down the USB meter reading from step 4 — it is __XIAO-ESP32S3-cam's own draw__, which step 5 subtracts.

## 5 — The charger chip

Start with the battery partly run down — __~3.7 V resting__ — so there is a full-current stretch to see. Running both XIAOs on it for half an hour or so does that.

1. Put U1's `VDD` wire back. Plug USB into XIAO-ESP32S3-cam
2. __Charge current = USB meter reading − XIAO-ESP32S3-cam's own draw__ from step 4. Expect __333–407 mA__
3. __XIAO-ESP32S3-cam's `5V` pin to `GND`__, with the meter, while it charges. This is the check that the XIAO's internal path from its USB-C to that pin carries the load — Seeed's schematic shows it as bare copper, no fuse or diode, with no rating written. Write the reading down
4. __Read the current at 1, 5, 15 and 30 minutes__, and the battery voltage at the breadboard's battery row. __A current that falls while the battery is still well under 4.1 V is the chip protecting itself from heat__ — thermal regulation, not a fault. On a small adapter with little copper it will throttle more than it will on the carrier; write down that it did, and when
5. __Touch-test the chip__ — carefully, with a fingertip on the adapter beside it. Hot to the touch is expected. Too hot to hold means it is throttling, which step 4 will already show
6. __Full is when the USB meter falls back to XIAO-ESP32S3-cam's own draw__ — the chip stops at 7.5% of its set current, ~28 mA. Write down the time
7. __Unplug USB.__ XIAO-ESP32S3-lora boots; XIAO-ESP32S3-cam carries on. Ten minutes later, the battery's resting voltage

## 6 — Power down

Unplug the battery. __A battery left on both XIAOs drains past its safe limit overnight__ — [LiPo-500mAh.md](../../hardware/LiPo-500mAh/LiPo-500mAh.md).

## Record on #30

| | Reading |
|---|---|
| Diode check, four readings (step 2) | |
| Battery to each BAT+ pigtail, no USB (step 3) | |
| XIAO-ESP32S3-lora dark with USB in (step 4) | yes / no |
| USB meter, pigtail in and out (step 4) — the same? | |
| XIAO-ESP32S3-cam's own draw (step 4) | |
| Charge current at 1, 5, 15, 30 min, with battery voltage (step 5) | |
| `5V` pin while charging (step 5) | |
| Throttled? When? (step 5) | |
| Start voltage → full, and the time (step 5) | |
| Resting voltage 10 min after (step 5) | |
| XIAO-ESP32S3-cam reset at any USB change? | |
