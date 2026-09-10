#!/usr/bin/env python3
"""Draw the bench breadboard layout as an SVG.

    python3 hardware/scripts/gen_breadboard_svg.py

Writes docs/bench-work/bench-breadboard.svg, which docs/bench-wiring.md embeds.
XIAO-ESP32S3-lora's own board is gen_breadboard_lora_svg.py.

WHY THIS IS A SCRIPT AND NOT A DRAWING. The layout has to agree with three
things that move independently: the XIAO pinout in docs/module-pinouts.md, the
sensor pin orders in the same file, and the connection table in
docs/bench-wiring.md. Keeping the placement as data means a pin order can be
corrected in one dict and the picture redrawn, rather than someone editing
paths in a vector editor and quietly disagreeing with the table.

ORIENTATION, which is the easy thing to get wrong. module-pinouts.md reads the
XIAO from the UNDERSIDE with the USB-C at the top: left column 5V..D7, right
column D0..D6. This drawing is from ABOVE with the USB-C at the LEFT, so both
of those change:

    underside, USB up        ->   top view, USB left
    left  5V GND 3V3 D10..D7      TOP edge, left to right:  5V GND 3V3 D10 D9 D8 D7
    right D0 D1 D2 D3 D4 D5 D6    BOTTOM edge, left to right: D0 D1 D2 D3 D4 D5 D6

So D4/D5 -- the I2C pins everything hangs off -- are in the LOWER half of the
board and the 3V3/GND pins are in the UPPER half. That is why the bus wires
cross the centre channel and the power wires do not.
"""

import os

# ---- geometry --------------------------------------------------------------
PITCH = 20                     # one hole pitch, 0.1 in
COLS = 63                      # a full-size breadboard
MARGIN_X = 78
BOARD_TOP = 196

# Row centres, in pitch units below the top edge of the board.
ROW_Y = {
    "+top": 0.7, "-top": 1.7,
    "A": 3.5, "B": 4.5, "C": 5.5, "D": 6.5, "E": 7.5,
    "F": 10.5, "G": 11.5, "H": 12.5, "I": 13.5, "J": 14.5,
    "-bot": 16.3, "+bot": 17.3,
}
BOARD_H = 18.4 * PITCH
BOARD_W = (COLS - 1) * PITCH + 2 * 28

W, H = MARGIN_X * 2 + BOARD_W, 1120
BOARD_BOT = BOARD_TOP + 18.4 * PITCH

# ---- palette ---------------------------------------------------------------
INK       = "#1b1b1b"
BOARD_BG  = "#f4f1ea"
BOARD_ED  = "#cdc6b8"
CHANNEL   = "#e6e1d6"
HOLE      = "#8d8577"
RED       = "#cc2f2f"          # +3V3
BLUE      = "#2f5fcc"          # SDA
BLACK     = "#222222"          # GND
YELLOW    = "#d99b00"          # SCL
GREY      = "#6f6f6f"          # D0, the buzzer
BATT_RED  = "#e03b3b"
XIAO_FILL = "#0f2f4a"
SENSOR    = "#1d6b3f"
NOTE      = "#5b5b5b"

# ---- the layout, as data ---------------------------------------------------
# XIAO-ESP32S3-cam straddles the channel. Seven columns, top edge in row E and
# bottom edge in row F -- see the orientation note at the top of this file.
XIAO_C0 = 7
XIAO_TOP = ["5V", "GND", "3V3", "D10", "D9", "D8", "D7"]
XIAO_BOT = ["D0", "D1", "D2", "D3", "D4", "D5", "D6"]

# Both sensors sit in the upper half with their headers in row B, bodies
# overhanging above the board. Pin orders are module-pinouts.md's, read off the
# parts. Only VIN, GND, SCL and SDA are used; the rest are drawn so the header
# can be counted against the silkscreen.
BMP_C0 = 24
BMP_PINS = ["VIN", "3Vo", "GND", "SCL", "SDO", "SDA", "CS", "INT"]
LSM_C0 = 36
LSM_PINS = ["VIN", "3Vo", "GND", "SCL", "SDA", "DO", "CS", "I1", "I2"]

BUZZ_C = 52                    # piezo, lower half: one leg to D0, one to GND


def col_x(c):
    return MARGIN_X + 28 + (c - 1) * PITCH


def row_y(r):
    return BOARD_TOP + ROW_Y[r] * PITCH


out = []
add = out.append


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, size=11, fill=INK, anchor="start", weight="normal", mono=False,
         halo=False):
    family = "Menlo,Consolas,monospace" if mono else "Helvetica,Arial,sans-serif"
    # halo = a white outline painted behind the glyphs, for labels a jumper
    # crosses. Without it a pin name under a wire is unreadable.
    extra = ' stroke="#ffffff" stroke-width="3.2" paint-order="stroke"' if halo else ""
    add(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" '
        f'font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
        f'font-weight="{weight}"{extra}>{esc(s)}</text>')


def wire(pts, colour, width=3.4, dash=None):
    """A jumper. Drawn as a smooth path so crossings stay readable."""
    d = f"M {pts[0][0]:.1f} {pts[0][1]:.1f}"
    for i in range(1, len(pts)):
        x0, y0 = pts[i - 1]
        x1, y1 = pts[i]
        d += f" L {x1:.1f} {y1:.1f}"
    da = f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="{width}" '
        f'stroke-linecap="round" stroke-linejoin="round"{da}/>')


def arc(p0, p1, colour, bow=52, width=3.4):
    """One jumper, hole to hole, drawn as an arc.

    Right-angled routing reads as a PCB trace and hides the holes it crosses.
    A bowed wire is both what the bench actually looks like and easier to
    follow where two of them cross."""
    (x0, y0), (x1, y1) = p0, p1
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    dx, dy = x1 - x0, y1 - y0
    ln = max((dx * dx + dy * dy) ** 0.5, 1e-6)
    cx, cy = mx - dy / ln * bow, my + dx / ln * bow
    add(f'<path d="M {x0:.1f} {y0:.1f} Q {cx:.1f} {cy:.1f} {x1:.1f} {y1:.1f}" '
        f'fill="none" stroke="{colour}" stroke-width="{width}" stroke-linecap="round"/>')


def plug(x, y, colour):
    """The end of a jumper, pushed into a hole."""
    add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.6" fill="{colour}" '
        f'stroke="#ffffff" stroke-width="1.2"/>')


# ---- canvas ----------------------------------------------------------------
add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
add(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')

text(MARGIN_X, 40, "Bench wiring — js-rocket-avionics #7 and #8", 20, INK, weight="bold")
text(MARGIN_X, 62, "Everything on this board hangs off XIAO-ESP32S3-cam. XIAO-ESP32S3-lora and the L76K are on a second board.", 13, NOTE)
text(MARGIN_X, 80, "Viewed from above, USB-C to the left. The battery never touches the breadboard — see the note at the foot.", 13, NOTE)

# ---- the board -------------------------------------------------------------
bx = MARGIN_X
add(f'<rect x="{bx}" y="{BOARD_TOP}" width="{BOARD_W}" height="{BOARD_H}" rx="7" '
    f'fill="{BOARD_BG}" stroke="{BOARD_ED}" stroke-width="2"/>')

# centre channel
ch_y = BOARD_TOP + 8.4 * PITCH
add(f'<rect x="{bx+4}" y="{ch_y}" width="{BOARD_W-8}" height="{1.6*PITCH}" '
    f'fill="{CHANNEL}"/>')

# rail stripes
for r, colour in (("+top", RED), ("-top", BLUE), ("-bot", BLUE), ("+bot", RED)):
    y = row_y(r)
    add(f'<line x1="{bx+14}" y1="{y}" x2="{bx+BOARD_W-14}" y2="{y}" '
        f'stroke="{colour}" stroke-width="1" opacity="0.45"/>')
    sign = "+" if r.startswith("+") else "−"
    text(bx + 8, y + 4, sign, 13, colour, weight="bold")
    text(bx + BOARD_W - 8, y + 4, sign, 13, colour, anchor="end", weight="bold")

# holes
for c in range(1, COLS + 1):
    for r in ROW_Y:
        if r in ("+top", "-top", "-bot", "+bot") and c % 6 == 0:
            continue                       # rails break every 6 holes, as they do
        add(f'<rect x="{col_x(c)-2.6:.1f}" y="{row_y(r)-2.6:.1f}" width="5.2" height="5.2" '
            f'rx="1.1" fill="none" stroke="{HOLE}" stroke-width="1" opacity="0.55"/>')

# column numbers every 5
for c in range(5, COLS + 1, 5):
    text(col_x(c), BOARD_TOP + 2.9 * PITCH - 4, str(c), 9, NOTE, anchor="middle")
    text(col_x(c), BOARD_TOP + 15.4 * PITCH, str(c), 9, NOTE, anchor="middle")

# row letters
for r in "ABCDE":
    text(bx - 10, row_y(r) + 4, r, 10, NOTE, anchor="end")
for r in "FGHIJ":
    text(bx - 10, row_y(r) + 4, r, 10, NOTE, anchor="end")

# ---- XIAO ------------------------------------------------------------------
x0 = col_x(XIAO_C0) - 13
x1 = col_x(XIAO_C0 + 6) + 13
add(f'<rect x="{x0:.1f}" y="{row_y("E")-14:.1f}" width="{x1-x0:.1f}" '
    f'height="{row_y("F")-row_y("E")+28:.1f}" rx="5" fill="{XIAO_FILL}" opacity="0.93"/>')
text((x0 + x1) / 2, row_y("E") + 30, "XIAO-ESP32S3-cam", 12, "#ffffff", anchor="middle", weight="bold")
text((x0 + x1) / 2, row_y("E") + 46, "Sense board on top", 9.5, "#c9d6e2", anchor="middle")
# USB-C stub
usb_y = (row_y("E") + row_y("F")) / 2 - 9
add(f'<rect x="{x0-16:.1f}" y="{usb_y:.1f}" width="16" height="18" rx="3" fill="#9aa3ab"/>')
text(x0 - 24, (row_y("E") + row_y("F")) / 2 + 4, "USB-C", 9, NOTE, anchor="end")

for i, lbl in enumerate(XIAO_TOP):
    c = XIAO_C0 + i
    plug(col_x(c), row_y("E"), "#dfe6ec")
    text(col_x(c), row_y("E") - 24, lbl, 9, INK, anchor="middle", weight="bold", halo=True)
text(x1 + 14, row_y("F") + 34, "headers point DOWN, into the board", 9.5, NOTE, halo=True)
for i, lbl in enumerate(XIAO_BOT):
    c = XIAO_C0 + i
    plug(col_x(c), row_y("F"), "#dfe6ec")
    text(col_x(c), row_y("F") + 34, lbl, 9, INK, anchor="middle", weight="bold", halo=True)

# ---- sensors ---------------------------------------------------------------
def sensor(c0, pins, name, sub):
    xa = col_x(c0) - 12
    xb = col_x(c0 + len(pins) - 1) + 12
    top = BOARD_TOP - 62
    add(f'<rect x="{xa:.1f}" y="{top}" width="{xb-xa:.1f}" height="46" rx="4" '
        f'fill="{SENSOR}" opacity="0.93"/>')
    text((xa + xb) / 2, top + 20, name, 11, "#ffffff", anchor="middle", weight="bold")
    text((xa + xb) / 2, top + 35, sub, 9, "#cfe6d8", anchor="middle")
    for i, lbl in enumerate(pins):
        c = c0 + i
        used = lbl in ("VIN", "GND", "SCL", "SDA")
        add(f'<line x1="{col_x(c)}" y1="{top+46}" x2="{col_x(c)}" y2="{row_y("B")}" '
            f'stroke="{"#b0b0b0" if not used else "#8a8a8a"}" stroke-width="2"/>')
        plug(col_x(c), row_y("B"), "#dfe6ec" if used else "#eceff1")
        text(col_x(c), top + 60, lbl, 8.5, INK if used else "#9a9a9a",
             anchor="middle", weight="bold" if used else "normal", halo=True)


sensor(BMP_C0, BMP_PINS, "BMP388", "barometer · 0x77")
sensor(LSM_C0, LSM_PINS, "LSM6DSO32", "IMU · 0x6A · Primary row")

# ---- buzzer ----------------------------------------------------------------
bz_x = col_x(BUZZ_C) + PITCH / 2
bz_y = BOARD_BOT + 54
for c in (BUZZ_C, BUZZ_C + 1):
    add(f'<line x1="{col_x(c)}" y1="{bz_y-16}" x2="{col_x(c)}" y2="{row_y("H")}" '
        f'stroke="#8a8a8a" stroke-width="2"/>')
    plug(col_x(c), row_y("H"), "#dfe6ec")
add(f'<circle cx="{bz_x:.1f}" cy="{bz_y:.1f}" r="24" fill="#4a4a4a"/>')
add(f'<circle cx="{bz_x:.1f}" cy="{bz_y:.1f}" r="13" fill="#c9a227"/>')
text(bz_x, bz_y + 44, "PS1240 piezo", 10, INK, anchor="middle", weight="bold")
text(bz_x, bz_y + 57, "bare disc, no + or −", 9, NOTE, anchor="middle")

# ---- jumpers ---------------------------------------------------------------
# power out of the XIAO and onto the top rails
arc((col_x(XIAO_C0 + 2), row_y("A")), (col_x(XIAO_C0 + 2), row_y("+top")), RED, bow=10)
plug(col_x(XIAO_C0 + 2), row_y("A"), RED); plug(col_x(XIAO_C0 + 2), row_y("+top"), RED)
arc((col_x(XIAO_C0 + 1), row_y("A")), (col_x(XIAO_C0 + 1) - 2 * PITCH, row_y("-top")), BLACK, bow=12)
plug(col_x(XIAO_C0 + 1), row_y("A"), BLACK)
plug(col_x(XIAO_C0 + 1) - 2 * PITCH, row_y("-top"), BLACK)

# rails to each sensor
for c0 in (BMP_C0, LSM_C0):
    arc((col_x(c0), row_y("A")), (col_x(c0), row_y("+top")), RED, bow=11)
    plug(col_x(c0), row_y("A"), RED); plug(col_x(c0), row_y("+top"), RED)
    arc((col_x(c0 + 2), row_y("A")), (col_x(c0 + 2), row_y("-top")), BLACK, bow=-11)
    plug(col_x(c0 + 2), row_y("A"), BLACK); plug(col_x(c0 + 2), row_y("-top"), BLACK)

# I2C: D4 = SDA, D5 = SCL, both in the LOWER half, both sensors in the upper.
sda_from = col_x(XIAO_C0 + 4)
scl_from = col_x(XIAO_C0 + 5)
arc((sda_from, row_y("H")), (col_x(BMP_C0 + 5), row_y("D")), BLUE, bow=46)
plug(sda_from, row_y("H"), BLUE); plug(col_x(BMP_C0 + 5), row_y("D"), BLUE)
arc((scl_from, row_y("I")), (col_x(BMP_C0 + 3), row_y("E")), YELLOW, bow=-30)
plug(scl_from, row_y("I"), YELLOW); plug(col_x(BMP_C0 + 3), row_y("E"), YELLOW)

# sensor to sensor -- one bus, two devices
arc((col_x(BMP_C0 + 5), row_y("C")), (col_x(LSM_C0 + 4), row_y("C")), BLUE, bow=26)
plug(col_x(BMP_C0 + 5), row_y("C"), BLUE); plug(col_x(LSM_C0 + 4), row_y("C"), BLUE)
arc((col_x(BMP_C0 + 3), row_y("D")), (col_x(LSM_C0 + 3), row_y("D")), YELLOW, bow=18)
plug(col_x(BMP_C0 + 3), row_y("D"), YELLOW); plug(col_x(LSM_C0 + 3), row_y("D"), YELLOW)

# buzzer: D0 to one leg, GND rail to the other
arc((col_x(XIAO_C0), row_y("G")), (col_x(BUZZ_C), row_y("H")), GREY, bow=-58)
plug(col_x(XIAO_C0), row_y("G"), GREY); plug(col_x(BUZZ_C), row_y("H"), GREY)
arc((col_x(BUZZ_C + 1), row_y("H")), (col_x(BUZZ_C + 1), row_y("-bot")), BLACK, bow=14)
plug(col_x(BUZZ_C + 1), row_y("H"), BLACK); plug(col_x(BUZZ_C + 1), row_y("-bot"), BLACK)

# rail links, so the lower rails carry the same supply as the upper
lk = col_x(COLS - 2)
wire([(lk, row_y("+top")), (lk + 26, row_y("+top")), (lk + 26, row_y("+bot")), (lk, row_y("+bot"))], RED, 3.0)
plug(lk, row_y("+top"), RED); plug(lk, row_y("+bot"), RED)
wire([(lk - PITCH, row_y("-top")), (lk + 14, row_y("-top")), (lk + 14, row_y("-bot")), (lk - PITCH, row_y("-bot"))], BLACK, 3.0)
plug(lk - PITCH, row_y("-top"), BLACK); plug(lk - PITCH, row_y("-bot"), BLACK)

# ---- the battery, deliberately off the board -------------------------------
by = BOARD_BOT + 148
add(f'<rect x="{MARGIN_X}" y="{by}" width="150" height="70" rx="8" fill="#3a3a3a"/>')
text(MARGIN_X + 75, by + 28, "LiPo-500mAh", 12, "#ffffff", anchor="middle", weight="bold")
text(MARGIN_X + 75, by + 44, "3.7 V · 500 mAh", 10, "#c9c9c9", anchor="middle")
text(MARGIN_X + 75, by + 58, "JST-PH, red + / black −", 9, "#c9c9c9", anchor="middle")

lx = MARGIN_X + 150
wire([(lx, by + 26), (lx + 60, by + 26)], BATT_RED, 4)
wire([(lx, by + 48), (lx + 60, by + 48)], BLACK, 4)

add(f'<rect x="{lx+60}" y="{by-14}" width="300" height="110" rx="8" fill="#fff6f6" stroke="{BATT_RED}" stroke-width="2"/>')
text(lx + 74, by + 8, "SOLDERED, not plugged", 12, BATT_RED, weight="bold")
text(lx + 74, by + 26, "red  → BAT+ pad, underside of BOTH XIAOs", 10.5, INK)
text(lx + 74, by + 42, "black → BAT− pad, underside of BOTH XIAOs", 10.5, INK)
text(lx + 74, by + 60, "There is no battery connector on a XIAO, and the", 10, NOTE)
text(lx + 74, by + 74, "pads are unreachable once the expansion board is on.", 10, NOTE)
text(lx + 74, by + 88, "Reversed polarity destroys the module instantly.", 10, BATT_RED)

# The lora stack is on its own 30-row board, with the L76K wired beside it:
# gen_breadboard_lora_svg.py draws that one. From this board it is only the
# other end of the battery junction.
sx = lx + 372
layers = [
    ("XIAO-ESP32S3-lora", "stock Meshtastic · never reflashed", "#0f2f4a"),
    ("Wio-SX1262", "LoRa, on the B2B connector", "#1d4a6b"),
]
for i, (name, sub, fill) in enumerate(layers):
    ly0 = by - 26 + i * 34
    add(f'<rect x="{sx}" y="{ly0}" width="248" height="30" rx="5" fill="{fill}" opacity="0.95"/>')
    text(sx + 10, ly0 + 13, name, 10.5, "#ffffff", weight="bold")
    text(sx + 10, ly0 + 25, sub, 8.5, "#c9d6e2")

text(sx, by + 62, "On its OWN 30-row board, with the L76K beside it:", 9.5, INK, weight="bold")
text(sx, by + 75, "docs/bench-work/bench-breadboard-lora.svg.", 9.5, NOTE)
text(sx, by + 92, "From this board it is only the other end of the battery", 9.5, NOTE)
text(sx, by + 105, "junction. No jumper between the two boards' rails.", 9.5, NOTE)
wire([(lx + 360, by + 40), (sx, by + 40)], BATT_RED, 3.2, dash="7 5")

# ---- legend ----------------------------------------------------------------
ly = by + 214
text(MARGIN_X, ly, "How the holes are joined", 13, INK, weight="bold")
gx = MARGIN_X
gy = ly + 16
add(f'<rect x="{gx}" y="{gy}" width="250" height="86" rx="6" fill="{BOARD_BG}" stroke="{BOARD_ED}"/>')
for i in range(5):
    for j in range(5):
        add(f'<rect x="{gx+22+i*22:.1f}" y="{gy+16+j*13:.1f}" width="5.2" height="5.2" rx="1.1" '
            f'fill="none" stroke="{HOLE}"/>')
add(f'<rect x="{gx+18}" y="{gy+10}" width="14" height="66" rx="4" fill="{BLUE}" opacity="0.16" stroke="{BLUE}"/>')
text(gx, gy + 104, "a column of five is one node — a jumper one row", 10, INK)
text(gx, gy + 117, "down from a pin is the same connection", 10, INK)
add(f'<rect x="{gx+142}" y="{gy+14}" width="96" height="12" rx="4" fill="{RED}" opacity="0.16" stroke="{RED}"/>')
text(gx + 142, gy + 46, "a rail runs the whole", 10, INK)
text(gx + 142, gy + 59, "length, and is split in", 10, INK)
text(gx + 142, gy + 72, "the middle on some", 10, INK)
text(gx + 142, gy + 85, "boards — bridge it", 10, INK)

kx = gx + 300
text(kx, ly, "Wire colours", 13, INK, weight="bold")
for i, (colour, lbl) in enumerate((
        (RED, "+3V3 — out of the XIAO's pin 12, then to both sensors"),
        (BLACK, "GND — the XIAO's pin 13, the sensors, the buzzer"),
        (BLUE, "SDA — D4. One wire, both sensors"),
        (YELLOW, "SCL — D5. One wire, both sensors"),
        (GREY, "D0 — drives the piezo directly. No supply wire"),
        (BATT_RED, "battery — soldered to BAT pads, never to the board"))):
    y = ly + 22 + i * 18
    add(f'<line x1="{kx}" y1="{y-4}" x2="{kx+30}" y2="{y-4}" stroke="{colour}" stroke-width="3.6" stroke-linecap="round"/>')
    text(kx + 40, y, lbl, 10.5, INK)

ox = kx + 470
text(ox, ly, "Optional — battery voltage for soak-power", 13, INK, weight="bold")
text(ox, ly + 20, "Without it every reset is still caught and named.", 10, NOTE)
text(ox, ly + 34, "With it the CSV also carries the shape of the sag.", 10, NOTE)
add(f'<rect x="{ox}" y="{ly+46}" width="300" height="76" rx="6" fill="#fbfbf8" stroke="{BOARD_ED}"/>')
text(ox + 14, ly + 68, "BAT+ ──[100k]──┬──[100k]── GND", 12, INK, mono=True)
text(ox + 14, ly + 88, "               └── D1  (pin 2)", 12, INK, mono=True)
text(ox + 14, ly + 110, "-DSOAK_VBAT_PIN=2 -DSOAK_VBAT_DIVIDER=2.0f", 9.5, NOTE, mono=True)

text(MARGIN_X, H - 18, "Generated by hardware/scripts/gen_breadboard_svg.py — edit the script, not the SVG. "
                       "Pin orders from docs/module-pinouts.md; connections from docs/bench-wiring.md.", 10, NOTE)

add("</svg>")

here = os.path.dirname(os.path.abspath(__file__))
dest = os.path.normpath(os.path.join(here, "..", "..", "docs", "bench-work", "bench-breadboard.svg"))
with open(dest, "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")
print(f"wrote {dest}")
