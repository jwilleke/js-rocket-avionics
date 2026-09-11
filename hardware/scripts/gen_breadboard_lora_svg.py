#!/usr/bin/env python3
"""Draw XIAO-ESP32S3-lora's bench breadboard as an SVG.

    python3 hardware/scripts/gen_breadboard_lora_svg.py

Writes docs/bench-work/bench-breadboard-lora.svg, which docs/bench-wiring.md
embeds beside the cam board's bench-breadboard.svg.

WHY A SECOND BOARD. The bench is two 30-row boards, one XIAO each
(bench-work/bench-breadbooards.jpg). The L76K left the XIAO stack on 2026-09-09
and mounts flat on the carrier, so on the bench it sits on the lora board and
is wired to the lora XIAO like any other module. Nothing joins the two boards
but the battery junction.

Same palette and drawing idioms as gen_breadboard_svg.py, which draws the cam
board. That script is a flat top-level program rather than a library, so the
few helpers are repeated here rather than imported.

ORIENTATION, twice over. Drawn from ABOVE, USB-C to the LEFT, as the cam
drawing is. The XIAO reads as in that drawing: top edge 5V..D7, bottom edge
D0..D6.

The L76K is the trap. Its 14 pads are the XIAO's pattern, but component side
up it shows the pattern a XIAO shows from its BACK (L76K-GNSS.md, from Seeed's
schematic and pinout). Turned with its antenna end facing the XIAO, its top
edge reads TX(D7) D8 D9 D10 3V3 GND 5V and its bottom edge RX(D6) D5..D1
WAKE(D0). That puts every wire on the same side of the channel as the XIAO pin
it comes from, and none of them crosses.
"""

import os

# ---- geometry, as gen_breadboard_svg.py -------------------------------------
PITCH = 20
COLS = 30                      # the 30-row A-J boards actually on the bench
MARGIN_X = 78
BOARD_TOP = 120
ROW_Y = {
    "+top": 0.7, "-top": 1.7,
    "A": 3.5, "B": 4.5, "C": 5.5, "D": 6.5, "E": 7.5,
    "F": 10.5, "G": 11.5, "H": 12.5, "I": 13.5, "J": 14.5,
    "-bot": 16.3, "+bot": 17.3,
}
BOARD_H = 18.4 * PITCH
BOARD_W = (COLS - 1) * PITCH + 2 * 28
BOARD_BOT = BOARD_TOP + BOARD_H
W, H = 1010, 930

# ---- palette, as gen_breadboard_svg.py ---------------------------------------
INK = "#1b1b1b"
BOARD_BG = "#f4f1ea"
BOARD_ED = "#cdc6b8"
CHANNEL = "#e6e1d6"
HOLE = "#8d8577"
RED = "#cc2f2f"                # +3V3
BLACK = "#222222"              # GND
GREEN = "#1d8a4a"              # D6 -> the L76K's RX
PURPLE = "#7a3fb5"             # D7 <- the L76K's TX
BATT_RED = "#e03b3b"
XIAO_FILL = "#0f2f4a"
GNSS_FILL = "#1d4a6b"
NOTE = "#5b5b5b"

# ---- the layout, as data -------------------------------------------------------
XIAO_C0 = 4
XIAO_TOP = ["5V", "GND", "3V3", "D10", "D9", "D8", "D7"]
XIAO_BOT = ["D0", "D1", "D2", "D3", "D4", "D5", "D6"]

# L76K V1.1 (the part in hand, operator 2026-09-11), component side up, antenna
# end to the LEFT (facing the XIAO). Labels are the function where the pad has
# one, else the XIAO position it meets. On V1.0, RST sat at D10 instead of D2.
L76K_C0 = 15
L76K_TOP = ["TX", "D8", "D9", "D10", "3V3", "GND", "5V"]
L76K_BOT = ["RX", "D5", "D4", "D3", "RST", "D1", "WAKE"]
L76K_USED = {"TX", "RX", "3V3", "GND"}


def col_x(c):
    return MARGIN_X + 28 + (c - 1) * PITCH


def row_y(r):
    return BOARD_TOP + ROW_Y[r] * PITCH


out = []
add = out.append


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, size=11, fill=INK, anchor="start", weight="normal", halo=False):
    extra = ' stroke="#ffffff" stroke-width="3.2" paint-order="stroke"' if halo else ""
    add(f'<text x="{x:.1f}" y="{y:.1f}" font-family="Helvetica,Arial,sans-serif" '
        f'font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
        f'font-weight="{weight}"{extra}>{esc(s)}</text>')


def wire(pts, colour, width=3.4, dash=None):
    d = f"M {pts[0][0]:.1f} {pts[0][1]:.1f}" + "".join(
        f" L {x:.1f} {y:.1f}" for x, y in pts[1:])
    da = f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="{width}" '
        f'stroke-linecap="round" stroke-linejoin="round"{da}/>')


def arc(p0, p1, colour, bow=52, width=3.4):
    (x0, y0), (x1, y1) = p0, p1
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    dx, dy = x1 - x0, y1 - y0
    ln = max((dx * dx + dy * dy) ** 0.5, 1e-6)
    cx, cy = mx - dy / ln * bow, my + dx / ln * bow
    add(f'<path d="M {x0:.1f} {y0:.1f} Q {cx:.1f} {cy:.1f} {x1:.1f} {y1:.1f}" '
        f'fill="none" stroke="{colour}" stroke-width="{width}" stroke-linecap="round"/>')


def plug(x, y, colour):
    add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.6" fill="{colour}" '
        f'stroke="#ffffff" stroke-width="1.2"/>')


def jumper(c0, r0, c1, r1, colour, bow):
    arc((col_x(c0), row_y(r0)), (col_x(c1), row_y(r1)), colour, bow)
    plug(col_x(c0), row_y(r0), colour)
    plug(col_x(c1), row_y(r1), colour)


def module(c0, top, bot, fill, name, sub, used=None):
    """A 14-pad module straddling the channel: pins in rows E and F."""
    x0 = col_x(c0) - 13
    x1 = col_x(c0 + 6) + 13
    add(f'<rect x="{x0:.1f}" y="{row_y("E")-14:.1f}" width="{x1-x0:.1f}" '
        f'height="{row_y("F")-row_y("E")+28:.1f}" rx="5" fill="{fill}" opacity="0.93"/>')
    text((x0 + x1) / 2, row_y("E") + 30, name, 12, "#ffffff", anchor="middle", weight="bold")
    text((x0 + x1) / 2, row_y("E") + 46, sub, 9.5, "#c9d6e2", anchor="middle")
    for row, labels, dy in (("E", top, -24), ("F", bot, 34)):
        for i, lbl in enumerate(labels):
            live = used is None or lbl in used
            plug(col_x(c0 + i), row_y(row), "#dfe6ec" if live else "#eceff1")
            text(col_x(c0 + i), row_y(row) + dy, lbl, 9, INK if live else "#9a9a9a",
                 anchor="middle", weight="bold" if live else "normal", halo=True)
    return x0, x1


# ---- canvas ----------------------------------------------------------------
add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
add(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')

text(MARGIN_X, 40, "Bench wiring — XIAO-ESP32S3-lora's board", 20, INK, weight="bold")
text(MARGIN_X, 62, "The second 30-row board. The L76K sits here and is wired to the lora XIAO; "
                   "nothing joins this board to the cam board but the battery.", 13, NOTE)
text(MARGIN_X, 80, "Viewed from above, USB-C to the left. Four jumpers: 3V3, GND, and the UART on D6/D7.",
     13, NOTE)

# ---- the board -------------------------------------------------------------
bx = MARGIN_X
add(f'<rect x="{bx}" y="{BOARD_TOP}" width="{BOARD_W}" height="{BOARD_H}" rx="7" '
    f'fill="{BOARD_BG}" stroke="{BOARD_ED}" stroke-width="2"/>')
ch_y = BOARD_TOP + 8.4 * PITCH
add(f'<rect x="{bx+4}" y="{ch_y}" width="{BOARD_W-8}" height="{1.6*PITCH}" fill="{CHANNEL}"/>')
for r, colour in (("+top", RED), ("-top", "#2f5fcc"), ("-bot", "#2f5fcc"), ("+bot", RED)):
    y = row_y(r)
    add(f'<line x1="{bx+14}" y1="{y}" x2="{bx+BOARD_W-14}" y2="{y}" '
        f'stroke="{colour}" stroke-width="1" opacity="0.45"/>')
    sign = "+" if r.startswith("+") else "−"
    text(bx + 8, y + 4, sign, 13, colour, weight="bold")
    text(bx + BOARD_W - 8, y + 4, sign, 13, colour, anchor="end", weight="bold")
for c in range(1, COLS + 1):
    for r in ROW_Y:
        if r in ("+top", "-top", "-bot", "+bot") and c % 6 == 0:
            continue
        add(f'<rect x="{col_x(c)-2.6:.1f}" y="{row_y(r)-2.6:.1f}" width="5.2" height="5.2" '
            f'rx="1.1" fill="none" stroke="{HOLE}" stroke-width="1" opacity="0.55"/>')
for c in range(5, COLS + 1, 5):
    text(col_x(c), BOARD_TOP + 2.9 * PITCH - 4, str(c), 9, NOTE, anchor="middle")
    text(col_x(c), BOARD_TOP + 15.4 * PITCH, str(c), 9, NOTE, anchor="middle")
for r in "ABCDEFGHIJ":
    text(bx - 10, row_y(r) + 4, r, 10, NOTE, anchor="end")

# ---- modules ----------------------------------------------------------------
x0, _ = module(XIAO_C0, XIAO_TOP, XIAO_BOT, XIAO_FILL, "XIAO-ESP32S3-lora",
               "Wio-SX1262 on top")
usb_y = (row_y("E") + row_y("F")) / 2 - 9
add(f'<rect x="{x0-16:.1f}" y="{usb_y:.1f}" width="16" height="18" rx="3" fill="#9aa3ab"/>')
text(x0 - 22, (row_y("E") + row_y("F")) / 2 + 4, "USB-C", 9, NOTE, anchor="end")

lx0, lx1 = module(L76K_C0, L76K_TOP, L76K_BOT, GNSS_FILL, "L76K GNSS",
                  "component side up", L76K_USED)
ufl_y = (row_y("E") + row_y("F")) / 2
add(f'<rect x="{lx0+4:.1f}" y="{ufl_y-6:.1f}" width="12" height="12" rx="2" fill="#c9a227"/>')
text(lx0 + 10, ufl_y + 18, "U.FL", 8, "#ffffff", anchor="middle")

# ---- jumpers ------------------------------------------------------------------
# Power out of the XIAO onto the top rails, and off them into the L76K.
jumper(XIAO_C0 + 2, "A", XIAO_C0 + 2, "+top", RED, 10)
jumper(XIAO_C0 + 1, "A", XIAO_C0 + 1, "-top", BLACK, -10)
jumper(L76K_C0 + 4, "A", L76K_C0 + 4, "+top", RED, 10)
jumper(L76K_C0 + 5, "A", L76K_C0 + 5, "-top", BLACK, -10)
# UART. The XIAO's D7 listens to the module's TX; its D6 talks to the module's RX.
jumper(XIAO_C0 + 6, "C", L76K_C0, "C", PURPLE, -34)
jumper(XIAO_C0 + 6, "H", L76K_C0, "H", GREEN, 34)

# ---- off-board: antennas and battery ---------------------------------------------
ax = col_x(L76K_C0) - 6
wire([(lx0 + 10, ufl_y + 6), (lx0 + 10, BOARD_BOT + 40), (ax + 60, BOARD_BOT + 40)], "#8a8a8a", 2)
add(f'<rect x="{ax+60}" y="{BOARD_BOT+26}" width="30" height="30" rx="3" fill="#7a7a7a"/>')
text(ax + 98, BOARD_BOT + 38, "GPS patch, on its U.FL lead", 10, INK, weight="bold")
text(ax + 98, BOARD_BOT + 52, "facing up, nothing metal above it", 9.5, NOTE)
text(col_x(XIAO_C0), BOARD_BOT + 38, "LoRa antenna: on the Wio-SX1262's", 10, INK, weight="bold")
text(col_x(XIAO_C0), BOARD_BOT + 52, "own U.FL, never on this board", 9.5, NOTE)
text(col_x(XIAO_C0), BOARD_BOT + 72, "Both antennas go on the payload sled in flight, ≥50 mm apart (#14).", 9.5, NOTE)

by = BOARD_BOT + 110
add(f'<rect x="{MARGIN_X}" y="{by}" width="150" height="70" rx="8" fill="#3a3a3a"/>')
text(MARGIN_X + 75, by + 28, "LiPo-500mAh", 12, "#ffffff", anchor="middle", weight="bold")
text(MARGIN_X + 75, by + 44, "the same battery as", 10, "#c9c9c9", anchor="middle")
text(MARGIN_X + 75, by + 58, "the cam board's", 10, "#c9c9c9", anchor="middle")
bl = MARGIN_X + 150
wire([(bl, by + 26), (bl + 60, by + 26)], BATT_RED, 4)
wire([(bl, by + 48), (bl + 60, by + 48)], BLACK, 4)
add(f'<rect x="{bl+60}" y="{by-14}" width="330" height="98" rx="8" fill="#fff6f6" '
    f'stroke="{BATT_RED}" stroke-width="2"/>')
text(bl + 74, by + 8, "SOLDERED to this XIAO's underside BAT pads", 12, BATT_RED, weight="bold")
text(bl + 74, by + 26, "one junction with the cam's pigtails — the only link", 10.5, INK)
text(bl + 74, by + 42, "between the two boards. No jumper between their rails.", 10.5, INK)
text(bl + 74, by + 62, "Battery connected: USB on ONE board only, never both.", 10.5, BATT_RED, weight="bold")
text(bl + 74, by + 76, "LiPo-500mAh.md, \"Two chargers on one battery\".", 9.5, NOTE)

# ---- notes and legend ------------------------------------------------------------
nx = MARGIN_X + BOARD_W + 36
text(nx, BOARD_TOP + 10, "Two traps on this board", 13, INK, weight="bold")
for i, line in enumerate((
        "1  The L76K is NOT the XIAO's twin. Component",
        "   side up its pins are mirrored against the",
        "   XIAO beside it. Seat it from these labels,",
        "   not by copying the XIAO.",
        "",
        "2  Wire by position, not by the silkscreen word.",
        "   The XIAO's D6 is its TRANSMIT; it goes to the",
        "   pad Seeed labels RX. TX to TX is the mistake.",
        "",
        "Left open, on purpose: 5V (connects to nothing",
        "on the module), RESET and WAKE (pulled up on",
        "the module behind diodes), and every other pad.")):
    text(nx, BOARD_TOP + 32 + i * 16, line, 10.5, NOTE if i >= 9 else INK)

ly = by + 130
text(MARGIN_X, ly, "Wire colours", 13, INK, weight="bold")
for i, (colour, lbl) in enumerate((
        (RED, "+3V3 — XIAO pin 12 to the top rail, rail to the L76K's 3V3"),
        (BLACK, "GND — XIAO pin 13 to the top rail, rail to the L76K's GND"),
        (GREEN, "D6 → the L76K's RX. The carrier calls this net GPS_TX"),
        (PURPLE, "D7 ← the L76K's TX. The carrier calls this net GPS_RX"),
        (BATT_RED, "battery — soldered to BAT pads, never to the board"))):
    y = ly + 22 + i * 18
    add(f'<line x1="{MARGIN_X}" y1="{y-4}" x2="{MARGIN_X+30}" y2="{y-4}" stroke="{colour}" '
        f'stroke-width="3.6" stroke-linecap="round"/>')
    text(MARGIN_X + 40, y, lbl, 10.5, INK)

text(MARGIN_X, H - 18, "Generated by hardware/scripts/gen_breadboard_lora_svg.py — edit the script, not the SVG. "
                       "L76K pins from hardware/L76K-GNSS/L76K-GNSS.md; connections from docs/bench-wiring.md.",
     10, NOTE)
add("</svg>")

here = os.path.dirname(os.path.abspath(__file__))
dest = os.path.normpath(os.path.join(here, "..", "..", "docs", "bench-work", "bench-breadboard-lora.svg"))
with open(dest, "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")
print(f"wrote {dest}")
