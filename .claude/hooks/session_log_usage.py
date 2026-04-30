#!/usr/bin/env python3
"""
Hook: SessionEnd
Purpose: Append a single JSONL line to .claude/usage-log.jsonl with the
         session's token usage and runtime metadata. Lets the user (and
         /gtr:doctor) surface expensive sessions before they snowball.

Privacy: writes only locally. Never reaches network. The log path is
gitignored.

Schema per line:
  {
    "ts": "<ISO 8601 with offset>",
    "duration_seconds": int,
    "model": str | null,
    "input_tokens": int,
    "output_tokens": int,
    "cache_creation_input_tokens": int,
    "cache_read_input_tokens": int,
    "total_tokens": int,
    "cwd": str
  }

Best-effort: any failure exits 0 silently — usage logging must never
interfere with normal session shutdown.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))
LOG_PATH = PROJECT_DIR / ".claude" / "usage-log.jsonl"


def _coerce_int(value) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    usage = data.get("usage", {}) or {}
    input_tokens = _coerce_int(usage.get("input_tokens"))
    output_tokens = _coerce_int(usage.get("output_tokens"))
    cache_creation = _coerce_int(usage.get("cache_creation_input_tokens"))
    cache_read = _coerce_int(usage.get("cache_read_input_tokens"))

    if not (input_tokens or output_tokens or cache_creation or cache_read):
        # Nothing useful to log; skip rather than emitting noise.
        sys.exit(0)

    record = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "duration_seconds": _coerce_int(data.get("duration_seconds")),
        "model": data.get("model"),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cache_creation_input_tokens": cache_creation,
        "cache_read_input_tokens": cache_read,
        "total_tokens": input_tokens + output_tokens + cache_creation + cache_read,
        "cwd": str(PROJECT_DIR),
    }

    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
