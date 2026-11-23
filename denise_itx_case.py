# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright (C) 2026 Arnljot Arntsen
"""
Denise ITX staaende kabinett, konsept v0.21 (CadQuery).

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
D = 210.0           # utvendig dybde (se LESMEG: 181 gaar ikke med 10 mm chamfer)
HB = 227.0          # hoyde kabinettkropp uten fot
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
BTN_PWR_L, BTN_RST_L = 12.0, 8.0     # gir fordypning like hoy som badge-fordypningen (27)
BTN_GAP, BTN_EDGE = 2.0, 2.5
DECO_W, DECO_D = 1.8, 0.5       # pyntespor
DECO_END = 1.0                  # sporet stopper saa langt fra chamferens topp- og bunnkant
BADGE, BADGE_MARGIN, BADGE_D = 25.0, 1.0, 1.0   # fordypning for 25 x 25 pc-badge
BADGE_X, BADGE_Z = 6.5, 6.5     # fra siden (eller fra knappefordypningen) og fra underkant front
BTN_LOW = True                  # knappefordypningen nede, underkant paa linje med badge-fordypningen
BTN_XC = 7.5        # knappenes senter fra venstre side. MX-bryteren maa da staa ca 3,6 mm til hoyre for knappen
BTN_OUT = 3.5       # knapp stikker ut foran fronten i hvile
BTN_CLEAR = 0.3
# MX-brytere bak knappene. Maal etter hukommelsen fra Cherry MX-databladet, kontroller mot faktisk bryter
MX_BODY = 15.6      # hus, kvadratisk
MX_CUT = 14.0       # utsnitt i brakettplate
MX_PLATE_T = 1.5
MX_STEM = 3.6       # stamme over hustopp
MX_TOP = 6.6        # hustopp til overside plate
MX_BELOW = 5.0      # overside plate til bunn av hus
MX_PINS = 3.3
MX_X = W - T - 0.7 - MX_BODY / 2      # brytersenter, saa langt mot hoyre vegg som mulig
MX_Z = [27.5, 11.5]                   # power, reset. 16 mm senteravstand
FOOT_T = 3.0        # knappens fot bak fronten
BOSS_L = 4.0        # tapp med kryssfeste for bryterstammen
Y_MX_TOP = T_FRONT + FOOT_T + BOSS_L           # hustopp
Y_MX_PLATE = Y_MX_TOP + MX_TOP                 # forside brakettplate
Y_MX_END = Y_MX_PLATE + MX_BELOW + MX_PINS     # pinnespisser
RIB_FRONT_BOTTOM_X1 = MX_X - MX_BODY / 2 - 2.0 # nedre fremre ribbe stopper her for aa gi plass til bryterne
# reservert sone for fremtidig SD-kortaapning i hoyre kant (ikke tegnet, bare holdt fri)
SD_Z0, SD_Z1 = T + 35.0, T + 115.0
SD_DEPTH = 26.0     # fra forkant hovedkort og innover
SD_OFFSET = 15.0    # fra undersiden av hovedkortet og ut mot venstre
LED_W, LED_L = 2.2, 5.0              # LED-vinduer i sporet (forslag)

# hovedkort (Mini-ITX 170 x 170)
PCB = 170.0
PCB_T = 1.6
STANDOFF = 6.0
BOARD_Z0 = 15.0     # Zorro-kanten av kortet over kroppens bunn
IO_AP_W, IO_AP_H = 158.75, 44.45   # ATX I/O-aapning
IO_BELOW_PCB = 2.24                # aapningens kant under PCB-undersiden (ATX)
IO_CENTER_U = 92.2                 # aapningens senter maalt fra Zorro-kanten ESTIMAT (tilpasset skjoldets hull mot kortbildet)
IO_FLANGE, IO_FLANGE_T = 2.0, 1.5  # skjoldets flens (ikke lenger i bruk, skjoldet er bygd inn i bakpanelet)
# Gjennomgaaende utsnitt etter DeniseITX I/O-skjoldets utforming, i skjoldets egne koordinater (0..162,75 x 0..48,45)
IO_RECTS = [(16.1, 5.0, 151.25, 18.6), (16.1, 24.5, 100.75, 38.1)]          # (sx0, sy0, sx1, sy1)
IO_CIRCLES = [(157.5, 12.9, 7.5), (9.0, 12.35, 11.5), (9.0, 27.6, 11.5)]    # (sx, sy, diameter)
# Zorro-kort: to slotter, kortplan lest av kortbildet ESTIMAT
ZORRO_U = [5.2, 5.2 + 15.24]       # kortplan fra hovedkortets nedre kant
ZORRO_OPEN_W = 11.0
ZORRO_X0, ZORRO_X1 = 31.0, 91.0    # aapningens utstrekning. Naermere hovedkortet enn 91 er det I/O-utsnitt
# Leppe og blindlokk etter monsteret til et standard PCI-blindlokk (PCI+cover.3mf), smalnet og kortet ned:
# plate mot innsiden av bakpanelet, flik boyd innover i enden lengst fra hovedkortet, skruehull 6,45 over platens
# underside og 1,5 til siden for midten i originalen. Skruen gaar i kortets innskyvingsretning.
LIP_X0, LIP_X1 = 22.9, 29.4        # leppa i X
LIP_D = 10.2                       # hvor langt leppa staar inn fra bakpanelet
LIP_Z = (-2.25, 6.25)              # leppa i Z relativt til kortplanet. Resten av bredden er hals paa lokket
LIP_HOLE_IN = 6.45                 # innsatshull fra bakpanelets innside (som paa standardlokket)
LIP_HOLE_DZ = 2.0                  # innsatshull relativt til kortplanet
COVER_W = 12.5
COVER_T = 1.5
COVER_TAB_H = 13.5
# DC og VGA ligger over Zorro-aapningene, saa det er fritt aa komme til skruene i leppene fra venstre
DC_X, DC_Z, DC_D = 14.0, 52.0, 8.1   # hals maalt til 7,75
DC_REC_D, DC_REC_LEFT = 12.1, 2.0    # fordypning paa innsiden og gods som staar igjen. Hals 4,5 lang, mutter 1,88 tykk
VGA_REC_W, VGA_REC_H, VGA_REC_LEFT = 32.6 + 0.6, 12.7 + 0.6, 1.5   # fordypning for panelkontaktens hus, og gods som staar igjen
VGA_X, VGA_Z = 44.0, 52.0          # DE-15 liggende. Aapning 18 x 10, skruehull 25 fra hverandre ESTIMAT
IO_CLEAR = 0.2
IO_GAP = 1.0        # PCB bakkant til innside bakpanel ESTIMAT
COMP_H = 14.0       # hoyeste vanlige komponent ESTIMAT
ITX_HOLES = [(6.35, 10.16), (163.83, 33.02), (6.35, 165.1), (163.83, 165.1)]  # (u fra Zorro-kant, v fra bakkant)

# floppy standard 3,5"
FD_W, FD_H, FD_L = 101.6, 25.4, 129.0   # lengde = 21 + 60 + 30 + 18 (maalt med skyvelaer, ikke proevd)
FD_SLOT_FROM_TOP = 9.0 + 3.3 / 2   # 9 mm fra lokket til disken (maalt), pluss halv disktykkelse
PICO_H, PICO_T, PICO_W = 36.0, 23.0, 45.0   # PicoPSU over hovedkortet, tykkelse, bredde (maalt)
PICO_OVERHANG = 2.5      # PicoPSU ut over forkanten av hovedkortet (maalt, ca)
DOM_H = 49.0             # disk on module paa akseleratorkortet, over hovedkortet (maalt)

# skruer M3. Messing varmeinnsatser M3 (blindhull): hull 4,0 i diameter, 4 dypt, minst 1,6 gods rundt
INS_D = 4.0
INS_DEPTH = 4.5     # 0,5 ekstra for plast som presses ned foran innsatsen
INS_EXT = 4.0       # smalere forlengelse bak innsatsen, saa skruen ikke bunner
# floppyhylle paa venstre sidepanel
# Noyaktige hull for drivens sidehull, maalt med skyvelaer (ikke proevd): 21, 81 og 111 fra drivens forkant. M3 x 0,5.
FD_HOLES_Y = [21.0, 81.0, 111.0]
FD_HOLE_UP = 5.75                 # hullsenter over drivens bunnplate. Maalt 5,75, usikkert mellom 5,5 og 6. Proeves med testbit
FD_GAP = 0.3                      # luft mellom drivens forkant og baksiden av frontpanelet
FD_REAR_HOLE = FD_HOLES_Y[-1]
SHELF_T = 4.0
SHELF_Y0, SHELF_Y1 = 1.5, FD_REAR_HOLE + 10.0   # hyllas utstrekning bak fronten
GUSSET = 15.0                     # smaa trekanter under hylla
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
def insert_hole(p, d, ext=INS_EXT):
    """Hull for M3 varmeinnsats fra flaten i punkt p, innover i retning d."""
    p0 = [p[i] - 0.5 * d[i] for i in range(3)]
    h = cq.Solid.makeCylinder(INS_D / 2, INS_DEPTH + 0.5, V(*p0), V(*d))
    return h.fuse(cq.Solid.makeCylinder(1.6, INS_DEPTH + 0.5 + ext, V(*p0), V(*d)))


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


def button(i):
    # knapp med fot og tapp for MX-stamme. Skrives ut staaende paa foten.
    (x0, x1, z0, z1) = button_layout()[1][i]
    b = box(x0, x1, -BTN_OUT, T_FRONT, z0, z1)
    lz0 = 1.3 if i == 1 else 0.8
    lz1 = 0.8 if i == 1 else 1.3
    fx0 = min(x0 - 1.3, MX_X - 4.0)
    b = b.union(box(fx0, min(x1 + 1.3, W - T - 0.4), T_FRONT, T_FRONT + FOOT_T, z0 - lz0, z1 + lz1))
    b = b.union(cyl((MX_X, T_FRONT + FOOT_T, MX_Z[i]), (0, 1, 0), 2.9, BOSS_L))
    ye = Y_MX_TOP
    for (dx, dz) in ((2.1, 0.7), (0.7, 2.1)):
        b = b.cut(box(MX_X - dx, MX_X + dx, ye - MX_STEM - 0.1, ye + 1, MX_Z[i] - dz, MX_Z[i] + dz))
    return b


def ref_buttons():
    return [button(0), button(1)]


def ref_mx():
    out = []
    for z in MX_Z:
        h = MX_BODY / 2
        out.append(box(MX_X - h, MX_X + h, Y_MX_TOP, Y_MX_PLATE + MX_BELOW, z - h, z + h)
                   .union(box(MX_X - 3, MX_X + 3, Y_MX_PLATE + MX_BELOW, Y_MX_END, z - 3, z + 3)))
    return out


def ref_sd_zone():
    x1 = X_PCB + PCB_T - SD_OFFSET
    return box(W - RIGHT_M + 3.0, x1, T_FRONT, Y_PCB_FRONT + SD_DEPTH, SD_Z0, SD_Z1)


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
            p = p.cut(insert_hole((x, T_FRONT, (z0 + z1) / 2), (0, -1, 0), ext=3.0))
    return p


def _ring():
    return rounded(Y_TUBE0, Y_TUBE1).cut(rounded(Y_TUBE0 - 1, Y_TUBE1 + 1, inset=T, r=1.0))


def u_bracket():
    u = _ring().intersect(box(X_SPLIT, W + 1, 0, D, -1, HB + 1))
    # ribber i topp og bunn, foran og bak: feste for front, bakpanel og sidepanel
    for (y0, y1) in RIB_Y:
        for (z0, z1) in RIB_Z:
            x1 = RIB_FRONT_BOTTOM_X1 if (y0 == Y_TUBE0 and z0 == T) else W - T
            u = u.union(box(X_SPLIT, x1, y0, y1, z0, z1))
    for iy, (y0, y1) in enumerate(RIB_Y):
        for (z0, z1) in RIB_Z:
            yc, zc = (y0 + y1) / 2, (z0 + z1) / 2
            # sidepanelskrue inn i ribbeenden
            u = u.cut(insert_hole((X_SPLIT, yc, zc), (1, 0, 0)))
            for x in PANEL_SCREW_X:
                if iy == 0:   # front: skrue innenfra gjennom ribben
                    u = u.cut(cyl((x, y0 - 1, zc), (0, 1, 0), CLEAR / 2, RIB + 2))
                else:         # bak: varmeinnsats for skrue utenfra gjennom bakpanelet
                    u = u.cut(insert_hole((x, y1, zc), (0, -1, 0), ext=3.0))
    # brakettplate for de to MX-bryterne, med avstivning langs overkanten
    h = MX_BODY / 2
    px0, pz1 = MX_X - h - 3.0, MX_Z[0] + h + 2.5
    plate = box(px0, W - T, Y_MX_PLATE, Y_MX_PLATE + MX_PLATE_T, T, pz1)
    plate = plate.union(box(px0, W - T, Y_MX_PLATE - 5.0, Y_MX_PLATE + MX_PLATE_T, pz1 - 1.5, pz1))
    for z in MX_Z:
        c = MX_CUT / 2
        plate = plate.cut(box(MX_X - c, MX_X + c, Y_MX_PLATE - 1, Y_MX_PLATE + MX_PLATE_T + 1, z - c, z + c))
    u = u.union(plate)
    # avstandsstykker for hovedkortet
    for (uu, vv) in ITX_HOLES:
        y, z = Y_PCB_REAR - vv, BOARD_Z0 + uu
        u = u.union(cyl((W - T - STANDOFF, y, z), (1, 0, 0), 4.0, STANDOFF + 0.5))
        u = u.cut(insert_hole((W - T - STANDOFF, y, z), (1, 0, 0), ext=3.0))
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
            s = s.union(cyl((T - 0.1, yc, zc), (1, 0, 0), 4.0, X_SPLIT - T + 0.05))      # anleggspute mot ribbeenden
            s = s.cut(cyl((-1, yc, zc), (1, 0, 0), CLEAR / 2, T + 3))
            s = s.cut(cq.Solid.makeCone(3.2, CLEAR / 2, 1.7, V(0, yc, zc), V(1, 0, 0)))
    # hylle som floppyen hviler paa og skrus fast i, med avstivere under
    fb = ref_floppy().val().BoundingBox()
    zt = fb.zmin
    ya, yb = T_FRONT + SHELF_Y0, T_FRONT + SHELF_Y1
    sh = box(T, fb.xmax, ya, yb, zt - SHELF_T, zt)
    for y in (ya, (ya + yb) / 2 - 1.5, yb - 3.0):
        g = (cq.Workplane("XZ").polyline([(T, zt - SHELF_T), (T + GUSSET, zt - SHELF_T), (T, zt - SHELF_T - GUSSET)]).close()
             .extrude(-3.0).translate((0, y, 0)))
        sh = sh.union(g)
    hx = fb.xmax - FD_HOLE_UP
    for hy in FD_HOLES_Y:
        y = T_FRONT + FD_GAP + hy
        sh = sh.cut(cyl((hx, y, zt - SHELF_T - 1), (0, 0, 1), CLEAR / 2, SHELF_T + 2))
        sh = sh.cut(cyl((hx, y, zt - SHELF_T - 1), (0, 0, 1), 3.2, 1.0 + 1.8))      # forsenkning for skruehode
    s = s.union(sh)
    return s


def io_to_panel(sx, sy):
    """Skjoldkoordinat -> (x, z) i kabinettet."""
    z = BOARD_Z0 + IO_CENTER_U - (sx - 81.375)
    x = (W - T - STANDOFF) - (sy - 2.0 - IO_BELOW_PCB)
    return x, z


def zorro_planes():
    return [BOARD_Z0 + u for u in ZORRO_U]


def rear_panel():
    p = rounded(Y_TUBE1, D)
    y0, y1 = Y_TUBE1 - 1, D + 1
    # I/O-utsnittene etter DeniseITX I/O-skjoldet rett i platen
    for (sx0, sy0, sx1, sy1) in IO_RECTS:
        xa, za = io_to_panel(sx0, sy0)
        xb, zb = io_to_panel(sx1, sy1)
        p = p.cut(box(min(xa, xb), max(xa, xb), y0, y1, min(za, zb), max(za, zb)))
    for (sx, sy, dia) in IO_CIRCLES:
        x, z = io_to_panel(sx, sy)
        p = p.cut(cyl((x, y0, z), (0, 1, 0), dia / 2, T_REAR + 2))
    # Zorro-aapninger med leppe og innsatshull paa innsiden
    for zp in zorro_planes():
        h = ZORRO_OPEN_W / 2
        p = p.cut(box(ZORRO_X0, ZORRO_X1, y0, y1, zp - h, zp + h))
        p = p.union(box(LIP_X0, LIP_X1, Y_TUBE1 - LIP_D, Y_TUBE1 + 0.1, zp + LIP_Z[0], zp + LIP_Z[1]))
        p = p.cut(insert_hole((LIP_X0, Y_TUBE1 - LIP_HOLE_IN, zp + LIP_HOLE_DZ), (1, 0, 0), ext=1.0))
    # DC-inntak og VGA paa hoykant i venstre soyle
    p = p.cut(cyl((DC_X, y0, DC_Z), (0, 1, 0), DC_D / 2, T_REAR + 2))
    p = p.cut(cyl((DC_X, y0, DC_Z), (0, 1, 0), DC_REC_D / 2, 1 + T_REAR - DC_REC_LEFT))
    p = p.cut(box(VGA_X - VGA_REC_W / 2, VGA_X + VGA_REC_W / 2, y0, Y_TUBE1 + T_REAR - VGA_REC_LEFT,
                  VGA_Z - VGA_REC_H / 2, VGA_Z + VGA_REC_H / 2))
    p = p.cut(box(VGA_X - 9.0, VGA_X + 9.0, y0, y1, VGA_Z - 5.0, VGA_Z + 5.0).edges("|Y").fillet(2.0))
    for dx in (-12.5, 12.5):
        p = p.cut(cyl((VGA_X + dx, y0, VGA_Z), (0, 1, 0), 1.6, T_REAR + 2))
    # avtrekk oppe til venstre
    z = 125.0
    while z < HB - 16:
        p = p.cut(box(10, 64, y0, y1, z, z + 3.0))
        z += 7.0
    for (z0, z1) in RIB_Z:
        for x in PANEL_SCREW_X:
            p = p.cut(cyl((x, y0, (z0 + z1) / 2), (0, 1, 0), CLEAR / 2, T_REAR + 2))
    return p


def zorro_cover(i):
    """Blindlokk for Zorro-aapning i, etter monster av standard PCI-blindlokk.
    Skrives ut med pluggen ned og stotter under hals og flik. Legges rett paa plass og skrus i leppa med M3 x 6."""
    zp = zorro_planes()[i]
    w = COVER_W / 2
    yi = Y_TUBE1                                   # bakpanelets innside
    tt = 1.5                                       # tykkelse flik
    c = box(LIP_X1 + 0.3, ZORRO_X1 + 1.5, yi - COVER_T, yi, zp - w, zp + w)                       # plate over aapningen
    c = c.union(box(LIP_X0 - tt, LIP_X1 + 0.3, yi - COVER_T, yi, zp - w, zp + LIP_Z[0] - 0.5))   # hals forbi leppa
    c = c.union(box(LIP_X0 - tt, LIP_X0, yi - COVER_TAB_H, yi, zp - w, zp + w))                   # flik mot leppa
    # plugg som gaar inn i aapningen, saa lokket hviler i bakpanelet og ikke bare paa skruen
    k = 0.25
    c = c.union(box(ZORRO_X0 + k, ZORRO_X1 - k, yi - 0.1, yi + T_REAR - 0.4, zp - ZORRO_OPEN_W / 2 + k, zp + ZORRO_OPEN_W / 2 - k))
    c = c.cut(cyl((LIP_X0 - tt - 1, yi - LIP_HOLE_IN, zp + LIP_HOLE_DZ), (1, 0, 0), CLEAR / 2, tt + 2))
    return c


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
        y = y0 + 1.5 + (y1 - y0 - 4.0 - 3.0) * i / n      # hjornestolpene trukket inn ogsaa i dybden
        f = f.union(box(x0 + 1.5, x0 + rw, y, y + 4.0, -FOOT_H, 0))
        f = f.union(box(x1 - rw, x1 - 1.5, y, y + 4.0, -FOOT_H, 0))
    for i in range(1, 3):
        x = x0 + (x1 - x0 - 4.0) * i / 3
        for ya in (y0, y1 - rw):
            f = f.union(box(x, x + 4.0, ya + 1.5 if ya == y0 else ya, ya + rw if ya == y0 else ya + rw - 1.5, -FOOT_H, 0))
    for (x, y) in FOOT_SCREWS:
        f = f.union(box(x - 5, x + 5, y - 5, y + 5, -FOOT_H, 0).intersect(box(x0 + 1.5, x1 - 1.5, y0, y1, -FOOT_H, 0)))
        f = f.cut(insert_hole((x, y, 0.0), (0, 0, -1)))
    return f


# ---------------------------------------------------------------- referansevolumer (skrives ikke ut)
def ref_board():
    pcb = box(X_PCB, X_PCB + PCB_T, Y_PCB_FRONT, Y_PCB_REAR, BOARD_Z0, BOARD_Z0 + PCB)
    comp = box(X_PCB - COMP_H, X_PCB, Y_PCB_FRONT + 2, Y_PCB_REAR, BOARD_Z0 + 2, BOARD_Z0 + PCB - 2)
    return pcb, comp


def ref_floppy():
    xl = XC - FD_SLOT_FROM_TOP          # lokket mot venstre
    return box(xl, xl + FD_H, T_FRONT + FD_GAP, T_FRONT + FD_GAP + FD_L, ZC_SLOT - FD_W / 2, ZC_SLOT + FD_W / 2)


def ref_picopsu():
    # ATX CN1: u 103..153, v 157..167 ESTIMAT fra kortbildet.
    # PicoPSU maalt: 36 over kortet, 23 tykk, 45 bred, henger ca 2,5 ut over forkanten av kortet.
    return box(X_PCB - PICO_H, X_PCB, Y_PCB_FRONT - PICO_OVERHANG, Y_PCB_FRONT - PICO_OVERHANG + PICO_T,
               BOARD_Z0 + 103.0, BOARD_Z0 + 103.0 + PICO_W)


def ref_zorro():
    # TandemIDE 129 x 74 i slot 1, nettverkskort 134 x 53 i slot 2. Plassert midt paa Zorro-kontakten (26..157 fra bakkant, ESTIMAT)
    cards = []
    yc = Y_PCB_REAR - 91.5
    for zp, (L, h) in zip(zorro_planes(), ((129.0, 74.0), (134.0, 53.0))):
        cards.append(box(X_PCB - 1.5 - h, X_PCB - 1.5, yc - L / 2, yc + L / 2, zp - 0.8, zp + 0.8))
    return cards


TEST_UPS = [5.0, 5.5, 6.0]


def floppy_testbit():
    # Liten mal for aa proeve hullene mot driven for sidepanelet skrives ut. Skrives ut flatt.
    # Drivens side legges paa platen, bunnplaten mot den lange kanten, forkanten mot den korte.
    L = FD_HOLES_Y[-1] + 8.0
    p = box(0, 14.0, 0, L, 0, 3.0)
    p = p.union(box(-2.0, 0, -2.0, L, 0, 9.0))        # lang anleggskant = drivens bunnplate
    p = p.union(box(-2.0, 14.0, -2.0, 0, 0, 9.0))     # kort anleggskant = drivens forkant
    # hvert hull har sin egen hoyde over bunnplaten, saa en utskrift avgjor hoyden: fremste 5,0, midtre 5,5, bakerste 6,0
    # antall hakk i ytterkanten ved hullet viser hvilket det er (1, 2, 3)
    for i, (hy, up) in enumerate(zip(FD_HOLES_Y, TEST_UPS)):
        p = p.cut(cyl((up, hy, -1), (0, 0, 1), 1.6, 5.0))
        for k in range(i + 1):
            p = p.cut(box(12.5, 15.0, hy - 1.0 + 3.0 * (k - i / 2.0), hy + 1.0 + 3.0 * (k - i / 2.0), -1, 4.0))
    return p


PARTS = {
    "zorro_blindlokk_1": (lambda: zorro_cover(0), (0.6, 0.6, 0.6)),
    "zorro_blindlokk_2": (lambda: zorro_cover(1), (0.6, 0.6, 0.6)),
    "knapp_power": (lambda: button(0), (0.9, 0.88, 0.82)),
    "knapp_reset": (lambda: button(1), (0.9, 0.88, 0.82)),
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
    for i, m in enumerate(ref_mx()):
        asm.add(m, name=f"REF_mx{i+1}", color=cq.Color(0.2, 0.2, 0.2))
    asm.add(ref_sd_zone(), name="REF_sd_sone", color=cq.Color(0.2, 0.5, 0.9, 0.3))
    asm.add(ref_picopsu(), name="REF_picopsu", color=cq.Color(0.9, 0.8, 0.1))
    for i, c in enumerate(ref_zorro()):
        asm.add(c, name=f"REF_zorro{i+1}", color=cq.Color(0.1, 0.6, 0.2))
    asm.save(os.path.join(out, "DeniseITX_kabinett_v0.21.step"))
    tb = floppy_testbit()
    cq.exporters.export(tb, os.path.join(out, "testbit_floppyhull.step"))
    cq.exporters.export(tb, os.path.join(out, "testbit_floppyhull.stl"), tolerance=0.02, angularTolerance=0.1)
    print("ok", out)
