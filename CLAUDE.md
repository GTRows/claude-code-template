# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## First-time setup check

Before doing any coding work, check for `.claude/.setup-complete`.
- If missing: recommend `/setup` to the user and wait for confirmation before starting implementation. Read-only questions and template maintenance are fine without it.
- If present: proceed normally.

## Available commands

- `/tpl` — list every template command, hook, and file in this repo.
- `/setup` — first-time wizard (only needed once per clone).
- `/task <subcommand>` — manage persistent TODO.md tasks. Key subcommands: `next` (one task), `run` (all Active tasks end-to-end). `/task` alone prints usage.
- `/doctor` — read-only health check.
- `/release <version>` — prepare a release (bump, rotate CHANGELOG, commit, tag). Never pushes.
- Plugin commands: `/commit`, `/commit-push-pr`, `/review-pr`, `/revise-claude-md`, `/create-skill`.

## Task workflow

Two layers — do not conflate them:

1. **TODO.md (persistent)** — durable tasks across sessions. Managed via `/task`. Each entry has an id (`t-N`), a title, and an Acceptance line. Sections: Active / Blocked / Done.
2. **Built-in TaskCreate (ephemeral)** — this session's subtask breakdown of whatever TODO task is in flight. Use it to plan and track step-by-step work within the conversation. Do not mirror TODO.md into it.

When starting work:
- One task at a time: `/task next` (moves it to top of Active, breaks into `TaskCreate` subtasks).
- Whole queue: `/task run` (processes every Active task end-to-end: plan → implement → test → commit → `done` gate → next task). Stops on failure, keeps unfinished work in Active.
- Step through subtasks one at a time. Mark each completed as soon as done, not in a batch.
- When the TODO task's acceptance is met AND tests pass AND a commit exists referencing its id, call `/task done <id>`. The verification gate in `/task` enforces this.

Do not leave a task half-implemented to start another. Finish or explicitly block (`/task block <id> <reason>`).

## Project Overview

<!-- Replace with your project description -->
**Name:** PROJECT_NAME
**Description:** Brief description of what this project does.
**Tech Stack:** Language, framework, database, etc.
**Platform:** Windows / macOS / Linux / Web / Cross-platform

## Architecture

<!-- Document your project's architecture. Include:
     - Entry points and how the app starts
     - Module/package breakdown with responsibilities
     - Data flow between components
     - External dependencies and integrations
     - Data storage locations and formats
-->

### Entry Flow

<!-- How the application starts and initializes -->

### Module Breakdown

<!-- List each module/package with its responsibility -->

### Data Storage

<!-- Where user data, config, logs, etc. are stored -->

## Development Commands

```bash
# Install dependencies
# npm install / pip install -r requirements.txt / etc.

# Run development server
# npm run dev / python main.py / etc.

# Run tests
# npm test / pytest / etc.

# Build for production
# npm run build / python setup.py build / etc.

# Lint / type check
# npm run lint / mypy . / npx tsc --noEmit / etc.
```

## Code Standards

- **Language:** All code, comments, variable names, and identifiers must be in English.
- **No emojis:** Do not use emojis anywhere in code, comments, or responses.
- **Formatting:** Follow the conventions already established in the project.

<!-- Add language-specific standards below -->
<!-- Examples:
- Python: PEP 8, max 100 chars/line, f-strings, type hints on new functions, snake_case.
- JavaScript: ES2022+, const by default, camelCase, PascalCase for classes.
- TypeScript: Strict mode, functional components, explicit return types.
- CSS: Utility-first (Tailwind) or BEM naming. Theme tokens in variables.
-->

## File Organization

- Max ~200 lines per file. Split by responsibility if a module grows beyond that.
- One module = one responsibility. Do not put unrelated logic in the same file.
- New files must fit into the existing directory structure.
- Do not create "utils" or "helpers" dump files. Keep feature-specific utilities in that feature's module.

## Protected Files

<!-- List files that should not be edited without explicit confirmation.
     These are enforced by the pre_guard_release_files.py hook. -->

The following files are protected by a pre-commit hook and require explicit user confirmation to edit:

- `package.json` / `package-lock.json`
- Build scripts and configuration
- CI/CD pipeline files
- Release/changelog files

> Update the `PROTECTED_EXACT` set in `.claude/hooks/pre_guard_release_files.py` to match your project.

## Git and Commits

- Use conventional commit format: `type(scope): description`
  - Types: feat, fix, refactor, style, docs, chore, test, build
  - Scopes: define per-project (e.g., api, ui, auth, db, build)
  - Example: `feat(api): add rate limiting to /users endpoint`
- Keep commit messages in English, concise, imperative mood.
- One logical change per commit. Do not bundle unrelated changes.
- Reference the TODO.md task id in the commit subject when applicable: `feat(api): add rate limit (t-42)`.
- Commits are authored by the user via local git config. Do NOT add `Co-Authored-By: Claude` trailers to commit messages.

## What NOT to Do

- Do not add `console.log` / `print()` for debugging. Use proper logging.
- Do not add TODO comments. Track work in TODO.md, DEFERRED.md, or the issue tracker.
- Do not write defensive code against impossible states.
- Do not add polyfills unless the minimum supported version requires them.
- Do not add external dependencies without discussing first.

## Deferred Work

Work that is intentionally postponed goes in `DEFERRED.md` at the repo root.
Each entry must have: what, why deferred, concrete trigger that unblocks it, owner.
See `.claude/TIPS.md` for the format. Do not leave TODO comments in code instead.

## Release

- **Identity**: `PROJECT.yaml` at repo root is the single source of truth for `name`, `display_name`, `version`, `icon`, license, and release config. Every derived manifest (`package.json`, `pyproject.toml`, etc.) follows it.
- **Changelog**: `CHANGELOG.md` uses the Keep a Changelog format. The release workflow extracts notes from the matching `## [x.y.z]` section.
- **Runbook**: See `RELEASE.md` for the end-to-end release procedure (preflight, cut, post-release, rollback).
- **Automation**: `.github/workflows/release.yml` triggers on tag push `v*.*.*`. Release is test-gated, matrix-built per platform, checksum-signed, and draft-first — a maintainer publishes manually.
- **Version bumps**: Use `/release <version>` to do the mechanical steps (bump `PROJECT.yaml`, rotate `CHANGELOG.md`, sync derived manifests, commit, tag). Push is always manual.
- **Identity drift**: If `PROJECT.yaml` disagrees with a derived manifest, `PROJECT.yaml` wins. `/doctor` reports drift; fix it by updating the derived file, never the other direction.
