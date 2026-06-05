# Tabloid

Turn a list of tabs, links, or feed items into a tiny personal newspaper PDF.

This is a minimal, local-first starter: no accounts, no tracking, just HTML-to-PDF rendering.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
tabloid --title "Sunday Paper" --output paper.html https://example.com https://www.python.org
```

Open `paper.html` in a browser and print to PDF, or use it as a base for a browser extension / cron job.

## CLI

```bash
tabloid URL [URL ...] --output paper.html --title "My Tabloid"
```

## Development

```bash
pytest
```
