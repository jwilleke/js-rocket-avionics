---
title: Bench bring-up
description: One session that closes #6, #7 and #8 — the epic that gates ordering copper.
---

# Bench bring-up

__One session, three issues.__ [#6](https://github.com/jwilleke/js-rocket-avionics/issues/6), [#7](https://github.com/jwilleke/js-rocket-avionics/issues/7) and [#8](https://github.com/jwilleke/js-rocket-avionics/issues/8) all block [#4](https://github.com/jwilleke/js-rocket-avionics/issues/4), which blocks [#11](https://github.com/jwilleke/js-rocket-avionics/issues/11), which is the order. They are written as three issues because they fail differently; they are __one bench session__ because the setup is the same and #8 cannot run until the other two have.

__Nothing needs buying.__ Every part is in hand. The carrier PCB and the arming switch are not needed to power anything up — and the arming switch is now [a convenience rather than a requirement](../hardware/Arming-switch.md), so it is not waiting on this either.

__Nothing in `fab/` goes to a fab until this closes.__ That directory holds a complete-looking gerber set generated from a board that is missing most of its footprints.

## Run it in this order, and the order is the point

Each step is cheap to fail and tells you something the next one assumes. Running #8 first would tell you nothing, because a brownout you cannot attribute is not a measurement.

| | Step | Fails cheaply because |
|---|---|---|
| 1 | __Stack check__, no power | A mechanical collision is not a bench nuisance, it is a design change |
| 2 | [__#6__](https://github.com/jwilleke/js-rocket-avionics/issues/6) XIAO-ESP32S3-lora alone | No firmware to write. If it does not enumerate, nothing downstream matters |
| 3 | [__#7__](https://github.com/jwilleke/js-rocket-avionics/issues/7) XIAO-ESP32S3-cam alone | Sensors before camera; I2C before SD. Each layer rules out the one below |
| 4 | [__#8__](https://github.com/jwilleke/js-rocket-avionics/issues/8) both on one cell | Only meaningful once each half is known good |

## 1 — Stack check, before any power

__The one genuinely open question on [#6](https://github.com/jwilleke/js-rocket-avionics/issues/6) is mechanical.__ The [L76K](../hardware/L76K-GNSS.md) plugs onto the XIAO's own 14 pads rather than presenting a header, so it and the [Wio-SX1262](../hardware/Wio-SX1262-LoRa.md) compete for the same B2B space. The two parcels arrived weeks apart and __nobody has ever stacked them__.

- Fit [XIAO-ESP32S3-lora](../hardware/XIAO-ESP32S3-lora.md) + Wio-SX1262 + L76K, dry, no cell
- __If they foul, stop and write it down.__ That is a layout change: the L76K returns to the carrier as a footprint needing ~21 mm, which the 95 mm board has but [#14](https://github.com/jwilleke/js-rocket-avionics/issues/14) has not allowed for
- Check the __≥50 mm antenna separation__ from [design.md](design.md) is physically achievable in the stack you just built. 915 MHz TX desenses a 1575 MHz front end by broadband noise, and the bench is where that first becomes observable

## 2 — #6, the beacon

__No firmware.__ That is the entire premise of this module: a supported Meshtastic device out of the box. Bring-up here confirms the premise rather than writing code.

- Power the matched kit over USB and confirm it __enumerates as Meshtastic, untouched__
- Get a __GPS fix outdoors__ and record __time to first fix__
- Range-check the __82 mm U.FL whip__. The beacon is the recovery system, and an untested link is an untested recovery

> __Its USB-C is not used in the flight build__ — charging and service go through the Sense stack, because this module must never be reflashed. Using its port on the bench is fine and expected; just note that the flight configuration has no service access to it.

## 3 — #7, the recorder

__Firmware exists now:__ [`firmware/bringup-cam/`](../firmware/bringup-cam/), a PlatformIO project. It runs #7's four criteria in the order that fails cheapest and prints a PASS/FAIL line for each. __It is untested — no hardware has run it__ — so a failure means check the wiring *and* check the code.

```sh
cd firmware/bringup-cam
pio run -t upload && pio device monitor
```

__No IDE settings to remember.__ Board, PSRAM and the partition table are all in [`platformio.ini`](../firmware/bringup-cam/platformio.ini), which is why this is not a sketch — `-DBOARD_HAS_PSRAM` is load-bearing, and a camera that fails to allocate its frame buffers reports an error that reads like a hardware fault.

Four wires per sensor, both on I2C:

```text
XIAO 3V3 -> sensor VIN      <- NOT 3Vo, that is the sensor's own regulator output
XIAO GND -> sensor GND
XIAO D4  -> sensor SDA
XIAO D5  -> sensor SCL
buzzer   -> D0 and GND      <- passive piezo, no supply rail
```

__Three traps, already paid for once__ and recorded in [module-pinouts.md](module-pinouts.md):

- __CS must be HIGH__ or a BMP3xx drops into SPI mode and never answers on I2C. If 0x77 is silent, check this before anything else
- __SDO selects the address, it is not data.__ High = 0x77, low = 0x76
- __Ignore the seller's wiring diagram.__ It is SPI, wired to Arduino 13/12/11/10, and following it wastes a session

__One trap that is new and not in any issue:__ the LSM6DSO32's full-scale bits are __not__ the LSM6DSO's. On the -32 part, `FS = 01` is ±32 g and `11` is ±16 — so assuming the top code is the top range gives you half the range and a plausible-looking number. If every axis reads near zero at rest, that is the first thing to check.

## 4 — #8, both on one cell

__This is the one that can change the copper__, so run it last and run it properly.

- Both modules on the __single cell__, camera capturing and LoRa transmitting
- Scope the rail through __camera inrush and SD write bursts__; failing a scope, watch the beacon for resets and read its log
- Measure __actual current draw__ against the ~300 mA estimate
- __Repeat on a partially discharged cell.__ A full cell is the easy case and sag is worst near the bottom

### Measure two more things while it is on the bench

Neither is in #8 as written, and both are nearly free once the setup exists.

__Actual runtime.__ 500 mAh against a ~300 mA *estimate* gives ~100 minutes. That figure now carries weight it did not before: with arming settled as a convenience, __"how long from connecting the cell to recovery"__ is the real operational limit on a launch day. Measure the draw rather than trusting the estimate, and correct [BOM.md](BOM.md).

__The two regulators.__ Both modules' `3V3` pins land on the __same plane__ on the carrier, so their regulators run __in parallel__ — see [PCB-carrier.md](../hardware/PCB-carrier.md#how-power-actually-reaches-everything). Linear regulators do not share load: whichever holds the marginally higher output does all the work until it current-limits, and if one module loses its pigtail the other back-feeds into its regulator output. __This is a consequence of the layout rather than a decision anyone made.__ Put a meter on both 3V3 pins with the camera running and write down what you see. The regulator type is assumed rather than read off Seeed's schematic, so read that too if the numbers look odd.

## What closing this epic requires

Not "it worked". A __stated verdict__ on the coupling, because that is the one that lands in copper:

- __acceptable__ — order as drawn
- __needs decoupling__ — bulk capacitance or separate regulators, and it goes into the layout __before__ [#16](https://github.com/jwilleke/js-rocket-avionics/issues/16)
- __needs the second cell__ — which was priced and rejected at +8 g, and can only be re-priced now that somebody knows how bad the coupling actually is

Write the numbers down even when they are boring. The predictions this epic exists to test have been sitting in [BOM.md](BOM.md) as accepted risks for weeks, and an accepted risk nobody measured is just a guess with a checkbox.
