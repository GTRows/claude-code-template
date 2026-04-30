"""Shared audit logger for guard hooks.

Append-only JSONL at ``.claude/hook-audit.log`` (gitignored). Records every
guard hook block so the user (and ``/gtr:doctor``) can spot patterns —
e.g. a hook that fires constantly is probably misconfigured, and a
sudden spike in secret blocks deserves a look.

Best-effort: any I/O failure is swallowed silently so audit logging
never breaks the calling hook.

Schema per line:
    {
        "ts": "<ISO 8601 with offset>",
        "hook": str,                # e.g. "pre_guard_security"
        "action": "block",          # reserved for future "warn" entries
        "file_path": str | null,
        "reason": str
    }
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

LOG_NAME = "hook-audit.log"


def _log_path() -> Path:
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))
    return root / ".claude" / LOG_NAME


def record_block(hook: str, *, file_path: str | None, reason: str) -> None:
    """Append one block record. Never raises."""
    try:
        record = {
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "hook": hook,
            "action": "block",
            "file_path": file_path,
            "reason": reason,
        }
        path = _log_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:
        pass
    except Exception:  # noqa: BLE001 — logging must never break hooks
        pass
