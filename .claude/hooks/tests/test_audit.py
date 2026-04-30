"""Tests for the shared audit logger and end-to-end guard-hook audit flow."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

HOOKS = Path(__file__).resolve().parents[1]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_record_block_appends_jsonl(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    audit = _load("_audit_unit", HOOKS / "_audit.py")
    audit.record_block("pre_guard_x", file_path="src/foo.py", reason="bad")

    log = tmp_path / ".claude" / "hook-audit.log"
    assert log.is_file()
    rec = json.loads(log.read_text(encoding="utf-8").strip())
    assert rec["hook"] == "pre_guard_x"
    assert rec["action"] == "block"
    assert rec["file_path"] == "src/foo.py"
    assert rec["reason"] == "bad"
    assert "ts" in rec


def test_record_block_swallows_oserror(tmp_path: Path, monkeypatch):
    """If the log path is unwritable, recording must not raise."""
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    audit = _load("_audit_unit_2", HOOKS / "_audit.py")
    # Make .claude exist but mark it read-only via a file collision.
    (tmp_path / ".claude").write_text("not-a-dir", encoding="utf-8")
    # Should not raise.
    audit.record_block("pre_guard_x", file_path=None, reason="x")


def _run_guard(hook_path: Path, payload: dict, project_dir: Path) -> int:
    proc = subprocess.run(
        [sys.executable, str(hook_path)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env={**os.environ, "CLAUDE_PROJECT_DIR": str(project_dir)},
    )
    return proc.returncode


def test_pre_guard_release_files_writes_audit_on_block(tmp_path: Path):
    payload = {"tool_name": "Write", "tool_input": {"file_path": "package.json"}}
    rc = _run_guard(HOOKS / "pre_guard_release_files.py", payload, tmp_path)
    assert rc == 2
    log = tmp_path / ".claude" / "hook-audit.log"
    assert log.is_file()
    rec = json.loads(log.read_text(encoding="utf-8").strip())
    assert rec["hook"] == "pre_guard_release_files"
    assert rec["action"] == "block"
    assert "package.json" in rec["reason"]


def test_pre_guard_release_files_no_audit_when_allowed(tmp_path: Path):
    payload = {"tool_name": "Write", "tool_input": {"file_path": "src/app.py"}}
    rc = _run_guard(HOOKS / "pre_guard_release_files.py", payload, tmp_path)
    assert rc == 0
    log = tmp_path / ".claude" / "hook-audit.log"
    assert not log.exists()


def test_audit_log_appends_multiple_records(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    audit = _load("_audit_unit_3", HOOKS / "_audit.py")
    audit.record_block("h1", file_path="a", reason="r1")
    audit.record_block("h2", file_path="b", reason="r2")
    log = tmp_path / ".claude" / "hook-audit.log"
    lines = log.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0])["hook"] == "h1"
    assert json.loads(lines[1])["hook"] == "h2"
