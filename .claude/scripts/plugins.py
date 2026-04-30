#!/usr/bin/env python3
"""
Plugin set tracker.

Records which plugins were installed when ``/gtr:setup`` ran. Lets
``/gtr:doctor`` report drift — e.g. a recommended plugin uninstalled,
a previously-installed plugin missing on a fresh clone.

Why not pin versions? Claude Code's ``claude plugin list`` does not
expose a stable, machine-readable version field across all plugin
sources. Pinning by name (presence / absence) is what we can verify
reliably; full version pinning belongs in the upstream marketplace
when it surfaces version metadata.

Usage::

    python .claude/scripts/plugins.py --pin       # write current set
    python .claude/scripts/plugins.py --check     # exit 1 on drift, print missing
    python .claude/scripts/plugins.py             # print recorded set
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


PIN_FILE = ".claude/plugin-pin.json"


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def list_installed() -> list[str]:
    """Return sorted ``name@marketplace`` strings, best-effort.

    Tries ``claude plugin list --json`` first, falls back to text parsing.
    Returns ``[]`` if the CLI is unavailable.
    """
    if shutil.which("claude") is None:
        return []

    try:
        proc = subprocess.run(
            ["claude", "plugin", "list", "--json"],
            capture_output=True,
            text=True,
            timeout=10,
            env={**os.environ, "NO_COLOR": "1"},
        )
        if proc.returncode == 0 and proc.stdout.strip():
            try:
                data = json.loads(proc.stdout)
                if isinstance(data, list):
                    return sorted({_render(item) for item in data if _render(item)})
                if isinstance(data, dict) and "plugins" in data:
                    return sorted({_render(item) for item in data["plugins"] if _render(item)})
            except (json.JSONDecodeError, TypeError):
                pass
    except (subprocess.TimeoutExpired, OSError):
        pass

    # Text fallback. Parse lines like "  plugin-name@marketplace".
    try:
        proc = subprocess.run(
            ["claude", "plugin", "list"],
            capture_output=True,
            text=True,
            timeout=10,
            env={**os.environ, "NO_COLOR": "1"},
        )
    except (subprocess.TimeoutExpired, OSError):
        return []

    if proc.returncode != 0:
        return []

    return sorted({m.group(0) for m in re.finditer(r"[\w-]+@[\w.-]+", proc.stdout)})


def _render(item) -> str | None:
    if isinstance(item, str):
        return item if "@" in item else None
    if isinstance(item, dict):
        name = item.get("name") or item.get("id")
        market = item.get("marketplace") or item.get("source")
        if name and market:
            return f"{name}@{market}"
    return None


def load_pin(root: Path) -> dict:
    f = root / PIN_FILE
    return json.loads(f.read_text(encoding="utf-8")) if f.is_file() else {}


def save_pin(root: Path, plugins: list[str]) -> Path:
    f = root / PIN_FILE
    f.parent.mkdir(parents=True, exist_ok=True)
    payload = {"plugins": plugins}
    f.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return f


def diff(installed: list[str], pinned: list[str]) -> tuple[list[str], list[str]]:
    """Return (missing_locally, extra_locally)."""
    pinned_set = set(pinned)
    installed_set = set(installed)
    return sorted(pinned_set - installed_set), sorted(installed_set - pinned_set)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pin", action="store_true", help="write current installed set to plugin-pin.json")
    parser.add_argument("--check", action="store_true", help="exit 1 if pinned plugins are missing locally")
    args = parser.parse_args()

    root = project_root()

    if args.pin:
        installed = list_installed()
        if not installed:
            print("could not query installed plugins (claude CLI unavailable or empty output)", file=sys.stderr)
            return 2
        path = save_pin(root, installed)
        print(f"wrote {path.relative_to(root)} ({len(installed)} plugins pinned)")
        return 0

    if args.check:
        pinned = load_pin(root).get("plugins", [])
        if not pinned:
            print("no plugin-pin.json found — run --pin to seed")
            return 0
        installed = list_installed()
        if not installed:
            print("cannot verify drift (claude CLI unavailable)", file=sys.stderr)
            return 0
        missing, extra = diff(installed, pinned)
        if missing:
            print("plugins pinned but missing locally:")
            for p in missing:
                print(f"  {p}")
        if extra:
            print("plugins installed but not pinned (informational):")
            for p in extra:
                print(f"  {p}")
        return 1 if missing else 0

    pinned = load_pin(root).get("plugins", [])
    if not pinned:
        print("no plugin-pin.json — run --pin to seed")
        return 0
    print("\n".join(pinned))
    return 0


if __name__ == "__main__":
    sys.exit(main())
