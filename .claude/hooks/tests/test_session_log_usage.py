"""Tests for the SessionEnd usage logger hook."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).resolve().parents[1] / "session_log_usage.py"


def _run(stdin_payload: dict, project_dir: Path) -> tuple[int, str, str]:
    proc = subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(stdin_payload),
        capture_output=True,
        text=True,
        env={**os.environ, "CLAUDE_PROJECT_DIR": str(project_dir)},
    )
    return proc.returncode, proc.stdout, proc.stderr


def test_writes_jsonl_record(tmp_path: Path):
    payload = {
        "duration_seconds": 42,
        "model": "claude-opus-4-7",
        "usage": {
            "input_tokens": 1000,
            "output_tokens": 200,
            "cache_creation_input_tokens": 50,
            "cache_read_input_tokens": 9000,
        },
    }
    rc, _out, _err = _run(payload, tmp_path)
    assert rc == 0

    log = tmp_path / ".claude" / "usage-log.jsonl"
    assert log.is_file()
    rec = json.loads(log.read_text(encoding="utf-8").strip())
    assert rec["input_tokens"] == 1000
    assert rec["output_tokens"] == 200
    assert rec["total_tokens"] == 1000 + 200 + 50 + 9000
    assert rec["model"] == "claude-opus-4-7"
    assert "ts" in rec


def test_appends_multiple_runs(tmp_path: Path):
    p = {"usage": {"input_tokens": 10, "output_tokens": 5}}
    _run(p, tmp_path)
    _run(p, tmp_path)
    log = tmp_path / ".claude" / "usage-log.jsonl"
    lines = log.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2


def test_skips_when_no_usage(tmp_path: Path):
    rc, _out, _err = _run({"duration_seconds": 5}, tmp_path)
    assert rc == 0
    assert not (tmp_path / ".claude" / "usage-log.jsonl").exists()


def test_invalid_stdin_exits_zero(tmp_path: Path):
    proc = subprocess.run(
        [sys.executable, str(HOOK)],
        input="not json",
        capture_output=True,
        text=True,
        env={**os.environ, "CLAUDE_PROJECT_DIR": str(tmp_path)},
    )
    assert proc.returncode == 0
    assert not (tmp_path / ".claude" / "usage-log.jsonl").exists()


def test_handles_missing_keys_gracefully(tmp_path: Path):
    payload = {"usage": {"input_tokens": "bogus", "output_tokens": 7}}
    rc, _out, _err = _run(payload, tmp_path)
    assert rc == 0
    log = tmp_path / ".claude" / "usage-log.jsonl"
    rec = json.loads(log.read_text(encoding="utf-8").strip())
    assert rec["input_tokens"] == 0
    assert rec["output_tokens"] == 7
