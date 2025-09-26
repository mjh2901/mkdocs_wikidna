# Techdox Docs

Welcome to the Techdox documentation site — your central place for guides, how-tos, and reference material about the project's Docker containers and networking setup.

This documentation is written with MkDocs and the Material theme. Use the links below to jump straight to the section you need.

---

## Quick links

- [About](about.md) — project purpose and maintainers
- Docker Containers
- Networking
  - [Overview](networking-overview.md)

## Quick start — preview locally

If you want to preview the docs locally, the easiest way is with MkDocs. If you don't have MkDocs and the Material theme installed, the minimal steps are:

```bash
# (optional) create and activate a virtualenv
python3 -m venv .venv
source .venv/bin/activate

# install mkdocs and the Material theme
pip install mkdocs mkdocs-material pymdown-extensions
```

Start a local preview server (will rebuild as you edit):

```bash
mkdocs serve
# then open http://127.0.0.1:8000 in your browser
```

Build a static site for deployment:

```bash
mkdocs build -d site
```

If you prefer using pipx instead of a virtualenv:

```bash
pipx install mkdocs
pipx inject mkdocs mkdocs-material pymdown-extensions
```

Note: there is a `docker-compose.yml` at the repository root — if you have a containerized preview service defined there, you can also use Docker Compose to run a preview. Check that file for a service named `mkdocs` or similar.

## How to edit

- Docs live in the `docs/` folder. The landing page is `docs/index.md`.
- Use Markdown for content. Front matter isn't required for basic pages.
- When ready, commit changes on a branch and open a pull request for review.

## Search tips

- Use the search box in the site header (Material theme) to quickly find pages or headings.
- Try broader keywords if an exact match doesn't show results.

## Contributing & support

Contributions are welcome. Suggested workflow:

1. Create a branch for your change.
2. Edit or add files under `docs/`.
3. Run `mkdocs serve` to preview.
4. Commit and open a pull request.

If you need help or want to report an issue, open an issue in the project's repository and tag the maintainers.

---

Thanks for reading — dive into the sections above to get started. If you'd like, I can also:

- Add a badges row (build, docs preview, license).
- Add a short changelog / version banner to this page.
- Create a minimal README with the exact commands to preview and build inside this repository.

Tell me which of those you'd like next.
