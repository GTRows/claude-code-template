"""Migration v0.6.4: rewrite ``## Communication`` in CLAUDE.md so help and
other slash-command output also speaks the configured language.

The pre-v0.6.0 setup wizard wrote a Communication block ending with::

    - Slash command output formatting (tables, status lines) stays English.

That bullet tells Claude to keep tables in English even when the user has
picked Turkish/etc., which contradicts the v0.6.0+ behaviour where slash
commands honour the chosen language. This migration detects the legacy
wording (verbatim match — we do not touch user-customised blocks) and
replaces the block body with the v0.6.0+ wording, preserving whatever
language the user originally chose.

Idempotent: skipped if the block is already updated, missing, or has been
hand-edited beyond the legacy template.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from migrations import Action  # type: ignore[import-not-found]


LEGACY_TAIL = "Slash command output formatting (tables, status lines) stays English."


def _extract_language(block_body: str) -> str | None:
    """Pull the language name out of ``- Speak with the user in <Language>.``."""
    m = re.search(r"Speak with the user in\s+([^\.\n]+?)\s*\.", block_body)
    if not m:
        return None
    raw = m.group(1).strip()
    raw = re.sub(r"\s*\([^)]*\)\s*$", "", raw).strip()
    return raw or None


def _find_block(text: str) -> tuple[int, int, str] | None:
    """Return (start, end, body) of the ``## Communication`` section, or None."""
    pattern = re.compile(r"(?m)^##\s+Communication\s*$")
    m = pattern.search(text)
    if not m:
        return None
    body_start = m.end()
    next_h = re.search(r"(?m)^##\s+\S", text[body_start:])
    body_end = body_start + next_h.start() if next_h else len(text)
    return m.start(), body_end, text[body_start:body_end]


def _new_block(language: str) -> str:
    return (
        "\n\n"
        f"- Speak with the user in {language}. All conversational responses,\n"
        "  prompts, summaries, questions, and slash-command output (including\n"
        "  /gtr:help, /gtr:doctor, /gsd:* commands) must be in this language.\n"
        "- Code, identifiers, comments, commit messages, and file contents\n"
        "  must always be in English regardless of conversation language.\n"
        "- Status lines, table headers, and command names stay verbatim\n"
        "  (e.g. `/gtr:setup`, `IDENTITY.yaml`) — do not translate them.\n\n"
    )


def plan(root: Path) -> list[Action]:
    actions: list[Action] = []
    claude_md = root / "CLAUDE.md"
    if not claude_md.is_file():
        return actions

    text = claude_md.read_text(encoding="utf-8")
    block = _find_block(text)
    if block is None:
        return actions

    _, _, body = block

    if LEGACY_TAIL not in body:
        return actions

    language = _extract_language(body)
    if not language:
        actions.append(
            Action(
                kind="note",
                note=(
                    "v0.6.4: legacy ## Communication block detected but language could not "
                    "be parsed; not rewritten. Edit CLAUDE.md manually."
                ),
            )
        )
        return actions

    actions.append(
        Action(
            kind="rewrite_communication",
            src="CLAUDE.md",
            payload=json.dumps({"language": language}),
            note=f"replace legacy ## Communication block (language: {language})",
        )
    )
    return actions


def apply(root: Path, actions: list[Action]) -> None:
    for a in actions:
        _apply_one(root, a)


def _apply_one(root: Path, a: Action) -> None:
    if a.kind == "rewrite_communication":
        f = root / a.src  # type: ignore[arg-type]
        if not f.is_file():
            return
        text = f.read_text(encoding="utf-8")
        block = _find_block(text)
        if block is None:
            return
        start, end, body = block
        if LEGACY_TAIL not in body:
            return
        payload = json.loads(a.payload or "{}")
        language = payload.get("language")
        if not language:
            return
        new_block = "## Communication" + _new_block(language)
        # Preserve trailing newline structure of the surrounding text.
        rebuilt = text[:start] + new_block.rstrip() + "\n" + text[end:].lstrip("\n")
        f.write_text(rebuilt, encoding="utf-8")
        return

    if a.kind == "note":
        log = root / ".claude" / "migration-log.md"
        log.parent.mkdir(parents=True, exist_ok=True)
        existing = log.read_text(encoding="utf-8") if log.is_file() else "# Template migration log\n\n"
        log.write_text(existing + f"- v0.6.4 note: {a.note}\n", encoding="utf-8")
        return

    raise ValueError(f"unknown action kind: {a.kind!r}")
