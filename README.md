# kart-docs

Documentation for the autonomous KART project.

📘 Live site: <https://um-driverless.github.io/kart-docs/>  
🧠 Main source: [Notion Kart Documentation](https://www.notion.so/KART-1b378747314380acb23ee354a4a4c4c7)

Built with [MkDocs](https://www.mkdocs.org/) using the [Material theme](https://squidfunk.github.io/mkdocs-material/).

## Build journey

Scan or click the QR code to follow the [kart's build journey](https://um-driverless.github.io/kart-docs/build-journey/).

<a href="https://um-driverless.github.io/kart-docs/build-journey/">
  <img src="docs/assets/images/build-journey-qr.png" alt="QR code linking to the kart build journey" width="244" height="244">
</a>

---

## (Beta) Automated Installation
Just run `install.sh` in Linux or macOS:

## 🔧 Setup (using uv)

Install uv:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

For other installation methods, see [uv documentation](https://docs.astral.sh/uv/getting-started/installation/).

---

Clone the repo and set up the project:

```bash
git clone git@github.com:UM-Driverless/kart-docs.git
cd kart-docs
uv sync
uv run playwright install --force chrome
```

This:
- Creates a virtual environment and installs dependencies
- Downloads a headless Chrome browser for PDF export

---

## ✅ Preview locally

```bash
uv run mkdocs serve
```
You can then access the documentation in your web browser, usually at `http://127.0.0.1:8000`.

To test the build before pushing (recommended):

```bash
uv run mkdocs build --strict
# Output: site/
```

The `--strict` flag will catch errors like broken links, missing files, and invalid configuration - the same checks that run in CI.

---

## 🚀 Deployment

Deployment to GitHub Pages happens automatically via GitHub Actions when you push to the `main` branch.

The workflow will:
1. Build the documentation with `--strict` flag
2. Deploy to GitHub Pages if the build succeeds
3. Site will be available at: https://um-driverless.github.io/kart-docs/

### Manual deployment (alternative)

If needed, you can still deploy manually:

```bash
uv run mkdocs gh-deploy
```

---

## 🤖 LLM-Friendly Documentation

This documentation includes LLM-optimized formats following the [llms.txt standard](https://llmstxt.org/):

- **llms.txt**: Sitemap-style overview of all documentation pages
- **llms-full.txt**: Complete documentation content in one consumable file

These files are automatically generated during the build process and are available at:
- Live site: https://um-driverless.github.io/kart-docs/llms.txt
- Live site: https://um-driverless.github.io/kart-docs/llms-full.txt

### Manual Generation

To manually generate the LLM files:

```bash
uv run python generate_llm_files.py
```

---

## 📊 BOM Reports & Parts Management

This documentation includes advanced BOM (Bill of Materials) management features:

### Automatic Features (Built into MkDocs)

When you build the docs, the following happens automatically:

- **Searchable parts table** - Dynamically generated from all `bom.yaml` files
- **Cost summaries** - Total costs by assembly, status, and criticality
- **Filterable by** - Assembly, status, category, or search text
- **Sortable columns** - Click any column header to sort

These features are enabled by the `generate_bom_hook.py` MkDocs hook.

### Manual BOM Reports

Generate comprehensive reports (JSON + CSV):

```bash
./generate_bom_reports.sh
```

Or manually:

```bash
uv run python scripts/aggregate_bom.py --output-dir reports/bom --format both
```

**Outputs:**
- `reports/bom/bom_complete_report.json` - Complete data (costs, suppliers, status)
- `reports/bom/bom_assembly_costs.csv` - Cost breakdown by assembly
- `reports/bom/bom_all_components.csv` - All components in spreadsheet format

### Adding Components

1. Navigate to appropriate assembly folder: `docs/assembly/steering/`
2. Edit `bom.yaml` file
3. Add component using YAML format
4. Component automatically appears in searchable table on next build

See the **[BOM page](https://um-driverless.github.io/kart-docs/bom/)** for complete documentation and searchable parts table.

---

## 📟 PDF Export (optional)

PDF export is disabled by default to speed up builds. To export PDFs explicitly:

```bash
EXPORT_PDF=true uv run mkdocs build
# Outputs: site/pdf/kart-documentation.pdf
```

---


## 🗂 Branch structure

- `main` → Markdown source (all edits go here)
- `gh-pages` → Legacy deployment branch (can be deleted if using GitHub Actions)
