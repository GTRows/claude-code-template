# Claude Code Project Template

Drop-in template for starting new projects with [Claude Code](https://claude.ai/code). Pre-configured hooks, slash commands, task tracking, and a tag-gated release pipeline, plus curated plugin recommendations.

---

## Two ways to use it

### A. Fresh project from the template

```bash
# 1. Clone as a new project (or use "Use this template" on GitHub)
git clone https://github.com/GTRows/claude-code-template.git my-project
cd my-project
rm -rf .git
git init && git add -A && git commit -m "chore: bootstrap from template"

# 2. Remove the per-clone setup marker that ships with the template repo
rm -f .claude/.setup-complete

# 3. Open Claude Code and run the wizard in a fresh session
claude
# then inside Claude Code:
/setup
```

`/setup` detects the stack, fills `CLAUDE.md`, writes `PROJECT.yaml`, installs recommended plugins, and sets up task tracking. Idempotent — safe to re-run.

### B. Implement into an existing project

Open Claude Code inside your existing repo and say:

> Implement https://github.com/GTRows/claude-code-template into this project. Follow IMPLEMENT.md from the template repo.

Claude will clone the template, merge hooks and commands non-destructively, leave your `README.md` and existing configs untouched, and run `/setup` when done. See [IMPLEMENT.md](./IMPLEMENT.md) for the exact runbook.

---

## What's in the box

### Slash commands (`.claude/commands/`)

| Command | Purpose |
|---------|---------|
| `/setup` | First-time project wizard. Fills CLAUDE.md, installs plugins, scaffolds task files. |
| `/task <sub>` | Persistent TODO.md tasks. Subcommands: `list`, `next`, `run`, `add`, `done`, `block`, `update`, `plan`, `roadmap`. `run` works through the whole Active queue end-to-end; `roadmap <goal>` generates a phased plan, asks you which proposals to drop, then writes the rest to TODO.md. |
| `/doctor` | Read-only health check: setup marker, plugin status, CLAUDE.md placeholders, identity drift, secrets. |
| `/release <ver>` | Prepare a release: bump PROJECT.yaml, rotate CHANGELOG, sync manifests, commit, tag. Never pushes. |
| `/tpl` | Discovery: list every template command, hook, and file. |
| `/new-migration` | Scaffold a DB migration following detected conventions. |

### Hooks (`.claude/hooks/`)

| Hook | Event | Behavior |
|------|-------|----------|
| `pre_guard_release_files.py` | PreToolUse Write/Edit | Blocks edits to protected files (PROJECT.yaml, package.json, CHANGELOG.md, CI configs, lockfiles, ...) |
| `pre_guard_security.py` | PreToolUse Write/Edit | Blocks dangerous patterns (innerHTML, eval, `shell=True`, SQL injection, ...) |
| `pre_guard_env_secrets.py` | PreToolUse Write/Edit | Blocks hardcoded secrets and writes to `.env*` files |
| `post_validate_syntax.py` | PostToolUse Write/Edit | Validates Python / JS / JSON syntax after writes |
| `session_check_setup.py` | SessionStart | Injects `/setup` reminder when marker is missing |
| `pre_check_setup.py` | UserPromptSubmit | Injects the same reminder on every prompt until setup completes (soft, never blocks) |
| `optional/pre_warn_win32_danger.py` | opt-in | Warns on HKLM writes, `SystemParametersInfo`, UAC elevation, `advapi32` calls |

### Permissions (`.claude/settings.json`)

Three layers:
- **deny** — `rm -rf`, `git push --force`, `git reset --hard`, `.env` / private key reads and writes
- **ask** — publish commands, `git push`, edits to `.claude/` and workflow files
- **allow** — managed per-user in `settings.local.json` (gitignored)

### Release pipeline

| File | Role |
|------|------|
| `PROJECT.yaml` | Single source of truth for name, display_name, version, icon, license, release config. Every derived manifest follows it. |
| `CHANGELOG.md` | Keep-a-Changelog format. Release notes extracted from `## [x.y.z]` section matching the pushed tag. |
| `RELEASE.md` | End-to-end runbook: preflight, cut, post-release, rollback, versioning rules. |
| `.github/workflows/release.yml.template` | Tag-triggered, test-gated, matrix build, checksum, draft-first GitHub Release. Activated by `/setup` on opt-in. |
| `.github/workflows/ci.yml.template` | Lint + test on push/PR. Activated by `/setup` on opt-in. |

### Task tracking

Two layers — do not conflate:
- **TODO.md (persistent)** — cross-session tasks with ids (`t-N`) and acceptance criteria. Managed via `/task`.
- **Built-in `TaskCreate` (ephemeral)** — subtask breakdown for the current Claude Code session only.

A verification gate in `/task done` checks: acceptance met, test present (or waived), commit exists referencing the task id.

### Recommended plugins

Installed globally (user scope) by `/setup`:

| Plugin | What it does |
|--------|--------------|
| `code-simplifier` | Reviews changed code for redundancy and over-engineering |
| `commit-commands` | `/commit`, `/commit-push-pr`, `/clean_gone` |
| `pr-review-toolkit` | Multi-aspect PR review |
| `claude-md-management` | `/revise-claude-md` + CLAUDE.md improver skill |
| `skill-creator` | Author and tune custom skills |
| `security-guidance` | Session-scoped security reminders |
| `frontend-design` | Distinctive, production-grade frontend code (only installed if project has a UI) |

Plugins live in user scope, so one install covers every project.

---

## Philosophy

- **Single source of truth.** Identity lives in `PROJECT.yaml`. Everything else derives. `/doctor` reports drift.
- **Hooks over vibes.** Guardrails are enforced by scripts, not reminders. You cannot accidentally commit an `.env` or force-push main.
- **Opt-in over magic.** Release automation and optional hooks are copied on opt-in during `/setup`, not imposed.
- **Two-tier tasks.** Persistent work lives in `TODO.md` across sessions; ephemeral breakdown lives in Claude's built-in task list within a session.
- **Plugins over bundled skills.** General-purpose capabilities live in global plugins; only project-specific skills go in `.claude/skills/`.
- **Senior-level releases.** Tag-triggered, test-gated, draft-first, checksum-signed, rollback-documented.

---

## Customization

After `/setup`:

- **Identity**: edit `PROJECT.yaml`. Run `/doctor` to catch drift in derived manifests.
- **Protected files**: adjust `PROTECTED_EXACT` / `PROTECTED_DIRS` in `.claude/hooks/pre_guard_release_files.py`.
- **Security patterns**: extend `DANGEROUS_PATTERNS` in `.claude/hooks/pre_guard_security.py` for project-specific sinks.
- **Secret patterns**: extend `SECRET_PATTERNS` in `.claude/hooks/pre_guard_env_secrets.py` for vendor token formats.
- **Release platforms**: edit `PROJECT.yaml#release.platforms` and the matrix in `.github/workflows/release.yml`.
- **Permissions**: project-wide rules in `.claude/settings.json`; personal allowlists in `.claude/settings.local.json`.

See `.claude/TIPS.md` for the long-form reference (hooks API, MCP servers, permissions, workflow tips).

---

## Requirements

- Claude Code (`claude` CLI)
- Python 3.10+ (for hooks)
- Git
- Node.js — only for JS syntax validation in `post_validate_syntax.py`

---

## License

This template itself is unlicensed — add a LICENSE appropriate to your project after cloning. The hooks, commands, and configuration files are provided as-is and are free to adapt.
