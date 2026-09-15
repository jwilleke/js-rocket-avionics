"""Put the carrier's silkscreen labels onto the PLA/PETG fit mock, readable in plastic.

    /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 \
        hardware/scripts/gen_carrier_fitmock.py
    /Applications/Blender.app/Contents/MacOS/Blender --background \
        --python hardware/scripts/gen_carrier_fitmock_labels.py

Second step after gen_carrier_fitmock.py, which exports the board body and writes
PCB-carrier-fit-mock-labels.json: every F.SilkS / B.SilkS text read off the board
file, and every hole. This adds them to the STL in place:

  - tall-side (F.SilkS) labels RAISED 0.4 mm on the top face -- the mock prints
    low side down, so the top face is the tall side
  - low-side (B.SilkS) labels CUT 0.4 mm into the bed face, mirrored as on the
    board, so they read from the low side

The board's silkscreen is 0.8-1.5 mm tall, too small to print legibly with a
0.4 mm nozzle. Each label starts at GROW x its board size and shrinks until its
box clears every hole, the arrow, the battery marks, the board edge and the
labels already placed on that face -- never below its board size. It stays
centred where the board has it. The sizes used are printed.
"""
import json
import math
import os

import bmesh
import bpy

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DIR = os.path.join(REPO, "hardware", "PCB-carrier", "fit-mock")
STL = os.path.join(DIR, "PCB-carrier-fit-mock.stl")
SIDE = os.path.join(DIR, "PCB-carrier-fit-mock-labels.json")

GROW, STEP = 1.8, 0.92       # start size multiple, shrink factor per try
CAP = 0.72                   # Blender's cap height per unit of text size
RAISE = CUT = 0.4
MARGIN = 0.3                 # mm kept clear around holes, edges and other labels


def clean(ob):
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.remove_doubles(threshold=1e-5)
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode="OBJECT")


def boolean(obj, cutter, op):
    m = obj.modifiers.new(name=op, type="BOOLEAN")
    m.operation, m.object, m.solver = op, cutter, "EXACT"
    m.use_hole_tolerant = True     # the font's curves leave slivers a few hundredths of a mm long
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.data.objects.remove(cutter, do_unlink=True)


def prism(outline, x, y, z, depth, name):
    """One clean solid from a 2-D outline -- used for the polarity marks."""
    bm = bmesh.new()
    lo = [bm.verts.new((x + u, y + v, z - depth / 2.0)) for u, v in outline]
    hi = [bm.verts.new((x + u, y + v, z + depth / 2.0)) for u, v in outline]
    bm.faces.new(lo[::-1])
    bm.faces.new(hi)
    n = len(outline)
    for i in range(n):
        bm.faces.new((lo[i], lo[(i + 1) % n], hi[(i + 1) % n], hi[i]))
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    return ob


def text_mesh(s, cap_h, x, y, back, z, depth):
    """A label as a solid. '+' and '-' are drawn, not typeset: a cross and a bar a third
    of the cap height thick, so they print as solid marks with a 0.4 mm nozzle."""
    if s in ("+", "-"):
        a, w = cap_h / 2.0, cap_h / 6.0            # arm half-length, bar half-width
        if s == "-":
            return prism([(-a, -w), (a, -w), (a, w), (-a, w)], x, y, z, depth, "minus")
        return prism([(-w, -a), (w, -a), (w, -w), (a, -w), (a, w), (w, w),
                      (w, a), (-w, a), (-w, w), (-a, w), (-a, -w), (-w, -w)], x, y, z, depth, "plus")
    bpy.ops.object.text_add(location=(0, 0, 0))
    ob = bpy.context.active_object
    ob.data.body = s
    ob.data.size = cap_h / CAP
    ob.data.align_x, ob.data.align_y = "CENTER", "CENTER"
    ob.data.extrude = depth / 2.0
    bpy.ops.object.convert(target="MESH")
    ob = bpy.context.active_object
    ob.location = (x, y, z)
    if back:
        ob.scale = (-1.0, 1.0, 1.0)          # mirrored, as B.SilkS is: reads from below
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return ob


def bbox(ob):
    xs = [v.co.x for v in ob.data.vertices]
    ys = [v.co.y for v in ob.data.vertices]
    return min(xs), max(xs), min(ys), max(ys)


def clashes(b, d, placed):
    x0, x1, y0, y1 = b[0] - MARGIN, b[1] + MARGIN, b[2] - MARGIN, b[3] + MARGIN
    bx0, by0, bx1, by1 = d["board"]
    if x0 < bx0 or x1 > bx1 or y0 < -by1 or y1 > -by0:
        return "edge"
    for h in d["holes"] + [{"x": m[0], "y": m[1], "r": m[2]} for m in d["marks"]]:
        cx, cy = h["x"], -h["y"]
        nx, ny = min(max(cx, x0), x1), min(max(cy, y0), y1)
        if math.hypot(nx - cx, ny - cy) < h["r"]:
            return "hole"
    ax = [p[0] for p in d["arrow"]]
    ay = [-p[1] for p in d["arrow"]]
    if not (x1 < min(ax) or x0 > max(ax) or y1 < min(ay) or y0 > max(ay)):
        return "arrow"
    for q in placed:
        if not (x1 < q[0] or x0 > q[1] or y1 < q[2] or y0 > q[3]):
            return "label"
    return None


def main():
    d = json.load(open(SIDE))
    t = d["thickness"]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    before = set(bpy.data.objects)
    bpy.ops.wm.stl_import(filepath=STL)
    part = (set(bpy.data.objects) - before).pop()
    clean(part)
    placed = {False: [], True: []}
    # bigger labels first, so the small marks fit round them
    for lab in sorted(d["labels"], key=lambda l: -l["size"] * len(l["text"])):
        back, x, y = lab["back"], lab["x"], -lab["y"]
        z, depth = ((CUT / 2.0 - 0.05, CUT + 0.1) if back else (t + RAISE / 2.0 - 0.05, RAISE + 0.1))
        h = lab["size"] * GROW
        while True:
            ob = text_mesh(lab["text"], h, x, y, back, z, depth)
            why = clashes(bbox(ob), d, placed[back])
            if not why or h <= lab["size"] * 1.0001:
                break
            bpy.data.objects.remove(ob, do_unlink=True)
            h = max(h * STEP, lab["size"])
        placed[back].append(bbox(ob))
        clean(ob)
        boolean(part, ob, "DIFFERENCE" if back else "UNION")
        bm = bmesh.new(); bm.from_mesh(part.data)
        nm = sum(1 for e in bm.edges if len(e.link_faces) != 2); bm.free()
        if nm:
            print("   after %r: %d non-manifold edges" % (lab["text"], nm))
        print("label  %-14s %s  %.2f mm (board %.2f)%s" % (repr(lab["text"]), "low " if back else "tall",
              h, lab["size"], "" if not why else "  -- still touches a %s" % why))
    # weld and close, as the sled scripts do -- slivers a boolean left open between labels
    clean(part)
    bpy.context.view_layer.objects.active = part
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.remove_doubles(threshold=1e-3)
    bpy.ops.mesh.select_all(action="DESELECT")
    bpy.ops.mesh.select_non_manifold(extend=False, use_wire=False, use_boundary=True,
                                     use_multi_face=False, use_non_contiguous=False, use_verts=False)
    bpy.ops.mesh.fill_holes(sides=0)
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode="OBJECT")
    bm = bmesh.new()
    bm.from_mesh(part.data)
    bad = sum(1 for e in bm.edges if len(e.link_faces) != 2)
    bm.free()
    assert bad == 0, "%d non-manifold edges after the labels" % bad
    bpy.ops.object.select_all(action="DESELECT")
    part.select_set(True)
    bpy.ops.wm.stl_export(filepath=STL, export_selected_objects=True, ascii_format=False)
    print("wrote  %s" % STL)


main()
