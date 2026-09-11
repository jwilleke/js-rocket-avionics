#!/usr/bin/env python3
"""Draw both sides of the carrier board, dimensioned, from gen_carrier.py's layout.

    python3 hardware/scripts/gen_carrier_diagram.py

Reads hardware/PCB-carrier/PCB-carrier-layout.json and writes
hardware/PCB-carrier/PCB-carrier-layout.svg, which PCB-carrier.md embeds.

WHERE THE NUMBERS COME FROM. Every pad position is pcbnew's own, exported by
gen_carrier.py after its pin and clearance checks pass; the part outlines are
the constants that placed those parts. This script adds no geometry of its own,
so the picture cannot drift from the board.

ONE BOARD, TWO SIDES. The tall side (both XIAO stacks, the L76K-GNSS, the JST)
faces 270 deg, the camera port. The low side (both sensors, two M3 standoffs)
faces 90 deg, the web. Each panel is drawn as seen by someone looking AT that
side with forward (the nose tip) up, so the two panels are mirror images of
each other left to right. Through-holes appear on both; the other side's parts
are drawn faint, so what sits behind what can be read straight across.
"""

import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "hardware", "PCB-carrier", "PCB-carrier-layout.json")
OUT = os.path.join(REPO, "hardware", "PCB-carrier", "PCB-carrier-layout.svg")

S = 6.5                         # px per mm
OY = 150
PANELS = {"tall": 150, "low": 470}
INK, NOTE, DIM = "#1b1b1b", "#5b5b5b", "#2f5fcc"
BOARD_BG, BOARD_ED = "#e9f1e4", "#5f7f52"
SIDE_COLOUR = {"tall": "#9a3412", "low": "#1d6b3f"}
STANDOFF = "#b7791f"
NET_COLOUR = {"+3V3": "#cc2f2f", "+3V3_LORA": "#f08a4b", "GND": "#222222", "VBAT": "#e03b3b",
              "SDA": "#2f5fcc", "SCL": "#d99b00", "BUZZER": "#6f6f6f", "GPS_TX": "#1d8a4a",
              "GPS_RX": "#7a3fb5"}
XIAO_LABELS = {"A": ["D0", "D1", "D2", "D3", "D4", "D5", "D6"],
               "B": ["D7", "D8", "D9", "D10", "3V3", "GND", "5V"]}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Svg:
    def __init__(self):
        self.out = []

    def add(self, s):
        self.out.append(s)

    def text(self, x, y, s, size=11, fill=INK, anchor="start", weight="normal"):
        self.add('<text x="%.1f" y="%.1f" font-size="%.1f" fill="%s" text-anchor="%s" '
                 'font-weight="%s">%s</text>' % (x, y, size, fill, anchor, weight, esc(s)))

    def line(self, x1, y1, x2, y2, stroke=INK, w=1.0, dash=None):
        d = ' stroke-dasharray="%s"' % dash if dash else ""
        self.add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                 'stroke-width="%.1f"%s/>' % (x1, y1, x2, y2, stroke, w, d))

    def rect(self, x, y, w, h, fill="none", stroke=INK, sw=1.0, r=0, opacity=1.0, dash=None):
        d = ' stroke-dasharray="%s"' % dash if dash else ""
        self.add('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%.1f" fill="%s" '
                 'fill-opacity="%.2f" stroke="%s" stroke-width="%.1f"%s/>'
                 % (x, y, w, h, r, fill, opacity, stroke, sw, d))

    def circle(self, x, y, r, fill="none", stroke=INK, sw=1.0, dash=None):
        d = ' stroke-dasharray="%s"' % dash if dash else ""
        self.add('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" stroke="%s" '
                 'stroke-width="%.1f"%s/>' % (x, y, r, fill, stroke, sw, d))


def main():
    L = json.load(open(SRC))
    bw, bh, z0 = L["board"]["w"], L["board"]["h"], L["board"]["nose_z0"]

    def px(side, x):
        # Tall side seen from the front, forward up: KiCad turned 180 deg.
        # Low side seen from the back, forward up: KiCad's x as it is.
        ox = PANELS[side]
        return ox + ((bw - x) if side == "tall" else x) * S

    def py(y):
        return OY + (bh - y) * S

    W, H = 1000, int(OY + bh * S + 110)
    svg = Svg()
    svg.add('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" '
            'font-family="Helvetica, Arial, sans-serif">' % (W, H, W, H))
    svg.rect(0, 0, W, H, "#ffffff", "none", 0)
    svg.text(24, 34, "PCB-carrier — one board, both sides", 18, INK, weight="bold")
    svg.text(24, 54, "Each side drawn as seen from that side, forward (nose tip) up — the panels are mirror "
                     "images. Dashed outlines are parts on the OTHER side of the board.", 11.5, NOTE)
    svg.text(24, 72, "Tall side faces 270° (camera port); low side faces 90° (the web, which the board hangs "
                     "off on two M3 standoffs).", 11.5, NOTE)

    titles = {"tall": ("TALL SIDE — faces 270°", "seen from the camera side"),
              "low": ("LOW SIDE — faces 90°", "seen from the web side")}
    for side in ("tall", "low"):
        x0 = px(side, bw) if side == "tall" else px(side, 0)
        svg.text(x0 + bw * S / 2, OY - 30, titles[side][0], 14, INK, "middle", "bold")
        svg.text(x0 + bw * S / 2, OY - 14, titles[side][1], 10.5, NOTE, "middle")
        svg.rect(x0, py(bh), bw * S, bh * S, BOARD_BG, BOARD_ED, 1.5, L["board"]["r"] * S)

        for b in L["bodies"]:
            mine = b["side"] == side
            c = SIDE_COLOUR[b["side"]]
            xa, xb = sorted((px(side, b["x0"]), px(side, b["x1"])))
            svg.rect(xa, py(b["y1"]), xb - xa, (b["y1"] - b["y0"]) * S,
                     c if mine else "none", c, 1.2 if mine else 0.7, 2,
                     0.18 if mine else 0.0, None if mine else "3,3")
        if side == "tall":
            for u in L["usb_c"]:
                xa, xb = sorted((px(side, u["x0"]), px(side, u["x1"])))
                svg.rect(xa, py(u["y0"]), xb - xa, (u["y0"] - u["y1"]) * S, "#b8b8b8", INK, 0.8)

        for so in L["standoffs"]:
            mine = side == "low"
            svg.circle(px(side, so["x"]), py(so["y"]), so["r"] * S, "#fff4d6" if mine else "none",
                       STANDOFF, 1.3 if mine else 0.7, None if mine else "3,2")
            if mine:
                svg.text(px(side, so["x"]), py(so["y"]) + 4, "M3", 10, STANDOFF, "middle", "bold")
            else:
                svg.text(px(side, so["x"]), py(so["y"]) + 3, "standoff,", 7.5, STANDOFF, "middle")
                svg.text(px(side, so["x"]), py(so["y"]) + 12, "other side", 7.5, STANDOFF, "middle")
        if side == "low":
            for leg in L["bmp_legs"]:
                svg.circle(px(side, leg["x"]), py(leg["y"]), 1.9 * S, "none",
                           SIDE_COLOUR["low"], 1.0, "2,2")

        for p in L["pads"]:
            if p["ref"].startswith("SO"):
                continue
            svg.circle(px(side, p["x"]), py(p["y"]), 0.8 * S,
                       NET_COLOUR.get(p["net"], "#d4af37"), INK, 0.5)
            if side == "tall" and p["ref"][:-1] in ("J_CAM_", "J_LORA_"):
                lab = XIAO_LABELS[p["ref"][-1]][int(p["num"]) - 1]
                right = px(side, p["x"]) > px(side, bw / 2)
                svg.text(px(side, p["x"]) + (11 if right else -11), py(p["y"]) + 3.5, lab, 8,
                         INK, "start" if right else "end")

        for b in L["bodies"]:
            if b["side"] != side:
                continue
            cx = (px(side, b["x0"]) + px(side, b["x1"])) / 2
            cy = py((b["y0"] + b["y1"]) / 2)
            name = "JST" if b["name"] == "JST-PH" else b["name"]
            parts = name.rsplit("-", 1) if name.startswith("XIAO") else [name]
            for i, part in enumerate(parts):
                svg.text(cx, cy + 4 + (i - (len(parts) - 1) / 2) * 13, part,
                         10.5 if name != "JST" else 9, SIDE_COLOUR[side], "middle", "bold")

    # nose z, shared, at the stations that matter
    ys = {0.0, bh} | {s_["y"] for s_ in L["standoffs"]}
    for b in L["bodies"]:
        if b["name"] != "JST-PH":
            ys |= {b["y0"], b["y1"]}
    last = None
    for y in sorted(ys):
        if last is not None and abs(py(y) - last) < 11:
            continue
        last = py(y)
        svg.line(112, py(y), PANELS["tall"], py(y), DIM, 0.5, "2,3")
        svg.text(108, py(y) + 4, "%.1f" % (z0 + y), 10, DIM, "end")
    svg.text(108, OY - 14, "nose z", 10, DIM, "end")
    svg.text(PANELS["tall"] + bw * S / 2, OY + bh * S + 22, "%g × %g mm" % (bw, bh), 10.5, DIM,
             "middle")

    lx, ly = 740, OY + 10
    svg.text(lx, ly, "Pad colour = net", 12, INK, weight="bold")
    for i, (net, c) in enumerate(NET_COLOUR.items()):
        svg.circle(lx + 8, ly + 16 + i * 17, 5, c, INK, 0.5)
        svg.text(lx + 22, ly + 20 + i * 17, net, 10.5, INK)
    yy = ly + 20 + len(NET_COLOUR) * 17 + 16
    for i, line in enumerate((
            "Through-holes pass through, so every",
            "pad shows on both sides.",
            "",
            "M3 standoffs (low side) take M3 plastic",
            "screws from the web's far face — M3 × 10,",
            "which stops short of the board.",
            "",
            "Dashed rings on the low side: the BMP388's",
            "M2 bolt-head legs.",
            "",
            "The sensors stand ~1 mm proud on their",
            "pins, header plastic up against the",
            "sensor, clear of the tall side's joints.")):
        svg.text(lx, yy + i * 15, line, 10, NOTE)

    svg.text(24, H - 18, "Generated by hardware/scripts/gen_carrier_diagram.py from PCB-carrier-layout.json, "
                         "which gen_carrier.py writes. Regenerate, do not edit.", 10, NOTE)
    svg.add("</svg>")
    with open(OUT, "w") as f:
        f.write("\n".join(svg.out) + "\n")
    print("wrote    %s" % OUT)


if __name__ == "__main__":
    main()
