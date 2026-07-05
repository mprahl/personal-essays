from __future__ import annotations

import argparse
import html
import json
import re
import shutil
from dataclasses import dataclass
from datetime import date, datetime, time, timezone
from email.utils import format_datetime
from pathlib import Path

import markdown

REPO_ROOT = Path(__file__).resolve().parent.parent
ESSAYS_DIR = REPO_ROOT / "essays"
ASSETS_DIR = REPO_ROOT / "assets"
STATIC_DIR = REPO_ROOT / "static"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "docs"

SITE_TITLE = "Matthew's Musings"
SITE_URL = "https://essays.mprahl.com"
SOCIAL_IMAGE_URL = f"{SITE_URL}/assets/social-card.png"
SITE_TAGLINE = (
    "A collection of essays, personal reflections, notes, and books about what it means to be "
    "human in the age of AI, musings on faith and early Christianity, general contemplations, "
    "and whatever else I'm interested in at the moment."
)
HOME_EYEBROW = "Writings by Matthew Prahl"

CSS = """
:root {
  --bg: #e5eee3;
  --surface: #f6f8f2;
  --surface-strong: #fcfdf9;
  --text: #223028;
  --muted: #5f685f;
  --border: #d4cec2;
  --accent: #6f8671;
  --accent-hover: #5a6f5c;
  --accent-soft: #d7e0d2;
  --accent-warm: #c79a7c;
  --code-bg: #f2ece2;
  --shadow: rgba(34, 48, 40, 0.08);
  --ui-font: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --body-font: Georgia, Cambria, "Times New Roman", Times, serif;
}

* {
  box-sizing: border-box;
}

html {
  font-size: 18px;
}

body {
  margin: 0;
  color: var(--text);
  background: var(--bg);
  font-family: var(--body-font);
  line-height: 1.72;
}

a {
  color: var(--accent);
  text-decoration-thickness: 1px;
  text-underline-offset: 0.14em;
}

a:hover {
  color: var(--accent-hover);
}

img {
  max-width: 100%;
}

.site-shell {
  width: min(1100px, calc(100% - 2rem));
  margin: 0 auto;
}

.site-header {
  padding: 0 0 2rem;
}

.site-masthead {
  margin-bottom: 1.6rem;
  background: linear-gradient(180deg, #6f8671 0%, #5f755f 100%);
  box-shadow: inset 0 -1px 0 rgba(251, 248, 242, 0.16);
}

.site-masthead .site-shell {
  display: flex;
  align-items: center;
  min-height: 3rem;
}

.site-header .site-shell {
  padding-bottom: 0.5rem;
}

.site-header h1 {
  margin-top: 1.6rem;
  color: var(--text);
}

.site-masthead .eyebrow {
  display: block;
  margin-bottom: 0;
  color: #f4f7f1;
  line-height: 1;
  transform: translateY(2px);
}

.site-masthead .eyebrow-link {
  color: inherit;
  text-decoration: none;
}

.site-masthead .eyebrow-link:hover {
  color: inherit;
  text-decoration: underline;
}

.site-header .tagline {
  max-width: 50rem;
  color: var(--muted);
}

.site-header h1,
.essay-header h1 {
  margin: 0;
  font-size: clamp(2.4rem, 5vw, 3.8rem);
  line-height: 1.05;
  letter-spacing: -0.02em;
}

.eyebrow,
.nav-link,
.essay-meta,
.footer-note,
.tile-link {
  font-family: var(--ui-font);
}

.eyebrow {
  margin-bottom: 0.85rem;
  color: var(--muted);
  font-size: 0.78rem;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.tagline {
  max-width: 50rem;
  margin: 1rem 0 0;
  color: var(--muted);
  font-size: 1.05rem;
  line-height: 1.8;
}

.home-grid {
  padding: 0 0 4rem;
}

.home-section h2 {
  margin-top: 0;
  font-size: 1rem;
  font-family: var(--ui-font);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--muted);
}

.tile p:last-child,
.essay-body > *:last-child {
  margin-bottom: 0;
}

.essay-list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1.1rem;
}

.tile {
  display: flex;
  flex-direction: column;
  padding: 1.4rem;
  background: var(--surface-strong);
  border: 1px solid var(--border);
  border-radius: 16px;
  text-decoration: none;
  box-shadow: 0 8px 24px rgba(36, 28, 24, 0.05);
  transition: transform 150ms ease, box-shadow 150ms ease, border-color 150ms ease,
    background-color 150ms ease;
}

.tile:hover {
  transform: translateY(-2px);
  background: var(--surface);
  border-color: var(--accent-soft);
  box-shadow: 0 14px 32px rgba(36, 28, 24, 0.08);
}

.tile h3 {
  margin: 0;
  font-size: 1.35rem;
  color: var(--text);
}

.tile-subtitle {
  margin: 0.5rem 0 0;
  color: var(--muted);
  font-style: italic;
}

.tile-meta {
  margin: 0;
  color: var(--muted);
  font-size: 0.82rem;
}

.tile-summary {
  margin: 0.9rem 0 0;
  color: var(--text);
}

.tile-footer {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 1rem;
  margin-top: auto;
  padding-top: 1.15rem;
}

.tile-link {
  display: inline-block;
  color: var(--accent);
  font-size: 0.88rem;
  font-weight: 600;
  white-space: nowrap;
}

.essay-page {
  padding: 1rem 0 4rem;
}

.essay-nav {
  margin-bottom: 2rem;
}

.nav-link {
  color: var(--muted);
  font-size: 0.92rem;
  text-decoration: none;
}

.nav-link:hover {
  color: var(--accent);
}

.essay-card {
  width: min(100%, 88ch);
  margin: 0 auto;
  padding: 2.5rem min(6vw, 3rem);
  background: var(--surface-strong);
  border: 1px solid var(--border);
  border-radius: 22px;
  box-shadow: 0 14px 38px var(--shadow);
}

.essay-header {
  padding-bottom: 1.75rem;
  margin-bottom: 2rem;
  border-bottom: 1px solid var(--border);
}

.essay-subtitle {
  margin: 1rem 0 0;
  color: var(--muted);
  font-size: 1.1rem;
  font-style: italic;
}

.essay-meta {
  margin-top: 1rem;
  color: var(--muted);
  font-size: 0.92rem;
}

.essay-body h2,
.essay-body h3,
.essay-body h4 {
  font-family: var(--ui-font);
  line-height: 1.25;
  letter-spacing: -0.01em;
}

.essay-body h2 {
  margin-top: 2.4rem;
  margin-bottom: 0.8rem;
  font-size: 1.45rem;
}

.essay-body h3 {
  margin-top: 1.9rem;
  margin-bottom: 0.55rem;
  font-size: 1.12rem;
}

.essay-body p,
.essay-body ul,
.essay-body ol,
.essay-body blockquote {
  margin: 1rem 0;
}

.essay-body blockquote {
  padding-left: 1rem;
  border-left: 3px solid var(--accent-warm);
  color: var(--muted);
}

.essay-body hr {
  margin: 2.2rem 0;
  border: 0;
  border-top: 1px solid var(--border);
}

.essay-body code {
  padding: 0.1rem 0.28rem;
  background: var(--code-bg);
  border-radius: 4px;
  font-size: 0.9em;
}

.essay-body pre {
  overflow-x: auto;
  padding: 1rem;
  background: var(--code-bg);
  border-radius: 10px;
}

.essay-body pre code {
  padding: 0;
  background: transparent;
}

.footer-note {
  margin-top: 2rem;
  color: var(--muted);
  font-size: 0.86rem;
}

@media (max-width: 900px) {
  .home-grid {
    padding-bottom: 3rem;
  }

  .essay-list {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  html {
    font-size: 17px;
  }

  .site-header {
    padding-bottom: 1.6rem;
  }

  .essay-card {
    padding: 1.6rem 1.2rem;
    border-radius: 18px;
  }
}
""".strip()


@dataclass(slots=True)
class Essay:
    title: str
    subtitle: str | None
    summary: str
    author: str | None
    first_published: date
    last_updated: date | None
    slug: str
    source_path: Path
    body_markdown: str
    body_html: str


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the static essay site.")
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory where the generated site will be written.",
    )
    parser.add_argument(
        "--domain",
        help="Optional custom domain. When set, writes a CNAME file for GitHub Pages.",
    )
    args = parser.parse_args()

    output_dir = Path(args.output).resolve()
    build_site(output_dir=output_dir, domain=args.domain)
    print(f"Built site into {output_dir}")


def build_site(output_dir: Path, domain: str | None = None) -> None:
    essays = load_essays()
    if not essays:
        raise SystemExit(f"No essays found in {ESSAYS_DIR}")

    if output_dir.exists():
        shutil.rmtree(output_dir)

    (output_dir / "assets").mkdir(parents=True, exist_ok=True)
    (output_dir / "essays").mkdir(parents=True, exist_ok=True)

    if STATIC_DIR.exists():
      shutil.copytree(STATIC_DIR, output_dir, dirs_exist_ok=True)

    (output_dir / "assets" / "site.css").write_text(CSS + "\n", encoding="utf-8")
    shutil.copy2(ASSETS_DIR / "social-card.png", output_dir / "assets" / "social-card.png")
    (output_dir / ".nojekyll").write_text("", encoding="utf-8")
    (output_dir / "index.html").write_text(render_homepage(essays), encoding="utf-8")
    (output_dir / "sitemap.xml").write_text(render_sitemap(essays), encoding="utf-8")
    (output_dir / "robots.txt").write_text(render_robots(), encoding="utf-8")
    (output_dir / "rss.xml").write_text(render_rss(essays), encoding="utf-8")
    (output_dir / "llms.txt").write_text(render_llms(essays), encoding="utf-8")

    if domain:
        normalized_domain = domain.strip()
        if not normalized_domain:
            raise SystemExit("Custom domain cannot be empty.")
        (output_dir / "CNAME").write_text(normalized_domain + "\n", encoding="utf-8")

    for essay in essays:
        article_path = output_dir / "essays" / f"{essay.slug}.html"
        article_path.write_text(render_essay_page(essay), encoding="utf-8")


def load_essays() -> list[Essay]:
    essays = [parse_essay(path) for path in ESSAYS_DIR.glob("*.md")]
    return sorted(
        essays,
        key=lambda essay: (-essay.first_published.toordinal(), essay.source_path.as_posix()),
    )


def parse_essay(path: Path) -> Essay:
    lines = path.read_text(encoding="utf-8").splitlines()
    source_path = path.relative_to(REPO_ROOT)
    index = skip_blank_lines(lines, 0)

    if index >= len(lines) or not lines[index].startswith("# "):
        raise SystemExit(f"{path} must begin with an H1 title.")

    title = lines[index][2:].strip()
    index = skip_blank_lines(lines, index + 1)

    subtitle = None
    if index < len(lines):
        stripped = lines[index].strip()
        subtitle_match = re.fullmatch(r"\*(?!\*)(.+?)\*", stripped)
        if subtitle_match:
            subtitle = subtitle_match.group(1).strip()
            index = skip_blank_lines(lines, index + 1)

    summary = None
    if index < len(lines):
      stripped = lines[index].strip()
      summary_match = re.fullmatch(r"\*\*Summary:\*\*\s*(.+)", stripped)
      if summary_match:
        summary = summary_match.group(1).strip()
        index = skip_blank_lines(lines, index + 1)

    if summary is None:
      raise SystemExit(f"{path} must include a **Summary:** line in the header.")

    author = None
    if index < len(lines):
        stripped = lines[index].strip()
        author_match = re.fullmatch(r"\*\*Author:\*\*\s*(.+)", stripped)
        if author_match:
            author = author_match.group(1).strip()
            index = skip_blank_lines(lines, index + 1)

    first_published = None
    if index < len(lines):
        stripped = lines[index].strip()
        first_published_match = re.fullmatch(r"\*\*First published:\*\*\s*(.+)", stripped)
        if first_published_match:
            first_published = parse_iso_date(
                first_published_match.group(1).strip(),
                path=path,
                label="First published",
            )
            index = skip_blank_lines(lines, index + 1)

    if first_published is None:
        raise SystemExit(f"{path} must include a **First published:** line in the header.")

    last_updated = None
    if index < len(lines):
        stripped = lines[index].strip()
        last_updated_match = re.fullmatch(r"\*\*Last updated:\*\*\s*(.+)", stripped)
        if last_updated_match:
            last_updated = parse_iso_date(
                last_updated_match.group(1).strip(),
                path=path,
                label="Last updated",
            )
            index = skip_blank_lines(lines, index + 1)

    if last_updated is not None and last_updated < first_published:
        raise SystemExit(f"{path} has a last updated date earlier than its first published date.")

    if index < len(lines) and lines[index].strip() == "---":
        index = skip_blank_lines(lines, index + 1)

    body_markdown = "\n".join(lines[index:]).strip()
    body_html = markdown.Markdown(extensions=["extra", "smarty", "toc"]).convert(body_markdown)
    body_html = rewrite_internal_essay_links(body_html, source_path=source_path)

    return Essay(
        title=title,
        subtitle=subtitle,
        summary=summary,
        author=author,
        first_published=first_published,
        last_updated=last_updated,
        slug=slugify(path.stem),
        source_path=source_path,
        body_markdown=body_markdown,
        body_html=body_html,
    )


def skip_blank_lines(lines: list[str], index: int) -> int:
    while index < len(lines) and not lines[index].strip():
        index += 1
    return index


def parse_iso_date(value: str, *, path: Path, label: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise SystemExit(f"{path} has an invalid {label} date {value!r}; use YYYY-MM-DD.") from exc


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "essay"


def rewrite_internal_essay_links(body_html: str, *, source_path: Path) -> str:
    def replace(match: re.Match[str]) -> str:
        href = html.unescape(match.group(1))
        if re.match(r"^[a-z]+:", href, flags=re.IGNORECASE) or href.startswith(("/", "#")):
            return match.group(0)

        path_part, separator, suffix = href.partition("#")
        if not path_part.endswith(".md"):
            return match.group(0)

        target_path = (source_path.parent / path_part).resolve()
        try:
            target_path.relative_to(ESSAYS_DIR)
        except ValueError:
            return match.group(0)

        rewritten = f'{slugify(target_path.stem)}.html'
        if separator:
            rewritten += f"#{suffix}"
        return f'href="{html.escape(rewritten, quote=True)}"'

    return re.sub(r'href="([^"]+)"', replace, body_html)


def strip_markdown(text: str) -> str:
    cleaned = re.sub(r"\[(.*?)\]\((.*?)\)", r"\1", text)
    cleaned = re.sub(r"[*_`>#]", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def render_inline_markdown(text: str) -> str:
    rendered = markdown.Markdown(extensions=["smarty"]).convert(text.strip())
    if rendered.startswith("<p>") and rendered.endswith("</p>"):
        return rendered[3:-4]
    return rendered


def format_display_date(value: date) -> str:
    return f"{value.strftime('%B')} {value.day}, {value.year}"


def essay_url(essay: Essay) -> str:
  return f"{SITE_URL}/essays/{essay.slug}.html"


def essay_modified_date(essay: Essay) -> date:
  return essay.last_updated or essay.first_published


def format_rss_date(value: date) -> str:
  timestamp = datetime.combine(value, time.min, tzinfo=timezone.utc)
  return format_datetime(timestamp, usegmt=True)


def render_sitemap(essays: list[Essay]) -> str:
  latest_modified = max(essay_modified_date(essay) for essay in essays)
  entries = [
    f"""  <url>
  <loc>{SITE_URL}/</loc>
  <lastmod>{latest_modified.isoformat()}</lastmod>
  </url>"""
  ]
  entries.extend(
    f"""  <url>
  <loc>{html.escape(essay_url(essay))}</loc>
  <lastmod>{essay_modified_date(essay).isoformat()}</lastmod>
  </url>"""
    for essay in essays
  )
  return """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{entries}
</urlset>
""".format(entries="\n".join(entries))


def render_robots() -> str:
  return f"""User-agent: *
Allow: /

Sitemap: {SITE_URL}/sitemap.xml
"""


def render_llms(essays: list[Essay]) -> str:
  articles = "\n\n".join(
    f"- [{strip_markdown(essay.title)}]({essay_url(essay)})\n  {essay.summary}" for essay in essays
  )
  return f"""# {SITE_TITLE}

> Essays by Matthew Prahl about early Christianity, process theology, humanity in the age of AI, and related subjects.

Canonical site: {SITE_URL}/

## Articles

{articles}
"""


def render_rss(essays: list[Essay]) -> str:
  latest_modified = max(essay_modified_date(essay) for essay in essays)
  items = "\n".join(
    f"""    <item>
    <title>{html.escape(strip_markdown(essay.title))}</title>
    <link>{html.escape(essay_url(essay))}</link>
    <guid isPermaLink="true">{html.escape(essay_url(essay))}</guid>
    <pubDate>{format_rss_date(essay.first_published)}</pubDate>
    <description>{html.escape(essay.summary)}</description>
  </item>"""
    for essay in essays
  )
  return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
  <title>{html.escape(SITE_TITLE)}</title>
  <link>{SITE_URL}/</link>
  <description>{html.escape(SITE_TAGLINE)}</description>
  <language>en</language>
  <lastBuildDate>{format_rss_date(latest_modified)}</lastBuildDate>
  <atom:link href="{SITE_URL}/rss.xml" rel="self" type="application/rss+xml" />
{items}
  </channel>
</rss>
"""


def render_article_json_ld(essay: Essay) -> str:
  data: dict[str, object] = {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": strip_markdown(essay.title),
    "description": essay.summary,
    "datePublished": essay.first_published.isoformat(),
    "dateModified": essay_modified_date(essay).isoformat(),
    "mainEntityOfPage": {"@type": "WebPage", "@id": essay_url(essay)},
    "url": essay_url(essay),
    "inLanguage": "en",
    "isPartOf": {"@type": "WebSite", "name": SITE_TITLE, "url": f"{SITE_URL}/"},
  }
  if essay.subtitle:
    data["alternativeHeadline"] = strip_markdown(essay.subtitle)
  if essay.author:
    data["author"] = {"@type": "Person", "name": essay.author}

  return json.dumps(data, ensure_ascii=False, indent=2).replace("</", "<\\/")


def render_social_metadata(*, title: str, description: str, url: str, content_type: str) -> str:
    return f"""<meta property="og:title" content="{html.escape(title, quote=True)}">
    <meta property="og:description" content="{html.escape(description, quote=True)}">
    <meta property="og:url" content="{html.escape(url, quote=True)}">
    <meta property="og:type" content="{html.escape(content_type, quote=True)}">
    <meta property="og:site_name" content="{html.escape(SITE_TITLE, quote=True)}">
    <meta property="og:image" content="{SOCIAL_IMAGE_URL}">
    <meta property="og:image:secure_url" content="{SOCIAL_IMAGE_URL}">
    <meta property="og:image:type" content="image/png">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta property="og:image:alt" content="{html.escape(SITE_TITLE, quote=True)}">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{html.escape(title, quote=True)}">
    <meta name="twitter:description" content="{html.escape(description, quote=True)}">
    <meta name="twitter:image" content="{SOCIAL_IMAGE_URL}">
    <meta name="twitter:image:alt" content="{html.escape(SITE_TITLE, quote=True)}">"""


def render_homepage(essays: list[Essay]) -> str:
    tiles = "\n".join(render_tile(essay) for essay in essays)
    social_metadata = render_social_metadata(
        title=SITE_TITLE,
        description=SITE_TAGLINE,
        url=f"{SITE_URL}/",
        content_type="website",
    )

    content = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{html.escape(SITE_TITLE)}</title>
    <meta name="description" content="{html.escape(SITE_TAGLINE)}">
    {social_metadata}
    <link rel="canonical" href="{SITE_URL}/">
    <link rel="alternate" type="application/rss+xml" title="{html.escape(SITE_TITLE)}" href="{SITE_URL}/rss.xml">
    <link rel="stylesheet" href="assets/site.css">
  </head>
  <body>
    <header class="site-header">
      <div class="site-masthead">
        <div class="site-shell">
          <div class="eyebrow"><a class="eyebrow-link" href="/">{html.escape(HOME_EYEBROW)}</a></div>
        </div>
      </div>
      <div class="site-shell">
        <h1>{html.escape(SITE_TITLE)}</h1>
        <p class="tagline">{html.escape(SITE_TAGLINE)}</p>
      </div>
    </header>
    <main class="site-shell home-grid">
      <section class="home-section">
        <h2>Articles</h2>
        <div class="essay-list">
          {tiles}
        </div>
      </section>
    </main>
  </body>
</html>
"""
    return content


def render_tile(essay: Essay) -> str:
    title = render_inline_markdown(essay.title)
    subtitle = f'<p class="tile-subtitle">{render_inline_markdown(essay.subtitle)}</p>' if essay.subtitle else ""
    published = html.escape(format_display_date(essay.first_published))
    return f"""<a class="tile" href="essays/{essay.slug}.html">
  <h3>{title}</h3>
  {subtitle}
  <p class="tile-summary">{html.escape(essay.summary)}</p>
  <div class="tile-footer">
    <span class="tile-meta">Published <time datetime="{essay.first_published.isoformat()}">{published}</time></span>
    <span class="tile-link">Read article</span>
  </div>
</a>"""


def render_essay_page(essay: Essay) -> str:
    display_title = render_inline_markdown(essay.title)
    subtitle = f'<p class="essay-subtitle">{render_inline_markdown(essay.subtitle)}</p>' if essay.subtitle else ""
    plain_title = strip_markdown(essay.title)
    meta_parts = []
    if essay.author:
        meta_parts.append(f"By {html.escape(essay.author)}")

    meta_parts.append(
        "First published "
        f'<time datetime="{essay.first_published.isoformat()}">{html.escape(format_display_date(essay.first_published))}</time>'
    )

    if essay.last_updated is not None:
        meta_parts.append(
            "Last updated "
            f'<time datetime="{essay.last_updated.isoformat()}">{html.escape(format_display_date(essay.last_updated))}</time>'
        )

    essay_meta = " &middot; ".join(meta_parts)
    article_json_ld = render_article_json_ld(essay)
    social_metadata = render_social_metadata(
        title=plain_title,
        description=essay.summary,
        url=essay_url(essay),
        content_type="article",
    )

    content = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{html.escape(plain_title)} | {html.escape(SITE_TITLE)}</title>
    <meta name="description" content="{html.escape(essay.summary)}">
    {social_metadata}
    <meta property="article:published_time" content="{essay.first_published.isoformat()}">
    <meta property="article:modified_time" content="{essay_modified_date(essay).isoformat()}">
    <link rel="canonical" href="{essay_url(essay)}">
    <link rel="alternate" type="application/rss+xml" title="{html.escape(SITE_TITLE)}" href="{SITE_URL}/rss.xml">
    <link rel="stylesheet" href="../assets/site.css">
    <script type="application/ld+json">
  {article_json_ld}
    </script>
  </head>
  <body>
    <header class="site-header">
      <div class="site-masthead">
        <div class="site-shell">
          <div class="eyebrow"><a class="eyebrow-link" href="/">{html.escape(HOME_EYEBROW)}</a></div>
        </div>
      </div>
    </header>
    <main class="site-shell essay-page">
      <article class="essay-card">
        <header class="essay-header">
          <h1>{display_title}</h1>
          {subtitle}
          <div class="essay-meta">{essay_meta}</div>
        </header>
        <div class="essay-body">
          {essay.body_html}
        </div>
      </article>
    </main>
  </body>
</html>
"""
    return content


if __name__ == "__main__":
    main()
