from __future__ import annotations

import argparse
import html
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import requests
from bs4 import BeautifulSoup


@dataclass(frozen=True)
class Article:
    url: str
    title: str
    excerpt: str


def fetch_article(url: str, timeout: float = 8.0) -> Article:
    """Fetch a URL and return a small, printable article summary."""
    try:
        response = requests.get(url, timeout=timeout, headers={"User-Agent": "Tabloid/0.1"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        title = (soup.title.string or url).strip() if soup.title else url
        paragraphs = " ".join(p.get_text(" ", strip=True) for p in soup.find_all("p")[:4])
        excerpt = paragraphs or soup.get_text(" ", strip=True)[:500] or "No preview available."
        return Article(url=url, title=title, excerpt=excerpt[:1200])
    except Exception as exc:  # network-friendly CLI: keep going
        return Article(url=url, title=url, excerpt=f"Could not fetch article: {exc}")


def reading_minutes(text: str) -> int:
    return max(1, round(len(text.split()) / 220))


def render_html(articles: Iterable[Article], title: str = "Tabloid") -> str:
    articles = list(articles)
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    items = []
    toc = []

    for index, article in enumerate(articles, start=1):
        anchor = f"story-{index}"
        safe_title = html.escape(article.title)
        safe_url = html.escape(article.url)
        safe_excerpt = html.escape(article.excerpt)
        minutes = reading_minutes(article.excerpt)
        toc.append(f'<li><a href="#{anchor}">{safe_title}</a> <small>{minutes} min</small></li>')
        items.append(
            f'<article id="{anchor}"><h2>{safe_title}</h2>'
            f'<p class="meta">{minutes} min · <a href="{safe_url}">{safe_url}</a></p>'
            f'<p>{safe_excerpt}</p></article>'
        )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    body {{ max-width: 780px; margin: 3rem auto; padding: 0 1rem; font: 18px/1.55 Georgia, serif; color: #111; }}
    header {{ border-bottom: 3px double #111; margin-bottom: 2rem; }}
    h1 {{ font-size: 3rem; margin: 0; }}
    h2 {{ break-after: avoid; }}
    .meta, small {{ color: #555; font-family: system-ui, sans-serif; font-size: .85rem; }}
    article {{ border-top: 1px solid #bbb; margin-top: 2rem; padding-top: 1rem; }}
    @media print {{ body {{ margin: 0.5in auto; }} a {{ color: inherit; }} }}
  </style>
</head>
<body>
  <header><h1>{html.escape(title)}</h1><p class="meta">Generated {generated}</p></header>
  <h2>Table of Contents</h2>
  <ol>{''.join(toc)}</ol>
  {''.join(items)}
</body>
</html>
"""


def build_newspaper(urls: list[str], output: Path, title: str) -> Path:
    articles = [fetch_article(url) for url in urls]
    output.write_text(render_html(articles, title), encoding="utf-8")
    return output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Turn tabs and links into a printable personal newspaper.")
    parser.add_argument("urls", nargs="+", help="URLs to include")
    parser.add_argument("-o", "--output", type=Path, default=Path("tabloid.html"), help="Output HTML file")
    parser.add_argument("-t", "--title", default="Tabloid", help="Newspaper title")
    args = parser.parse_args(argv)

    path = build_newspaper(args.urls, args.output, args.title)
    print(f"Wrote {path}. Open it and print to PDF.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
