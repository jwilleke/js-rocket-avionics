# js-rocket-avionics

Carrier PCB and flight firmware for the [js-rocket](https://github.com/jwilleke/js-rocket) electronics sled.

**This is one candidate payload for the rocket, not *the* payload.** The rocket flies on ballast alone. The interface it has to satisfy — 40.0 mm bore × 150 mm, an M3 × 55 retainer at nose z 15, a ~50 g mass ceiling, an optional camera port — is [`js-rocket/docs/payload-bay.md`](https://github.com/jwilleke/js-rocket/blob/main/docs/payload-bay.md), and that is the only page in that repo this project depends on.

Separate from the rocket repo on purpose: `js-rocket` is geometry and documentation with no code, no package manager and no dependencies, and its `CLAUDE.md` says so explicitly. Copper, firmware and **the design record — every decision and why, in [docs/design.md](docs/design.md)** — live here instead.

**Why it is built this way is in [docs/design.md](docs/design.md).** **Every part this project needs is in [docs/BOM.md](docs/BOM.md)** — what each part is, which board it serves, mass, size, and what was rejected. **What was actually bought is in [docs/shopping-list.md](docs/shopping-list.md)** — SKUs, orders, costs, arrival status. The printed sled that carries these boards, and the [PayloadAdapter](https://github.com/jwilleke/js-rocket/blob/main/docs/3d-printed-parts/payload-adapter.md) it loads through, are rocket parts and stay in [js-rocket](https://github.com/jwilleke/js-rocket).

**Status: 2a complete, 2b partial.** Outline, stackup, mounting holes, ground and power planes, both XIAO header positions and their net assignments — **DRC clean at 0 violations, 0 unconnected**. Still missing: footprints for the sensors, buzzer and battery connector, and all signal routing. The GPS needs no footprint — it rides the XIAO stack.

> **Do not order it.** It quotes cleanly, which is a toolchain check and nothing more. Everything except the two XIAOs is still absent.

## The frozen interface

These numbers are what the rocket's sled generator derives its rail bosses from. **Changing them means reprinting the sled**, so they freeze here first.

| | Value |
|---|---|
| Board | **24.000 × 95.000 mm** |
| Thickness | **1.0 mm**, 4 copper layers |
| Corner radius | 2.0 mm |
| Mounting holes | **4 × Ø2.200 mm** (M2 clearance) at **(3, 3), (21, 3), (3, 92), (21, 92)** |
| Mounting pattern | 18.0 mm × 89.0 mm centres |
| Mass | **4.3 g** (FR4 at 1.9 g/cm³) |
| XIAO B centre | y = 18.0 mm — the Sense, so the camera lands at nose z 30..45 |
| XIAO A centre | y = 46.0 mm |

Verified from the exported Gerber and drill files, not from the generator's own console output.

**Why 1.0 mm and not 0.8.** The card is the sled's structural span over ~70 mm. It carries no cutouts to weaken it — see below — but 0.8 mm FR4 flexes over that length.

**Why 24 mm wide.** The card sits on a *diameter* of the 40.0 mm payload bore, so its width is not chord-limited and could go to ~38 mm. 24 mm is set by the parts, not the bore.

**Why it grew from 70 to 95 mm.** The 70 mm figure assumed the two XIAOs could overlap in plan view, one per face. They cannot — these are *through-hole* headers, so the holes pass through the board, and XIAO A uses D6/D7 for the GPS UART while XIAO B uses D4/D5 for I2C. Different nets, same holes. They must sit end to end:

```text
top face     XIAO A 21 + GPS in the stack, not end to end     = 21 mm
bottom face  XIAO B 21 + LSM6DSO32 25.5 + BMP388 25.5 + buzzer = 84 mm
```

At 24 mm wide against 17.8 mm sensors, no two sit side by side. 95 mm gives the bottom face its 84 mm plus spacing. Costs 1.1 g and lands the sled inside 150 mm with 36 mm to spare.

**The bottom face sets the length.** The top-face line above once read `XIAO A 21 + GPS ~25 = 46 mm`, from a MAX-M10S breakout that has since been rejected — see [The GPS is an L76K](#the-gps-is-an-l76k-and-it-is-not-a-carrier-part). The top face now needs only 21 mm, **the 84 mm bottom face is unchanged, and so is every number in the frozen interface above**. Nothing reprints.

## The XIAO stack, and why there is no cutout

An earlier plan had each XIAO sitting flat on its own card, with a window cut to clear the expansion board underneath. KiCad's Seeed XIAO footprint kills that:

```text
14 pads, 3 x 2 mm
x = +/-8.5 mm       rows 17.0 mm apart, pad inner edges at +/-7.0
y = -7.62..+7.62    7 per row, 2.54 mm pitch
board 17.5 x 21 mm
```

The expansion board — Sense camera or Wio-SX1262 — is the **same XIAO outline, ±8.75 mm**. The part needing clearance is **wider than the pads are apart**, so any window big enough to pass it removes the copper the pads solder to. No cutout satisfies both.

So the XIAOs mount on **2×7 stacking headers, ~14 mm standoff**, expansion board hanging in the gap, **15 mm** total above the card. Two of them on opposite faces:

```text
at the XIAO's edge (x = +/-8.75 from centre):
  available depth = sqrt(19.7^2 - 8.75^2) = 17.6 mm each side

two stacks + card = 15 + 1.0 + 15 = 31.0 mm
available         = 2 x 17.6      = 35.2 mm     fits, ~2 mm margin
```

## Connections

There is **no schematic file**. Nets are assigned to pads directly in the generator, which is more robust than hand-authoring schematic s-expressions for ~9 nets and keeps one generator as the single source of truth. The cost is no ERC and no drawn diagram — so this table *is* the wiring diagram. **Keep it in step with `gen_carrier.py`.**

| Net | XIAO A (plain, beacon) | XIAO B (Sense, recorder) | Also reaches |
|---|---|---|---|
| `GND` | pin 13 | pin 13 | In1 plane, every module, JST − |
| `+3V3` | pin 12 | pin 12 | In2 plane, every module |
| `GPS_TX` | **D6** (pin 7, GPIO43) | — | L76K RX — **met in the XIAO stack, not on this board** |
| `GPS_RX` | **D7** (pin 8, GPIO44) | — | L76K TX — **met in the XIAO stack, not on this board** |
| `SDA` | — | **D4** (pin 5, GPIO5) | LSM6DSO32, BMP388 |
| `SCL` | — | **D5** (pin 6, GPIO6) | LSM6DSO32, BMP388 |
| `BUZZER` | — | **D0** (pin 1, GPIO1) | buzzer + |
| `VBAT` | — | — | JST +, pigtails to both XIAO BAT pads — **footprint not yet placed** |

### The pin map, and an error worth not repeating

The KiCad footprint numbers its pads 1–14 with no signal names, DIP-style — 1 at top-left, down to 7 at bottom-left, 8 at bottom-right, up to 14 at top-right. Seeed's pinout gives the meaning:

```text
pin  1  2  3  4  5  6  7   8  9  10  11   12   13   14
sig  D0 D1 D2 D3 D4 D5 D6  D7 D8 D9  D10  3V3  GND  5V
```

An earlier revision of the generator put GPS on pins 6/7 and I2C on 4/5 — which are **D5/D6 and D3/D4, every one off by one**. Caught by reading the mapping back out of the saved board rather than trusting the script's own output. The generator now names pins (`XIAO_PIN["D6"]`) so the numbers never appear by hand.

**Each 1×7 header numbers its own pads 1–7**, so the right-hand row maps as `xiao_pin = 15 − pad`. A readback that ignores this reports nonsense — it did once already.

## The GPS is an L76K, and it is not a carrier part

Earlier revisions of this file named a **MAX-M10S** in the net table, the deferred-footprint list and the RF section. That part was rejected on 2026-08-06: **44.2 × 30.5 mm — wider than this 24 mm board — and ~$60**. The chosen part is Seeed's **L76K GNSS for XIAO (109100021)** — 18 × 21 mm, $11.99, active antenna included, UART on **D6/D7**, which is already what the netlist assigns.

**It plugs onto the XIAO's own 14 pads rather than presenting a header to this board.** So:

- **No GPS footprint is placed here, and none is planned.** `GPS_TX` / `GPS_RX` stay in the netlist — they are the same node the L76K meets in the stack — so the DRC's 0-unconnected result is unaffected.
- **The top-face length term drops from ~46 mm to 21 mm.** The board stays 95 mm because the bottom face drives it.
- **The risk moves from layout to stack height.** Whether the L76K clears the Wio-SX1262 on the B2B is still open, and the XIAO stack's 15 mm was computed against ~2 mm of bore margin. **If it will not ride the stack it returns here as a footprint**, needing ~21 mm on the top face — which this board has, but which the breadboard stage must settle rather than assume.

The same staleness reached the barometer: **BMP390 → BMP388**, settled on 2026-08-06 when the 390 went out of stock at an 8–12 week lead. Same BMP3xx driver, same 25.5 × 17.8 mm STEMMA QT outline the 95 mm was computed from, address 0x77, and its pinout is now **confirmed off the physical part** — see the rocket repo's `electronics-plan.md`.

## Deliberately not placed yet

Footprints for the **LSM6DSO32, BMP388, buzzer and battery JST**.

Their header pin *order* varies between vendors, and a wrong order is a scrapped board rather than a re-solder. These land after the breadboard stage confirms the parts actually in hand. XIAO geometry was safe to commit now only because it comes from KiCad's own Seeed footprint, which cites Seeed's package drawing.

The BMP388 is the one exception on pin order — **confirmed from the part in hand** (`VIN 3Vo GND SCL SDO SDA CS INT`, two Ø2.35 mm mounting holes at 20.58 mm centres, **M2 not M2.5**). It still waits on the breadboard because mounting orientation is shared with the LSM6DSO32, which has not arrived.

## Battery — read before assembling

**BAT+/BAT− are underside pads on the XIAO**, not brought out to the castellated edge, so the cell cannot reach a XIAO through the headers. The cell lands on a JST-PH on this card and reaches each XIAO by a short **soldered pigtail**.

- **Solder the pigtails before fitting the expansion board.** Seeed's documentation implies the pads are inaccessible once it is on.
- **On battery power there is no voltage on the 5V pin** — nothing can be fed from a XIAO's 5V rail.
- Both XIAO chargers sit in parallel on one cell. **Charge through one USB port at a time.**
- Mark the pigtail polarity on the silkscreen. Reversing a LiPo into a XIAO destroys it.

## No RF on this board

The L76K and the Wio-SX1262 each carry their own U.FL connector, so both antennas leave from the modules and **no RF ever crosses the carrier**. It is a purely digital and power board of roughly 9 nets, which is what makes it tractable to generate and verify headlessly.

## Building

Requires KiCad 10. The generator uses KiCad's bundled Python so `pcbnew` matches the CLI exactly.

```bash
KPY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3
CLI=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli

$KPY hardware/scripts/gen_carrier.py
$CLI pcb drc  --format json -o /tmp/drc.json hardware/carrier/carrier.kicad_pcb
$CLI pcb export gerbers -o fab/gerbers/ hardware/carrier/carrier.kicad_pcb
$CLI pcb export drill   -o fab/gerbers/ hardware/carrier/carrier.kicad_pcb
```

**The board is generated, not hand-edited.** `.kicad_pcb` format shifts between KiCad releases; building it through `pcbnew` means the file is written by the same code that reads it. Edit `hardware/scripts/gen_carrier.py` and re-run — do not edit the board file directly, or the next run overwrites you.

`gen_outline.py` is the superseded 2a-only version, kept for reference.

DRC must report **0 violations** before anything is ordered.

## Remaining stages

| Stage | State |
|---|---|
| 2a — outline, holes, stackup | **done**, DRC clean |
| 2b — nets + XIAO footprints | **partial** — XIAOs placed and netted; sensors, buzzer, JST deferred. GPS needs no footprint |
| 2b — GND/+3V3 planes | **done**, In1 and In2 filled |
| 2c — placement of remaining parts | blocked on confirming real module pinouts |
| 2d — signal routing | not started |
| 2e — Gerber + drill for fab | chain proven; needs a finished board |

**Do not order copper before breadboarding.** A layout error costs ~$33 and two weeks; a wiring error costs minutes. The deferred footprints above are exactly the parts the breadboard exists to confirm.

Fab target is **OSH Park**. The 24 × 70 mm version quoted **$26.00 for 3 copies** — $9.32/in² — so 24 × 95 mm (3.53 in²) should land near **$33**. Re-upload to confirm; three copies is right, two populated plus a spare.

**OSH Park accepts the `.kicad_pcb` directly** — confirmed by upload, not assumed. It read the layer count and outline unaided, so `fab/gerbers/` is not in the ordering path and exists only as a check that the export chain works.
