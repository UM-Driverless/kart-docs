<!-- reference — closed tasks, moved off tasks.md. Nothing here is actionable. -->
# Done archive

Closed items from `tasks.md`, newest first, each with the date and closing note it carried
when it was closed.


### The kart-medulla repo's stale firmware-target claims are fixed (2026-08-14)
Closed together with the kart-docs warning banner that had been standing in for the fix. What was
corrected in `kart-medulla`:

- `platformio.ini` — the "does NOT link yet" comment was already gone; the remaining
  "UNVERIFIED on hardware" note on `upload_speed = 921600` was replaced with the confirmed
  measurement (2026-08-10 flash from the Orin, 338 kB in 2.6 s, hash verified).
- `.agents/esp32s3-pinmap.md` — already corrected on 2026-08-10, verified here.
- `README.md` — the S3 map is the primary table and the classic one is collapsed and labelled;
  the FreeRTOS rates (was comms 20 Hz / control 10 Hz), the PID gains (was Kp 0.15 / Kd 0.01 /
  limit 0.15), the upload speed (was 115200/CP2102) and the `km_sdir` description were all
  brought to what `main.c` actually does.
- `AGENTS.md` — the Architecture table (was 3 tasks, control at 100 Hz, "Read AS5600"), the
  Steering Pipeline gains (was Kp 0.03 / Kd 0.0004), the classic-ESP32 hardware table and the
  AS5600 wiring table (both for a board that is not on the kart), the "40% steering limit", the
  "firmware does not drive the SDC at all" claim and the `/dev/ttyUSB0` monitor path.
- `components/km_gpio/km_gpio.h` — the `#else` branch was labelled "(current build)" and the
  file's top banner named only the classic board. Both now say which env selects which map and
  why mixing them is dangerous. Rebuilt `esp32-s3-devkitc-1` afterwards: SUCCESS.

`kart-docs` no longer carries the three "believe the code, not the repo" banners on
`assembly/electronics/kart-medulla/firmware.md`; the page states the facts directly.

### The S3 upload speed of 921600 is confirmed on hardware (2026-08-14)
It had been verified by the 2026-08-08 and 2026-08-10 flashes and recorded in the firmware repo's
`AGENTS.md`, but `platformio.ini` and the kart-docs firmware page still carried the original
"UNVERIFIED — raised from reading the datasheets" wording. Both now state the measurement.

### The camera page's YOLOv5 walkthrough is rewritten (2026-08-14)
`assembly/sensors/camera.md` described cone detection as running inside the ZED wrapper through a
custom ONNX model. That is one of two real modes, and not the default. The page now separates
them: our own `yolo_detector` node running YOLOv11n at `imgsz` 320 (the default, launched by
`perception_3d.launch.py`), and the ZED SDK's built-in object detection (`perception_zed_od.launch.py`),
which is where the ONNX and `common_stereo.yaml` steps belong. The "out of date" banner is gone.
`software/ros2/packages.md`'s parameter table was corrected against the node at the same time —
`conf_threshold` 0.25 -> 0.10, `imgsz` 640 -> 320, `device` default is auto not `cpu`, and
`crop_top` was missing.

### The wiring SVG showed the Cytron on 12 V — fixed (2026-08-08)

The 2026-07-30 decision below fixed `wiring.yaml` and the prose pages but never reached
`wiring/images/wiring-global.svg`, which still had the Cytron box at `25 A · 12 V`, the steering
motor at `DC 12 V`, and a red wire drawn from the **12 V rail** labelled `12 V → Cytron`. The
third was a topology error, not a wording one, so it needed a reroute: the feed now branches off
the battery run at (900, 1410) and reaches the Cytron via the x = 1610 corridor, in bold stroke
per the legend's "bold = 48 V". Rubén confirmed the same day: "cytron is powered directly from
the battery". The Cytron box now reads `25 A · 7–58 V in` (its actual input range) and the motor
box `fed from the 48 V bridge`.

### Cytron H-bridge runs off the 48 V pack, not the 12 V rail (2026-07-30)
Settled by Rubén. `steering/index.md` was right; `kart-medulla/index.md` and
`power/battery.md` were wrong and are fixed. In `wiring/wiring.yaml` the Cytron's supply pin
moved from the `12V` net to `PACK48` and was renamed `v12` → `vin`, and the `STEER_M+`/`STEER_M-`
motor leads are re-labelled 48 V. The MD25HV accepts 7–58 V so the pack is in spec. The
"permanent, not switched through the mode switch" part of the original decision stands — that
was about inrush browning out the Orin, not about which rail.

### PCB fabrication sponsor identified: AISLER (2026-07-30)
Named in the 2026-07-29 LinkedIn post ("Thanks to AISLER for sponsoring the fabrication").
Added to `docs/credits.md` under Partners & sponsors, and the TODO comment removed.

### Reconciled the mission lists across the docs (2026-07-30)
The three pages listed three different subsets. Authoritative set taken from
`kart_control/scripts/state_machine_node.py:34` (`AUTONOMOUS_MISSIONS`) plus the
`manual`/`remote_control` branch at `:148`: ten missions total. `software/state_machine.md`
now carries the full list and cites its source; `dashboard.md` and `ros2/packages.md` say which
eight have buttons and link to it. Recorded there as a known bug: `throttle_test` is gated as
autonomous but missing from `protocol.py`'s `MISSIONS` map, so `MISSIONS.get(..., 0)` sends it
to the ESP32 as `manual` (ID 0).

### Audited the non-electronics docs for contradictions and stale claims (2026-07-30)
Covered `docs/software/**`, `docs/assembly/{steering,sensors,pneumatic-braking,powertrain}/**`,
`docs/rules/**`, `docs/build-journey/**` and the top-level pages, checked against the
`kart-brain` source and the live Orin. Findings and fixes are in `history.md` (2026-07-30).
What could not be settled from the desk was split back out into its own Ready entries.

### llms.txt and llms-full.txt were 404 on the live site (2026-07-19)
`generate_llm_files.py` parsed `mkdocs.yml` with a custom `SafeLoader` that knew about
`!ENV` but not `!!python/name:`, which mkdocs-material uses for its emoji index and
superfences formatter. The script died on `mkdocs.yml:21` from commit `e0c057c`
(2026-07-10, the Build Journey section) onward, so both files were missing from every
deploy for nine days. Fixed with a multi-constructor for the `python/name` tag prefix.
The failure survived that long because `generate_llm_hook.py` printed only `result.stderr`
while the script reports errors on stdout — the warning always rendered with an empty
reason and read as cosmetic noise. The hook now prints both streams.

### Build Journey section (2026-07-10)
Ported the portfolio's build-journey into kart-docs as a team-shareable section:
`docs/build-journey/index.md` + images/videos under `docs/build-journey/{images,videos}/`,
nav entry, `attr_list`/`md_in_html`/`pymdownx.emoji` extensions, and a primary
"Read the Build Journey" button at the bottom of the home page. Added the 2026-07-10
"first autonomous drive" post (latest LinkedIn). NOTE: the 2026-07-08 "steering gear
materials" (PPA) post is published but intentionally not added yet.

### Credits page (2026-07-10)
`docs/credits.md` — contributors (subsystem-tagged, one list, append-only) + partners &
sponsors. Full names resolved from the Notion workspace member list. Team members add their
own LinkedIn/GitHub via the GitHub "Edit" pencil (git-practice on-ramp); how-to is a source
comment, not shown on the page. Lead entry kept modest — shared work (ROS 2, dashboard)
credited to the people who did it, not the lead.


## 2026-09-19 — Reduce build-journey media downloads

Compressed the 20 displayed images from 24,154,189 to 3,293,544 bytes (86.4%); kept original files and lossless diagram pixels. Added eight video posters, on-demand video loading, explicit media dimensions, and a repeatable media script. Strict build passed. Browser checks at 1280px and 390px decoded every image, played all eight videos, and found no initial MP4 requests or horizontal overflow.
