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
| `rook_height` | 227 | Outer height without the foot. |
| `rook_depth` | 211 | Outer depth. The minimum is 210, which gives a warning because it leaves less room between the switch pins and the mainboard. |
| `rook_width` | 117 | Outer width. |
| `rook_corner_radius` | 4 | Corner radius seen from the front, 0.5 to 6. |
| `rook_foot_grill_height` | 3 | Height of each grill in the foot. |
| `rook_foot_grill_gap` | 2.5 | Gap between the grills. |
| `rook_foot_grills` | 3 | Number of grills. The foot height follows from these three. |
| `chamfer_recess_enable` | true | The recessed chamfer field in the front. `false` gives a flat front. |
| `deco_groove_enable` | true | The thin decorative groove on the left chamfer. |
| `pc_badge_recess_enable` | true | Recess for a 25 x 25 mm case badge. |
| `led_window_width`, `led_window_length` | 2.2, 5 | The two LED windows. The defaults fit 2 x 5 mm rectangular LEDs. |
| `floppy_legacy_enable` | true | Legacy 3.5" floppy drive. `false` removes the disk slot, the eject cut-out, the shelf on the side panel and the test gauge. |
| `floppy_mount_hole_height` | 5 | Height of the mounting holes above the bottom plate of the drive. |
| `zorro_cutout_enable` | true | Openings, lips and blanking covers for the two Zorro slots. |
| `back_port_vga_enable` | true | Cut-out for a DE-15 panel connector. |
| `back_port_dc_enable`, `back_port_dc_diameter` | true, 8.1 | Hole for the DC panel jack. |
| `heatinsert_diameter`, `heatinsert_depth`, `heatinsert_wall_thickness` | 4, 4.5, 1.6 | Heat-set insert holes and the minimum wall around them. |

The case size has minimums that depend on the other options. The mainboard, the power and reset switches, the PicoPSU, the Zorro cards and, when enabled, the floppy drive all have to fit. A value below the minimum stops the script and the message states the minimum. A case larger than the Bambu Lab H2D single nozzle volume of 325 x 320 x 325 mm gives a warning and is still built.

The minimums come from clearances calculated in the model. Only the default size has been built up part by part, so treat other sizes as untested. When the width changes, the chamfer field and the floppy slot keep their distance from the left edge and the extra width goes to the right.

## make_3mf.py

Writes a Bambu Studio project with one build plate per part, each part oriented for printing. It imports `rook3k.py` and builds the parts itself, so the STEP files are not needed.

```bash
python src/make_3mf.py [version] [template.3mf] [output_dir]
```

| Argument | Default | Meaning |
|---|---|---|
| `version` | the version of the model | Label used in the file name, for example `v0.22` gives `rook3k_v0.22.3mf`. |
| `template.3mf` | `bambu_template.3mf` in the repository root | A project saved from your own Bambu Studio. Printer, filament and process settings and the bed size are taken from it. |
| `output_dir` | the repository root | Where the project file is written. |

The template is not part of the repository, because it holds the printer profile and user details of whoever saved it. To make one, open Bambu Studio, choose your printer, filament and process, and save an empty project as `bambu_template.3mf` in the repository root. Bambu Studio only loads the plate layout when the file carries project settings, which is why the template is required.
