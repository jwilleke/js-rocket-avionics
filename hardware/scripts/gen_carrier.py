"""Generate the carrier PCB: outline, mounting holes, XIAO headers and nets.

    /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 \
        hardware/scripts/gen_carrier.py

Supersedes gen_outline.py (stage 2a), which produced outline and holes only.

WHY THE BOARD GREW FROM 24x70 TO 24x95. The 70 mm figure assumed the two XIAOs
could overlap in plan view, one per face. They cannot: these are *through-hole*
stacking headers, so the holes pass through the board, and XIAO A uses D6/D7
for the GPS UART while XIAO B uses D4/D5 for I2C -- different nets on the same
holes. They have to sit end to end. Laying the real parts out:

    top face     XIAO A 21 + GPS in the stack, not end to end    = 21 mm
    bottom face  XIAO B 21 + LSM6DSO32 25.5 + BMP388 25.5 + buzzer = 84 mm

and the board is 24 mm wide against 17.8 mm sensors, so no two sit side by
side. 95 mm gives the bottom face its 84 mm plus spacing.

The top-face line above once read "XIAO A 21 + GPS ~25 = 46 mm", from a
MAX-M10S breakout that was rejected on 2026-08-06 (44.2 x 30.5 mm -- wider
than this board -- and ~$60). The GPS is a Seeed L76K for XIAO (109100021),
which plugs onto the XIAO's own 14 pads and needs no footprint here. The
BOTTOM face is what sets 95 mm, so the board length is unaffected and the
mounting pattern the rocket's sled generator derives from it does not move.

WHY NO SCHEMATIC FILE. Nets are assigned directly to pads here rather than
generated from a .kicad_sch. For ~9 nets that is more robust than authoring
schematic s-expressions by hand, and it keeps one generator as the single
source of truth. The cost is no ERC and no drawn wiring diagram, so the
human-readable version lives in README.md as a connection table -- keep the
two in step.

WHAT IS DELIBERATELY NOT HERE YET. Footprints for the LSM6DSO32, BMP388,
buzzer and battery JST -- but NOT the GPS, which needs none; the L76K rides
the XIAO stack. Their header pin ORDER differs between vendors and a wrong
order is a scrapped board, not a re-solder. Those land after the breadboard
stage confirms the actual parts in hand. XIAO geometry is safe to commit now
because it comes from KiCad's own Seeed footprint, which cites Seeed's package
drawing.

XIAO HEADER GEOMETRY, from RF_Module:MCU_Seeed_ESP32C3:

    14 pads, x = +/-8.5 mm (rows 17.0 mm apart)
    y = -7.62..+7.62, 7 per row at 2.54 mm pitch
    board 17.5 x 21 mm

Pin numbering follows that footprint: 1..7 down the -8.5 mm row, 8..14 back up
the +8.5 mm row, so pin 8 faces pin 7.
"""
import os
import sys

import pcbnew

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(REPO, "hardware", "carrier", "carrier.kicad_pcb")

BOARD_W = 24.0
BOARD_H = 95.0
THICKNESS = 1.0
COPPER_LAYERS = 4
CORNER_R = 2.0
HOLE_INSET = 3.0

XIAO_ROW_DX = 8.5          # header rows at +/-8.5 mm from the XIAO centreline
XIAO_PITCH = 2.54
XIAO_PINS_PER_ROW = 7

# XIAO centres along the board's long axis. B carries the camera and must land
# at carrier-relative 10..25 mm so the OV2640 reaches the Nosecone collar port
# at nose z 30..45; A sits above it.
XIAO_B_Y = 18.0            # Sense: camera, microSD, sensors
XIAO_A_Y = 46.0            # plain: Wio-SX1262 + GPS

MM = pcbnew.FromMM

# Footprint pad number -> XIAO signal name. The KiCad footprint numbers its
# pads 1..14 with no names, DIP-style: 1 at top-left, down to 7 at bottom-left,
# 8 at bottom-right, up to 14 at top-right. Seeed's pinout then gives:
#
#     pin  1  2  3  4  5  6  7   8  9  10  11   12   13   14
#     sig  D0 D1 D2 D3 D4 D5 D6  D7 D8 D9  D10  3V3  GND  5V
#
# Naming the pins rather than hard-coding numbers because getting this wrong is
# a scrapped board: an earlier revision of this file had GPS on pins 6/7 and
# I2C on 4/5, which are D5/D6 and D3/D4 -- every one off by one.
XIAO_PIN = {
    "D0": 1, "D1": 2, "D2": 3, "D3": 4, "D4": 5, "D5": 6, "D6": 7,
    "D7": 8, "D8": 9, "D9": 10, "D10": 11, "3V3": 12, "GND": 13, "5V": 14,
}

# A: D6/D7 = GPIO43/44 = UART to the L76K GNSS, which meets these nets in the
# XIAO stack rather than through a footprint on this board.
# B: D4/D5 = GPIO5/6   = I2C;  D0 = GPIO1 = buzzer
# Pins not listed are left unassigned rather than guessed.
XIAO_A_SIGNALS = {"D6": "GPS_TX", "D7": "GPS_RX", "3V3": "+3V3", "GND": "GND"}
XIAO_B_SIGNALS = {"D0": "BUZZER", "D4": "SDA", "D5": "SCL",
                  "3V3": "+3V3", "GND": "GND"}

XIAO_A_NETS = {XIAO_PIN[k]: v for k, v in XIAO_A_SIGNALS.items()}
XIAO_B_NETS = {XIAO_PIN[k]: v for k, v in XIAO_B_SIGNALS.items()}

FP_LIB = ("/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/"
          "Connector_PinHeader_2.54mm.pretty")
FP_HEADER = "PinHeader_1x07_P2.54mm_Vertical"
MH_LIB = ("/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/"
          "MountingHole.pretty")
MH_NAME = "MountingHole_2.2mm_M2"


def outline(board, w, h, r):
    """Edge.Cuts as four segments plus four corner arcs.

    Radiused on purpose: a sharp corner on a card that slides into printed
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

    seg(r, 0, w - r, 0)
    seg(w, r, w, h - r)
    seg(w - r, h, r, h)
    seg(0, h - r, 0, r)
    arc(r, r, r, 0, 0, r)
    arc(w - r, r, w, r, w - r, 0)
    arc(w - r, h - r, w - r, h, w, h - r)
    arc(r, h - r, 0, h - r, r, h)


def load(lib, name, board):
    fp = pcbnew.FootprintLoad(lib, name)
    if fp is None:
        raise SystemExit("could not load %s from %s" % (name, lib))
    return fp


def add_mounting_holes(board, w, h, inset):
    for i, (x, y) in enumerate([(inset, inset), (w - inset, inset),
                                (inset, h - inset), (w - inset, h - inset)], 1):
        fp = load(MH_LIB, MH_NAME, board)
        fp.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
        fp.SetReference("H%d" % i)
        # Default reference text lands off a board edge 3 mm away and trips
        # silk_edge_clearance. Nothing reads a mounting hole's designator.
        fp.Reference().SetVisible(False)
        fp.Value().SetVisible(False)
        board.Add(fp)


def add_xiao(board, ref, cy, netmap, nets):
    """Two 1x7 vertical headers 17.0 mm apart, matching the XIAO pad rows."""
    placed = []
    for side, dx in (("A", -XIAO_ROW_DX), ("B", +XIAO_ROW_DX)):
        fp = load(FP_LIB, FP_HEADER, board)
        fp.SetPosition(pcbnew.VECTOR2I(MM(BOARD_W / 2.0 + dx), MM(cy)))
        fp.SetReference("%s%s" % (ref, side))
        fp.Value().SetVisible(False)
        if side == "A":
            # One label per XIAO, parked on the centreline between the two
            # header rows -- empty of both copper and board edge, which is
            # what silk_over_copper and silk_edge_clearance object to.
            fp.Reference().SetPosition(
                pcbnew.VECTOR2I(MM(BOARD_W / 2.0), MM(cy)))
        else:
            fp.Reference().SetVisible(False)
        board.Add(fp)
        placed.append((side, fp))

    # Row -8.5 carries XIAO pins 1..7 top-to-bottom; row +8.5 carries 8..14
    # bottom-to-top, so pin 8 sits opposite pin 7.
    for side, fp in placed:
        for i in range(1, XIAO_PINS_PER_ROW + 1):
            pad = fp.FindPadByNumber(str(i))
            if pad is None:
                continue
            offset = (i - (XIAO_PINS_PER_ROW + 1) / 2.0) * XIAO_PITCH
            if side == "A":
                xiao_pin = i
                pad.SetY(MM(cy + offset))
            else:
                xiao_pin = XIAO_PINS_PER_ROW * 2 + 1 - i
                pad.SetY(MM(cy - offset))
            name = netmap.get(xiao_pin)
            if name:
                pad.SetNet(nets[name])


def add_plane(board, layer, net, inset=0.5):
    """Flood an inner layer with one net.

    This is what the 4-layer stackup is for: GND on In1 and +3V3 on In2 mean
    the two XIAOs share power and ground without a single routed trace, and
    every signal on the outer layers gets a solid return path directly beneath
    it. Inset from the board edge so copper is not exposed at the cut.
    """
    zone = pcbnew.ZONE(board)
    zone.SetLayer(layer)
    zone.SetNet(net)
    zone.SetIsFilled(True)
    pts = pcbnew.VECTOR_VECTOR2I()
    for x, y in ((inset, inset), (BOARD_W - inset, inset),
                 (BOARD_W - inset, BOARD_H - inset), (inset, BOARD_H - inset)):
        pts.append(pcbnew.VECTOR2I(MM(x), MM(y)))
    zone.AddPolygon(pts)
    board.Add(zone)
    return zone


def main():
    board = pcbnew.CreateEmptyBoard()
    board.SetCopperLayerCount(COPPER_LAYERS)
    board.GetDesignSettings().SetBoardThickness(MM(THICKNESS))

    nets = {}
    for name in ("GND", "+3V3", "VBAT", "GPS_TX", "GPS_RX", "SDA", "SCL",
                 "BUZZER"):
        n = pcbnew.NETINFO_ITEM(board, name)
        board.Add(n)
        nets[name] = n

    outline(board, BOARD_W, BOARD_H, CORNER_R)
    add_mounting_holes(board, BOARD_W, BOARD_H, HOLE_INSET)
    add_xiao(board, "J_XIAO_B", XIAO_B_Y, XIAO_B_NETS, nets)
    add_xiao(board, "J_XIAO_A", XIAO_A_Y, XIAO_A_NETS, nets)

    add_plane(board, pcbnew.In1_Cu, nets["GND"])
    add_plane(board, pcbnew.In2_Cu, nets["+3V3"])
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pcbnew.SaveBoard(OUT, board)

    bbox = board.GetBoardEdgesBoundingBox()
    print("wrote    %s" % OUT)
    print("outline  %.2f x %.2f mm"
          % (pcbnew.ToMM(bbox.GetWidth()), pcbnew.ToMM(bbox.GetHeight())))
    print("layers   %d copper, %.2f mm"
          % (board.GetCopperLayerCount(),
             pcbnew.ToMM(board.GetDesignSettings().GetBoardThickness())))
    print("parts    %d footprints" % len(board.GetFootprints()))
    print("nets     %d declared" % len(nets))
    assigned = sum(1 for fp in board.GetFootprints() for p in fp.Pads()
                   if p.GetNetname())
    print("pads     %d net-assigned" % assigned)
    print("planes   %d filled" % len(board.Zones()))


if __name__ == "__main__":
    sys.exit(main())
