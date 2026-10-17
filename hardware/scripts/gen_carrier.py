"""Generate the carrier PCB: one two-sided board.

    /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 \
        hardware/scripts/gen_carrier.py

Supersedes gen_outline.py (stage 2a), which produced outline and holes only.

ONE BOARD, TWO SIDES (operator, 2026-09-11; hardware/PCB-carrier/PCB-carrier-design.md).
The board sits on the PayloadSled's centre line and hangs off the web on two
M3 standoffs, so it can come off the sled as one unit:

    tall side  F.Cu, faces 270 deg (the camera port)
               XIAO-ESP32S3-cam aft, under the camera; L76K-GNSS; XIAO-ESP32S3-lora
               turned 90 deg; the two data-link jumpers forward
               the PS1240 buzzer at the forward end, facing the Nosecone's sound hole
    low side   B.Cu, faces 90 deg (the web)
               LSM6DSO32, rows lengthwise; BMP388 turned, its row across the board;
               two plain M3 holes for female-female standoffs

The web is offset toward 90 deg, clear of the low side, and two M3 plastic
screws come in from its far face into the standoffs (js-rocket#99). Nothing
fastens through to the tall side, so no screw head ever sits under a module.

WHY THE SENSORS RUN LENGTHWISE. Written when the XIAO rows were drawn at
x 3.5 / 20.5 and the sensors' rows sat 2.14 mm inboard of them. At the real
spacing (#33) the XIAO rows are x 4.38 / 19.62, and a sensor row 12.7 mm wide
behind a XIAO-pattern module lands 1.27 mm from its rows: verify_clearances()
now refuses it.
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

XIAO HEADER GEOMETRY, from Seeed's own XIAO ESP32S3 footprint (Flux; screenshot in
hardware/XIAO-ESP32S3-cam/PCB_Design_XIAO4.png): through-hole pins at x = +/-7.62,
rows 15.24 mm apart (#33). NOT KiCad's RF_Module:MCU_Seeed_ESP32C3, whose +/-8.5
is the centre of each castellated SMD pad -- this file used that until 2026-09-15
and no XIAO could be fitted. Pin numbering still follows that footprint:

    14 pins, x = +/-7.62 mm (rows 15.24 mm apart)
    y = -7.62..+7.62, 7 per row at 2.54 mm pitch
    board 17.5 x 21 mm

Pin numbering: 1..7 down the -7.62 mm row, 8..14 back up
the +7.62 mm row, so pin 8 faces pin 7. That footprint is a FRONT view, so it
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
BOARD_H = 115.7            # y 0 at nose z 25.4, forward positive. 90.4 until 2026-09-15, when the
                           # battery moved behind the board (layout B2, PCB-carrier-design.md)
BOARD_NOSE_Z0 = 25.4       # payload-sled.md: the board's aft end
THICKNESS = 1.6                # OSH Park 4-layer is 1.6 mm only (operator, 2026-09-15); was 1.0
COPPER_LAYERS = 4
CORNER_R = 2.0
CX = BOARD_W / 2.0
PITCH = 2.54

MM = pcbnew.FromMM

# ---- the two XIAOs, tall side -------------------------------------------------
# XIAO-ESP32S3-cam USB-C aft. XIAO-ESP32S3-lora TURNED 90 deg (PCB-carrier.md, #34):
# its USB-C out the -x long edge, so its underside BAT pads
# (footprint x -4.5) land forward, toward its pigtail holes. Its 21 mm length runs
# across the 24 mm board.
XIAO_ROW_DX = 7.62         # header rows at +/-7.62 mm from the XIAO centreline (#33)
# Seeed's footprint, held separately so verify_pins() can check the board against
# it: 5V at (7.62, 7.62), TX at (-7.62, -7.62), pitch 2.54, hole 1.1.
SEEED_XIAO_ROW_DX = 7.62
XIAO_PINS_PER_ROW = 7
# XIAO-ESP32S3-cam sits under the camera pad, centred at nose z 43.435
# (payload-sled.md, #89): 43.4 - 25.4. XIAO-ESP32S3-lora NEXT to it, ahead of the
# L76K-GNSS (operator, 2026-10-15, #36): nearer the LoRa strip at the PORT end, and
# the GNSS nearer its patch at the forward disc. Its rows start 1 mm past the cam
# XIAO's battery anchors' keep-out (y 30 + 1.5). LORA_Y was 68.0, behind the GNSS.
CAM_Y = 18.0
LORA_Y = 41.4
LORA_ANCHOR_DY = 12.8      # its BAT anchors, forward of its centre, past its body

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
# The data links' far ends (operator, 2026-10-16, #26): the cam XIAO hears the GPS on
# D1 and sends event text from D3; the lora XIAO takes it on D1 (GPIO2), which stock
# Meshtastic leaves free -- its seeed_xiao_s3 variant claims D0, D4-D10 and GPIO38-42.
# The PS1240 is driven from TWO pins in opposite phase, D0 and D2, for twice the
# swing across the disc, ~+6 dB (operator, 2026-10-17, #25). D2 (GPIO3) is quiet at
# boot; D6 would chirp it with the ROM's boot log.
CAM_SIGNALS = {"D0": "BUZZER", "D1": "GPS_CAM", "D2": "BUZZER_B", "D3": "EVT_CAM", "D4": "SDA", "D5": "SCL",
               "3V3": "+3V3", "GND": "GND"}
LORA_SIGNALS = {"D1": "EVT_LORA", "D6": "GPS_TX", "D7": "GPS_RX", "3V3": "+3V3_LORA", "GND": "GND"}
XIAOS = [("J_CAM_", CAM_Y, CAM_SIGNALS, False), ("J_LORA_", LORA_Y, LORA_SIGNALS, True)]


def xiao_xy(cy, dx, dy, turned):
    """Board position of footprint offset (dx, dy) on a XIAO centred at (CX, cy).
    Turned: footprint (dx, dy) -> board (dy, -dx), so the USB-C end (dy -7.62)
    points to -x and the -7.62 row (pins 1..7) lies forward."""
    return (CX + dy, cy - dx) if turned else (CX + dx, cy + dy)

# ---- L76K-GNSS, tall side, its own pins, TURNED: antenna end toward +x -------
# Turned 90 deg like the lora (operator, 2026-10-15, #36): 18 mm along the board
# instead of 21, its rows across it. Antenna end toward +x, away from the -x edge
# the LoRa lead runs round. Forward of the lora XIAO's battery anchors.
# Seeed's V1.1 top view (hardware/L76K-GNSS), antenna end UP, as (x, y) on
# screen. Pads are named by the XIAO position they meet; the functions are RX
# at D6, TX at D7, WAKE at D0, RESET at D2. Face up it shows a XIAO's BACK
# pattern, so it is written out, not derived from XIAO_PIN.
L76K_TOPVIEW = {
    "D6": (-7.62, -7.62), "D5": (-7.62, -5.08), "D4": (-7.62, -2.54), "D3": (-7.62, 0.0),
    "D2": (-7.62, 2.54), "D1": (-7.62, 5.08), "D0": (-7.62, 7.62),
    "D7": (7.62, -7.62), "D8": (7.62, -5.08), "D9": (7.62, -2.54), "D10": (7.62, 0.0),
    "3V3": (7.62, 2.54), "GND": (7.62, 5.08), "5V": (7.62, 7.62),
}
L76K_Y = LORA_Y + LORA_ANCHOR_DY + 1.5 + 1.0 + 9.0   # 65.7: body 56.7..74.7
L76K_NETS = {"D6": "GPS_TX", "D7": "GPS_RX", "3V3": "+3V3_LORA", "GND": "GND"}
# The same picture turned by eye. Antenna forward, each column listed aft to
# forward, X20 at x 19.62 and X3 at x 4.38; turned so the antenna points +x, each
# column becomes a row listed from -x to +x: X20 the aft row (y - 7.62), X3 the
# forward row (y + 7.62). verify_pins() holds the code's turn to it.
L76K_COL_X20 = ["D0", "D1", "D2", "D3", "D4", "D5", "D6"]      # aft row
L76K_COL_X3 = ["5V", "GND", "3V3", "D10", "D9", "D8", "D7"]    # forward row

# ---- sensors, low side, rows lengthwise --------------------------------------
# Front photographs (module-pinouts.md): 25.5 x 17.8 mm, header row along the
# bottom edge, VIN on the left, 2.54 mm pitch, rows 12.70 mm apart (measured).
# As (px, py) from the board's centre on screen, y down:
ROW_PY = 17.8 / 2 - 2.54            # the header row, 2.54 from the bottom edge
LSM_Y = 20.75                       # body y 8.0..33.5 -- aft, clear of the aft standoff (B2)
# Slid toward +x (operator, 2026-09-15, #33): at the real XIAO spacing its rows,
# 12.7 mm apart, cannot sit inside the cam XIAO's 15.24. So the 9-pin row goes
# OUTSIDE the cam XIAO's +x row (x 19.62) and the 5-pin row inside it. 3.45 puts
# the 9-pin row at x 21.81: its joints clear that row's header plastic (to x 20.89)
# by FILLET_R, and its holes sit 2.18 mm from the XIAO's. The body hangs ~0.36 mm
# past the board edge, at r <= 8.8 -- inside the door.
LSM_DX = 3.45
LSM_PRIMARY = ["VIN", "3Vo", "GND", "SCL", "SDA", "DO", "CS", "I1", "I2"]
LSM_AUX = ["SCX", "SDX", "CS", "DO", "GND"]    # over Primary pins 3..7
LSM_NETS = {"VIN": "+3V3", "GND": "GND", "SCL": "SCL", "SDA": "SDA"}
# BMP388 TURNED 90 deg (operator, 2026-10-12, #36), so the tall side's forward
# end has room for the PS1240. Its 25.5 mm length lies across the 24 mm board,
# ~0.75 past each edge at r <= 8.8 -- clear of the web at r 10.5. Its row runs
# across, aft, just forward of the lora's battery anchors; its two mounting holes
# land forward at the board's edges. NO BOLT HOLES in the carrier: a spacer goes
# through each of the BMP388's own holes and rests on the low face, so nothing
# crosses to the tall side. Lengthwise until 2026-10-12, at BMP_Y 94.6.
BMP_Y = 96.0                        # body y 87.1..104.9 -- clear of standoff 2's courtyard (106.55)
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


def bmp_top_xy(px, py, cy):
    """The turned BMP388, route 1: seen from the low side, turn the front view
    180 deg (row aft), then mirror x for KiCad's top view."""
    x_low, y = CX - px, cy - py
    return BOARD_W - x_low, y


def bmp_top_xy_route2(px, py, cy):
    """Route 2: mirror first (the back view), then turn it 180 deg in the top view."""
    bx, by = -px, py
    return CX - bx, cy - by


# ---- battery, buzzer, standoffs ----------------------------------------------
# NO BATTERY ON THE BOARD (operator, 2026-10-11, #30). A Y-cable joins the
# battery to the two XIAOs' BAT pigtails, off the board, and the battery's lead
# runs aft to below the sled, where it unplugs for the charger. So there is no
# JST and no VBAT net here; until then there was a JST-PH at (4.2, 81.5) and
# the pigtails were soldered into a VBAT net.
# The battery, from PCB-carrier.md -- the carrier's source of truth (operator,
# 2026-09-15). Change it there first, then here. Not a footprint: it lies on the
# low side against the web, 5.25 mm off the board, and the PayloadSled's cage is
# built to this position. Written to the layout JSON so the diagram and the fit
# mock both draw it from here rather than from copies of their own.
BATTERY_Y = (42.5, 79.9)     # nose z 67.9..105.3 -- the cage cavity, 37.4 mm (js-rocket#99)
BATTERY_HALF_W = 14.5        # 29 mm across, 2.5 past each board edge
BATTERY_R = (5.75, 10.5)     # toward 90 deg: 4.75 thick, against the web's inner face
# Wire holes, 3.2 apart: each XIAO's BAT pigtail. The pigtail holes
# are ANCHORS, not connections: no net. The wires lace through them to the
# Y-cable, so a pull lands on the board, not on the XIAO's 2.3 x 1.3 mm pads.
WIRE_PADS = [
    ("TP_CAM_BAT_P", (8.8, 30.0), None), ("TP_CAM_BAT_N", (12.0, 30.0), None),
    ("TP_LORA_BAT_P", (10.4, LORA_Y + LORA_ANCHOR_DY), None),
    ("TP_LORA_BAT_N", (13.6, LORA_Y + LORA_ANCHOR_DY), None),
]
# Two data links, each a 2-pin header with a slide-on shunt and a ~1 kOhm series
# resistor, on the tall side at the forward end (operator, 2026-09-12, #26;
# PCB-carrier-design.md). Shunt off is the safe state. GPS -> cam: header pin 1 on
# GPS_RX, the L76K's transmit line. cam -> lora: one way, for Meshtastic's Serial
# module. Far ends: GPS_CAM to cam D1, EVT_CAM from cam D3, EVT_LORA to lora D1
# (operator, 2026-10-16, #26). Each resistor sits at the cam XIAO's end.
# Between the lora's battery anchors and the BMP388's row, one link at each edge
# (#36, 2026-10-12); in the middle at y 92..102.5 until then, where the PS1240
# now sits.
LINK_HEADERS = [("J_LINK_GPS", (3.5, 84.0), {1: "GPS_RX", 2: "LINK_GPS"}),
                ("J_LINK_EVT", (16.9, 84.0), {1: "LINK_EVT", 2: "EVT_LORA"})]
LINK_RESISTORS = [("R_LINK_GPS", (3.0, 87.0), {1: "LINK_GPS", 2: "GPS_CAM"}),
                  ("R_LINK_EVT", (14.5, 87.0), {1: "EVT_CAM", 2: "LINK_EVT"})]
LINK_LABELS = [("GPS", 8.4, 84.0), ("EVT", 14.2, 84.0)]
# The PS1240 ON THE BOARD (operator, 2026-10-12, #36), tall side, forward, facing
# a sound hole in the Nosecone at 270 deg. Its leads were flying wires to the nose
# wall until then, from wire pads between the cam XIAO and the L76K-GNSS.
# 12.2 x 6.5 mm (TDK catalog; Adafruit lists 11.9 x 6.53), so its top is at r 7.6
# against the bore's 20. BUZ_PITCH is TDK's, confirmed on the part in hand 2026-10-15.
BUZ_XY = (11.5, 103.0)              # nose z 128.4
BUZ_R = 6.1
BUZ_PITCH = 5.0
BUZ_PADS = [("TP_BUZ", (BUZ_XY[0] - BUZ_PITCH / 2, BUZ_XY[1]), "BUZZER"),
            ("TP_BUZ_G", (BUZ_XY[0] + BUZ_PITCH / 2, BUZ_XY[1]), "BUZZER_B")]
R_FP = "R_Axial_DIN0204_L3.6mm_D1.6mm_P5.08mm_Horizontal"   # pad 2 at +5.08 x at 0 deg
# Each XIAO's battery pigtail laces through the two holes directly behind it
# (operator, 2026-09-13, #14; anchors only from 2026-10-11), so the holes are
# labelled on BOTH sides -- BAT, + and - -- mirrored on the back, + for the red
# wire. The low-side labels end up under the LSM6DSO32 and BMP388; they are for
# assembly, which laces the pigtails before the sensors go on. Positions keep
# the text off every pad and standoff 2.
BAT_LABELS = [
    ("+", 8.8, 28.1), ("-", 12.0, 28.1), ("BAT", 5.3, 30.0),     # XIAO-ESP32S3-cam
    ("+", 10.4, LORA_Y + LORA_ANCHOR_DY - 1.9), ("-", 13.6, LORA_Y + LORA_ANCHOR_DY - 1.9),
    ("BAT", 17.2, LORA_Y + LORA_ANCHOR_DY - 0.2),                 # XIAO-ESP32S3-lora
]
# Each module's name on the board surface under it, on its own side, so the
# carrier says what goes where during assembly (operator, 2026-09-13). Centred
# in each outline, between its pin rows; the low-side names are mirrored to read
# from there. DRC proves they stay off every pad.
MODULE_LABELS = [
    # (text, x, y, size, back)
    ("XIAO-ESP32S3", 12.0, 13.0, 0.8, False), ("cam", 12.0, 19.2, 1.5, False),
    ("L76K-GNSS", 12.0, L76K_Y, 1.0, False),
    ("XIAO-ESP32S3", 12.0, LORA_Y - 1.2, 0.8, False), ("lora", 12.0, LORA_Y + 1.2, 1.5, False),
    ("LSM6DSO32", 14.4, LSM_Y, 1.0, True),   # between its 5-pin row and the cam's x 19.62 row
    ("BMP388", 12.0, 96.0, 1.0, True),       # between its row and the buzzer's leads
    ("PS1240", BUZ_XY[0], BUZ_XY[1] - 2.5, 1.0, False),   # under the disc
]
# Two plain M3 holes (operator, 2026-10-17): the board hangs off the web on
# female-female M3 hex standoffs, a screw from each side -- the mount proved on the
# fit mock, and no soldering. Each screw head sits on the TALL side, so neither
# hole is under a module: standoff 1 is at the aft
# end, under the USB-C plug room, ~13.5 mm from the camera; standoff 2 as far
# forward as the board allows. Until 2026-10-17 these were Wuerth WA-SMSI
# surface-mount standoffs (9774100360), which need reflow or hot air. (Standoff 1
# was first put under the cam XIAO, where a long screw
# would have reached the XIAO's back -- operator, 2026-09-11.)
STANDOFFS = [(CX, 4.0), (16.5, 110.5)]   # forward one 5.2 mm from the board's end, as before, under
                                          # no module; 85.2 until 2026-09-15
STANDOFF_FP = "MountingHole_3.2mm_M3"
STANDOFF_R = 3.2           # a 5.5 mm hex standoff's corners, low side; > an M3 head's r 2.85, tall side
SCREW_HEAD_R = 2.85        # an M3 button head, ISO 7380, on the tall side
BMP_SPACER_R = 1.9         # a spacer's foot on the low face, under each BMP388 hole
FILLET_R = 0.9             # a through-hole joint on the far face

FP_ROOT = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/"
FP_LIB = FP_ROOT + "Connector_PinHeader_2.54mm.pretty"
TP_LIB = FP_ROOT + "TestPoint.pretty"
R_LIB = FP_ROOT + "Resistor_THT.pretty"
SO_LIB = FP_ROOT + "MountingHole.pretty"


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


def add_xiao(board, ref, cy, signals, turned):
    """Two 1x7 headers 15.24 mm apart, a XIAO on the tall side."""
    netmap = {XIAO_PIN[k]: v for k, v in signals.items()}
    rows = {"A": [], "B": []}
    for pin in range(1, 15):
        x, y = xiao_xy(cy, *FOOTPRINT_PIN[pin], turned)
        rows["A" if pin <= 7 else "B"].append((pin, x, y))
    for side, pads in rows.items():
        fp_pads = [(str(p), x, y) for p, x, y in pads]
        add_row(board, ref + side, "PinHeader_1x07_P2.54mm_Vertical", fp_pads,
                {str(p): netmap[p] for p, _, _ in pads if p in netmap})


def l76k_board_xy(label):
    """Seeed's top view turned 90 deg, so the antenna end (its -y) points to +x."""
    lx, ly = L76K_TOPVIEW[label]
    return (CX - ly, L76K_Y + lx)


def add_l76k(board):
    rows = {}
    for label in L76K_TOPVIEW:
        x, y = l76k_board_xy(label)
        rows.setdefault(round(y, 3), []).append((label, x, y))
    for ref, y in (("J_L76K_A", max(rows)), ("J_L76K_B", min(rows))):
        pads = sorted(rows[y], key=lambda p: p[1])
        add_row(board, ref, "PinHeader_1x07_P2.54mm_Vertical", pads, L76K_NETS)


def sensor_pads(front, cy, dx=0.0):
    out = []
    for lab, px, py in front:
        x, y = low_side_top_xy(px, py, cy)
        out.append((lab, x + dx, y))
    return out


def add_sensors(board):
    lsm = sensor_pads(front_pins_lsm(), LSM_Y, LSM_DX)
    add_row(board, "J_LSM_P", "PinHeader_1x09_P2.54mm_Vertical",
            [p for p in lsm if not p[0].endswith("_AUX")], LSM_NETS, back=True)
    add_row(board, "J_LSM_A", "PinHeader_1x05_P2.54mm_Vertical",
            [p for p in lsm if p[0].endswith("_AUX")], {}, back=True)
    add_row(board, "J_BMP", "PinHeader_1x08_P2.54mm_Vertical",
            [(lab,) + bmp_top_xy(px, py, BMP_Y) for lab, px, py in front_pins_bmp()],
            BMP_NETS, back=True)


def bmp_spacers():
    return [bmp_top_xy(s * BMP_HOLE_PX, BMP_HOLE_PY, BMP_Y) for s in (-1, 1)]


def add_power_and_wires(board):
    for ref, (x, y), net in WIRE_PADS + BUZ_PADS:
        tp = place(board, TP_LIB, "TestPoint_THTPad_D2.0mm_Drill1.0mm", ref, x, y, silk=False)
        if net:
            tp.FindPadByNumber("1").SetNet(board.nets[net])
    def silk_text(text, x, y, back=False, size=1.2):
        t = pcbnew.PCB_TEXT(board)
        t.SetText(text)
        t.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
        t.SetLayer(pcbnew.B_SilkS if back else pcbnew.F_SilkS)
        t.SetMirrored(back)                 # reads the right way from the low side
        t.SetTextSize(pcbnew.VECTOR2I(MM(size), MM(size)))
        t.SetTextThickness(MM(0.2 if size >= 1.2 else 0.15))
        board.Add(t)
    for text, x, y, size, back in MODULE_LABELS:
        silk_text(text, x, y, back=back, size=size)
    for text, x, y in BAT_LABELS:
        size = 1.0 if text == "BAT" else 1.2
        silk_text(text, x, y, back=False, size=size)
        silk_text(text, x, y, back=True, size=size)
    for i, (x, y) in enumerate(STANDOFFS, 1):
        place(board, SO_LIB, STANDOFF_FP, "SO%d" % i, x, y)
    for ref, (x, y), nets in LINK_HEADERS:
        fp = place_strip(board, ref, "PinHeader_1x02_P2.54mm_Vertical", (x, y), (x + PITCH, y))
        for num, net in nets.items():
            fp.FindPadByNumber(str(num)).SetNet(board.nets[net])
    for ref, (x, y), nets in LINK_RESISTORS:
        fp = place(board, R_LIB, R_FP, ref, x, y, silk=False)
        for num, net in nets.items():
            fp.FindPadByNumber(str(num)).SetNet(board.nets[net])
    for text, x, y in LINK_LABELS:
        silk_text(text, x, y, size=0.8)
    ring = pcbnew.PCB_SHAPE(board)          # where the PS1240 sits
    ring.SetShape(pcbnew.SHAPE_T_CIRCLE)
    ring.SetCenter(pcbnew.VECTOR2I(MM(BUZ_XY[0]), MM(BUZ_XY[1])))
    ring.SetEnd(pcbnew.VECTOR2I(MM(BUZ_XY[0] + BUZ_R), MM(BUZ_XY[1])))
    ring.SetLayer(pcbnew.F_SilkS)
    ring.SetWidth(MM(0.15))
    board.Add(ring)


# The footprint the pin numbering follows, RF_Module:MCU_Seeed_ESP32C3, as a
# pin -> (x, y) table. Row -7.62 runs 1..7 with y increasing; row +7.62 runs 8..14
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

    for ref, cy, signals, turned in XIAOS:
        for sig, net in signals.items():
            pin = XIAO_PIN[sig]
            fx, fy = FOOTPRINT_PIN[pin]
            px, py = photo_pin(sig)
            if abs(px - fx) > 0.01 or abs(py - fy) > 0.01:
                bad.append("%s %s: footprint (%.2f, %.2f), photo (%.2f, %.2f)"
                           % (ref, sig, fx, fy, px, py))
            # the photo's offset, turned by hand here rather than through xiao_xy()
            ex, ey = (CX + py, cy - px) if turned else (CX + px, cy + py)
            if not near(got.get((ref + ("A" if pin <= 7 else "B"), net), []), ex, ey):
                bad.append("%s %s (%s) not at (%.2f, %.2f)" % (ref, sig, net, ex, ey))

    for label, net in L76K_NETS.items():
        col = L76K_COL_X20 if label in L76K_COL_X20 else L76K_COL_X3
        ex = CX + (col.index(label) - 3) * PITCH
        ey = L76K_Y - XIAO_ROW_DX if col is L76K_COL_X20 else L76K_Y + XIAO_ROW_DX
        x, y = l76k_board_xy(label)
        if abs(x - ex) > 0.01 or abs(y - ey) > 0.01:
            bad.append("L76K %s: turned (%.2f, %.2f), by eye (%.2f, %.2f)" % (label, x, y, ex, ey))
        ref = "J_L76K_B" if col is L76K_COL_X20 else "J_L76K_A"
        if not near(got.get((ref, net), []), ex, ey):
            bad.append("L76K %s (%s) not at (%.2f, %.2f)" % (label, net, ex, ey))

    for name, front, cy, nets, ref, dx, r1, r2 in (
            ("LSM6DSO32", front_pins_lsm(), LSM_Y, LSM_NETS, "J_LSM_P", LSM_DX,
             low_side_top_xy, low_side_top_xy_route2),
            ("BMP388", front_pins_bmp(), BMP_Y, BMP_NETS, "J_BMP", 0.0, bmp_top_xy, bmp_top_xy_route2)):
        for lab, px, py in front:
            a = r1(px, py, cy)
            b = r2(px, py, cy)
            a, b = (a[0] + dx, a[1]), (b[0] + dx, b[1])
            if abs(a[0] - b[0]) > 0.01 or abs(a[1] - b[1]) > 0.01:
                bad.append("%s %s: route 1 (%.2f, %.2f), route 2 (%.2f, %.2f)" % (name, lab, *a, *b))
            if lab in nets and not near(got.get((ref, nets[lab]), []), *a):
                bad.append("%s %s (%s) not at (%.2f, %.2f)" % (name, lab, nets[lab], *a))

    # every XIAO-pattern header row where Seeed's footprint puts it (#33); the
    # turned lora's and L76K's rows lie across the board, 7.62 either side of centre
    for fp in board.GetFootprints():
        if fp.GetReference()[:-1] in ("J_CAM_", "J_LORA_", "J_L76K_"):
            for pad in fp.Pads():
                if fp.GetReference().startswith("J_LORA_"):
                    dx = abs(pcbnew.ToMM(pad.GetY()) - LORA_Y)
                elif fp.GetReference().startswith("J_L76K_"):
                    dx = abs(pcbnew.ToMM(pad.GetY()) - L76K_Y)
                else:
                    dx = abs(pcbnew.ToMM(pad.GetX()) - CX)
                if abs(dx - SEEED_XIAO_ROW_DX) > 0.01:
                    bad.append("%s pad %s is %.2f mm off centre; Seeed's footprint says %.2f"
                               % (fp.GetReference(), pad.GetNumber(), dx, SEEED_XIAO_ROW_DX))

    if bad:
        raise AssertionError("pin mapping wrong:\n  " + "\n  ".join(bad))
    print("verify   XIAOs, L76K-GNSS and sensors match their footprints and photographs")


def verify_clearances(board):
    """No two through-holes too close, nothing under a standoff or a BMP388
    spacer, and nothing on the tall side under the PS1240 but its own leads.

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
    # A sensor's joint on the tall face must clear a XIAO-pattern header's plastic
    # strip, which sits on that face: 2.54 mm wide, 1.27 past its end pins. The
    # hole-to-hole distance above never saw this (#33).
    strips = {}
    for fp in board.GetFootprints():
        if fp.GetReference()[:-1] in ("J_CAM_", "J_LORA_", "J_L76K_"):
            xs = [pcbnew.ToMM(p.GetX()) for p in fp.Pads()]
            ys = [pcbnew.ToMM(p.GetY()) for p in fp.Pads()]
            strips[fp.GetReference()] = (min(xs) - 1.27, max(xs) + 1.27, min(ys) - 1.27, max(ys) + 1.27)
    for ref, num, px, py in holes:
        if not ref.startswith(("J_LSM", "J_BMP")):
            continue
        for sref, (x0, x1, y0, y1) in strips.items():
            gx = max(x0 - px, 0.0, px - x1)
            gy = max(y0 - py, 0.0, py - y1)
            if (gx * gx + gy * gy) ** 0.5 < FILLET_R:
                bad.append("%s pad %s joint at (%.2f, %.2f) under %s's header plastic"
                           % (ref, num, px, py, sref))
    keep = [(x, y, STANDOFF_R + FILLET_R, "standoff") for x, y in STANDOFFS]
    keep += [(x, y, BMP_SPACER_R + FILLET_R, "BMP388 spacer") for x, y in bmp_spacers()]
    keep += [(BUZ_XY[0], BUZ_XY[1], BUZ_R + FILLET_R, "PS1240")]
    for x, y in STANDOFFS:          # the disc must not sit on a screw head. Standoff 2's
        # clears it by ~0.06 mm on paper, and it fits on the printed mock (operator,
        # 2026-10-17): the disc's 12.2 is the catalog's; Adafruit lists 11.9
        gap = ((x - BUZ_XY[0]) ** 2 + (y - BUZ_XY[1]) ** 2) ** 0.5 - BUZ_R - SCREW_HEAD_R
        if gap < 0.0:
            bad.append("PS1240 disc only %.2f mm from the screw head at (%.1f, %.1f)" % (gap, x, y))
    for ref, num, px, py in holes:
        for x, y, r, what in keep:
            if what == "PS1240" and ref.startswith("TP_BUZ"):
                continue
            if (px - x) ** 2 + (py - y) ** 2 < r * r:
                bad.append("%s pad %s at (%.2f, %.2f) under the %s at (%.1f, %.1f)"
                           % (ref, num, px, py, what, x, y))
    if bad:
        raise AssertionError("clearance breached:\n  " + "\n  ".join(bad))
    print("verify   %d through-holes clear of each other, the standoffs, the BMP388 spacers and the PS1240"
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
        ("L76K-GNSS", "tall", CX - 10.5, L76K_Y - 9.0, CX + 10.5, L76K_Y + 9.0),   # turned
        ("XIAO-ESP32S3-lora", "tall", CX - 10.5, LORA_Y - 8.9, CX + 10.5, LORA_Y + 8.9),   # turned
        ("GPS link", "tall", 1.5, 82.6, 9.6, 88.3),
        ("EVT link", "tall", 13.0, 82.6, 21.1, 88.3),
        ("LSM6DSO32", "low", CX + LSM_DX - 8.9, LSM_Y - 12.75, CX + LSM_DX + 8.9, LSM_Y + 12.75),
        ("BMP388", "low", CX - 12.75, BMP_Y - 8.9, CX + 12.75, BMP_Y + 8.9),   # turned
    ]
    out = {
        "board": {"w": BOARD_W, "h": BOARD_H, "r": CORNER_R, "nose_z0": BOARD_NOSE_Z0},
        "usb_c": [{"x0": CX - 4.0, "y0": CAM_Y - 11.7, "x1": CX + 4.0, "y1": CAM_Y - 10.5},
                  {"x0": CX - 11.7, "y0": LORA_Y - 4.0, "x1": CX - 10.5, "y1": LORA_Y + 4.0}],
        "bodies": [dict(zip(("name", "side", "x0", "y0", "x1", "y1"), b)) for b in bodies],
        "standoffs": [{"x": x, "y": y, "r": STANDOFF_R} for x, y in STANDOFFS],
        "bmp_spacers": [{"x": x, "y": y, "r": BMP_SPACER_R} for x, y in bmp_spacers()],
        "buzzer": {"x": BUZ_XY[0], "y": BUZ_XY[1], "r": BUZ_R},
        "battery": {"x0": CX - BATTERY_HALF_W, "y0": BATTERY_Y[0],
                    "x1": CX + BATTERY_HALF_W, "y1": BATTERY_Y[1],
                    "r0": BATTERY_R[0], "r1": BATTERY_R[1]},
        "pads": sorted(pads, key=lambda p: (p["ref"], p["num"])),
    }
    with open(LAYOUT, "w") as f:
        json.dump(out, f, indent=1)
        f.write("\n")
    print("wrote    %s" % LAYOUT)


def write_rules():
    """The DRC rules file beside the board. Empty since the Wuerth SMT standoffs
    left (2026-10-17): their land pattern was the project's one exception."""
    with open(OUT.replace(".kicad_pcb", ".kicad_dru"), "w") as f:
        f.write('(version 1)\n')


def main():
    board = pcbnew.CreateEmptyBoard()
    board.SetCopperLayerCount(COPPER_LAYERS)
    board.GetDesignSettings().SetBoardThickness(MM(THICKNESS))

    board.nets = {}
    for name in ("GND", "+3V3", "+3V3_LORA", "GPS_TX", "GPS_RX", "SDA", "SCL",
                 "BUZZER", "BUZZER_B", "LINK_GPS", "LINK_EVT", "GPS_CAM", "EVT_CAM", "EVT_LORA"):
        n = pcbnew.NETINFO_ITEM(board, name)
        board.Add(n)
        board.nets[name] = n

    outline(board, BOARD_W, BOARD_H, CORNER_R)
    for ref, cy, signals, turned in XIAOS:
        add_xiao(board, ref, cy, signals, turned)
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
