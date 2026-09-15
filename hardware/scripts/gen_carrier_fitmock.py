"""PLA fit mock of the carrier PCB: the generated board's body, holes opened up for printing.

    /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 \
        hardware/scripts/gen_carrier_fitmock.py

Reads the board gen_carrier.py wrote, so the mock can never drift from it. It
changes a COPY, never the board:

  - every drilled hole opened by HOLE_GROW, because a printed hole comes out
    undersize and the real header pins, pigtail wires and M3 screws must pass
  - an arrow cut through the board, pointing forward (nose tip), on the tall
    side's clear stretch -- it says which end is forward. It cannot say which
    face is which (a hole looks the same from both sides): printed low side
    down, the top face is the tall side
  - four small marker holes at the board's edges where the battery's aft and
    forward ends fall on the low side (it is not a footprint, so nothing else
    on the board shows it)

then exports the board body alone as STL with kicad-cli. Print it flat, low
side on the bed: KiCad's STL has the low side (B.Cu) at z 0.
"""
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
KICAD_CLI = "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"

HOLE_GROW = 0.30           # mm on diameter: 1.0 header drill -> 1.3 printed
BATTERY_Y = (45.1, 81.1)   # layout y of the battery's ends -- PCB-carrier-design.md, layout B2
THICKNESS = 1.0            # the real board. KiCad exports its core alone, ~0.91 mm;
                           # scaled in z so the mock stands the headers at their true height
MARK_R = 0.75              # the battery marker holes
MARK_X = (1.2, 22.8)       # inside both long edges
# arrow: tip forward (+y), centred on the board, over the tall side's clear stretch
ARROW = [(12.0, 106.0), (15.5, 100.0), (13.2, 100.0), (13.2, 92.0),
         (10.8, 92.0), (10.8, 100.0), (8.5, 100.0)]

MM = pcbnew.FromMM


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


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    board = pcbnew.LoadBoard(BOARD)
    grown = 0
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            d = pad.GetDrillSize()
            if d.x > 0:
                pad.SetDrillSize(pcbnew.VECTOR2I(d.x + MM(HOLE_GROW), d.y + MM(HOLE_GROW)))
                grown += 1
    for z in list(board.Zones()):
        board.Remove(z)
    edge_poly(board, ARROW)
    for y in BATTERY_Y:
        for x in MARK_X:
            edge_circle(board, x, y, MARK_R)
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
