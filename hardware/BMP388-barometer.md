# BMP388 — barometer

__The only module measured off the part.__ Unported, and deliberately demoted.

## What it is for

Not the altimeter. With the static port dropped, its jobs are __timestamping the ejection event and detecting landing__.

__The port was dropped for five reasons__, of which [design.md](../docs/design.md) calls the last decisive:

1. __No legal location__ — ports want a straight section ≥1 caliber clear of any transition; the longest run above the sled is __0.33 cal__
2. __Cannot be built__ — extending the body to a full caliber costs +38 mm against 15.9 mm of build headroom, and 3:1 fineness breaks
3. __Unrepeatable__ — hand-drilled into a part with no generator that takes 2 h 48 m to print
4. __Drags a pressure bulkhead in with it__ — a new part and a new failure mode
5. __Nothing consumes the number.__ No pyro channels; ejection is the motor delay. Apogee is data, not deployment

A __contamination bulkhead__ — foam or plate, no sealing duty — still belongs at the sled base to keep black-powder particulate off the boards.

Because it is not the altimeter, __the part is interchangeable__: it shares the BMP3xx driver so it was a drop-in for the out-of-stock BMP390, and a generic BMP280 would serve.

## Photographs

| [Front](../docs/resources/BMP388-front.jpg) | [Back](../docs/resources/BMP388-back.jpg) |
|---|---|
| ![BMP388 front](../docs/resources/BMP388-front.jpg) | ![BMP388 back](../docs/resources/BMP388-back.jpg) |

__The front photo confirms the pin order below on the physical silkscreen__ — VIN, 3Vo, GND, SCL, SDO, SDA, CS, INT, labels alternating above and below the row, both Qwiic connectors on the short edges, and both mounting holes on the long edge __opposite__ the header. The board is a blue clone, not an Adafruit black one, which is what makes the layout-clone claim worth having checked rather than assumed.

## Pinout — confirmed from the part

Eight pins, __2.54 mm pitch__ (0.1 in), single row along one long edge, labels alternating above and below:

| Pin | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| | __VIN__ | 3Vo | __GND__ | __SCL__ | SDO | __SDA__ | CS | INT |

__Four are used: 1, 3, 4, 6__ — VIN, GND, SCL, SDA. Address __0x77__, no clash with the IMU.

## Four traps, all documented before bring-up

- __CS must be HIGH to select I2C.__ CS low puts a BMP3xx into SPI mode. If it does not enumerate at 0x77, __check CS first__ — it is the most likely cause
- __SDO selects the address, it is not data.__ High = 0x77 (default, jumper open), low = 0x76
- __Power to VIN, never 3Vo.__ 3Vo is the on-board regulator's *output*; back-feeding it kills the LDO
- __Ignore the seller's wiring diagram.__ It is SPI — SCL/SDO/SDA/CS to Arduino 13/12/11/10, the hardware SPI pins — and following it wastes a bench session

## Measured 2026-08-08 — and why it matters

| | Measured | Assumed | |
|---|---|---|---|
| Thickness over Qwiic connectors | __4.79 mm__ | 4.4 (Adafruit) | +0.4 |
| Mounting-hole diameter | __Ø2.35 mm__ | 2.5 (Adafruit) | __undersize__ |
| Mounting-hole spacing | __20.58 mm__ | — | now known |
| Qwiic cables supplied | 2 × 110 mm | "two included" | — |
| Board outline | __25.5 × 17.8 mm__ | 25.5 × 17.8 (Adafruit) | measured 2026-09-06, __matches__ |
| Header row → near long edge | __2.54 mm__ | — | measured 2026-09-06 |
| Mounting holes → far long edge | __14.65 mm__ | — | measured 2026-09-06 |
| Mounting holes → each short side | __2.54 mm__ | — | measured 2026-09-06 |

__Every figure above is identical on the LSM6DSO32__, so the carrier takes one outline and one hole pattern, placed twice and rotated. Two readings need care — the header's far-edge figure does not close on the width, and hole spacing has two routes 0.16 mm apart. Working in [module-pinouts.md](../docs/module-pinouts.md).

__The mounting screw is M2, not M2.5.__ Ø2.35 passes an M2 with 0.35 mm of total clearance; __an M2.5 does not fit at all__. Anyone sizing this off the datasheet picks a screw that will not go in. This board is where the __M2-everywhere__ standard came from — see [Fasteners](README.md#fasteners--m2-everywhere).

__The `3-5VDC` figure did not survive the part arriving.__ That is Adafruit's wording, which the listing copies; __the board in hand is marked 3 V__. The design runs +3V3 into VIN so nothing changes, but __5 V is no longer a documented fallback__.

__Sled bosses must be modelled oversize__ — a hole modelled at nominal prints undersize by ~0.3 mm on that printer. Do not copy 2.35 straight into CAD.

## Open

- __Board length and width are still Adafruit's figures__, on a board already wrong twice. Two minutes with the calipers — folded into [#5](https://github.com/jwilleke/js-rocket-avionics/issues/5)
- __Never enumerated__ — [#7](https://github.com/jwilleke/js-rocket-avionics/issues/7)

---

Part numbers, vendors and masses live in [BOM.md](../docs/BOM.md), which is the single source of truth for both. Purchase history is in [shopping-list.md](../docs/shopping-list.md); the reasoning is in [design.md](../docs/design.md).

![BMP388-back](../docs/resources/BMP388-back.jpg)
