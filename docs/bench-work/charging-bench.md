---
title: The charging bench — the charger chip on its adapter
description: Step by step, the carrier's charging circuit built on a breadboard with both XIAOs and the battery, before any of it goes into copper.
---

# The charging bench — the charger chip on its adapter

__This page proves the carrier's charging circuit on a breadboard before it is drawn in copper__ — [#30](https://github.com/jwilleke/js-rocket-avionics/issues/30), which blocks the carrier order ([#11](https://github.com/jwilleke/js-rocket-avionics/issues/11)). The circuit, its parts and its values are owned by [charge-circuit.md](../../hardware/charge-circuit/charge-circuit.md); this page is the procedure. The parts bought for it are in [shopping-list.md](../shopping-list.md#the-charging-bench-30--ordered).

__The adapter built here is the one that flies.__ The chip is soldered to it once, proven on the breadboard, and moved to the carrier.

## What it must show

| | Pass |
|---|---|
| __No USB__ | both XIAOs run on the battery |
| __USB in XIAO-ESP32S3-cam__ | both XIAOs keep running — XIAO-ESP32S3-lora's node stays heard in the Meshtastic app; the charger chip and XIAO-ESP32S3-cam's built-in charger both charge |
| __Charging__ | __current into the battery well positive__ with XIAO-ESP32S3-lora running; __the two chargers together under 500 mA__; the `5V` pin holds up; the time from ~3.7 V to full |
| __USB out again__ | both XIAOs carry on, no reset |

## The circuit

Four points on the breadboard, each a row or a rail. __Every wire below joins two of these, and nothing else joins them.__

```text
                        (meter A, in series, only when step 4 or 5 says so)
  battery + ---[ A ]---+---- XIAO-ESP32S3-cam's BAT+ pigtail
   (BATT row)          |
                       +---[ B ]---- XIAO-ESP32S3-lora's BAT+ pigtail
                       |    (meter B, in series, only when step 4 says so)
                       |
                       +---- adapter: charger VBAT (pin 3)
                       |
                     4.7 uF          adapter: charger VDD (pin 4) --+-- XIAO-ESP32S3-cam 5V pin
                       |                                            |
                      GND                                        4.7 uF
                                                                    |
                                     adapter: charger PROG (pin 5) -- resistor, see below -- GND
                                     adapter: charger VSS (pin 2)  -- GND
                                     adapter: charger STAT (pin 1) -- not connected

  GND rail: battery -, both XIAOs' BAT- pigtails, XIAO-ESP32S3-cam's GND pin, charger VSS, the PROG resistor, both 4.7 uF
```

- __The `PROG` resistor sets the charger chip's current__ — the value and why are on [charge-circuit.md](../../hardware/charge-circuit/charge-circuit.md). __Never fit a single 2.7 kΩ.__ With XIAO-ESP32S3-cam's built-in charger alongside, it can put more than 500 mA into the battery. The bench order bought 2.7 kΩ only: __two 2.7 kΩ in series__ (5.4 kΩ, ~185 mA) is safe until the carrier's value is in hand, but it tests the `5V` pin and the net charge at about half the carrier's current
- __Where a meter is not in series, a plain wire joins those two points.__ The meter is only ever in one place at a time
- __XIAO-ESP32S3-cam's `GND` pin goes to the GND rail.__ The charger's current returns to USB through it; the thin pigtail is not meant to carry that

## 1 — Build the chip onto its adapter, and measure the adapter

The charger chip is SOT-23-5, too small for a breadboard. It goes onto the __6-pad SOT-23-to-DIP adapter__ with straight header pins, so it plugs in like any other part.

- __MCP73831T-2ACI/OT__ — pin 1 `STAT`, 2 `VSS`, 3 `VBAT`, 4 `VDD`, 5 `PROG`. Pins 1–3 are on one long side, 4 and 5 on the other (Microchip datasheet, table 3-1). One adapter pad stays empty
- __After soldering, find which header pin is which with the meter's continuity beep__, chip leg to header pin, and write it on the adapter. The adapter's own labels are for its pads, not for this chip
- __Measure the adapter before it goes on the breadboard__: the spacing between its two pin rows, centre to centre, and its outline. __Record both on #30__ — the carrier's six holes are drawn from them

## 2 — Look before power

- __Battery unplugged. No USB anywhere.__
- __XIAO-ESP32S3-lora stays off USB for this whole page.__ Its own charger would join in, spoil every reading, and take the total past 500 mA. And never upload firmware with it on USB — [XIAO-ESP32S3-lora.md](../../hardware/XIAO-ESP32S3-lora/XIAO-ESP32S3-lora.md) says why
- __Every new JST pigtail checked with the meter__, red positive — [the battery's JST and the XIAOs' are wired opposite ways](../../hardware/LiPo-500mAh/LiPo-500mAh.md#on-the-bench--the-join-harness). The join harness is not used on this page; the breadboard replaces it
- __The `PROG` resistor is not a single 2.7 kΩ__ — read it with the meter
- __The adapter's `VBAT` and `VDD` pins, by the marks from step 1__ — a swap puts USB's 5 V onto the battery row
- __The USB meter is between USB and XIAO-ESP32S3-cam.__ The multimeter, on its mA range, is the in-series meter at A or B
- __XIAO-ESP32S3-cam runs [`soak-power`](../../firmware/soak-power/)__. It prints its NVS reset history at every boot, so a reset at a USB change that nobody saw still shows, with its reason, the next time it is on USB
- __Stay with it.__ A LiPo is never charged unattended; charge on a hard, non-flammable surface

## 3 — No USB: both run on the battery

1. Wires at A and B. Plug the battery in
2. __Both boot__ — XIAO-ESP32S3-lora's node appears in the Meshtastic app; XIAO-ESP32S3-cam runs whatever it carries

## 4 — What XIAO-ESP32S3-lora draws

Still no USB.

1. __Multimeter in series at B.__ Read XIAO-ESP32S3-lora's draw for a minute, through a few beacon transmissions, and write down the typical reading and the highest seen
2. Wire back at B

This is the number [#8](https://github.com/jwilleke/js-rocket-avionics/issues/8) never had. It is what the chargers lose to the lora side while charging.

## 5 — Charging

Start with the battery partly run down — __~3.7 V resting__ — so there is a full-current stretch to see. Running both XIAOs on it for half an hour or so does that.

1. __Multimeter in series at A__, the battery's own lead. Plug USB into XIAO-ESP32S3-cam
2. __Both XIAOs keep running__ — XIAO-ESP32S3-lora's node stays heard
3. __Meter A is the net current into the battery.__ __It must be positive__, and well above zero. If it reads negative — the battery discharging — unplug USB and stop
4. __The two chargers must stay under 500 mA__: meter A plus XIAO-ESP32S3-lora's draw from step 4. If more, unplug USB and stop
5. __XIAO-ESP32S3-cam's `5V` pin to `GND`__, with a second meter or by moving the multimeter briefly (wire back at A first). This is the check that the XIAO's internal path from its USB-C to that pin carries the load — Seeed's schematic shows it as bare copper, no fuse or diode, with no rating written. Write the reading down, and the resistor it was taken with
6. __Read meter A at 1, 5, 15 and 30 minutes__, and the battery voltage at the battery row. __A current that falls while the battery is still well under 4.1 V is the chip protecting itself from heat__ — thermal regulation, not a fault. On the adapter it has little copper; write down that it did, and when
7. __Touch-test the chip__ — carefully, with a fingertip on the adapter beside it. Hot to the touch is expected. Too hot to hold means it is throttling, which the readings will already show
8. __Charged is when meter A falls to near zero with the battery at ~4.2 V.__ The chargers never stop while XIAO-ESP32S3-lora runs, so there is no "done" light to wait for. Write down the time
9. __Unplug USB.__ Both XIAOs carry on. Ten minutes later, the battery's resting voltage

## 6 — Power down

Unplug the battery. __A battery left on both XIAOs drains past its safe limit overnight__ — [LiPo-500mAh.md](../../hardware/LiPo-500mAh/LiPo-500mAh.md).

## Record on #30

| | Reading |
|---|---|
| Adapter: row spacing and outline (step 1) | |
| Adapter: which header pin is which chip leg (step 1) | |
| `PROG` resistor fitted | |
| XIAO-ESP32S3-lora's draw, typical and highest (step 4) | |
| Net current into the battery at 1, 5, 15, 30 min, with battery voltage (step 5) | |
| Chargers' total (step 5) | |
| `5V` pin while charging (step 5) | |
| Throttled? When? (step 5) | |
| Start voltage → charged, and the time (step 5) | |
| Resting voltage 10 min after (step 5) | |
| XIAO-ESP32S3-cam or XIAO-ESP32S3-lora reset at any USB change? | |
