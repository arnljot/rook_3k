"""
Denise ITX staaende kabinett, konsept v0.9 (CadQuery).

Koordinater: X mot hoyre sett forfra, Y bakover (front = 0), Z opp (kabinettkropp bunn = 0).
Hovedkortet staar paa hoykant paa hoyre vegg, komponentsiden mot venstre,
portene bak og Zorro-slottene nederst.

Kjor:  python denise_itx_case.py   (skriver STEP/STL til ./out)
Alle maal i mm. Maal merket ESTIMAT maa kontrolleres med skyvelaer.
"""
import os
import cadquery as cq
from cadquery import Vector as V

# ---------------------------------------------------------------- parametre
W = 117.0           # utvendig bredde
D = 195.0           # utvendig dybde (se LESMEG: 181 gaar ikke med 10 mm chamfer)
HB = 225.0          # hoyde kabinettkropp uten fot
R = 4.0             # hjorneradius sett forfra
T = 3.0             # veggtykkelse
T_REAR = 3.0        # bakpanel
FOOT_H = 14.0       # fot
FOOT_INSET = 4.0

# front (Amiga 3000 rotert 90 grader)
REC = 10.0          # dybde chamfer
FLOOR = 2.5         # gods bak sporet
T_FRONT = REC + FLOOR
CHAMFER_W = 20.3    # bredde paa skraa flate fra hver side
SIDE_M = (W - 14.0 - 2 * CHAMFER_W) / 2   # flat kant venstre/hoyre naar feltet er sentrert
LEFT_M = 22.0       # flat kant til venstre for chamferfeltet. Sett lik TOP_M for felt trukket mot venstre
BTN_RIGHT = True   # knapper i hoyre kant i stedet for venstre
BADGE_RIGHT = True # badge nede til hoyre i stedet for venstre
TOP_M = 22.0        # flat kant topp
BOT_M = 45.0        # flat kant bunn
GROOVE = 14.0       # flatt spor i bunn av chamfer
STEEP = 4.0         # bredde paa bratt chamfer topp/bunn
SLOT_L, SLOT_W = 100.0, 8.0          # diskaapning
EJECT_L, EJECT_W = 21.0, 5.0         # eject-knapp ESTIMAT plassering
EJECT_DX = 11.0     # eject senter i X relativt til sporets senter ESTIMAT
EJECT_FROM_TOP = 16.5                # eject senter under ovre ende av diskaapning ESTIMAT
LED_TOP_GAP = 2.0   # fra toppen av sporet til forste LED
LED_PITCH = 7.0
BTN_POCKET_D = 3.0  # fordypning for power/reset i venstre kant
BTN_W = 7.0         # knappene staar paa hoykant
BTN_PWR_L, BTN_RST_L = 15.0, 10.0
BTN_GAP, BTN_EDGE = 2.0, 2.5
DECO_W, DECO_D = 1.8, 0.5       # pyntespor
DECO_END = 1.0                  # sporet stopper saa langt fra chamferens topp- og bunnkant
BADGE, BADGE_MARGIN, BADGE_D = 25.0, 1.0, 1.0   # fordypning for 25 x 25 pc-badge
BADGE_X, BADGE_Z = 6.5, 6.5     # fra siden (eller fra knappefordypningen) og fra underkant front
BTN_LOW = True                  # knappefordypningen nede, underkant paa linje med badge-fordypningen
BTN_XC = 7.5        # knappenes senter fra venstre side. MX-bryteren maa da staa ca 3,6 mm til hoyre for knappen
BTN_OUT = 3.5       # knapp stikker ut foran fronten i hvile
BTN_CLEAR = 0.3
LED_W, LED_L = 2.2, 5.0              # LED-vinduer i sporet (forslag)

# hovedkort (Mini-ITX 170 x 170)
PCB = 170.0
PCB_T = 1.6
STANDOFF = 6.0
BOARD_Z0 = 15.0     # Zorro-kanten av kortet over kroppens bunn
IO_AP_W, IO_AP_H = 158.75, 44.45   # ATX I/O-aapning
IO_BELOW_PCB = 2.24                # aapningens kant under PCB-undersiden (ATX)
IO_CENTER_U = 92.2                 # aapningens senter maalt fra Zorro-kanten ESTIMAT (tilpasset skjoldets hull mot kortbildet)
IO_FLANGE, IO_FLANGE_T = 2.0, 1.5  # skjoldets flens
IO_CLEAR = 0.2
IO_GAP = 1.0        # PCB bakkant til innside bakpanel ESTIMAT
COMP_H = 14.0       # hoyeste vanlige komponent ESTIMAT
ITX_HOLES = [(6.35, 10.16), (163.83, 33.02), (6.35, 165.1), (163.83, 165.1)]  # (u fra Zorro-kant, v fra bakkant)

# floppy standard 3,5"
FD_W, FD_H, FD_L = 101.6, 25.4, 146.0
FD_SLOT_FROM_TOP = 9.0 + 3.3 / 2   # 9 mm fra lokket til disken (maalt), pluss halv disktykkelse
PICO_H, PICO_T, PICO_W = 36.0, 23.0, 45.0   # PicoPSU over hovedkortet, tykkelse, bredde (maalt)
PICO_OVERHANG = 2.5      # PicoPSU ut over forkanten av hovedkortet (maalt, ca)
DOM_H = 49.0             # disk on module paa akseleratorkortet, over hovedkortet (maalt)

# skruer M3
PILOT = 2.6
CLEAR = 3.4

Y_TUBE0 = T_FRONT
Y_TUBE1 = D - T_REAR
X_SPLIT = 4.0       # deling mellom venstre sidepanel og U-brakett
X_PCB = W - T - STANDOFF - PCB_T      # komponentsiden av PCB
Y_PCB_REAR = Y_TUBE1 - IO_GAP
Y_PCB_FRONT = Y_PCB_REAR - PCB
RIGHT_M = W - LEFT_M - 2 * CHAMFER_W - 14.0
XC = LEFT_M + CHAMFER_W + 7.0      # senter av sporet og diskaapningen
Z_REC0, Z_REC1 = BOT_M, HB - TOP_M
Z_GROOVE1 = Z_REC1 - STEEP
Z_LEDS = [Z_GROOVE1 - LED_TOP_GAP - LED_L / 2 - i * LED_PITCH for i in range(2)]
Z_SLOT1 = Z_LEDS[-1] - LED_L / 2 - 3.5      # diskaapning loftet opp under LED-ene
ZC_SLOT = Z_SLOT1 - SLOT_L / 2

RIB = 8.0
RIB_Z = [(T, T + RIB), (HB - T - RIB, HB - T)]
RIB_Y = [(Y_TUBE0, Y_TUBE0 + RIB), (Y_TUBE1 - RIB, Y_TUBE1)]
PANEL_SCREW_X = [25.0, W - 25.0]


# ---------------------------------------------------------------- hjelpere
def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def cyl(p, d, r, h):
    return cq.Solid.makeCylinder(r, h, V(*p), V(*d))


def rounded(y0, y1, inset=0.0, r=R):
    b = box(inset, W - inset, y0, y1, inset, HB - inset)
    return b.edges("|Y").fillet(r)


def rect_wire(y):
    t = y / REC
    side = CHAMFER_W * t
    x0, x1 = LEFT_M + side, W - RIGHT_M - side
    z0, z1 = Z_REC0 + STEEP * t, Z_REC1 - STEEP * t
    pts = [V(x0, y, z0), V(x1, y, z0), V(x1, y, z1), V(x0, y, z1), V(x0, y, z0)]
    return cq.Wire.makePolygon(pts)


def button_layout():
    # venstre kant, fordypningen aapen ut mot venstre side
    ph = 2 * BTN_EDGE + BTN_PWR_L + BTN_GAP + BTN_RST_L
    pz1 = BADGE_Z + ph if BTN_LOW else Z_REC1
    pz0 = pz1 - ph
    z = pz1 - BTN_EDGE
    holes = []
    for l in (BTN_PWR_L, BTN_RST_L):
        xc = W - BTN_XC if BTN_RIGHT else BTN_XC
        holes.append((xc - BTN_W / 2, xc + BTN_W / 2, z - l, z))
        z -= l + BTN_GAP
    if BTN_RIGHT:
        return (xc - BTN_W / 2 - BTN_EDGE, W + 1.0, pz0, pz1), holes
    return (-1.0, xc + BTN_W / 2 + BTN_EDGE, pz0, pz1), holes


def ref_buttons():
    # knappetopper i hvileposisjon, kun for visning
    return [box(x0, x1, -BTN_OUT, BTN_POCKET_D + 2, z0, z1) for (x0, x1, z0, z1) in button_layout()[1]]


# ---------------------------------------------------------------- deler
def front_panel():
    p = rounded(0, T_FRONT)
    recess = cq.Solid.makeLoft([rect_wire(-1.0), rect_wire(REC)], True)
    p = p.cut(recess)
    # diskaapning i sporet
    p = p.cut(box(XC - SLOT_W / 2, XC + SLOT_W / 2, -1, T_FRONT + 1, ZC_SLOT - SLOT_L / 2, ZC_SLOT + SLOT_L / 2))
    # eject paa hoyre chamfer, floppy staar med lokket mot venstre
    ez = Z_SLOT1 - EJECT_FROM_TOP
    ex = XC + EJECT_DX
    p = p.cut(box(ex - EJECT_W / 2, ex + EJECT_W / 2, -1, T_FRONT + 1, ez - EJECT_L / 2, ez + EJECT_L / 2))
    # LED-vinduer i toppen av sporet
    for z in Z_LEDS:
        p = p.cut(box(XC - LED_W / 2, XC + LED_W / 2, -1, T_FRONT + 1, z - LED_L / 2, z + LED_L / 2))
    # fordypning med staaende power- og resetknapp i venstre kant
    (px0, px1, pz0, pz1), holes = button_layout()
    p = p.cut(box(px0, px1, -1, BTN_POCKET_D, pz0, pz1))
    for (x0, x1, z0, z1) in holes:
        c = BTN_CLEAR
        p = p.cut(box(x0 - c, x1 + c, -1, T_FRONT + 1, z0 - c, z1 + c))
    # pyntespor midt i venstre chamfer, 0,5 dypt vinkelrett paa flaten
    import math
    dy = DECO_D * math.hypot(REC, CHAMFER_W) / CHAMFER_W
    gx = LEFT_M + CHAMFER_W / 2 - DECO_W / 2
    shifted = cq.Solid.makeLoft([rect_wire(-1.0), rect_wire(REC)], True).translate(V(0, dy, 0))
    def zlim(x):
        t = (x - LEFT_M) / CHAMFER_W
        return Z_REC0 + STEEP * t + DECO_END, Z_REC1 - STEEP * t - DECO_END
    (a0, a1), (b0, b1) = zlim(gx), zlim(gx + DECO_W)
    strip = (cq.Workplane("XZ").polyline([(gx, a0), (gx + DECO_W, b0), (gx + DECO_W, b1), (gx, a1)]).close()
             .extrude(-T_FRONT).translate((0, -1, 0)))
    p = p.cut(cq.Workplane("XY").add(shifted).intersect(strip))
    # fordypning for pc-badge nede til venstre
    bs = BADGE + 2 * BADGE_MARGIN
    bx0 = W - BADGE_X - bs if BADGE_RIGHT else BADGE_X
    if BTN_LOW and BTN_RIGHT and BADGE_RIGHT:
        bx0 = px0 - BADGE_X - bs
    p = p.cut(box(bx0, bx0 + bs, -1, BADGE_D, BADGE_Z, BADGE_Z + bs).edges("|Y").fillet(1.5))
    # pilothull bak for skruer gjennom ribbene i U-braketten
    for (z0, z1) in RIB_Z:
        for x in PANEL_SCREW_X:
            p = p.cut(cyl((x, T_FRONT - 8.0, (z0 + z1) / 2), (0, 1, 0), PILOT / 2, 9.0))
    return p


def _ring():
    return rounded(Y_TUBE0, Y_TUBE1).cut(rounded(Y_TUBE0 - 1, Y_TUBE1 + 1, inset=T, r=1.0))


def u_bracket():
    u = _ring().intersect(box(X_SPLIT, W + 1, 0, D, -1, HB + 1))
    # ribber i topp og bunn, foran og bak: feste for front, bakpanel og sidepanel
    for (y0, y1) in RIB_Y:
        for (z0, z1) in RIB_Z:
            u = u.union(box(X_SPLIT, W - T, y0, y1, z0, z1))
    for iy, (y0, y1) in enumerate(RIB_Y):
        for (z0, z1) in RIB_Z:
            yc, zc = (y0 + y1) / 2, (z0 + z1) / 2
            # sidepanelskrue inn i ribbeenden
            u = u.cut(cyl((X_SPLIT - 1, yc, zc), (1, 0, 0), PILOT / 2, 13.0))
            for x in PANEL_SCREW_X:
                if iy == 0:   # front: skrue innenfra gjennom ribben
                    u = u.cut(cyl((x, y0 - 1, zc), (0, 1, 0), CLEAR / 2, RIB + 2))
                else:         # bak: pilothull for skrue utenfra
                    u = u.cut(cyl((x, y0 - 1, zc), (0, 1, 0), PILOT / 2, RIB + 2))
    # avstandsstykker for hovedkortet
    for (uu, vv) in ITX_HOLES:
        y, z = Y_PCB_REAR - vv, BOARD_Z0 + uu
        u = u.union(cyl((W - T - STANDOFF, y, z), (1, 0, 0), 4.0, STANDOFF + 0.5))
        u = u.cut(cyl((W - T - STANDOFF - 1, y, z), (1, 0, 0), PILOT / 2, STANDOFF + 2.5))
    # luftinntak i bunn, over foten
    y = 30.0
    while y < Y_TUBE1 - 20:
        u = u.cut(box(16, W - 15, y, y + 4.0, -1, T + 1))
        y += 9.0
    # hull for fotskruer
    for (x, yy) in FOOT_SCREWS:
        u = u.cut(cyl((x, yy, -1), (0, 0, 1), CLEAR / 2, T + 2))
    return u


FOOT_SCREWS = [(10.0, 27.0), (W - 10.0, 27.0), (10.0, 176.0), (W - 10.0, 176.0)]


def side_panel():
    s = _ring().intersect(box(-1, X_SPLIT, 0, D, -1, HB + 1))
    for (y0, y1) in RIB_Y:
        for (z0, z1) in RIB_Z:
            yc, zc = (y0 + y1) / 2, (z0 + z1) / 2
            s = s.cut(cyl((-1, yc, zc), (1, 0, 0), CLEAR / 2, T + 3))
            s = s.cut(cq.Solid.makeCone(3.2, CLEAR / 2, 1.7, V(0, yc, zc), V(1, 0, 0)))
    return s


def rear_panel():
    p = rounded(Y_TUBE1, D)
    y0, y1 = Y_TUBE1 - 1, D + 1
    # standard ITX I/O-aapning for DeniseITX I/O-skjoldet (162,75 x 48,45, kant 158,5 x 44,5)
    ax1 = W - T - STANDOFF + IO_BELOW_PCB           # 2,24 under PCB-undersiden
    ax0 = ax1 - IO_AP_H
    az0 = BOARD_Z0 + IO_CENTER_U - IO_AP_W / 2
    az1 = az0 + IO_AP_W
    c = IO_CLEAR
    p = p.cut(box(ax0 - c, ax1 + c, y0, y1, az0 - c, az1 + c))
    f = IO_FLANGE + c
    p = p.cut(box(ax0 - f, ax1 + f, y0, Y_TUBE1 + IO_FLANGE_T, az0 - f, az1 + f))   # forsenkning for flensen paa innsiden
    # DC-inntak for PicoPSU
    p = p.cut(cyl((25.0, y0, 100.0), (0, 1, 0), 4.0, T_REAR + 2))
    # avtrekk oppe til venstre
    z = 125.0
    while z < HB - 16:
        p = p.cut(box(10, ax0 - 8, y0, y1, z, z + 3.0))
        z += 7.0
    for (z0, z1) in RIB_Z:
        for x in PANEL_SCREW_X:
            p = p.cut(cyl((x, y0, (z0 + z1) / 2), (0, 1, 0), CLEAR / 2, T_REAR + 2))
    return p


def foot():
    x0, x1, y0, y1 = FOOT_INSET, W - FOOT_INSET, FOOT_INSET, D
    rw = 6.0
    fin_t, gap = 3.0, 2.5
    f = None
    z = -FOOT_H
    while z < -0.1:
        fin = box(x0, x1, y0, y1, z, z + fin_t).cut(box(x0 + rw, x1 - rw, y0 + rw, y1 - rw, z - 1, z + fin_t + 1))
        f = fin if f is None else f.union(fin)
        z += fin_t + gap
    # stolper som baerer lamellene, ca 28 mm mellom
    n = 6
    for i in range(n + 1):
        y = y0 + (y1 - y0 - 4.0) * i / n
        f = f.union(box(x0 + 1.5, x0 + rw, y, y + 4.0, -FOOT_H, 0))
        f = f.union(box(x1 - rw, x1 - 1.5, y, y + 4.0, -FOOT_H, 0))
    for i in range(1, 3):
        x = x0 + (x1 - x0 - 4.0) * i / 3
        for ya in (y0, y1 - rw):
            f = f.union(box(x, x + 4.0, ya + 1.5 if ya == y0 else ya, ya + rw if ya == y0 else ya + rw - 1.5, -FOOT_H, 0))
    for (x, y) in FOOT_SCREWS:
        f = f.union(box(x - 5, x + 5, y - 5, y + 5, -FOOT_H, 0).intersect(box(x0 + 1.5, x1 - 1.5, y0, y1, -FOOT_H, 0)))
        f = f.cut(cyl((x, y, -10.0), (0, 0, 1), PILOT / 2, 11.0))
    return f


# ---------------------------------------------------------------- referansevolumer (skrives ikke ut)
def ref_board():
    pcb = box(X_PCB, X_PCB + PCB_T, Y_PCB_FRONT, Y_PCB_REAR, BOARD_Z0, BOARD_Z0 + PCB)
    comp = box(X_PCB - COMP_H, X_PCB, Y_PCB_FRONT + 2, Y_PCB_REAR, BOARD_Z0 + 2, BOARD_Z0 + PCB - 2)
    return pcb, comp


def ref_floppy():
    xl = XC - FD_SLOT_FROM_TOP          # lokket mot venstre
    return box(xl, xl + FD_H, T_FRONT, T_FRONT + FD_L, ZC_SLOT - FD_W / 2, ZC_SLOT + FD_W / 2)


def ref_picopsu():
    # ATX CN1: u 103..153, v 157..167 ESTIMAT fra kortbildet.
    # PicoPSU maalt: 36 over kortet, 23 tykk, 45 bred, henger ca 2,5 ut over forkanten av kortet.
    return box(X_PCB - PICO_H, X_PCB, Y_PCB_FRONT - PICO_OVERHANG, Y_PCB_FRONT - PICO_OVERHANG + PICO_T,
               BOARD_Z0 + 103.0, BOARD_Z0 + 103.0 + PICO_W)


def ref_zorro(card_h=70.0):
    cards = []
    for u in (5.4, 20.4):               # slottposisjoner ESTIMAT fra kortbildet
        cards.append(box(X_PCB - 5.0 - card_h, X_PCB - 5.0, Y_PCB_FRONT, Y_PCB_REAR, BOARD_Z0 + u - 0.8, BOARD_Z0 + u + 0.8))
    return cards


PARTS = {
    "frontpanel": (front_panel, (0.85, 0.83, 0.78)),
    "u_brakett": (u_bracket, (0.75, 0.73, 0.68)),
    "sidepanel_venstre": (side_panel, (0.75, 0.73, 0.68)),
    "bakpanel": (rear_panel, (0.45, 0.45, 0.45)),
    "fot": (foot, (0.45, 0.45, 0.45)),
}

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
    os.makedirs(out, exist_ok=True)
    asm = cq.Assembly(name="DeniseITX_kabinett")
    for name, (fn, col) in PARTS.items():
        s = fn()
        cq.exporters.export(s, os.path.join(out, f"{name}.step"))
        cq.exporters.export(s, os.path.join(out, f"{name}.stl"), tolerance=0.05, angularTolerance=0.2)
        asm.add(s, name=name, color=cq.Color(*col))
    pcb, comp = ref_board()
    asm.add(pcb, name="REF_hovedkort", color=cq.Color(0.4, 0.1, 0.4))
    asm.add(comp, name="REF_komponentsone", color=cq.Color(0.6, 0.3, 0.8, 0.3))
    asm.add(ref_floppy(), name="REF_floppy", color=cq.Color(0.8, 0.7, 0.5))
    for i, b in enumerate(ref_buttons()):
        asm.add(b, name=f"REF_knapp{i+1}", color=cq.Color(0.9, 0.88, 0.82))
    asm.add(ref_picopsu(), name="REF_picopsu", color=cq.Color(0.9, 0.8, 0.1))
    for i, c in enumerate(ref_zorro()):
        asm.add(c, name=f"REF_zorro{i+1}", color=cq.Color(0.1, 0.6, 0.2))
    asm.save(os.path.join(out, "DeniseITX_kabinett_v0.9.step"))
    print("ok", out)
