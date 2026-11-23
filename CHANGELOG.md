# Changelog

All notable changes to the DeniseITX case. Versions are tagged `vX.Y` in git.

## Unreleased

- Licensed under CERN-OHL-S-2.0. Copyright and licence notices added to README and scripts.

## v0.21 - Connector recesses and 3MF export

- 12.1 mm recess for the DC jack and a 33.2 x 13.3 mm recess for the VGA panel connector on the inside of the rear panel; DC hole 8.1 mm.
- make_3mf.py writes a Bambu Studio project with one build plate per part, oriented for printing, using project settings from a template project.

## v0.20 - Connectors above the Zorro openings

- VGA (now horizontal) and DC inlet moved above the Zorro openings to keep the lip screws accessible.
- Blanking cover gets a plug that seats in the opening.

## v0.19 - Covers patterned on a PCI cover

- Lip and blanking cover follow the layout of a standard PCI slot cover (tab, screw in the insertion direction, hole 6.45 mm inside the panel), narrowed and shortened for the DeniseITX slot pitch.

## v0.18 - Rear panel rework

- I/O cut-outs following the DeniseITX I/O shield layout built into the rear panel; the separate shield aperture is gone.
- Two Zorro openings (15.24 mm pitch) with an inner lip and insert hole, and a blanking cover.
- VGA (DE-15) and DC inlet cut-outs.

## v0.17 - Heat-set inserts

- M3 brass heat-set insert holes (4.0 x 4.5 mm) for foot, front panel, rear panel, side panel and mainboard standoffs.
- Contact pads on the side panel at the four screws.

## v0.16 - Test gauge and STL export

- Small printable gauge to verify floppy hole positions and hole height (5.0, 5.5 and 6.0 mm) before printing the side panel.
- Hole height set to 5.75 mm pending that test.
- STL export for all parts.

## v0.15 - Exact floppy holes

- Slots replaced by three exact M3 holes at 21, 81 and 111 mm from the drive front; drive length 129 mm.

## v0.14 - Simpler shelf

- Shelf reduced to a plain T with three small gussets.
- Slotted holes covering the mounting patterns in the Mitsubishi MF355B specification and SFF-8301.

## v0.13 - Floppy shelf

- Shelf on the left side panel that carries the floppy drive; body height 227 mm.
- The panel with drive swings in around its front edge so the eject button enters its cut-out.

## v0.12 - Foot corner posts

- Corner posts of the foot inset in both directions so the slats run unbroken around the corners.

## v0.11 - Switches behind the buttons

- Button plungers with a foot and a cross socket for MX-style key switches; switch plate integrated in the U-bracket.
- Depth increased to 210 mm so the switches fit between front panel and mainboard.
- Keep-out zone reserved behind the right front edge for a future SD card opening.

## v0.10 - Smaller buttons

- Buttons reduced to 7 x 12 and 7 x 8 mm so the button pocket matches the badge recess height.

## v0.9 - Wider case, recess shifted left

- Width increased to 117 mm; the chamfer field keeps its own symmetry but moves left so the floppy clears the PicoPSU.
- Left edge equals the top edge (22 mm). Buttons and badge recess moved to the lower right.
- Depth increased to 195 mm to make room for the PicoPSU in front of the mainboard.

## v0.8 - Measured component data

- Floppy raised to clear the disk-on-module on the accelerator card; body height 225 mm.
- Slot offset in the drive and PicoPSU height taken from measurements.
- Known issue: floppy drive and PicoPSU collide with a centred slot at 95 mm width.

## v0.7 - Foot symmetry fix

- Foot screw blocks were asymmetric and filled the slats on one side. Now mirrored and inset.

## v0.6 - Badge recess

- Top edge grooves removed; chamfer groove limited to the left chamfer face.
- 27 x 27 x 1 mm recess for a 25 mm PC badge in the lower left corner.

## v0.5 - Front detailing

- Button pocket aligned with the lower border of the top edge; gap between buttons halved; buttons moved 4 mm further left.
- Decorative 1.8 x 0.5 mm groove in the left chamfer and two grooves on the top edge.

## v0.4 - Buttons on the left edge

- Power and reset moved to the left edge, with the pocket open through the side of the front.

## v0.3 - Slimmer top edge

- Top edge reduced to 22 mm, close to the side edges.
- Centre groove widened to 14 mm; chamfers 20.3 mm.
- Buttons turned upright and moved towards the top right corner.

## v0.2 - First design review

- Floppy drive rotated 180 degrees and raised so the slot sits directly below the LED windows.
- Side chamfers narrowed from 31 to 23.3 mm; top edge raised to 32 mm.
- Rectangular power and reset buttons in a pocket on the top edge.
- Foot mirrored so both long sides show the slats.
- Rear panel takes a standard ITX I/O shield (158.75 x 44.45 mm aperture with flange rebate).

## v0.1 - Initial concept

- First parametric CadQuery model of an upright case for the DeniseITX mainboard: front panel, U-bracket (top, right side, bottom), left side panel, rear panel and a slatted foot.
- Amiga 3000 style front rotated 90 degrees: recessed chamfer field with a vertical groove holding the floppy slot.
- Outer size 95 x 187 x 226 mm. Reference volumes for mainboard, floppy drive, PicoPSU and Zorro cards.
