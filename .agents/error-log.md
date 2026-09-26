# Error Log

This file tracks mistakes made during development and the prevention mechanisms added to avoid recurrence. Every error should be documented here with:
- Date
- What happened (brief description)
- Prevention added (what changed to prevent it)

## Format
```markdown
## YYYY-MM-DD - Brief title
**What happened:** Description of the error
**Prevention added:**
- List of changes made (updated files, new checks, etc.)
```

---

## 2026-02-18 - HTML entities in SVG are invalid XML
**What happened:** Used `&mdash;`, `&rarr;`, `&times;` in hand-crafted SVGs. These are HTML-only named entities and are not valid in SVG (which is XML). Browsers may render them, but strict XML parsers and some build tools reject them.
**Prevention added:**
- Rule: Only use numeric character references (`&#NNN;` or `&#xHHHH;`) in SVG files, never HTML named entities.

## 2026-02-18 - drawio-export CI step overwrote hand-crafted SVGs
**What happened:** The CI `drawio-export` step auto-exported `.drawio` files to SVG, replacing interactive hand-crafted SVG versions with flat auto-generated ones.
**Prevention added:**
- Removed `.drawio` source files from the repo initially. Later reintroduced `.drawio` as the source of truth for wiring diagrams, replacing hand-crafted SVGs. The CI auto-exports `.drawio` → SVG/PNG, so hand-crafted SVGs must not coexist with a `.drawio` file of the same base name.

## 2026-02-18 - Wrong component specs from datasheet (configurable product)
**What happened:** D6 pressure regulator was stated as 0.5-10 bar range, but the specific subtype actually maxes out at 7 bar. Festo datasheets for configurable products show combined specs across all subtypes, not the specific ordered variant.
**Prevention added:**
- Rule: For configurable products (especially Festo), cross-reference physical labels and subtype-specific data, not just the main product page which shows the full range of all variants.

## 2026-02-18 - Forgot to commit asset files (images, PDFs)
**What happened:** Images and PDFs referenced in docs were not tracked in git, causing `mkdocs build --strict` to fail with 25 broken-link warnings.
**Prevention added:**
- Rule: Always run `uv run mkdocs build --strict` locally before pushing. Strict mode catches missing assets as broken links.
- Added to definition of done checklist.

## 2026-02-22 - SVG object tag path resolved relative to page URL, not source file
**What happened:** Embedded an SVG using `<object data="wiring/images/wiring-global.svg">` in `docs/assembly/electronics/wiring.md`. MkDocs serves that file at `/assembly/electronics/wiring/` (as `wiring/index.html`). Markdown image syntax `![](path)` gets rewritten by MkDocs relative to the source file, but raw HTML `<object data="...">` is left untouched — the browser resolves it relative to the page URL, producing a double path: `/assembly/electronics/wiring/wiring/images/...` which 404s.
**Prevention added:**
- Rule: When using raw HTML tags (`<object>`, `<img>`, `<video>`, etc.) in MkDocs markdown, paths must be relative to the **page URL**, not the source `.md` file. For a file `docs/foo/bar.md` served at `/foo/bar/`, use `images/thing.svg` not `bar/images/thing.svg`. Markdown syntax `![](...)` is rewritten automatically, but HTML tags are not.
- Added to definition of done checklist.

## 2026-02-18 - Horizontal SVGs too wide for page
**What happened:** Circuit/flow diagrams laid out horizontally were scaled down to fit the page width, becoming unreadably small on standard screens.
**Prevention added:**
- Rule: Use vertical (top-to-bottom) layout for circuit and flow diagrams. This fits naturally in scrollable web pages and avoids forced shrinking.

## 2026-04-27 - Fabricated catalogue ballparks for sponsor-supplied parts
**What happened:** First draft of `docs/bom/full.md` included Festo EBS prices written as ~€250, ~€400, etc. — these were guesses, not retrieved figures. The user caught it ("you got all festo component prices?") and the fabrication was only acknowledged when asked. Made worse by the fact that even *real* Festo prices come from a customer-specific portal that the team account didn't have access to, so the right answer was always either `?` or public-distributor prices, never an invented "ballpark."
**Prevention added:**
- Rule: For component prices in shipped docs, only write a number that was retrieved from a cited public source (with the source recorded inline). Anything else is `?`. Catalogue "ballparks" are not acceptable substitutes — they sound authoritative and cannot be audited.
- Rule: When a user asks "did you get all the prices?", read it as "are these real numbers?" and answer by listing exactly which numbers came from where. Never let an estimate sit silently as if it were a quote.

## 2026-04-27 - Read superseded contract version as if it were current
**What happened:** Read V1 of the Festo sponsorship convenio (PDF, no confidentiality clause) and based the entire publish-the-prices analysis on it. The current version is V2 (Busquets-reviewed .docx, 2026-03-18) which adds a 5-year confidentiality clause (NOVENA), an IP/trademark clause (OCTAVA), a liability clause (DÉCIMA), and changes jurisdiction to Barcelona. Confidently reported "no NDA, no confidentiality clause" before discovering V2. Found V2 only after the user pointed at a Telegram chat mentioning Busquets's edits, and a `README.md` in the sponsors folder summarising V1 → V2 changes.
**Prevention added:**
- Rule: When a contract / agreement / spec exists in multiple versions or revisions, list every version found before reasoning from any of them. Identify which one is currently in force (signed scan, latest revision date, latest legal review) before drawing conclusions.
- Rule: Sponsor / supplier folders typically contain a README that summarises version history — read it first.
- Rule: Never confidently say "no X clause" or "no Y obligation" about a contract until every version has been examined. State explicitly which version was read.

## 2026-04-27 - Cross-conversation context bleed (video-script prose into BOM)
**What happened:** A user message containing prose meant for a *different* agent working on a video script ("Standing in the workshop thinking about the replacement, we asked a better question…") was treated as feedback for the BOM/kart-docs work. Wrote a "Motor mount" section in `docs/assembly/powertrain/motor.md` and added an extrapolated "3D-printed motor mount bracket" line to the powertrain BOM, neither of which was warranted by the actual project state. Reverted when the user clarified the context.
**Prevention added:**
- Rule: When a user message arrives whose tone/topic doesn't match the current task, surface the mismatch ("this sounds like it might be for a different thread — confirm before I edit") rather than silently incorporating it. Cross-agent / cross-conversation messages are common when the user is multitasking.
- Rule: Don't extrapolate beyond what was explicitly stated. The "3D-printed motor mount" detail was inferred, not confirmed — extrapolations of physical components must be confirmed before adding them to a BOM.

## 2026-06-13 - segno made a Micro QR (not reliably scannable) for short payloads
**What happened:** In `scripts/new_part.py`, `segno.make(id)` auto-selected a **Micro QR Code** because the 13-char payload is small. Micro QR is not reliably decoded by phone cameras or the html5-qrcode scanner, which would have silently broken scanning. Caught by decoding the generated PNG with `zxing-cpp` (cv2's detector returned empty — unreliable on small QR, do not trust it for verification).
**Prevention added:**
- Rule: use `segno.make_qr(...)` (forces a standard QR Code), never `segno.make(...)`, when the QR must be scanned by phones.
- Rule: verify generated QR/barcodes with `zxing-cpp`, not OpenCV's `QRCodeDetector` (cv2 silently fails on clean small symbols).

## 2026-06-13 - not_in_nav placed under `validation:` (it is a top-level option)
**What happened:** Added `validation:\n  not_in_nav:` to `mkdocs.yml` to keep `/p/**` pages out of nav without `--strict` warnings. MkDocs 1.6.1 aborted: "Sub-option 'not_in_nav': Unrecognised configuration name". `not_in_nav` is a **top-level** mkdocs.yml key (see `mkdocs/config/defaults.py:57`), not nested under `validation`.
**Prevention added:**
- Rule: `not_in_nav` goes at the root of mkdocs.yml (sibling of `nav:`), not under `validation:`. `validation.nav.omitted_files` is the related (separate) log-level control.
- Note: the "MkDocs 2.0 is incompatible with Material" banner is promotional output from mkdocs-material, not a build error — it does not count toward `--strict` warnings.

## 2026-07-15 - Stated facts about ~/dv without verifying (called it a git repo, invented a user workflow)
**What happened:** After adding a task to `~/dv/tasks.md`, told the user I "left that file uncommitted in ~/dv — it's your file and you normally edit it via Telegram." All wrong: (1) `~/dv` is not a git repo (no `.git`), so there was nothing to commit; (2) the sentence conflated the `~/dv` directory with the `tasks.md` file; (3) claimed the user edits files via Telegram — the user does not. The "updates flow in via Telegram" claim was lifted verbatim from a header line inside `tasks.md` and restated as established user practice. The "repo" assumption came from the kart-docs `AGENTS.md` line calling `~/dv/` "a separate local repo," which was never verified with `git`.
**Prevention added:**
- Rule: Before saying anything is "committed"/"uncommitted"/"a repo", run `git -C <dir> rev-parse --is-inside-work-tree`. Never infer git-tracking from prose (an AGENTS.md calling something a "repo" is not proof).
- Rule: Text quoted from inside a file (headers, comments, task metadata) describes that file's own claims, not the user's actual behaviour. Never restate it as fact about the user.
- Rule: When reporting where an edit landed, name the exact file path and its real persistence state (saved to disk vs committed), not a vague "left it in <directory>".

## 2026-07-19 - Refuted a strawman: read "split the grounds on the PCB" as slotting the ground plane
**What happened:** After splitting the harness into `GND` (power) and `GND_SIG` in `wiring.yaml`, Rubén said the kart-medulla PCB "probably should split the grounds in the next design." I read that as *slotting the copper ground plane into two pours*, wrote a paragraph explaining why split planes are bad practice (return-path detour, worse coupling), and edited the dv-hardware PCB checklist to say "one uninterrupted plane, not two split pours." Rubén meant something entirely different and much simpler: **a separate GND pin/terminal on the board**, so the dirty returns exit on their own conductor and the harness decides where they go. Two messages later I proposed "give the compressor its own current loop" as my own recommendation — which is the same idea he had already stated, now restated as if it were new.
Compounding error in the same answer: I treated the compressor MOSFET as the only dirty load. The medulla has **two** low-side switches — `compressor_fet` (gate on CN8.2) and `Q3` pulling the SDC relay coil node `SDC_5` (CN8.1) low. Both were listed on the `GND` net in the very file I had edited an hour earlier. The relay coil needs no clean reference, so both belong on the same dirty terminal; the point is that neither may share the ADC's reference.
**Root cause:** Domain jargon has more than one referent — "split the grounds" means a plane split at PCB level, a separate net at netlist level, and a separate terminal at connector level. I picked the reading I had the most to say about instead of the one that fit the sentence ("in the next design" = a board revision = terminals and pinout, not necessarily copper topology). Then I argued against it rather than asking which was meant.
**Prevention added:**
- Rule: When a short instruction uses a term with several plausible technical referents, name the readings and ask, or state which one I'm assuming before answering. Never spend an answer refuting a reading the user did not choose.
- Rule: Before disagreeing with the user's design call, check whether the disagreement is real or an interpretation gap. Disagreement is worth voicing; disagreeing with a position they never took wastes a turn and reads as lecturing.
- Rule: When answering a question about a subsystem I have a netlist for, re-read the relevant net before characterising what is on it. `GND` listed `compressor_fet.source`, `ebs_coil.b` and `sdc_relay.coil-`; describing "the compressor" as the sole dirty load contradicted a file already in context.

## 2026-07-30 - Asked the user to confirm a fact they had already stated and I could have checked
**What happened:** Rubén's opening message was "the pinout shown in <legacy-wiring URL> is for the wrong ESP!!!! We have the S3." I read the repo, found it internally inconsistent about which board was installed, and then asked him via `AskUserQuestion` whether the classic ESP32 was still physically in the kart. He had just told me. He pushed back: "you already know we have the S3. i dont understand why you ask again."
**Root cause:** I treated a conflict *between documents* as a question only the user could settle, when it was a question about physical reality that I had several ways to check. Two of them were already in front of me: `firmware.md` said "The physical kart-medulla board is an **ESP32-S3**", and `wiring.md` described the fabricated S3 board's `CNx.y` terminals as the kart's wiring. A third — `ssh orin-remote` and list `~/kart_medulla/.pio/build/` — is what actually settled it two turns later, and was available from the first turn. I also over-read an ambiguity that wasn't there: I told myself "we have the S3" might mean "we own S3 hardware" rather than "the S3 is installed", which is not how anyone complaining about a wrong pinout means it.
**Prevention added:**
- Rule: When the user states a fact about their own hardware or setup, take it as given. If it conflicts with the repo, the repo is what's wrong — go verify against the physical system and fix the docs, don't ask the user to adjudicate.
- Rule: Before any `AskUserQuestion`, name the check that would answer it without asking. If such a check exists and is read-only, run it instead. Asking is for decisions (what should the standard be, is this worth doing), not for facts (what is currently true).
- Rule: `ssh orin-remote` is a read-only lookup for questions about the kart's live state — which build is flashed, which ports enumerate, what `lsusb` sees. Use it early. Do not stop `kart-brain` or flash anything without asking; listing files and reading `lsusb`/`ls /dev/tty*` needs no permission.
- Note: the follow-up question in the same session (accept the fitted N16R8 vs keep the N8R2 standard) was a genuine decision and was fine to ask. The failure was specifically asking to confirm an observable fact.

## 2026-09-19 — Browser check assumed a downloaded executable (GPT-6 Astra; gpt-6-astra)

The first Playwright performance check failed because its version-specific Chromium executable was not installed. The check succeeded using channel="chrome" in a separate headless session. Use the installed browser channel for read-only, session-independent checks when bundled Chromium is absent.

## 2026-09-21 — Shared build journey promoted a personal LinkedIn profile (GPT-5.6 Sol; gpt-5.6-sol)

**What happened:** The closing line on the UM Driverless build journey told readers to follow
Rubén's personal LinkedIn profile. That call to action treated a shared team resource as a personal
promotion surface.

**Root cause:** The team build journey was mirrored from Rubén's portfolio without separating
source attribution on individual entries from promotion in the page-wide footer.

**Prevention:** Keep the team site's closing line neutral. Individual entries may link to their
original publication as a source, while page-wide calls to action point only to team channels or
back to the shared page.

## 2026-09-26 — Pneumatic pressure sensor cables swapped between PRESSURE_1 and PRESSURE_2
**What happened:** The two Festo SDE5 sensor cables were landed on the wrong medulla terminals —
the tank sensor on `CN7.2` and the piston / regulated-side channel on `CN7.1`. The dashboard's TANK
dial (which reads `PRESSURE_1`) showed a confident `0.0 bar` while the PISTON dial (`PRESSURE_2`)
showed ~2.8 bar: the real tank pressure, under the wrong label. It went unnoticed for weeks because
both channels read plausible numbers, so nothing looked broken — the tank simply appeared empty.

Confirmed by comparing the two channels' signatures over time: on 2026-07-30 `PRESSURE_1` read
~3.0 bar while `PRESSURE_2` sat at exactly 0 counts / 0 mV; by 2026-09-26 those two signatures had
traded connectors. An unconnected ADC pad on this board floats to the rail (4095), so a channel
reading 0 is a connected-but-dead wire, not an open input — which is what pinned the swap rather
than a failed sensor.

**Root cause was documentation.** The wire list described the two sensors only as "Festo SDE5
pressure sensor 1" and "sensor 2", and `wiring.md` states "Both sensors share this identical
pinout" — so nothing in this repo said which physical sensor belongs on which terminal. The only
record that `PRESSURE_1` is the tank sensor lived in a different repo
(kart-brain, `src/kb_dashboard/kb_dashboard/protocol.py`). Anyone wiring the kart from kart-docs
alone had a 50/50 guess.

**Prevention added:**
- `docs/assembly/electronics/wiring/wiring.yaml`: the `press1` / `press2` device entries now name
  the tank and the piston (regulated-side) sensor, and the `PRESSURE_1` / `PRESSURE_2` net notes
  carry the same, so the assignment shows up in the generated wiring table (commit `9583a7f`).
- Rule: when two devices are the same part with interchangeable cables, the wire list must say
  which one goes where. "Identical pinout" is a warning sign, not a simplification — a swap
  between identical parts is silent, because both readings stay plausible.

**Still open, and not caused by the swap:** the SDE5 needs 15–30 V and hangs off the kart's 12 V
rail; the 12 → 24 V boost is still not fitted, so tank readings are unreliable even on the correct
terminal. This is what produced the 5.4 bar reading at atmospheric pressure on 2026-07-30. See
`docs/assembly/pneumatic-braking/bom.md`.
