---
description: "[TEMPLATE] Show everything this template provides: commands, hooks, task files, recommended plugins."
---

Print the reference below. For the `Recommended global plugins` section, run `claude plugin list` first and mark each one as `installed` or `missing`.

Do not execute any other tool. Just print.

---

# Template reference

## Commands in this project

| Command | Purpose |
|---------|---------|
| `/menu` | Interactive entry point — pick what to do, Claude routes to the right command. |
| `/setup` | First-time setup wizard. Run once per fresh clone. |
| `/onboard` | Interactive runbook to merge the template into an existing project (driver for IMPLEMENT.md). |
| `/update` | Pull template updates from upstream and merge non-destructively. |
| `/task <subcommand>` | Manage persistent `TODO.md` tasks. Subcommands include `run` (work through the whole queue end-to-end). `/task` alone prints its usage. |
| `/doctor` | Read-only health check. |
| `/release <version>` | Prepare a release — bump, rotate CHANGELOG, commit, tag. Does NOT push. |
| `/new-migration` | Scaffold a new DB migration. |
| `/tpl` | This reference. |

## Commands from installed plugins

| Command | Plugin |
|---------|--------|
| `/commit`, `/commit-push-pr`, `/clean_gone` | `commit-commands` |
| `/review-pr` | `pr-review-toolkit` |
| `/revise-claude-md` | `claude-md-management` |
| `/create-skill` | `skill-creator` |

## Hooks registered by this template

| Event | Hook | Behavior |
|-------|------|----------|
| PreToolUse `Write\|Edit` | `pre_guard_release_files.py` | Blocks edits to protected files |
| PreToolUse `Write\|Edit` | `pre_guard_security.py` | Blocks dangerous code patterns |
| PreToolUse `Write\|Edit` | `pre_guard_env_secrets.py` | Blocks secret-like content |
| PostToolUse `Write\|Edit` | `post_validate_syntax.py` | Validates Python/JS/JSON after writes |
| SessionStart | `session_check_setup.py` | Injects `/setup` reminder when marker is missing |
| UserPromptSubmit | `pre_check_setup.py` | Injects reminder on every prompt until setup completes (non-blocking) |
| Opt-in | `optional/pre_warn_win32_danger.py` | Windows native API guardrail |

## Files used by the template

| File | Role |
|------|------|
| `CLAUDE.md` | Project instructions (filled by `/setup`) |
| `PROJECT.yaml` | Single source of truth for identity, version, release config |
| `CHANGELOG.md` | Keep-a-Changelog formatted; release notes source |
| `RELEASE.md` | End-to-end release runbook |
| `TODO.md` | Persistent tasks (managed by `/task`) |
| `DEFERRED.md` | Intentionally postponed work with triggers |
| `.github/workflows/release.yml` | Tag-triggered release automation (activated from `release.yml.template`) |
| `.github/workflows/ci.yml` | Lint + test on push/PR (activated from `ci.yml.template`) |
| `.claude/.setup-complete` | Setup marker written by `/setup`. Gitignored. |
| `.claude/.template-manifest.json` | Sha-256 manifest of every template-owned file at install time. Used by `/update` and `/doctor` to detect user modifications. |
| `.claude/scripts/manifest.py` | Helper that builds the manifest. Supports `--write` and `--check`. |
| `.claude/hooks/tests/` | Pytest suite for the guard hooks and manifest script. |
| `.claude/VERSION` | Template version pin |
| `.claude/TIPS.md` | Long-form reference |

## Recommended global plugins

Mark status for each from `claude plugin list`:

- `code-simplifier@claude-plugins-official`
- `commit-commands@claude-plugins-official`
- `pr-review-toolkit@claude-plugins-official`
- `claude-md-management@claude-plugins-official`
- `skill-creator@claude-plugins-official`
- `security-guidance@claude-plugins-official`
- `oh-my-claudecode@omc` (autopilot / ralph / ultrawork / deep-dive / plan agents — register marketplace first: `claude plugin marketplace add https://github.com/Yeachan-Heo/oh-my-claudecode`)
- `frontend-design@claude-code-plugins` (only if project has a UI)

## Quick recipes

| Task | Command |
|------|---------|
| Start working (one task) | `/task next` |
| Work through the whole queue | `/task run` |
| Plan a bulk roadmap | `/task roadmap <goal>` |
| See what's left | `/task list` |
| Finish a task | `/task done <id>` (enforces acceptance + test + commit) |
| Diagnose issues | `/doctor` |
| Refresh `CLAUDE.md` | `/revise-claude-md` (plugin) |
| Cut a release | `/release <version>` |
