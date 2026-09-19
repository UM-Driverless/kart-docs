<!-- consult selectively — grep, never read in full -->

# History

Append-only log of notable decisions and events for `kart-docs`. Chronological (oldest first), append at the end.

---

## 2026-04-13 — Kart Medulla MCU: classic ESP32 → ESP32-S3 (docs reframed)

**Decision.** The next revision of the Kart Medulla interface PCB targets the **ESP32-S3** (ESP32-S3-WROOM-1 module). The classic ESP32 (ESP32-WROOM-32 on a DevKitC V4) is retired as the target MCU for new hardware.

**Status at decision time.** No Kart Medulla PCB has been manufactured. The classic ESP32 is currently hand-wired directly in the kart for basic functionality — this continues to be the operational setup until the S3 PCB is built and flashed.

**Why.**

- **Pin count.** The classic ESP32 ran out of usable GPIOs once CAN, SPI, status RGB, buzzer, and the Orin link were added on top of 3× halls, 3× pressure, accelerator, brake, SDC, steering, and relay. Too many classic-ESP32 GPIOs are reserved for flash/SDIO or are strap-pin traps. The S3 offers ~45 usable GPIOs.
- **Native USB-OTG.** Orin link moves from UART (through an external USB-UART bridge chip) to direct USB CDC-ACM — drops a BOM item, raises throughput from ~1 Mbit/s to ~12 Mbit/s full-speed USB, and gives hot-plug handling for free.
- **Built-in USB-Serial-JTAG.** Flash + serial monitor + step-debugging over one USB cable. No external ESP-Prog / FT2232H.

**Trade-off accepted.** The S3 has no built-in DAC, so `CMD_ACC` (5V analog throttle output) now comes from an external **MCP4728** (quad 12-bit I²C DAC) on the interface PCB. 12-bit vs the classic's 8-bit is a resolution upgrade. MCP4728 shares the existing I²C bus, so no additional GPIO cost.

**Variants considered and rejected.** ESP32-S2 (has DAC but single-core, no BT), ESP32-C3 (too few GPIOs), ESP32-C6 (no DAC, Wi-Fi 6 unnecessary for a kart), ESP32-H2 (no Wi-Fi).

**Docs reframe performed today.**

- `docs/assembly/electronics/kart-medulla/index.md` — rewritten around ESP32-S3 (new pinout table, hardware decisions, Why-S3 rationale).
- `docs/assembly/electronics/kart-medulla/legacy-wiring.md` — new page preserving the classic ESP32 hand-wiring as currently deployed in the kart. **Temporary** — to be removed once the S3 PCB is deployed.
- `mkdocs.yml` — nav renamed "Kart Medulla (ESP32)" → "Kart Medulla (ESP32-S3)" with the legacy page nested under it.
- `docs/assembly/electronics/bom.yaml` — added `esp32_s3` entry (status `planned`); `esp32_wroom_32` demoted to `status: legacy` with a pointer to the legacy wiring page.
- `docs/bom/index.md` — now lists both MCUs.
- `docs/assembly/electronics/orin-setup.md` — PlatformIO flashing snippet now shows both environments (`esp32dev` for the legacy setup, `esp32-s3-devkitc-1` for when firmware migrates).

**Pointers to deeper context.**

- PCB project + `.epro` backups + full decision log: Drive folder `formula_24-25-26/dv/kart/kart-medulla/` — especially `README.md`, `history.md`, and `pinout-esp32-s3.txt` (which keeps both classic and S3 pinouts side-by-side as a reference).
- EasyEDA project: account `dv.umotorsport@gmail.com`, Personal Workspace, project ID `5b30b0a2e25c44179a5af8629b1dff0d`.

**Follow-ups.**

- Firmware (`kart-medulla` repo) needs to gain a working `esp32-s3-devkitc-1` PlatformIO/IDF configuration. `sdkconfig.esp32-s3-devkitc-1` is already present; pinout in firmware will need updating to match the S3 assignments once they're finalized during PCB layout.
- Delete `legacy-wiring.md` once the S3 PCB is manufactured, flashed, and deployed in the kart.

---

## 2026-04-23 — ESP32-S3-WROOM-1 suffix locked: N8R2 (R8 banned)

**Decision.** The exact module to order is **ESP32-S3-WROOM-1-N8R2** (8 MB flash, 2 MB quad PSRAM). Any octal-PSRAM variant (R8) is **banned** for the Kart Medulla.

**N8 vs N16 (flash).** The `N` suffix is on-module QSPI NOR flash. Flash size does not affect pinout — it all lives on the internal QSPI bus. N8 (8 MB) is plenty for this firmware (code < 1 MB, room for dual OTA slots + filesystem + growth). N16 (16 MB) is a silent upgrade path if ever needed.

**R2 vs R8 (PSRAM) — this is the critical one, and it is PHYSICAL, not firmware-configurable.**

- **R2 = 2 MB quad PSRAM.** Shares the existing QSPI flash data lines inside the module. Costs zero additional module pins. All GPIOs remain available.
- **R8 = 8 MB octal PSRAM.** The octal PSRAM die is hard-wired inside the module package to **GPIO 33–37** (the SPI0/1 extension pins). Espressif's ESP32-S3-WROOM-1 datasheet explicitly marks GPIO 33–37 as **not available** on R8 variants. Those module pads exist on the footprint but are permanently tied to PSRAM data lines inside the package.

**Why you cannot "just ignore PSRAM" on an R8 module.** Disabling PSRAM in `sdkconfig` does NOT reclaim GPIO 33–37. The PSRAM die is physically attached to the traces inside the module regardless of firmware. Driving those pads externally risks contention with whatever the PSRAM does at power-up (the ROM bootloader probes PSRAM). Treating an R8 board as if it were an R2 board is a hardware-level error, not a firmware choice.

**Rule (crystal clear).** For the Kart Medulla, only quad-PSRAM WROOM-1 variants (R2, or no PSRAM) are acceptable. R8 is rejected. This applies to the ordered module AND to any dev-board purchase — an ESP32-S3-DevKitC-1 with an N16R8 module soldered on is not a drop-in substitute for the N8R2 variant.

**GPIO 33–37 policy.** Our pinout does NOT treat GPIO 33–37 as reserved. We will try to leave them free where it is convenient, but that is a courtesy, not a commitment, and it is NOT the standard we follow. The module must make those pins available — i.e., the module must never be R8. If a future revision ever wanted to move to R8, the pinout would first have to be audited to confirm GPIO 33–37 are genuinely unused, and that audit has NOT been performed and is NOT planned.

**Alternatives on file.**

- **ESP32-S3-WROOM-1-N16R2** — valid upgrade path if firmware ever outgrows 8 MB flash. Quad PSRAM, zero GPIO cost, no PCB/pinout change required. This is the proper "fallback with headroom," replacing the previous mention of N16R8.
- **ESP32-S3-WROOM-1-N16R8** — **DISCARDED.** See above.

**Action.** Buy ESP32-S3-WROOM-1-N8R2. `bom.yaml`, `kart-medulla/index.md`, and `docs/bom/index.md` updated accordingly.

---

## 2026-04-27 — Public BOM page + steering power budget; Festo prices redacted under V2 sponsorship

**What was done.**

- New `docs/bom/full.md`: shareable consolidated BOM with two cost columns (team cost vs market cost), `Source` column (Donated / Sponsored / Purchased / Salvage / Custom), per-section tables (chassis, powertrain, steering, electronics compute & control, electronics power, sensors, EBS, wiring & misc), totals, and a tooling section sized for a "what would a new team need" view.
- New `docs/assembly/steering/power-budget.md`: back-of-envelope steering torque/power calc (μ·N·a → ~15–20 Nm static at the steering shaft, ≥100 rpm for 0.3 s lock-to-lock, ~50 W cont / ~200 W peak operating; ~2 kW stall headroom available with the current setup, rarely if ever hit). Includes a "current setup (kept)" section and an "interesting alternatives (not currently planned)" table covering Bosch F006-B20 generic wiper, Bosch WDD2 motorsport actuator, Doga 319H with Hall feedback, Doga 319.4860, generic 24V planetary gearmotor.
- `mkdocs.yml`: BOM nav split into two pages (overview + full); steering nav adds Power Budget.

**Festo / EBS pricing — what changed and why.**

The first draft of `bom/full.md` carried catalogue ballpark prices for the Festo-supplied EBS components. After re-reading the **V2 sponsorship contract** (`marketing/sponsors/festo/convenio-festo-umotorsport-2026-v2-rev-busquets-18-03-26.docx`, Busquets review 2026-03-18), the per-line Festo prices were **stripped from the public page** and replaced with `redacted` markers. V2 added:

- **NOVENA — Confidentiality.** All information accessed in the course of the agreement, 5 years post-termination, breach is "incumplimiento grave."
- **OCTAVA — IP/trademark.** Limited, revocable license to use Festo brand under their guidelines; 7-day brand removal post-termination.
- **DÉCIMA — Liability.** Festo disclaims liability; team indemnifies Festo against third-party claims.
- **UNDÉCIMA — Jurisdiction:** Barcelona (was Madrid in V1).
- **EXPONEN III** clarified the relationship as "patrocinio publicitario mediante aportaciones no dinerarias y acciones de visibilidad."
- **SEGUNDA** new bullet: supply subject to availability; no obligation of continuous/exclusive supply.

Cap on Festo's seasonal supply is **€1 500 incl. VAT per season** (Cláusula SEGUNDA-1). The team's reciprocal obligations (Cláusula TERCERA): logo on the kart, IG/LinkedIn tagging, Formula Student event invitations, sponsor listing on the team website. Term to 2026-12-31.

V2 was returned by Festo on 2026-03-18 and was being sealed by Cristina (URJC marketing). Per Jorge's chat, as of late April the signed version had not been finalised, but the redaction posture is the same either way.

**Price-research ledger kept in Drive.** Public-distributor price research (15 of 18 items priced from IAS Components, esd.equipment, Direct Pneumatics, Motion World; 3 still `?`) is preserved at `formula/formula_24-25-26/dv/kart/pneumatics/festo-public-distributor-prices-2026-04.md`. If Festo later confirms in writing that retail-equivalent estimates are publishable, the numbers can be moved straight back into the public BOM without re-research.

**Other notable BOM facts captured.**

- Orin: Silicon Highway 2023-04 invoice — net €1 821.29 + €36 shipping = **€1 857.29 transferred**, intra-EU reverse charge (0 % VAT on invoice). True project cost ~€2 247 once URJC self-accounts the 21 % reverse-charge VAT (URJC has limited input-VAT deduction as a public university). Footnote on the row explains.
- Steering: salvaged 24 V geared DC motor from a discarded massage chair, run at 12 V, through a **15 : 1** 3D-printed planetary; AS5600 angle sensor on the shaft. Bench-measured ~2 kW stall capacity; normal operation 50–200 W. Off-the-shelf wiper motors don't replace it without an equivalent reduction stage and procurement is the limiting factor for the team.
- Battery cells: 60× Molicel P42A bought from NKON for €230 (€3.83/cell), 52 in the 13S4P pack → €198. No 12 V auxiliary battery — 12 V rail comes from a buck regulator off the 48 V pack. Pack assembled by team; nickel strip + Kapton + 3D-printed PETG enclosure + fire-retardant foam liner.
- Orin storage: 500 GB M.2 NVMe pulled from a personal laptop during a 2 TB upgrade. €0 to project. Big improvement on `apt`/builds/repos; no effect on autonomy runtime FPS.

**Team-cost result.** ~€3 095 transferred to suppliers, ~€3 485 including the ~€390 reverse-charge VAT on the Orin. Page-level *market* total is redacted (the EBS row pulls the sum into non-disclosable territory); a non-Festo retail subtotal of ~€4 815 incl. VAT is shown as a partial reference.

**Open follow-ups (not closed in this session).** Sponsors page on the public site to satisfy Cláusula TERCERA-4; pneumatic schematic on the EBS page; rechecking the BOM once V2 is signed and we have the green/red on what's publishable.

---

## 2026-05-04 — drawio vs hand-crafted SVG for the wiring diagram

After thrashing through five attempts at `wiring-global` (drawio auto-routed,
hand SVG, drawio + manual waypoints, D2/ELK, drawio + electrical stencils),
the team's preference was clear: real component photos and pixel-precise
layout matter more than tool ergonomics. The fifth iteration on `wip/wiring-svg-rich`
went with hand-crafted SVG and produced a usable result on the first pass.
Notes from that experience for the next person:

**drawio strengths.** CI export is wired up (`rlespinasse/drawio-export`).
GUI editing exists for someone who prefers drag-drop. Built-in electrical
stencil library has shapes for battery, motor, switches, op-amp, relay
(actual stencil names live in `mxgraph.electrical.miscellaneous.*`,
`mxgraph.electrical.electro-mechanical.*`, etc. — extract them with
`strings /Applications/draw.io.app/Contents/Resources/app.asar | grep mxgraph.electrical`
because the names are not all guessable; the wrong path renders as a fallback
rectangle silently).

**drawio weaknesses (encountered, not theoretical).**
- Auto-routing produces spaghetti the moment edges have non-trivial geometry.
- `verticalLabelPosition=bottom` on a stencil makes the label overflow the
  cell's geometry box, so neighbors that were at the original spacing now
  collide with the label of the cell above them. The fix is either to
  re-space everything (cascading shifts because the relay block has
  internal sub-elements) or to use horizontal label position (which then
  fights with the cell width). Both routes burned an iteration.
- Photo embeds via `shape=image;image=<path>` work in CI but the path
  resolution is fiddly — relative paths to images outside the diagram's
  directory frequently render as broken-image placeholders in the CLI
  export. Data URIs work but blow up the file size.
- Edges connect by source/target cell IDs, so when you reposition a
  component the edges follow — but their waypoints don't, so the
  routing degrades silently.

**hand-crafted SVG strengths (encountered).**
- Pixel-precise placement: `<rect x= y= width= height=>` and `<polyline
  points="...">` go where you tell them. No layout engine to fight.
- `<image href="../../../emergency-braking/images/components/festo-*.png">`
  resolves correctly in any browser-based renderer (Chrome headless,
  the deployed mkdocs site, the `<object>` tag in the markdown).
  ImageMagick can't resolve those, but you don't need ImageMagick if you
  render with Chrome headless.
- Component icons drawn as inline `<path>` / `<circle>` / `<rect>` are
  free — the 13-cell battery stack, the BLDC motor rotor with U/V/W
  terminals, the SDC relay coil + NO contacts, the kill mushrooms, etc.
  Took maybe 30 minutes of careful coordinate math, no library lookup.
- White-halo edge labels (`paint-order: stroke fill; stroke: white;
  stroke-width: 4px`) just work, no fighting drawio's label background.

**hand-crafted SVG weaknesses.**
- No GUI for non-coders. The team can edit but only via text.
- Moving one component does NOT auto-reroute its edges; you have to
  update the polyline points manually. For 30+ edges this is real work.
- Verifying overlaps requires render-and-look (Chrome headless screenshot
  + Read tool); there's no equivalent of drawio's "click and drag, watch
  it snap to a clean route".

**Rendering pipeline gotcha.** ImageMagick's SVG renderer (and `qlmanage`)
do NOT load `<image>` tags via relative file paths. Render previews with:
```
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --headless \
  --disable-gpu --screenshot=/tmp/r.png --window-size=2400,1800 \
  --hide-scrollbars --force-device-scale-factor=2 \
  "file://$PWD/docs/assembly/electronics/wiring/images/wiring-global.svg"
```
The deployed mkdocs site uses real browser SVG rendering, so what you see
in Chrome locally matches what the team will see on `um-driverless.github.io`.

**Branches left for comparison (none merged to main).**
- `wip/wiring-d2-rewrite` — D2 + ELK auto-layout. Cleanest edges of any
  attempt, but every component is a generic colored rectangle.
- `wip/wiring-drawio-rich` — drawio with electrical stencils for battery,
  motor, kill switches, KEY, impact, op-amp. Acronym legend added,
  Buck/brake-bullet text corrected. Has the label-overflow / overlap
  problems that pushed us off drawio.
- `wip/wiring-svg-rich` — the hand-crafted SVG. Real Festo photos,
  schematic-style component icons, pixel-precise layout. Current
  best candidate but not yet team-reviewed.

**Bottom line.** For a documentation-grade wiring diagram with hardware-
recognizable shapes that the team isn't going to drag around in a GUI
every week, hand-crafted SVG produced a better result faster than the
drawio iterations did. drawio remains the right call for diagrams the
team WILL drag around (because the GUI saves time over coordinate math),
but those diagrams should accept the visual constraint of "labeled
rectangles with auto-routed edges" rather than fighting for stencils
and embedded photos.

---

## 2026-06-14 — BOM stays YAML-in-git, kept separate from the Notion AI Inventory (linked, not merged)

**Decision.** The published BOM stays as the `bom.yaml`-in-git system that `generate_bom_hook.py` renders into the searchable parts table. It is not folded into the team's Notion "AI Inventory" database, and it is not replaced by a public filtered view of that database.

**Context.** The Notion AI Inventory is the team's most-used tool — it tracks physical stock (tools, bolts, components) by quantity and location. It overlaps the kart, so the question came up: merge the BOM into it (a `location: kart` value), or publish a filtered Notion view as the BOM, or leave the BOM as-is.

**Why separate-but-linked is the answer.** A BOM and an inventory answer different questions and are *different sets*, not the same set filtered:

- Inventory = "what physical stock do we own, how much, where is it now" — instance/quantity-level, location-tracked.
- BOM = "what does the kart design call for" — type-level spec, by assembly, with required quantities.
- The BOM has rows with **no inventory entry**: assemblies/sub-assemblies, custom-fabricated parts (Orin adapter, Kart Medulla PCB), and design-required quantities that are a spec rather than physical stock. The inventory has rows with **no BOM line**: tools, consumables, spares. The overlap is only the COTS purchased parts.

So a "filtered inventory view" can only ever be that purchased-parts subset dressed as the whole BOM. Two pain points the user raised are the same modelling error from opposite sides: "2 bolts in the kart, the rest on a shelf — how to display" is only ugly if you model physical *units* as rows (you want one part row with quantity-by-location, not 50 rows); "two formats are hard to copy-paste on transfer" only exists if the item lives in two places.

**Publish-surface reasons to keep the docs table:** it sits inside MkDocs in-site search, it feeds `llms.txt`/`llms-full.txt` for AI ingestion, it's themed, it works offline, and it carries no dependency on a Notion page staying public. An embedded public-Notion view loses all of those.

**Link mechanism instead of merge.** Give each inventory item an optional shared part ID (`bom_id`) and each BOM part the catalog ID, so inventory↔BOM cross-reference rather than getting copy-pasted. If freshness on the overlapping purchased rows ever becomes a real problem, add a one-way Notion→`bom.yaml` pull for just those IDs — never two-way sync.

**Tipping condition that would flip this.** If the published BOM ever becomes just "the list of components we bought" — purchased COTS only, no assembly hierarchy, no custom parts, and no `llms.txt` need — then the BOM *is* the purchased-parts subset of inventory and a public filtered Notion view becomes the lower-effort, always-fresh choice.

**State found today (drives the follow-up work).**

- **Data is stale.** 6 of 8 `bom.yaml` files untouched since 2025-09 (only `electronics` 2026-05, `steering` 2025-11). Placeholder/unverified data present: `powertrain/bom.yaml` motor lists Amazon ASIN `B0C6WXYZ` (fake) as `verified: true`; several `TBD`/`pending` part numbers and round-number costs.
- **Render looks bad.** `generate_bom_hook.py` emits hand-rolled inline-styled HTML (hardcoded `background:#f5f5f5`, white-text status badges, fixed colors). It bypasses the Material theme, so there is no dark-mode support and it clashes with the rest of the site.

**Follow-up (not yet done).** (1) Audit each `bom.yaml` against the real kart and `~/dv/kart/<subsystem>/` notes — fix fake/placeholder part numbers, costs, and status flags. (2) Rework the hook's output to use Material-friendly, theme-aware markup (dark-mode safe) instead of inline styles.

**Update (same day): the styling rework (2) is done.** `docs/stylesheets/bom.css` (new) holds all table styling on Material CSS custom properties (theme-primary header, soft status/criticality badges, dark-mode ready); `generate_bom_hook.py` now emits class-based markup with no inline styles and the filter/sort JS was tidied; `mkdocs.yml` wires `extra_css`. Verified by building + screenshotting. The data audit (1) is still open.

## 2026-06-14 — QR scan resolves to the BOM (kart-docs), not the Notion inventory

**Decision.** The part-label QR system (`/scan/` → `/p/<id>/`) is for **kart parts**, and a scan resolves to that part's **BOM component / engineering docs in kart-docs**, not to the Notion AI Inventory. An inventory link stays optional/secondary on the `/p/` page.

**Why.** The motivating use case is disambiguating **versions that look physically identical** (e.g. Orin adapter v1 vs v2, ESP32-WROOM-32 *legacy* vs ESP32-S3). A QR carries a per-physical-unit opaque ID, so look-alike units get different IDs → different `/p/<id>/` pages → each links to *its* BOM component, which already encodes the revision (`status`, per-version description). The Notion inventory counts stock by *type* and can't say which revision is the one mounted, so it's the wrong primary target here.

**Permanence rule preserved.** The QR holds only the opaque ID; resolution is relative through kart-docs `/p/<id>/`. Labels never encode a Notion URL (long, org-bound → perishable sticker).

**Requirement this imposes.** For disambiguation to actually work, BOM component IDs must separate versions (`orin_adapter_v1` / `orin_adapter_v2`), not collapse to a generic `orin_adapter`.

**Obsolete versions.** Mark the superseded BOM component `status: legacy` (renders as the grey "Legacy" badge) rather than deleting it — keeps the row visible-but-retired and lets an old sticker still resolve. Delete a `/p/<id>/` page only when the physical part *and* its sticker are gone; otherwise a scan would 404. Where a unit is retired in place, point its `/p/` page at the superseding component.

---

## 2026-07-16 — tasks.md consolidated to the repo root; `.agents/tasks.md` retired

`.agents/tasks.md` was moved to `tasks.md` at the repo root with `git mv`, so the file's history follows it. `.agents/tasks.md` no longer exists in this repo and must not be recreated — the rule is one `tasks.md` per repo, at the root.

**Rationale:** tasks are the project's tasks regardless of who does them. Two files named `tasks.md` only produce duplicates and stale entries, because whichever one the current session isn't reading quietly goes out of date.

`AGENTS.md` previously didn't mention the task board at all; its "Key Files (Read Before Working)" list now names `tasks.md` first, ahead of `.agents/error-log.md` and `.agents/definition-of-done.md`.

Note: `docs/assembly/pneumatic-braking/index.md` points at `dv/tasks.md`, which is a *different* repo's board, not this one — it was already correct and was left alone. Stale `.agents/tasks.md` paths in append-only records (`history.md`, `.agents/error-log.md`) were also deliberately left as written: they were accurate on the date they were logged, and rewriting them would falsify the record.

---

## 2026-07-30 — `legacy-wiring.md` deleted: the ESP32-S3 Medulla PCB is the board in the kart

The classic-ESP32 page has been deleted, executing the plan recorded in the 2026-04-13 entry
above ("Delete `legacy-wiring.md` once the S3 PCB is manufactured, flashed, and deployed in
the kart"). Confirmed by Rubén: the ESP32-S3 interface PCB is installed and the hand-wired
classic ESP32 (ESP32-DevKitC V4, flying wires, no PCB) is out of the kart.

**Trigger.** Searching the live site for "esp32" returned "Legacy wiring (classic ESP32)" as
the *first* of 24 results, above every current page — so the top hit for the project's main
microcontroller was a retired pinout. The page carried a prominent "temporary page" warning
and was correctly nested in the nav, and that still wasn't enough: search surfaces pages
context-free, so a page that is only correct when read with its banner will be read wrong.
The lesson is that a legacy page's cost is paid at search time, not at nav time — retire it
on the day it stops being true rather than leaving it to be sorted out later.

**Removed.** `docs/assembly/electronics/kart-medulla/legacy-wiring.md` plus the five
classic-ESP32 images it was the only referent of (`esp32-devkitc-v4-pinout.png`,
`esp32-devkitc-v4-typec-header-pinout.png`, `ESP32-DevKitC-Dimensions.png`, and two that were
already orphaned: `ESP32-DOIT-DEV-KIT-v1-pinout-mischianti.png`, `ESP32-pinout-diagram.jpg`).
The nav entry under Kart Medulla is gone. The ESP32-S3 pinout on
`kart-medulla/index.md` was already complete and correct; nothing was migrated.

**Docs that still claimed the classic board was installed, now corrected.** The repo had been
inconsistent for a while — `wiring.md` and `kart-medulla/index.md` described the fabricated S3
board with its `CNx.y` terminals and physical board-rework steps, while `legacy-wiring.md`,
`bom.yaml`, and both BOM pages said the classic ESP32 was the operational setup:

- `bom.yaml` — `esp32_s3` `status: planned` → `active`; `esp32_wroom_32` description and notes
  rewritten as retired. Its `pin_assignments:` block was deleted — it held a *third*
  classic pinout that disagreed with the legacy page itself (it claimed GPIO 18/19 for the
  Orin UART and GPIO 25/26 for the motor driver) and no script read it.
- `esp32_wroom_32` keeps `status: legacy` rather than being deleted, per the 2026-06-14 QR
  convention: the row must stay resolvable so stickers on the physical modules don't 404.
- `docs/bom/index.md`, `docs/bom/full.md` — "currently hand-wired in the kart" → retired.
- `orin-setup.md` — the `esp32dev` flashing command is unchanged (it is still the image that
  gets flashed), but its comment no longer describes it as "the legacy hand-wired classic
  ESP32 currently in the kart", which is now false about the hardware.

**Stale DAC part name fixed in passing.** `docs/bom/full.md` still listed a planned "MCP4728
quad 12-bit I²C DAC", and `bom.yaml`'s `esp32_s3` entry referenced the MCP4728 twice. The
design switched to the **MCP4922** (dual 12-bit SPI) on 2026-04-17. The MCP4922 still has no
component entry of its own in `bom.yaml` — filed in `tasks.md`.

Verified with `mkdocs build --strict`: no broken links, and "Legacy wiring" no longer appears
in `site/search/search_index.json`.

---

## 2026-07-30 — Settled: the kart runs the `esp32-s3-devkitc-1` build, not `esp32dev`

The earlier entry today left an open contradiction: `firmware.md` said the board is an
ESP32-S3 while also calling the classic `esp32dev` environment "the image that actually runs
on the kart", and the `orin-setup.md` edit in that same commit repeated the claim. Both were
wrong. A classic-ESP32 image cannot run on an S3 at all — Xtensa LX6 vs LX7, and esptool
rejects the chip-ID mismatch — so this was never a question of which was more current, only
of which one was false.

**Checked directly on the kart's Orin over `orin-remote` (read-only, nothing stopped or
flashed):**

- `~/kart_medulla/.pio/build/` contains exactly one environment, `esp32-s3-devkitc-1`, with a
  `firmware.bin` from 2026-07-30 11:08. There is no `esp32dev` build directory at all.
- The ESP32 is on `/dev/ttyACM0`; no `/dev/ttyUSB*` exists on the machine. The classic board's
  CP2102 enumerated as `ttyUSB0`, so its absence is itself evidence.
- `lsusb` shows `1a86:55d3 QinHeng Electronics USB Single Serial` — the WCH CH343 on the S3
  board.

Corroborating, from session transcripts: two `pio run -e esp32-s3-devkitc-1 --target upload
--upload-port /dev/ttyACM0` runs over `ssh orin-remote` on 2026-07-26 both reported SUCCESS,
one of them immediately before a commit whose message quotes steering values "measured on the
kart". `platformio.ini` confirms `[env:esp32dev]` still has `board = esp32dev` — it was never
repointed at the S3; it is a fallback that is simply not used.

**Where the false claim came from.** `platformio.ini` still carries a comment above the S3 env
saying it "does NOT link yet", and `.agents/esp32s3-pinmap.md` still says "The S3 build does
not exist." Both were true when written and were never updated after the S3 target started
working. `firmware.md` faithfully copied them. The lesson is that a doc which cites its source
is only as fresh as that source — `firmware.md` even flagged "doc lag" in those two files
while trusting their substance.

**Fixed here:** `firmware.md` (warning block, env table, and flashing section rewritten around
the S3 target) and `orin-setup.md`. Two further errors surfaced while verifying the flashing
commands against the live machine: the repo path on the Orin is `~/kart_medulla` with an
underscore, not `~/kart-medulla`, and `pio` is **not** on the Orin's PATH (`which pio` returns
nothing) — it must be called as `~/.local/bin/pio`. The documented flash sequence would have
failed on both counts. It also now stops and restarts `kart-brain`, which holds the serial
port.

**Left open in `tasks.md`,** because they live in the `kart-medulla` repo: the three stale
statements above, and a real unresolved one — `AGENTS.md` says `km_gpio.h` uses the S3 pin map
while `.agents/esp32s3-pinmap.md` says it still holds the classic map. That one is
safety-relevant: under the classic map `PIN_STEER_PWM` is GPIO 18, which on the S3 board is
the gate of Q3, the shutdown-circuit MOSFET.

Also added the **MCP4922-E/SL** as its own `bom.yaml` component (it had none), with the
MCP4728 recorded under `rejected:`. Its unit cost is a placeholder — the chips came from
workshop stock and no price was paid.

---

## 2026-07-30 — Module standard changed: the fitted N16R8 is accepted, the "never R8" rule retired

The docs specified **ESP32-S3-WROOM-1-N8R2** and carried an explicit "DO NOT BUY" rule against
octal-PSRAM (R8) variants. The module actually on the board is an **N16R8** — an R8. So the
BOM banned the part it was describing, and the earlier edit today that flipped `esp32_s3` to
`status: active` made it worse by asserting the N8R2 was the installed part.

**Evidence the fitted module is R8:** `esptool` on the hardware reports `ESP32-S3 (QFN56)
revision v0.2` with `Embedded PSRAM 8MB (AP_3v3)` — 8 MB of PSRAM is octal, quad variants are
2 MB. Three independent statements in the firmware repo agree: `AGENTS.md` ("the kart-medulla
PCB now carries an ESP32-S3 (WROOM-1-N16R8)"), `.agents/error-log.md`, and
`.agents/esp32s3-pinmap.md` ("The fitted module is an **N16R8**").

**Decision (Rubén, 2026-07-30): accept the R8 and rewrite the rule.** The ban was written to
protect GPIO 33–37, but the pinout had already been changed to leave all five free — 33, 35,
36 and 37 are `HOLD`, `CMD_REVERSE` moved to the PCF8574 expander on 2026-05-03, and
`MOTOR_HALL_1` moved off GPIO 37 to GPIO 16. The thing the rule was protecting had already
been given up voluntarily, so the R8 costs this design nothing and the rule was the stale part.

The constraint that remains real, and is now stated that way: **GPIO 33–37 must never be
assigned.** Substituting a quad-PSRAM module (N16R2, N8R2) is a safe drop-in that *frees* those
pins; the failure case is the reverse — assigning 33–37 and then fitting an R8.

**Contradictions this cleared up, all pre-existing.** `index.md` had two adjacent admonitions
saying opposite things: a note headed "N8R2 preferred; N8R8 still works" immediately above a
danger block headed "octal-PSRAM variants (R8) are tolerated, never preferred" whose body then
said "**Do not substitute an R8 variant**" — tolerated and forbidden in the same breath. Both
are replaced by one block. `bom.yaml` separately claimed "**GPIO 33–37 are NOT reserved by our
pinout** ... the pinout may and does use GPIO 33–37 when needed", which the pin table on
`index.md` had contradicted since at least 2026-05-08 by marking all five `HOLD`. And
`index.md` still described `CMD_REVERSE` as living on GPIO 36 flagged `SPARE/CMD_REVERSE`,
two months after it moved to the PCF8574.

Also corrected while sweeping: `docs/bom/full.md` still listed the medulla PCB as "next
revision, blank" with its terminal blocks and level shifters as "Planned", though the board is
fabricated, populated, and running the kart; and `wiring.md` linked to the medulla page as
"Kart Medulla (ESP32)".

**Naming note for anyone reading old text:** "N8R8" appears in a few places in the pre-2026-07-30
docs where "N16R8" was meant. N8R8 is a real Espressif part (8 MB flash, 8 MB octal PSRAM), just
not the one on this board.

---

## 2026-07-30 — Pin table diffed against dv-hardware; U12 does not exist, the part is Q4

Following the module-suffix fix, the ESP32-S3 pin table was compared row-by-row against its
declared source of truth, `dv-hardware/projects/kart-medulla/docs/pinout-esp32-s3.md`. The
kart-docs table claimed to mirror it "as of 2026-05-08"; that file has since been edited twice
(2026-07-10 bench bring-up, 2026-07-18), so the claim was ~2.5 months stale.

**All 44 rows agree except two, and on those two kart-docs is the more current side.**
dv-hardware still lists GPIO 1 as `PRESSURE_3` and GPIO 3 as `BUZZER` in its `Signal` column
even though its own notes describe both reassignments. So the blanket "if the two disagree,
dv-hardware wins" rule would have *undone* the steering-angle-PWM and compressor-PWM
repurposings. The rule is now scoped: dv-hardware wins everywhere except those two rows, and
the underlying fix is filed in `tasks.md` as an upstream job.

**Corrections pulled down from the 2026-07-10 bench session:**

- **GPIO 3 is not a strap pin on this chip.** The old note said "Strap pin (JTAG src select),
  idle-high at boot is acceptable". Both halves were measured wrong: the `STRAP_JTAG_SEL` eFuse
  is unburned so GPIO 3 is never sampled at reset, and `IO_MUX_GPIO3 = 0x0a02` shows no
  internal pull, so it floats and an external pulldown wins at boot. That is precisely why it
  is safe driving the compressor MOSFET gate.
- **GPIO 35–37 are `BLOCKED`, not `HOLD`.** With an N16R8 fitted they are not reclaimable at
  all, so the status legend now separates "kept free by choice" from "physically impossible".

**U12 does not exist.** The docs described the REVERSE-wire driver as "U12, a PC357N1J000F
optocoupler, swapping to a BSS123 in the next schematic edit, board not yet manufactured, swap
is free". Every clause was wrong: the part is **Q4**, a BSS123, already fitted on a
manufactured and bench-tested board. The netlist's reference designators are
`U1, U02, U5, U13, U14, U19, U23, U24, U25` — no U12 anywhere in schematic, PCB, netlist or
BOM. The optocoupler was never placed on a sheet; it survives only as an unused library entry
in the EasyEDA source, and even the 2026-05-03 export already has the BSS123 placed as Q4.

**One conflict left open rather than guessed at.** kart-docs puts the reverse-command wire on
terminal **CN4.3**; the dv-hardware netlist puts `/REVERSE_WIRE` on **CN8 pin 1**, which
kart-docs assigns to `SDC_IN_LOW_SIDE`. Mixing up a reverse command with the shutdown-circuit
terminal is not a harmless error, and nothing on hand settles it — CN6–CN10 are already flagged
as possibly physically reversed. Both `index.md` and `wiring.yaml` now carry an explicit
"unverified" marker at that terminal, and it is filed in `tasks.md` for a check against the
board.

Verified after the edits: `check_wiring.py` still reports 115/115 connectable pins wired, and
`mkdocs build --strict` is clean.

---

## 2026-07-30 — CN4.3/CN8.1 settled: kart-docs was right, the dv-hardware netlist's CN numbers are not the silkscreen's

Confirmed by Rubén: on the board, **CN4.3 carries REVERSE and CN8.1 is `SDC_IN_LOW_SIDE`** —
exactly what `wiring.yaml` and `kart-medulla/index.md` already said. The "unverified" markers
added to both files earlier today have been removed.

The discrepancy that prompted them is real but lives upstream, and it is worse than a swapped
pair. `dv-hardware/projects/kart-medulla/output/netlist.net` (exported 2026-05-07) puts
`/REVERSE_WIRE` on **CN8 pin 1** *and* `/SDC_IN_LOW_SIDE` on **CN5**. Two nets, two different
mismatches — so the netlist's `CN` reference designators are simply not the silkscreen `CN`
numbers, rather than being off by a consistent permutation. The KiCad project is a ConvertEDA
import of the EasyEDA original, which is the likeliest point at which connector designators
were reassigned.

The consequence is worth stating plainly, because it is the kind of thing that gets someone
hurt: anyone wiring the kart from that netlist would land the **reverse command on the
shutdown-circuit terminal**. Filed in `tasks.md` — the netlist stays useful for nets and part
designators (it is how `Q4`/BSS123 was confirmed), but it is not authoritative for terminal
numbers until the designators are reconciled.

**Method note.** The mismatch surfaced only because the pin table was diffed against its
declared source of truth instead of being trusted, and it was resolved only by asking the one
person who could see the board. Neither half would have worked alone: the diff found the
conflict but had no way to say which side was right, and the netlist looked authoritative
precisely because it is machine-generated. Machine-generated does not mean correct about
physical labels — it means faithful to whatever the schematic's designators say, which is a
different claim.

---

## 2026-07-30 — `km_gpio.h` settled: both pin maps live behind a compile-time switch

The last open safety question is closed, and the alarming version of it was wrong.
`components/km_gpio/km_gpio.h` does not "hold the classic map" *or* "hold the S3 map" — it
holds **both**, selected by `#if defined(CONFIG_IDF_TARGET_ESP32S3)` with the classic map in
the `#else` branch. Building the `esp32-s3-devkitc-1` environment takes the S3 branch:

- `PIN_STEER_PWM` = GPIO 40
- `PIN_STEER_DIR` = GPIO 17
- `PIN_SDC_NOT_EMERGENCY` = GPIO 18
- `PIN_STEER_PWM_IN` = GPIO 1, commented `CN5.2 — MT6701 OUT, ~994 Hz PWM angle frame`

which matches the kart-docs pin table on every one of those pins, including the GPIO 1
repurposing that dv-hardware's own table has not caught up on.

So `AGENTS.md` was right and `.agents/esp32s3-pinmap.md` is stale. The hazard raised earlier
today — "under the classic map `PIN_STEER_PWM` is GPIO 18, which is Q3's gate" — is real about
the `#else` branch and irrelevant in practice, because that branch is not compiled for this
board. Worth recording as a false alarm rather than quietly dropping: the reasoning was sound
but rested on treating two docs' disagreement as evidence about the code, when the code was
readable the whole time and answered it in one grep.

Remaining stale statements in the firmware repo are consolidated into a single `tasks.md`
entry, now including `km_gpio.h:108`, whose `#else` branch is still labelled "(current build)".

---

## 2026-07-30 — Audited the docs nobody had opened: software, mechanical, rules, top-level

The electronics sweep earlier today only covered `docs/assembly/electronics/**` and
`docs/bom/**`. Three parallel audits covered the rest, and their claims were then checked
against two authorities rather than taken on trust: the `kart-brain` ROS 2 source, and the live
Orin.

**Two facts settled by looking at the running machine.** `/dev/serial/by-id/` on the Orin holds
exactly one entry, `usb-1a86_USB_Single_Serial_5C37207028-if00 → ttyACM0`, which matches the
`serial_port` default in `kb_coms_micro.cpp:6` — so the docs' Silicon Labs CP2102 path was
stale on both counts (wrong vendor, and the real default is a `by-id` path rather than a bare
device node). And `ss -tlnp` shows the dashboard process listening on **port 80**, confirming
`dashboard.md` and refuting the three pages that said 8080.

**The most consequential fix was a latency figure that inverted a conclusion.**
`performance.md` documented the ESP32 PID loop at 10 Hz / ~100 ms and drew the reasonable
conclusion that the microcontroller was the pipeline's largest tail after perception. The
firmware's actual control task targets 500 Hz (2 ms). `firmware.md` had already flagged 10 Hz
as a superseded number months ago; `performance.md` was the surviving copy. Fixing the number
also required rewriting the surrounding prose, the pipeline budget diagram, and a measurement
checklist item that asked whether "the 10 Hz PID cycle" was stable — a stale number does not
sit in one cell, it grows conclusions around itself.

**Corrections applied.** `/dev/ttyUSB0` → `/dev/ttyACM0`; CP2102 → the real WCH by-id path;
port 8080 → 80 in three places; `cmd_vel_bridge` documented as subscribing `/kart/cmd_vel`
when the source says `/kart/cmd_vel_muxed` (the wrong version implied the state-machine safety
mux was bypassed); `zed2i` → `zed2`; YOLOv11s at 640 px → YOLOv11n at 320; `/esp32/health` →
the real `/esp32/health/flags` + `/esp32/health/data`; `/esp32/throttle` marked as
simulator-only, since on hardware `kb_coms_micro` publishes `/esp32/acceleration` and that
dashboard dial stays blank; `ros2 launch kb_dashboard dashboard.launch.py` → `kart_bringup`
(both packages have a file by that name, and they are not equivalent); and
`state_machine.md`'s claim that the gamepad publishes `/kart/cmd_vel_manual` — it publishes
`/kart/cmd_vel`, the *autonomous* input, which is worth knowing before trusting the mux.

Outside software: `faq.md` argued the Orin's 40-pin header could replace the ESP32 because it
has "2 hardware PWM channels (steering servo + motor ESC)". There is no ESC and throttle is not
PWM — it is an analog DAC output — so the trade-off was mis-scoped, not merely mislabelled.
`index.md` was dated `2025-06-18`, ten months before the kart existed, and both it and
`about.md` still said steering actuation was "ordered" three weeks after the kart drove itself.
`assembly/index.md` described the MCU as "ESP32, UART 115200" and throttle as "0–3.3 V (66% max
until 5V DAC available)" — a limitation the fitted MCP4922 removed. The CAN diagram on
`steering/index.md` and the CAN transceiver line on `computer.md` both contradicted "no CAN
anywhere on the kart"; the transceiver is real but unused, so that line now says so.
`as_state_machine.md` described the dashboard stop button as equivalent to ASMS-off when it
returns to `AS_READY` and stays armed.

Also: `docs/rules/` was reachable only by an inline link and is now in the nav; the orphaned
`assembly/electronics/microcontroller/` directory (a Blue Pill page and two pinout images from
before the medulla existed, referenced by nothing) was deleted; and the build-journey's
"every Wednesday" claim was softened, since 5 of 13 posts landed on a Wednesday.

**Left open in `tasks.md`, four items that need a person or a multimeter:** what actually powers
the Cytron H-bridge (two pages say the 12 V rail, `steering/index.md` says the 48 V pack and
specs stall at 47 V × 43 A); rewriting the camera page's YOLOv5 export walkthrough for v11;
whether the kart is presented as a competition entry (`index.md` says it will not compete,
`as_state_machine.md` calls it an APC entry and tracks rule compliance); and reconciling three
different mission lists — during which the audit turned up a live bug worth repeating here:
`throttle_test` is gated as an autonomous mission but is missing from `protocol.py`'s
`MISSIONS` map, so `MISSIONS.get(..., 0)` sends it to the ESP32 as **manual**.

---

## 2026-07-30 — The Cytron runs off the 48 V pack; the 12 V claim was wrong in three files

Settled by Rubén: the steering H-bridge is fed from the **48 V traction pack**, not the 12 V
rail. So `steering/index.md` — the page flagged as the outlier when the audit found this — was
the correct one, and the two pages that agreed with each other were both wrong. Worth
remembering: two sources agreeing is not evidence, when one was written by copying the other.

Corrected `kart-medulla/index.md` (the 2026-05-01 decision entry) and
`electronics/power/battery.md` (which listed the H-bridge among the 12 V rail's loads). In
`wiring/wiring.yaml` the Cytron's supply pin moved from the `12V` net to `PACK48` and was
renamed `v12` → `vin` — the old pin name encoded the wrong answer, so leaving it would have
re-seeded the error — and `STEER_M+` / `STEER_M-` are re-labelled 48 V. `check_wiring.py` still
reports 115/115 pins wired.

The Cytron MD25HV takes 7–58 V, so the pack is within spec, which is why nothing downstream
needs to change. The "powered permanently, not switched through the manual/autonomous mode
switch" half of the original decision is unaffected: that was about inrush current browning out
the Orin on every switch into autonomous, which is a question of *when* it is connected, not of
*which rail*. Only the rail was wrong.

---

## 2026-07-31 — Part IDs are per-design, not per-physical-unit (amends 2026-06-14)

**Decision.** A part ID (`part_id`, the 16-digit number in the QR) identifies a **design revision**,
not an individual physical object. Every board built to the same revision carries the same sticker
and resolves to the same `/p/<id>/` page. Ruben's call, 2026-07-31.

**What this changes.** The 2026-06-14 entry above ("QR scan resolves to the BOM") wrote "a QR carries
a per-physical-unit opaque ID". That wording is superseded. Its *reasoning* is untouched and in fact
argues for per-design: the motivating case is telling apart versions that look physically identical
(Orin adapter v1 vs v2, ESP32-WROOM-32 vs ESP32-S3), and a per-design ID separates those completely.
Per-unit IDs would only add distinguishing two boards of the same revision from each other, which
nothing in the project needs, at the cost of a unique sticker and a unique page per object built.

Everything else in that entry stands: the QR holds only the opaque ID, resolution is relative through
`/p/<id>/`, superseded revisions get `status: legacy` rather than deletion so old stickers still
resolve, and a `/p/` page is deleted only when the part and its stickers are gone.

**Vocabulary, so the two levels have real names.** The design-level number is a **part number** (PN;
**MPN** when it is the manufacturer's own, **GTIN** in the GS1 barcode world). A per-object number is a
**serial number** (SN; **UII** under MIL-STD-130's IUID scheme, **SGTIN** in GS1/EPC). This project has
the first and not the second. If per-object tracking is ever needed, add a `serial` field alongside
`part_id` rather than redefining `part_id` — PN plus SN on one label is the standard form, and it
extends the scheme without invalidating a single printed sticker.

**Consequence for revisions.** Each revision needs its own part ID and its own page, since the ID *is*
the revision. Created the same day: `Kart Medulla PCB v2` = `1604 0948 4608 5574`
(`docs/p/1604094846085574.md`).

**Addendum (same day) — the names we use.** The standard names read backwards to us ("part number"
sounds like it names the object; "serial" sounds like it must count up, and modern ones often do not),
so the project uses plain names, with the standard ones kept as the translation for suppliers:

| Level | Our name | Standard name |
|---|---|---|
| The design revision — every unit built to it shares this | **design ID** | **PN**, part number (**MPN** when it is the manufacturer's own) |
| One individual physical object | **unit ID** | **SN**, serial number |

The 16-digit number in the QR is a design ID. There is no unit ID in the system, and adding one would
mean a second field, not a redefinition of the first. Use PN/MPN when talking to suppliers — that is
the term they answer to. The `part_id` field name is unchanged for now; renaming it to `design_id`
would touch `scripts/new_part.py`, `docs/scan.md`, `docs/p/index.md` and the frontmatter of each
existing part page.

**Not UII.** MIL-STD-130's unique item identifier was considered as a name for the unit ID and
rejected: a UII is not a bare number but a concatenation of issuing agency code + enterprise
identifier (CAGE/DUNS/DoDAAC) + serial (Construct 1), or the same with the part number inserted and
the serial only unique within it (Construct 2). It presumes a registered enterprise, and the standard
also specifies the mark as Data Matrix ECC 200 with a defined data syntax rather than a QR carrying
bare digits. The serial component itself may be random — nothing in the standard requires counting up
— but that does not make a random number a UII. SN stays the standard equivalent of unit ID.

## 2026-08-08 — CN1–CN10 pinout published, and cross-repo links pinned to commits

The medulla connector table was never missing, just invisible from here: it lives in dv-hardware as
`projects/kart-medulla/docs/pinout-cn-connectors.md`, next to the KiCad schematic that defines it,
and this repo only linked at it in prose. `scripts/sync_pinout.py` now copies it verbatim into
`docs/assembly/electronics/kart-medulla/pinout.md` under a provenance banner. Still one authored
table, so the drift that got the old hand-maintained tables deleted cannot return.

The copy is committed rather than rendered by a mkdocs hook the way the wiring and BOM tables are,
because GitHub Actions checks out kart-docs alone and cannot reach dv-hardware at build time.
`--check` reports staleness wherever the source is visible and exits 0 where it is not.

**Cross-repo links are pinned to a commit, never `main`** (Ruben's rule, this session): a `main`
link silently changes meaning as the other repo moves, so a reader comparing the copy against
"the source" would be reading a different document than the one that produced it. The banner
carries a permalink to the exact revision plus its date; syncing from a dirty dv-hardware working
tree is refused, because such a copy would correspond to no commit. `--allow-dirty` overrides.
`pinout-esp32-s3.md` and `esp32-s3-pin-capabilities.md` links in the medulla page are pinned too;
dv-hardware's `projects/kart-medulla/README.md` is deliberately left on `main`, because it is a
living rework list that is meant to be read as current state.

Three things found while doing it:

- **Every `dv-hardware` link in this repo pointed at `github.com/rubenayla/dv-hardware`, which
  404s.** The remote is `UM-Driverless/dv-hardware`. All of them were dead; all are fixed.
- Two stale pointers on the medulla page: it told readers to filter the wire list's `From`/`To`
  columns (the column is `Connected pins`, and pins read `medulla.CN1.2`), and claimed the
  "ESP32-S3 Pin Assignment" section above held a table with a `Silkscreen` column — that section
  explicitly carries no table.
- kart-docs and kart-medulla disagreed on the CN5.2 rework. This repo said remove R10 only; the
  firmware repo said R9+R10. Ruben confirmed this repo was right, and kart-medulla was corrected
  (`078e34e` there). kart-medulla also still called the steering sensor an AS5600.

kart-medulla reads dv-hardware directly rather than going through kart-docs: it is a peer of the
hardware repo, and a hop through the docs site could only ever be staler than what it reads today.

## 2026-08-08 — the mode switch is DPDT and the diagram only showed one of its poles

Rubén, correcting a wrong assumption of mine: the manual/autonomous selector is "a normal DPDT
switch in the panel of the kart". Both poles matter and only one was documented.

- **Pole 1 — throttle source.** Already in `wiring.yaml`: pedal or medulla `CMD_ACC_DAC` to the ESC.
- **Pole 2 — steering motor.** Was missing entirely. It breaks the cable from the Cytron H-bridge
  to the steering motor, so in manual the motor is physically disconnected from its driver. The
  netlist had `STEER_M+` running straight from `cytron.mplus` to `steer_motor.mplus`; it is now
  split into `STEER_M+_SW` (Cytron → switch) and `STEER_M+` (switch → motor).

**The Cytron's supply is not what the switch gates**, which is the part that had been confusing.
It sits permanently on PACK48; gating it was tried and reverted because the inrush at every
switch-to-autonomous browned out the Orin. Only the motor cable is broken.

**Which conductor pole 2 actually breaks is not verified** — M+ is what the netlist now assumes.
Buzz it before trusting the row; if it is M− or both, move it.

**Why the design is a switch and not electronics.** Manual mode works with the entire electronics
side unpowered, because metal contacts hold their position with no supply and no firmware. This
came up because `dv-hardware` had a MAX4660 analog mux on the medulla doing the same throttle
selection, believed to pass the pedal through when unpowered. It does not — a CMOS switch is open
at V+ = 0 (see the `dv-hardware` history entry of the same date for the datasheet evidence). The
panel switch was doing the real work all along, so the mux is redundant and is being deleted in
medulla-v2 rather than fixed.

**Still missing: the medulla cannot read the mode.** Nothing routes the switch position back to
it. Planned fix is a third pole shorting a sense wire to ground in autonomous, against a pull-up
on the medulla — read-only, so firmware can observe the mode but never cause it. Not built; the
medulla pin is part of the v2 allocation being decided in `dv-hardware`.

**Found and not fixed:** the SVG still shows the Cytron on 12 V, contradicting the 2026-07-30
decision that it runs off the 48 V pack. Filed in `tasks.md` — it needs a reroute, not a
relabel, so it was left alone rather than half-corrected.

### Same day — both open questions closed by Rubén

1. **"motor + is the one switched."** The mode switch's second pole breaks **M+**; M− runs
   straight through. The `STEER_M+_SW` / `STEER_M+` split in `wiring.yaml` was already modelled
   that way and is now stated as confirmed rather than assumed.
2. **"cytron is powered directly from the battery. confirmed."** So the SVG's `12 V → Cytron`
   wire was wrong in topology, not just in its label. Rerouted to branch off the battery run at
   (900, 1410) and climb the x = 1610 corridor to the Cytron, drawn in bold stroke because the
   legend already defines bold red as 48 V. First attempt routed it up x = 1900 and it crossed
   straight through the acronym legend box (1620–1960, y 80–350) and Kill 2 at (1700, 910) —
   caught by rendering the SVG to PNG and looking at it, which is the only way these collisions
   show up in a hand-written SVG. x = 1610 threads between the perception zone (ends 1600) and
   the legend (starts 1620).

Also corrected while there: the Cytron box said `25 A · 12 V`, now `25 A · 7–58 V in` (its real
input range, so the number stops implying a supply choice), and the steering motor box said
`DC 12 V`, now `fed from the 48 V bridge`. The motor's own voltage rating is still not recorded
anywhere — worth measuring or finding, but it is no longer being asserted wrongly.

### Same day — the steering motor is a 24 V part run at 48 V, on purpose

Closing the "motor voltage not recorded" note I left earlier that day: it **was** already recorded
— `docs/assembly/steering/index.md` has said "24 V geared DC motor (salvaged), driven from the
battery" all along. What was missing was the reason that is acceptable, which is the part a reader
would otherwise file as a bug.

Rubén, 2026-08-08: the motor is rated 24 V and runs off the ~48 V pack deliberately. It is never
worked hard continuously, it is well cooled, and firmware caps PWM at 50 % duty, so the average
voltage across it is about its rating. He is explicit that even removing the 50 % cap would not
damage it, given the duty cycle — so the cap is margin rather than the thing keeping the motor
alive.

Recorded in three places so it survives: a "Why a 24 V motor runs off the 48 V pack" section on the
steering page, the `steer_motor` description in `wiring.yaml`, and the motor box in the global SVG
(now "24 V motor on 48 V / intentional — PWM capped 50%") instead of the vague "fed from the 48 V
bridge" I had put there hours earlier.

**The firmware consequence worth carrying forward:** the 50 % PWM cap exists for a hardware reason.
Anyone treating it as an arbitrary tuning number and raising it should at least know why it is
there. Noted on the steering page next to the reasoning.

What would actually change this judgement is duty cycle, not voltage — sustained holding against
load rather than move-and-release.

## 2026-08-08 — Steering gears broken during a reflash; the board has no hardware default for steering

The steering swung to full lock while the ESP32-S3 was being reflashed with the kart in autonomous,
and broke teeth off the steering gears. Full diagnosis and the firmware response are in the
kart-medulla repo's `history.md`, same date; the requirement that came out of it is dv-hardware
`projects/kart-medulla/requirements.md` REQ-08.

What matters for these docs: the line in
`docs/assembly/electronics/kart-medulla/index.md` that reads *"Steering is NOT muxed — the ESP32
always drives the Cytron H-bridge directly; in manual mode firmware sets PWM = 0"* turned out to be
the whole story of the failure. It was written as a description of the mux's scope. It is also a
statement that steering has no safe state when firmware is not running, which is every reset and so
every flash — and nothing in these docs said that out loud.

The contrast is on the same page: `SELECT_THROTTLE` gets R32's 10 kΩ pulldown so the driver's pedal
takes over whenever the ESP32 is unbooted or crashed, and the compressor MOSFET gate has a 100 kΩ
pulldown holding it off through boot. Two outputs designed to fail safe, one that was not, and the
asymmetry was documented without ever being named as one.

A task is filed in this repo's `tasks.md` for the pulldown, including the meter test that separates
the two candidate causes, because the cause is not settled — Ruben's reading is that the swing
happened during the flash itself rather than just after the reboot.

## 2026-08-14 — Removed the "other repos are stale" banners, and a structure pass

Ruben, on the S3-build warning at the top of
`docs/assembly/electronics/kart-medulla/firmware.md`: noting that the repos are wrong instead of
fixing them is a botched idea. He is right, and the banner had already rotted — two of the three
statements it warned about had been corrected in `kart-medulla` on 2026-08-10, so the warning was
itself the stale doc by the time it was read. Fixed the sources (written up in
`kart-medulla/history.md`, same date) and deleted all three banners here: the S3-build one, the
"older task-rate figures elsewhere are superseded" one, and the "PID gains differ across sources"
one.

Corrections that came out of doing it, all checked against `main/main.c` and `kart-brain`:

- The PID callout's own numbers were stale. It said Kp 1.50 / Kd 0.02 citing `main.c:277-279`; the
  code has `PID_DEFAULT_KP` 1.00 and `PID_DEFAULT_KD` 0.05. A banner warning that other files drift
  had drifted. The page now names the constants and their file instead of citing line numbers,
  which move.
- The task table said `control`'s real rate was "capped by the blocking I2C AS5600 read, so it runs
  below 500 Hz". It is not — the MT6701 is read by MCPWM capture, nothing in the loop blocks, and
  500 Hz is measured via `control_iters`. The cap is UART bandwidth.
- The steering pipeline said the AS5600 is read over I2C. Sensor changed 2026-07-12.
- The comms-loss section said the firmware "does not drive [the SDC] yet". It has since 2026-07-26;
  what is missing is the wire from Q3's gate. Split into its own "Shutdown circuit (SDC)" section
  with the whitelist conditions spelled out, so the distinction between "logic runs" and "nothing
  happens physically" is visible rather than buried in a negative.
- Added a danger callout about de-powering the steering before a flash. The steering pins float
  through the bootloader window and this broke gear teeth on 2026-08-08; it was recorded in
  `kart-medulla/AGENTS.md` and in this repo's `tasks.md`, but nowhere on the published site, which
  is what a human at the kart actually reads.
- `kart-medulla/index.md` claimed "Native USB-OTG — the Orin link becomes a direct USB cable,
  dropping the USB-UART bridge IC". That is the S3's capability, not the kart's wiring: the link
  runs over UART0 through the DevKitC's CH343 bridge at 115200. Both the "Why ESP32-S3" bullet and
  the "Orin link" hardware-decision line now say what is actually connected.
- `assembly/sensors/camera.md` carried a "the YOLOv5 sections below are out of date" banner over a
  walkthrough for the ZED wrapper's built-in ONNX detection. Both halves needed work: the version
  (YOLOv11n now) and the framing. There are genuinely two modes — our own `yolo_detector` node,
  which is the default, and the ZED SDK's built-in detection, which `perception_zed_od.launch.py`
  exists for. The ONNX steps belong to the second and are now labelled as such, so nothing had to
  be deleted.
- `software/ros2/packages.md`'s `yolo_detector` parameter table was checked against the node while
  there: `conf_threshold` 0.25 -> 0.10, `imgsz` 640 -> 320, `device` default is auto-detect not
  `cpu`, and `crop_top` was missing entirely.
- `orin-setup.md` listed YOLOv5 in the JetPack-compatibility sentence.

Structure, since the same request asked whether the organisation makes sense:

- `docs/hydraulics/` sat at the top level while the nav filed it under Assembly, so the two braking
  systems lived in different places. Moved to `docs/assembly/hydraulics/` and rewritten — it opened
  with a bare bullet and no statement of what the hydraulics are for. It now says the pneumatics
  actuate these brakes, which is the fact that makes the two pages make sense together. Flagged
  that the recorded Sensata part code and the Mouser link on the same page are different variants;
  filed as a task rather than guessed at.
- `diego-design.md` renamed to `design-history.md` (named for the job, not the author) and added to
  the nav — it was linked from the pneumatics page but invisible in the sidebar, and was the only
  page mkdocs reported as missing from the nav. The build is now warning-free.
- Deleted `TODO.md`: a second, Spanish, task list at the repo root next to `tasks.md`, holding a
  plan for a Blue Pill v2 board with an AliExpress I2C DAC module. Superseded by the medulla PCB
  and its MCP4922. The CAN part link it also held moved to `stuff.md`, which is the declared home
  for links with no better place.
- `tasks.md` had a `## Done` section on the board while its own header said closed items live in
  `tasks/done-archive.md`, a file that did not exist. Created it and moved the eight closed entries
  across, plus the three this session closed.
- `assembly/index.md`'s trailing "Notes" was two bullets and a literal `...`. Kept the facts, said
  what the section is for, and turned the unknown bearing-spacer dimensions into an explicit
  measure-this rather than a `?` that reads as a typo.
- `electronics/computer.md` was three H1s deep with "Power consumption:" left blank and "Specs:
  TODO". Filled the specs from `orin-setup.md` (they were already recorded there), fixed the
  heading levels, and pointed the software half at the setup page instead of half-duplicating it.

## 2026-08-14 (later) — The AS5600 → MT6701 swap was never written into kart-docs

Ruben asked where the "why we dropped the AS5600" reasoning should live, and whether `faq.md` was
the place. It isn't: the FAQ holds whole-project questions (why pneumatic braking, why electric,
why an ESP32 at all) that someone asks before they know where anything lives. A decision about one
component belongs on that component's page, or the page has to link out for its own most important
fact. Rough test used: if the answer would change when you swap the part out, it goes on the part's
page.

Then his correction, which was the right one and I should have reached myself: obsolete material
must not be laid out like current material. Collapsed `??? info` blocks, not normal headings.
House style already had this — `powertrain/fasteners.md`, `steering/h-bridge.md`.

`assembly/steering/sensor/index.md` was written from before the swap: "Current sensor: AS5600 over
I2C (validated)… it is the validated, in-use sensor", with the MT6701 as "plan of record" that
"**will be** mounted", hardware "expected to arrive around 2026-07-22". The AS5600 was retired
2026-07-12 and the MT6701 has been reading on the kart since the end of July. Rewritten: MT6701
current, the two reasons for the change promoted to their own section, everything AS5600 collapsed
under a `## History` heading.

**The reason for the swap was only ever in `kart-medulla/history.md`,** which is the actual gap
behind his question. Now stated on the page: the AS5600 reconstructs the angle from how the *axial*
field varies across a 1 mm circle on the die, and the kart's shaft magnet is two large magnets stuck
sideways, which gives a field that is strong but nearly uniform over that span — nothing to measure,
so it reports no-magnet and gates its own output even touching the magnet. The MT6701 senses the
*direction* of the in-plane field at a point, which a big magnet defines cleanly. Sensing principle,
not resolution or price. The cable-length reason (medulla at the rear, ~1.2 m, I2C glitch hangs the
shared PCF8574 bus) is real but second — it is why PWM rather than I2C, not why this chip.

Kept two honesty caveats from the source notes rather than letting the page read as a win: the
MT6701 wants essentially the same small magnet and tight gap as the AS5600 (it tolerates our
uniform-field problem, not sloppy mounting), and past its 0.3 mm off-axis figure it degrades
smoothly rather than failing — a different failure class from the AS5600's detection failure.

**Five more pages still called the AS5600 current**, found by grepping rather than assumed:

- `wiring.md` — "Current (validated): an AS5600 … it works today", with the MT6701 as "Planned".
- `steering/index.md` — three places: the architecture paragraph, the signal-chain ASCII diagram,
  and step 1 of "Main process".
- `steering/motor-options.md` — feedback source, and a Doga-motor note about dropping "the AS5600
  and one I2C bus".
- `steering/h-bridge.md` — a VESC alternative saying to keep the sensor on I2C.
- `software/ros2/performance.md` — the same wrong claim already fixed on the firmware page earlier
  today: that the loop runs below 500 Hz because the I2C read blocks. It runs at 500 Hz, measured
  via `control_iters`; the cap is UART bandwidth. Also an open measurement item built on the same
  false premise, rewritten to ask about UART-write jitter instead.
- `faq.md` — one line listing I2C/AS5600 among peripherals the Orin's header could absorb. Replaced
  with the real obstacle: the angle now arrives as a ~994 Hz PWM whose duty carries the value, and
  one count is 244 ns of edge timing — a hardware-capture job, which strengthens rather than
  weakens the answer that the ESP32 earns its place.
- `software/dashboard.md` — the Magnet+AGC and I2C cards were documented as live readouts. They are
  permanently blank on this board, and kart-brain's own `index.html` already said so ("never
  populated on this board… would peg the chip to a permanent false alarm"). Marked as such.

Left alone deliberately: `build-journey/index.md` (dated posts — the June entry was true when
written, and the 2026-07-30 post already explains the swap), `pinout.md` (generated from
dv-hardware by `sync_pinout.py`, must be fixed upstream), and `packages.md`'s `ESP_DIAG_STEERING`
row (checked against `km_coms.h` — the frame really is AS5600 diagnostic registers, still valid on
the classic build).

Filed rather than guessed: `steering/fasteners.md` and `fasteners/bom.yaml` give screws and an
assembly order for mounting an AS5600 board to a bracket, and the MT6701 breakout is a different
board — needs someone at the kart. And the steering BOM lists the AS5600 with no MT6701 at all.

## 2026-08-14 (later still) — Three "ask Ruben" items were lookups, and two of my claims were wrong

Ruben on the three questions I ended the previous handoff with: *"super imprecise and unneeded
question. 3d printed holder, pressure sensor should be from the festo sponsorship notes, in
inventory also, i dont know what a bearing-spacer is, but we have the whole cad in fusion 360."*

He is right, and the shared instructions already say so — his repos are more accurate than his
recall, so asking him to enumerate facts on disk spends his turn on a lookup. All three were
answerable from `~/dv/`.

Worse, going to look turned up two things I had asserted wrongly on the sensor page, both because I
built it from `kart-medulla/history.md` and never opened `~/dv/kart/steering/history.md`:

1. **The sensor is FRONT-mounted, and always was.** Ruben, 2026-07-31: *"front! always was front.
   already done. with great 3d printed adjustable mount"*. I had written the cable-length argument —
   medulla moving to the rear, ~1.2 m, I2C unreliable over that run — as a reason for choosing PWM.
   That was the 2026-07-14 plan, which the same entry records as never having happened and not
   pending. The page now says so explicitly, because the claim is still sitting in `wiring.md`'s
   history and will otherwise get copied forward again.
2. **The two repos disagree about why the AS5600 was dropped**, which is the thing he originally
   asked me to document. `kart-medulla/history.md` has the magnet-physics story: axial field must
   vary across a 1 mm circle, the kart's two big sideways magnets give a uniform field, magnet-detect
   read zero with the chip touching the magnet. `~/dv/kart/steering/history.md` (2026-07-31) says
   *"magnet tolerance turned out not to be a real risk on this kart — the AS5600 already read the
   installed magnets fine, and the MT6701 confirms it."* The bench magnet was handheld and the kart's
   is mounted, which plausibly explains both, but nobody has reconciled them. I had written the
   magnet story as settled fact with a mechanism. Now presented as an open disagreement with both
   sides quoted, and filed.

The other two lookups:

- **The Sensata hydraulic pressure sensor is not fitted.** `~/dv/kart/pneumatics/README.md`:
  *"Hydraulic pressure sensor (Sensata PTE/700-33) - not used in this system"*, and the 2026-04 Festo
  price sheet lists it as *"Not Festo; on hand, currently unused"*. The kart-docs hydraulics page
  presented it as "our pressure sensor" with a spec table, i.e. as installed hardware. Rewritten as
  bought-but-not-fitted, with a pointer that the *pneumatic* sensors (Festo SDE5-D10) are the ones
  actually reading. The variant-code mismatch I had filed as a task is moot next to that — dv records
  it as PTE/700-33, matching the `-33` in the recorded code, so the Mouser link was simply the wrong
  listing.
- **The steering sensor mount is a 3D-printed adjustable holder**, not a bracket with screws.
  `steering/fasteners.md` and its `bom.yaml` said "AS5600 sensor board to mounting bracket" and
  "AS5600 must be centered over magnet". Corrected, and the adjustability is now stated as the point:
  it is what lets the air gap and angular zero be trimmed after assembly. Still unrecorded anywhere,
  per the dv entry: the mount's CAD source and its adjustment range. Filed.
- **The bearing spacer is a CAD lookup**, not a workshop trip — the whole kart is modelled in Fusion
  360. The task said "measure them off the kart", which is why it read as a chore. Also renamed: the
  original note called it "a tube", which is why the item was unrecognisable to its own owner.

Method note worth keeping: every wrong thing I wrote today came from reading one repo's history and
treating it as the record. `~/dv/` is the engineering log and kart-docs' own `AGENTS.md` says to
check it before rewriting any subsystem. I did not, on a subsystem rewrite. Grep `~/dv/kart/<area>/`
first, not last.

## 2026-08-14 (correction) — I broke a correct fact by trusting an agent's inference

Reverting my own commit `cd573f2`. **The kart-medulla PCB is at the rear of the kart, next to the
Orin; the sensor is at the front on the steering shaft; the ~1.2 m run between them is real**, and
it is the reason the single-wire PWM interface matters. Confirmed by Ruben, 2026-08-14.

How I got it wrong. `~/dv/kart/steering/history.md`'s 2026-07-31 entry reads:

> **Mounted in the FRONT** (Rubén, 2026-07-31: *"front! always was front. already done. with great
> 3d printed adjustable mount"*). Note this contradicts the 2026-07-14 plan … — that rear move never
> happened and is not pending.

Ruben's quote is about the **sensor**. The sentence after it is unquoted agent commentary that
inferred the **kart-medulla PCB** had not moved either. Two different objects. I read the paragraph
as one claim and propagated it into `wiring.md` and the sensor page as "sensor and PCB are both at
the front, so the run is short" — deleting a correct explanation and replacing it with a wrong one.

Two lessons, and the second is the one that actually cost the turn.

1. **A quote's scope is the quote, not the paragraph around it.** When a note pairs a direct
   quotation with an agent's gloss, only the quoted words carry the user's authority. If the gloss
   generalises past the quote's subject, it is a claim to check, not a fact to inherit. I had
   already spotted this — I told Ruben the quote was about the sensor while the rear move was about
   the PCB — and then wrote the page as if the gloss were true anyway.
2. **Answer the question that was asked.** Asked who wrote the note, I gave the right answer and
   then kept going into what I could and could not stand behind, ending on a request for a decision.
   Ruben: *"you are treating sentences like a soup of words. they aren't."* The sprawl was the
   symptom; the cause was reading a paragraph as a bag of assertions with a single truth value
   instead of parsing what each sentence was about.

Also corrected the source note in `~/dv/kart/steering/history.md` in place, since it is a
current-state claim about the kart's layout rather than a dated observation, and it is what will be
read next time. Marked as a 2026-08-14 correction with its old wording quoted, so the record shows
what changed.

Terminology, per Ruben the same day: write **kart-medulla PCB**, never "the board". "Board" is
ambiguous here — the kart has several, and the dev-board-on-a-PCB arrangement makes it worse.

## 2026-09-06 — Legacy Tony Kart Extreme brake spares research

The kart documentation identifies the chassis as a Tony Kart Extreme and says the original
hydraulic circuit remains in service, with flexible hoses using **M10×1.0 female inverted-flare
connectors**. A period analysis of the 1998 Extreme describes the matching legacy system as a
two-piston master cylinder without a recovery reservoir, a two-piece caliper with 28 mm pistons,
and a grooved 210 mm disc. A separate BS1 identification for late-1990s Extreme chassis matches
that description. Current catalogue data still lists BS1/BS2 pump assemblies and components, a
BS1 steel-braided hose kit, calipers, pads, and discs, but availability of the old complete parts
should be confirmed before ordering. Sources: <https://tkart.it/en/magazine/first-analysis/historic-tony-kart-extreme-1998>,
<https://forums.kartpulse.com/uploads/short-url/q2LkxLOz4d8Akc3W1q68pZDRR2O.pdf>,
<https://www.agskartparts.com.au/products/456/BRAKE-PAD-SOFT-OTK-BS2>,
<https://www.kart24.eu/kartshop/bremsen/leitungen-verschraubungen/>.

## 2026-09-19 — Build journey QR in the repository README

Added a clickable QR image to `README.md`, stored at `docs/assets/images/build-journey-qr.png`. It encodes <https://um-driverless.github.io/kart-docs/build-journey/> directly, using a standard QR code with high error correction and a four-module white border. Verified decoding with zxing-cpp at the original 392 px and displayed 244 px sizes. The strict MkDocs build passed.

## 2026-09-19 — Build-journey media loading

The live page downloaded 13,079,698 encoded response-body bytes in an isolated Chrome session at 1280×900, measured through five seconds after load. All eight MP4 files were requested before playback. This is one unthrottled run, not a controlled latency benchmark.

The 20 displayed source images totalled 24,154,189 bytes. WebP copies total 3,293,544 bytes (86.4% smaller). Photos use quality 82 and a 1600-pixel maximum side; PNG diagrams and screenshots use lossless compression at original dimensions. Originals remain alongside the derivatives for regeneration and existing direct links. Eight small WebP video posters replace metadata preloading; videos use preload=none and lazy loading. Explicit media dimensions reserve layout space, and the first photo loads eagerly. The script scripts/optimize_journey_media.py regenerates these assets using Pillow and ffmpeg. GitHub Pages remains the host; measure the media reduction before considering migration.

Validation: strict MkDocs build passed; isolated Chrome checks at desktop 1280×900 and mobile 390×844 decoded all 20 images, played all eight videos, and found no initial MP4 requests or horizontal overflow. Photo and rendered diagram previews were inspected. References: https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/video and https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#webp .

Live verification after deployment of 0a141e3: the same isolated Chrome check downloaded 596,144 bytes versus 13,079,698 before (95.4% fewer bytes), with zero initial MP4 requests. Both samples used a fresh browser at 1280×900 and five seconds after load; transfer reduction is measured, not a claim of equivalent load-time improvement. GitHub Actions run 35439582699 passed build and deployment.

## 2026-09-19 — Collapsible build journey sharing section

Added a collapsed “Share this page” section before the build journey jump links, reusing `docs/assets/images/build-journey-qr.png`. The strict MkDocs build passed. A headless browser check confirmed the section starts closed, opens on click, and loads the QR image.
