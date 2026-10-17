"""Route the PCB-carrier's signal nets: a grid maze router, called by gen_carrier.py.

THE BOARD WAS PLACED, NETTED AND CHECKED, BUT NEVER WIRED (#15). Ground and the
cam XIAO's 3V3 reach every pad through the two inner planes, so only the signal
nets need traces: I2C, the GPS lines, the GPS's own 3V3, the buzzer's two drive
lines and the three data-link wires. Done by hand in KiCad that is an hour of
clicking, and it is thrown away by the next layout change. Done here it is
regenerated with the board, and KiCad's DRC is the proof -- 0 violations and
0 unconnected items, or the generator fails.

HOW. A Dijkstra search on a 0.127 mm grid over the two outer copper layers,
F.Cu (the tall side) and B.Cu (the low side). A cell is blocked for a net when
it lies within clearance + half a track of any copper of another net, or of a
mounting hole, or of the board edge. A via (0.6 / 0.3 mm) joins the layers and
costs as much as a few millimetres of track, so the router hops sides only when
it must. Nets of three or more pads grow as a tree: each new branch may start
anywhere on the copper the net already has. Each finished route becomes copper
that later nets must clear.

Track 0.25 mm and clearance 0.2 mm, inside OSH Park's 4-layer rules (5 mil /
5 mil); the via drill 0.3 mm against their 10 mil minimum.
"""
import heapq
import math

import pcbnew

GRID = 0.127
TRACK = 0.25
CLEAR = 0.2
VIA_D, VIA_DRILL = 0.6, 0.3
VIA_COST = 30          # in grid steps: ~3.8 mm of track
EDGE = 0.5             # copper keeps this far from the board edge
LAYERS = (pcbnew.F_Cu, pcbnew.B_Cu)
MM = pcbnew.FromMM


class Feature:
    """Copper (or a hole) another net must clear: a circle or a square."""

    def __init__(self, x, y, r, net, layers, square=False):
        self.x, self.y, self.r, self.net, self.layers, self.square = x, y, r, net, layers, square

    def dist(self, x, y):
        dx, dy = abs(x - self.x), abs(y - self.y)
        if self.square:
            if dx <= self.r and dy <= self.r:
                return -min(self.r - dx, self.r - dy)
            return math.hypot(max(dx - self.r, 0.0), max(dy - self.r, 0.0))
        return math.hypot(dx, dy) - self.r


def _pads(board):
    out = []
    for fp in board.GetFootprints():
        for p in fp.Pads():
            x, y = pcbnew.ToMM(p.GetX()), pcbnew.ToMM(p.GetY())
            half = pcbnew.ToMM(max(p.GetSize().x, p.GetSize().y)) / 2.0
            net = p.GetNetname()
            if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
                out.append(Feature(x, y, pcbnew.ToMM(p.GetDrillSize().x) / 2.0, "#hole", (0, 1)))
            else:
                out.append(Feature(x, y, half, net, (0, 1),
                                   square=p.GetShape() == pcbnew.PAD_SHAPE_RECT))
    return out


def route(board, nets, w, h):
    """Route each net in `nets` (names) in order. Returns {net: (segments, vias)}."""
    nx, ny = int(w / GRID) + 1, int(h / GRID) + 1
    feats = _pads(board)
    done = {}

    def idx(i, j):
        return j * nx + i

    def pos(i, j):
        return i * GRID, j * GRID

    for net in nets:
        own = [f for f in feats if f.net == net]
        if len(own) < 2:
            continue
        # blocked cells per layer for this net
        blocked = [bytearray(nx * ny), bytearray(nx * ny)]
        reach = CLEAR + TRACK / 2.0
        for f in feats:
            if f.net == net:
                continue
            rr = f.r + reach + (0.0 if f.net != "#hole" else 0.05)
            span = rr * (1.42 if f.square else 1.0)
            i0, i1 = max(0, int((f.x - span) / GRID)), min(nx - 1, int((f.x + span) / GRID) + 1)
            j0, j1 = max(0, int((f.y - span) / GRID)), min(ny - 1, int((f.y + span) / GRID) + 1)
            for j in range(j0, j1 + 1):
                for i in range(i0, i1 + 1):
                    x, y = pos(i, j)
                    if f.dist(x, y) < reach + (0.05 if f.net == "#hole" else 0.0):
                        for L in f.layers:
                            blocked[L][idx(i, j)] = 1
        edge = EDGE + TRACK / 2.0
        ei, ej = int(math.ceil(edge / GRID)), int(math.ceil(edge / GRID))
        for j in range(ny):
            for i in list(range(0, ei)) + list(range(nx - ei, nx)):
                blocked[0][idx(i, j)] = blocked[1][idx(i, j)] = 1
        for j in list(range(0, ej)) + list(range(ny - ej, ny)):
            for i in range(nx):
                blocked[0][idx(i, j)] = blocked[1][idx(i, j)] = 1
        # a via needs room on both layers
        via_reach = CLEAR + VIA_D / 2.0

        def via_ok(i, j):
            x, y = pos(i, j)
            for f in feats:
                if f.net != net and f.dist(x, y) < via_reach:
                    return False
            return not (x < VIA_D or x > w - VIA_D or y < VIA_D or y > h - VIA_D)

        def inside(f, i, j):
            x, y = pos(i, j)
            return f.dist(x, y) <= -0.05

        def cells_of(f):
            span = f.r * 1.42
            for j in range(max(0, int((f.y - span) / GRID)), min(ny - 1, int((f.y + span) / GRID) + 1) + 1):
                for i in range(max(0, int((f.x - span) / GRID)), min(nx - 1, int((f.x + span) / GRID) + 1) + 1):
                    if inside(f, i, j):
                        yield i, j

        connected = [own[0]]
        todo = own[1:]
        net_cells = {(L, i, j) for (i, j) in cells_of(own[0]) for L in (0, 1)}
        segs, vias = [], []
        while todo:
            targets = {}
            for k, f in enumerate(todo):
                for (i, j) in cells_of(f):
                    for L in (0, 1):
                        targets[(L, i, j)] = k
            # A*: no direction in the state (that multiplied the work ~10x); the
            # heuristic is the octile distance to the nearest unreached pad
            tgt_xy = [(int(round(f.x / GRID)), int(round(f.y / GRID))) for f in todo]

            def hfun(i, j):
                best = 1e18
                for (ti, tj) in tgt_xy:
                    a, b = abs(i - ti), abs(j - tj)
                    best = min(best, max(a, b) + 0.414 * min(a, b))
                return best
            dist = {}
            prev = {}
            heap = []
            for c in net_cells:
                dist[c] = 0.0
                heapq.heappush(heap, (hfun(c[1], c[2]), 0.0, c))
            hit = None
            steps = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0),
                     (1, 1, 1.414), (1, -1, 1.414), (-1, 1, 1.414), (-1, -1, 1.414)]
            while heap:
                _, d, cur = heapq.heappop(heap)
                if dist.get(cur, 1e18) < d:
                    continue
                L, i, j = cur
                if cur in targets and cur not in net_cells:
                    hit = cur
                    break
                for (di, dj, c) in steps:
                    ii, jj = i + di, j + dj
                    if not (0 <= ii < nx and 0 <= jj < ny):
                        continue
                    nxt = (L, ii, jj)
                    if blocked[L][idx(ii, jj)] and nxt not in targets:
                        continue
                    nd = d + c
                    if nd < dist.get(nxt, 1e18):
                        dist[nxt] = nd
                        prev[nxt] = cur
                        heapq.heappush(heap, (nd + hfun(ii, jj), nd, nxt))
                o = 1 - L
                nxt = (o, i, j)
                if not blocked[o][idx(i, j)] and nxt not in dist and via_ok(i, j):
                    nd = d + VIA_COST
                    dist[nxt] = nd
                    prev[nxt] = cur
                    heapq.heappush(heap, (nd + hfun(i, j), nd, nxt))
            if hit is None:
                raise RuntimeError("could not route %s to %s" % (net, [(f.x, f.y) for f in todo]))
            path = []
            key = hit
            while key in prev:
                path.append(key)
                key = prev[key]
            path.append(key)
            path.reverse()
            k = targets[hit]
            reached = todo.pop(k)
            connected.append(reached)
            # copper: segments per layer run, a via at each layer change
            pts = [(L, pos(i, j)) for (L, i, j) in path]
            start_pad = min(connected[:-1], key=lambda f: f.dist(*pts[0][1]))
            if start_pad.dist(*pts[0][1]) <= 0:
                pts.insert(0, (pts[0][0], (start_pad.x, start_pad.y)))
            pts.append((pts[-1][0], (reached.x, reached.y)))
            run = [pts[0]]
            for p in pts[1:]:
                if p[0] != run[-1][0]:
                    vias.append(run[-1][1])
                    segs.append((run[-1][0], [q[1] for q in run]))
                    run = [(p[0], run[-1][1]), p]
                else:
                    run.append(p)
            segs.append((run[-1][0], [q[1] for q in run]))
            for (L, i, j) in path:
                net_cells.add((L, i, j))
            for (i, j) in cells_of(reached):
                net_cells.add((0, i, j))
                net_cells.add((1, i, j))
        # the finished net becomes copper for the nets after it
        for L, poly in segs:
            for (x0, y0), (x1, y1) in zip(poly, poly[1:]):
                n = max(1, int(math.hypot(x1 - x0, y1 - y0) / (GRID / 2)))
                for t in range(n + 1):
                    feats.append(Feature(x0 + (x1 - x0) * t / n, y0 + (y1 - y0) * t / n,
                                         TRACK / 2.0, net, (LAYERS.index(LAYERS[L]),)))
        for (x, y) in vias:
            feats.append(Feature(x, y, VIA_D / 2.0, net, (0, 1)))
        done[net] = (segs, vias)
    return done


def simplify(poly):
    """Drop points that lie on a straight run."""
    out = [poly[0]]
    for k in range(1, len(poly) - 1):
        (x0, y0), (x1, y1), (x2, y2) = out[-1], poly[k], poly[k + 1]
        if abs((x1 - x0) * (y2 - y1) - (y1 - y0) * (x2 - x1)) > 1e-6:
            out.append(poly[k])
    out.append(poly[-1])
    return out


def add_tracks(board, routed):
    n_seg = n_via = 0
    for net, (segs, vias) in routed.items():
        code = board.nets[net]
        for L, poly in segs:
            poly = simplify(poly)
            for (x0, y0), (x1, y1) in zip(poly, poly[1:]):
                if abs(x0 - x1) < 1e-6 and abs(y0 - y1) < 1e-6:
                    continue
                t = pcbnew.PCB_TRACK(board)
                t.SetStart(pcbnew.VECTOR2I(MM(x0), MM(y0)))
                t.SetEnd(pcbnew.VECTOR2I(MM(x1), MM(y1)))
                t.SetWidth(MM(TRACK))
                t.SetLayer(LAYERS[L])
                t.SetNet(code)
                board.Add(t)
                n_seg += 1
        for (x, y) in vias:
            v = pcbnew.PCB_VIA(board)
            v.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
            v.SetWidth(MM(VIA_D))
            v.SetDrill(MM(VIA_DRILL))
            v.SetNet(code)
            board.Add(v)
            n_via += 1
    return n_seg, n_via
