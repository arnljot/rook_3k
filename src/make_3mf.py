# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright (C) 2026 Arnljot Arntsen
"""Writes a Bambu Studio project (.3mf) with one build plate per part, oriented for printing.
Bambu Studio only loads the plate layout when the file carries project settings, so these are taken from a
project saved in Bambu Studio (bambu_template.3mf).
Usage: python src/make_3mf.py [version] [template.3mf] [output_dir]
  version      label used in the file name; default: the version of the model, e.g. v0.22
  template.3mf project saved from Bambu Studio; default bambu_template.3mf in the repository root
  output_dir   default: the repository root
Options are read from config.txt in the repository root, or from the file given with --config <file>."""
import os, sys, zipfile, datetime, math
import numpy as np
import cadquery as cq
import rook3k as d

VER = sys.argv[1] if len(sys.argv) > 1 else d.VERSION
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # repository root, the parent of src/
TEMPLATE = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "bambu_template.3mf")
OUT_DIR = sys.argv[3] if len(sys.argv) > 3 else ROOT
import json, re
_t = zipfile.ZipFile(TEMPLATE)
T_FILES = {n: _t.read(n) for n in ("Metadata/project_settings.config", "Metadata/slice_info.config", "Metadata/filament_sequence.json") if n in _t.namelist()}
_ps = json.loads(T_FILES["Metadata/project_settings.config"])
_area = [tuple(float(v) for v in p.split("x")) for p in _ps["printable_area"]]
APP = re.search(r'<metadata name="Application">([^<]*)<', _t.read("3D/3dmodel.model").decode()).group(1)
print("template:", _ps.get("printer_settings_id"), _ps["printable_area"], APP)
BED_X, BED_Y = max(a[0] for a in _area), max(a[1] for a in _area)   # from the template
STRIDE_X, STRIDE_Y = BED_X * 1.2, BED_Y * 1.2   # Bambu Studio lays the plates out in a grid with 20 % spacing

RX_M = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]], float)     # +Y (rear) down on the plate
RX_P = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]], float)     # -Y (front) down on the plate
RY_M = np.array([[0, 0, -1], [0, 1, 0], [1, 0, 0]], float)     # -X (left) down on the plate
RY_P = np.array([[0, 0, 1], [0, 1, 0], [-1, 0, 0]], float)     # +X (right) down on the plate
I3 = np.eye(3)

RX_F = np.array([[1, 0, 0], [0, -1, 0], [0, 0, -1]], float)    # upside down

# How each kind of part lies on the plate, and the order of the plates
ORIENT = {"front_panel": RX_M, "u_bracket": RY_P, "side_panel_left": RY_M, "rear_panel": RX_M, "foot": I3,
          "button_power": RX_P, "button_reset": RX_P, "button_eject": I3, "zorro_cover": RX_M, "foot_pad": RX_F, "tpu_pad": I3, "side_plug": RY_M}
# Small parts of the same kind and material share a plate
PLATE_OF = {"button_power": "buttons", "button_reset": "buttons", "button_eject": "buttons"}
ORDER = ["front_panel", "u_bracket", "side_panel_left", "rear_panel", "foot", "foot_pad", "tpu_pad", "buttons", "zorro_cover", "side_plug"]

d.check_clearances()
_plates = {}
for _name, (_fn, _col) in d.PARTS.items():
    _base = d.base_name(_name)
    _plates.setdefault(PLATE_OF.get(_base, _base), []).append((_name, _fn(), ORIENT[_base]))
# (plate name, [(part name, shape, rotation), ...])
PLATES = [(k if len(_plates[k]) == 1 or k == "buttons" else f"{k} x{len(_plates[k])}", _plates[k]) for k in ORDER if k in _plates]
if d.FLOPPY:
    PLATES.append(("floppy_test_gauge", [("floppy_test_gauge", d.floppy_test_gauge(), I3)]))
    PLATES.append(("eject_test_buttons", [(f"eject_test_{s:g}", d.button_eject(s, k + 1), I3)
                                          for k, s in enumerate(d.EJECT_SLOTS_TEST)]))


def mesh(shape, R, name=""):
    s = shape.val() if hasattr(shape, "val") else shape
    vs, ts = s.tessellate(0.02, 0.15)
    v = np.array([[p.x, p.y, p.z] for p in vs])
    t = np.array(ts, int)
    # The tessellation gives every face its own vertices. Weld them, so the mesh is closed and a slicer
    # does not have to guess how the outlines of a layer join up.
    _, first, inv = np.unique(np.round(v, 5), axis=0, return_index=True, return_inverse=True)
    v, t = v[first], inv.reshape(-1)[t]
    t = t[(t[:, 0] != t[:, 1]) & (t[:, 1] != t[:, 2]) & (t[:, 2] != t[:, 0])]
    e = np.concatenate([t[:, [0, 1]], t[:, [1, 2]], t[:, [2, 0]]])
    fwd = set(map(tuple, e))
    if len(fwd) != len(e) or any((b, a) not in fwd for a, b in fwd):
        print(f"warning: the mesh of {name} is not closed", file=sys.stderr)
    return v @ R.T, t


cols = int(math.ceil(math.sqrt(len(PLATES))))
objs, items, cfg_obj, cfg_plate = [], [], [], []
oid = 0
for pi, (pname, parts) in enumerate(PLATES):
    col, row = pi % cols, pi // cols
    cx, cy = col * STRIDE_X + BED_X / 2, -row * STRIDE_Y + BED_Y / 2
    inst = []
    n = len(parts)
    for k, (name, shape, R) in enumerate(parts):
        v, t = mesh(shape, R, name)
        mn, mx = v.min(0), v.max(0)
        v = v - [(mn[0] + mx[0]) / 2, (mn[1] + mx[1]) / 2, mn[2]]      # centred in XY, standing on Z = 0
        mid, wid = oid + 1, oid + 2
        oid += 2
        vx = "".join(f'<vertex x="{a:.5f}" y="{b:.5f}" z="{c:.5f}"/>' for a, b, c in v)
        tx = "".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in t)
        objs.append(f'<object id="{mid}" type="model"><mesh><vertices>{vx}</vertices><triangles>{tx}</triangles></mesh></object>')
        objs.append(f'<object id="{wid}" type="model"><components><component objectid="{mid}" transform="1 0 0 0 1 0 0 0 1 0 0 0"/></components></object>')
        oy = (k - (n - 1) / 2) * ((mx[1] - mn[1]) + 15.0)
        items.append(f'<item objectid="{wid}" transform="1 0 0 0 1 0 0 0 1 {cx:.4f} {cy + oy:.4f} 0" printable="1"/>')
        cfg_obj.append(f'''  <object id="{wid}">
    <metadata key="name" value="{name}"/>
    <metadata key="extruder" value="1"/>
    <part id="{mid}" subtype="normal_part">
      <metadata key="name" value="{name}"/>
      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>
    </part>
  </object>''')
        inst.append(f'''    <model_instance>
      <metadata key="object_id" value="{wid}"/>
      <metadata key="instance_id" value="0"/>
      <metadata key="identify_id" value="{100 + wid}"/>
    </model_instance>''')
        print(f"plate {pi+1} {name}: {len(v)} points, {len(t)} triangles, {mx[0]-mn[0]:.1f} x {mx[1]-mn[1]:.1f} x {mx[2]-mn[2]:.1f}")
        assert mx[0] - mn[0] < BED_X and mx[1] - mn[1] < BED_Y, name
    cfg_plate.append(f'''  <plate>
    <metadata key="plater_id" value="{pi + 1}"/>
    <metadata key="plater_name" value="{pname}"/>
    <metadata key="locked" value="false"/>
    <metadata key="filament_map_mode" value="Auto For Flush"/>
''' + "\n".join(inst) + "\n  </plate>")

today = datetime.date.today().isoformat()
model = f'''<?xml version="1.0" encoding="UTF-8"?>
<model xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" unit="millimeter" xml:lang="en-US" xmlns:BambuStudio="http://schemas.bambulab.com/package/2021">
 <metadata name="Application">{APP}</metadata>
 <metadata name="BambuStudio:3mfVersion">1</metadata>
 <metadata name="CreationDate">{today}</metadata>
 <metadata name="ModificationDate">{today}</metadata>
 <metadata name="Title">Rook 3K {VER}</metadata>
 <resources>
{chr(10).join(objs)}
 </resources>
 <build>
{chr(10).join(items)}
 </build>
</model>
'''
config = '<?xml version="1.0" encoding="UTF-8"?>\n<config>\n' + "\n".join(cfg_obj) + "\n" + "\n".join(cfg_plate) + "\n</config>\n"
ctypes = '''<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
 <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
 <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
 <Default Extension="png" ContentType="image/png"/>
 <Default Extension="gcode" ContentType="text/x.gcode"/>
</Types>
'''
rels = '''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
</Relationships>
'''
out = os.path.join(OUT_DIR, f"rook3k_{VER}.3mf")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("[Content_Types].xml", ctypes)
    z.writestr("_rels/.rels", rels)
    z.writestr("3D/3dmodel.model", model)
    z.writestr("Metadata/model_settings.config", config)
    for n, b in T_FILES.items():
        z.writestr(n, b)
print("wrote", out)
