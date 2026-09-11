#!/usr/bin/env python3
"""Draw the carrier as a dimensioned two-face diagram.

    python3 hardware/scripts/gen_carrier_diagram.py

Writes hardware/PCB-carrier/PCB-carrier-layout.svg, which PCB-carrier.md embeds.

WHAT IT DRAWS: only what is fixed today -- the outline, the four mounting holes,
both XIAO positions, their header strips, the USB-C ends and the underside BAT
pads -- plus the free length left on each face. Sensors, buzzer, L76K and JST
are unplaced (#14, stage 2c), so they appear as numbers, not shapes. The
battery is not on the carrier at all: it rides the PayloadSled, forward of it.

WHERE THE NUMBERS COME FROM. Holes, header positions and the outline are read
out of PCB-carrier.kicad_pcb, so the picture follows the board. The XIAO outline,
USB-C tab and BAT pads come from KiCad's RF_Module:MCU_Seeed_ESP32C3, the same
footprint gen_carrier.py takes its pad grid from:

    board      x +/-8.9, y +/-10.5            (17.8 x 21 mm)
    USB-C      x +/-4.0, out to y -11.7       (1.2 mm past the edge)
    pad 16     (-4.5, -0.4), 2.3 x 1.3        BAT+
    pad 17     (-4.5, -2.3), 2.3 x 1.3        BAT-

Footprint y is negative toward the USB-C, and the USB-C faces aft
(module-pinouts.md), so carrier y = centre y + footprint y.

ORIENTATION, which is the trap. Each face is drawn as seen by someone looking
AT that face, forward up. Looking at the top face with forward up puts carrier
x = 0 on the RIGHT; turning the board over about its long axis to look at the
bottom face puts it on the LEFT. Drawn that way, each XIAO is seen from its own
front and the two look identical: D0..D6 down the right side, 5V at the
bottom left, the BAT pads 4.5 mm right of centre and just aft of it.

The board has to agree, and main() asserts it does: in both views the header
carrying pins 1..7 (reference suffix "A") must sit on the right. #21 was the
board getting this wrong for the bottom-face module, netting it as if it were
top-mounted.
"""

import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PCB = os.path.join(REPO, "hardware", "PCB-carrier", "PCB-carrier.kicad_pcb")
OUT = os.path.join(REPO, "hardware", "PCB-carrier", "PCB-carrier-layout.svg")

# ---- design knowledge the board file does not carry --------------------------
XIAOS = {                       # header reference prefix -> (page name, face)
    "J_XIAO_A": ("XIAO-ESP32S3-lora", "top"),
    "J_XIAO_B": ("XIAO-ESP32S3-cam", "bottom"),
}
XIAO_HW, XIAO_HL, XIAO_R = 8.9, 10.5, 2.2
USB_HW, USB_OUT = 4.0, 11.7
BAT_PADS = [("BAT+", -4.5, -0.4), ("BAT−", -4.5, -2.3)]
BAT_W, BAT_H = 2.3, 1.3
HEADER_W, HEADER_L = 2.54, 7 * 2.54
PITCH = 2.54
# Front view, USB-C down: pin 1 at the bottom right, 14 at the bottom left.
RIGHT_COL = ["D0", "D1", "D2", "D3", "D4", "D5", "D6"]
LEFT_COL = ["5V", "GND", "3V3", "D10", "D9", "D8", "D7"]
UNPLACED = {
    "top": "L76K ~21, and the JST toward the forward end",
    "bottom": "LSM6DSO32 25.5 + BMP388 25.5 + buzzer ~12 = 63",
}

# ---- drawing constants --------------------------------------------------------
S = 7.0                         # px per mm
PANEL_W = 580
TOP_Y = 110
INK, NOTE = "#1b1b1b", "#5b5b5b"
BOARD_BG, BOARD_ED = "#e9f1e4", "#5f7f52"
XIAO_FILL, HEADER = "#0f2f4a", "#9a9a9a"
DIM, ZONE = "#2f5fcc", "#d99b00"
PAD = "#e03b3b"


def read_board():
    """Outline extent, mounting holes and header positions from the .kicad_pcb."""
    text = open(PCB).read()
    xs, ys = [], []
    for m in re.finditer(r"\(gr_(?:line|arc)(.*?)\(layer \"Edge\.Cuts\"\)", text, re.S):
        for x, y in re.findall(r"\((?:start|end|mid) ([-\d.]+) ([-\d.]+)\)", m.group(1)):
            xs.append(float(x))
            ys.append(float(y))
    holes, headers = [], {}
    for m in re.finditer(r'\(footprint "([^"]+)".*?\(at ([-\d.]+) ([-\d.]+)'
                         r'.*?\(property "Reference" "([^"]+)"', text, re.S):
        name, x, y, ref = m.group(1), float(m.group(2)), float(m.group(3)), m.group(4)
        if name.startswith("MountingHole"):
            holes.append((x, y))
        elif name.startswith("PinHeader"):
            headers.setdefault(ref[:-1], []).append((x, y, ref[-1]))
    return max(xs) - min(xs), max(ys) - min(ys), holes, headers


class Svg:
    def __init__(self):
        self.out = []

    def add(self, s):
        self.out.append(s)

    def text(self, x, y, s, size=12, fill=INK, anchor="start", weight="normal", italic=False):
        style = ' font-style="italic"' if italic else ""
        self.add('<text x="%.1f" y="%.1f" font-size="%d" fill="%s" text-anchor="%s" '
                 'font-weight="%s"%s>%s</text>' % (x, y, size, fill, anchor, weight, style, s))

    def line(self, x1, y1, x2, y2, stroke=INK, w=1.0, dash=None, marker=False):
        d = ' stroke-dasharray="%s"' % dash if dash else ""
        m = ' marker-end="url(#arrow)"' if marker else ""
        self.add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                 'stroke-width="%.1f"%s%s/>' % (x1, y1, x2, y2, stroke, w, d, m))

    def rect(self, x, y, w, h, fill="none", stroke=INK, sw=1.0, r=0, dash=None):
        d = ' stroke-dasharray="%s"' % dash if dash else ""
        self.add('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%.1f" fill="%s" '
                 'stroke="%s" stroke-width="%.1f"%s/>' % (x, y, w, h, r, fill, stroke, sw, d))

    def circle(self, x, y, r, fill="none", stroke=INK, sw=1.0):
        self.add('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" stroke="%s" '
                 'stroke-width="%.1f"/>' % (x, y, r, fill, stroke, sw))


def vdim(svg, x, y0, y1, label, side=-1, color=DIM):
    """Vertical dimension between page y0 and y1, label to the given side."""
    svg.line(x, y0, x, y1, color, 1)
    for y in (y0, y1):
        svg.line(x - 4, y, x + 4, y, color, 1)
    svg.text(x + side * 6, (y0 + y1) / 2 + 4, label, 11, color, "end" if side < 0 else "start")


def panel(svg, ox, face, bw, bh, holes, headers):
    def px(u):                  # view x in mm -> page
        return ox + u * S

    def py(y):                  # carrier y in mm -> page, forward up
        return TOP_Y + (bh - y) * S

    def vx(cx):                 # carrier x -> view x for this face
        return bw - cx if face == "top" else cx

    mine = [(ref, v) for ref, v in XIAOS.items() if v[1] == face][0]
    other = [(ref, v) for ref, v in XIAOS.items() if v[1] != face][0]
    ref, (name, _) = mine
    cy = headers[ref][0][1]
    ocy = headers[other[0]][0][1]
    oname = other[1][0]

    title = "TOP FACE" if face == "top" else "BOTTOM FACE"
    how = ("looking at the top face" if face == "top"
           else "board turned over about its long axis")
    svg.text(px(bw / 2), 40, title, 17, INK, "middle", "bold")
    svg.text(px(bw / 2), 58, how, 12, NOTE, "middle")
    svg.text(px(bw / 2), TOP_Y - 26, "↑ FORWARD (nose tip)", 12, NOTE, "middle")
    svg.text(px(bw / 2), py(0) + 44, "↓ AFT", 12, NOTE, "middle")

    # Board.
    svg.rect(px(0), py(bh), bw * S, bh * S, BOARD_BG, BOARD_ED, 1.5, 2 * S)
    x0 = px(bw) if face == "top" else px(0)
    svg.text(x0, py(0) + 16, "x = 0 edge", 10, NOTE, "end" if face == "top" else "start")
    for hx, hy in holes:
        svg.circle(px(vx(hx)), py(hy), 1.1 * S, "#ffffff", INK, 1)

    # The other face's XIAO, as a ghost: its header holes pass through this face.
    svg.rect(px(bw / 2 - XIAO_HW), py(ocy + XIAO_HL), 2 * XIAO_HW * S, 2 * XIAO_HL * S,
             "none", NOTE, 1, XIAO_R * S, "5,4")
    svg.text(px(bw / 2), py(ocy) - 4, oname, 11, NOTE, "middle", italic=True)
    svg.text(px(bw / 2), py(ocy) + 11, "on the other face", 11, NOTE, "middle", italic=True)

    # This face's XIAO.
    svg.rect(px(bw / 2 - USB_HW), py(cy - XIAO_HL), 2 * USB_HW * S, (USB_OUT - XIAO_HL) * S,
             "#b8b8b8", INK, 1)
    svg.rect(px(bw / 2 - XIAO_HW), py(cy + XIAO_HL), 2 * XIAO_HW * S, 2 * XIAO_HL * S,
             XIAO_FILL, INK, 1.2, XIAO_R * S)
    for hx, _, _ in headers[ref]:
        u = vx(hx)
        svg.rect(px(u - HEADER_W / 2), py(cy + HEADER_L / 2), HEADER_W * S, HEADER_L * S,
                 HEADER, INK, 0.8)
    for i in range(7):
        y = cy - 3 * PITCH + i * PITCH      # i = 0 is the USB end
        for u, lab, anchor, dx in ((bw / 2 + 8.5, RIGHT_COL[i], "start", 2.0),
                                   (bw / 2 - 8.5, LEFT_COL[i], "end", -2.0)):
            svg.circle(px(u), py(y), 0.5 * S, "#d4af37", INK, 0.6)
            svg.text(px(u + dx), py(y) + 4, lab, 10, INK, anchor)
    stem, _, tail = name.rpartition("-")
    svg.text(px(bw / 2), py(cy) - 44, stem, 11, "#ffffff", "middle", "bold")
    svg.text(px(bw / 2), py(cy) - 30, tail, 11, "#ffffff", "middle", "bold")
    svg.text(px(bw / 2), py(cy - XIAO_HL) - 8, "USB-C", 10, "#ffffff", "middle")

    # BAT pads: on the module's back, facing the carrier, so dashed. The footprint
    # is a front view with USB up; turned USB-down, (fx, fy) -> (-fx, fy).
    for lab, fx, fy in BAT_PADS:
        u = bw / 2 - fx
        svg.rect(px(u - BAT_W / 2), py(cy + fy + BAT_H / 2), BAT_W * S, BAT_H * S,
                 "none", PAD, 1.6, 1, "3,2")
        svg.text(px(u - BAT_W / 2) - 3, py(cy + fy) + 4, lab, 10, PAD, "end", "bold")

    # Pigtail exits. Both long sides are walled by header plastic, so the wires
    # leave through an open end: aft (USB-C) or forward.
    pad_y = sum(fy for _, _, fy in BAT_PADS) / len(BAT_PADS)
    u = bw / 2 + 4.5
    svg.line(px(u), py(cy + pad_y), px(u), py(cy - XIAO_HL - 2.5), PAD, 1.4, "4,3", True)
    svg.line(px(u), py(cy + pad_y), px(u), py(cy + XIAO_HL + 2.5), PAD, 1.4, "4,3", True)
    svg.text(px(u) + 5, py(cy - XIAO_HL - 2.5) + 4, "%.1f to USB-C end"
             % (pad_y + XIAO_HL), 10, PAD, weight="bold")
    svg.text(px(u) - 5, py(cy + XIAO_HL + 2.5) + 2, "%.1f to far end"
             % (XIAO_HL - pad_y), 10, PAD, "end", "bold")

    # Dimensions down the left: y stations from the aft edge.
    x_dim = px(0) - 50
    stations = sorted({0.0, cy - XIAO_HL, cy + XIAO_HL, ocy - XIAO_HL, ocy + XIAO_HL, bh})
    for y in stations:
        svg.line(x_dim - 4, py(y), px(0), py(y), DIM, 0.5, "2,3")
        svg.text(x_dim - 8, py(y) + 4, "%g" % round(y, 1), 11, DIM, "end")
    svg.text(x_dim - 8, py(bh) - 14, "carrier y, mm", 10, DIM, "end")

    # Width.
    svg.line(px(0), py(0) + 26, px(bw), py(0) + 26, DIM, 1)
    for u in (0, bw):
        svg.line(px(u), py(0) + 21, px(u), py(0) + 31, DIM, 1)
    svg.text(px(bw / 2), py(0) + 22, "%g" % bw, 11, DIM, "middle")

    # Free length on this face, on the right.
    x_z = px(bw) + 24
    aft_end = cy - USB_OUT      # to the USB-C tip
    aft_label = "%.1f clear, to the USB-C tip" if face == "top" else "%.1f, USB-C service end (#1)"
    vdim(svg, x_z, py(0), py(aft_end), aft_label % aft_end, +1, ZONE)
    vdim(svg, x_z, py(cy + XIAO_HL), py(bh), "%.1f clear" % (bh - cy - XIAO_HL), +1, ZONE)
    svg.text(x_z + 6, py(bh) - 14, "unplaced (#14):", 10, ZONE)
    svg.text(x_z + 6, py(bh) - 2 + 0, UNPLACED[face], 10, ZONE)


def main():
    bw, bh, holes, headers = read_board()
    for ref, (name, face) in XIAOS.items():
        xs = sorted(x for x, _, _ in headers[ref])
        assert len(xs) == 2 and abs((xs[1] - xs[0]) - 17.0) < 0.01, (ref, xs)
        # Pins 1..7 (D0..D6) are drawn on the right of each face's view. #21.
        pin1_x = [x for x, _, side in headers[ref] if side == "A"][0]
        view_x = bw - pin1_x if face == "top" else pin1_x
        assert abs(view_x - (bw / 2 + 8.5)) < 0.01, (
            "%s: the board puts pins 1..7 on the other row from this drawing" % name)

    W = 2 * PANEL_W + 100
    H = TOP_Y + bh * S + 170
    svg = Svg()
    svg.add('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
            'viewBox="0 0 %d %d" font-family="Helvetica, Arial, sans-serif">' % (W, H, W, H))
    svg.add('<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
            'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" '
            'fill="%s"/></marker></defs>' % PAD)
    svg.rect(0, 0, W, H, "#ffffff", "none", 0)
    panel(svg, 120, "top", bw, bh, holes, headers)
    panel(svg, 120 + PANEL_W + 40, "bottom", bw, bh, holes, headers)
    svg.text(20, H - 40, "Header strips (grey) are 2.5 mm plastic walls down both long sides "
             "of each XIAO: a BAT pigtail can only leave through an open end.", 12, NOTE)
    svg.text(20, H - 22, "BAT pads (dashed red) are on each XIAO's back, facing the carrier. "
             "Generated by hardware/scripts/gen_carrier_diagram.py from PCB-carrier.kicad_pcb.",
             12, NOTE)
    svg.add("</svg>")
    with open(OUT, "w") as f:
        f.write("\n".join(svg.out) + "\n")
    print("wrote    %s" % OUT)


if __name__ == "__main__":
    main()
