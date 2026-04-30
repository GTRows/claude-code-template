#!/usr/bin/env python3
"""
Versioned migration runner for the claude-code-template.

Discovers per-version migration modules under
``.claude/scripts/migrations/`` and applies any whose target version is
strictly greater than the project's current ``.claude/VERSION`` and less
than or equal to the upstream target version supplied on the command line
(or read from a fresh ``.claude/VERSION`` if no flag is given).

Each migration module exports two functions:

    def plan(root: Path) -> list[Action]
    def apply(root: Path, actions: list[Action]) -> None

``plan`` is pure and inspects the filesystem to decide what needs to
change. ``apply`` performs the changes. Splitting them lets ``--check``
preview without mutating the repo.

Idempotent: each ``plan`` returns an empty list when the target state is
already in place.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Callable

# ---------- Versioning ----------

VERSION_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)(?:-[A-Za-z0-9.\-]+)?$")


def parse_version(s: str) -> tuple[int, int, int]:
    m = VERSION_RE.match(s.strip())
    if not m:
        raise ValueError(f"invalid version {s!r}")
    return tuple(int(p) for p in m.groups())  # type: ignore[return-value]


def read_version(root: Path) -> str:
    f = root / ".claude" / "VERSION"
    return f.read_text(encoding="utf-8").strip() if f.is_file() else "0.0.0"


# ---------- Action shape ----------


@dataclass
class Action:
    """Single migration action, JSON-serialisable for --check output."""

    kind: str  # one of: move, delete, write, append, replace_in_file, note
    src: str | None = None
    dst: str | None = None
    payload: str | None = None
    note: str | None = None

    def to_json(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None}


# ---------- Discovery ----------


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def migrations_dir() -> Path:
    return Path(__file__).resolve().parent / "migrations"


def discover() -> list[tuple[tuple[int, int, int], Path]]:
    """Return [(version_tuple, module_path), ...] sorted ascending."""
    out: list[tuple[tuple[int, int, int], Path]] = []
    if not migrations_dir().is_dir():
        return out
    for f in migrations_dir().glob("v*_*_*.py"):
        m = re.match(r"v(\d+)_(\d+)_(\d+)\.py$", f.name)
        if not m:
            continue
        out.append((tuple(int(p) for p in m.groups()), f))
    out.sort(key=lambda x: x[0])
    return out


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location(f"migration_{path.stem}", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


# ---------- Driver ----------


def select(
    current: tuple[int, int, int], target: tuple[int, int, int]
) -> list[tuple[tuple[int, int, int], Path]]:
    return [item for item in discover() if current < item[0] <= target]


def run(root: Path, target_version: str, dry_run: bool, log: Callable[[str], None]) -> int:
    current = parse_version(read_version(root))
    target = parse_version(target_version)
    if target <= current:
        log(f"already at v{read_version(root)} (>= target v{target_version}); no migrations to run")
        return 0

    plan_set = select(current, target)
    if not plan_set:
        log(f"no migrations defined for v{read_version(root)} -> v{target_version}")
        return 0

    log(f"running {len(plan_set)} migration(s): v{read_version(root)} -> v{target_version}")
    for ver, path in plan_set:
        mod = load_module(path)
        actions: list[Action] = mod.plan(root)
        ver_str = ".".join(str(p) for p in ver)
        if not actions:
            log(f"  v{ver_str}: no actions (already migrated)")
            continue
        log(f"  v{ver_str}: {len(actions)} action(s)")
        for a in actions:
            log(f"    - {a.kind} {a.src or ''} {('-> ' + a.dst) if a.dst else ''} {a.note or ''}".rstrip())
        if not dry_run:
            mod.apply(root, actions)
            # Bump VERSION after each successful migration so partial runs are recoverable.
            (root / ".claude" / "VERSION").write_text(ver_str + "\n", encoding="utf-8")
            log(f"  v{ver_str}: applied; bumped .claude/VERSION")
    return 0


# ---------- CLI ----------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--target",
        help="target version to migrate to. Default: read .claude/VERSION (so this is a no-op unless used by /gtr:update with a fresher copy).",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="preview only — print actions, do not write.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="machine-readable output (only meaningful with --check).",
    )
    args = parser.parse_args()

    root = project_root()
    target = args.target or read_version(root)

    if args.json:
        current = parse_version(read_version(root))
        target_t = parse_version(target)
        plan_set = select(current, target_t)
        out = []
        for ver, path in plan_set:
            mod = load_module(path)
            ver_str = ".".join(str(p) for p in ver)
            out.append({"version": ver_str, "actions": [a.to_json() for a in mod.plan(root)]})
        json.dump({"current": read_version(root), "target": target, "migrations": out}, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    return run(root, target, args.check, print)


if __name__ == "__main__":
    sys.exit(main())
