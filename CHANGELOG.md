# Changelog

All notable changes to Rook 3K, a case for the DeniseITX mainboard. Versions are tagged `vX.Y` in git.

## v0.28 - Eject button for the floppy drive

- New part `button_eject.step`. A Chinon FZ-354 without face plate has no button of its own, only a sheet metal hook. The button is a press fit on the hook, like a saddle: a lip goes down behind the bent strip and the tongue of the hook goes up into the button. It goes on the drive first, and threads into the front panel when the side panel is swung in on its front edge. That movement is checked in the model. The face of the button is flat, parallel to the front of the case, with rounded edges.
- `eject_test_buttons.step` has the button with slots of 0.5, 0.6 and 0.7 mm for the sheet metal, marked with one, two and three notches. It has its own plate in the 3MF project. The buttons are printed standing on end, with support under the lip.
- The cut-out in the front panel moves 2.2 mm towards the end of the disk slot and sits wholly on the chamfer, 0.7 mm from the groove. It has rounded corners.
- The drive sits 2.6 mm behind the front panel, up from 0.3, to make room for the hook and the button. The mounting holes in the shelf of the side panel move with it.
- The front panel and the left side panel change. The other parts are the same as in v0.27.
- The position of the hook is read from pictures of the drive, and its travel is measured roughly. All of it is an estimate until the drive has been tried in a complete case.

## v0.27 - Alicia 1200 connectors in a pocket on the inside

- Only `mainboard=alicia_itx` changes. The parts of the default configuration are the same as in v0.26.
- The rear panel is 3 mm thick, which left the D-sub connectors too short on the outside for a plug to seat. The connector housings and the rear edge of the board now sit in a pocket on the inside of the rear panel, which leaves 1 mm of material, as a sheet metal shield would. The outside of the panel stays flat.
- The Alicia therefore sits 2 mm further back than a DeniseITX, and the mounting posts in the U-bracket move with it. A U-bracket printed for one board does not fit the other.
- The openings for RGB and the two joystick ports are D-shaped.
- The dimensions have still not been verified against an actual Alicia.

## v0.26 - Alicia 1200 added, VGA cut-out off by default

- `mainboard=alicia_itx` is available. The rear panel gets cut-outs for RGB, keyboard, mouse, two joystick ports, audio and PCMCIA, and no Zorro slots. The dimensions have not been verified against an actual Alicia yet, and the script gives a warning. The cut-outs are plain rectangles and round holes for now.
- `back_port_vga_enable` is now false by default. The cut-out is for a panel connector from a scan doubler, which most builds do not have. Set it to true to get the rear panel of v0.25.
- With the default configuration only the rear panel changes. `out/vga_test_gauge.step` is no longer in `out/`, the script writes it when the VGA cut-out is enabled.
- `src/render.py` draws the line drawings and the shaded picture in the README from the model, for any configuration.

## v0.25 - VGA recess set from the test gauge

- The recess for the VGA panel connector now leaves 0.8 mm of material, down from 1.5. All three steps of the test gauge fitted, 1.2, 1.0 and 0.8 mm, and the deepest was chosen.
- `back_port_vga_rim_thickness` sets this value, from 0.8 to 1.2.
- Only the rear panel changes. The other parts are the same as in v0.24.
- README shows a shaded render of the case below the line drawings.
- The VGA test gauge is still exported as `out/vga_test_gauge.step`, but no longer has a plate in the 3MF project.

## v0.24 - One screw size, panels fastened from the inside

- Every screw is now M3 x 6 with a cylinder head, with 3 mm under the head and 3 mm in the insert.
- Front panel: the screws through the front ribs of the U-bracket have counterbores for the heads. The right hand screws moved 3 mm towards the middle.
- Rear panel: fastened from the inside. The rear panel has four bosses with inserts that sit in pockets in the rear ribs. There are no screws on the back of the case any more.
- Left side panel: cylinder head screws in counterbores instead of countersunk screws, with a boss behind each. `side_plug.step` is a plug that hides the screw head.
- The ribs of the U-bracket are 10 mm high and 11 mm deep, up from 8 by 8, to make room for this.
- The U-bracket, the left side panel and the rear panel change. The front panel changes only in the position of two insert holes. A rear panel from v0.22 or v0.23 still lines up with the new U-bracket for a trial fit.
- README lists the screws and inserts and the assembly order.
- Not test printed in this form.

## v0.23 - Mainboard profiles, slot states and more options

- `mainboard` selects the board profile. `denise_itx` is unchanged, `pc_itx` gives a standard ATX aperture with a pocket for a loose I/O shield, `alicia_itx` is reserved.
- `zorro_slot_1` and `zorro_slot_2` replace `zorro_cutout_enable`. Each slot is `open`, `closed` or `custom`. A custom slot cuts a user supplied STEP file out of the closed panel, and `out/zorro_slot_template.step` shows the field to draw on.
- `button_power` and `button_reset` place each button on its own: in the front, absent, or for power one wide button. Values for buttons at the back are reserved and not available yet.
- `led_power_enable` and `led_drive_enable` switch each LED window.
- `bottom` chooses the grill foot, four feet with TPU pads, or nothing.
- `ssd_mount_enable` adds four ears on the inside of the left side panel for a 2.5" SSD. The drive is screwed through its side holes, so no screws show on the outside.
- Clearance check: the reference volumes are tested against each other before the parts are written.
- The 3MF project puts the two buttons on one plate, and lays out feet and pads as four copies.
- Test print of the rear panel verified the I/O cut-outs, the Zorro openings and the DC jack. The VGA recess did not fit.
- `out/vga_test_gauge.step` is a small plate with three VGA cut-outs that leave 1.2, 1.0 and 0.8 mm in the recess, to find the thickness the panel connector needs. It has its own plate in the 3MF project.
- The default configuration gives the same parts as v0.22.
- Not test printed: `pc_itx`, the feet with pads, the SSD mount and custom slots.

## v0.22 - Configuration file, English names and verified fits

- Default depth increased from 210 to 211 mm, which gives 1 mm more between the switch pins and the mainboard. 210 is still allowed and gives a warning. The U-bracket, the left side panel and the foot change; the front and rear panels are unchanged.
- Test print of the U-bracket verified the MX switch plate and the four mainboard mounting holes.
- Code, comments, part names and file names are now in English. The model script is `src/rook3k.py`, the assembly is `out/rook3k_v0.22.step` and the Bambu Studio project is `rook3k_v0.22.3mf`. Earlier versions in the history are in Norwegian.
- The two identical Zorro blanking covers are exported as one file, `zorro_cover.step`.
- make_3mf.py takes the version from the model when none is given.
- Renders are regenerated with fixed file names, so the README links stay valid between versions.
- `config.txt` added and read by both scripts: case size with minimum checks, corner radius, foot grills, and switches for the chamfer recess, badge recess, legacy floppy, Zorro cut-outs, VGA and DC ports, plus LED window and heat-set insert dimensions.
- Floppy mounting holes verified with the test gauge against a Chinon FZ-354 without face plate. Hole height corrected from 5.75 to 5.0 mm in the model.
- Zorro openings and lips are positioned from the right side, so they follow the mainboard when the width changes.
- README has a printing section: designed for the Bambu Lab H2D, with part sizes and an assessment for 254 mm class printers.
- STL exports removed; the model script no longer writes them.
- Scripts moved to `src/`, with a README on how to run them. Both take an optional output directory.
- STEP files and renders moved to `out/`, which is where the model script now writes by default. The 3MF project stays in the repository root.
- Logo added: a chess rook with circuit board traces, as mark, lockup and badge.
- The project is named Rook 3K.
- Source location set to https://github.com/arnljot/rook_3k.
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
