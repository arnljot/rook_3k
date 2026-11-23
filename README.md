# Rook 3K

![Rook 3K](logo/rook3k_lockup.svg)

A 3D-printable tower case for the Amiga DeniseITX Mini-ITX mainboard.

![Rook 3K seen from four angles](out/DeniseITX_kabinett_v0.21_oversikt.png)

![Rear panel with I/O, Zorro, VGA and DC cut-outs](out/DeniseITX_kabinett_v0.21_bakpanel.png)

*Renders of the v0.21 CAD model.*

The design is a tribute to the Commodore Amiga 3000 desktop case and to the Checkmate 1500 Plus case, which is itself a tribute to the same Amiga 3000. The name follows from that: the rook is the tower among the chess pieces, and 3K is 3000.

A small volume has been desirable but never an absolute goal. Aesthetics and the creator's own configuration and preferences have guided the design.

## Status

Work in progress. The parts are modelled but have not been test printed, and several dimensions are still estimates. See [CHANGELOG.md](CHANGELOG.md).

## Hardware

The model is designed for M3 x 3.0 brass heat-set inserts from [CNC Kitchen](https://cnckitchen.com). The insert holes are 4.0 mm in diameter and 4.5 mm deep, with a narrower relief behind the insert for the screw. The parameters `INS_D`, `INS_DEPTH` and `INS_EXT` in `src/denise_itx_case.py` can be changed to suit other inserts.

## Contents

- `src/denise_itx_case.py` is the parametric CadQuery model. Running it writes the STEP files.
- `src/make_3mf.py` writes a Bambu Studio project with one build plate per part. It needs a `bambu_template.3mf` saved from your own Bambu Studio.
- [src/README.md](src/README.md) explains how to run the scripts and which arguments they take.
- `out/` holds the exported STEP files, one per part plus the full assembly, and the renders.
- `DeniseITX_kabinettv0.21.3mf` is the Bambu Studio project for v0.21.
- `logo/` holds the logo as SVG: the mark, a lockup with the name, and a badge version for the 25 mm recess in the front panel. The lettering is Space Grotesk, converted to outlines.

## Credits

Designed by Arnljot Arntsen. The CAD model was written with Claude Fable 5.2 (Anthropic) as an AI tool, under the designer's direction. All design decisions and all responsibility for the design rest with the designer.

## License

Copyright (C) 2026 Arnljot Arntsen.

This source describes Open Hardware and is licensed under the CERN-OHL-S v2. You may redistribute and modify this source and make products using it under the terms of the CERN-OHL-S v2. The full text is in [LICENSE](LICENSE).

This source is distributed WITHOUT ANY EXPRESS OR IMPLIED WARRANTY, INCLUDING OF MERCHANTABILITY, SATISFACTORY QUALITY AND FITNESS FOR A PARTICULAR PURPOSE. Please see the CERN-OHL-S v2 for applicable conditions.

Source location: https://github.com/arnljot/rook_3k

As per CERN-OHL-S v2 section 4, should you produce hardware based on this source, you must where practicable maintain the source location visible on the product or in its documentation.
