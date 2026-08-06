# js-rocket-avionics

Carrier PCB and flight firmware for the [js-rocket](https://github.com/jwilleke/js-rocket) electronics sled.

Separate from the rocket repo on purpose: `js-rocket` is geometry and documentation with no code, no package manager and no dependencies, and its `CLAUDE.md` says so explicitly. Copper and firmware live here instead. The design record — every decision and why — stays in [`js-rocket/docs/planing/electronics-plan.md`](https://github.com/jwilleke/js-rocket/blob/main/docs/planing/electronics-plan.md).

**Status: stage 2a complete.** Board outline, stackup and mounting holes exist and pass DRC. There is **no schematic, no placement and no routing yet**, so this board is **empty copper** — outline and four holes, nothing else.

> **Do not order it.** Uploading it to OSH Park quotes cleanly (**$26.00 for 3**, 4 layers, 0.94 × 2.76 in detected unaided), which is a useful toolchain check and nothing more. You would receive three blank cards.

## The frozen interface

These numbers are what the rocket's sled generator derives its rail bosses from. **Changing them means reprinting the sled**, so they freeze here first.

| | Value |
|---|---|
| Board | **24.000 × 70.000 mm** |
| Thickness | **1.0 mm**, 4 copper layers |
| Corner radius | 2.0 mm |
| Mounting holes | **4 × Ø2.200 mm** (M2 clearance) at **(3, 3), (21, 3), (3, 67), (21, 67)** |
| Mounting pattern | 18.0 mm × 64.0 mm centres |

Verified from the exported Gerber and drill files, not from the generator's own console output.

**Why 1.0 mm and not 0.8.** The card is the sled's structural span over ~70 mm. It carries no cutouts to weaken it — see below — but 0.8 mm FR4 flexes over that length.

**Why 24 mm wide.** The card sits on a *diameter* of the 40.0 mm payload bore, so its width is not chord-limited and could go to ~38 mm. 24 mm is set by the parts, not the bore.

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

## Battery — read before assembling

**BAT+/BAT− are underside pads on the XIAO**, not brought out to the castellated edge, so the cell cannot reach a XIAO through the headers. The cell lands on a JST-PH on this card and reaches each XIAO by a short **soldered pigtail**.

- **Solder the pigtails before fitting the expansion board.** Seeed's documentation implies the pads are inaccessible once it is on.
- **On battery power there is no voltage on the 5V pin** — nothing can be fed from a XIAO's 5V rail.
- Both XIAO chargers sit in parallel on one cell. **Charge through one USB port at a time.**
- Mark the pigtail polarity on the silkscreen. Reversing a LiPo into a XIAO destroys it.

## No RF on this board

The MAX-M10S breakout and the Wio-SX1262 each carry their own U.FL connector, so both antennas leave from the modules and **no RF ever crosses the carrier**. It is a purely digital and power board of roughly 9 nets, which is what makes it tractable to generate and verify headlessly.

## Building

Requires KiCad 10. The generator uses KiCad's bundled Python so `pcbnew` matches the CLI exactly.

```bash
KPY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3
CLI=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli

$KPY hardware/scripts/gen_outline.py
$CLI pcb drc  --format json -o /tmp/drc.json hardware/carrier/carrier.kicad_pcb
$CLI pcb export gerbers -o fab/gerbers/ hardware/carrier/carrier.kicad_pcb
$CLI pcb export drill   -o fab/gerbers/ hardware/carrier/carrier.kicad_pcb
```

**The board is generated, not hand-edited.** `.kicad_pcb` format shifts between KiCad releases; building it through `pcbnew` means the file is written by the same code that reads it. Edit `hardware/scripts/gen_outline.py` and re-run — do not edit the board file directly, or the next run overwrites you.

DRC must report **0 violations** before anything is ordered.

## Remaining stages

| Stage | State |
|---|---|
| 2a — outline, holes, stackup | **done**, DRC clean |
| 2b — schematic, footprints, netlist | not started |
| 2c — placement | not started |
| 2d — routing | not started |
| 2e — Gerber + drill for fab | chain proven; needs a real board first |

**Do not order copper before breadboarding both populations.** A layout error costs $26 and two weeks; a wiring error costs minutes.

Fab target is **OSH Park** — **quoted $26.00 for 3 copies**, 4 layers, ENIG, free US shipping, no customs. Three is exactly right: two populated plus a spare.

**OSH Park accepts the `.kicad_pcb` directly** — confirmed by upload, not assumed. It read the layer count and outline unaided, so `fab/gerbers/` is not in the ordering path and exists only as a check that the export chain works.
