# Module pinouts, measured off the parts

__Footprints cannot be drawn until these are read off the physical parts.__ Vendor listings copy Adafruit's product text verbatim, and this project has already caught two places where the board in hand disagreed with the datasheet it was sold under. A wrong pin order scraps a board rather than costing a re-solder.

__BMP388 is confirmed. Nothing else is.__

Moved here from the rocket repo's `electronics-plan.md` — this is footprint input for the carrier PCB, so it belongs with the copper. What each part *is* and why it was chosen stays in [BOM.md](BOM.md); the design record stays in [electronics-plan.md](https://github.com/jwilleke/js-rocket/blob/main/docs/planing/electronics-plan.md).

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

Calipers and scale, on the board in hand. Photos: [front](resources/PXL_20260808_193009460.jpg), [back](resources/PXL_20260808_192959846.jpg).

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

__20.58 mm of spacing on a 25.5 mm edge__ puts the holes ~2.46 mm in from each end, which is the standard STEMMA QT placement and consistent with the clone claim. __Board length and width were not measured__ — the 25.5 × 17.8 mm figures are still Adafruit's. Worth two minutes with the calipers already out, since the footprint depends on them.

## Still needed

- __LSM6DSO32__ (Adafruit 4692) — header order. __Due 2026-08-11__, and it is the last unknown blocking sensor footprints
- __L76K GNSS__ — it plugs onto the XIAO's 14 pads rather than using its own header, so the question is __stack collision with the Wio-SX1262 on the B2B__, not pin order. Needs both Seeed parcels, and they arrive weeks apart
- __Buzzer, reed switch__ — trivial, two pins each

Arrival dates are in [shopping-list.md](shopping-list.md).

## The mounting-orientation question

Both sensors put their header on __one edge only__. Two ways to mount, and it is a real 2c decision:

- __Perpendicular__ — header into the carrier, board standing up. Simple, but ~17.8 mm tall plus header against __19.7 mm__ available at the bore centre, and __cantilevered off the header alone__.
- __Flat__ — right-angle headers or short links, with the mounting holes doing the mechanical work. Lower and far better for shock, more fiddly to assemble.

__Flat is the answer, and the calipers settled it.__ On the BMP388 the two mounting holes sit at the corners of the edge *opposite* the header, with the Qwiic connectors on the short sides — confirmed on the part. Screws at one end and a soldered header at the other gives __two-point restraint__ across the board, exactly what boost loading wants and what perpendicular mounting cannot offer.

Flat also wins on height now that the board is measured. It stacks __4.79 mm__ plus standoff against the __19.7 mm__ available at the bore centre; perpendicular would stand 17.8 mm of board plus header into that same 19.7 mm, cantilevered off the header alone.

__Footprint inputs, from the part:__ two Ø2.35 mm holes at 20.58 mm spacing, __M2 screws__. See [BMP388 — measured](#bmp388--measured-2026-08-08) above. The LSM6DSO32 shares this form factor and is expected to match, but __it is in hand since 2026-08-10 and still unmeasured — measure it, do not assume__ — this board already disagreed with Adafruit's dimensions in two places.

## Before designing a footprint round any module

__Confirm the silicon matches the label.__ Clone listings copy Adafruit's product text verbatim and the chip does not always match.

- BMP3xx `reg 0x00` → __0x50 = BMP388__, 0x60 = BMP390. A __BMP280__ answers __0x58__ at `reg 0xD0`.
- __Photograph the header pin order__ with the part in front of you, as was done for the BMP388 above. That order is the footprint input.
