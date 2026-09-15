#!/usr/bin/env python3
"""Full-size paper template of the carrier, both sides -- where every part goes.

    python3 hardware/scripts/gen_carrier_template.py

Writes hardware/PCB-carrier/PCB-carrier-template.svg, and a PDF beside it when
Google Chrome is installed. Print at 100 % ("Actual size") on US Letter; the
100 mm bar on the sheet proves the scale. Hold the fit mock against a panel and
every hole lines up.

WHY PAPER. The fit mock's printed labels did not survive slicing: their strokes
are ~0.15 mm against a 0.42 mm line, and the G-code carried 21 mm of extrusion
on each label layer (operator, 2026-09-15: no labels on the mock). A sheet of
paper says what goes where at no cost in plastic.

WHERE THE NUMBERS COME FROM. Part outlines, pads and nets from
PCB-carrier-layout.json (gen_carrier.py); holes, the arrow and the battery
markers from the fit mock's own sidecar (gen_carrier_fitmock.py), so the
template shows exactly the holes the mock has. Nothing is typed in here.

THE PANELS are drawn as gen_carrier_diagram.py draws them, each seen from its
own side with forward up, so they are mirror images. 1 unit = 1 mm.
"""
import json
import os
import subprocess
import tempfile
import time

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DIR = os.path.join(REPO, "hardware", "PCB-carrier")
LAYOUT = os.path.join(DIR, "PCB-carrier-layout.json")
SIDECAR = os.path.join(DIR, "fit-mock", "PCB-carrier-fit-mock-holes.json")
OUT = os.path.join(DIR, "PCB-carrier-template.svg")
PDF = os.path.join(DIR, "PCB-carrier-template.pdf")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

PAGE_W, PAGE_H = 215.9, 279.4               # US Letter, mm
OY = 34.0                                   # top of both boards on the sheet
PANELS = {"tall": 38.0, "low": 128.0}       # left edge of each board
INK, NOTE = "#1b1b1b", "#555555"
SIDE_COLOUR = {"tall": "#9a3412", "low": "#1d6b3f"}
BATTERY, STANDOFF = "#5a6b8c", "#b7791f"
NET_COLOUR = {"+3V3": "#cc2f2f", "+3V3_LORA": "#f08a4b", "GND": "#222222", "VBAT": "#e03b3b",
              "SDA": "#2f5fcc", "SCL": "#d99b00", "BUZZER": "#6f6f6f", "GPS_TX": "#1d8a4a",
              "GPS_RX": "#7a3fb5"}
XIAO_LABELS = {"A": ["D0", "D1", "D2", "D3", "D4", "D5", "D6"],
               "B": ["D7", "D8", "D9", "D10", "3V3", "GND", "5V"]}
# callouts beside the board, by pad reference: (text lines, page-y nudge in mm)
CALLOUTS = [
    (("TP_CAM_BAT_P", "TP_CAM_BAT_N", "TP_BUZ", "TP_BUZ_G"),
     ("XIAO-ESP32S3-cam pigtail: BAT+ red, BAT− black", "buzzer leads: BUZ grey, BUZ G black"), 0.0),
    (("TP_LORA_BAT_P", "TP_LORA_BAT_N"), ("XIAO-ESP32S3-lora pigtail: BAT+ red, BAT− black",), 0.0),
    (("J_BAT",), ("JST — the battery plug, + at pin 1:", "check it against the red lead"), -6.5),
    (("J_LSM_P", "J_LSM_A"), ("LSM6DSO32, low side: its 9-hole row (green) outside", "the cam XIAO's row, its 5-hole row inside"), 0.0),
    (("J_BMP",), ("BMP388, low side: its 8-hole row, green,", "and two M2 bolt heads on the far edge"), -4.0),
]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Svg:
    def __init__(self):
        self.out = []

    def add(self, s):
        self.out.append(s)

    def text(self, x, y, s, size, fill=INK, anchor="middle", weight="normal"):
        self.add('<text x="%.2f" y="%.2f" font-size="%.2f" fill="%s" text-anchor="%s" '
                 'font-weight="%s">%s</text>' % (x, y, size, fill, anchor, weight, esc(s)))

    def rect(self, x, y, w, h, fill="none", stroke=INK, sw=0.2, r=0.0, opacity=1.0, dash=None):
        d = ' stroke-dasharray="%s"' % dash if dash else ""
        self.add('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" rx="%.2f" fill="%s" '
                 'fill-opacity="%.2f" stroke="%s" stroke-width="%.2f"%s/>'
                 % (x, y, w, h, r, fill, opacity, stroke, sw, d))

    def circle(self, x, y, r, fill="none", stroke=INK, sw=0.15, dash=None):
        d = ' stroke-dasharray="%s"' % dash if dash else ""
        self.add('<circle cx="%.2f" cy="%.2f" r="%.2f" fill="%s" stroke="%s" stroke-width="%.2f"%s/>'
                 % (x, y, r, fill, stroke, sw, d))

    def line(self, x1, y1, x2, y2, stroke=INK, sw=0.2):
        self.add('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" stroke-width="%.2f"/>'
                 % (x1, y1, x2, y2, stroke, sw))

    def poly(self, pts, fill, stroke=INK, sw=0.15):
        self.add('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.2f"/>'
                 % (" ".join("%.2f,%.2f" % p for p in pts), fill, stroke, sw))


def main():
    L = json.load(open(LAYOUT))
    M = json.load(open(SIDECAR))
    bw, bh, z0 = L["board"]["w"], L["board"]["h"], L["board"]["nose_z0"]

    def px(side, x):
        # tall side seen from the front, forward up: KiCad turned 180 deg; low side as KiCad has it
        return PANELS[side] + ((bw - x) if side == "tall" else x)

    def py(y):
        return OY + (bh - y)

    svg = Svg()
    svg.add('<svg xmlns="http://www.w3.org/2000/svg" width="%gmm" height="%gmm" viewBox="0 0 %g %g" '
            'font-family="Helvetica, Arial, sans-serif">' % (PAGE_W, PAGE_H, PAGE_W, PAGE_H))
    svg.rect(0, 0, PAGE_W, PAGE_H, "#ffffff", "none", 0)
    svg.text(12, 12, "PCB-carrier — full-size template, both sides", 5.0, INK, "start", "bold")
    svg.text(12, 18, "Print at 100 % (\"Actual size\"), US Letter. Generated from PCB-carrier-layout.json "
                     "and the fit mock's own holes — regenerate, do not edit.", 2.6, NOTE, "start")

    titles = {"tall": ("TALL SIDE — faces 270°", "the fit mock's TOP face as printed"),
              "low": ("LOW SIDE — faces 90°", "the fit mock's BED face as printed")}
    for side in ("tall", "low"):
        x0 = PANELS[side]
        svg.text(x0 + bw / 2, OY - 8.5, titles[side][0], 3.4, SIDE_COLOUR[side], weight="bold")
        svg.text(x0 + bw / 2, OY - 4.5, titles[side][1], 2.4, NOTE)
        svg.text(x0 + bw / 2, OY - 1.2, "↑ forward, nose tip", 2.2, NOTE)
        pads = {}
        svg.rect(x0, py(bh), bw, bh, "#eef3ea", "#5f7f52", 0.3, L["board"]["r"])

        # the battery, on the low side: not on the board, 5.25 mm off it in the sled's cage
        b = L["battery"]
        mine = side == "low"
        xa, xb = sorted((px(side, b["x0"]), px(side, b["x1"])))
        svg.rect(xa, py(b["y1"]), xb - xa, b["y1"] - b["y0"], BATTERY if mine else "none", BATTERY,
                 0.3 if mine else 0.2, 1.0, 0.15 if mine else 0.0, "1.2,0.8")

        for body in L["bodies"]:
            mine = body["side"] == side
            c = SIDE_COLOUR[body["side"]]
            xa, xb = sorted((px(side, body["x0"]), px(side, body["x1"])))
            svg.rect(xa, py(body["y1"]), xb - xa, body["y1"] - body["y0"], c if mine else "none", c,
                     0.35 if mine else 0.2, 0.6, 0.12 if mine else 0.0, None if mine else "1,0.7")
        if side == "tall":
            for u in L["usb_c"]:
                xa, xb = sorted((px(side, u["x0"]), px(side, u["x1"])))
                svg.rect(xa, py(u["y0"]), xb - xa, u["y0"] - u["y1"], "#b8b8b8", INK, 0.15)
                svg.text((xa + xb) / 2, py((u["y0"] + u["y1"]) / 2) + 0.35, "USB-C", 1.0, INK)

        for so in L["standoffs"]:
            svg.circle(px(side, so["x"]), py(so["y"]), so["r"], "none", STANDOFF, 0.25,
                       None if side == "low" else "1,0.7")
        if side == "low":
            for leg in L["bmp_legs"]:
                svg.circle(px(side, leg["x"]), py(leg["y"]), 1.9, "none", SIDE_COLOUR["low"], 0.2, "0.7,0.5")

        # every hole the mock has, at the size the mock has it, rimmed in the colour of the side
        # whose part owns it -- so the sensors' holes stand out from the XIAO rows beside them
        for h in M["holes"]:
            owner = min(L["pads"], key=lambda q: (q["x"] - h["x"]) ** 2 + (q["y"] - h["y"]) ** 2)
            rim = STANDOFF if owner["ref"].startswith("SO") else SIDE_COLOUR[owner["side"]]
            svg.circle(px(side, h["x"]), py(h["y"]), h["r"], "#ffffff", rim, 0.3)
        for x, y, r in M["marks"]:
            svg.circle(px(side, x), py(y), r, "#ffffff", BATTERY, 0.25)
        svg.poly([(px(side, x), py(y)) for x, y in M["arrow"]], "#ffffff", INK, 0.2)

        # net colour on each pad, and names where a wire or a pin row goes
        for p in L["pads"]:
            if p["ref"].startswith("SO"):
                continue
            pads.setdefault(p["ref"], []).append((px(side, p["x"]), py(p["y"])))
            if p["net"]:
                svg.circle(px(side, p["x"]), py(p["y"]), 0.3, NET_COLOUR.get(p["net"], "#d4af37"), "none", 0)
            if side == "tall" and p["ref"][:-1] in ("J_CAM_", "J_LORA_"):
                lab = XIAO_LABELS[p["ref"][-1]][int(p["num"]) - 1]
                right = px(side, p["x"]) > px(side, bw / 2)
                edge = PANELS[side] + (bw + 3.3 if right else -3.3)
                svg.text(edge, py(p["y"]) + 0.6, lab, 1.7, INK, "start" if right else "end")
            if p["ref"] == "J_BAT" and p["num"] == "1" and side == "tall":
                svg.text(px(side, p["x"]), py(p["y"]) - 1.3, "+", 2.2, NET_COLOUR["VBAT"], weight="bold")

        for body in L["bodies"]:
            if body["side"] != side:
                continue
            cx = (px(side, body["x0"]) + px(side, body["x1"])) / 2
            if body["name"] == "LSM6DSO32":      # between its 5-pin row and the cam's row, clear of holes
                cx = px(side, 14.4)
            cy = py((body["y0"] + body["y1"]) / 2)
            name = "JST" if body["name"] == "JST-PH" else body["name"]
            parts = name.rsplit("-", 1) if name.startswith("XIAO") else [name]
            size = 1.4 if name == "JST" else 1.6
            for i, part in enumerate(parts):
                svg.text(cx, cy + 0.7 + (i - (len(parts) - 1) / 2) * 2.6, part, size,
                         SIDE_COLOUR[side], weight="bold")

        # what each wire hole and the JST are, beside the board with a leader
        tx = PANELS[side] + bw + 6.5
        for refs, text, nudge in CALLOUTS:
            pts = [q for r in refs for q in pads.get(r, [])]
            if not pts:
                continue
            ax = max(q[0] for q in pts)
            ay = sum(q[1] for q in pts) / len(pts)
            ty = ay + nudge
            svg.line(ax + 0.6, ay, tx - 0.8, ty - 0.6, NOTE, 0.12)
            for i, t in enumerate(text):
                svg.text(tx, ty + i * 2.3, t, 1.7, INK, "start")
        if side == "low":
            by = py((L["battery"]["y0"] + L["battery"]["y1"]) / 2)
            svg.text(px(side, bw / 2), by + 10.5, "battery", 2.4, BATTERY, weight="bold")
            svg.text(px(side, bw / 2), by + 13.3, "in the sled's cage,", 1.7, BATTERY)
            svg.text(px(side, bw / 2), by + 15.5, "%.2f mm off the board" % (L["battery"]["r0"] - 0.5),
                     1.7, BATTERY)
            for so in L["standoffs"]:
                svg.text(px(side, so["x"]), py(so["y"]) + 0.7, "M3", 2.0, STANDOFF, weight="bold")

    # nose z down the left, at the ends of every part
    ys = {0.0, bh} | {L["battery"]["y0"], L["battery"]["y1"]}
    for body in L["bodies"]:
        ys |= {body["y0"], body["y1"]}
    last = None
    for y in sorted(ys):
        if last is not None and abs(py(y) - last) < 2.6:
            continue
        last = py(y)
        svg.text(PANELS["tall"] - 9.0, py(y) + 0.7, "%.1f" % (z0 + y), 1.8, "#2f5fcc", "end")
    svg.text(PANELS["tall"] - 9.0, OY - 1.2, "nose z", 1.8, "#2f5fcc", "end")

    # the proof of scale
    sy = OY + bh + 14
    svg.line(12, sy, 112, sy, INK, 0.4)
    for i in range(11):
        svg.line(12 + 10 * i, sy - (2.2 if i % 5 == 0 else 1.2), 12 + 10 * i, sy, INK, 0.25)
    svg.text(62, sy + 4.2, "this bar must measure 100 mm — if not, reprint at 100 % / Actual size", 2.3, INK)
    svg.text(PANELS["tall"] + bw / 2, OY + bh + 5.5, "%g × %g mm" % (bw, bh), 2.2, NOTE)

    lines = (
        "How to use it: hold the fit mock TOP face toward you, the arrow pointing up — it matches",
        "the TALL SIDE panel, hole for hole. Turn it over left to right: the LOW SIDE panel.",
        "Solid outlines are parts on that side; dashed are parts on the other side.",
        "White circles are the mock's holes, rimmed red for a tall-side part and green for a",
        "low-side part; the dot in each is its net. The LSM6DSO32 is slid sideways: its 9-hole row",
        "is outside the cam XIAO's row, its 5-hole row inside. Pin names beside the XIAO rows are",
        "for the XIAO plugged in from the tall side. The small blue-rimmed holes at the long edges mark the",
        "battery's two ends. BAT+/BAT− are each XIAO's battery pigtail, soldered on the low side.",
        "Source of truth: hardware/PCB-carrier/PCB-carrier.md.",
    )
    for i, t in enumerate(lines):
        svg.text(12, sy + 12 + i * 4.0, t, 2.5, INK, "start")
    lx, ly = 150, OY + bh + 22
    svg.text(lx, ly, "Pad colour = net", 2.6, INK, "start", "bold")
    for i, (net, c) in enumerate(NET_COLOUR.items()):
        svg.circle(lx + 1.2, ly + 4.2 + i * 4.0, 1.0, c, INK, 0.1)
        svg.text(lx + 3.4, ly + 5.0 + i * 4.0, net, 2.2, INK, "start")

    svg.add("</svg>")
    with open(OUT, "w") as f:
        f.write("\n".join(svg.out) + "\n")
    print("wrote    %s" % OUT)

    if os.path.exists(CHROME):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            page = os.path.join(tmp, "t.html")
            with open(page, "w") as f:
                f.write('<!doctype html><style>@page{size:%gmm %gmm;margin:0}html,body{margin:0}'
                        'img{display:block;width:%gmm;height:%gmm}</style><img src="file://%s">'
                        % (PAGE_W, PAGE_H, PAGE_W, PAGE_H, OUT))
            if os.path.exists(PDF):
                os.remove(PDF)
            # headless Chrome writes the PDF and then does not always exit: wait for the file
            # to stop growing, then end it
            proc = subprocess.Popen([CHROME, "--headless=new", "--user-data-dir=" + os.path.join(tmp, "p"),
                                     "--no-pdf-header-footer", "--print-to-pdf=" + PDF, "file://" + page],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            size, still = -1, 0
            for _ in range(240):
                time.sleep(0.5)
                now = os.path.getsize(PDF) if os.path.exists(PDF) else -1
                still = still + 1 if now == size and now > 0 else 0
                size = now
                if still >= 4 or proc.poll() is not None:
                    break
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
        if not os.path.exists(PDF) or os.path.getsize(PDF) == 0:
            raise SystemExit("Chrome wrote no PDF -- print the SVG from a browser at 100 %")
        print("wrote    %s" % PDF)
    else:
        print("no Chrome -- print the SVG from a browser at 100 %")


if __name__ == "__main__":
    main()
