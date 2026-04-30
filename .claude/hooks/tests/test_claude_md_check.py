"""Tests for the CLAUDE.md drift checker."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


checker = _load("claude_md_check", SCRIPTS / "claude_md_check.py")


def test_parse_sections_extracts_h2_blocks():
    text = "# Title\n\n## A\n\nbody-a\n\n## B\nbody-b\n"
    s = checker.parse_sections(text)
    assert set(s.keys()) == {"A", "B"}
    assert s["A"] == "body-a"
    assert s["B"] == "body-b"


def test_is_placeholder_recognises_html_comments_only():
    assert checker.is_placeholder("")
    assert checker.is_placeholder("<!-- nothing here -->\n")
    assert checker.is_placeholder("\n  \n  <!-- todo -->")
    assert not checker.is_placeholder("real content")
    assert not checker.is_placeholder("<!-- comment -->\nactual line")


def test_check_reports_missing_when_file_absent(tmp_path):
    result = checker.check(tmp_path / "CLAUDE.md")
    assert not result["found"]
    assert "Available commands" in result["missing"]


def test_check_reports_placeholders(tmp_path):
    md = tmp_path / "CLAUDE.md"
    md.write_text(
        "# Test\n\n"
        "## Available commands\n\n"
        "<!-- TODO -->\n\n"
        "## Project Overview\n\n"
        "Real description.\n",
        encoding="utf-8",
    )
    result = checker.check(md)
    assert result["found"]
    assert "Available commands" in result["placeholders"]
    assert "Project Overview" not in result["placeholders"]


def test_check_extras_listed_but_not_flagged(tmp_path):
    md = tmp_path / "CLAUDE.md"
    md.write_text(
        "# Test\n\n## Custom Section\nx\n\n## Project Overview\nReal.\n",
        encoding="utf-8",
    )
    result = checker.check(md)
    assert "Custom Section" in result["extras"]
