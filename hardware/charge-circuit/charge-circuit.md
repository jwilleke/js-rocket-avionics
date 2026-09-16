# Charge circuit

__The battery's charger on the PCB-carrier.__ USB into [XIAO-ESP32S3-cam](../XIAO-ESP32S3-cam/XIAO-ESP32S3-cam.md), directly or through the service pigtail ([#1](https://github.com/jwilleke/js-rocket-avionics/issues/1)), charges the [LiPo-500mAh](../LiPo-500mAh/LiPo-500mAh.md) with both XIAOs still running. There is nothing to operate: plugging USB in starts it.

Part numbers are in [BOM.md](../../docs/BOM.md). Where it sits on the board is on [PCB-carrier.md](../PCB-carrier/PCB-carrier.md#tall-side--faces-270-the-camera). Decisions are on [#30](https://github.com/jwilleke/js-rocket-avionics/issues/30); the reasoning is in [PCB-carrier-design.md](../PCB-carrier/PCB-carrier-design.md#charging-on-the-carrier--a-charger-chip-on-an-adapter-no-cut-off-switches).

## What it is

| Part | What it does | Values |
|---|---|---|
| __MCP73831 charger chip, on its adapter__ | charges the battery from XIAO-ESP32S3-cam's `5V` pin | SOT-23-5, soldered to a __6-pad SOT-23-to-DIP adapter__. __3.0 kΩ__ on `PROG`: 1000 V ÷ 3.0 kΩ = __333 mA__, 300–367 mA across the datasheet's ±10%. __4.7 µF__ on `VDD` and on `VBAT`. `STAT` not connected — a light inside a closed nose is seen by nobody |
| __XIAO-ESP32S3-cam's built-in charger__ | charges the battery through its BAT pigtail. It cannot be turned off | inside the XIAO, ~115–120 mA |

```text
  XIAO-ESP32S3-cam 5V pin --+-- adapter pin VDD (chip pin 4)
                            |
                          4.7 uF
                            |
                           GND        adapter pin PROG (chip pin 5) -- 3.0 kΩ -- GND
                                      adapter pin VSS  (chip pin 2) -- GND
                                      adapter pin STAT (chip pin 1) -- not connected
  VBAT --+-- adapter pin VBAT (chip pin 3)
         |
       4.7 uF
         |
        GND
```

Chip pins from Microchip's datasheet, table 3-1: 1 `STAT`, 2 `VSS`, 3 `VBAT`, 4 `VDD`, 5 `PROG`. One adapter pad is unused.

## How it behaves

- __Up to ~487 mA from the two chargers__ — the chip's 367 at the top of its tolerance plus the XIAO's 120 — __under the battery's 500 mA limit__. That limit is why the resistor is 3.0 kΩ
- __XIAO-ESP32S3-lora stays on the battery while charging.__ It takes its share of the chargers' current and the rest goes into the battery, so charging is slower by the lora side's draw. The beacon and GPS keep running
- __The charge never shows done.__ The chargers hold the battery at 4.2 V and supply XIAO-ESP32S3-lora for as long as USB is in. __Unplug when charged; never leave it plugged in unattended__
- __No cut-off switches__, for either XIAO. Both chargers stop at 4.2 V, and nothing switches when USB goes in or out
- __USB into one XIAO at a time, never both.__ With both in, XIAO-ESP32S3-lora's own charger joins the other two and the total passes the battery's 500 mA — [Two chargers on one battery](../LiPo-500mAh/LiPo-500mAh.md#two-chargers-on-one-battery)
- __The USB source must give ~0.6 A__ — XIAO-ESP32S3-cam's own draw plus the chip. A USB-C charger or power bank does; an old USB-A port through an A-to-C cable promises 500 mA and may sag
- __It gets hot.__ At the start of a charge the chip turns about 0.5 W into heat. On the adapter it has only six pins to shed it into, so it cuts its own current to protect itself — thermal regulation. That costs charge time, not safety. Keep the sensors away from it

## Mounting — the adapter on header pins

__No bare surface-mount chip is soldered to the carrier.__ The chip goes onto the adapter on the bench, and that adapter stands on the carrier like the sensor breakouts:

- __Straight male header pins__ through the adapter's six pads, soldered on top
- The pins go through __six through-holes__ in the carrier, two rows of three at 2.54 mm, and are soldered on the far side
- __On the carrier's tall side, in its forward end__ — [PCB-carrier.md](../PCB-carrier/PCB-carrier.md#tall-side--faces-270-the-camera). About 5 mm tall: header plastic, the adapter and the chip
- The 3.0 kΩ and both 4.7 µF are on the carrier beside the adapter's pins
- __The adapter proven on the [charging bench](../../docs/bench-work/charging-bench.md) is the one that flies.__ The chip is soldered once

__Measured on the part, not yet known:__

| | Value |
|---|---|
| Spacing between the adapter's two pin rows, centre to centre | *owed — adapters not yet delivered* |
| Adapter outline | *owed* |
| Which adapter pad connects to which chip leg | *owed — continuity-checked on the bench, step 1* |

__The carrier's six holes are drawn from these.__ Until they are measured, the charge circuit stays on PCB-carrier.md's [Not yet in the generator](../PCB-carrier/PCB-carrier.md#not-yet-in-the-generator) list.

## Owed before copper

- __XIAO-ESP32S3-cam's `5V` pin carries the chip's current.__ Seeed's schematic shows copper straight from the USB-C's `VBUS` to that pin, no fuse or diode, and no rating written
- __The net current into the battery is well positive__ with XIAO-ESP32S3-lora running. Its draw on its own has never been measured

The [charging bench](../../docs/bench-work/charging-bench.md) measures both.
