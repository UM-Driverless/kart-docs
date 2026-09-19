<!-- consult-selectively: the project's task board (one per repo, at the root). Claim a task by setting status In progress + your id, commit, then Done. -->
# Task Board

Done items do not stay on the board. When one closes, move it — with its date and closing note —
to `tasks/done-archive.md`, which holds nothing actionable. Exception: a done step of a task that is
still open stays put, since archiving it strips the remaining open step of the context saying what
was already settled. A cluster moves to the archive whole, once its last step closes.

## Ready

### Add a pulldown on CMD_STEER_PWM so a resetting ESP32 cannot drive the steering motor
On 2026-08-08 the steering swung hard to one lock while the ESP32-S3 was being reflashed and
broke teeth off the steering gears. The kart was in autonomous at the time. Rubén's reading of
the event is that the swing happened during the flash itself, while the chip sat in the
bootloader running no code at all — which means no firmware change and no change on the Orin
can prevent a repeat, because nothing on the ESP32 is executing during that window.

The board has no hardware default for steering. `docs/assembly/electronics/kart-medulla/index.md`
states it plainly: "Steering is NOT muxed — the ESP32 always drives the Cytron H-bridge
directly; in manual mode firmware sets PWM = 0." So the steering's only safety is firmware
writing zero, which by definition does not exist while the chip is unbooted, resetting, or
crashed. `CMD_STEER_PWM` (CN9.1, ESP32-S3 GPIO 40) is left floating in all three cases, and a
floating CMOS line can sit above the Cytron MD25HV's input threshold indefinitely.

Fix: a pulldown from `CMD_STEER_PWM` to GND, at the Cytron end of the net so it also protects
against the connector being unplugged. 10 kΩ matches the pulldown already used on this board
for `SELECT_THROTTLE` (GPIO 15) and is nowhere near the ESP32's drive limit. The firmware
drives the Cytron in sign-magnitude mode — PWM duty for magnitude, a separate DIR pin for sign
(`km_act`) — so zero on the PWM line means the motor is off and DIR does not matter. **Confirm
the Cytron's mode switches actually select sign-magnitude before relying on that**: in a
locked-antiphase mode a low PWM line would mean full reverse, i.e. the pulldown would cause the
exact failure it is meant to prevent. A second pulldown on `CMD_STEER_DIR` (CN8.3) is cheap and
makes the resting direction deterministic.

This is the same protection throttle already has and steering was never given. Do it as a
rework on the current board, not only in v2 — the kart is being flashed regularly today.

Worth confirming with a meter while the fix is being made: probe CN9.1 against GND, motor
unplugged, and flash. A reading clearly above 0 V during the bootloader window confirms the
mechanism; near 0 V the whole time means the cause was something else and the fix is the
firmware/Orin side instead (see kart-brain `tasks.md`, same date).

Until the resistor exists, the operating rule is to de-power the Cytron or unplug the steering
motor before every flash.

### Split the medulla's ground terminals between GND and GND_SIG
The harness now has two grounds: `GND` (power) and `GND_SIG` (sensors, black + white
stripe), tied only at the rear ground Wago block near the battery and the 12 V / 24 V
regulators. All three medulla ground terminals (CN1.3, CN9.3, CN10.3) are still on the
power `GND` net in `docs/assembly/electronics/wiring/wiring.yaml`, because which of them
the PCB routes to its analog ground is not recorded here. Check the authoritative KiCad
project (`dv-hardware/projects/kart-medulla`): if the board has separate analog and power
grounds, move the analog terminal to `GND_SIG`; if it has one ground plane, say so in
`wiring.md` so nobody assumes the split reaches the board.

### Redraw the wiring SVG for the two-ground split
`docs/assembly/electronics/wiring/images/wiring-global.svg` is hand-drawn and still shows
one common ground. It needs the `GND_SIG` return, the rear Wago star point, and the
striped-black convention, otherwise the diagram and the generated wire table disagree.
Background on the two-ground split: `docs/assembly/electronics/wiring.md`, section
"Why two grounds".

### The dv-hardware netlist's CN designators do not match the board silkscreen
Settled 2026-07-30: on the board, **CN4.3 is REVERSE and CN8.1 is `SDC_IN_LOW_SIDE`**, as
kart-docs has always said. But `dv-hardware/projects/kart-medulla/output/netlist.net`
(exported 2026-05-07) puts `/REVERSE_WIRE` on **CN8 pin 1** and `/SDC_IN_LOW_SIDE` on **CN5** —
so its `CN` reference designators are not the silkscreen `CN` numbers, and it is not a simple
pairwise swap either. Anyone wiring from that netlist would land the reverse command on the
shutdown-circuit terminal.

The KiCad project is a ConvertEDA import of the EasyEDA original, which is the likely place the
designators were reassigned. Work out the real mapping, then either renumber the connectors in
the KiCad schematic to match the silkscreen or put a loud warning at the top of the netlist and
in `projects/kart-medulla/README.md`. Until that is done, **do not treat the netlist as
authoritative for terminal numbers** — only for nets and part designators.

### Upstream pinout doc disagrees with itself on CMD_STEER_DIR
`dv-hardware/projects/kart-medulla/docs/pinout-esp32-s3.md` has `CMD_STEER_DIR__3V3` on
**GPIO 17** in its pin table (Pin 32, "Moved here from GPIO 0 on 2026-05-08") but its own prose
at the end of the file says "`CMD_STEER_PWM` (GPIO 40) and `CMD_STEER_DIR` (GPIO 0) —
unchanged". kart-docs follows the table (GPIO 17). Fix the prose upstream so the file stops
contradicting itself; the schematic decides.

### Refresh the two rows dv-hardware has not caught up on
`dv-hardware`'s pinout table still lists GPIO 1 as `PRESSURE_3` and GPIO 3 as `BUZZER` in its
`Signal` column, even though the same file's notes describe both reassignments (steering-angle
PWM capture and `CMD_COMPRESSOR_PWM`). kart-docs is ahead on these two rows and now says so
explicitly, but the right fix is upstream — update the `Signal` cells there so the
"dv-hardware wins" rule can go back to being unconditional.

### Decide whether the kart is presented as a competition entry
`docs/index.md` says "This prototype is not intended to compete, so no specific racing
regulations apply." `docs/rules/as_state_machine.md` calls the kart an "APC entry", tracks
compliance gaps against FS rules ("NOT currently implemented but are required for competition
compliance"), and the repo ships `FS-AI_2026_APC_Technical_Rules_v1.pdf`. `docs/about.md` also
lists competing as a medium-term objective. Pick one position and make the three pages agree.

### Reconcile the two accounts of why the AS5600 was dropped
The repos disagree, and `assembly/steering/sensor/index.md` now says so rather than picking.
`kart-medulla/history.md` (2026-07-11/12) says the AS5600 physically cannot read the kart's magnet —
it needs the axial field to vary across a 1 mm circle, and two large magnets stuck sideways give a
field that is strong but uniform, so magnet-detect stayed at zero even touching the chip.
`~/dv/kart/steering/history.md` (2026-07-31) says *"magnet tolerance turned out not to be a real risk
on this kart — the AS5600 already read the installed magnets fine"*. The bench magnet was handheld
and the kart's is mounted, which may explain both, but nobody has written that down. It matters
because it decides whether a future sensor choice carries a magnet constraint or not.

### Record the steering sensor mount's CAD source and adjustment range
The MT6701 sits on a 3D-printed adjustable mount at the front of the kart; the adjustment is what
sets the air gap and angular zero after assembly. `~/dv/kart/steering/history.md` (2026-07-31) notes
that the mount's CAD source and its adjustment range are recorded nowhere — worth capturing from the
Fusion 360 model before anyone reprints it. The fastener page and the Angle Sensor page both
reference the mount now, so they are where it goes.

### Add the MT6701 to the BOM
`assembly/steering/bom.yaml` lists the AS5600 (€2.00) as the steering angle sensor and the MT6701 is
absent, so the BOM describes a kart that no longer exists. The AS5600 rows should stay — the parts
were bought, and the classic-ESP32 fallback build still uses that driver — but need marking as
superseded, with the MT6701 module (~€10, AliExpress) added as the fitted part. `bom/index.md` and
`bom/full.md` regenerate from the YAML.

### Pull the wheel-bearing spacer dimensions out of the Fusion 360 model
`docs/assembly/index.md` describes the spacer tube between the wheel bearings with its ID, OD and
length written as `?`. The whole kart is modelled in Fusion 360, so this is a CAD lookup rather than
a trip to the workshop. While filling it in, name it properly and say which assembly it belongs to —
the original note just called it "a tube", which is why the item was unrecognisable.

### Document the ZED2's published topics and the RViz2 cone-detection setup
Two gaps left as a source comment on `docs/assembly/sensors/camera.md` since the page was written:
which ZED topics the stack actually consumes (the page has a commented-out table marked "CORREGIR
POR TOPICS CORRECTOS"), and which packages have to be installed to see cone detections in RViz2.
Both are answerable from `kart-brain`'s launch files and the ZED wrapper config.

### Build-journey mini-entries (blocked on media from Rubén)
Convention in `AGENTS.md` (build-journey section): small dated entries for build moments too minor for a LinkedIn post, no LinkedIn link, mirrored to the portfolio build journey. First two to write, both waiting on photos + facts from Rubén:
- Steel steering gear arrived (replaces the worn 3D-printed gear the steering posts documented).
- MOSFET driver board 3.3 V fix (5 V-designed input stage: bridge rectifier removed, input resistor swapped; verify part numbers/values against the schematic in `~/dv/kart/kart-medulla/` before publishing).

## In progress

_(none)_

## Done

Closed items live in [`tasks/done-archive.md`](tasks/done-archive.md), with the date and
closing note each one carried. Nothing actionable is kept there.
