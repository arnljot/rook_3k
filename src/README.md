# Scripts

Both scripts are run from the repository root. They need Python 3 with [CadQuery](https://cadquery.readthedocs.io) and NumPy. The model was developed with CadQuery 2.8.

```bash
pip install cadquery numpy
```

## rook3k.py

The parametric model. Running it writes one STEP file per part, the test gauge for the floppy mounting holes, and the full assembly with reference volumes for the mainboard, floppy drive, PicoPSU and Zorro cards.

```bash
python src/rook3k.py [output_dir]
```

| Argument | Default | Meaning |
|---|---|---|
| `output_dir` | `out/` in the repository root | Where the STEP files are written. Existing files with the same names are overwritten. |

The options most people will want to change are in `config.txt`, described below. All other dimensions are constants near the top of the file, in millimetres. Dimensions marked `ESTIMATE` in the comments have not yet been checked against the hardware.

## config.txt

Both scripts read `config.txt` in the repository root. To use another file, add `--config <file>` to either command. Lines are `key=value`, `#` starts a comment, and a key that is left out or left empty keeps its default. An unknown key or a value of the wrong type stops the script with an error, so a typing mistake does not pass unnoticed.

| Key | Default | Meaning |
|---|---|---|
| `mainboard` | denise_itx | `denise_itx` has the DeniseITX I/O cut-outs and two Zorro slots. `pc_itx` has a standard ATX aperture for a loose I/O shield and no Zorro slots. `alicia_itx` is planned. |
| `rook_height` | 227 | Outer height without the foot. |
| `rook_depth` | 211 | Outer depth. The minimum is 210, which gives a warning because it leaves less room between the switch pins and the mainboard. |
| `rook_width` | 117 | Outer width. |
| `rook_corner_radius` | 4 | Corner radius seen from the front, 0.5 to 6. |
| `bottom` | foot_grill | `foot_grill` is one grill foot under the whole case. `foot_pads` gives four round feet with a recess for a TPU pad, and the pads. `none` leaves the bottom bare. |
| `bottom_pad_height`, `bottom_pad_diameter` | 10, 18 | Size of the feet for `foot_pads`. |
| `rook_foot_grill_height` | 3 | Height of each grill in the foot. |
| `rook_foot_grill_gap` | 2.5 | Gap between the grills. |
| `rook_foot_grills` | 3 | Number of grills. The foot height follows from these three. |
| `chamfer_recess_enable` | true | The recessed chamfer field in the front. `false` gives a flat front. |
| `deco_groove_enable` | true | The thin decorative groove on the left chamfer. |
| `pc_badge_recess_enable` | true | Recess for a 25 x 25 mm case badge. |
| `button_power` | front | `front`, `front_wide`, `back`, `back_wide` or `none`. A wide button fills the pocket and needs the reset button on the other side or absent. The `back` values are planned and not available yet. `none` gives a warning, since the DeniseITX needs a pulse on its power input to turn on. |
| `button_reset` | front | `front`, `back` or `none`. `back` is planned. With no button in the front, the pocket and the switch plate are left out. |
| `led_power_enable`, `led_drive_enable` | true, true | The power LED window and the drive LED window below it. |
| `led_window_width`, `led_window_length` | 2.2, 5 | Size of the LED windows. The defaults fit 2 x 5 mm rectangular LEDs. |
| `floppy_legacy_enable` | true | Legacy 3.5" floppy drive. `false` removes the disk slot, the eject cut-out, the shelf on the side panel and the test gauge. |
| `floppy_mount_hole_height` | 5 | Height of the mounting holes above the bottom plate of the drive. |
| `zorro_slot_1`, `zorro_slot_2` | open, open | Slot 1 is the lower one. `open` is an opening with a lip and a blanking cover, `closed` is solid panel, `custom` is solid panel with your own cut-outs, see below. |
| `ssd_mount_enable` | false | Four ears on the inside of the left side panel for a 2.5" SSD, above the floppy shelf. The drive is screwed through the ears into its side holes with M3 x 6, so nothing shows on the outside. Mount it while the side panel is off the case. |
| `back_port_vga_enable` | true | Cut-out for a DE-15 panel connector. |
| `back_port_vga_rim_thickness` | 0.8 | Material left in the recess behind the VGA cut-out, 0.8 to 1.2. `out/vga_test_gauge.step` has all three steps to try a connector against. |
| `back_port_dc_enable`, `back_port_dc_diameter` | true, 8.1 | Hole for the DC panel jack. |
| `heatinsert_diameter`, `heatinsert_depth`, `heatinsert_wall_thickness` | 4, 4.5, 1.6 | Heat-set insert holes and the minimum wall around them. |

The case size has minimums that depend on the other options. The mainboard, the power and reset switches, the PicoPSU, the Zorro cards and, when enabled, the floppy drive all have to fit. A value below the minimum stops the script and the message states the minimum. A case larger than the Bambu Lab H2D single nozzle volume of 325 x 320 x 325 mm gives a warning and is still built.

The minimums come from clearances calculated in the model. Only the default size has been built up part by part, so treat other sizes as untested. When the width changes, the chamfer field and the floppy slot keep their distance from the left edge and the extra width goes to the right.

### Custom Zorro slots

With `zorro_slot_1=custom` the script looks for `custom1.step` in the same folder as the configuration file, and `custom2.step` for slot 2. The file holds what is to be removed from the panel, so you only draw the holes.

`out/zorro_slot_template.step` shows the field you may cut in. It is 60 x 14 mm and as thick as the rear panel. In the file, x runs along the slot towards the mainboard, y is up, and z goes from the outside face of the panel at 0 to the inside face. The cut-outs may not reach outside the field in x and y, and should pass through it in z.

An optional `custom1_add.step` is joined to the panel after the cut, for a lip or a screw boss. It must overlap the panel a little, not only touch it. The script stops if the result is not one solid body.

### Clearance check

Before anything is written, the reference volumes are tested against each other: mainboard, PicoPSU, Zorro cards, floppy drive, SSD and the switches behind the buttons. If two of them occupy the same space the script stops and names them. The check is only as good as the volumes, which are simple boxes.

## make_3mf.py

Writes a Bambu Studio project with the parts oriented for printing. Each large part has its own plate. Small parts of the same kind share a plate, and parts that are needed more than once are laid out as copies. It imports `rook3k.py` and builds the parts itself, so the STEP files are not needed.

```bash
python src/make_3mf.py [version] [template.3mf] [output_dir]
```

| Argument | Default | Meaning |
|---|---|---|
| `version` | the version of the model | Label used in the file name, for example `v0.22` gives `rook3k_v0.22.3mf`. |
| `template.3mf` | `bambu_template.3mf` in the repository root | A project saved from your own Bambu Studio. Printer, filament and process settings and the bed size are taken from it. |
| `output_dir` | the repository root | Where the project file is written. |

The template is not part of the repository, because it holds the printer profile and user details of whoever saved it. To make one, open Bambu Studio, choose your printer, filament and process, and save an empty project as `bambu_template.3mf` in the repository root. Bambu Studio only loads the plate layout when the file carries project settings, which is why the template is required.
