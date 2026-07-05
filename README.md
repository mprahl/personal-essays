# Personal Essays

A small static site for publishing longform essays from Markdown.

The essays in `./essays` are the source of truth. A tiny Python build script converts them into plain HTML and CSS in `./docs`.

## Quick Start

```bash
uv sync
uv run personal-essays-build
```

Then open `docs/index.html` in a browser to preview the generated site.

## Project Layout

- `essays/`: source Markdown essays
- `personal_essays/build_site.py`: the static site generator
- `docs/`: generated site output

## Essay Metadata

Each essay in `essays/` uses a small inline header instead of YAML front matter:

```md
# Title

*Subtitle*

**Summary:** A concise description of the essay's subject and central claim.
**Author:** Matthew Prahl
**First published:** 2026-05-13
**Last updated:** 2026-05-20

---
```

`Summary` and `First published` are required. The summary is used for search metadata, feeds, and article listings. Dates must use `YYYY-MM-DD`; `Last updated` is optional.

The build also generates `sitemap.xml`, `robots.txt`, `rss.xml`, and `llms.txt`, along with canonical links, Article JSON-LD, and stable heading anchors in each HTML page.

## Rebuilding The Site

```bash
uv run personal-essays-build
```

To generate a `CNAME` file for GitHub Pages, pass your domain during the build:

```bash
uv run personal-essays-build --domain essays.example.com
```
