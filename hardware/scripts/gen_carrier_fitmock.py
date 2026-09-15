"""Fit mock of the carrier PCB: the generated board's body, holes opened up for printing.

    /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 \
        hardware/scripts/gen_carrier_fitmock.py

Reads the board gen_carrier.py wrote, so the mock can never drift from it. It
changes a COPY, never the board:

  - every drilled hole opened by HOLE_GROW, because a printed hole comes out
    undersize and the real header pins, pigtail wires and M3 screws must pass
  - an arrow cut through the board, pointing forward (nose tip), at the
    forward end -- it says which end is forward. The labels say which face is
    which: printed low side down, the top face is the tall side
  - four small marker holes at the board's edges where the battery's aft and
    forward ends fall on the low side (it is not a footprint, so nothing else
    on the board shows it)

then exports the board body alone as STL with kicad-cli, and writes the
board's silkscreen texts and holes to a sidecar for the second step,
gen_carrier_fitmock_labels.py (Blender), which puts the labels on. Print it
flat, low side on the bed: KiCad's STL has the low side (B.Cu) at z 0.
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
SIDECAR = os.path.join(OUT_DIR, "PCB-carrier-fit-mock-labels.json")   # for gen_carrier_fitmock_labels.py
KICAD_CLI = "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"

HOLE_GROW = 0.30           # mm on diameter: 1.0 header drill -> 1.3 printed
BATTERY_Y = (45.1, 81.1)   # layout y of the battery's ends -- PCB-carrier-design.md, layout B2
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


def BOARD_H_MM(board):
    """From the layout JSON gen_carrier.py writes -- KiCad 10's binding will not return the box."""
    lay = json.load(open(os.path.join(REPO, "hardware", "PCB-carrier", "PCB-carrier-layout.json")))
    return lay["board"]["h"]


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
                HOLES.append({"x": pcbnew.ToMM(pad.GetPosition().x), "y": pcbnew.ToMM(pad.GetPosition().y),
                              "r": (pcbnew.ToMM(d.x) + HOLE_GROW) / 2})
    for z in list(board.Zones()):
        board.Remove(z)
    edge_poly(board, ARROW)
    for y in BATTERY_Y:
        for x in MARK_X:
            edge_circle(board, x, y, MARK_R)
    # labels and holes for the Blender step, read off the board rather than retyped
    labels, holes = [], HOLES
    # KiCad 10's binding will not iterate the board's drawings, so read the texts off the file
    for m in re.finditer(r'\(gr_text "([^"]*)"\s*\(at ([-\d.]+) ([-\d.]+)[^)]*\)\s*\(layer "([FB])\.SilkS"\)(.*?)\n\t\)',
                         open(BOARD).read(), re.S):
        size = re.search(r"\(size ([\d.]+) ([\d.]+)\)", m.group(5))
        labels.append({"text": m.group(1), "x": float(m.group(2)), "y": float(m.group(3)),
                       "size": float(size.group(1)) if size else 1.0, "back": m.group(4) == "B"})
    json.dump({"thickness": THICKNESS, "board": [0.0, 0.0, 24.0, BOARD_H_MM(board)], "labels": labels,
               "holes": holes, "arrow": ARROW, "marks": [[x, y, MARK_R] for y in BATTERY_Y for x in MARK_X]},
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
