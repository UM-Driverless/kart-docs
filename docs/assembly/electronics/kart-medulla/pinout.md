<!-- sync_pinout source-sha256: e3cf840001fb978ac21ac25462cb68c74e256adfe43e7e5a1b7ba8f94789611b -->
<!-- sync_pinout source-commit: f31aee8909ad7d7e10c654b739ed06bc67a11c0a -->
!!! info "Generated page — edit it in `dv-hardware`, not here"
    This is a verbatim copy of [`projects/kart-medulla/docs/pinout-cn-connectors.md`](https://github.com/UM-Driverless/dv-hardware/blob/f31aee8909ad7d7e10c654b739ed06bc67a11c0a/projects/kart-medulla/docs/pinout-cn-connectors.md) in the **dv-hardware**
    repo, which holds the KiCad schematic that defines these assignments. Changes
    made here are overwritten. To update: edit the file in dv-hardware, then run
    `uv run python scripts/sync_pinout.py` in kart-docs and commit the result.

    Pinned to dv-hardware commit [`f31aee8909ad`](https://github.com/UM-Driverless/dv-hardware/commit/f31aee8909ad7d7e10c654b739ed06bc67a11c0a) (2026-09-26). The link above is a permalink to that exact revision, so it keeps meaning what it meant when this copy was made; dv-hardware may have newer commits.

    Related: [Kart Medulla board](index.md) · [whole-kart wire list](../wiring.md#wire-list-whole-kart)
    · ESP32-S3 GPIO map in dv-hardware's `pinout-esp32-s3.md`.

# Push-in connector pinout (CN1–CN10)

> **Authoritative source: the schematic in this same project folder (`../kart-medulla.kicad_sch` + `../kart-medulla_P1.kicad_sch`).** This document mirrors the per-CN pin assignments for human reading. When this doc and the schematic disagree, the schematic wins; fix this file. Re-verify before each fab release.

The medulla PCB has 10 three-pin push-in (1990012) connectors arranged around the ESP32-S3 dev module. Each CN is a 3-pin Wago-style cage-clamp terminal; wires terminate independently per pin (no per-CN cable grouping is required — see `history.md` 2026-05-08 for context).

Connectors are placed in a "chip-pinout" layout to minimize jumper-wire length to the ESP32 module:

  - CN1–CN5 sit on the **right** side of the PCB, **bottom→top** (CN1 closest to USB, CN5 closest to the top edge). They map onto ESP32 pins 1–22 (right edge, RIGHT_HEADER).
  - CN6–CN10 sit on the **left** side, **top→bottom** (CN6 closest to the top edge, CN10 closest to USB). They map onto ESP32 pins 23–44 (left edge, LEFT_HEADER).

Pin numbering within each CN (verified against `kart-medulla.kicad_pcb`, 2026-07-10 — this
used to read "pin 1/2/3 from top to bottom", which is only true of the right-hand side):

  - **CN1–CN5** (right, footprint rotation −90°): pin **1 at top**, pin 3 at bottom.
  - **CN6–CN10** (left, footprint rotation +90°): pin **1 at bottom**, pin 3 at top.

Note the consequence: on the right the CNs advance bottom→top while their pins advance
top→bottom; on the left the CNs advance top→bottom while their pins advance bottom→top. So on
**both** sides the pin numbering runs *counter* to the CN numbering, and on both sides the wire
entry faces **inward**, toward the middle of the board. See the "flip the connectors" task in
`../tasks.md`.

Footprint is `CONN-TH_3P-P2.50-S5.00_1990012`: 2.50 mm pitch, and the pads are **staggered** —
pins 1 and 3 in one row, pin 2 in a row 5.00 mm across. A 180° rotation therefore moves pin 2's
pad row to the opposite side and is not a free change; the copper under each connector must be
re-routed.

## Silkscreen is the authority (v1, the only board that exists)

The table below is transcribed from the **v1 PCB silkscreen** — v1 is the only revision built, so
this is what is physically in front of you:

```
CN1        CN2        CN3        CN4       CN5        CN6        CN7        CN8         CN9          CN10
1 +3V3     1 HALL3    1 EXP_P1   1 SCL     1 HYD2     1 PED_BRK  1 PRES1    1 SDC       1 STEER_PWM  1 CMD_ACC
2 +12V     2 HALL2    2 EXP_P2   2 SDA     2 PRES3    2 PED_ACC  2 PRES2    2 BUZZ      2 HYD1       2 CMD_BRK
3 GND      3 +5V      3 EXP_P3   3 REV     3 EXP_P4   3 +3V3     3 HALL1    3 STEER_DIR 3 GND        3 GND
```

**Two naming traps, both of which have already caused confusion:**

1. **`BUZZ` on CN8.2 is an OLD name.** There is no buzzer on it. The net was repurposed to
   `CMD_COMPRESSOR_PWM` — GPIO 3 driving the EBS compressor MOSFET gate. Wherever `BUZZER` appears
   in this repo it should be read as *(old name)*. Note this collides with the rules-mandated ASSI
   buzzer, which still needs a home — see `projects/kart-medulla/tasks.md`.
2. **`EXP_P2` is CN3.2, and always has been.** A stale export of `projects/kart-medulla/output/netlist.net`
   (dated 7 May, re-exported 2026-08-10 and now current with the schematic) used to list
   `CN8.2 → /EXP_P2` and show Q3's and Q4's gates on no net at all — both artifacts of the schematic
   having moved on without a re-export. Re-exporting fixed both; the netlist now agrees with the
   silkscreen and this table. If a future edit makes them disagree again, trust the silkscreen and
   this table until the netlist is re-exported.
3. **Designator mismatch: schematic vs the fabricated v1 board.** An earlier draft of the schematic
   (before the netlist above was current) put the pressure channels on `CN2.1`/`CN2.2`/`CN2.3`. On
   the v1 silkscreen and PCB — the only board that physically exists — those pins are
   `CN7.1`/`CN7.2`/`CN5.2`, and PCB `CN2` is instead `HALL3`/`HALL2`/`+5V_REG` (see the assignment
   table below). **Anyone wiring the kart should read from the silkscreen/PCB, never from a
   schematic printout**, in case a future schematic edit drifts from the fabricated board again
   before a new revision is built.

## Assignment table

Each row is one independent terminal. `CN5.2` means connector CN5, pin 2.
The three pins in a connector do **not** imply a shared device or cable.
“Board label” is the text printed on the built board; the function describes its current use.

| Terminal | Board label | Signal and function |
|---|---|---|
| **CN1.1** | `+3V3` | `+3V3` — 3.3 V supply output from the ESP32 module. |
| **CN1.2** | `+12V` | `+12V` — 12 V supply input from the kart battery. |
| **CN1.3** | `GND` | `GND` — Ground return. |
| **CN2.1** | `HALL3` | `MOTOR_HALL_3` — Motor Hall sensor 3 input, 5 V. |
| **CN2.2** | `HALL2` | `MOTOR_HALL_2` — Motor Hall sensor 2 input, 5 V. |
| **CN2.3** | `+5V` | `+5V_REG` — 5 V rail for the motor Hall sensors. |
| **CN3.1** | `EXP_P1` | `EXP_P1` — PCF8574 expander pin P1. |
| **CN3.2** | `EXP_P2` | `EXP_P2` — PCF8574 expander pin P2. |
| **CN3.3** | `EXP_P3` | `EXP_P3` — PCF8574 expander pin P3. |
| **CN4.1** | `SCL` | `SCL` — I²C (Inter-Integrated Circuit) clock, 3.3 V. |
| **CN4.2** | `SDA` | `SDA` — I²C data, 3.3 V. |
| **CN4.3** | `REV` | `REVERSE_WIRE` — Reverse command from PCF8574 P0; open-drain output shared with the manual reverse button. |
| **CN5.1** | `HYD2` | `HYDRAULIC_2` — Hydraulic pressure sensor 2 input, 0–5 V. |
| **CN5.2** | `PRES3` | `CMD_STEER_PWM_IN` — MT6701 steering-angle input, pulse-width modulation (PWM). Repurposed pressure input; no pressure sensor here. |
| **CN5.3** | `EXP_P4` | `EXP_P4` — Spare PCF8574 expander pin P4. |
| **CN6.1** | `PED_BRK` | `PEDAL_BRAKE` — Brake pedal position input, 0–5 V. |
| **CN6.2** | `PED_ACC` | `PEDAL_ACC` — Accelerator pedal position input, 0–5 V. |
| **CN6.3** | `+3V3` | `+3V3` — 3.3 V supply output from the ESP32 module. |
| **CN7.1** | `PRES1` | `PRESSURE_1` — Pneumatic pressure sensor 1 input, 0–10 V through a divider. |
| **CN7.2** | `PRES2` | `PRESSURE_2` — Pneumatic pressure sensor 2 input, 0–10 V through a divider. |
| **CN7.3** | `HALL1` | `MOTOR_HALL_1` — Motor Hall sensor 1 input, 5 V. |
| **CN8.1** | `SDC` | `SDC_IN_LOW_SIDE` — Shutdown circuit (SDC) return, connected to Q3 drain. See voltage reference below. |
| **CN8.2** | `BUZZ` | `CMD_COMPRESSOR_PWM` — 3.3 V command to the external compressor transistor gate; not a buzzer or compressor power supply. |
| **CN8.3** | `STEER_DIR` | `CMD_STEER_DIR` — Cytron steering H-bridge direction output, 3.3 V. |
| **CN9.1** | `STEER_PWM` | `CMD_STEER_PWM` — Cytron steering H-bridge PWM output, 3.3 V. |
| **CN9.2** | `HYD1` | `HYDRAULIC_1` — Hydraulic pressure sensor 1 input, 0–5 V. |
| **CN9.3** | `GND` | `GND` — Ground return. |
| **CN10.1** | `CMD_ACC` | `CMD_ACC` — Throttle command to the motor controller, nominal 0–5 V. |
| **CN10.2** | `CMD_BRK` | `CMD_PRES` — Pressure setpoint for the Festo VPPM regulator, nominal 0–10 V. See output circuit notes below. |
| **CN10.3** | `GND` | `GND` — Ground return and reference for the VPPM setpoint; common with the 24 V supply’s 0 V. |

### Bus and sensor connections

CN4.1 and CN4.2 expose the bus shared with the on-board PCF8574 (U25). The
AS5600 connection used these bus lines; the MT6701 steering-angle PWM input is
CN5.2. CN4.3 is an independent reverse command.

CN5.2 is silkscreened `PRES3`, but its current use is steering-angle capture on
ESP32 GPIO 1. See “As-built pin use — board `84d6dd0`” in `pinout-esp32-s3.md`.
CN8.2 is silkscreened `BUZZ`, but GPIO 3 drives the gate resistor of the external
compressor MOSFET (metal-oxide-semiconductor field-effect transistor).

### Output circuit notes (CN10)

Pin 1 = throttle command, to the motor controller: MCP4922 VOUTA (0–3.3 V) goes through the LM358 U1B non-inverting stage (gain 1.51, set by R37 5.1K / R38 10K, giving 4.99 V full scale) straight to CN10.1. Nothing is muxed on this path — the MAX4660 (U14) that used to sit here has been deleted from the schematic; the panel DPDT switch on the kart, downstream of this board, is what selects whether the motor controller listens to this command or to the driver's pedal.

Pin 2 = **pressure command to the Festo VPPM proportional regulator, not to the motor controller** — braking on this kart is pneumatic. It is VOUTB amplified ×3 by the LM358 (U1A) (R19 = 2K, R20 = 1K), so 9.9 V leaves the board, not 10 V exactly, since the DAC's full scale is 3.3 V rather than 5 V — the MCP4922 U13 was moved from +5V to +3V3 on 2026-08-01 (commit 16a35fb) to fix an SPI logic-threshold problem. The net was called `CMD_BRAKE` until 2026-07-31; it is `CMD_PRES__0_10V` now, because the signal is a pressure setpoint for a proportional regulator rather than a brake-force command. The silkscreen on the built board still reads `CMD_BRK`.

Pin 3 = GND, and it is also the **return the VPPM's setpoint is measured against**: the valve runs from a separate 24 V supply, so that supply's 0 V must be common with the medulla's GND or the commanded pressure shifts by whatever the offset is.

## The pneumatic side — three devices, three supplies, only one of them on a medulla pin

Written 2026-07-31 because "the valve" was being used to mean different things. Sources:
`~/dv/kart/pneumatics/README.md` and `~/dv/kart/pneumatics/history.md` (2026-05-30).

| Device | Festo part | Its own supply | What the medulla does |
|---|---|---|---|
| **VPPM-8L proportional pressure regulator** | 571293 | **24 V DC** (21.6–26.4 V, 300 mA, 7 W) from a UENPO 9–36 V → 24 V buck-boost | Drives its **0–10 V setpoint** out of **CN10.2** (`CMD_PRES__0_10V`). GND on **CN10.3** is the return that setpoint is measured against. The medulla does **not** supply its 24 V. |
| **EBS emergency electrovalve** (and the ASB valve) | 8035174 / 8035167, VUVS-LT25 | **12 V** coils, switched by the **shutdown relay** | Nothing. No medulla pin touches it. |
| **SDE5 pressure sensors** | 567465 | 15–30 V, fed from the same 24 V rail | Reads their **0–10 V outputs** on `PRESSURE_1`/`PRESSURE_2` (CN7.1, CN7.2) through dividers |

The setpoint and the supply are different things on the VPPM: 0–10 V is the command, 24 V is what
powers the valve. When a note here says a 24 V fault could reach a medulla pin, it means the VPPM's
supply appearing on CN10.2 through a harness fault — not the EBS valve, which is 12 V and not wired
to this board at all.

The VPPM setpoint is a signal input and the LM358 drives it directly; its input impedance was
treated as an open question until 2026-07-31 and is not one.
## Voltage levels — quick reference

| Suffix in signal name | Meaning |
|---|---|
| `__3V3` | 3.3 V logic level (ESP32 native) |
| `__5V` | 5 V logic level (motor hall, level-shifted by U5 to 3V3 before reaching the ESP32) |
| `__0_5V` | analog 0–5 V (sensors, DAC outputs) |
| `__0_10V` | analog 0–10 V (pressure sensors) |
| no suffix on power names (`+12V`, `+3V3`, `+5V_REG`) | rail of that nominal voltage |

`SDC_IN_LOW_SIDE` is the drain of Q3 (IRLZ44N): nominally 0 V when Q3 conducts (no emergency), floats up to whatever the upstream SDC node sits at (≤ 12 V) when Q3 is off (emergency). Treat it as a 12-V-tolerant line.

## Power architecture summary (where each rail comes from)

  - `+12V`         — externally, from the kart battery, via **CN1 pin 2**.
  - `+5V_REG`      — on-board L7805CDT linear regulator (U19), or the external XW-1224 5 V rail tied in via the same net, feeds the `+5V_REG` global net.
  - `+3V3`         — generated by the ESP32-S3 module's on-board LDO from its 5 V input. Available on LEFT_HEADER pins 23/24 of the dev module.
  - `+5V_USB`      — independent 5 V rail from the medulla USB-C connector; powers only the ESP32 dev module (split-rail design, see `pinout-esp32-s3.md`).

The single `power:+12V` symbol that asserts the `+12V` rail name is placed at CN1 pin 2 (the entry point). Same convention applies to `+3V3` and `+5V_REG` symbols on whichever CN exports them — the symbol just declares the rail and can sit anywhere on the net.

## Cross-reference

  - ESP32 module pinout → `pinout-esp32-s3.md` (which GPIO drives which signal in the table above).
  - PCB physical layout / silkscreen → the `kart-medulla.kicad_pcb` file in this folder. The silkscreen legend that lists the 21 numbered external signals is being updated to match this assignment.
  - Decision history → `../../../history.md` entry `2026-05-08 — kart-medulla CN1–CN10 pin assignments locked to ESP32 geometry`.
