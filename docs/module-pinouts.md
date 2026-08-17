# Module pinouts, measured off the parts

**Footprints cannot be drawn until these are read off the physical parts.** Vendor listings copy Adafruit's product text verbatim, and this project has already caught two places where the board in hand disagreed with the datasheet it was sold under. A wrong pin order scraps a board rather than costing a re-solder.

**BMP388 is confirmed. Nothing else is.**

Moved here from the rocket repo's `electronics-plan.md` — this is footprint input for the carrier PCB, so it belongs with the copper. What each part *is* and why it was chosen stays in [BOM.md](BOM.md); the design record stays in [electronics-plan.md](https://github.com/jwilleke/js-rocket/blob/main/docs/planing/electronics-plan.md).

## BMP388 — confirmed from the part

Eight pins, 0.1 in pitch, single row along one long edge, labels alternating above and below:

| Pin | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| | **VIN** | 3Vo | **GND** | **SCL** | SDO | **SDA** | CS | INT |

Identical to Adafruit 3966, which labels 4 and 6 as SCK/SDI for SPI — same pins. So it is a true layout clone and the STEMMA QT dimensions (25.5 × 17.8 mm, two mounting holes) hold.

**We use four: 1, 3, 4, 6** — VIN, GND, SCL, SDA.

**The seller's wiring diagram is SPI, and following it will waste a bench session.** It wires SCL/SDO/SDA/CS to Arduino 13/12/11/10, which are SCK/MISO/MOSI/SS — the hardware SPI pins. On BMP3xx the pins are dual-purpose: in SPI mode SCL is the clock, SDO is MISO and SDA is MOSI. We use I2C, which needs only the four above.

Two I2C gotchas, both worth knowing *before* bring-up:

- **CS must be HIGH to select I2C.** CS low puts a BMP3xx into SPI mode. Adafruit's layout pulls it up so I2C is the default and this is a layout clone — but **if the sensor does not enumerate at 0x77, check CS first**. It is the most likely cause.
- **SDO selects the address, it is not data.** High = 0x77 (default, jumper open), low = 0x76. Leave it alone unless a second barometer is ever added.

**Power to VIN, never to 3Vo.** `3Vo` is the on-board regulator's *output*; back-feeding it kills the LDO.

**The `3-5VDC` figure did not survive the part arriving.** This section previously stated the back silkscreen read `Vcc/Logic: 3-5VDC`, which is Adafruit's wording and is what the listing copies. The board in hand is **marked 3 V**. Since the design runs +3V3 into VIN, nothing in it changes — but **5 V is no longer a documented fallback**, and the back silkscreen should be read cleanly before anyone relies on one. It is a good illustration of the rule at the top of this page: the listing describes Adafruit's board, not necessarily this one.

Back silkscreen also confirms **`addr default 0x77`** with a solder jumper for 0x76, and SPI/I2C selectable.

Header ships **loose and un-soldered**, confirmed on the part — which keeps the mounting orientation open.

## BMP388 — measured 2026-08-08

Calipers and scale, on the board in hand. Photos: [front](resources/PXL_20260808_193009460.jpg), [back](resources/PXL_20260808_192959846.jpg).

| | Measured | Was assumed | |
|---|---|---|---|
| Mass | **1.8 g** — [BOM.md](BOM.md) owns this figure | 1.0 g (old estimate) | **+80%** |
| Thickness over Qwiic connectors | **4.79 mm** | 4.4 mm (Adafruit) | +0.4 |
| Mounting-hole diameter | **Ø2.35 mm** | 2.5 mm (Adafruit) | **undersize** |
| Mounting-hole spacing | **20.58 mm** | — | now known |
| Qwiic cables supplied | 2 × **110 mm** | "two included" | — |

The front photo confirms the recorded pin order on the physical silkscreen — **VIN, 3Vo, GND, SCL, SDO, SDA, CS, INT**, labels alternating above and below the row — with the two Qwiic connectors on the short edges and both mounting holes on the long edge opposite the header. The layout-clone assumption holds.

**The mounting screw is M2, not M2.5.** Ø2.35 mm passes an M2 (2.0 mm major) with 0.35 mm of total clearance; an M2.5 does not fit at all. Adafruit's own breakouts use 2.5 mm holes, so anyone sizing this off the datasheet rather than the part will pick a screw that will not go in.

**The sled's bosses must be modelled oversize.** Same rule as the anchor bore in the rocket repo's [sections.md](https://github.com/jwilleke/js-rocket/blob/main/docs/sections.md) — a hole modelled at nominal prints undersize by ~0.3 mm on that printer. Model for M2 clearance accordingly, and do not copy the 2.35 mm figure straight into CAD.

**20.58 mm of spacing on a 25.5 mm edge** puts the holes ~2.46 mm in from each end, which is the standard STEMMA QT placement and consistent with the clone claim. **Board length and width were not measured** — the 25.5 × 17.8 mm figures are still Adafruit's. Worth two minutes with the calipers already out, since the footprint depends on them.

## Still needed

- **LSM6DSO32** (Adafruit 4692) — header order. **Due 2026-08-11**, and it is the last unknown blocking sensor footprints
- **L76K GNSS** — it plugs onto the XIAO's 14 pads rather than using its own header, so the question is **stack collision with the Wio-SX1262 on the B2B**, not pin order. Needs both Seeed parcels, and they arrive weeks apart
- **Buzzer, reed switch** — trivial, two pins each

Arrival dates are in [shopping-list.md](shopping-list.md).

## The mounting-orientation question

Both sensors put their header on **one edge only**. Two ways to mount, and it is a real 2c decision:

- **Perpendicular** — header into the carrier, board standing up. Simple, but ~17.8 mm tall plus header against **19.7 mm** available at the bore centre, and **cantilevered off the header alone**.
- **Flat** — right-angle headers or short links, with the mounting holes doing the mechanical work. Lower and far better for shock, more fiddly to assemble.

**Flat is the answer, and the calipers settled it.** On the BMP388 the two mounting holes sit at the corners of the edge *opposite* the header, with the Qwiic connectors on the short sides — confirmed on the part. Screws at one end and a soldered header at the other gives **two-point restraint** across the board, exactly what boost loading wants and what perpendicular mounting cannot offer.

Flat also wins on height now that the board is measured. It stacks **4.79 mm** plus standoff against the **19.7 mm** available at the bore centre; perpendicular would stand 17.8 mm of board plus header into that same 19.7 mm, cantilevered off the header alone.

**Footprint inputs, from the part:** two Ø2.35 mm holes at 20.58 mm spacing, **M2 screws**. See [BMP388 — measured](#bmp388--measured-2026-08-08) above. The LSM6DSO32 shares this form factor and is expected to match, but **it is in hand since 2026-08-10 and still unmeasured — measure it, do not assume** — this board already disagreed with Adafruit's dimensions in two places.

## Before designing a footprint round any module

**Confirm the silicon matches the label.** Clone listings copy Adafruit's product text verbatim and the chip does not always match.

- BMP3xx `reg 0x00` → **0x50 = BMP388**, 0x60 = BMP390. A **BMP280** answers **0x58** at `reg 0xD0`.
- **Photograph the header pin order** with the part in front of you, as was done for the BMP388 above. That order is the footprint input.
