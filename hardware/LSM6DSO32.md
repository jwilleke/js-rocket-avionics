# LSM6DSO32 — 6-DoF IMU

__The apogee sensor.__ ±32 g accelerometer plus gyro, on a STEMMA QT breakout sharing the BMP388's layout.

## Why ±32 g, and why that reason is now stale

[design.md](../docs/design.md) selected this part against a __17.6 g boost peak__ — 32.90 N peak thrust over a 0.190 kg liftoff mass — on the argument that __±16 g parts clip during boost__ and a clipped boost integral destroys the velocity estimate for the whole flight. MPU6050, LSM6DS3, ICM-20948, ICM-42688-P and ADXL345 are all ±16 g and were all ruled out on it.

> __That 17.6 g figure describes a single-stage rocket, and flight 3 is two-stage.__ Against the weighed flight-3 masses the peak is __7.3–13.0 g__ depending on case. __Keep the part__ — it is bought, in hand, and the headroom costs nothing — but the stated reason no longer holds, and it is filed under constraints that must not be re-litigated, which is how a stale rule gets defended. Correcting it is [#12](https://github.com/jwilleke/js-rocket-avionics/issues/12).

## The FIFO is a hard requirement

__9 KB__, and [design.md](../docs/design.md) treats it as non-negotiable on any substitute: __do not poll at 500 Hz__. Batch-reading cuts ISR load, relieves the PSRAM path, and means a brief stall __queues samples in the sensor instead of losing them__.

__The gyro is not the apogee sensor.__ The accelerometer is. The gyro exists so body-frame acceleration can be rotated into the earth frame and gravity subtracted off the correct axis as the rocket tips over.

## Substitutes

| Part | Range | Gyro | Note |
|---|---|---|---|
| __BMI088__ | ±24 g | yes | Bosch, widely stocked, ~$12 |
| __MPU6050 + ADXL375__ | ±16 g + ±200 g | yes | One chip for coast and attitude, one for boost |
| __MPU6050 + H3LIS331DL__ | ±16 g + ±400 g | yes | Same split, more headroom |

The two-chip split is where this design began. __Reverting costs +1 g and one I2C address — no extra pins__, since everything shares the bus.

__Integrated 10DOF modules were evaluated and rejected.__ The DFRobot Gravity 10DOF is representative: its BMI323 maxes at ±16 g, it is 32 × 27 mm — wider than the carrier — uses a PH2.0 flying lead, and carries a magnetometer this design deliberately excludes.

## Mounting

__Flat, not perpendicular.__ Settled on the BMP388's measurements and it survives the form-factor surprise below: screws on the __Aux__ edge with the Primary header soldered opposite give __two-point restraint__ across the board, which is what boost loading wants and what a cantilevered header cannot offer. Flat also stacks low against the __19.7 mm__ available at the bore centre.

__Module footprint, not the bare chip.__ A bare LSM6DSO32 is an __LGA-14 at 2.5 × 3 mm__ and is not hand-solderable.

__The screw is M2__ — the project standard, see [Fasteners](README.md#fasteners--m2-everywhere). Nothing here is sized off a datasheet hole: M3 does not fit these breakouts, and the BMP388's holes measured Ø2.35 against a published 2.5. __What is still owed on this part is the hole *spacing*__, not the diameter.

## Photographs — and the form factor is not what was assumed

| [Front](../docs/resources/LSM6DSO32-front.jpg) | [Back](../docs/resources/LSM6DSO32-back.jpg) |
|---|---|
| ![LSM6DSO32 front](../docs/resources/LSM6DSO32-front.jpg) | ![LSM6DSO32 back](../docs/resources/LSM6DSO32-back.jpg) |

__Read off the photographs, not off calipers.__ Dimensions are still owed — see Open below.

> __It does not share the BMP388's form factor.__ [module-pinouts.md](../docs/module-pinouts.md) expected it to: *"the LSM6DSO32 shares this form factor and is expected to match."* __It has two header rows, not one__, and __both mounting holes sit on the same edge as one of them__, where the BMP388's sit on the edge opposite its single row.

| | BMP388 | LSM6DSO32 |
|---|---|---|
| Header rows | __one__, 8 pins | __two__ — 9-pin `Primary I2C/SPI`, 5-pin `Aux. I2C/SPI` |
| Mounting holes | long edge __opposite__ the header | flanking the __Aux__ row, on that edge |

__The mounting conclusion survives the surprise.__ Screws on the Aux edge and the Primary header soldered on the opposite edge still gives __two-point restraint across the board__, which is what [module-pinouts.md](../docs/module-pinouts.md) wanted from flat mounting. The premise was wrong; the answer is unchanged.

### Measured 2026-09-05

__Outline 25.5 × 17.8 mm__, __mounting-hole spacing 20.58 mm__ (provisional — *"appears to be"*), __thickness over the Qwiic connectors 4.80 mm__, __header pitch 2.54 mm__.

__That is the BMP388 exactly__ — same 25.5 × 17.8 outline, same 20.58 mm centres, 4.79 mm thick — so __the carrier carries one hole pattern, placed twice__: two M2 clearance holes at 20.58 mm centres. What differs between the two boards is the rotation, not the drilling: the BMP388's holes are on the edge opposite its header, these are on the __Aux__ edge with the Primary row opposite.

> __The holes are not on the end pins' centres.__ At 2.54 mm pitch the 9-pin Primary row spans __20.32 mm__ against __20.58 mm__ of hole spacing, so the holes sit __0.13 mm outboard on each side__. Invisible by eye, and a trap if the footprint snaps its holes to the end pads.

### Y offsets, measured 2026-09-06

Header row centreline __2.54 mm__ from its near long edge; mounting-hole centreline __14.65 mm__ from the far long edge, __3.15__ from the near; holes __2.54 mm__ in from each short side. __Identical on the BMP388.__

The hole readings close on the 17.80 width exactly. The header pair does not — 2.54 + 15.75 = 18.29, so __use the 2.54__ and derive 15.26. Full working, and the 0.16 mm hole-spacing discrepancy worth one tie-break reading before fabrication, in [module-pinouts.md](../docs/module-pinouts.md).

### What the silkscreen says

__Primary row, 9 pins:__ `VIN 3Vo GND SCL SDA DO CS I1 I2`, labels alternating above and below the row.

__Aux row, 5 pins:__ `SCX SDX CS DO GND`. Exact ordering wants confirming with the part in hand rather than off a photograph.

Back silkscreen, all of it useful:

- __`ST LSM6DSO32`, `6-DoF Accel+Gyro IMU`__ — the *"confirm the silicon matches the label"* check at the foot of [module-pinouts.md](../docs/module-pinouts.md) __passes__
- __`Accel ±4/8/16/32 g`__ — ±32 g confirmed on the part, not on a listing
- `Gyro ±125~2000 dps`
- __`I2C Addr 0x6A`__ with an `AD0` solder jumper — __no clash with the BMP388's 0x77__, confirming from the part what [design.md](../docs/design.md) claimed from datasheets
- __`I2C VLogic/Vcc: 3-5VDC`__ — worth noting, because that exact wording is what *"did not survive the part arriving"* on the BMP388, whose board turned out to be marked 3 V. __Here it really is on the part__
- STEMMA QT on both short edges; board marked revision __B__

## Open — this part is the bottleneck

__It has been in hand since 2026-08-10 and has never been measured.__ [module-pinouts.md](../docs/module-pinouts.md) names it as *"the last unknown blocking sensor footprints"*, and the carrier has sat at stage 2c ever since.

__Do not assume it matches the BMP388.__ It is expected to share the form factor, but the BMP388 disagreed with its own datasheet in two places — Ø2.35 mm holes against a published 2.5, so __an M2.5 screw does not fit__, and 4.79 mm thick against 4.4.

Measuring it is [#5](https://github.com/jwilleke/js-rocket-avionics/issues/5): header pin order, hole diameter and spacing, board length and width, thickness over the Qwiic connectors, and confirmation that the silicon matches the label.

---

Part numbers, vendors and masses live in [BOM.md](../docs/BOM.md), which is the single source of truth for both. Purchase history is in [shopping-list.md](../docs/shopping-list.md); the reasoning is in [design.md](../docs/design.md).
