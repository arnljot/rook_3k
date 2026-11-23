# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright (C) 2026 Arnljot Arntsen
"""
Denise ITX staaende kabinett, konsept v0.21 (CadQuery).

Koordinater: X mot hoyre sett forfra, Y bakover (front = 0), Z opp (kabinettkropp bunn = 0).
Hovedkortet staar paa hoykant paa hoyre vegg, komponentsiden mot venstre,
portene bak og Zorro-slottene nederst.

Run:  python src/denise_itx_case.py [output_dir]
      Writes one STEP file per part plus the assembly. output_dir defaults to out/ in the repository root.
      Options are read from config.txt in the repository root, or from the file given with --config <file>.
Alle maal i mm. Maal merket ESTIMAT maa kontrolleres med skyvelaer.
"""
import os
import sys
import cadquery as cq
from cadquery import Vector as V

# ---------------------------------------------------------------- configuration
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # repository root, the parent of src/

# key: default. The type of the default decides how the value in config.txt is parsed.
CONFIG_DEFAULTS = {
    "rook_height": 227.0,
    "rook_depth": 210.0,
    "rook_width": 117.0,
    "rook_corner_radius": 4.0,
    "rook_foot_grill_height": 3.0,
    "rook_foot_grill_gap": 2.5,
    "rook_foot_grills": 3,
    "chamfer_recess_enable": True,
    "deco_groove_enable": True,
    "pc_badge_recess_enable": True,
    "led_window_width": 2.2,
    "led_window_length": 5.0,
    "floppy_legacy_enable": True,
    "floppy_mount_hole_height": 5.0,
    "zorro_cutout_enable": True,
    "back_port_vga_enable": True,
    "back_port_dc_enable": True,
    "back_port_dc_diameter": 8.1,
    "heatinsert_diameter": 4.0,
    "heatinsert_depth": 4.5,
    "heatinsert_wall_thickness": 1.6,
}


def config_error(msg):
    sys.exit(f"config error: {msg}")


def load_config():
    """Read key=value lines from config.txt. Missing keys keep their defaults, unknown keys are errors."""
    path = os.path.join(ROOT, "config.txt")
    explicit = "--config" in sys.argv
    if explicit:
        i = sys.argv.index("--config")
        if i + 1 >= len(sys.argv):
            config_error("--config needs a file name")
        path = sys.argv[i + 1]
        del sys.argv[i:i + 2]
    cfg = dict(CONFIG_DEFAULTS)
    if not os.path.exists(path):
        if explicit:
            config_error(f"{path} not found")
        return cfg
    with open(path, encoding="utf-8") as f:
        for no, line in enumerate(f, 1):
            line = line.split("#", 1)[0].strip()
            if not line:
                continue
            if "=" not in line:
                config_error(f"{path} line {no}: expected key=value")
            key, val = (t.strip() for t in line.split("=", 1))
            if key not in CONFIG_DEFAULTS:
                config_error(f"{path} line {no}: unknown key '{key}'")
            if val == "":
                continue                      # empty value keeps the default
            default = CONFIG_DEFAULTS[key]
            try:
                if isinstance(default, bool):
                    if val.lower() not in ("true", "false"):
                        raise ValueError
                    cfg[key] = val.lower() == "true"
                elif isinstance(default, int):
                    cfg[key] = int(val)
                else:
                    cfg[key] = float(val.replace(",", "."))
            except ValueError:
                kind = "true or false" if isinstance(default, bool) else "a number"
                config_error(f"{path} line {no}: {key} must be {kind}, got '{val}'")
    return cfg


CFG = load_config()
FLOPPY = CFG["floppy_legacy_enable"]
ZORRO = CFG["zorro_cutout_enable"]

# ---------------------------------------------------------------- parametre
W = CFG["rook_width"]           # utvendig bredde
D = CFG["rook_depth"]           # utvendig dybde (se LESMEG: 181 gaar ikke med 10 mm chamfer)
HB = CFG["rook_height"]         # hoyde kabinettkropp uten fot
R = CFG["rook_corner_radius"]   # hjorneradius sett forfra
T = 3.0             # veggtykkelse
T_REAR = 3.0        # bakpanel
FOOT_FIN_T, FOOT_FIN_GAP, FOOT_FINS = CFG["rook_foot_grill_height"], CFG["rook_foot_grill_gap"], CFG["rook_foot_grills"]
FOOT_H = FOOT_FINS * FOOT_FIN_T + (FOOT_FINS - 1) * FOOT_FIN_GAP      # fot, 14,0 med standardverdiene
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
LED_W, LED_L = CFG["led_window_width"], CFG["led_window_length"]    # LED-vinduer i sporet

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
ZORRO_X0, ZORRO_X1 = W - 86.0, W - 26.0   # aapningens utstrekning, maalt fra hoyre side siden kortene henger paa hovedkortet. 31 og 91 ved bredde 117
# Leppe og blindlokk etter monsteret til et standard PCI-blindlokk (PCI+cover.3mf), smalnet og kortet ned:
# plate mot innsiden av bakpanelet, flik boyd innover i enden lengst fra hovedkortet, skruehull 6,45 over platens
# underside og 1,5 til siden for midten i originalen. Skruen gaar i kortets innskyvingsretning.
LIP_X0, LIP_X1 = W - 94.1, W - 87.6   # leppa i X. 22,9 og 29,4 ved bredde 117
LIP_D = 10.2                       # hvor langt leppa staar inn fra bakpanelet
LIP_Z = (-2.25, 6.25)              # leppa i Z relativt til kortplanet. Resten av bredden er hals paa lokket
LIP_HOLE_IN = 6.45                 # innsatshull fra bakpanelets innside (som paa standardlokket)
LIP_HOLE_DZ = 2.0                  # innsatshull relativt til kortplanet
COVER_W = 12.5
COVER_T = 1.5
COVER_TAB_H = 13.5
# DC og VGA ligger over Zorro-aapningene, saa det er fritt aa komme til skruene i leppene fra venstre
DC_X, DC_Z, DC_D = 14.0, 52.0, CFG["back_port_dc_diameter"]   # hals maalt til 7,75
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
INS_D = CFG["heatinsert_diameter"]
INS_DEPTH = CFG["heatinsert_depth"]     # 0,5 ekstra for plast som presses ned foran innsatsen
INS_WALL = CFG["heatinsert_wall_thickness"]
INS_BOSS_R = max(4.0, INS_D / 2 + INS_WALL)    # radius of round bosses that hold an insert
INS_EXT = 4.0       # smalere forlengelse bak innsatsen, saa skruen ikke bunner
# floppyhylle paa venstre sidepanel
# Noyaktige hull for drivens sidehull: 21, 81 og 111 fra drivens forkant. M3 x 0,5.
# Verified with the test gauge against a Chinon FZ-354 without face plate: all three positions fit, hole height 5.0.
FD_HOLES_Y = [21.0, 81.0, 111.0]
FD_HOLE_UP = CFG["floppy_mount_hole_height"]   # hullsenter over drivens bunnplate. 5,0 for Chinon FZ-354
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

RIB = max(8.0, INS_D + 2 * INS_WALL)
RIB_Z = [(T, T + RIB), (HB - T - RIB, HB - T)]
RIB_Y = [(Y_TUBE0, Y_TUBE0 + RIB), (Y_TUBE1 - RIB, Y_TUBE1)]
PANEL_SCREW_X = [25.0, W - 25.0]


# ---------------------------------------------------------------- validation
def validate_config():
    """Stop on values the design cannot hold, warn on values that exceed the Bambu Lab H2D single nozzle volume."""
    eps = 1e-6
    # height: the mainboard must clear the upper rib, and the front must hold the LEDs and the floppy slot
    h_min = BOARD_Z0 + PCB + RIB + T + 1.0
    if FLOPPY:
        h_min = max(h_min, BOT_M + TOP_M + 2 * STEEP + LED_TOP_GAP + LED_L + LED_PITCH + 3.5 + SLOT_L)
    # depth: the front edge of the mainboard must sit behind the pins of the power and reset switches
    d_min = Y_MX_END + 1.6 + PCB + IO_GAP + T_REAR
    # width: front layout, rear panel cut-outs, Zorro card height, and floppy next to the PicoPSU
    w_min = LEFT_M + 2 * CHAMFER_W + GROOVE + BTN_XC + BTN_W / 2 + BTN_EDGE + 2.0
    w_min = max(w_min, 64.0 + 2.0 + 38.1 - 2.0 - IO_BELOW_PCB + T + STANDOFF)          # vents clear of the I/O cut-outs
    if ZORRO:
        w_min = max(w_min, T + 74.0 + 1.5 + PCB_T + STANDOFF + T)                       # 74 mm high Zorro card
    if FLOPPY:
        w_min = max(w_min, XC - FD_SLOT_FROM_TOP + FD_H + 4.0 + PICO_H + PCB_T + STANDOFF + T)
    for key, val, low in (("rook_height", HB, h_min), ("rook_depth", D, d_min), ("rook_width", W, w_min)):
        if val < low - eps:
            config_error(f"{key}={val:g} is too small, the minimum with this configuration is {low:.1f}")
    if not 0.5 <= R <= 6.0:
        config_error(f"rook_corner_radius={R:g} must be between 0.5 and 6.0")
    if FOOT_FINS < 1 or FOOT_FIN_T < 0.8 or FOOT_FIN_GAP < 0:
        config_error("rook_foot_grills must be at least 1, rook_foot_grill_height at least 0.8 and rook_foot_grill_gap not negative")
    if FOOT_H < INS_DEPTH + INS_EXT + 1.5 - eps:
        config_error(f"the foot is {FOOT_H:g} high, it must be at least {INS_DEPTH + INS_EXT + 1.5:g} to hold the heat inserts")
    if INS_D < 2.0 or INS_DEPTH < 2.0 or INS_WALL < 0.8:
        config_error("heatinsert_diameter and heatinsert_depth must be at least 2.0 and heatinsert_wall_thickness at least 0.8")
    if INS_DEPTH + 3.0 + 1.5 > T_FRONT + eps:
        config_error(f"heatinsert_depth={INS_DEPTH:g} is too deep for the {T_FRONT:g} mm front panel")
    if ZORRO and INS_D / 2 + INS_WALL > (LIP_Z[1] - LIP_Z[0]) / 2 + eps:
        print(f"warning: the Zorro lips are too narrow for heatinsert_wall_thickness={INS_WALL:g}", file=sys.stderr)
    if not (0.5 <= LED_W <= GROOVE - 2.0 and 0.5 <= LED_L <= LED_PITCH - 1.0):
        config_error(f"led_window_width must be 0.5 to {GROOVE - 2.0:g} and led_window_length 0.5 to {LED_PITCH - 1.0:g}")
    if FLOPPY and not 2.5 <= FD_HOLE_UP <= 12.0:
        config_error(f"floppy_mount_hole_height={FD_HOLE_UP:g} must be between 2.5 and 12.0")
    if not 3.0 <= DC_D <= 20.0:
        config_error(f"back_port_dc_diameter={DC_D:g} must be between 3.0 and 20.0")
    # Bambu Lab H2D, single nozzle: 325 x 320 x 325 mm. The U-bracket lies on its right wall.
    a, b = sorted((HB, Y_TUBE1 - Y_TUBE0), reverse=True)
    if a > 325.0 or b > 320.0 or W > 325.0:
        print(f"warning: {W:g} x {D:g} x {HB:g} exceeds the Bambu Lab H2D single nozzle volume of 325 x 320 x 325 mm",
              file=sys.stderr)


validate_config()


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
    if CFG["chamfer_recess_enable"]:
        recess = cq.Solid.makeLoft([rect_wire(-1.0), rect_wire(REC)], True)
        p = p.cut(recess)
    if FLOPPY:
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
    if CFG["chamfer_recess_enable"] and CFG["deco_groove_enable"]:
        p = p.cut(cq.Workplane("XY").add(shifted).intersect(strip))
    # fordypning for pc-badge nede til venstre
    bs = BADGE + 2 * BADGE_MARGIN
    bx0 = W - BADGE_X - bs if BADGE_RIGHT else BADGE_X
    if BTN_LOW and BTN_RIGHT and BADGE_RIGHT:
        bx0 = px0 - BADGE_X - bs
    if CFG["pc_badge_recess_enable"]:
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
        u = u.union(cyl((W - T - STANDOFF, y, z), (1, 0, 0), INS_BOSS_R, STANDOFF + 0.5))
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


FOOT_SCREWS = [(10.0, 27.0), (W - 10.0, 27.0), (10.0, D - 34.0), (W - 10.0, D - 34.0)]


def side_panel():
    s = _ring().intersect(box(-1, X_SPLIT, 0, D, -1, HB + 1))
    for (y0, y1) in RIB_Y:
        for (z0, z1) in RIB_Z:
            yc, zc = (y0 + y1) / 2, (z0 + z1) / 2
            s = s.union(cyl((T - 0.1, yc, zc), (1, 0, 0), 4.0, X_SPLIT - T + 0.05))      # anleggspute mot ribbeenden
            s = s.cut(cyl((-1, yc, zc), (1, 0, 0), CLEAR / 2, T + 3))
            s = s.cut(cq.Solid.makeCone(3.2, CLEAR / 2, 1.7, V(0, yc, zc), V(1, 0, 0)))
    if not FLOPPY:
        return s
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
    for zp in (zorro_planes() if ZORRO else []):
        h = ZORRO_OPEN_W / 2
        p = p.cut(box(ZORRO_X0, ZORRO_X1, y0, y1, zp - h, zp + h))
        p = p.union(box(LIP_X0, LIP_X1, Y_TUBE1 - LIP_D, Y_TUBE1 + 0.1, zp + LIP_Z[0], zp + LIP_Z[1]))
        p = p.cut(insert_hole((LIP_X0, Y_TUBE1 - LIP_HOLE_IN, zp + LIP_HOLE_DZ), (1, 0, 0), ext=1.0))
    # DC-inntak og VGA paa hoykant i venstre soyle
    if CFG["back_port_dc_enable"]:
        p = p.cut(cyl((DC_X, y0, DC_Z), (0, 1, 0), DC_D / 2, T_REAR + 2))
        p = p.cut(cyl((DC_X, y0, DC_Z), (0, 1, 0), max(DC_REC_D, DC_D + 4.0) / 2, 1 + T_REAR - DC_REC_LEFT))
    if CFG["back_port_vga_enable"]:
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
    fin_t, gap = FOOT_FIN_T, FOOT_FIN_GAP
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
        hb = max(5.0, INS_D / 2 + INS_WALL)
        f = f.union(box(x - hb, x + hb, y - hb, y + hb, -FOOT_H, 0).intersect(box(x0 + 1.5, x1 - 1.5, y0, y1, -FOOT_H, 0)))
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


PARTS = {} if not ZORRO else {
    "zorro_blindlokk_1": (lambda: zorro_cover(0), (0.6, 0.6, 0.6)),
    "zorro_blindlokk_2": (lambda: zorro_cover(1), (0.6, 0.6, 0.6)),
}
PARTS.update({
    "knapp_power": (lambda: button(0), (0.9, 0.88, 0.82)),
    "knapp_reset": (lambda: button(1), (0.9, 0.88, 0.82)),
    "frontpanel": (front_panel, (0.85, 0.83, 0.78)),
    "u_brakett": (u_bracket, (0.75, 0.73, 0.68)),
    "sidepanel_venstre": (side_panel, (0.75, 0.73, 0.68)),
    "bakpanel": (rear_panel, (0.45, 0.45, 0.45)),
    "fot": (foot, (0.45, 0.45, 0.45)),
})

if __name__ == "__main__":
    # Output directory: first argument, else out/ in the repository root (the parent of src/)
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out")
    os.makedirs(out, exist_ok=True)
    asm = cq.Assembly(name="DeniseITX_kabinett")
    for name, (fn, col) in PARTS.items():
        s = fn()
        cq.exporters.export(s, os.path.join(out, f"{name}.step"))
        asm.add(s, name=name, color=cq.Color(*col))
    pcb, comp = ref_board()
    asm.add(pcb, name="REF_hovedkort", color=cq.Color(0.4, 0.1, 0.4))
    asm.add(comp, name="REF_komponentsone", color=cq.Color(0.6, 0.3, 0.8, 0.3))
    if FLOPPY:
        asm.add(ref_floppy(), name="REF_floppy", color=cq.Color(0.8, 0.7, 0.5))
    for i, m in enumerate(ref_mx()):
        asm.add(m, name=f"REF_mx{i+1}", color=cq.Color(0.2, 0.2, 0.2))
    asm.add(ref_sd_zone(), name="REF_sd_sone", color=cq.Color(0.2, 0.5, 0.9, 0.3))
    asm.add(ref_picopsu(), name="REF_picopsu", color=cq.Color(0.9, 0.8, 0.1))
    for i, c in enumerate(ref_zorro()):
        asm.add(c, name=f"REF_zorro{i+1}", color=cq.Color(0.1, 0.6, 0.2))
    asm.save(os.path.join(out, "DeniseITX_kabinett_v0.21.step"))
    if FLOPPY:
        tb = floppy_testbit()
        cq.exporters.export(tb, os.path.join(out, "testbit_floppyhull.step"))
    print("ok", out)
