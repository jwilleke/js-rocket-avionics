"""Generate the carrier PCB: one two-sided board.

    /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 \
        hardware/scripts/gen_carrier.py

Supersedes gen_outline.py (stage 2a), which produced outline and holes only.

ONE BOARD, TWO SIDES (operator, 2026-09-11; hardware/PCB-carrier/PCB-carrier-design.md).
The board sits on the PayloadSled's centre line and hangs off the web on two
M3 standoffs, so it can come off the sled as one unit:

    tall side  F.Cu, faces 270 deg (the camera port)
               XIAO-ESP32S3-cam aft, under the camera; L76K-GNSS; XIAO-ESP32S3-lora
               forward; the battery JST at the forward end
    low side   B.Cu, faces 90 deg (the web)
               LSM6DSO32 and BMP388, rows running lengthwise; two SMT M3 standoffs

The web is offset toward 90 deg, clear of the low side, and two M3 plastic
screws come in from its far face into the standoffs (js-rocket#99). Nothing
fastens through to the tall side, so no screw head ever sits under a module.

WHY THE SENSORS RUN LENGTHWISE. Their pin rows sit 2.14 mm inboard of the
tall-side modules' rows (x 3.5 / 20.5), parallel, so no hole meets another.
Turned 90 deg, their rows would cross the modules' rows. They stand ~1 mm proud
of the board on their pins, header plastic up against the sensor, so the
plastic clears the tall-side modules' solder joints on the low face.

WHY NO SCHEMATIC FILE. Nets are assigned directly to pads here rather than
generated from a .kicad_sch. For ~10 nets that is more robust than authoring
schematic s-expressions by hand, and it keeps one generator as the single
source of truth. The cost is no ERC and no drawn wiring diagram, so the
human-readable version lives in README.md as a connection table -- keep the
two in step.

BACK-SIDE PARTS ARE THE TRAP (#21). A part on the low side shows its BACK to
anyone looking at KiCad's top view, so its pins are mirrored there. The sensors
are positioned from their front photographs by two independent routes, and the
L76K-GNSS, face up on the tall side, shows a XIAO's back pattern and is written
out from Seeed's drawing. verify_pins() holds each to a second source.

XIAO HEADER GEOMETRY, from RF_Module:MCU_Seeed_ESP32C3:

    14 pads, x = +/-8.5 mm (rows 17.0 mm apart)
    y = -7.62..+7.62, 7 per row at 2.54 mm pitch
    board 17.5 x 21 mm

Pin numbering follows that footprint: 1..7 down the -8.5 mm row, 8..14 back up
the +8.5 mm row, so pin 8 faces pin 7. That footprint is a FRONT view, so it
holds as drawn for a XIAO on the tall side -- which both are.
"""
import json
import os
import sys

import pcbnew

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(REPO, "hardware", "PCB-carrier", "PCB-carrier.kicad_pcb")
# Everything gen_carrier_diagram.py draws, so the drawing cannot drift from the board.
LAYOUT = os.path.join(REPO, "hardware", "PCB-carrier", "PCB-carrier-layout.json")

BOARD_W = 24.0             # the PayloadSled web's width
BOARD_H = 90.4             # y 0 at nose z 25.4, forward positive
BOARD_NOSE_Z0 = 25.4       # payload-sled.md: the board's aft end
THICKNESS = 1.0
COPPER_LAYERS = 4
CORNER_R = 2.0
CX = BOARD_W / 2.0
PITCH = 2.54

MM = pcbnew.FromMM

# ---- the two XIAOs, tall side, USB-C aft -------------------------------------
XIAO_ROW_DX = 8.5          # header rows at +/-8.5 mm from the XIAO centreline
XIAO_PINS_PER_ROW = 7
# XIAO-ESP32S3-cam sits under the camera pad, centred at nose z 43.435
# (payload-sled.md, #89): 43.4 - 25.4. XIAO-ESP32S3-lora at the forward end.
CAM_Y = 18.0
LORA_Y = 68.0

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
# The cam XIAO feeds the +3V3 plane and the sensors. The lora XIAO feeds only the
# L76K-GNSS, from its own 3V3 pin -- kept off the plane so no two regulators are
# ever paralleled. GPS_TX / GPS_RX are named from the XIAO's side.
CAM_SIGNALS = {"D0": "BUZZER", "D4": "SDA", "D5": "SCL", "3V3": "+3V3", "GND": "GND"}
LORA_SIGNALS = {"D6": "GPS_TX", "D7": "GPS_RX", "3V3": "+3V3_LORA", "GND": "GND"}
XIAOS = [("J_CAM_", CAM_Y, CAM_SIGNALS), ("J_LORA_", LORA_Y, LORA_SIGNALS)]

# ---- L76K-GNSS, tall side, its own pins, antenna end forward ------------------
# Seeed's V1.1 top view (hardware/L76K-GNSS), antenna end UP, as (x, y) on
# screen. Pads are named by the XIAO position they meet; the functions are RX
# at D6, TX at D7, WAKE at D0, RESET at D2. Face up it shows a XIAO's BACK
# pattern, so it is written out, not derived from XIAO_PIN.
L76K_TOPVIEW = {
    "D6": (-8.5, -7.62), "D5": (-8.5, -5.08), "D4": (-8.5, -2.54), "D3": (-8.5, 0.0),
    "D2": (-8.5, 2.54), "D1": (-8.5, 5.08), "D0": (-8.5, 7.62),
    "D7": (8.5, -7.62), "D8": (8.5, -5.08), "D9": (8.5, -2.54), "D10": (8.5, 0.0),
    "3V3": (8.5, 2.54), "GND": (8.5, 5.08), "5V": (8.5, 7.62),
}
L76K_Y = 44.0              # body y 33.5..54.5
L76K_NETS = {"D6": "GPS_TX", "D7": "GPS_RX", "3V3": "+3V3_LORA", "GND": "GND"}
# The same picture turned by eye so the antenna points forward (+y): each
# column listed aft to forward. verify_pins() holds the code's turn to it.
L76K_COL_X20 = ["D0", "D1", "D2", "D3", "D4", "D5", "D6"]      # at x 20.5
L76K_COL_X3 = ["5V", "GND", "3V3", "D10", "D9", "D8", "D7"]    # at x 3.5

# ---- sensors, low side, rows lengthwise --------------------------------------
# Front photographs (module-pinouts.md): 25.5 x 17.8 mm, header row along the
# bottom edge, VIN on the left, 2.54 mm pitch, rows 12.70 mm apart (measured).
# As (px, py) from the board's centre on screen, y down:
ROW_PY = 17.8 / 2 - 2.54            # the header row, 2.54 from the bottom edge
LSM_Y = 41.75                       # body y 29.0..54.5
LSM_PRIMARY = ["VIN", "3Vo", "GND", "SCL", "SDA", "DO", "CS", "I1", "I2"]
LSM_AUX = ["SCX", "SDX", "CS", "DO", "GND"]    # over Primary pins 3..7
LSM_NETS = {"VIN": "+3V3", "GND": "GND", "SCL": "SCL", "SDA": "SDA"}
BMP_Y = 68.25                       # body y 55.5..81.0
BMP_PINS = ["VIN", "3Vo", "GND", "SCL", "SDO", "SDA", "CS", "INT"]
# CS tied high forces I2C, which settles #19's unverified pull-up on the part.
BMP_NETS = {"VIN": "+3V3", "GND": "GND", "SCL": "SCL", "SDA": "SDA", "CS": "+3V3"}
BMP_HOLE_PX = 20.58 / 2             # its mounting holes, top corners
BMP_HOLE_PY = ROW_PY - 12.70        # in line with the top edge's 2.54 inset


def front_pins_lsm():
    out = [(lab, (k - 4) * PITCH, ROW_PY) for k, lab in enumerate(LSM_PRIMARY)]
    out += [(lab + "_AUX", (j - 2) * PITCH, ROW_PY - 12.70) for j, lab in enumerate(LSM_AUX)]
    return out


def front_pins_bmp():
    return [(lab, (k - 3.5) * PITCH, ROW_PY) for k, lab in enumerate(BMP_PINS)]


def low_side_top_xy(px, py, cy):
    """Route 1: turn the front view 90 deg clockwise (row to the left, pin 1
    aft) as seen from the low side, then mirror x for KiCad's top view."""
    x_low, y = CX - py, cy + px
    return BOARD_W - x_low, y


def low_side_top_xy_route2(px, py, cy):
    """Route 2: mirror first (the back view), then turn 90 deg anticlockwise."""
    bx, by = -px, py
    return CX + by, cy - bx


# ---- battery, buzzer, standoffs ----------------------------------------------
# JST-PH on the tall side at the forward end, mating face forward toward the
# battery. VERIFY PIN 1 AGAINST THE BATTERY'S RED LEAD BEFORE SOLDERING --
# reversing a LiPo into a XIAO destroys it, and JST-PH polarity is not standard.
JST_XY = (4.2, 81.5)
JST_NETS = {1: "VBAT", 2: "GND"}
# Wire pads, 3.2 apart: each XIAO's BAT pigtail, and the buzzer's flying leads
# (the PS1240 sits against the nose wall, not on the board).
WIRE_PADS = [
    ("TP_CAM_BAT_P", (8.8, 30.0), "VBAT"), ("TP_CAM_BAT_N", (12.0, 30.0), "GND"),
    ("TP_BUZ", (15.2, 30.0), "BUZZER"), ("TP_BUZ_G", (12.0, 33.2), "GND"),
    ("TP_LORA_BAT_P", (10.4, 80.8), "VBAT"), ("TP_LORA_BAT_N", (13.6, 80.8), "GND"),
]
# Polarity on the silkscreen: reversing a LiPo into a XIAO destroys it.
PLUS_MARKS = [(JST_XY[0] - 2.0, JST_XY[1] - 2.6), (8.8, 28.1), (10.4, 78.9)]
# Two surface-mount M3 standoffs on the low side, 10 mm (Wuerth WA-SMSI
# 9774100360). Screws come in from the web's far face. Each has a 4.4 mm hole
# through the board, so neither sits under a module: standoff 1 is at the aft
# end, under the USB-C plug room, ~13.5 mm from the camera; standoff 2 as far
# forward as the board allows. M3 x 10 through the 3 mm web stops inside the
# standoff. (Standoff 1 was first put under the cam XIAO, where a long screw
# would have reached the XIAO's back -- operator, 2026-09-11.)
STANDOFFS = [(CX, 4.0), (16.5, 85.2)]
STANDOFF_FP = "Mounting_Wuerth_WA-SMSI-M3_H10mm_9774100360"
STANDOFF_R = 3.95          # its courtyard
BMP_LEG_R = 1.9            # an M2 bolt head resting on the board
FILLET_R = 0.9             # a through-hole joint on the far face

FP_ROOT = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/"
FP_LIB = FP_ROOT + "Connector_PinHeader_2.54mm.pretty"
TP_LIB = FP_ROOT + "TestPoint.pretty"
JST_LIB = FP_ROOT + "Connector_JST.pretty"
SO_LIB = FP_ROOT + "Mounting_Wuerth.pretty"


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


def place(board, lib, name, ref, x, y, deg=0, back=False, silk=True):
    """Load a footprint, hide its texts, place it, turn it, maybe put it on B.Cu."""
    fp = load(lib, name, board)
    fp.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
    # Attach before flipping: Flip() on a footprint with no board crashes pcbnew.
    board.Add(fp)
    if back:
        fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    if deg:
        fp.SetOrientationDegrees(deg)
    fp.SetReference(ref)
    # Default designators land on neighbouring pads and trip silk_over_copper.
    # Nothing on this board is read by designator; the README table is the map.
    fp.Reference().SetVisible(False)
    fp.Value().SetVisible(False)
    if not silk:
        # Moved to the fab layer rather than removed: removing through the
        # bindings leaves the footprint unusable.
        for item in fp.GraphicalItems():
            if item.GetLayer() == pcbnew.F_SilkS:
                item.SetLayer(pcbnew.F_Fab)
            elif item.GetLayer() == pcbnew.B_SilkS:
                item.SetLayer(pcbnew.B_Fab)
    return fp


def place_strip(board, ref, fp_name, first, second, back=False):
    """A header strip whose own pad 1 -> pad 2 direction matches first -> second,
    so its courtyard and fab outline sit over the pads."""
    dx, dy = second[0] - first[0], second[1] - first[1]
    best = None
    scratch = pcbnew.CreateEmptyBoard()
    for deg in (0, 90, 180, 270):
        fp = load(FP_LIB, fp_name, board)
        fp.SetPosition(pcbnew.VECTOR2I(MM(first[0]), MM(first[1])))
        scratch.Add(fp)
        if back:
            fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
        fp.SetOrientationDegrees(deg)
        p2 = fp.FindPadByNumber("2")
        ex = pcbnew.ToMM(p2.GetX()) - first[0] - dx
        ey = pcbnew.ToMM(p2.GetY()) - first[1] - dy
        if best is None or ex * ex + ey * ey < best[0]:
            best = (ex * ex + ey * ey, deg)
    return place(board, FP_LIB, fp_name, ref, first[0], first[1], best[1], back, silk=False)


def tight_courtyard(fp, back):
    """Replace a header's courtyard with one hugging its pads.

    The stock header courtyard is 3.6 mm wide for the plastic strip. Here the
    rows on the two sides run 2.15 mm apart by design, and the sensors stand
    proud so their plastic never meets the board -- so the footprint's claim is
    its pads plus 0.15 mm. verify_clearances() is what keeps the holes apart.
    """
    crt = pcbnew.B_CrtYd if back else pcbnew.F_CrtYd
    fab = pcbnew.B_Fab if back else pcbnew.F_Fab
    for item in fp.GraphicalItems():
        if item.GetLayer() == crt:
            item.SetLayer(fab)
    xs = [pcbnew.ToMM(p.GetX()) for p in fp.Pads()]
    ys = [pcbnew.ToMM(p.GetY()) for p in fp.Pads()]
    r = pcbnew.PCB_SHAPE(fp)
    r.SetShape(pcbnew.SHAPE_T_RECT)
    r.SetStart(pcbnew.VECTOR2I(MM(min(xs) - 1.0), MM(min(ys) - 1.0)))
    r.SetEnd(pcbnew.VECTOR2I(MM(max(xs) + 1.0), MM(max(ys) + 1.0)))
    r.SetLayer(crt)
    r.SetWidth(MM(0.05))
    fp.Add(r)


def add_row(board, ref, fp_name, pads, nets, back=False):
    """One header strip whose pads are placed absolutely.

    pads: list of (label, x, y) in pad-number order. nets: label -> net name.
    """
    fp = place_strip(board, ref, fp_name, pads[0][1:], pads[1][1:], back)
    for i, (label, x, y) in enumerate(pads, 1):
        pad = fp.FindPadByNumber(str(i))
        pad.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
        if label in nets:
            pad.SetNet(board.nets[nets[label]])
    tight_courtyard(fp, back)
    return fp


def add_xiao(board, ref, cy, signals):
    """Two 1x7 headers 17.0 mm apart, a XIAO on the tall side, USB-C aft."""
    netmap = {XIAO_PIN[k]: v for k, v in signals.items()}
    rows = {"A": [], "B": []}
    for pin in range(1, 15):
        dx, dy = FOOTPRINT_PIN[pin]
        rows["A" if pin <= 7 else "B"].append((pin, CX + dx, cy + dy))
    for side, pads in rows.items():
        fp_pads = [(str(p), x, y) for p, x, y in pads]
        add_row(board, ref + side, "PinHeader_1x07_P2.54mm_Vertical", fp_pads,
                {str(p): netmap[p] for p, _, _ in pads if p in netmap})


def l76k_board_xy(label):
    """Seeed's top view turned 180 deg, so the antenna end points forward (+y)."""
    lx, ly = L76K_TOPVIEW[label]
    return (CX - lx, L76K_Y - ly)


def add_l76k(board):
    cols = {}
    for label in L76K_TOPVIEW:
        x, y = l76k_board_xy(label)
        cols.setdefault(round(x, 3), []).append((label, x, y))
    for ref, x in (("J_L76K_A", min(cols)), ("J_L76K_B", max(cols))):
        pads = sorted(cols[x], key=lambda p: p[2])
        add_row(board, ref, "PinHeader_1x07_P2.54mm_Vertical", pads, L76K_NETS)


def sensor_pads(front, cy):
    return [(lab, *low_side_top_xy(px, py, cy)) for lab, px, py in front]


def add_sensors(board):
    lsm = sensor_pads(front_pins_lsm(), LSM_Y)
    add_row(board, "J_LSM_P", "PinHeader_1x09_P2.54mm_Vertical",
            [p for p in lsm if not p[0].endswith("_AUX")], LSM_NETS, back=True)
    add_row(board, "J_LSM_A", "PinHeader_1x05_P2.54mm_Vertical",
            [p for p in lsm if p[0].endswith("_AUX")], {}, back=True)
    add_row(board, "J_BMP", "PinHeader_1x08_P2.54mm_Vertical",
            sensor_pads(front_pins_bmp(), BMP_Y), BMP_NETS, back=True)


def bmp_legs():
    return [low_side_top_xy(s * BMP_HOLE_PX, BMP_HOLE_PY, BMP_Y) for s in (-1, 1)]


def add_power_and_wires(board):
    fp = place(board, JST_LIB, "JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal", "J_BAT",
               JST_XY[0], JST_XY[1], silk=False)
    for num, net in JST_NETS.items():
        fp.FindPadByNumber(str(num)).SetNet(board.nets[net])
    for ref, (x, y), net in WIRE_PADS:
        tp = place(board, TP_LIB, "TestPoint_THTPad_D2.0mm_Drill1.0mm", ref, x, y, silk=False)
        tp.FindPadByNumber("1").SetNet(board.nets[net])
    for x, y in PLUS_MARKS:
        t = pcbnew.PCB_TEXT(board)
        t.SetText("+")
        t.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
        t.SetLayer(pcbnew.F_SilkS)
        t.SetTextSize(pcbnew.VECTOR2I(MM(1.2), MM(1.2)))
        t.SetTextThickness(MM(0.2))
        board.Add(t)
    for i, (x, y) in enumerate(STANDOFFS, 1):
        place(board, SO_LIB, STANDOFF_FP, "SO%d" % i, x, y, back=True)


# The footprint the pin numbering follows, RF_Module:MCU_Seeed_ESP32C3, as a
# pin -> (x, y) table. Row -8.5 runs 1..7 with y increasing; row +8.5 runs 8..14
# with y decreasing, so 1 faces 14 and 7 faces 8. BOTH coordinates matter: pins
# 7 and 8 share y = +7.62, as do 1 and 14 at -7.62, so only x tells the rows apart.
FOOTPRINT_PIN = {p: (-XIAO_ROW_DX, -7.62 + (p - 1) * PITCH) for p in range(1, 8)}
FOOTPRINT_PIN.update({p: (+XIAO_ROW_DX, 7.62 - (p - 8) * PITCH) for p in range(8, 15)})

# The same XIAO read off its own silkscreen, independently of the footprint and
# of XIAO_PIN: docs/module-pinouts.md, from XIAO-ESP32-S3-bottom.jpg -- the
# UNDERSIDE, USB-C at the top, each column listed from the USB-C end.
UNDERSIDE_LEFT = ["5V", "GND", "3V3", "D10", "D9", "D8", "D7"]
UNDERSIDE_RIGHT = ["D0", "D1", "D2", "D3", "D4", "D5", "D6"]


def photo_pin(signal):
    """(dx, dy) of a signal on a tall-side XIAO, from the underside photo: the
    front, which the top view shows, is the underside mirrored."""
    for col, dx in ((UNDERSIDE_LEFT, -XIAO_ROW_DX), (UNDERSIDE_RIGHT, +XIAO_ROW_DX)):
        if signal in col:
            return (-dx, -7.62 + col.index(signal) * PITCH)
    raise KeyError(signal)


def pads_by_ref_net(board):
    out = {}
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            if pad.GetNetname():
                out.setdefault((fp.GetReference(), pad.GetNetname()), []).append(
                    (pcbnew.ToMM(pad.GetX()), pcbnew.ToMM(pad.GetY())))
    return out


def near(pts, x, y):
    return any(abs(px - x) < 0.01 and abs(py - y) < 0.01 for px, py in pts)


def verify_pins(board):
    """Assert every net sits where its part puts that pin, from two sources each.

    THE POINT OF THIS FUNCTION IS THAT IT RUNS. Three revisions of this file
    shipped a wrong pin mapping -- GPS on 6/7 and I2C on 4/5 the first time, the
    whole +8.5 row mirrored the second (#18), a back-mounted XIAO netted as if on
    the front the third (#21). All three were found by a human.

    XIAO: the footprint table against the underside photograph. L76K-GNSS:
    Seeed's drawing turned by code against the same drawing turned by eye.
    Sensors, which sit on the back: their front photographs carried to KiCad's
    top view by two independent routes (turn then mirror, mirror then turn).
    """
    got = pads_by_ref_net(board)
    pin_name = {v: k for k, v in XIAO_PIN.items()}
    bad = []

    for ref, cy, signals in XIAOS:
        for sig, net in signals.items():
            pin = XIAO_PIN[sig]
            fx, fy = FOOTPRINT_PIN[pin]
            px, py = photo_pin(sig)
            if abs(px - fx) > 0.01 or abs(py - fy) > 0.01:
                bad.append("%s %s: footprint (%.2f, %.2f), photo (%.2f, %.2f)"
                           % (ref, sig, fx, fy, px, py))
            if not near(got.get((ref + ("A" if pin <= 7 else "B"), net), []), CX + fx, cy + fy):
                bad.append("%s %s (%s) not at (%.2f, %.2f)" % (ref, sig, net, CX + fx, cy + fy))

    for label, net in L76K_NETS.items():
        col = L76K_COL_X20 if label in L76K_COL_X20 else L76K_COL_X3
        ex = CX + XIAO_ROW_DX if col is L76K_COL_X20 else CX - XIAO_ROW_DX
        ey = L76K_Y + (col.index(label) - 3) * PITCH
        x, y = l76k_board_xy(label)
        if abs(x - ex) > 0.01 or abs(y - ey) > 0.01:
            bad.append("L76K %s: turned (%.2f, %.2f), by eye (%.2f, %.2f)" % (label, x, y, ex, ey))
        ref = "J_L76K_B" if ex > CX else "J_L76K_A"
        if not near(got.get((ref, net), []), ex, ey):
            bad.append("L76K %s (%s) not at (%.2f, %.2f)" % (label, net, ex, ey))

    for name, front, cy, nets, ref in (("LSM6DSO32", front_pins_lsm(), LSM_Y, LSM_NETS, "J_LSM_P"),
                                       ("BMP388", front_pins_bmp(), BMP_Y, BMP_NETS, "J_BMP")):
        for lab, px, py in front:
            a = low_side_top_xy(px, py, cy)
            b = low_side_top_xy_route2(px, py, cy)
            if abs(a[0] - b[0]) > 0.01 or abs(a[1] - b[1]) > 0.01:
                bad.append("%s %s: route 1 (%.2f, %.2f), route 2 (%.2f, %.2f)" % (name, lab, *a, *b))
            if lab in nets and not near(got.get((ref, nets[lab]), []), *a):
                bad.append("%s %s (%s) not at (%.2f, %.2f)" % (name, lab, nets[lab], *a))

    if bad:
        raise AssertionError("pin mapping wrong:\n  " + "\n  ".join(bad))
    print("verify   XIAOs, L76K-GNSS and sensors match their footprints and photographs")


def verify_clearances(board):
    """No two through-holes too close, and nothing under a standoff or a BMP388 leg.

    The two sides share every through-hole, so a sensor pin on the low side can
    land on a module pin on the tall side. That is the check that makes a
    two-sided layout safe to change.
    """
    holes = []
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            if pad.GetAttribute() == pcbnew.PAD_ATTRIB_PTH:
                holes.append((fp.GetReference(), pad.GetNumber(),
                              pcbnew.ToMM(pad.GetX()), pcbnew.ToMM(pad.GetY())))
    bad = []
    for i in range(len(holes)):
        for j in range(i + 1, len(holes)):
            a, b = holes[i], holes[j]
            if a[0] == b[0]:
                continue
            d = ((a[2] - b[2]) ** 2 + (a[3] - b[3]) ** 2) ** 0.5
            if d < 2.1:
                bad.append("%s-%s and %s-%s only %.2f mm apart" % (a[0], a[1], b[0], b[1], d))
    keep = [(x, y, STANDOFF_R + FILLET_R, "standoff") for x, y in STANDOFFS]
    keep += [(x, y, BMP_LEG_R + FILLET_R, "BMP388 leg") for x, y in bmp_legs()]
    for ref, num, px, py in holes:
        for x, y, r, what in keep:
            if (px - x) ** 2 + (py - y) ** 2 < r * r:
                bad.append("%s pad %s at (%.2f, %.2f) under the %s at (%.1f, %.1f)"
                           % (ref, num, px, py, what, x, y))
    if bad:
        raise AssertionError("clearance breached:\n  " + "\n  ".join(bad))
    print("verify   %d through-holes clear of each other, the standoffs and the BMP388 legs"
          % len(holes))


def add_plane(board, layer, net, inset=0.5):
    """Flood an inner layer with one net.

    GND on In1 and +3V3 on In2 give every signal on the outer layers a solid
    return path, and feed the sensors without a routed trace. Only the cam XIAO
    feeds +3V3; the lora XIAO's 3V3 reaches the L76K-GNSS alone.
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


def write_layout(board):
    """The board as data for gen_carrier_diagram.py: pads from pcbnew itself,
    part bodies from the same constants that placed them."""
    side_of = {}
    pads = []
    for fp in board.GetFootprints():
        side_of[fp.GetReference()] = "low" if fp.IsFlipped() else "tall"
        for pad in fp.Pads():
            pads.append({"ref": fp.GetReference(), "num": pad.GetNumber(),
                         "net": pad.GetNetname(), "side": side_of[fp.GetReference()],
                         "x": round(pcbnew.ToMM(pad.GetX()), 3),
                         "y": round(pcbnew.ToMM(pad.GetY()), 3)})
    bodies = [
        # name, side, x0, y0, x1, y1 -- outlines in KiCad's top view
        ("XIAO-ESP32S3-cam", "tall", CX - 8.9, CAM_Y - 10.5, CX + 8.9, CAM_Y + 10.5),
        ("L76K-GNSS", "tall", CX - 9.0, L76K_Y - 10.5, CX + 9.0, L76K_Y + 10.5),
        ("XIAO-ESP32S3-lora", "tall", CX - 8.9, LORA_Y - 10.5, CX + 8.9, LORA_Y + 10.5),
        ("JST-PH", "tall", JST_XY[0] - 2.45, JST_XY[1] - 1.85, JST_XY[0] + 4.45, JST_XY[1] + 6.75),
        ("LSM6DSO32", "low", CX - 8.9, LSM_Y - 12.75, CX + 8.9, LSM_Y + 12.75),
        ("BMP388", "low", CX - 8.9, BMP_Y - 12.75, CX + 8.9, BMP_Y + 12.75),
    ]
    out = {
        "board": {"w": BOARD_W, "h": BOARD_H, "r": CORNER_R, "nose_z0": BOARD_NOSE_Z0},
        "usb_c": [{"x0": CX - 4.0, "y0": y - 11.7, "x1": CX + 4.0, "y1": y - 10.5}
                  for y in (CAM_Y, LORA_Y)],
        "bodies": [dict(zip(("name", "side", "x0", "y0", "x1", "y1"), b)) for b in bodies],
        "standoffs": [{"x": x, "y": y, "r": STANDOFF_R} for x, y in STANDOFFS],
        "bmp_legs": [{"x": x, "y": y} for x, y in bmp_legs()],
        "pads": sorted(pads, key=lambda p: (p["ref"], p["num"])),
    }
    with open(LAYOUT, "w") as f:
        json.dump(out, f, indent=1)
        f.write("\n")
    print("wrote    %s" % LAYOUT)


def write_rules():
    """The project's one DRC exception, beside the board where kicad-cli finds it.

    Wuerth's WA-SMSI land pattern puts its solder pads right at the edge of its
    own 4.4 mm hole. That is the maker's design, not a clearance error, so it is
    allowed for the standoffs and nowhere else.
    """
    with open(OUT.replace(".kicad_pcb", ".kicad_dru"), "w") as f:
        f.write('(version 1)\n'
                '(rule "Wuerth WA-SMSI standoff land pattern"\n'
                '  (condition "A.memberOfFootprint(\'SO*\') && B.memberOfFootprint(\'SO*\')")\n'
                '  (constraint hole_clearance (min 0mm)))\n')


def main():
    board = pcbnew.CreateEmptyBoard()
    board.SetCopperLayerCount(COPPER_LAYERS)
    board.GetDesignSettings().SetBoardThickness(MM(THICKNESS))

    board.nets = {}
    for name in ("GND", "+3V3", "+3V3_LORA", "VBAT", "GPS_TX", "GPS_RX", "SDA", "SCL",
                 "BUZZER"):
        n = pcbnew.NETINFO_ITEM(board, name)
        board.Add(n)
        board.nets[name] = n

    outline(board, BOARD_W, BOARD_H, CORNER_R)
    for ref, cy, signals in XIAOS:
        add_xiao(board, ref, cy, signals)
    add_l76k(board)
    add_sensors(board)
    add_power_and_wires(board)

    verify_pins(board)
    verify_clearances(board)

    add_plane(board, pcbnew.In1_Cu, board.nets["GND"])
    add_plane(board, pcbnew.In2_Cu, board.nets["+3V3"])
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pcbnew.SaveBoard(OUT, board)
    write_rules()
    write_layout(board)

    bbox = board.GetBoardEdgesBoundingBox()
    print("wrote    %s" % OUT)
    print("outline  %.2f x %.2f mm, nose z %.1f..%.1f"
          % (pcbnew.ToMM(bbox.GetWidth()), pcbnew.ToMM(bbox.GetHeight()),
             BOARD_NOSE_Z0, BOARD_NOSE_Z0 + BOARD_H))
    print("layers   %d copper, %.2f mm"
          % (board.GetCopperLayerCount(),
             pcbnew.ToMM(board.GetDesignSettings().GetBoardThickness())))
    print("parts    %d footprints" % len(board.GetFootprints()))
    print("nets     %d declared" % len(board.nets))
    print("planes   %d filled" % len(board.Zones()))


if __name__ == "__main__":
    sys.exit(main())
