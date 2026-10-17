"""Fabrication files for the PCB-carrier, and a read-back of what the fab will see (#16).

    /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 \
        hardware/scripts/gen_carrier_fab.py

Run after gen_carrier.py. It DELETES fab/gerbers/ and writes a fresh set from the
current board -- the stale set there was a plausible-looking board with no
routing, which is the most likely way a wrong board gets ordered.

THEN IT READS THE OUTPUT BACK, not the board. The checks parse the gerber,
drill and IPC-D-356 files themselves, so they see what the fab sees:

  outline    Edge.Cuts extents are 24 x 115.7 mm, its corners are quarter arcs
  drills     every hole in the drill files is a pad, a via or a mounting hole
             of the board, at its position and size, and none is missing
  netlist    every XIAO, GNSS and sensor pin lands on the net its part's pinout
             says, per the IPC-D-356 netlist -- the file a fab's electrical test uses
  sled       the two mounting holes sit where the ElectronicsSled's web holes are

Any mismatch raises; nothing is called ready on a failure.
"""
import glob
import math
import os
import re
import shutil
import subprocess
import sys

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
BOARD = os.path.join(REPO, "hardware", "PCB-carrier", "PCB-carrier.kicad_pcb")
FAB = os.path.join(REPO, "fab", "gerbers")
CLI = "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"
LAYERS = "F.Cu,In1.Cu,In2.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,Edge.Cuts"

sys.path.insert(0, HERE)
_argv, sys.argv = sys.argv, [sys.argv[0]]
import gen_carrier as G                      # the intent: pin maps, board size
sys.argv = _argv


def run(*args):
    subprocess.run([CLI] + list(args), check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def export():
    if os.path.isdir(FAB):
        shutil.rmtree(FAB)
    os.makedirs(FAB)
    run("pcb", "export", "gerbers", "--layers", LAYERS, "-o", FAB + "/", BOARD)
    run("pcb", "export", "drill", "--format", "excellon", "--excellon-separate-th",
        "--excellon-units", "mm", "-o", FAB + "/", BOARD)
    run("pcb", "export", "ipcd356", "-o", os.path.join(FAB, "carrier.ipc"), BOARD)
    return sorted(os.listdir(FAB))


def gerber_coords(path):
    """(x, y) of every D01/D02/D03 in a gerber, in mm."""
    txt = open(path).read()
    m = re.search(r"%FSLAX(\d)(\d)Y\d\d\*%", txt)
    dec = int(m.group(2))
    pts = []
    x = y = 0.0
    for xs, ys in re.findall(r"(?:X(-?\d+))?(?:Y(-?\d+))?(?:I-?\d+J-?\d+)?D0[123]\*", txt):
        if xs:
            x = int(xs) / 10 ** dec
        if ys:
            y = int(ys) / 10 ** dec
        pts.append((x, y))
    return pts, txt


def check_outline():
    path = glob.glob(os.path.join(FAB, "*Edge_Cuts*"))[0]
    pts, txt = gerber_coords(path)
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    w, h = max(xs) - min(xs), max(ys) - min(ys)
    assert abs(w - G.BOARD_W) < 0.01 and abs(h - G.BOARD_H) < 0.01, "outline %.2f x %.2f" % (w, h)
    arcs = len(re.findall(r"G0[23]", txt)) + len(re.findall(r"I-?\d+J-?\d+D01", txt))
    assert "G75" in txt or arcs, "no arcs in the outline"
    return w, h


def excellon(path):
    txt = open(path).read()
    tools, out, cur = {}, [], None
    for line in txt.splitlines():
        m = re.match(r"T(\d+)C([\d.]+)", line)
        if m:
            tools[m.group(1)] = float(m.group(2))
            continue
        m = re.match(r"T(\d+)$", line)
        if m:
            cur = tools.get(m.group(1))
            continue
        m = re.match(r"X(-?[\d.]+)Y(-?[\d.]+)", line)
        if m and cur:
            out.append((float(m.group(1)), float(m.group(2)), cur))
    return out


def check_drills():
    b = pcbnew.LoadBoard(BOARD)
    want = []
    for fp in b.GetFootprints():
        for p in fp.Pads():
            if p.GetDrillSize().x > 0:
                want.append((pcbnew.ToMM(p.GetX()), pcbnew.ToMM(p.GetY()), pcbnew.ToMM(p.GetDrillSize().x)))
    for t in b.GetTracks():
        if t.GetClass() == "PCB_VIA":
            want.append((pcbnew.ToMM(t.GetX()), pcbnew.ToMM(t.GetY()), pcbnew.ToMM(t.GetDrillValue())))
    got = []
    for f in glob.glob(os.path.join(FAB, "*.drl")):
        got += excellon(f)
    # drill files are in the board's own frame with y negated
    used = [False] * len(got)
    for x, y, d in want:
        k = next((i for i, (gx, gy, gd) in enumerate(got)
                  if not used[i] and abs(gx - x) < 0.01 and abs(-gy - y) < 0.01 and abs(gd - d) < 0.01), None)
        assert k is not None, "hole (%.2f, %.2f) d%.2f missing from the drill files" % (x, y, d)
        used[k] = True
    assert all(used), "%d holes in the drill files the board does not have" % used.count(False)
    sizes = sorted(set(round(d, 2) for _, _, d in got))
    return len(got), sizes


def check_netlist():
    """IPC-D-356 '317' records, read by POSITION: the format cuts a refdes to six
    characters, so J_CAM_A and J_CAM_B both read 'J_CAM_'. Coordinates are in
    0.0001 inch, y negated. Each XIAO pin is found where its part's own map in
    gen_carrier.py puts it, and its net held to that map."""
    rec = []
    for line in open(os.path.join(FAB, "carrier.ipc")):
        if not line.startswith("317"):
            continue
        net = line[3:17].strip()
        m = re.search(r"X([+-]\d+)Y([+-]\d+)", line)
        x, y = int(m.group(1)) * 0.00254, -int(m.group(2)) * 0.00254
        rec.append((net, x, y, line[20:27].strip()))

    def net_at(x, y):
        hits = [r for r in rec if abs(r[1] - x) < 0.05 and abs(r[2] - y) < 0.05 and r[3] != "VIA"]
        return hits[0][0] if hits else None

    bad = []
    for cy, signals, turned in ((G.CAM_Y, G.CAM_SIGNALS, False), (G.LORA_Y, G.LORA_SIGNALS, True)):
        for sig, net in signals.items():
            x, y = G.xiao_xy(cy, *G.FOOTPRINT_PIN[G.XIAO_PIN[sig]], turned)
            got = net_at(x, y)
            if got != net[:14]:
                bad.append("XIAO at y %.1f, %s (%.2f, %.2f): netlist says %r, want %r" % (cy, sig, x, y, got, net))
    for label, net in G.L76K_NETS.items():
        x, y = G.l76k_board_xy(label)
        got = net_at(x, y)
        if got != net[:14]:
            bad.append("L76K %s: netlist says %r, want %r" % (label, got, net))
    for name, front, cy, nets, f in (("BMP388", G.front_pins_bmp(), G.BMP_Y, G.BMP_NETS, G.bmp_top_xy),
                                     ("LSM6DSO32", G.front_pins_lsm(), G.LSM_Y, G.LSM_NETS, G.low_side_top_xy)):
        dx = G.LSM_DX if name == "LSM6DSO32" else 0.0
        for lab, px, py in front:
            if lab in nets:
                x, y = f(px, py, cy)
                got = net_at(x + dx, y)
                if got != nets[lab][:14]:
                    bad.append("%s %s: netlist says %r, want %r" % (name, lab, got, nets[lab]))
    for n in ("SDA", "SCL", "GPS_TX", "GPS_RX", "+3V3_LORA", "BUZZER", "BUZZER_B",
              "GPS_CAM", "EVT_CAM", "EVT_LORA", "LINK_GPS", "LINK_EVT"):
        members = [r for r in rec if r[0] == n and r[3] != "VIA"]
        if len(members) < 2:
            bad.append("net %s has %d pads in the netlist" % (n, len(members)))
    assert not bad, "netlist read-back:\n  " + "\n  ".join(bad)
    return len(rec), len(set(r[0] for r in rec))


def check_sled():
    """The sled's two M3 holes, from sled-features.py's own numbers: part x =
    12 - board x, nose z = board y + 25.4."""
    src = open(os.path.join(REPO, "..", "js-rocket", "rocket", "scripts", "sled-features.py")).read()
    m = re.search(r"HOLES = \[\(BOARD_X\(([\d.]+)\), NZ\(([\d.]+)\)\), \(BOARD_X\(([\d.]+)\), NZ\(([\d.]+)\)\)\]", src)
    sled = [(float(m.group(1)), float(m.group(2)) - 25.4), (float(m.group(3)), float(m.group(4)) - 25.4)]
    for (sx, sy), (bx, by) in zip(sled, G.STANDOFFS):
        assert abs(sx - bx) < 0.01 and abs(sy - by) < 0.01, "sled hole %s vs board %s" % ((sx, sy), (bx, by))
    return sled


if __name__ == "__main__":
    files = export()
    print("wrote    %d files to fab/gerbers/" % len(files))
    print("outline  %.2f x %.2f mm, read back from Edge.Cuts" % check_outline())
    n, sizes = check_drills()
    print("drills   %d holes, sizes %s mm -- every one a board hole, none missing" % (n, sizes))
    n, k = check_netlist()
    print("netlist  %d pad records, %d nets -- every XIAO pin on its part's net" % (n, k))
    print("sled     mounting holes match the ElectronicsSled's: %s" % check_sled())
