"""Fit mock of the carrier PCB: the generated board's body, holes opened up for printing.

    /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 \
        hardware/scripts/gen_carrier_fitmock.py

Reads the board gen_carrier.py wrote, so the mock can never drift from it. It
changes a COPY, never the board:

  - every drilled hole opened by HOLE_GROW, because a printed hole comes out
    undersize and the real header pins, pigtail wires and M3 screws must pass
  - an arrow cut through the board, pointing forward (nose tip), at the
    forward end -- it says which end is forward. Printed low side down, the
    top face is the tall side
  - four small marker holes at the board's edges where the battery's aft and
    forward ends fall on the low side (it is not a footprint, so nothing else
    on the board shows it)

then exports the board body alone as STL with kicad-cli, and writes its holes,
the arrow and the battery markers to a sidecar that gen_carrier_template.py
draws the paper template from. Print it flat, low side on the bed: KiCad's STL
has the low side (B.Cu) at z 0.

NO LABELS (operator, 2026-09-15). Raised or engraved silkscreen came out of the
slicer as nothing -- ~0.15 mm strokes against a 0.42 mm line -- so the mock is
bare, and the paper template says what goes where.
"""
import json
import os
import re
import struct
import subprocess
import sys

import pcbnew

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BOARD = os.path.join(REPO, "hardware", "PCB-carrier", "PCB-carrier.kicad_pcb")
OUT_DIR = os.path.join(REPO, "hardware", "PCB-carrier", "fit-mock")
TMP = os.path.join(OUT_DIR, "PCB-carrier-fit-mock.kicad_pcb")
STL = os.path.join(OUT_DIR, "PCB-carrier-fit-mock.stl")
SIDECAR = os.path.join(OUT_DIR, "PCB-carrier-fit-mock-holes.json")    # for gen_carrier_template.py
KICAD_CLI = "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"

HOLE_GROW = 0.30           # mm on diameter: 1.0 header drill -> 1.3 printed
THICKNESS = 1.6            # the real board, OSH Park 4-layer. KiCad exports its core alone;
                           # scaled in z so the mock stands the headers at their true height
MARK_R = 0.75              # the battery marker holes
MARK_X = (1.2, 22.8)       # inside both long edges
# arrow: tip forward (+y)
ARROW = [(8.5, 114.4), (11.5, 110.4), (9.7, 110.4), (9.7, 107.6),
         (7.3, 107.6), (7.3, 110.4), (5.5, 110.4)]   # the forward tip: clear on both faces,
                                                     # between the BMP388 and the forward standoff

MM = pcbnew.FromMM
HOLES = []


def edge_poly(board, pts):
    for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]):
        seg = pcbnew.PCB_SHAPE(board)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetLayer(pcbnew.Edge_Cuts)
        seg.SetWidth(MM(0.05))
        seg.SetStart(pcbnew.VECTOR2I(MM(x1), MM(y1)))
        seg.SetEnd(pcbnew.VECTOR2I(MM(x2), MM(y2)))
        board.Add(seg)


def edge_circle(board, x, y, r):
    c = pcbnew.PCB_SHAPE(board)
    c.SetShape(pcbnew.SHAPE_T_CIRCLE)
    c.SetLayer(pcbnew.Edge_Cuts)
    c.SetWidth(MM(0.05))
    c.SetStart(pcbnew.VECTOR2I(MM(x), MM(y)))
    c.SetEnd(pcbnew.VECTOR2I(MM(x + r), MM(y)))
    board.Add(c)


def to_binary_scaled(path):
    """kicad-cli writes ASCII STL; rewrite it binary, z scaled to THICKNESS."""
    txt = open(path, "rb").read()
    verts = [tuple(map(float, m.split())) for m in
             re.findall(rb"vertex\s+(\S+\s+\S+\s+\S+)", txt)]
    zmax = max(v[2] for v in verts)
    k = THICKNESS / zmax
    tris = [verts[i:i + 3] for i in range(0, len(verts), 3)]
    with open(path, "wb") as fh:
        fh.write(b"PCB-carrier fit mock -- gen_carrier_fitmock.py".ljust(80, b"\0"))
        fh.write(struct.pack("<I", len(tris)))
        for t in tris:
            fh.write(struct.pack("<3f", 0.0, 0.0, 0.0))
            for x, y, z in t:
                fh.write(struct.pack("<3f", x, y, z * k))
            fh.write(b"\0\0")
    print("scaled   %.3f -> %.3f mm thick, %d triangles, binary" % (zmax, THICKNESS, len(tris)))


def layout():
    """The layout JSON gen_carrier.py writes -- KiCad 10's binding will not return the
    board's box, and the battery is not on the board at all."""
    return json.load(open(os.path.join(REPO, "hardware", "PCB-carrier", "PCB-carrier-layout.json")))


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    lay = layout()
    BATTERY_Y = (lay["battery"]["y0"], lay["battery"]["y1"])   # the battery's two ends
    board = pcbnew.LoadBoard(BOARD)
    grown = 0
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            d = pad.GetDrillSize()
            if d.x > 0:
                pad.SetDrillSize(pcbnew.VECTOR2I(d.x + MM(HOLE_GROW), d.y + MM(HOLE_GROW)))
                grown += 1
                HOLES.append({"x": pcbnew.ToMM(pad.GetPosition().x), "y": pcbnew.ToMM(pad.GetPosition().y),
                              "r": (pcbnew.ToMM(d.x) + HOLE_GROW) / 2})
    for z in list(board.Zones()):
        board.Remove(z)
    edge_poly(board, ARROW)
    for y in BATTERY_Y:
        for x in MARK_X:
            edge_circle(board, x, y, MARK_R)
    json.dump({"thickness": THICKNESS, "board": [0.0, 0.0, 24.0, lay["board"]["h"]],
               "holes": HOLES, "arrow": ARROW, "marks": [[x, y, MARK_R] for y in BATTERY_Y for x in MARK_X]},
              open(SIDECAR, "w"), indent=1)
    board.Save(TMP)
    print("holes    %d opened by %.2f mm on diameter" % (grown, HOLE_GROW))
    subprocess.run([KICAD_CLI, "pcb", "export", "stl", "--board-only", "--force",
                    "--output", STL, TMP], check=True, capture_output=True)
    to_binary_scaled(STL)
    for ext in (".kicad_pcb", ".kicad_prl", ".kicad_pro"):
        p = TMP[:-len(".kicad_pcb")] + ext
        if os.path.exists(p):
            os.remove(p)
    print("wrote    %s" % STL)


if __name__ == "__main__":
    sys.exit(main())
