"""Tests for the migration runner and the v0.2.0 migration script."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# Load the runner package and the v0.2.0 module so the runner's Action class
# is the same instance the migration imports.
runner = _load("migrations", SCRIPTS / "migrations.py")
v020 = _load("migrations.v0_2_0", SCRIPTS / "migrations" / "v0_2_0.py")


# ---------- runner ----------


def test_parse_version_accepts_semver():
    assert runner.parse_version("0.1.5") == (0, 1, 5)
    assert runner.parse_version("1.0.0-rc.1") == (1, 0, 0)


def test_select_picks_versions_strictly_above_current(monkeypatch, tmp_path):
    # Stub discover() to return a controlled list.
    monkeypatch.setattr(runner, "discover", lambda: [
        ((0, 2, 0), tmp_path / "v0_2_0.py"),
        ((0, 3, 0), tmp_path / "v0_3_0.py"),
    ])
    out = runner.select((0, 1, 5), (0, 3, 0))
    versions = [v for v, _ in out]
    assert versions == [(0, 2, 0), (0, 3, 0)]
    out2 = runner.select((0, 2, 0), (0, 3, 0))
    assert [v for v, _ in out2] == [(0, 3, 0)]
    out3 = runner.select((0, 3, 0), (0, 3, 0))
    assert out3 == []


# ---------- v0.2.0 plan ----------


def _make_v0_1_layout(root: Path, *, with_todo_content: bool = False, with_deferred: bool = True):
    (root / ".claude" / "commands").mkdir(parents=True)
    for name in v020.GTR_COMMANDS + v020.DROPPED_COMMANDS:
        (root / ".claude" / "commands" / name).write_text(f"# {name}\n", encoding="utf-8")
    (root / ".claude" / "VERSION").write_text("0.1.5\n", encoding="utf-8")
    (root / "PROJECT.yaml").write_text("identity:\n  name: demo\n", encoding="utf-8")
    if with_todo_content:
        (root / "TODO.md").write_text("# TODO\n\n## Active\n\n- [t-1] hello\n", encoding="utf-8")
    else:
        (root / "TODO.md").write_text("# TODO\n\n## Active\n## Blocked\n## Done\n", encoding="utf-8")
    if with_deferred:
        (root / "DEFERRED.md").write_text("# Deferred\n", encoding="utf-8")
    (root / "CLAUDE.md").write_text("Run `/setup`, then `/menu`.\n", encoding="utf-8")


def test_plan_idempotent_on_clean_v0_2_layout(tmp_path):
    # Clean v0.2 layout — no v0.1 commands present, gtr/ is the only dir,
    # no PROJECT.yaml at root.
    (tmp_path / ".claude" / "commands" / "gtr").mkdir(parents=True)
    (tmp_path / ".claude" / "VERSION").write_text("0.2.0\n", encoding="utf-8")
    (tmp_path / "IDENTITY.yaml").write_text("identity:\n  name: demo\n", encoding="utf-8")
    actions = v020.plan(tmp_path)
    assert actions == []


def test_plan_for_v0_1_layout_lists_expected_actions(tmp_path):
    _make_v0_1_layout(tmp_path)
    actions = v020.plan(tmp_path)
    kinds = [a.kind for a in actions]
    # Snapshot copy must come first.
    assert kinds[0] == "copytree"
    # All gtr commands moved.
    moves = {(a.src, a.dst) for a in actions if a.kind == "move"}
    for name in v020.GTR_COMMANDS:
        assert (f".claude/commands/{name}", f".claude/commands/gtr/{name}") in moves
    # Both dropped commands deleted.
    deletes = {a.src for a in actions if a.kind == "delete"}
    for name in v020.DROPPED_COMMANDS:
        assert f".claude/commands/{name}" in deletes
    # PROJECT.yaml renamed to IDENTITY.yaml.
    assert any(a.kind == "move" and a.src == "PROJECT.yaml" and a.dst == "IDENTITY.yaml" for a in actions)


def test_apply_renames_files_and_creates_snapshot(tmp_path):
    _make_v0_1_layout(tmp_path)
    actions = v020.plan(tmp_path)
    v020.apply(tmp_path, actions)

    # gtr/ commands present.
    for name in v020.GTR_COMMANDS:
        assert (tmp_path / ".claude" / "commands" / "gtr" / name).is_file()
        assert not (tmp_path / ".claude" / "commands" / name).is_file()

    # Dropped commands gone.
    for name in v020.DROPPED_COMMANDS:
        assert not (tmp_path / ".claude" / "commands" / name).is_file()

    # Snapshot exists with the legacy command files.
    snapshot = tmp_path / ".claude" / "commands.pre-v0.2.0"
    assert snapshot.is_dir()
    assert (snapshot / "task.md").is_file()
    assert (snapshot / "setup.md").is_file()

    # IDENTITY.yaml replaces PROJECT.yaml.
    assert (tmp_path / "IDENTITY.yaml").is_file()
    assert not (tmp_path / "PROJECT.yaml").is_file()

    # CLAUDE.md slash-command refs rewritten.
    text = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert "/gtr:setup" in text
    assert "/gtr:menu" in text
    assert "/setup`" not in text


def test_todo_with_content_preserved_as_legacy(tmp_path):
    _make_v0_1_layout(tmp_path, with_todo_content=True)
    actions = v020.plan(tmp_path)
    v020.apply(tmp_path, actions)
    assert (tmp_path / "TODO.md.legacy").is_file()
    assert not (tmp_path / "TODO.md").is_file()


def test_empty_todo_deleted_outright(tmp_path):
    _make_v0_1_layout(tmp_path, with_todo_content=False)
    actions = v020.plan(tmp_path)
    v020.apply(tmp_path, actions)
    assert not (tmp_path / "TODO.md").is_file()
    assert not (tmp_path / "TODO.md.legacy").is_file()


def test_double_apply_is_noop(tmp_path):
    _make_v0_1_layout(tmp_path)
    v020.apply(tmp_path, v020.plan(tmp_path))
    second = v020.plan(tmp_path)
    # No moves remain because the source files no longer exist.
    assert all(a.kind != "move" for a in second)
    # No deletes for dropped commands either.
    assert all(a.kind != "delete" or a.src not in {f".claude/commands/{n}" for n in v020.DROPPED_COMMANDS} for a in second)


def test_runner_dry_run_does_not_mutate(tmp_path):
    _make_v0_1_layout(tmp_path)
    captured: list[str] = []
    runner.run(tmp_path, "0.2.0", dry_run=True, log=captured.append)
    assert (tmp_path / "PROJECT.yaml").is_file()
    assert (tmp_path / "TODO.md").is_file()
    assert any("0.2.0" in line for line in captured)


def test_runner_apply_bumps_version(tmp_path):
    _make_v0_1_layout(tmp_path)
    runner.run(tmp_path, "0.2.0", dry_run=False, log=lambda _msg: None)
    assert (tmp_path / ".claude" / "VERSION").read_text(encoding="utf-8").strip() == "0.2.0"


# ---------- v0.6.4 plan ----------

v064 = _load("migrations.v0_6_4", SCRIPTS / "migrations" / "v0_6_4.py")


LEGACY_COMM = (
    "## Communication\n\n"
    "- Speak with the user in Turkish (Türkçe). All conversational responses,\n"
    "  prompts, summaries, and questions must be in Turkish.\n"
    "- Code, identifiers, comments, commit messages, and file contents\n"
    "  must always be in English regardless of conversation language.\n"
    "- Slash command output formatting (tables, status lines) stays English.\n"
)

NEW_COMM_MARKER = "slash-command output (including"
LEGACY_TAIL = "Slash command output formatting (tables, status lines) stays English."


def _write_claude_md(root: Path, body: str) -> Path:
    f = root / "CLAUDE.md"
    f.write_text(body, encoding="utf-8")
    return f


def test_v064_plan_no_op_when_legacy_block_absent(tmp_path):
    _write_claude_md(tmp_path, "# CLAUDE.md\n\nNo communication section.\n")
    assert v064.plan(tmp_path) == []


def test_v064_plan_no_op_when_already_migrated(tmp_path):
    _write_claude_md(
        tmp_path,
        "# CLAUDE.md\n\n## Communication\n\n"
        "- Speak with the user in Turkish. All conversational responses,\n"
        "  prompts, summaries, questions, and slash-command output (including\n"
        "  /gtr:help, /gtr:doctor, /gsd:* commands) must be in this language.\n",
    )
    assert v064.plan(tmp_path) == []


def test_v064_plan_detects_legacy_block(tmp_path):
    _write_claude_md(tmp_path, "# CLAUDE.md\n\n" + LEGACY_COMM + "\n## Next\n")
    actions = v064.plan(tmp_path)
    assert len(actions) == 1
    assert actions[0].kind == "rewrite_communication"
    assert actions[0].src == "CLAUDE.md"


def test_v064_apply_replaces_legacy_block(tmp_path):
    f = _write_claude_md(tmp_path, "# CLAUDE.md\n\n" + LEGACY_COMM + "\n## Next section\n\nbody.\n")
    actions = v064.plan(tmp_path)
    v064.apply(tmp_path, actions)
    out = f.read_text(encoding="utf-8")
    assert NEW_COMM_MARKER in out
    assert LEGACY_TAIL not in out
    assert "## Next section" in out
    assert "body." in out


def test_v064_apply_is_idempotent(tmp_path):
    _write_claude_md(tmp_path, "# CLAUDE.md\n\n" + LEGACY_COMM + "\n## Next\n")
    v064.apply(tmp_path, v064.plan(tmp_path))
    second_plan = v064.plan(tmp_path)
    assert second_plan == []


def test_v064_unparseable_language_logs_note(tmp_path):
    body = (
        "## Communication\n\n"
        "- Custom rule that does not include the Speak-in line.\n"
        "- Slash command output formatting (tables, status lines) stays English.\n"
    )
    _write_claude_md(tmp_path, body)
    actions = v064.plan(tmp_path)
    assert len(actions) == 1
    assert actions[0].kind == "note"
