"""Migration v0.2.0: namespace template commands under /gtr:*, drop /task and
/tpl, drop TODO.md / DEFERRED.md, rename PROJECT.yaml -> IDENTITY.yaml,
update slash-command references in CLAUDE.md / README.md.

Idempotent: every action checks current state and is skipped if already done.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

from migrations import Action  # type: ignore[import-not-found]


# Commands moved into the gtr/ subdirectory.
GTR_COMMANDS = (
    "setup.md",
    "menu.md",
    "doctor.md",
    "release.md",
    "update.md",
    "onboard.md",
    "new-migration.md",
)

# Commands removed in v0.2.0 (replaced by GSD).
DROPPED_COMMANDS = ("task.md", "tpl.md")

# Slash command renames applied to text files (word-boundary, in-prose only).
SLASH_RENAMES = {
    "/setup": "/gtr:setup",
    "/menu": "/gtr:menu",
    "/doctor": "/gtr:doctor",
    "/release": "/gtr:release",
    "/update": "/gtr:update",
    "/onboard": "/gtr:onboard",
    "/new-migration": "/gtr:new-migration",
    "/tpl": "/gtr:help",  # tpl folded into help in v0.2.0
}

# Files where slash-command references should be auto-rewritten.
TEXT_TARGETS = (
    "CLAUDE.md",
    "README.md",
    "IMPLEMENT.md",
)


def _commands_dir(root: Path) -> Path:
    return root / ".claude" / "commands"


def _gtr_dir(root: Path) -> Path:
    return _commands_dir(root) / "gtr"


def _has_content(path: Path) -> bool:
    """True when a markdown file has non-comment, non-blank lines worth keeping."""
    if not path.is_file():
        return False
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("<!--"):
            continue
        return True
    return False


def plan(root: Path) -> list[Action]:
    actions: list[Action] = []
    cmds = _commands_dir(root)
    gtr = _gtr_dir(root)

    # 1. Snapshot the existing commands directory before rearranging it.
    snapshot = root / ".claude" / "commands.pre-v0.2.0"
    if cmds.is_dir() and not snapshot.exists():
        # Only snapshot if at least one of the legacy command files is present
        # at the OLD location — otherwise the project is already migrated.
        legacy_present = any((cmds / name).is_file() for name in GTR_COMMANDS + DROPPED_COMMANDS)
        if legacy_present:
            actions.append(
                Action(
                    kind="copytree",
                    src=str(cmds.relative_to(root)),
                    dst=str(snapshot.relative_to(root)),
                    note="rollback snapshot",
                )
            )

    # 2. Move kept commands into gtr/ subdir.
    for name in GTR_COMMANDS:
        src = cmds / name
        dst = gtr / name
        if src.is_file() and not dst.exists():
            actions.append(
                Action(
                    kind="move",
                    src=str(src.relative_to(root)).replace("\\", "/"),
                    dst=str(dst.relative_to(root)).replace("\\", "/"),
                )
            )

    # 3. Delete dropped commands.
    for name in DROPPED_COMMANDS:
        src = cmds / name
        if src.is_file():
            actions.append(
                Action(kind="delete", src=str(src.relative_to(root)).replace("\\", "/"), note="dropped in v0.2.0")
            )

    # 4. TODO.md / DEFERRED.md handling.
    for name in ("TODO.md", "DEFERRED.md"):
        f = root / name
        legacy = root / f"{name}.legacy"
        if f.is_file() and not legacy.exists():
            if _has_content(f):
                actions.append(
                    Action(
                        kind="move",
                        src=name,
                        dst=f"{name}.legacy",
                        note="content preserved; migrate via /gsd:new-project",
                    )
                )
            else:
                actions.append(Action(kind="delete", src=name, note="empty in v0.1.x layout"))

    # 5. PROJECT.yaml -> IDENTITY.yaml rename (single source of truth for identity).
    project_yaml = root / "PROJECT.yaml"
    identity_yaml = root / "IDENTITY.yaml"
    if project_yaml.is_file() and not identity_yaml.exists():
        actions.append(
            Action(
                kind="move",
                src="PROJECT.yaml",
                dst="IDENTITY.yaml",
                note="renamed to avoid collision with GSD's PROJECT.md",
            )
        )

    # 6. Slash-command renames in text files (preview only — apply checks per file).
    for name in TEXT_TARGETS:
        f = root / name
        if f.is_file() and _has_legacy_slash_refs(f):
            actions.append(Action(kind="replace_in_file", src=name, note="rename /cmd -> /gtr:cmd"))

    # 7. /task references that cannot be auto-migrated — surface them.
    task_refs = _find_task_refs(root)
    if task_refs:
        actions.append(
            Action(
                kind="note",
                note=(
                    "Found /task references in: "
                    + ", ".join(task_refs)
                    + " — these cannot be auto-migrated to GSD. Update manually after running /gsd:new-project."
                ),
            )
        )

    # 8. PROJECT.yaml mentions inside text files become IDENTITY.yaml mentions.
    for name in TEXT_TARGETS + ("RELEASE.md", ".claude/TIPS.md"):
        f = root / name
        if f.is_file() and "PROJECT.yaml" in f.read_text(encoding="utf-8"):
            actions.append(
                Action(kind="replace_text", src=name, note="PROJECT.yaml -> IDENTITY.yaml in prose")
            )

    return actions


def apply(root: Path, actions: list[Action]) -> None:
    for a in actions:
        _apply_one(root, a)


def _apply_one(root: Path, a: Action) -> None:
    if a.kind == "copytree":
        src = root / a.src  # type: ignore[arg-type]
        dst = root / a.dst  # type: ignore[arg-type]
        if not dst.exists() and src.is_dir():
            shutil.copytree(src, dst)
        return

    if a.kind == "move":
        src = root / a.src  # type: ignore[arg-type]
        dst = root / a.dst  # type: ignore[arg-type]
        if src.exists() and not dst.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
        return

    if a.kind == "delete":
        src = root / a.src  # type: ignore[arg-type]
        if src.is_file():
            src.unlink()
        return

    if a.kind == "replace_in_file":
        f = root / a.src  # type: ignore[arg-type]
        text = f.read_text(encoding="utf-8")
        for old, new in SLASH_RENAMES.items():
            text = re.sub(rf"(?<![\w/]){re.escape(old)}\b", new, text)
        f.write_text(text, encoding="utf-8")
        return

    if a.kind == "replace_text":
        f = root / a.src  # type: ignore[arg-type]
        text = f.read_text(encoding="utf-8")
        text = text.replace("PROJECT.yaml", "IDENTITY.yaml")
        f.write_text(text, encoding="utf-8")
        return

    if a.kind == "note":
        # Append to migration log (created on demand).
        log = root / ".claude" / "migration-log.md"
        log.parent.mkdir(parents=True, exist_ok=True)
        existing = log.read_text(encoding="utf-8") if log.is_file() else "# Template migration log\n\n"
        log.write_text(existing + f"- v0.2.0 note: {a.note}\n", encoding="utf-8")
        return

    raise ValueError(f"unknown action kind: {a.kind!r}")


# ---------- helpers ----------


def _has_legacy_slash_refs(f: Path) -> bool:
    text = f.read_text(encoding="utf-8")
    for old in SLASH_RENAMES:
        if re.search(rf"(?<![\w/]){re.escape(old)}\b(?![:\w])", text):
            return True
    return False


def _find_task_refs(root: Path) -> list[str]:
    out: list[str] = []
    candidates = [
        root / "CLAUDE.md",
        root / "README.md",
        root / "IMPLEMENT.md",
        root / ".claude" / "TIPS.md",
    ]
    for f in candidates:
        if f.is_file() and re.search(r"(?<![\w/])/task\b", f.read_text(encoding="utf-8")):
            out.append(str(f.relative_to(root)).replace("\\", "/"))
    return out
