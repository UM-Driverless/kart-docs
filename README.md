# kart-docs

Documentation for the Formula Student KART project.

This site is built with [MkDocs](https://www.mkdocs.org/) using the [Material theme](https://squidfunk.github.io/mkdocs-material/).

📘 Live site: <https://um-driverless.github.io/kart-docs/>
🧠 Main source: [Notion Kart Documentation](https://www.notion.so/KART-1b378747314380acb23ee354a4a4c4c7)

---

## 🔧 Setup

```bash
git clone git@github.com:UM-Driverless/kart-docs.git
cd kart-docs
./dev.sh
```

This script:
- Sets up a Python virtual environment using `uv`
- Installs MkDocs + Material theme
- Launches a local preview server at `http://127.0.0.1:8000`

---

## 🚀 Deployment

To deploy to GitHub Pages:

```bash
mkdocs gh-deploy
```

Make sure GitHub Pages is enabled in the repo settings → Pages → Source: `gh-pages` branch.

---
