# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright (C) 2026 Arnljot Arntsen
"""Lager en Bambu Studio-prosjektfil (.3mf) med en byggeplate per del, ferdig orientert for utskrift.
Bambu Studio laster bare plateinndelingen naar filen har prosjektinnstillinger, saa de hentes fra et
prosjekt lagret i Bambu Studio (bambu_template.3mf).
Usage: python src/make_3mf.py <version> [template.3mf] [output_dir]
  version      label used in the file name, e.g. v0.21
  template.3mf project saved from Bambu Studio; default bambu_template.3mf in the repository root
  output_dir   default: the repository root"""
import os, sys, zipfile, datetime, math
import numpy as np
import cadquery as cq
import denise_itx_case as d

VER = sys.argv[1] if len(sys.argv) > 1 else "vX"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # repository root, the parent of src/
TEMPLATE = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "bambu_template.3mf")
OUT_DIR = sys.argv[3] if len(sys.argv) > 3 else ROOT
import json, re
_t = zipfile.ZipFile(TEMPLATE)
T_FILES = {n: _t.read(n) for n in ("Metadata/project_settings.config", "Metadata/slice_info.config", "Metadata/filament_sequence.json") if n in _t.namelist()}
_ps = json.loads(T_FILES["Metadata/project_settings.config"])
_area = [tuple(float(v) for v in p.split("x")) for p in _ps["printable_area"]]
APP = re.search(r'<metadata name="Application">([^<]*)<', _t.read("3D/3dmodel.model").decode()).group(1)
print("mal:", _ps.get("printer_settings_id"), _ps["printable_area"], APP)
BED_X, BED_Y = max(a[0] for a in _area), max(a[1] for a in _area)   # fra malen
STRIDE_X, STRIDE_Y = BED_X * 1.2, BED_Y * 1.2   # Bambu Studio legger platene i rutenett med 20 % mellomrom

RX_M = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]], float)     # +Y (bak) ned mot plata
RX_P = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]], float)     # -Y (front) ned mot plata
RY_M = np.array([[0, 0, -1], [0, 1, 0], [1, 0, 0]], float)     # -X (venstre) ned mot plata
RY_P = np.array([[0, 0, 1], [0, 1, 0], [-1, 0, 0]], float)     # +X (hoyre) ned mot plata
I3 = np.eye(3)

# (platenavn, [(delnavn, shape, rotasjon), ...])
PLATES = [
    ("frontpanel", [("frontpanel", d.front_panel(), RX_M)]),
    ("u_brakett", [("u_brakett", d.u_bracket(), RY_P)]),
    ("sidepanel_venstre", [("sidepanel_venstre", d.side_panel(), RY_M)]),
    ("bakpanel", [("bakpanel", d.rear_panel(), RX_M)]),
    ("fot", [("fot", d.foot(), I3)]),
    ("knapp_power", [("knapp_power", d.button(0), RX_P)]),
    ("knapp_reset", [("knapp_reset", d.button(1), RX_P)]),
    ("zorro_blindlokk x2", [("zorro_blindlokk_1", d.zorro_cover(0), RX_M), ("zorro_blindlokk_2", d.zorro_cover(1), RX_M)]),
    ("testbit_floppyhull", [("testbit_floppyhull", d.floppy_testbit(), I3)]),
]


def mesh(shape, R):
    s = shape.val() if hasattr(shape, "val") else shape
    vs, ts = s.tessellate(0.02, 0.15)
    v = np.array([[p.x, p.y, p.z] for p in vs]) @ R.T
    return v, np.array(ts, int)


cols = int(math.ceil(math.sqrt(len(PLATES))))
objs, items, cfg_obj, cfg_plate = [], [], [], []
oid = 0
for pi, (pname, parts) in enumerate(PLATES):
    col, row = pi % cols, pi // cols
    cx, cy = col * STRIDE_X + BED_X / 2, -row * STRIDE_Y + BED_Y / 2
    inst = []
    n = len(parts)
    for k, (name, shape, R) in enumerate(parts):
        v, t = mesh(shape, R)
        mn, mx = v.min(0), v.max(0)
        v = v - [(mn[0] + mx[0]) / 2, (mn[1] + mx[1]) / 2, mn[2]]      # sentrert i XY, staar paa Z = 0
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
        print(f"plate {pi+1} {name}: {len(v)} punkter, {len(t)} trekanter, {mx[0]-mn[0]:.1f} x {mx[1]-mn[1]:.1f} x {mx[2]-mn[2]:.1f}")
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
 <metadata name="Title">DeniseITX kabinett {VER}</metadata>
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
out = os.path.join(OUT_DIR, f"DeniseITX_kabinett_{VER}.3mf")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("[Content_Types].xml", ctypes)
    z.writestr("_rels/.rels", rels)
    z.writestr("3D/3dmodel.model", model)
    z.writestr("Metadata/model_settings.config", config)
    for n, b in T_FILES.items():
        z.writestr(n, b)
print("skrev", out)
