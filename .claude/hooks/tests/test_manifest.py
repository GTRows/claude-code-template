"""Tests for the template manifest script."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"


def _load_manifest_module():
    spec = importlib.util.spec_from_file_location(
        "manifest", SCRIPTS_DIR / "manifest.py"
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules["manifest"] = mod
    spec.loader.exec_module(mod)
    return mod


manifest = _load_manifest_module()


def test_sha256_hashes_file(tmp_path: Path):
    f = tmp_path / "a.txt"
    f.write_bytes(b"hello")
    digest = manifest.sha256(f)
    assert digest == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"


def test_collect_files_picks_up_template_paths(tmp_path: Path):
    (tmp_path / ".claude" / "commands").mkdir(parents=True)
    (tmp_path / "CLAUDE.md").write_text("ok", encoding="utf-8")
    (tmp_path / ".claude" / "commands" / "x.md").write_text("ok", encoding="utf-8")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("ok", encoding="utf-8")  # not template-owned

    found = manifest.collect_files(tmp_path)
    paths = {p.relative_to(tmp_path).as_posix() for p in found}
    assert "CLAUDE.md" in paths
    assert ".claude/commands/x.md" in paths
    assert "src/app.py" not in paths


def test_build_manifest_shape(tmp_path: Path):
    (tmp_path / ".claude").mkdir()
    (tmp_path / ".claude" / "VERSION").write_text("1.2.3", encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text("body", encoding="utf-8")

    m = manifest.build_manifest(tmp_path)
    assert m["version"] == "1.2.3"
    assert "CLAUDE.md" in m["files"]
    assert len(m["files"]["CLAUDE.md"]) == 64  # sha256 hex length


def test_diff_against_existing_finds_drift(tmp_path: Path):
    existing = {"version": "1.0.0", "files": {"a.md": "old-sha", "b.md": "same-sha"}}
    (tmp_path / ".claude").mkdir()
    (tmp_path / ".claude" / ".template-manifest.json").write_text(
        json.dumps(existing), encoding="utf-8"
    )

    current = {"files": {"a.md": "new-sha", "b.md": "same-sha"}}
    drift = manifest.diff_against_existing(tmp_path, current)
    assert drift == ["a.md"]


def test_load_existing_returns_none_when_missing(tmp_path: Path):
    (tmp_path / ".claude").mkdir()
    assert manifest.load_existing(tmp_path) is None


def test_read_version_defaults_when_missing(tmp_path: Path):
    assert manifest.read_version(tmp_path) == "0.0.0"


def test_write_manifest_is_atomic_and_leaves_no_temp(tmp_path: Path):
    (tmp_path / ".claude").mkdir()
    payload = {"version": "1.0.0", "files": {"a": "b"}}
    written = manifest.write_manifest(tmp_path, payload)
    assert written.exists()
    assert json.loads(written.read_text(encoding="utf-8")) == payload
    leftover = list((tmp_path / ".claude").glob(".template-manifest.*.json.tmp"))
    assert leftover == []


def test_write_manifest_overwrites_existing(tmp_path: Path):
    (tmp_path / ".claude").mkdir()
    target = tmp_path / ".claude" / ".template-manifest.json"
    target.write_text('{"old": true}', encoding="utf-8")
    new_payload = {"version": "2.0.0", "files": {}}
    manifest.write_manifest(tmp_path, new_payload)
    assert json.loads(target.read_text(encoding="utf-8")) == new_payload
