# Module pinouts, measured off the parts

__Footprints cannot be drawn until these are read off the physical parts.__ Vendor listings copy Adafruit's product text verbatim, and this project has already caught two places where the board in hand disagreed with the datasheet it was sold under. A wrong pin order scraps a board rather than costing a re-solder.

__Both sensor boards are confirmed from the parts__ — the BMP388 by caliper, the LSM6DSO32 by pin order and markings off photographs and by every dimension a footprint needs ([#5](https://github.com/jwilleke/js-rocket-avionics/issues/5), closed 2026-09-06). __Nothing else is.__

Moved here from the rocket repo's `electronics-plan.md` — this is footprint input for the carrier PCB, so it belongs with the copper. What each part *is* and why it was chosen stays in [BOM.md](BOM.md); the design record stays in [electronics-plan.md](https://github.com/jwilleke/js-rocket/blob/main/docs/planing/electronics-plan.md).

## How these are measured — photograph on the grid, not calipers

__Adopted 2026-09-06, operator.__ These parts are 17–25 mm and their features sit on a 2.54 mm pitch; __reading 0.1 mm or better off them with calipers is not realistic__, and two attempts at it produced numbers that did not close (a header pair 0.49 mm over the board width, and hole spacing with two routes 0.16 mm apart).

__The method is: lay the part flat on the printed grid, shoot square-on from directly above, keep the calibration bar in frame, and read the dimensions off the image.__ The grid is [`pcb_measurement_grid.pdf`](bench-work/pcb_measurement_grid.pdf); the bar reads `CALIBRATION BAR 100.0 mm`, so the image's own scale is recoverable from the photograph regardless of camera distance.

Why it is better here:

- __It measures to the feature, not to whatever the jaws could reach.__ Most of the readings wanted are edge-to-hole-__centre__, which a caliper cannot do directly and a grid can
- __It is auditable.__ The photograph is committed, so a disputed number can be re-read years later without the part
- __It reads every dimension at once__, rather than one careful reading at a time
- __Its error is honest__ — perspective, and how squarely the shot was taken. Keep the camera above the part, not off to one side

__Realistic precision is ±0.2–0.3 mm__ on a square-on shot — __but only when the image is actually measured__, in an editor or a script that calibrates off the bar and reads pixel coordinates. It is worse than a caliper's theoretical resolution and __better than a caliper's actual result on parts this size__.

> __Eyeballing a photograph is not the same thing and does not get there.__ Reading these images by eye lands at roughly __±1 mm__, which is fine for confirming a pin count, a marking or a rough outline, and __not__ fine for a footprint. Two eyeball reads of the same LSM6DSO32 grid shot gave 24.3 and 24.7 mm against a board known to be 25.5. Where a number is going into copper, measure the image; do not squint at it.

## BMP388 — confirmed from the part

Eight pins, 0.1 in pitch, single row along one long edge, labels alternating above and below:

| Pin | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| | __VIN__ | 3Vo | __GND__ | __SCL__ | SDO | __SDA__ | CS | INT |

Identical to Adafruit 3966, which labels 4 and 6 as SCK/SDI for SPI — same pins. So it is a true layout clone and the STEMMA QT dimensions (25.5 × 17.8 mm, two mounting holes) hold.

__We use four: 1, 3, 4, 6__ — VIN, GND, SCL, SDA.

__The seller's wiring diagram is SPI, and following it will waste a bench session.__ It wires SCL/SDO/SDA/CS to Arduino 13/12/11/10, which are SCK/MISO/MOSI/SS — the hardware SPI pins. On BMP3xx the pins are dual-purpose: in SPI mode SCL is the clock, SDO is MISO and SDA is MOSI. We use I2C, which needs only the four above.

Two I2C gotchas, both worth knowing *before* bring-up:

- __CS must be HIGH to select I2C.__ CS low puts a BMP3xx into SPI mode. Adafruit's layout pulls it up so I2C is the default and this is a layout clone — but __if the sensor does not enumerate at 0x77, check CS first__. It is the most likely cause.
- __SDO selects the address, it is not data.__ High = 0x77 (default, jumper open), low = 0x76. Leave it alone unless a second barometer is ever added.

__Power to VIN, never to 3Vo.__ `3Vo` is the on-board regulator's *output*; back-feeding it kills the LDO.

__The `3-5VDC` figure did not survive the part arriving.__ This section previously stated the back silkscreen read `Vcc/Logic: 3-5VDC`, which is Adafruit's wording and is what the listing copies. The board in hand is __marked 3 V__. Since the design runs +3V3 into VIN, nothing in it changes — but __5 V is no longer a documented fallback__, and the back silkscreen should be read cleanly before anyone relies on one. It is a good illustration of the rule at the top of this page: the listing describes Adafruit's board, not necessarily this one.

Back silkscreen also confirms __`addr default 0x77`__ with a solder jumper for 0x76, and SPI/I2C selectable.

Header ships __loose and un-soldered__, confirmed on the part — which keeps the mounting orientation open.

## BMP388 — measured 2026-08-08

Calipers and scale, on the board in hand. Photos: [front](../hardware/BMP388-barometer/BMP388-front.jpg), [back](../hardware/BMP388-barometer/BMP388-back.jpg).

| | Measured | Was assumed | |
|---|---|---|---|
| Mass | __1.8 g__ — [BOM.md](BOM.md) owns this figure | 1.0 g (old estimate) | __+80%__ |
| Thickness over Qwiic connectors | __4.79 mm__ | 4.4 mm (Adafruit) | +0.4 |
| Mounting-hole diameter | __Ø2.35 mm__ | 2.5 mm (Adafruit) | __undersize__ |
| Mounting-hole spacing | __20.58 mm__ | — | now known |
| Qwiic cables supplied | 2 × __110 mm__ | "two included" | — |

The front photo confirms the recorded pin order on the physical silkscreen — __VIN, 3Vo, GND, SCL, SDO, SDA, CS, INT__, labels alternating above and below the row — with the two Qwiic connectors on the short edges and both mounting holes on the long edge opposite the header. The layout-clone assumption holds.

__The mounting screw is M2, not M2.5.__ Ø2.35 mm passes an M2 (2.0 mm major) with 0.35 mm of total clearance; an M2.5 does not fit at all. Adafruit's own breakouts use 2.5 mm holes, so anyone sizing this off the datasheet rather than the part will pick a screw that will not go in.

__The sled's bosses must be modelled oversize.__ Same rule as the anchor bore in the rocket repo's [sections.md](https://github.com/jwilleke/js-rocket/blob/main/docs/sections.md) — a hole modelled at nominal prints undersize by ~0.3 mm on that printer. Model for M2 clearance accordingly, and do not copy the 2.35 mm figure straight into CAD.

__20.58 mm of spacing on a 25.5 mm edge__ puts the holes __2.46 mm in from each end__, which is the standard STEMMA QT placement and consistent with the clone claim. __Outline measured 2026-09-06: 25.5 × 17.8 mm__, matching Adafruit's published figures — the one dimension of theirs that survived contact with the part.

## LSM6DSO32 — read off photographs 2026-09-05, not off calipers

Photos: [front](../hardware/LSM6DSO32/LSM6DSO32-front.jpg), [back](../hardware/LSM6DSO32/LSM6DSO32-back.jpg).

__It does not share the BMP388's form factor, which this page assumed it would.__ Two header rows rather than one, and both mounting holes on the same edge as one of them:

| | BMP388 | LSM6DSO32 |
|---|---|---|
| Header rows | __one__, 8 pins | __two__ — 9-pin `Primary I2C/SPI`, 5-pin `Aux. I2C/SPI` |
| Mounting holes | long edge __opposite__ the header | flanking the __Aux__ row, on that edge |

__The flat-mounting conclusion survives.__ Screws on the Aux edge with the Primary header soldered on the opposite edge still gives two-point restraint across the board — the premise below was wrong, the answer is not.

__Primary row, 9 pins:__ `VIN 3Vo GND SCL SDA DO CS I1 I2`, labels alternating above and below.

__Aux row, 5 pins:__ `SCX SDX CS DO GND`. Confirm the ordering against the part; a photograph is not a reading.

Back silkscreen: __`ST LSM6DSO32`__, `6-DoF Accel+Gyro IMU`, __`Accel ±4/8/16/32 g`__, `Gyro ±125~2000 dps`, __`I2C Addr 0x6A`__ with an `AD0` jumper, `I2C VLogic/Vcc: 3-5VDC`, STEMMA QT both short edges, board revision __B__.

Three things that follow:

- __The silicon matches the label__ — the check at the foot of this page passes on this part
- __±32 g is confirmed on the board itself__, not on a listing
- __0x6A does not clash with the BMP388's 0x77__, now confirmed from the part rather than from a datasheet

__`3-5VDC` appears on this board's back and is presumably true here__, unlike the BMP388, where the identical wording came off Adafruit's copy and the part in hand was marked 3 V. The design runs +3V3 either way.

### Measured 2026-09-05

| | Reading | Confidence |
|---|---|---|
| Mounting-hole spacing | __20.58 mm__ | *"appears to be"* — provisional |
| Thickness over Qwiic connectors | __4.80 mm__ | *"about the same"* as the BMP388's 4.79 |
| Header pitch | __2.54 mm__ | confirmed on the BMP388 and the XIAO |
| Board outline | __25.5 × 17.8 mm__ | measured 2026-09-06, __same as the BMP388__ |

__The two sensor boards are the same outline, the same hole pattern and the same thickness.__ 25.5 × 17.8, holes at 20.58 mm centres __2.46 mm in from each end__, 4.79/4.80 thick. For the carrier that means __one footprint outline and one hole pattern, placed twice and rotated__ — not two footprints.

__Both sensors take the same mounting pattern.__ 20.58 mm centres on the LSM6DSO32 against 20.58 mm on the BMP388, and 4.80 mm thick against 4.79 — indistinguishable at this precision. __So the carrier needs one hole pattern, placed twice__: two M2 clearance holes at 20.58 mm centres.

__What differs is not the pattern but its orientation.__ The BMP388's holes sit on the edge opposite its single 8-pin row; the LSM6DSO32's sit on its __Aux__ edge with the Primary row opposite. Same drill pattern, different rotation on the board.

__X positions, derived from the outline and the 2.54 mm pitch — no further measuring:__

| | Span | Inset per end, if centred |
|---|---|---|
| Mounting holes, both boards | __20.58__ | __2.46 mm__ |
| LSM6DSO32 Primary row, 9 pins | 8 × 2.54 = __20.32__ | 2.59 mm |
| BMP388 row, 8 pins | 7 × 2.54 = __17.78__ | 3.86 mm |

> __The holes do not line up with the end pins, and it is close enough to assume they do.__ At 2.54 mm pitch the LSM6DSO32's 9-pin Primary row spans __8 × 2.54 = 20.32 mm__ against a hole spacing of __20.58__. The holes sit __0.13 mm outboard of the end pins on each side__ — a real offset, and one that will not be visible by eye. Do not snap the footprint's holes to the end pads.

__Hole diameter is not an open question.__ The fastener is __M2 across the project__ (operator, 2026-09-05) — M3 does not fit these breakouts and nothing 2.5 mm is being bought. Footprints are drawn for __M2 clearance__, not for whatever a given board's hole measures.

## The Y offsets — measured 2026-09-06, both boards the same

Read off the parts by the operator, *"as best as I can do on these parts"*:

| | Reading |
|---|---|
| Header row centreline → near long edge | __2.54 mm__ |
| Header row centreline → far long edge | 15.75 mm |
| Mounting-hole centreline → far long edge | __14.65 mm__ (so __3.15__ from the near edge) |
| Mounting hole → each short side | __2.54 mm__ |

__Both boards read the same__, which is consistent with everything else: same outline, same pattern, same thickness.

### One pair closes and one does not

__The mounting-hole readings close exactly.__ 14.65 + 3.15 = __17.80__, the measured width. Take those as good.

__The header pair does not.__ 2.54 + 15.75 = __18.29__ against a 17.80 width — __0.49 mm over__, so one of the two is not an edge-to-centre reading. __Use the 2.54__: it is the short, easy reading, it sits on the 0.1 in grid these boards are laid out to, and the far edge then derives as __15.26 mm__. The 15.75 is most likely taken to the far side of the hole rather than its centre.

### The hole spacing has two routes and they differ by 0.16 mm

- From the short-side inset: 25.50 − 2 × 2.54 = __20.42 mm__
- Measured across the holes directly: __20.58 mm__

__0.16 mm, and that matters more than it looks.__ An M2 in a Ø2.35 hole has __0.35 mm of total clearance__, so a 0.16 mm error in hole spacing consumes __46% of it__ before any fabrication or print tolerance is added. It will very likely still assemble; it is not comfortable.

__Worth one tie-break reading before the board is fabricated__, not before the footprint is drawn: outside-edge to outside-edge across both mounting holes, minus one hole diameter. Whichever number that supports becomes the footprint's. Until then the footprint is drawn on __20.58__, the direct measurement of the thing that actually matters.

__Nothing further is needed to draw the footprint.__ Outline, pitch, hole pattern and both Y offsets are in hand, and every X position falls out of the outline and the 2.54 mm pitch.

__One reading is still worth taking before fabrication__ — the hole-spacing tie-break above. It does not block [#14](https://github.com/jwilleke/js-rocket-avionics/issues/14).

## XIAO ESP32S3 — read off the underside 2026-09-08

__The pinout the whole carrier netlist rests on, and until now it was never verified.__ Read off [`XIAO-ESP32-S3-bottom.jpg`](resources/XIAO-ESP32-S3-bottom.jpg) — the labels are on the __underside__, which is why the earlier top-face photo could not settle it.

Underside view, USB-C at the top. __The columns are mirrored from the top view__, which is the trap:

```text
left  column, top -> bottom    5V   GND  3V3  D10  D9  D8  D7
right column, top -> bottom    D0   D1   D2   D3   D4  D5  D6
```

So the numbering runs __D0..D6 down one side, then D7, D8, D9, D10, 3V3, GND, 5V back up the other__:

| Pin | Label | | Pin | Label |
|---|---|---|---|---|
| 1 | __D0__ | ← USB end → | 14 | __5V__ |
| 2 | D1 | | 13 | __GND__ |
| 3 | D2 | | 12 | __3V3__ |
| 4 | D3 | | 11 | D10 |
| 5 | D4 | | 10 | D9 |
| 6 | D5 | | 9 | D8 |
| 7 | __D6__ | ← far end → | 8 | __D7__ |

__Three things this confirms, none of which had been checked:__

- __`RF_Module:MCU_Seeed_ESP32C3`'s geometry is correct for an ESP32-__S3__ board.__ `gen_carrier.py` takes its pad grid from a __C3__ footprint while the parts in hand are S3. The XIAO form factor is standard across variants — but that was an assumption, and this is the reading that supports it.
- __`XIAO_PIN` in `gen_carrier.py` matches the silkscreen__, so [#18](https://github.com/jwilleke/js-rocket-avionics/issues/18)'s fix lands the nets on the right physical pins, not merely on the right footprint pads.
- __Pin 1 = D0 sits at the USB-C end__, so the USB-C faces __aft__ on the carrier. [#1](https://github.com/jwilleke/js-rocket-avionics/issues/1)'s charging pigtail depends on that and had been resting on an inference.

__Also visible and consistent with [XIAO-ESP32S3-cam.md](../hardware/XIAO-ESP32S3-cam/XIAO-ESP32S3-cam.md):__ `BAT+`/`BAT−` are __centre pads on the underside__, not on the castellated edge — which is why the battery reaches each board by soldered pigtail rather than through the headers. The JTAG pads (`MTCK`, `MTDO`, `MTDI`, `MTMS`) sit between them.

## What is left

__Every part is in hand, and every part has an owner__ — a [hardware page](../hardware/README.md), which also indexes the grid photographs. Nothing here is waiting for a part to arrive.

- __One reading is owed, and this page owns it:__ the hole-spacing tie-break above. It is a __pre-fabrication__ check, not a footprint blocker — [#16](https://github.com/jwilleke/js-rocket-avionics/issues/16)
- __[L76K-GNSS](../hardware/L76K-GNSS/L76K-GNSS.md) now needs a pin order, and does not have one.__ It took no carrier footprint until 2026-09-09 and so was never measured; mounting it flat on the carrier makes it a footprint like any other, and __an unread pin order is what scraps a board__. Photograph it on the grid and read the row off the part — [#6](https://github.com/jwilleke/js-rocket-avionics/issues/6), [#14](https://github.com/jwilleke/js-rocket-avionics/issues/14)
- __[PS1240-buzzer](../hardware/PS1240-buzzer/PS1240-buzzer.md)__ — two pins. Nothing to read off it

__There is no reed switch__ — [Arming-switch.md](../hardware/Arming-switch/Arming-switch.md) owns what replaced it and why.

Purchase history is in [shopping-list.md](shopping-list.md).

## The mounting-orientation question

Both sensors put their header on __one edge only__. Two ways to mount, and it is a real 2c decision:

- __Perpendicular__ — header into the carrier, board standing up. Simple, but ~17.8 mm tall plus header against __19.7 mm__ available at the bore centre, and __cantilevered off the header alone__.
- __Flat__ — board parallel to the carrier, standing on its header pins, with the mounting holes doing the rest of the mechanical work. Lower and far better for shock.

__Flat is the answer, and the calipers settled it.__ On the BMP388 the two mounting holes sit at the corners of the edge *opposite* the header, with the Qwiic connectors on the short sides — confirmed on the part. Screws at one end and a soldered header at the other gives __two-point restraint__ across the board, exactly what boost loading wants and what perpendicular mounting cannot offer.

Flat also wins on height now that the board is measured. It stacks __4.79 mm__ plus standoff against the __19.7 mm__ available at the bore centre; perpendicular would stand 17.8 mm of board plus header into that same 19.7 mm, cantilevered off the header alone.

### The header is a straight kit-standard strip — settled 2026-09-08

__Straight headers. Not right-angle, not links.__ The board stands on its pins at the header's own __~2.50 mm__ standoff, parallel to the carrier, with __M2 spacers of the same height__ under the two mounting holes. Header edge and screw edge at the same height is what makes it flat.

__This design already does exactly that.__ A XIAO mounts flat on two straight 1×7 strips — see [Stacking-headers.md](../hardware/Stacking-headers/Stacking-headers.md) and [design.md](design.md). A sensor is the same problem with one header row instead of two, the screws standing in for the second row.

Right-angle would only be needed to lie a board flat with the header entering from the *side*, and nothing here asks for that. __An earlier revision of the bullet above offered "right-angle headers or short links" and never chose between them__; that clause appeared once, propagated to no part page, and was read as an open decision it was never intended to be. It is closed: the strips in the kit are the part, for the bench and for flight, __soldered once and never removed__.

Height, for the record: 4.79 mm board + 2.50 mm standoff = __7.29 mm__ off the carrier, against 10.72 mm for XIAO-ESP32S3-cam on the same face. The sensors do not set the height budget.

__Footprint inputs, from the part:__ two Ø2.35 mm holes at 20.58 mm spacing, __M2 screws__. See [BMP388 — measured](#bmp388--measured-2026-08-08) above. __The LSM6DSO32 was expected to share this form factor and does not__ — it carries two header rows and puts its mounting holes on the same edge as one of them (see above). The two-point restraint argument still holds, on the Aux edge rather than the header-opposite edge. __Its readings are above__ ([LSM6DSO32](#lsm6dso32--read-off-photographs-2026-09-05-not-off-calipers)), taken off the grid rather than with calipers.

## Before designing a footprint round any module

__Confirm the silicon matches the label.__ Clone listings copy Adafruit's product text verbatim and the chip does not always match.

- BMP3xx `reg 0x00` → __0x50 = BMP388__, 0x60 = BMP390. A __BMP280__ answers __0x58__ at `reg 0xD0`.
- __Photograph the header pin order__ with the part in front of you, as was done for the BMP388 above. That order is the footprint input.
