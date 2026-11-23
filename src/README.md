# Scripts

Both scripts are run from the repository root. They need Python 3 with [CadQuery](https://cadquery.readthedocs.io) and NumPy. The model was developed with CadQuery 2.8.

```bash
pip install cadquery numpy
```

## denise_itx_case.py

The parametric model. Running it writes one STEP file per part, the test gauge for the floppy mounting holes, and the full assembly with reference volumes for the mainboard, floppy drive, PicoPSU and Zorro cards.

```bash
python src/denise_itx_case.py [output_dir]
```

| Argument | Default | Meaning |
|---|---|---|
| `output_dir` | the repository root | Where the STEP files are written. Existing files with the same names are overwritten. |

All dimensions are constants near the top of the file, in millimetres. Change them there and run the script again. Dimensions marked `ESTIMAT` in the comments are estimates that have not yet been checked against the hardware.

## make_3mf.py

Writes a Bambu Studio project with one build plate per part, each part oriented for printing. It imports `denise_itx_case.py` and builds the parts itself, so the STEP files are not needed.

```bash
python src/make_3mf.py <version> [template.3mf] [output_dir]
```

| Argument | Default | Meaning |
|---|---|---|
| `version` | `vX` | Label used in the file name, for example `v0.21` gives `DeniseITX_kabinett_v0.21.3mf`. |
| `template.3mf` | `bambu_template.3mf` in the repository root | A project saved from your own Bambu Studio. Printer, filament and process settings and the bed size are taken from it. |
| `output_dir` | the repository root | Where the project file is written. |

The template is not part of the repository, because it holds the printer profile and user details of whoever saved it. To make one, open Bambu Studio, choose your printer, filament and process, and save an empty project as `bambu_template.3mf` in the repository root. Bambu Studio only loads the plate layout when the file carries project settings, which is why the template is required.
