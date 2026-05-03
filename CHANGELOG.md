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

## [0.6.9] - 2026-05-03

### Fixed
- `/gtr:update` reported a stale upstream version when the latest tag was pushed without a published GitHub Release. Step 1 now queries `git ls-remote --tags` first (tags are the source of truth) and only falls back to `gh release list` if the ls-remote call fails. Previously the order was inverted, so a tag-only push made `/gtr:update` report the older published release as "latest".

## [0.6.8] - 2026-05-03

### Added
- `/gtr:set-language [lang]`: switch the conversation language without re-running `/gtr:setup`. Writes (or updates) the `## Communication` block in `CLAUDE.md` and syncs the `language:` line in `.claude/.setup-complete`. Accepts English names (`Turkish`), native names (`Türkçe`), or ISO 639-1 codes (`tr`). Listed in `/gtr:help` (TOC, INTENT cheat-sheet, command reference) and added as menu option 3 in `/gtr:menu` with downstream options renumbered.

### Changed
- `.claude/settings.json` no longer puts `Bash(git push:*)` on the `ask` list. Force variants (`git push --force`, `git push -f`) remain on `deny`, and per-user `allow` rules in `settings.local.json` now take effect without a per-call prompt.
- `.claude/VERSION` synced to `0.6.7` to match `IDENTITY.yaml`. The two had drifted (`VERSION` was stuck at `0.5.0`); future migrations need an accurate `VERSION` to detect the gap.

## [0.6.7] - 2026-05-02

### Fixed
- `/gtr:next` rendering section headers (`RIGHT NOW`, `WHY`, `AFTER THIS`, `PROJECT STATE`) and bullet labels (`Setup complete`, `Conversation language`, `Identity`, `Project vision`, `Roadmap`, `Codebase indexed`, `Active plan`, `Active plan finished`) in English when `## Communication` was set to a non-English language. Layout in `next.md` is now annotated with `<header: ...>` / `<label: ...>` placeholders so it is unambiguously a structural template, not a verbatim string. File paths in parentheses (`IDENTITY.yaml`, `.planning/PROJECT.md`, etc.) still stay verbatim. Sample translations for Turkish included as a reference.

## [0.6.6] - 2026-05-02

### Added
- `.claude/docs/output-style.md`: hard length-and-prose budget for every `/gtr:*` command. Spells out: 25-line cap, no preamble, no recap, bullets over paragraphs, anti-examples for slop. Single source of truth so individual command files do not have to repeat the same rule.

### Changed
- `/gtr:setup`, `/gtr:menu`, `/gtr:doctor`, `/gtr:next`, `/gtr:onboard`, `/gtr:release`, `/gtr:update`, `/gtr:help` now point at `.claude/docs/output-style.md` and add a per-command line cap (8-30 lines depending on the command). Cuts the AI-written verbosity that was making routine commands look like reading a wiki.

## [0.6.5] - 2026-05-02

### Changed
- `/gtr:help` no-args output is now state-aware. Instead of dumping the full 10-step lifecycle every time, it inspects the project (setup marker, IDENTITY, CLAUDE.md, .planning/* artefacts, source-file count) and prints only the **remaining steps** in order, capped at 5, each with a one-clause why. Steps already completed (setup done, vision written, roadmap drafted, etc.) are skipped. Users who want the full chain can run `/gtr:help workflow`.
- The static lifecycle list moved from the no-args path to a dedicated reference section, reachable only via `/gtr:help workflow`.

### Fixed
- `/gtr:help` printing the full "General workflow" (steps 1-10) every time, including steps the user had already finished. The new From-here block keeps the output short and tailored.

## [0.6.4] - 2026-05-01

### Added
- `.claude/scripts/migrations/v0_6_4.py`: rewrites the legacy `## Communication` block in `CLAUDE.md` (the pre-v0.6.0 wording that ended with "Slash command output formatting (tables, status lines) stays English.") with the v0.6.0+ wording. Preserves the language the user originally chose. Idempotent. Skipped if the block was hand-edited beyond the template default; in that case a note is appended to `.claude/migration-log.md`.
- 6 unit tests for the new migration cover legacy detection, no-op on missing/already-migrated/customised blocks, replacement, idempotency, and note logging.

### Changed
- `/gtr:help` output-language directive made explicit: in the table-of-contents code block, the right-hand description column **must be translated** when `## Communication` is set to a non-English language. Slash-command names, file paths, version strings, and shell commands stay verbatim. Previously the rule said "code blocks stay verbatim", which was ambiguous and caused some renderings to leave descriptions in English.

### Fixed
- `/gtr:help` rendering descriptions in English even when conversation language was set to Turkish (or another non-English language). Together with the v0.6.4 migration that updates the project's `## Communication` block, `/gtr:update` now produces help output that is fully in the chosen language on next render.

## [0.6.3] - 2026-05-01

### Added
- `/gtr:next` — state-aware advisor. Reads the project's state (setup marker, IDENTITY, CLAUDE.md, .planning/* artefacts, source-file count) and prints the single next command to run, with a one-line reason and the likely follow-ups. Print-and-stop by default; reply "do it" to dispatch. Decision table prioritises earliest-stage gaps: setup -> map-codebase (brownfield) -> new-project -> create-roadmap -> plan-phase -> execute-plan -> verify-work -> plan-fix -> release.
- `/gtr:menu` exposes "Tell me what to do next" as option 2, routing to `/gtr:next`.
- `/gtr:help` table-of-contents and INTENT cheat sheet include `/gtr:next` and the row "What should I do right now?".

## [0.6.2] - 2026-05-01

### Added
- `/gtr:help` no-args output now includes an **INTENT -> COMMAND** quick map at the bottom of the table-of-contents code block. Maps natural-language intents ("break a phase into tasks", "run the plan", "walk the roadmap") to the exact slash command, so users do not have to read the full workflow topic to find the right command.
- `/gtr:help` no-args output now also prints a **General workflow** section beneath the TOC: a numbered 1-10 list (setup -> map-codebase -> new-project -> create-roadmap -> plan-phase -> execute-plan -> verify -> loop -> release -> maintain). This is the short answer to "how do I actually use this template?" without scrolling for the deep `Topic: workflow` walkthrough.

## [0.6.1] - 2026-05-01

### Added
- `## Communication` recognised by `claude_md_check.py` as a known section so it does not show up as an unexpected extra.

### Changed
- Language directive applied to all remaining `/gtr:*` commands (`menu`, `doctor`, `onboard`, `release`, `update`, `new-adr`, `new-migration`, `new-rule`, `new-skill`). Each command now reads `## Communication` from `CLAUDE.md` and produces conversational output in that language; file content, code, and command identifiers stay verbatim. Previously only `/gtr:help` honoured the rule.
- `claude_md_check.py` is now informational by default. No section is marked required; the script reports presence/missing/placeholder and exits non-zero only when `CLAUDE.md` is absent. Prevents `/gtr:doctor` from failing on projects that use a different CLAUDE.md structure.
- `/gtr:doctor` section 2 wording updated to reflect that the section list is informational, not a failure gate.
- `/gtr:setup` step 2 (preflight) now explicitly tells Claude to use the `Read` tool for the `.claude/.setup-complete` existence check. Avoids the assistant generating PowerShell `Test-Path` or other shell-specific syntax that fails under Git Bash on Windows.

### Fixed
- `/gtr:doctor` falsely flagging projects without the template's exact section names as failing the structural check.
- `/gtr:menu`, `/gtr:doctor`, `/gtr:onboard`, etc. answering in English even when `## Communication` was set to another language.
- `/gtr:setup` preflight emitting `if (Test-Path ...) { ... }` PowerShell syntax that errored out under bash.

## [0.6.0] - 2026-05-01

### Added
- `/gtr:help` new top-level topic: `workflow`. Walks the full lifecycle (setup -> frame project -> plan phase -> execute -> verify -> release -> keep current) with a quick decision tree. Printed automatically when `/gtr:help` is invoked with no arguments, alongside the table of contents.
- `/gtr:help` `planning` topic now includes concrete greenfield and brownfield walkthroughs, plus an explanation of the three execution strategies auto-selected by `/gsd:execute-plan` (no checkpoints, verify checkpoints, decision checkpoints).

### Changed
- `/gtr:setup` step ordering: conversation language is now **step 1**, asked before the preflight check and before any other interactive prompt. Once chosen, the language is written to `CLAUDE.md` `## Communication` and bound for every subsequent setup prompt and slash-command output. Steps 2-16 renumbered accordingly. `--extras` mode now reads the existing `## Communication` section to keep the language consistent.
- `/gtr:help` output language directive: when `CLAUDE.md` `## Communication` is set, all explanatory prose, headings, and bullets render in that language. Command names, file paths, and code blocks stay verbatim. Falls back to the language the user wrote the request in if `## Communication` is missing.
- `.claude/docs/setup-flow.md` updated to reflect the new step ordering and the language-binding behaviour.

### Removed
- The hard rule "Help output stays English regardless of conversation language" in `/gtr:help`. Help now follows the configured conversation language.

## [0.5.0] - 2026-04-30

### Added
- `.claude/scripts/claude_md_check.py`: structural drift checker for CLAUDE.md. Reports missing required sections and sections that are still placeholders (HTML-comment-only). Returns non-zero exit code only when required sections are absent. 5 unit tests cover parse, placeholder detection, missing/extra reporting.
- `.claude/scripts/plugins.py`: plugin set tracker. Records `name@marketplace` for every installed plugin into `.claude/plugin-pin.json` (committed). Drift detection compares the pin against the currently installed set. 6 unit tests cover render, save/load, diff.
- `/gtr:doctor` section 2 now invokes `claude_md_check.py` before legacy grep checks.
- `/gtr:doctor` section 5 now invokes `plugins.py --check` after the recommended-plugin check.
- `/gtr:setup` step 8c writes the plugin pin after install so `/gtr:doctor` can flag drift later.

## [0.4.0] - 2026-04-30

### Added
- `.claude/hooks/_audit.py`: shared append-only audit logger. Every guard hook (`pre_guard_release_files`, `pre_guard_security`, `pre_guard_env_secrets`) now records each block to `.claude/hook-audit.log` (gitignored). Schema: ts, hook, action, file_path, reason. 5 audit tests cover unit + end-to-end paths.
- `/gtr:doctor` section 12 reads the audit log over the last 7 days and flags hooks that fire more than 50 times (likely misconfigured pattern).
- `/gtr:new-skill`: scaffolds a project-specific skill under `.claude/skills/<slug>/SKILL.md` with trigger-condition guidance and anti-patterns. Discourages duplicating plugin functionality.
- `/gtr:new-rule`: scaffolds a path-scoped CLAUDE.md rule under `.claude/rules/<slug>.md` with a `paths:` glob frontmatter so rules only load when relevant files are touched.
- `/gtr:help` table of contents updated with the new commands.

## [0.3.0] - 2026-04-30

### Added
- `/gtr:new-adr` command. Scaffolds sequentially-numbered Architecture Decision Records under `docs/adr/` with a structured template (Status / Context / Decision / Consequences / Alternatives / References) and lifecycle conventions.
- `.claude/docs/` directory with per-topic reference files (hooks, mcp, commands, permissions, releases, setup-flow, deferred-work, claude-md-best-practices, workflow). `.claude/TIPS.md` is now a thin index.
- `/gtr:new-migration` rewritten with explicit per-tool detection: Alembic, Django, Prisma, Knex, TypeORM, sqlx, diesel, Flyway, goose / atlas / sql-migrate. Prefers the tool's own scaffolder, falls back to hand-writing only when no generator exists. Documents rollback paths for destructive changes.
- Manifest now tracks `.claude/docs/*.md` and `.claude/scripts/migrations/*.py`.

### Changed
- TIPS.md split into focused topic files; entry points stay the same (`/gtr:help <topic>` or browse `.claude/docs/`).

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
