# MKDocs WikiDNA
MkDocs port of the WikiDNA network documentation templates.

This repository is a MkDocs-formatted port of the original WikiDNA content. The docs have been converted and reorganized to work with MkDocs + the Material theme.

This README is a lightweight entry point — the full content lives under `docs/` and the site is generated with MkDocs.

Quick links

- About: `docs/about.md`
- Networking overview: `docs/networking-overview.md`

Preview locally

```bash
# optional: create and activate a virtualenv
python3 -m venv .venv
source .venv/bin/activate

# install mkdocs and the Material theme
pip install mkdocs mkdocs-material pymdown-extensions

# preview locally
mkdocs serve

# build a static site
mkdocs build -d site
```

Repository notes

- Docs: `docs/`
- MkDocs config: `mkdocs.yml`
- Scripts for conversion and checks: `scripts/` (link checker, markdown fixers, rename helpers)

This repo was created by converting legacy WikiDNA content to Markdown and fixing formatting for MkDocs compatibility. For details, see `report.md`.
