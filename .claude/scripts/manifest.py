#!/usr/bin/env python3
"""
Generate .claude/.template-manifest.json by hashing every template-owned file
that currently exists in the project. Used by /setup at install time and by
/update after applying upstream changes.

Usage:
    python .claude/scripts/manifest.py [--write] [--check]

Without flags, prints the computed manifest to stdout (JSON).
--write   overwrite .claude/.template-manifest.json with the computed manifest.
--check   exit 1 if any template-owned file's sha differs from the manifest;
          used by /doctor and /update to detect user modifications.
"""

import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

# Paths under PROJECT_ROOT that the template owns. Glob-aware via Path.rglob.
TEMPLATE_PATHS = [
    ".claude/commands/*.md",
    ".claude/commands/gtr/*.md",
    ".claude/hooks/*.py",
    ".claude/hooks/optional/*.py",
    ".claude/scripts/*.py",
    ".claude/scripts/migrations/*.py",
    ".claude/docs/*.md",
    ".claude/TIPS.md",
    ".claude/VERSION",
    ".claude/settings.json",
    ".github/workflows/*.template",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/ISSUE_TEMPLATE/*.md",
    "CLAUDE.md",
    "IMPLEMENT.md",
    "RELEASE.md",
    ".editorconfig",
    ".gitignore",
]


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def collect_files(root: Path) -> list[Path]:
    found: set[Path] = set()
    for pattern in TEMPLATE_PATHS:
        if "*" in pattern:
            parent, _, glob = pattern.rpartition("/")
            base = root / parent if parent else root
            if base.is_dir():
                for path in base.glob(glob):
                    if path.is_file():
                        found.add(path)
        else:
            path = root / pattern
            if path.is_file():
                found.add(path)
    return sorted(found)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def read_version(root: Path) -> str:
    vfile = root / ".claude" / "VERSION"
    if vfile.is_file():
        return vfile.read_text(encoding="utf-8").strip()
    return "0.0.0"


def build_manifest(root: Path) -> dict:
    return {
        "version": read_version(root),
        "files": {
            str(p.relative_to(root)).replace("\\", "/"): sha256(p)
            for p in collect_files(root)
        },
    }


def load_existing(root: Path) -> dict | None:
    mfile = root / ".claude" / ".template-manifest.json"
    if not mfile.is_file():
        return None
    return json.loads(mfile.read_text(encoding="utf-8"))


def write_manifest(root: Path, manifest: dict) -> Path:
    """Write the manifest atomically.

    Writes to a sibling temp file in the same directory and renames it onto
    the destination via os.replace, which is atomic on POSIX and Windows.
    Prevents a partial file or a write/write race between concurrent
    /setup and /update sessions from leaving a corrupted manifest.
    """
    mfile = root / ".claude" / ".template-manifest.json"
    mfile.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(
        prefix=".template-manifest.", suffix=".json.tmp", dir=mfile.parent
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, sort_keys=True)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, mfile)
    except Exception:
        Path(tmp_path).unlink(missing_ok=True)
        raise
    return mfile


def diff_against_existing(root: Path, current: dict) -> list[str]:
    existing = load_existing(root)
    if existing is None:
        return []
    drift: list[str] = []
    e_files = existing.get("files", {})
    c_files = current.get("files", {})
    for path, sha in c_files.items():
        if path in e_files and e_files[path] != sha:
            drift.append(path)
    return drift


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write manifest to disk")
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit 1 if local files differ from manifest",
    )
    args = parser.parse_args()

    root = project_root()
    manifest = build_manifest(root)

    if args.check:
        drift = diff_against_existing(root, manifest)
        if drift:
            print("template files modified vs manifest:")
            for path in drift:
                print(f"  {path}")
            return 1
        print("clean: all template files match manifest")
        return 0

    if args.write:
        path = write_manifest(root, manifest)
        print(f"wrote {path.relative_to(root)} ({len(manifest['files'])} files)")
        return 0

    json.dump(manifest, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
