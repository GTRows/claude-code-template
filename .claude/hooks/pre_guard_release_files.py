#!/usr/bin/env python3
"""
Hook: PreToolUse -- Write | Edit
Purpose: Protect release, build, and packaging files from accidental modifications.
         These files should only be edited deliberately, not as a side effect.

Exit 2 = block + send stderr as feedback to Claude.

CUSTOMIZE: Edit PROTECTED_EXACT, PROTECTED_SUFFIXES, and PROTECTED_DIRS
           to match your project's protected files.
"""

import json
import os
import sys

# ---------- CONFIGURATION ----------
# Full filenames that are always protected (case-insensitive match)
PROTECTED_EXACT = {
    "package.json",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "setup.py",
    "setup.cfg",
    "pyproject.toml",
    "cargo.toml",
    "cargo.lock",
    "go.mod",
    "go.sum",
    "project.yaml",
    "changelog.md",
    "release.md",
    "requirements.txt",
    "requirements-dev.txt",
    "dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
}

# File suffixes that are always protected
PROTECTED_SUFFIXES = (
    ".spec",
    ".iss",
)

# Directory prefixes that are protected (files inside these dirs are blocked)
PROTECTED_DIRS = (
    ".github/workflows",
    "scripts",
)

# Directory prefixes that are NEVER protected, even if the filename matches
# PROTECTED_EXACT. Needed because command/skill/doc files may share names
# with release artifacts (e.g. .claude/commands/release.md).
EXEMPT_DIRS = (
    ".claude/commands",
    ".claude/skills",
    ".claude/hooks",
    ".claude/agents",
    ".claude/scripts",
)
# -----------------------------------


def is_protected(path: str) -> bool:
    if not path:
        return False

    normalized = path.replace("\\", "/").lower()

    if any(f"/{d}/" in normalized or normalized.startswith(f"{d}/") for d in EXEMPT_DIRS):
        return False

    name = os.path.basename(normalized)
    if name in PROTECTED_EXACT:
        return True
    if any(name.endswith(s) for s in PROTECTED_SUFFIXES):
        return True

    return any(f"/{d}/" in normalized or normalized.startswith(f"{d}/") for d in PROTECTED_DIRS)



# --- audit ---
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
try:
    from _audit import record_block as _record_block
except Exception:
    def _record_block(*_args, **_kwargs):
        pass
# --- end audit ---

def main() -> None:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    if is_protected(file_path):
        print(
            f"Blocked: '{os.path.basename(file_path)}' is a protected file.\n"
            "This file affects builds, releases, or infrastructure. "
            "Confirm with the user before proceeding.",
            file=sys.stderr,
        )
        _record_block("pre_guard_release_files", file_path=file_path, reason=f"protected file: {os.path.basename(file_path)}")
        sys.exit(2)


if __name__ == "__main__":
    main()
