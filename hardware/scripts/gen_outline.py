"""Generate the carrier PCB outline, stackup and mounting holes.

    /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 \
        hardware/scripts/gen_outline.py

This is stage 2a of the plan in js-rocket/docs/planing/electronics-plan.md: the
mechanical envelope only. It is deliberately separate from placement and
routing because **the js-rocket sled generator derives its rail bosses from
these numbers**, so the outline has to freeze before the printed part can be
designed. Nothing here depends on the schematic.

WHY PROGRAMMATIC AND NOT HAND-WRITTEN S-EXPRESSIONS. The .kicad_pcb format
moves between KiCad releases. Building through `pcbnew` means the file is
written by the same code KiCad reads it with, so it cannot drift, and
`kicad-cli pcb drc` can check the result headlessly.

GEOMETRY, and where each number comes from:

  board            24.0 x 70.0 mm, 1.0 mm FR4, 4 layers
  centre plane     the card sits on a diameter of the 40.0 mm payload bore,
                   so its width is not chord-limited -- 24 mm is chosen to
                   suit the parts, not the bore, and could go to ~38 mm
  thickness        1.0 mm, not 0.8 -- this card is the sled's structural
                   span over ~70 mm and there are no cutouts left to weaken
                   (see "Why the twin-PCB idea died")
  mounting holes   4 x M2 clearance (2.2 mm), 3.0 mm inset from each corner
  corner radius    2.0 mm, so the card cannot dig into the printed rails

XIAO CLEARANCE. The XIAO mounts on ~14 mm stacking headers with its expansion
board hanging in the gap; the stack is 15 mm tall above this card. Two of them
on opposite faces need 15 + 1.0 + 15 = 31.0 mm, against 2 * sqrt(19.7^2 -
8.75^2) = 35.2 mm available at the XIAO's +/-8.75 mm edge inside the 39.4 mm
sled envelope. That check is what sets the 1.0 mm thickness as affordable.
"""
import os
import sys

import pcbnew

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(REPO, "hardware", "carrier", "carrier.kicad_pcb")

BOARD_W = 24.0
BOARD_H = 70.0
THICKNESS = 1.0
COPPER_LAYERS = 4

CORNER_R = 2.0
HOLE_DIA = 2.2          # M2 clearance
HOLE_INSET = 3.0        # from each edge to hole centre

MM = pcbnew.FromMM


def rounded_rect_outline(board, w, h, r):
    """Edge.Cuts as four segments plus four corner arcs.

    Drawn as an explicit path rather than SHAPE_T_RECT so the corners are
    genuinely radiused -- a sharp corner on a card that slides into printed
    rails chews the rails on every insertion.
    """
    def seg(x1, y1, x2, y2):
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(pcbnew.VECTOR2I(MM(x1), MM(y1)))
        s.SetEnd(pcbnew.VECTOR2I(MM(x2), MM(y2)))
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(MM(0.1))
        board.Add(s)

    def arc(cx, cy, sx, sy, ex, ey):
        a = pcbnew.PCB_SHAPE(board)
        a.SetShape(pcbnew.SHAPE_T_ARC)
        a.SetCenter(pcbnew.VECTOR2I(MM(cx), MM(cy)))
        a.SetStart(pcbnew.VECTOR2I(MM(sx), MM(sy)))
        a.SetEnd(pcbnew.VECTOR2I(MM(ex), MM(ey)))
        a.SetLayer(pcbnew.Edge_Cuts)
        a.SetWidth(MM(0.1))
        board.Add(a)

    # straight runs, inset by the corner radius at each end
    seg(r, 0, w - r, 0)              # top
    seg(w, r, w, h - r)              # right
    seg(w - r, h, r, h)              # bottom
    seg(0, h - r, 0, r)              # left

    # corners: KiCad arcs sweep counter-clockwise from start to end
    arc(r, r, r, 0, 0, r)                        # top-left
    arc(w - r, r, w, r, w - r, 0)                # top-right
    arc(w - r, h - r, w - r, h, w, h - r)        # bottom-right
    arc(r, h - r, 0, h - r, r, h)                # bottom-left


def add_mounting_holes(board, w, h, inset, dia):
    """Plain non-plated holes, placed as footprints so DRC sees them."""
    lib = ("/Applications/KiCad/KiCad.app/Contents/SharedSupport/"
           "footprints/MountingHole.pretty")
    name = "MountingHole_2.2mm_M2"
    positions = [
        (inset, inset),
        (w - inset, inset),
        (inset, h - inset),
        (w - inset, h - inset),
    ]
    for i, (x, y) in enumerate(positions, start=1):
        fp = pcbnew.FootprintLoad(lib, name)
        if fp is None:
            raise SystemExit("could not load %s from %s" % (name, lib))
        fp.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
        fp.SetReference("H%d" % i)
        # The default reference text sits above the pad, which for a hole
        # 3 mm from the edge lands off the board and trips
        # silk_edge_clearance. Nothing reads a mounting hole's designator on
        # the silkscreen, so hide it rather than shuffle it inboard.
        fp.Reference().SetVisible(False)
        fp.Value().SetVisible(False)
        board.Add(fp)


def main():
    board = pcbnew.CreateEmptyBoard()
    board.SetCopperLayerCount(COPPER_LAYERS)

    stackup_settings = board.GetDesignSettings()
    stackup_settings.SetBoardThickness(MM(THICKNESS))

    rounded_rect_outline(board, BOARD_W, BOARD_H, CORNER_R)
    add_mounting_holes(board, BOARD_W, BOARD_H, HOLE_INSET, HOLE_DIA)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pcbnew.SaveBoard(OUT, board)

    bbox = board.GetBoardEdgesBoundingBox()
    print("wrote %s" % OUT)
    print("outline  %.2f x %.2f mm"
          % (pcbnew.ToMM(bbox.GetWidth()), pcbnew.ToMM(bbox.GetHeight())))
    print("layers   %d copper, %.2f mm thick"
          % (board.GetCopperLayerCount(),
             pcbnew.ToMM(board.GetDesignSettings().GetBoardThickness())))
    print("holes    %d" % len(board.GetFootprints()))


if __name__ == "__main__":
    sys.exit(main())
