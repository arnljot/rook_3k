# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright (C) 2026 Arnljot Arntsen
"""
Rook 3K, an upright 3D-printable case for the DeniseITX Mini-ITX mainboard (CadQuery).

Coordinates: X to the right seen from the front, Y towards the rear (front = 0), Z up (bottom of the case body = 0).
The mainboard stands on edge on the right wall with the component side facing left,
the ports at the rear and the Zorro slots at the bottom.

Run:  python src/rook3k.py [output_dir]
      Writes one STEP file per part plus the assembly. output_dir defaults to out/ in the repository root.
      Options are read from config.txt in the repository root, or from the file given with --config <file>.
All dimensions in mm. Dimensions marked ESTIMATE have not been checked against the hardware.
"""
import math
import os
import sys
import cadquery as cq
from cadquery import Vector as V

# ---------------------------------------------------------------- configuration
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # repository root, the parent of src/

# key: default. The type of the default decides how the value in config.txt is parsed.
CONFIG_DEFAULTS = {
    "mainboard": "denise_itx",
    "rook_height": 227.0,
    "rook_depth": 211.0,
    "rook_width": 117.0,
    "rook_corner_radius": 4.0,
    "rook_foot_grill_height": 3.0,
    "rook_foot_grill_gap": 2.5,
    "rook_foot_grills": 3,
    "bottom": "foot_grill",
    "bottom_pad_height": 10.0,
    "bottom_pad_diameter": 18.0,
    "ssd_mount_enable": False,
    "chamfer_recess_enable": True,
    "deco_groove_enable": True,
    "pc_badge_recess_enable": True,
    "button_power": "front",
    "button_reset": "front",
    "led_power_enable": True,
    "led_drive_enable": True,
    "led_window_width": 2.2,
    "led_window_length": 5.0,
    "floppy_legacy_enable": True,
    "floppy_mount_hole_height": 5.0,
    "zorro_slot_1": "open",
    "zorro_slot_2": "open",
    "back_port_vga_enable": True,
    "back_port_dc_enable": True,
    "back_port_dc_diameter": 8.1,
    "heatinsert_diameter": 4.0,
    "heatinsert_depth": 4.5,
    "heatinsert_wall_thickness": 1.6,
}


# allowed values for the keys that take a word
CONFIG_CHOICES = {
    "mainboard": ("denise_itx", "pc_itx", "alicia_itx"),
    "zorro_slot_1": ("open", "closed", "custom"),
    "zorro_slot_2": ("open", "closed", "custom"),
    "button_power": ("front", "front_wide", "back", "back_wide", "none"),
    "button_reset": ("front", "back", "none"),
    "bottom": ("foot_grill", "foot_pads", "none"),
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
    cfg, given = dict(CONFIG_DEFAULTS), set()
    folder = os.path.dirname(os.path.abspath(path))
    if not os.path.exists(path):
        if explicit:
            config_error(f"{path} not found")
        return cfg, given, folder
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
            given.add(key)
            if isinstance(default, str):
                if val not in CONFIG_CHOICES[key]:
                    config_error(f"{path} line {no}: {key} must be one of {', '.join(CONFIG_CHOICES[key])}, got '{val}'")
                cfg[key] = val
                continue
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
    return cfg, given, folder


VERSION = "v0.23"
CFG, CFG_GIVEN, CFG_DIR = load_config()      # values, the keys set in the file, and the folder of the file
FLOPPY = CFG["floppy_legacy_enable"]
MAINBOARD = CFG["mainboard"]
if MAINBOARD == "alicia_itx":
    config_error("mainboard=alicia_itx is planned but not available yet")
HAS_ZORRO = MAINBOARD == "denise_itx"
ZORRO_KEYS = ("zorro_slot_1", "zorro_slot_2")
for _k in ZORRO_KEYS:
    if not HAS_ZORRO and _k in CFG_GIVEN and CFG[_k] != "closed":
        config_error(f"{_k}={CFG[_k]} is not possible, mainboard={MAINBOARD} has no Zorro slots")
ZORRO_SLOTS = [CFG[k] if HAS_ZORRO else "closed" for k in ZORRO_KEYS]     # open, closed or custom
ZORRO = "open" in ZORRO_SLOTS                    # at least one opening with lip and blanking cover
ZORRO_CARDS = [s != "closed" for s in ZORRO_SLOTS]
POWER, RESET = CFG["button_power"], CFG["button_reset"]
# a wide power button takes the place of the reset button on the same side
if POWER == "front_wide" and RESET == "front":
    config_error("button_power=front_wide needs button_reset=back or none")
if POWER == "back_wide" and RESET == "back":
    config_error("button_power=back_wide needs button_reset=front or none")
for _k, _v in (("button_power", POWER), ("button_reset", RESET)):
    if "back" in _v:
        config_error(f"{_k}={_v} is planned but not available yet")
if POWER == "none":
    print("warning: button_power=none leaves the case without a power button. The DeniseITX needs a pulse on its "
          "power input to turn on", file=sys.stderr)
BOTTOM = CFG["bottom"]
SSD = CFG["ssd_mount_enable"]

# ---------------------------------------------------------------- parameters
W = CFG["rook_width"]           # outer width
D = CFG["rook_depth"]           # outer depth. 210 is the minimum, 211 adds 1 mm between the switch pins and the mainboard
HB = CFG["rook_height"]         # height of the case body without the foot
R = CFG["rook_corner_radius"]   # corner radius seen from the front
T = 3.0             # wall thickness
T_REAR = 3.0        # rear panel
FOOT_FIN_T, FOOT_FIN_GAP, FOOT_FINS = CFG["rook_foot_grill_height"], CFG["rook_foot_grill_gap"], CFG["rook_foot_grills"]
FOOT_H = FOOT_FINS * FOOT_FIN_T + (FOOT_FINS - 1) * FOOT_FIN_GAP      # foot, 14.0 with the default values
FOOT_INSET = 4.0

# front (Amiga 3000 rotated 90 degrees)
REC = 10.0          # depth of the chamfer
FLOOR = 2.5         # material behind the groove
T_FRONT = REC + FLOOR
CHAMFER_W = 20.3    # width of the sloping face from each side
SIDE_M = (W - 14.0 - 2 * CHAMFER_W) / 2   # flat margin left/right when the field is centred
LEFT_M = 22.0       # flat margin to the left of the chamfer field. Equal to TOP_M, so the field sits towards the left
BTN_RIGHT = True   # buttons at the right edge instead of the left
BADGE_RIGHT = True # badge at the bottom right instead of the left
TOP_M = 22.0        # flat margin, top
BOT_M = 45.0        # flat margin, bottom
GROOVE = 14.0       # flat groove at the bottom of the chamfer
STEEP = 4.0         # width of the steep chamfer at top and bottom
SLOT_L, SLOT_W = 100.0, 8.0          # disk slot
EJECT_L, EJECT_W = 21.0, 5.0         # eject button, position is an ESTIMATE
EJECT_DX = 11.0     # eject centre in X relative to the centre of the groove ESTIMATE
EJECT_FROM_TOP = 16.5                # eject centre below the upper end of the disk slot ESTIMATE
LED_TOP_GAP = 2.0   # from the top of the groove to the first LED
LED_PITCH = 7.0
BTN_POCKET_D = 3.0  # depth of the pocket for power and reset
BTN_W = 7.0         # the buttons stand on end
BTN_PWR_L, BTN_RST_L = 12.0, 8.0     # gives a pocket as tall as the badge recess (27)
BTN_GAP, BTN_EDGE = 2.0, 2.5
DECO_W, DECO_D = 1.8, 0.5       # decorative groove
DECO_END = 1.0                  # the groove stops this far from the top and bottom edge of the chamfer
BADGE, BADGE_MARGIN, BADGE_D = 25.0, 1.0, 1.0   # recess for a 25 x 25 case badge
BADGE_X, BADGE_Z = 6.5, 6.5     # from the side (or from the button pocket) and from the bottom edge of the front
BTN_LOW = True                  # button pocket at the bottom, lower edge in line with the badge recess
BTN_XC = 7.5        # button centre from the side. The MX switch then sits about 3.6 mm further in than the button
BTN_OUT = 3.5       # the button protrudes this far in front of the panel at rest
BTN_CLEAR = 0.3
# MX switches behind the buttons, common MX footprint. Plate cut-out and fit verified in a test print of the U-bracket
MX_BODY = 15.6      # housing, square
MX_CUT = 14.0       # cut-out in the switch plate
MX_PLATE_T = 1.5
MX_STEM = 3.6       # stem above the top of the housing
MX_TOP = 6.6        # top of the housing to the upper side of the plate
MX_BELOW = 5.0      # upper side of the plate to the bottom of the housing
MX_PINS = 3.3
MX_X = W - T - 0.7 - MX_BODY / 2      # switch centre, as far towards the right wall as possible
# buttons in the front panel, from the top of the pocket: (part name, length)
FRONT_BUTTONS = []
if POWER == "front":
    FRONT_BUTTONS.append(("button_power", BTN_PWR_L))
elif POWER == "front_wide":
    FRONT_BUTTONS.append(("button_power", BTN_PWR_L + BTN_GAP + BTN_RST_L))
if RESET == "front":
    FRONT_BUTTONS.append(("button_reset", BTN_RST_L))
BTN_LENGTHS = [l for _, l in FRONT_BUTTONS]
if len(FRONT_BUTTONS) == 2:
    MX_Z = [27.5, 11.5]               # power, reset. 16 mm between centres
else:
    MX_Z = [BADGE_Z + BTN_EDGE + l / 2 for l in BTN_LENGTHS]     # a single switch sits centred behind its button
FOOT_T = 3.0        # foot of the button behind the front panel
BOSS_L = 4.0        # boss with a cross socket for the switch stem
Y_MX_TOP = T_FRONT + FOOT_T + BOSS_L           # top of the housing
Y_MX_PLATE = Y_MX_TOP + MX_TOP                 # front face of the switch plate
Y_MX_END = Y_MX_PLATE + MX_BELOW + MX_PINS     # pin tips
RIB_FRONT_BOTTOM_X1 = (MX_X - MX_BODY / 2 - 2.0) if BTN_LENGTHS else W - T   # the lower front rib stops here to make room for the switches
# zone reserved for a future SD card opening at the right edge (not modelled, only kept free)
SD_Z0, SD_Z1 = T + 35.0, T + 115.0
SD_DEPTH = 26.0     # from the front edge of the mainboard and inwards
SD_OFFSET = 15.0    # from the underside of the mainboard and out to the left
LED_W, LED_L = CFG["led_window_width"], CFG["led_window_length"]    # LED windows in the groove

# mainboard (Mini-ITX 170 x 170). Mounting holes and standoffs verified in a test print of the U-bracket
PCB = 170.0
PCB_T = 1.6
STANDOFF = 6.0
BOARD_Z0 = 15.0     # Zorro edge of the board above the bottom of the body
IO_AP_W, IO_AP_H = 158.75, 44.45   # ATX I/O aperture
IO_BELOW_PCB = 2.24                # edge of the aperture below the underside of the PCB (ATX)
IO_CENTER_U = 92.2                 # centre of the aperture measured from the Zorro edge. Fitted to a picture of the board, verified in a test print of the rear panel
IO_FLANGE, IO_FLANGE_T = 2.0, 1.5  # flange of the shield (no longer used, the shield is built into the rear panel)
# Through cut-outs following the DeniseITX I/O shield layout, in the shield's own coordinates (0..162.75 x 0..48.45)
IO_RECTS = [(16.1, 5.0, 151.25, 18.6), (16.1, 24.5, 100.75, 38.1)]          # (sx0, sy0, sx1, sy1)
IO_CIRCLES = [(157.5, 12.9, 7.5), (9.0, 12.35, 11.5), (9.0, 27.6, 11.5)]    # (sx, sy, diameter)
# Zorro cards: two slots, card planes read from a picture of the board and verified in a test print of the rear panel
if MAINBOARD == "pc_itx":
    # standard ATX aperture for a loose I/O shield, with a pocket on the inside so the shield can clip to a thin rim
    IO_RECTS, IO_CIRCLES = [(2.0, 2.0, 2.0 + IO_AP_W, 2.0 + IO_AP_H)], []
IO_SHIELD_W, IO_SHIELD_H, IO_RIM = 162.75, 48.45, 1.0    # outline of a loose ATX shield, and the rim left for it to clip to
IO_X_MIN = (W - T - STANDOFF) - (max(r[3] for r in IO_RECTS) - 2.0 - IO_BELOW_PCB)   # left edge of the I/O cut-outs
VENT_X0, VENT_X1 = 10.0, min(64.0, IO_X_MIN - 2.0)       # exhaust vents, kept clear of the I/O cut-outs
ZORRO_U = [5.2, 5.2 + 15.24]       # card plane from the lower edge of the mainboard
ZORRO_OPEN_W = 11.0
SLOT_FIELD_H = 14.0                # height of the field a custom slot may cut in, centred on the card plane
ZORRO_X0, ZORRO_X1 = W - 86.0, W - 26.0   # extent of the opening, measured from the right side since the cards hang on the mainboard. 31 and 91 at width 117
# Lip and blanking cover patterned on a standard PCI blanking cover, narrowed and shortened:
# a plate against the inside of the rear panel, a tab bent inwards at the end furthest from the mainboard, screw hole 6.45 above the
# underside of the plate and 1.5 off centre in the original. The screw runs in the insertion direction of the card.
LIP_X0, LIP_X1 = W - 94.1, W - 87.6   # the lip in X. 22.9 and 29.4 at width 117
LIP_D = 10.2                       # how far the lip stands in from the rear panel
LIP_Z = (-2.25, 6.25)              # the lip in Z relative to the card plane. The rest of the width is the neck of the cover
LIP_HOLE_IN = 6.45                 # insert hole from the inside of the rear panel (as on the standard cover)
LIP_HOLE_DZ = 2.0                  # insert hole relative to the card plane
COVER_W = 12.5
COVER_T = 1.5
COVER_TAB_H = 13.5
# DC and VGA sit above the Zorro openings, so the screws in the lips can be reached from the left
DC_X, DC_Z, DC_D = 14.0, 52.0, CFG["back_port_dc_diameter"]   # neck measured to 7.75
DC_REC_D, DC_REC_LEFT = 12.1, 2.0    # recess on the inside and the material left. Neck 4.5 long, nut 1.88 thick
VGA_REC_W, VGA_REC_H, VGA_REC_LEFT = 32.6 + 0.6, 12.7 + 0.6, 1.5   # recess for the housing of the panel connector, and the material left
VGA_X, VGA_Z = 44.0, 52.0          # DE-15 lying down. Opening 18 x 10, screw holes 25 apart ESTIMATE
IO_CLEAR = 0.2
IO_GAP = 1.0        # rear edge of the PCB to the inside of the rear panel ESTIMATE
COMP_H = 14.0       # tallest ordinary component ESTIMATE
ITX_HOLES = [(6.35, 10.16), (163.83, 33.02), (6.35, 165.1), (163.83, 165.1)]  # (u from the Zorro edge, v from the rear edge)

# floppy drive, standard 3.5"
FD_W, FD_H, FD_L = 101.6, 25.4, 129.0   # length = 21 + 60 + 30 + 18, measured with calipers
FD_SLOT_FROM_TOP = 9.0 + 3.3 / 2   # 9 mm from the lid to the disk (measured), plus half the thickness of a disk
PICO_H, PICO_T, PICO_W = 36.0, 23.0, 45.0   # PicoPSU above the mainboard, thickness, width (measured)
PICO_OVERHANG = 2.5      # PicoPSU overhang past the front edge of the mainboard (measured, approximate)
DOM_H = 49.0             # disk on module on the accelerator card, above the mainboard (measured)

# M3 screws. Brass heat-set inserts in blind holes. Defaults for CNC Kitchen M3 x 3.0
INS_D = CFG["heatinsert_diameter"]
INS_DEPTH = CFG["heatinsert_depth"]     # hole depth, with room in front of the insert for displaced plastic
INS_WALL = CFG["heatinsert_wall_thickness"]
INS_BOSS_R = max(4.0, INS_D / 2 + INS_WALL)    # radius of round bosses that hold an insert
INS_EXT = 4.0       # narrower extension behind the insert, so the screw does not bottom out
# floppy shelf on the left side panel
# Exact holes for the side holes of the drive: 21, 81 and 111 from the front of the drive. M3 x 0.5.
# Verified with the test gauge against a Chinon FZ-354 without face plate: all three positions fit, hole height 5.0.
FD_HOLES_Y = [21.0, 81.0, 111.0]
FD_HOLE_UP = CFG["floppy_mount_hole_height"]   # hole centre above the bottom plate of the drive. 5.0 for a Chinon FZ-354
FD_GAP = 0.3                      # gap between the front of the drive and the back of the front panel
FD_REAR_HOLE = FD_HOLES_Y[-1]
SHELF_T = 4.0
SHELF_Y0, SHELF_Y1 = 1.5, FD_REAR_HOLE + 10.0   # extent of the shelf behind the front panel
GUSSET = 15.0                     # small gussets under the shelf
PILOT = 2.6
CLEAR = 3.4

Y_TUBE0 = T_FRONT
Y_TUBE1 = D - T_REAR
X_SPLIT = 4.0       # split between the left side panel and the U-bracket
X_PCB = W - T - STANDOFF - PCB_T      # component side of the PCB
Y_PCB_REAR = Y_TUBE1 - IO_GAP
Y_PCB_FRONT = Y_PCB_REAR - PCB
RIGHT_M = W - LEFT_M - 2 * CHAMFER_W - 14.0
XC = LEFT_M + CHAMFER_W + 7.0      # centre of the groove and the disk slot
Z_REC0, Z_REC1 = BOT_M, HB - TOP_M
Z_GROOVE1 = Z_REC1 - STEEP
Z_LEDS = [Z_GROOVE1 - LED_TOP_GAP - LED_L / 2 - i * LED_PITCH for i in range(2)]
Z_SLOT1 = Z_LEDS[-1] - LED_L / 2 - 3.5      # disk slot placed just below the LEDs
ZC_SLOT = Z_SLOT1 - SLOT_L / 2

RIB = max(8.0, INS_D + 2 * INS_WALL)
RIB_Z = [(T, T + RIB), (HB - T - RIB, HB - T)]
RIB_Y = [(Y_TUBE0, Y_TUBE0 + RIB), (Y_TUBE1 - RIB, Y_TUBE1)]
PANEL_SCREW_X = [25.0, W - 25.0]
FOOT_SCREWS = [(10.0, 27.0), (W - 10.0, 27.0), (10.0, D - 34.0), (W - 10.0, D - 34.0)]
# separate feet with TPU pads, as an alternative to the grill foot
PAD_H, PAD_D = CFG["bottom_pad_height"], CFG["bottom_pad_diameter"]
PAD_REC, PAD_TPU_T, PAD_EXT = 1.5, 2.5, 2.0     # recess for the TPU pad, pad thickness, hole extension below the insert
# 2.5" SSD flat against the left side panel, above the floppy shelf and to the left of the drive, connector end up.
# It sits between four ears on the panel and is screwed through them into its side holes, so nothing shows on the
# outside. Mount it while the side panel is off the case.
# Outline and side holes after SFF-8201 as remembered, ESTIMATE until tried against a drive.
SSD_L, SSD_W, SSD_T = 100.0, 69.85, 7.0
SSD_HOLE_UP = 3.0                  # side holes above the bottom face of the drive
SSD_HOLE_Z = (14.0, 90.6)          # side holes from the connector end
SSD_GAP = 0.25                     # play between the drive and each ear
SSD_EAR_T, SSD_EAR_W = 3.0, 10.0   # thickness of an ear and its width along the drive
SSD_Y0 = T_FRONT + 25.0
SSD_Y1 = SSD_Y0 + SSD_W
SSD_Z0 = 86.0


# ---------------------------------------------------------------- validation
def validate_config():
    """Stop on values the design cannot hold, warn on values that exceed the Bambu Lab H2D single nozzle volume."""
    eps = 1e-6
    # height: the mainboard must clear the upper rib, and the front must hold the LEDs and the floppy slot
    h_min = BOARD_Z0 + PCB + RIB + T + 1.0
    if FLOPPY:
        h_min = max(h_min, BOT_M + TOP_M + 2 * STEEP + LED_TOP_GAP + LED_L + LED_PITCH + 3.5 + SLOT_L)
    # depth: the front edge of the mainboard must sit behind the pins of the power and reset switches
    if BTN_LENGTHS:
        d_min = Y_MX_END + 1.6 + PCB + IO_GAP + T_REAR
    else:                                              # without switches the PicoPSU overhang sets the limit
        d_min = T_FRONT + 1.0 + PICO_OVERHANG + PCB + IO_GAP + T_REAR
    # width: front layout, rear panel cut-outs, Zorro card height, and floppy next to the PicoPSU
    w_min = LEFT_M + 2 * CHAMFER_W + GROOVE + BTN_XC + BTN_W / 2 + BTN_EDGE + 2.0
    io_w = (W - T - STANDOFF) - IO_X_MIN                                               # width taken by the I/O cut-outs
    w_min = max(w_min, VENT_X0 + 30.0 + 2.0 + io_w + T + STANDOFF)                     # room for 30 mm wide vents
    if CFG["back_port_vga_enable"]:
        w_min = max(w_min, VGA_X + VGA_REC_W / 2 + 2.0 + io_w + T + STANDOFF)          # VGA clear of the I/O cut-outs
    if any(ZORRO_CARDS):
        w_min = max(w_min, T + 74.0 + 1.5 + PCB_T + STANDOFF + T)                       # 74 mm high Zorro card
    if FLOPPY:
        w_min = max(w_min, XC - FD_SLOT_FROM_TOP + FD_H + 4.0 + PICO_H + PCB_T + STANDOFF + T)
    for key, val, low in (("rook_height", HB, h_min), ("rook_depth", D, d_min), ("rook_width", W, w_min)):
        if val < low - eps:
            config_error(f"{key}={val:g} is too small, the minimum with this configuration is {low:.1f}")
    if BTN_LENGTHS and D < d_min + 1.0 - eps:
        print(f"warning: rook_depth={D:g} leaves only {D - d_min + 1.6:.1f} mm between the switch pins and the mainboard, "
              f"{d_min + 1.0:.0f} or more is recommended", file=sys.stderr)
    if not 0.5 <= R <= 6.0:
        config_error(f"rook_corner_radius={R:g} must be between 0.5 and 6.0")
    if BOTTOM == "foot_grill":
        if FOOT_FINS < 1 or FOOT_FIN_T < 0.8 or FOOT_FIN_GAP < 0:
            config_error("rook_foot_grills must be at least 1, rook_foot_grill_height at least 0.8 and rook_foot_grill_gap not negative")
        if FOOT_H < INS_DEPTH + INS_EXT + 1.5 - eps:
            config_error(f"the foot is {FOOT_H:g} high, it must be at least {INS_DEPTH + INS_EXT + 1.5:g} to hold the heat inserts")
    if BOTTOM == "foot_pads":
        pad_min = INS_DEPTH + PAD_EXT + 1.0 + PAD_REC
        if PAD_H < pad_min - eps:
            config_error(f"bottom_pad_height={PAD_H:g} is too low, the minimum with these heat inserts is {pad_min:g}")
        if not max(12.0, INS_D + 2 * INS_WALL + 4.0) - eps <= PAD_D <= 20.0 + eps:
            config_error(f"bottom_pad_diameter={PAD_D:g} must be between {max(12.0, INS_D + 2 * INS_WALL + 4.0):g} and 20")
    if SSD and SSD_Z0 + SSD_L + 25.0 > HB - T + eps:
        config_error(f"ssd_mount_enable needs rook_height of at least {SSD_Z0 + SSD_L + 25.0 + T:.0f} for the drive and its cable")
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


# ---------------------------------------------------------------- helpers
def insert_hole(p, d, ext=INS_EXT):
    """Hole for an M3 heat-set insert from the surface at point p, inwards in direction d."""
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
    # the pocket is open towards the side of the case
    ph = 2 * BTN_EDGE + sum(BTN_LENGTHS) + BTN_GAP * (len(BTN_LENGTHS) - 1)
    pz1 = BADGE_Z + ph if BTN_LOW else Z_REC1
    pz0 = pz1 - ph
    z = pz1 - BTN_EDGE
    holes = []
    xc = W - BTN_XC if BTN_RIGHT else BTN_XC
    for l in BTN_LENGTHS:
        holes.append((xc - BTN_W / 2, xc + BTN_W / 2, z - l, z))
        z -= l + BTN_GAP
    if BTN_RIGHT:
        return (xc - BTN_W / 2 - BTN_EDGE, W + 1.0, pz0, pz1), holes
    return (-1.0, xc + BTN_W / 2 + BTN_EDGE, pz0, pz1), holes


def button(i):
    # button with a foot and a boss for the MX stem. Printed with the front face down.
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
    return [button(i) for i in range(len(BTN_LENGTHS))]


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


# ---------------------------------------------------------------- parts
def front_panel():
    p = rounded(0, T_FRONT)
    if CFG["chamfer_recess_enable"]:
        recess = cq.Solid.makeLoft([rect_wire(-1.0), rect_wire(REC)], True)
        p = p.cut(recess)
    if FLOPPY:
        # disk slot in the groove
        p = p.cut(box(XC - SLOT_W / 2, XC + SLOT_W / 2, -1, T_FRONT + 1, ZC_SLOT - SLOT_L / 2, ZC_SLOT + SLOT_L / 2))
        # eject on the right chamfer, the drive has its lid towards the left
        ez = Z_SLOT1 - EJECT_FROM_TOP
        ex = XC + EJECT_DX
        p = p.cut(box(ex - EJECT_W / 2, ex + EJECT_W / 2, -1, T_FRONT + 1, ez - EJECT_L / 2, ez + EJECT_L / 2))
    # LED windows at the top of the groove
    for z, on in zip(Z_LEDS, (CFG["led_power_enable"], CFG["led_drive_enable"])):
        if on:
            p = p.cut(box(XC - LED_W / 2, XC + LED_W / 2, -1, T_FRONT + 1, z - LED_L / 2, z + LED_L / 2))
    # pocket with the power and reset buttons standing on end
    (px0, px1, pz0, pz1), holes = button_layout() if BTN_LENGTHS else ((W, W, 0, 0), [])
    if BTN_LENGTHS:
        p = p.cut(box(px0, px1, -1, BTN_POCKET_D, pz0, pz1))
    for (x0, x1, z0, z1) in holes:
        c = BTN_CLEAR
        p = p.cut(box(x0 - c, x1 + c, -1, T_FRONT + 1, z0 - c, z1 + c))
    # decorative groove in the middle of the left chamfer, 0.5 deep perpendicular to the face
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
    # recess for the case badge
    bs = BADGE + 2 * BADGE_MARGIN
    bx0 = W - BADGE_X - bs if BADGE_RIGHT else BADGE_X
    if BTN_LOW and BTN_RIGHT and BADGE_RIGHT:
        bx0 = px0 - BADGE_X - bs
    if CFG["pc_badge_recess_enable"]:
        p = p.cut(box(bx0, bx0 + bs, -1, BADGE_D, BADGE_Z, BADGE_Z + bs).edges("|Y").fillet(1.5))
    # insert holes at the back for the screws through the ribs of the U-bracket
    for (z0, z1) in RIB_Z:
        for x in PANEL_SCREW_X:
            p = p.cut(insert_hole((x, T_FRONT, (z0 + z1) / 2), (0, -1, 0), ext=3.0))
    return p


def _ring():
    return rounded(Y_TUBE0, Y_TUBE1).cut(rounded(Y_TUBE0 - 1, Y_TUBE1 + 1, inset=T, r=1.0))


def u_bracket():
    u = _ring().intersect(box(X_SPLIT, W + 1, 0, D, -1, HB + 1))
    # ribs at top and bottom, front and rear: mounting for the front, rear and side panels
    for (y0, y1) in RIB_Y:
        for (z0, z1) in RIB_Z:
            x1 = RIB_FRONT_BOTTOM_X1 if (y0 == Y_TUBE0 and z0 == T) else W - T
            u = u.union(box(X_SPLIT, x1, y0, y1, z0, z1))
    for iy, (y0, y1) in enumerate(RIB_Y):
        for (z0, z1) in RIB_Z:
            yc, zc = (y0 + y1) / 2, (z0 + z1) / 2
            # side panel screw into the end of the rib
            u = u.cut(insert_hole((X_SPLIT, yc, zc), (1, 0, 0)))
            for x in PANEL_SCREW_X:
                if iy == 0:   # front: screw from the inside through the rib
                    u = u.cut(cyl((x, y0 - 1, zc), (0, 1, 0), CLEAR / 2, RIB + 2))
                else:         # rear: heat-set insert for a screw from the outside through the rear panel
                    u = u.cut(insert_hole((x, y1, zc), (0, -1, 0), ext=3.0))
    # plate for the two MX switches, with a stiffener along the upper edge
    h = MX_BODY / 2
    if MX_Z:
        px0, pz1 = MX_X - h - 3.0, max(MX_Z) + h + 2.5
        plate = box(px0, W - T, Y_MX_PLATE, Y_MX_PLATE + MX_PLATE_T, T, pz1)
        plate = plate.union(box(px0, W - T, Y_MX_PLATE - 5.0, Y_MX_PLATE + MX_PLATE_T, pz1 - 1.5, pz1))
        for z in MX_Z:
            c = MX_CUT / 2
            plate = plate.cut(box(MX_X - c, MX_X + c, Y_MX_PLATE - 1, Y_MX_PLATE + MX_PLATE_T + 1, z - c, z + c))
        u = u.union(plate)
    # standoffs for the mainboard
    for (uu, vv) in ITX_HOLES:
        y, z = Y_PCB_REAR - vv, BOARD_Z0 + uu
        u = u.union(cyl((W - T - STANDOFF, y, z), (1, 0, 0), INS_BOSS_R, STANDOFF + 0.5))
        u = u.cut(insert_hole((W - T - STANDOFF, y, z), (1, 0, 0), ext=3.0))
    # air intake in the bottom, above the foot
    y = 30.0
    while y < Y_TUBE1 - 20:
        u = u.cut(box(16, W - 15, y, y + 4.0, -1, T + 1))
        y += 9.0
    # holes for the foot screws
    for (x, yy) in (FOOT_SCREWS if BOTTOM != "none" else []):
        u = u.cut(cyl((x, yy, -1), (0, 0, 1), CLEAR / 2, T + 2))
    return u



def side_panel():
    s = _ring().intersect(box(-1, X_SPLIT, 0, D, -1, HB + 1))
    for (y0, y1) in RIB_Y:
        for (z0, z1) in RIB_Z:
            yc, zc = (y0 + y1) / 2, (z0 + z1) / 2
            s = s.union(cyl((T - 0.1, yc, zc), (1, 0, 0), 4.0, X_SPLIT - T + 0.05))      # pad resting against the end of the rib
            s = s.cut(cyl((-1, yc, zc), (1, 0, 0), CLEAR / 2, T + 3))
            s = s.cut(cq.Solid.makeCone(3.2, CLEAR / 2, 1.7, V(0, yc, zc), V(1, 0, 0)))
    if SSD:
        # four ears with a screw hole each, in line with the side holes of the drive
        xh = T + SSD_HOLE_UP
        for dz in SSD_HOLE_Z:
            zc = SSD_Z0 + SSD_L - dz
            for ya in (SSD_Y0 - SSD_GAP - SSD_EAR_T, SSD_Y1 + SSD_GAP):
                ear = box(T - 0.1, xh + 3.5, ya, ya + SSD_EAR_T, zc - SSD_EAR_W / 2, zc + SSD_EAR_W / 2)
                s = s.union(ear.cut(cyl((xh, ya - 1, zc), (0, 1, 0), CLEAR / 2, SSD_EAR_T + 2)))
    if not FLOPPY:
        return s
    # shelf the floppy drive rests on and is screwed to, with gussets underneath
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
        sh = sh.cut(cyl((hx, y, zt - SHELF_T - 1), (0, 0, 1), 3.2, 1.0 + 1.8))      # counterbore for the screw head
    s = s.union(sh)
    return s


def io_to_panel(sx, sy):
    """Shield coordinate -> (x, z) in the case."""
    z = BOARD_Z0 + IO_CENTER_U - (sx - 81.375)
    x = (W - T - STANDOFF) - (sy - 2.0 - IO_BELOW_PCB)
    return x, z


def zorro_planes():
    return [BOARD_Z0 + u for u in ZORRO_U]


def zorro_slot_template():
    """The field a custom slot may cut in, in the coordinates of the custom file: x along the slot towards the
    mainboard, y up, z from the outside face (0) to the inside face of the rear panel."""
    return box(0, ZORRO_X1 - ZORRO_X0, 0, SLOT_FIELD_H, 0, T_REAR)


def custom_slot(p, i, zp):
    """Cut custom<n>.step out of the closed slot, and add custom<n>_add.step if it exists."""
    n = i + 1
    length = ZORRO_X1 - ZORRO_X0

    def load(fname, required):
        path = os.path.join(CFG_DIR, fname)
        if not os.path.exists(path):
            if required:
                config_error(f"zorro_slot_{n}=custom needs {path}. Draw the cut-outs on zorro_slot_template.step from the output folder")
            return None
        shape = cq.importers.importStep(path).val()
        bb = shape.BoundingBox()
        tol = 0.01
        if bb.xmin < -tol or bb.xmax > length + tol or bb.ymin < -tol or bb.ymax > SLOT_FIELD_H + tol:
            config_error(f"{fname} reaches outside the slot field of {length:g} x {SLOT_FIELD_H:g} mm "
                         f"(x {bb.xmin:.2f}..{bb.xmax:.2f}, y {bb.ymin:.2f}..{bb.ymax:.2f})")
        if bb.zmin < -20.0 or bb.zmax > 40.0:
            config_error(f"{fname} reaches more than 20 mm outside or 37 mm inside the rear panel")
        # file coordinates (x, y, z) -> case coordinates (ZORRO_X0 + x, D - z, card plane - half field + y)
        return shape.rotate(V(0, 0, 0), V(1, 0, 0), 90).translate(V(ZORRO_X0, D, zp - SLOT_FIELD_H / 2))

    p = p.cut(load(f"custom{n}.step", True))
    add = load(f"custom{n}_add.step", False)
    if add is not None:
        p = p.union(add)
    solids = p.solids().vals()
    if len(solids) != 1 or not p.val().isValid():
        config_error(f"zorro_slot_{n}=custom does not leave the rear panel as one solid body, check custom{n}.step")
    return p


def rear_panel():
    p = rounded(Y_TUBE1, D)
    y0, y1 = Y_TUBE1 - 1, D + 1
    # I/O cut-outs following the DeniseITX I/O shield layout, straight in the panel
    for (sx0, sy0, sx1, sy1) in IO_RECTS:
        xa, za = io_to_panel(sx0, sy0)
        xb, zb = io_to_panel(sx1, sy1)
        p = p.cut(box(min(xa, xb), max(xa, xb), y0, y1, min(za, zb), max(za, zb)))
    for (sx, sy, dia) in IO_CIRCLES:
        x, z = io_to_panel(sx, sy)
        p = p.cut(cyl((x, y0, z), (0, 1, 0), dia / 2, T_REAR + 2))
    if MAINBOARD == "pc_itx":
        xa, za = io_to_panel(-0.3, -0.3)
        xb, zb = io_to_panel(IO_SHIELD_W + 0.3, IO_SHIELD_H + 0.3)
        p = p.cut(box(min(xa, xb), max(xa, xb), y0, Y_TUBE1 + T_REAR - IO_RIM, min(za, zb), max(za, zb)))
    # Zorro openings with a lip and an insert hole on the inside
    for i, zp in enumerate(zorro_planes()):
        if ZORRO_SLOTS[i] == "custom":
            p = custom_slot(p, i, zp)
        if ZORRO_SLOTS[i] != "open":
            continue
        h = ZORRO_OPEN_W / 2
        p = p.cut(box(ZORRO_X0, ZORRO_X1, y0, y1, zp - h, zp + h))
        p = p.union(box(LIP_X0, LIP_X1, Y_TUBE1 - LIP_D, Y_TUBE1 + 0.1, zp + LIP_Z[0], zp + LIP_Z[1]))
        p = p.cut(insert_hole((LIP_X0, Y_TUBE1 - LIP_HOLE_IN, zp + LIP_HOLE_DZ), (1, 0, 0), ext=1.0))
    # DC jack and VGA to the left of the mainboard
    if CFG["back_port_dc_enable"]:
        p = p.cut(cyl((DC_X, y0, DC_Z), (0, 1, 0), DC_D / 2, T_REAR + 2))
        p = p.cut(cyl((DC_X, y0, DC_Z), (0, 1, 0), max(DC_REC_D, DC_D + 4.0) / 2, 1 + T_REAR - DC_REC_LEFT))
    if CFG["back_port_vga_enable"]:
        p = p.cut(box(VGA_X - VGA_REC_W / 2, VGA_X + VGA_REC_W / 2, y0, Y_TUBE1 + T_REAR - VGA_REC_LEFT,
                      VGA_Z - VGA_REC_H / 2, VGA_Z + VGA_REC_H / 2))
        p = p.cut(box(VGA_X - 9.0, VGA_X + 9.0, y0, y1, VGA_Z - 5.0, VGA_Z + 5.0).edges("|Y").fillet(2.0))
        for dx in (-12.5, 12.5):
            p = p.cut(cyl((VGA_X + dx, y0, VGA_Z), (0, 1, 0), 1.6, T_REAR + 2))
    # exhaust vents at the upper left
    z = 125.0
    while z < HB - 16:
        p = p.cut(box(VENT_X0, VENT_X1, y0, y1, z, z + 3.0))
        z += 7.0
    for (z0, z1) in RIB_Z:
        for x in PANEL_SCREW_X:
            p = p.cut(cyl((x, y0, (z0 + z1) / 2), (0, 1, 0), CLEAR / 2, T_REAR + 2))
    return p


def zorro_cover(i):
    """Blanking cover for Zorro opening i, patterned on a standard PCI blanking cover.
    Printed with the plug down and supports under the neck and the tab. Dropped into place and screwed to the lip with M3 x 6."""
    zp = zorro_planes()[i]
    w = COVER_W / 2
    yi = Y_TUBE1                                   # inside of the rear panel
    tt = 1.5                                       # thickness of the tab
    c = box(LIP_X1 + 0.3, ZORRO_X1 + 1.5, yi - COVER_T, yi, zp - w, zp + w)                       # plate over the opening
    c = c.union(box(LIP_X0 - tt, LIP_X1 + 0.3, yi - COVER_T, yi, zp - w, zp + LIP_Z[0] - 0.5))   # neck past the lip
    c = c.union(box(LIP_X0 - tt, LIP_X0, yi - COVER_TAB_H, yi, zp - w, zp + w))                   # tab against the lip
    # plug that enters the opening, so the cover rests in the rear panel and not only on the screw
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
    # posts that carry the grills, about 28 mm apart
    n = 6
    for i in range(n + 1):
        y = y0 + 1.5 + (y1 - y0 - 4.0 - 3.0) * i / n      # the corner posts are inset in depth as well
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


def foot_pad(i):
    """One of four separate feet, screwed on from the inside like the grill foot. Printed with the recess up."""
    x, y = FOOT_SCREWS[i]
    f = cq.Workplane("XY").circle(PAD_D / 2).extrude(PAD_H).translate((x, y, -PAD_H))
    f = f.cut(insert_hole((x, y, 0.0), (0, 0, -1), ext=PAD_EXT))
    return f.cut(cyl((x, y, -PAD_H - 1.0), (0, 0, 1), (PAD_D - 4.0) / 2, 1.0 + PAD_REC))


def tpu_pad(i):
    """Soft pad for the recess under a foot, printed in TPU. Stands 1 mm proud of the foot."""
    x, y = FOOT_SCREWS[i]
    return (cq.Workplane("XY").circle((PAD_D - 4.0 - 0.3) / 2).extrude(PAD_TPU_T)
            .translate((x, y, -PAD_H + PAD_REC - PAD_TPU_T)))


# ---------------------------------------------------------------- reference volumes (not printed)
def ref_board():
    pcb = box(X_PCB, X_PCB + PCB_T, Y_PCB_FRONT, Y_PCB_REAR, BOARD_Z0, BOARD_Z0 + PCB)
    comp = box(X_PCB - COMP_H, X_PCB, Y_PCB_FRONT + 2, Y_PCB_REAR, BOARD_Z0 + 2, BOARD_Z0 + PCB - 2)
    return pcb, comp


def ref_floppy():
    xl = XC - FD_SLOT_FROM_TOP          # lid towards the left
    return box(xl, xl + FD_H, T_FRONT + FD_GAP, T_FRONT + FD_GAP + FD_L, ZC_SLOT - FD_W / 2, ZC_SLOT + FD_W / 2)


def ref_picopsu():
    # ATX CN1: u 103..153, v 157..167 ESTIMATE from a picture of the board.
    # PicoPSU measured: 36 above the board, 23 thick, 45 wide, overhangs the front edge of the board by about 2.5.
    return box(X_PCB - PICO_H, X_PCB, Y_PCB_FRONT - PICO_OVERHANG, Y_PCB_FRONT - PICO_OVERHANG + PICO_T,
               BOARD_Z0 + 103.0, BOARD_Z0 + 103.0 + PICO_W)


def ref_zorro():
    # TandemIDE 129 x 74 in slot 1, network card 134 x 53 in slot 2. Centred on the Zorro connector (26..157 from the rear edge, ESTIMATE)
    cards = []
    yc = Y_PCB_REAR - 91.5
    for zp, (L, h), present in zip(zorro_planes(), ((129.0, 74.0), (134.0, 53.0)), ZORRO_CARDS):
        if present:
            cards.append(box(X_PCB - 1.5 - h, X_PCB - 1.5, yc - L / 2, yc + L / 2, zp - 0.8, zp + 0.8))
    return cards


TEST_UPS = [5.0, 5.5, 6.0]


VGA_TEST_LEFT = [1.2, 1.0, 0.8]


def vga_test_gauge():
    """Small plate with three VGA cut-outs, each with a different thickness left in the recess, to find the one
    the panel connector fits. Printed with the outside face down. The notches at the edge count 1, 2, 3 from the bottom.
    Local coordinates: x across, y through the plate with the outside face at 0, z up."""
    w, pitch = VGA_REC_W + 12.0, VGA_REC_H + 5.0
    p = box(0, w, 0, T_REAR, 0, len(VGA_TEST_LEFT) * pitch + 5.0)
    xc = (w - 4.0) / 2
    for i, left in enumerate(VGA_TEST_LEFT):
        zc = 5.0 + VGA_REC_H / 2 + i * pitch
        p = p.cut(box(xc - VGA_REC_W / 2, xc + VGA_REC_W / 2, left, T_REAR + 1, zc - VGA_REC_H / 2, zc + VGA_REC_H / 2))
        p = p.cut(box(xc - 9.0, xc + 9.0, -1, T_REAR + 1, zc - 5.0, zc + 5.0).edges("|Y").fillet(2.0))
        for dx in (-12.5, 12.5):
            p = p.cut(cyl((xc + dx, -1, zc), (0, 1, 0), 1.6, T_REAR + 2))
        for k in range(i + 1):
            zn = zc + 3.0 * (k - i / 2.0)
            p = p.cut(box(w - 2.0, w + 1, -1, T_REAR + 1, zn - 0.8, zn + 0.8))
    return p


def floppy_test_gauge():
    # Small gauge for trying the holes against the drive before the side panel is printed. Printed flat.
    # The side of the drive lies on the plate, the bottom plate against the long edge and the front against the short edge.
    L = FD_HOLES_Y[-1] + 8.0
    p = box(0, 14.0, 0, L, 0, 3.0)
    p = p.union(box(-2.0, 0, -2.0, L, 0, 9.0))        # long stop = bottom plate of the drive
    p = p.union(box(-2.0, 14.0, -2.0, 0, 0, 9.0))     # short stop = front of the drive
    # each hole has its own height above the bottom plate, so one print settles the height: front 5.0, middle 5.5, rear 6.0
    # the number of notches in the outer edge at a hole shows which one it is (1, 2, 3)
    for i, (hy, up) in enumerate(zip(FD_HOLES_Y, TEST_UPS)):
        p = p.cut(cyl((up, hy, -1), (0, 0, 1), 1.6, 5.0))
        for k in range(i + 1):
            p = p.cut(box(12.5, 15.0, hy - 1.0 + 3.0 * (k - i / 2.0), hy + 1.0 + 3.0 * (k - i / 2.0), -1, 4.0))
    return p


def ref_ssd():
    return box(T, T + SSD_T, SSD_Y0, SSD_Y1, SSD_Z0, SSD_Z0 + SSD_L)


def check_clearances():
    """Test the reference volumes against each other and stop if two of them occupy the same space.
    Parts that sit on the mainboard are not tested against the mainboard or each other."""
    pcb, comp = ref_board()
    items = [("the mainboard", pcb, "board"), ("the component zone above the mainboard", comp, "board"),
             ("the PicoPSU", ref_picopsu(), "board")]
    items += [(f"the Zorro card in slot {i + 1}", c, "board") for i, c in zip([i for i, on in enumerate(ZORRO_CARDS) if on], ref_zorro())]
    if FLOPPY:
        items.append(("the floppy drive", ref_floppy(), None))
    if SSD:
        items.append(("the SSD", ref_ssd(), None))
    items += [(f"switch {i + 1} behind the buttons", m, None) for i, m in enumerate(ref_mx())]
    for a in range(len(items)):
        for b in range(a + 1, len(items)):
            (na, sa, ga), (nb, sb, gb) = items[a], items[b]
            if ga is not None and ga == gb:
                continue
            common = sa.val().intersect(sb.val())
            vol = common.Volume() if common.isValid() else 0.0
            if vol > 1.0:
                bb = common.BoundingBox()
                config_error(f"{na} and {nb} collide: they overlap by {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f} mm")


# Parts that are printed more than once. They are exported as one STEP file and laid out as copies in the 3MF.
MULTI = ("zorro_cover", "foot_pad", "tpu_pad")


def base_name(name):
    head, _, tail = name.rpartition("_")
    return head if tail.isdigit() and head in MULTI else name


PARTS = {}
for _i, _state in enumerate(ZORRO_SLOTS):
    if _state == "open":
        PARTS[f"zorro_cover_{_i + 1}"] = (lambda i=_i: zorro_cover(i), (0.6, 0.6, 0.6))
for _i, (_name, _len) in enumerate(FRONT_BUTTONS):
    PARTS[_name] = (lambda i=_i: button(i), (0.9, 0.88, 0.82))
PARTS.update({
    "front_panel": (front_panel, (0.85, 0.83, 0.78)),
    "u_bracket": (u_bracket, (0.75, 0.73, 0.68)),
    "side_panel_left": (side_panel, (0.75, 0.73, 0.68)),
    "rear_panel": (rear_panel, (0.45, 0.45, 0.45)),
})
if BOTTOM == "foot_grill":
    PARTS["foot"] = (foot, (0.45, 0.45, 0.45))
elif BOTTOM == "foot_pads":
    for _i in range(4):
        PARTS[f"foot_pad_{_i + 1}"] = (lambda i=_i: foot_pad(i), (0.45, 0.45, 0.45))
    for _i in range(4):
        PARTS[f"tpu_pad_{_i + 1}"] = (lambda i=_i: tpu_pad(i), (0.15, 0.15, 0.15))

if __name__ == "__main__":
    # Output directory: first argument, else out/ in the repository root (the parent of src/)
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out")
    os.makedirs(out, exist_ok=True)
    check_clearances()
    asm = cq.Assembly(name="rook3k")
    written = set()
    for name, (fn, col) in PARTS.items():
        s = fn()
        if base_name(name) not in written:           # identical copies are written once
            cq.exporters.export(s, os.path.join(out, f"{base_name(name)}.step"))
            written.add(base_name(name))
        asm.add(s, name=name, color=cq.Color(*col))
    if HAS_ZORRO:
        cq.exporters.export(zorro_slot_template(), os.path.join(out, "zorro_slot_template.step"))
    pcb, comp = ref_board()
    asm.add(pcb, name="REF_mainboard", color=cq.Color(0.4, 0.1, 0.4))
    asm.add(comp, name="REF_component_zone", color=cq.Color(0.6, 0.3, 0.8, 0.3))
    if FLOPPY:
        asm.add(ref_floppy(), name="REF_floppy", color=cq.Color(0.8, 0.7, 0.5))
    for i, m in enumerate(ref_mx()):
        asm.add(m, name=f"REF_mx{i+1}", color=cq.Color(0.2, 0.2, 0.2))
    asm.add(ref_sd_zone(), name="REF_sd_zone", color=cq.Color(0.2, 0.5, 0.9, 0.3))
    asm.add(ref_picopsu(), name="REF_picopsu", color=cq.Color(0.9, 0.8, 0.1))
    for i, c in enumerate(ref_zorro()):
        asm.add(c, name=f"REF_zorro{i+1}", color=cq.Color(0.1, 0.6, 0.2))
    if SSD:
        asm.add(ref_ssd(), name="REF_ssd", color=cq.Color(0.3, 0.3, 0.35))
    asm.save(os.path.join(out, f"rook3k_{VERSION}.step"))
    if FLOPPY:
        tb = floppy_test_gauge()
        cq.exporters.export(tb, os.path.join(out, "floppy_test_gauge.step"))
    if CFG["back_port_vga_enable"]:
        cq.exporters.export(vga_test_gauge(), os.path.join(out, "vga_test_gauge.step"))
    print("ok", out)
