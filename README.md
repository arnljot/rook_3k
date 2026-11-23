# DeniseITX case

A 3D-printable case for the Amiga DeniseITX mainboard.

The design is a tribute to the Commodore Amiga 3000 desktop case and to the Checkmate 1500 Plus case, which is itself a tribute to the same Amiga 3000.

A small volume has been desirable but never an absolute goal. Aesthetics and the creator's own configuration and preferences have guided the design.

## Status

Work in progress. The parts are modelled but have not been test printed, and several dimensions are still estimates. See [CHANGELOG.md](CHANGELOG.md).

## Contents

- `denise_itx_case.py` is the parametric CadQuery model. Running it writes the STEP files.
- `make_3mf.py` writes a Bambu Studio project with one build plate per part. It needs a `bambu_template.3mf` saved from your own Bambu Studio.
- `*.step` are the exported parts and the full assembly.

## Credits

Designed by Arnljot Arntsen. The CAD model was written with Claude Fable 5.2 (Anthropic) as an AI tool, under the designer's direction. All design decisions and all responsibility for the design rest with the designer.

## License

Not decided yet.
