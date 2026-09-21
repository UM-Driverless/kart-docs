# Agent Quick Reference

## Key Files (Read Before Working)
Before making any changes, consult:
1. **`tasks.md`** (repo root) — Task board. Claim a task by setting status In progress + your id, commit, then Done. One `tasks.md` per repo and it lives at the root — there is no `.agents/tasks.md`. Done items don't stay on the board: they move, with date and closing note, to `tasks/done-archive.md`, except a done step of a task that's still open, which stays put until the whole cluster closes.
2. **`.agents/error-log.md`** — Past errors and added preventions
3. **`.agents/definition-of-done.md`** — Pre-commit checklist

## Project Overview

Documentation repository for the UM Driverless autonomous kart project. Built with MkDocs Material theme, deployed to GitHub Pages.

**This repository is the single source of truth for kart documentation.** Previously managed in Notion, all documentation has been migrated to this MkDocs-based system.

**Live site:** https://um-driverless.github.io/kart-docs/

## Build-journey post media: `~/ruben-files/videos/kart/linkedin/posts/`

Every build-journey post has a source folder there, named **`<YYYY-MM-DD>_<slug>`** — the date
is the LinkedIn publication date. Look it up by date; do **not** search for filenames resembling
the post title, and never conclude the media is missing without listing that directory.

```bash
ls -d ~/ruben-files/videos/kart/linkedin/posts/2026-07-29*/     # find by date
```

Each folder holds the raw video and images plus `post.md` (the published LinkedIn text),
`README.md`, `history.md`, and often a transcript and `.srt`. Numbered files (`01_…`, `02_…`)
are the ones that went into the post, in order.

**Adding a post's media to this repo:**

1. Videos are **compressed before committing** — the raw files are 100–250 MB. Target ≈20 MB,
   which is where every existing clip sits (largest is 21.7 MB):
   ```bash
   ffmpeg -i <raw>.mp4 -vf scale=1280:-2 -c:v libx264 -crf 30 -preset slow \
     -pix_fmt yuv420p -movflags +faststart -c:a aac -b:a 96k <slug>.mp4
   ```
   CRF 30 at 720p is the setting that lands there for talking-head footage; raise the CRF if a
   clip comes out heavier. Check a frame (`ffmpeg -ss 12 -i out.mp4 -frames:v 1 f.png`) before
   committing.
2. Video → `docs/build-journey/videos/<slug>.mp4`, referenced as `videos/<slug>.mp4`.
3. Images → `docs/build-journey/images/<YYYY-MM-DD>-<slug>/`, keeping the source filenames,
   then run `uv run scripts/optimize_journey_media.py` (requires ffmpeg). It keeps the
   originals, creates WebP display copies and video posters, and adds image dimensions
   plus on-demand video loading so new posts do not slow the whole page.
4. The same post also goes in the **portfolio repo** (`~/repos/portfolio`), which uses absolute
   paths (`/videos/…`, `../images/build-journey/…`) and links the post title to its LinkedIn
   URL. Update the `**Jump to:**` anchor line in both.

**Mini-entries (decided 2026-08-07):** the build journey also carries small dated entries for
build moments too minor for a LinkedIn post (a part arriving, a quick board fix, a bench
observation) — the page is the build log, not only a post mirror. Anatomy: same `## <title>
{ #<anchor> }` section, `*<YYYY-MM-DD>*` date line with **no LinkedIn link** (the missing link is
what marks it as a mini), one photo + a few sentences, inserted in chronological order among the
posts. Add its anchor to `**Jump to:**` like any other. Mirror every mini into the portfolio's
build journey the same way. Facts in a mini get the same verification bar as a post — check
numbers against `~/dv/` before publishing them.

End the team page with its final entry; it needs no closing message or call to action. Individual
entries may cite their original posts as sources because this is a shared UM Driverless record.

## Related Repository: `~/dv/` (engineering working notes)

The team's raw engineering notes, decisions, datasheets, and component data live in a **separate local repo at `~/dv/`** (the "DV" / driverless working repo). This `kart-docs` repo is the *polished, published* documentation; `~/dv/` is where the messy source material and design reasoning accumulate. **Check it before researching or rewriting any subsystem** — the answer (and its history) is usually already there.

Most useful entry points:

- **`~/dv/kart/pneumatics/`** — EBS/ASB braking: `history.md` (dated design decisions, sizing math, rule checks), `README.md` (on-hand components + part numbers), `pneumatic_diagram.svg/.drawio`, datasheets in `resources/`.
- **`~/dv/kart/<subsystem>/history.md`** — per-subsystem decision logs (`steering/`, `kart-medulla/`, …). These follow the "consult selectively — grep, never read in full" convention.
- **`~/dv/history.md`** — top-level cross-cutting history.

These `history.md` files are the authoritative record of *why* a design is the way it is — grep them when a doc page needs the rationale behind a choice.

## Related code repositories (ground truth for docs)

Three sibling repos hold the actual implementation; when a doc describes them, verify against these, not memory:

- **`~/repos/dv-hardware/`** — the KiCad PCB projects. `projects/kart-medulla/` is the authoritative source for the medulla board: `output/drc_report.json` carries the exact `F.Silkscreen` connector layout (CN1–CN10), and `docs/pinout-esp32-s3.md` the pin map. Use this for any connector/pinout claim.
- **`~/repos/kart-brain/`** — the ROS 2 software stack on the Orin (`src/kb_*`, `src/kart_*`), including the `kb_dashboard` web dashboard and `kb_bms` battery node. `history.md` holds the design rationale.
- **`~/repos/kart-medulla/`** — the ESP32 firmware. `components/km_coms/km_coms.c` is the ground truth for the Orin↔ESP32 wire protocol; `.agents/esp32s3-pinmap.md` is the firmware pin map; `history.md` logs the bring-up decisions.

## Tech Stack

- **Documentation:** MkDocs with Material theme
- **Package Manager:** uv (migrated from Poetry)
- **Python:** >= 3.12
- **BOM Management:** YAML-based system in `docs/assembly/*/bom.yaml`
- **Deployment:** GitHub Actions → GitHub Pages

## Project Structure

```
kart-docs/
├── docs/
│   ├── bom/
│   │   ├── index.md          # BOM overview with dynamic parts table
│   │   └── README.md         # BOM management guide
│   ├── assembly/
│   │   ├── */bom.yaml        # Component data per assembly
│   │   ├── powertrain/
│   │   ├── steering/
│   │   ├── electronics/
│   │   └── sensors/
│   ├── tools/
│   │   ├── index.md          # Tools catalog documentation
│   │   └── tools.yaml        # Tool inventory
│   └── assets/
│       └── datasheets/       # PDF datasheets
├── scripts/
│   ├── aggregate_bom.py      # BOM report generation
│   └── sync_pinout.py        # Pulls the CN1–CN10 pinout page from dv-hardware
├── generate_bom_hook.py      # MkDocs hook for dynamic parts table
├── generate_bom_reports.sh   # Helper script for reports
└── pyproject.toml            # uv-compatible project config
```

## Key Commands
```bash
uv sync                        # Install dependencies
uv run mkdocs serve            # Local dev server
uv run mkdocs build --strict   # Build with strict warnings (CI uses this)
./generate_bom_reports.sh      # Generate BOM reports
uv run python scripts/sync_pinout.py          # Refresh the CN1–CN10 pinout page
uv run python scripts/sync_pinout.py --check  # Fail if that page is stale
```

### Pin maps come from dv-hardware

A pin map is only correct relative to a schematic revision, so `dv-hardware` owns
both medulla pin tables and kart-docs never hand-writes them:

- **`projects/kart-medulla/docs/pinout-cn-connectors.md`** — the CN1–CN10 terminal
  assignments. Republished at `docs/assembly/electronics/kart-medulla/pinout.md` by
  `scripts/sync_pinout.py`, which copies it verbatim under a provenance banner.
  Edit the dv-hardware file, then re-run the script and commit the result — the
  generated page is committed, because GitHub Actions checks out kart-docs alone
  and cannot reach dv-hardware at build time. The script finds dv-hardware as a
  sibling directory, or via `$DV_HARDWARE`.
  **Cross-repo links are pinned to a commit, never to `main`.** The banner links
  the exact dv-hardware revision the copy came from, so it keeps meaning what it
  meant when the copy was made instead of drifting as dv-hardware moves on.
  Syncing from a dirty dv-hardware working tree is refused (`--allow-dirty`
  overrides) because such a copy would correspond to no commit.
- **`projects/kart-medulla/docs/pinout-esp32-s3.md`** — the 44-row terminal → GPIO
  map. Linked, not copied.

## Key Features

### BOM Management System

**YAML-based part tracking:**
- Each assembly has `bom.yaml` with component specifications
- Fields: id, part_number, description, quantity, unit_cost, status, criticality, suppliers, specifications
- Hierarchical structure matches physical assembly

**Dynamic features:**
- `generate_bom_hook.py` auto-generates searchable HTML table on build
- Real-time search, filtering by assembly/status/category
- Sortable columns, color-coded badges
- Cost summaries injected into BOM index

**Report generation:**
- `scripts/aggregate_bom.py` creates JSON + CSV reports
- Outputs: cost summaries, supplier lists, status reports

### Tools Catalog

- `docs/tools/tools.yaml` - Workshop tool inventory
- Categories: hand tools, electronics, power tools, measuring equipment
- Tracks: location, status, calibration schedules, safety requirements

## Important Patterns

### Adding Components to BOM

1. Navigate to `docs/assembly/{assembly}/bom.yaml`
2. Add component in YAML format
3. Component auto-appears in searchable table on next build

### Documentation Philosophy

- **Consolidate, don't duplicate** - Keep docs in README.md files, avoid creating extra "guide" files
- **No authors in pyproject.toml** - Git history tracks contributors
- **Folder README convention** - Use `README.md` for folder documentation (e.g., `docs/bom/README.md`)

## Files to Ignore/Not Create

- Don't create FEATURES_ADDED.md, MIGRATION.md, or similar - keep current state in README
- Don't maintain author lists - Git already tracks this

## Build Pipeline

GitHub Actions workflow (`.github/workflows/deploy-docs.yml`):
1. Uses `astral-sh/setup-uv@v4`
2. Runs `uv sync` to install dependencies
3. Builds with `uv run mkdocs build --strict --verbose`
4. Deploys to GitHub Pages

## Commit Safety Protocol (Mandatory)
Before any `git commit`, you MUST:
1. Run `git status` to see which files will be included
2. Run `git diff --cached` to verify changes line by line
3. If build fails: document the error in `.agents/error-log.md`, fix it, and add prevention if recurring

**Never commit blindly.**

## Pushing
Push finished work without asking. Committing and pushing are one step here — a commit sitting
unpushed helps nobody, and the deploy workflow is what publishes the site. The checks above are
the safeguard, not a confirmation prompt. Do not end a turn with "say the word" or "want me to
push?"; push, then report the branch and commit.
