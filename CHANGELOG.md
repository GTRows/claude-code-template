# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

The release workflow extracts the body of the section matching the pushed tag
and uses it as the GitHub release notes. Do not change the heading format.

## [Unreleased]

### Added
### Changed
### Deprecated
### Removed
### Fixed
### Security

## [0.2.0] - 2026-04-30

### Added
- `/gtr:help` command. Detailed reference for both `/gtr:*` template commands and `/gsd:*` planning commands. Args: `/gtr:help` (table of contents), `/gtr:help <command>`, `/gtr:help <topic>` (planning, release, hooks, manifest, migration, onboarding, permissions).
- `/gtr:setup --extras` mode. Run only the optional scaffolding step (LICENSE, SECURITY.md, CONTRIBUTING.md, CODEOWNERS, dependabot, pre-commit, .env.example) without re-running the core wizard.
- `/gtr:doctor` predictive health: CHANGELOG churn, release recency, plan staleness, manifest drift volume, pending migrations.
- `/gtr:doctor` token usage summary: rolls up the last seven days of `.claude/usage-log.jsonl` and flags sessions that burned 5x the average.
- `.claude/hooks/session_log_usage.py` SessionEnd hook. Appends a JSONL line with token usage per session to `.claude/usage-log.jsonl` (gitignored, local-only). 5 tests cover happy path, multiple runs, missing usage, malformed stdin, partial keys.
- Versioned migration runner under `.claude/scripts/migrations.py` plus `migrations/v0_2_0.py`. 10 migration tests cover dry-run, apply, idempotency, runner version selection.
- `/gtr:update` step 2.5 invokes the migration runner before fetching upstream so reshapes happen first.

### Changed
- BREAKING: All template commands moved under the `/gtr:*` namespace. Slash command renames in CLAUDE.md / README.md / IMPLEMENT.md are auto-applied by the v0.2.0 migration script with word-boundary safety.
- BREAKING: `PROJECT.yaml` renamed to `IDENTITY.yaml`. Resolves naming collision with GSD's `.planning/PROJECT.md` (vision document). Migration handles the rename and rewrites in-prose mentions across template-owned docs.
- Planning workflow now delegates to the GSD plugin (`oh-my-claudecode`). The previous in-house `/task` system kept everything in the main session context and burned tokens linearly with task count; GSD's per-plan worktree-isolated subagent dispatch keeps main context at ~5%.
- `/gtr:menu` is now the friendly face for both `/gtr:*` and `/gsd:*` commands so users do not have to memorise GSD's command names.
- `/gtr:setup` step 9 hands off to GSD on opt-in (yes / no / later). Brief auto-fills from `IDENTITY.yaml` + `CLAUDE.md` + `README.md`.

### Removed
- BREAKING: `/task` and all its subcommands (`list`, `next`, `run`, `add`, `done`, `block`, `update`, `plan`, `roadmap`).
- BREAKING: `/tpl` (folded into `/gtr:help`).
- BREAKING: `TODO.md` and `DEFERRED.md` are no longer part of the template skeleton. Existing files with content are preserved as `*.legacy` by the migration; empty ones are deleted.

### Migration
Run `/gtr:update` from a v0.1.x project. The runner detects the version jump, snapshots `.claude/commands/` to `.claude/commands.pre-v0.2.0/`, applies all v0.2.0 reshapes idempotently, and bumps `.claude/VERSION`. /task references in CLAUDE.md / README.md cannot be auto-mapped to GSD — the migration leaves them in place and writes a note to `.claude/migration-log.md` so you can rewrite them after running `/gsd:new-project`.


<!--
Section template for a new release:

## [x.y.z] - YYYY-MM-DD

### Added
- ...

### Changed
- ...

### Fixed
- ...
-->
