from pathlib import Path

from tabloid.main import Article, build_newspaper, reading_minutes, render_html


def test_render_html_contains_title_and_url():
    html = render_html([Article("https://example.com", "Example", "A short article.")], "My Paper")
    assert "My Paper" in html
    assert "Example" in html
    assert "https://example.com" in html
    assert "Table of Contents" in html


def test_reading_minutes_minimum_one():
    assert reading_minutes("") == 1
    assert reading_minutes("hello world") == 1


def test_build_newspaper_with_failed_fetch(tmp_path: Path):
    output = tmp_path / "paper.html"
    build_newspaper(["not-a-real-url"], output, "Offline Paper")
    assert output.exists()
    assert "Offline Paper" in output.read_text(encoding="utf-8")
