# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright (C) 2026 Arnljot Arntsen
"""Renders the pictures used in the README from the model: two sheets of line drawings and one shaded picture.
Usage: python src/render.py [output_dir]
  output_dir   default: out/ in the repository root
Options are read from config.txt in the repository root, or from the file given with --config <file>.
Needs cairosvg and Pillow besides CadQuery. The shaded picture is drawn with VTK, which comes with CadQuery."""
import os, sys, tempfile, warnings
warnings.filterwarnings("ignore")
import numpy as np
import cadquery as cq
import cairosvg
import vtk
from vtkmodules.util import numpy_support as ns
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont
import rook3k as d

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(d.ROOT, "out")
TMP = tempfile.mkdtemp()
PARTS = {n: f().val() for n, (f, _) in d.PARTS.items()}
d.check_clearances()


def pick(*bases):
    """The parts whose kind is one of the given names, in model order."""
    return [s for n, s in PARTS.items() if d.base_name(n) in bases]


# ---------------------------------------------------------------- line drawings
def line_view(shapes, eye, w=900, h=1000):
    """Hidden-line drawing of the shapes seen from the direction eye, as a picture."""
    n = np.array(eye, float); n /= np.linalg.norm(n)
    rt = np.cross([0, 0, 1], n); rt /= np.linalg.norm(rt); up = np.cross(n, rt)
    m = cq.Matrix([list(rt) + [0], list(up) + [0], list(n) + [0]])
    c = cq.Compound.makeCompound(shapes).transformGeometry(m)
    svg, png = os.path.join(TMP, "v.svg"), os.path.join(TMP, "v.png")
    cq.exporters.export(c, svg, opt={"width": w, "height": h, "marginLeft": 30, "marginTop": 30, "projectionDir": (0, 0, 1),
                                      "showAxes": False, "showHidden": False, "strokeWidth": 0.35})
    cairosvg.svg2png(url=svg, write_to=png, background_color="white", scale=1.3)
    return Image.open(png).convert("RGB")


def font(size):
    for name in ("DejaVuSans.ttf", "arial.ttf", "Arial.ttf", "Helvetica.ttc"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def sheet(views, path):
    """Several labelled views side by side, cropped below the lowest line."""
    f = font(30)
    h = max(im.height for im, _ in views) + 60
    s = Image.new("RGB", (sum(im.width for im, _ in views), h), "white")
    dr = ImageDraw.Draw(s); x = 0
    for im, label in views:
        s.paste(im, (x, 60)); dr.text((x + 30, 14), label, fill=(40, 40, 40), font=f); x += im.width
    bb = ImageChops.difference(s, Image.new("RGB", s.size, "white")).getbbox()
    s.crop((0, 0, s.width, min(s.height, bb[3] + 40))).save(path)


def reference_volumes():
    pcb, _ = d.ref_board()
    refs = [m.val() for m in d.ref_mx()] + [pcb.val(), d.ref_picopsu().val()] + [c.val() for c in d.ref_zorro()]
    if d.FLOPPY:
        refs.append(d.ref_floppy().val())
    if d.SSD:
        refs.append(d.ref_ssd().val())
    return refs


def line_drawings():
    everything = list(PARTS.values())
    feet = pick("foot", "foot_pad", "tpu_pad")
    buttons = pick("button_power", "button_reset")
    open_case = pick("front_panel", "u_bracket", "rear_panel") + feet + buttons + reference_volumes()
    sheet([(line_view(pick("front_panel") + feet + buttons, (0, -1, 0), 500, 1000), "Front"),
           (line_view(everything, (-0.7, -1, 0.45)), "Front left"),
           (line_view(open_case, (-1, -0.55, 0.3), 1000, 1000), "Inside, side panel removed"),
           (line_view(everything, (-0.6, 1, 0.35)), "Rear")], os.path.join(OUT, "rook3k_overview.png"))
    rear, covers = pick("rear_panel"), pick("zorro_cover")
    views = [(line_view(rear, (0, 1, 0), 600, 1000), "Rear panel, outside")]
    if covers:
        views.append((line_view(rear + covers, (0.55, -1, 0.3), 800, 1000), "Inside, with Zorro covers"))
    views.append((line_view(rear, (0.55, -1, 0.3), 800, 1000), "Inside" + (", covers removed" if covers else "")))
    sheet(views, os.path.join(OUT, "rook3k_rear_panel.png"))


# ---------------------------------------------------------------- shaded picture
BEIGE, DARK, LIGHT = (0.86, 0.83, 0.76), (0.74, 0.71, 0.64), (0.93, 0.91, 0.86)
COLOUR = {"rear_panel": DARK, "foot": DARK, "foot_pad": DARK, "tpu_pad": (0.2, 0.2, 0.2), "zorro_cover": DARK,
          "button_power": LIGHT, "button_reset": LIGHT}


def polydata(shape):
    """A shape as triangles: with smoothed normals for shading, and as it is for finding the sharp edges."""
    vs, ts = shape.tessellate(0.03, 0.08)
    pts = vtk.vtkPoints(); pts.SetData(ns.numpy_to_vtk(np.array([[p.x, p.y, p.z] for p in vs], float), deep=True))
    cells = vtk.vtkCellArray()
    arr = np.hstack([np.full((len(ts), 1), 3), np.array(ts)]).astype(np.int64).ravel()
    cells.SetCells(len(ts), ns.numpy_to_vtkIdTypeArray(arr, deep=True))
    pd = vtk.vtkPolyData(); pd.SetPoints(pts); pd.SetPolys(cells)
    clean = vtk.vtkCleanPolyData(); clean.SetInputData(pd); clean.Update()
    nrm = vtk.vtkPolyDataNormals(); nrm.SetInputConnection(clean.GetOutputPort())
    nrm.SetFeatureAngle(18); nrm.SplittingOn(); nrm.ConsistencyOn(); nrm.AutoOrientNormalsOn(); nrm.Update()
    return nrm.GetOutput(), clean.GetOutput()


def shaded_view(eye, size=(2800, 3400), dist=820):
    """The whole case seen from the direction eye, rendered at twice the final size."""
    ren = vtk.vtkRenderer(); ren.SetBackground(0.93, 0.93, 0.92); ren.SetBackground2(0.99, 0.99, 0.98); ren.GradientBackgroundOn()
    for name, shape in PARTS.items():
        smooth, raw = polydata(shape)
        mp = vtk.vtkPolyDataMapper(); mp.SetInputData(smooth); a = vtk.vtkActor(); a.SetMapper(mp)
        p = a.GetProperty(); p.SetColor(*COLOUR.get(d.base_name(name), BEIGE))
        p.SetAmbient(0.34); p.SetDiffuse(0.70); p.SetSpecular(0.10); p.SetSpecularPower(18)
        ren.AddActor(a)
        fe = vtk.vtkFeatureEdges(); fe.SetInputData(raw); fe.BoundaryEdgesOff(); fe.NonManifoldEdgesOff(); fe.ManifoldEdgesOff()
        fe.FeatureEdgesOn(); fe.SetFeatureAngle(40); fe.ColoringOff()
        em = vtk.vtkPolyDataMapper(); em.SetInputConnection(fe.GetOutputPort()); em.SetResolveCoincidentTopologyToPolygonOffset()
        ea = vtk.vtkActor(); ea.SetMapper(em)
        ea.GetProperty().SetColor(0.28, 0.27, 0.25); ea.GetProperty().SetLineWidth(2.4); ea.GetProperty().SetOpacity(0.55)
        ren.AddActor(ea)
    c = np.array([d.W / 2, d.D / 2, d.HB / 2 - 7.0]); e = np.array(eye, float); e /= np.linalg.norm(e)
    cam = ren.GetActiveCamera(); cam.SetFocalPoint(*c); cam.SetPosition(*(c + e * dist)); cam.SetViewUp(0, 0, 1); cam.SetViewAngle(28)
    ren.ResetCameraClippingRange()
    # three lights that follow the camera: a key light, a fill light and one from above
    ren.RemoveAllLights()
    up = np.array([0, 0, 1.0]); right = np.cross(-e, up); right /= np.linalg.norm(right)
    for v, inten in ((e * 0.8 + right * 0.45 + up * 0.5, 0.80), (e * 0.5 - right * 0.9 + up * 0.2, 0.50), (e * 0.2 + up * 1.0, 0.35)):
        lt = vtk.vtkLight(); lt.SetLightTypeToSceneLight(); lt.SetPosition(*(c + v * 800)); lt.SetFocalPoint(*c)
        lt.SetIntensity(inten); lt.SetPositional(False); ren.AddLight(lt)
    rw = vtk.vtkRenderWindow(); rw.SetOffScreenRendering(1); rw.SetSize(*size); rw.SetMultiSamples(0); rw.AddRenderer(ren)

    def grab(zbuffer=False):
        rw.Render()
        w = vtk.vtkWindowToImageFilter(); w.SetInput(rw)
        if zbuffer:
            w.SetInputBufferTypeToZBuffer()
        else:
            w.SetInputBufferTypeToRGB()
        w.ReadFrontBufferOff(); w.Update()
        img = w.GetOutput(); dx, dy, _ = img.GetDimensions()
        return ns.vtk_to_numpy(img.GetPointData().GetScalars()).reshape(dy, dx, -1)[::-1].astype(np.float32)

    plain = grab(); depth = grab(True)[..., 0]
    # ambient occlusion darkens recesses and slots. It works from the depth picture and leaves dark smudges along the
    # outline of the case, so it is rendered separately and only applied a little way inside the outline.
    basic = vtk.vtkRenderStepsPass(); ao = vtk.vtkSSAOPass()
    ao.SetRadius(22); ao.SetBias(0.6); ao.SetKernelSize(256); ao.BlurOn(); ao.SetDelegatePass(basic); ren.SetPass(ao)
    occluded = grab()
    inside = Image.fromarray(((depth < 0.9999) * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(61)).filter(ImageFilter.GaussianBlur(14))
    k = (np.asarray(inside, np.float32) / 255.0)[..., None]
    ratio = np.clip(occluded / np.maximum(plain, 1.0), 0.0, 1.0)
    return Image.fromarray(np.clip(plain * (1.0 - k + k * ratio), 0, 255).astype(np.uint8))


def shaded_picture():
    a, b = shaded_view((-0.62, -1.0, 0.42)), shaded_view((0.75, 1.0, 0.42))
    s = Image.new("RGB", (a.width + b.width, a.height)); s.paste(a, (0, 0)); s.paste(b, (a.width, 0))
    s.resize((s.width // 2, s.height // 2), Image.LANCZOS).save(os.path.join(OUT, "rook3k_shaded.png"))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    line_drawings()
    shaded_picture()
    print("wrote", OUT)
