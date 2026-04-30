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
/gtr:setup
```

`/gtr:setup` detects the stack, fills `CLAUDE.md`, writes `PROJECT.yaml`, installs recommended plugins, and sets up task tracking. Idempotent — safe to re-run.

### B. Implement into an existing project

Two options:

1. **Recommended — `/gtr:onboard`**: clone the template into a temp dir, copy in the slash commands and hooks (or have someone copy `.claude/commands/onboard.md` over once), then run:
   ```
   /gtr:onboard
   ```
   The runbook walks you through every file decision interactively (apply / skip / view-diff). Your `README.md`, `package.json`, and existing configs are never touched. See [.claude/commands/onboard.md](./.claude/commands/onboard.md).

2. **Manual** — read [IMPLEMENT.md](./IMPLEMENT.md) and apply the file-by-file plan yourself, or paste the runbook into Claude and ask it to execute step by step.

---

## What's in the box

### Slash commands (`.claude/commands/`)

| Command | Purpose |
|---------|---------|
| `/gtr:menu` | Interactive entry point — pick what to do, Claude routes to the right command. |
| `/gtr:setup` | First-time project wizard. Asks conversation language + i18n, fills CLAUDE.md, installs plugins, scaffolds task files, writes the template manifest. |
| `/gtr:update` | Pull template updates from upstream and merge non-destructively (uses sha-keyed manifest to detect user modifications). |
| `/gtr:doctor` | Read-only health check: setup marker, plugin status, CLAUDE.md placeholders, identity drift, secrets, template version drift, manifest drift. |
| `/gtr:release <ver>` | Prepare a release: bump PROJECT.yaml, rotate CHANGELOG, sync manifests, commit, tag. Never pushes. |
| `/gtr:help` | Discovery: list every template command, hook, and file. |
| `/gtr:new-migration` | Scaffold a DB migration following detected conventions. |

### Hooks (`.claude/hooks/`)

| Hook | Event | Behavior |
|------|-------|----------|
| `pre_guard_release_files.py` | PreToolUse Write/Edit | Blocks edits to protected files (PROJECT.yaml, package.json, CHANGELOG.md, CI configs, lockfiles, ...) |
| `pre_guard_security.py` | PreToolUse Write/Edit | Blocks dangerous patterns (innerHTML, eval, `shell=True`, SQL injection, ...) |
| `pre_guard_env_secrets.py` | PreToolUse Write/Edit | Blocks hardcoded secrets and writes to `.env*` files |
| `post_validate_syntax.py` | PostToolUse Write/Edit | Validates Python / JS / JSON syntax after writes |
| `session_check_setup.py` | SessionStart | Injects `/gtr:setup` reminder when marker is missing |
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
| `.github/workflows/release.yml.template` | Tag-triggered, test-gated, matrix build, checksum, draft-first GitHub Release. Activated by `/gtr:setup` on opt-in. |
| `.github/workflows/ci.yml.template` | Lint + test on push/PR. Activated by `/gtr:setup` on opt-in. |

### Planning (powered by GSD)

The template delegates planning and execution to the **GSD** plugin (`oh-my-claudecode`). GSD writes durable phase plans to `.planning/` and runs each plan in a worktree-isolated subagent — main context stays at ~5% so token cost is predictable.

Two layers:
- **`.planning/` (persistent)** — `PROJECT.md` (vision), `ROADMAP.md` (phases), `STATE.md` (memory), `phases/<N>-<name>/<N>-<P>-PLAN.md` (the plan being executed). Survives sessions.
- **Built-in `TaskCreate` (ephemeral)** — current-session subtask breakdown of the in-flight plan.

Use `/gtr:menu` if you do not want to learn GSD's command names directly. It surfaces every option as a numbered choice and routes to the right `/gsd:*` command underneath.

### Recommended plugins

Installed globally (user scope) by `/gtr:setup`:

| Plugin | What it does |
|--------|--------------|
| `code-simplifier` | Reviews changed code for redundancy and over-engineering |
| `commit-commands` | `/commit`, `/commit-push-pr`, `/clean_gone` |
| `pr-review-toolkit` | Multi-aspect PR review |
| `claude-md-management` | `/revise-claude-md` + CLAUDE.md improver skill |
| `skill-creator` | Author and tune custom skills |
| `security-guidance` | Session-scoped security reminders |
| `oh-my-claudecode` | Autopilot, ralph, ultrawork, deep-dive, plan, team, and more advanced agents (custom marketplace `omc`) |
| `frontend-design` | Distinctive, production-grade frontend code (only installed if project has a UI) |

Plugins live in user scope, so one install covers every project.

---

## Philosophy

- **Single source of truth.** Identity lives in `PROJECT.yaml`. Everything else derives. `/gtr:doctor` reports drift.
- **Hooks over vibes.** Guardrails are enforced by scripts, not reminders. You cannot accidentally commit an `.env` or force-push main.
- **Opt-in over magic.** Release automation and optional hooks are copied on opt-in during `/gtr:setup`, not imposed.
- **Planning lives on disk, not in chat.** Phase plans live under `.planning/` (managed by GSD). Each plan executes in an isolated subagent so the main context stays light.
- **Plugins over bundled skills.** General-purpose capabilities live in global plugins; only project-specific skills go in `.claude/skills/`.
- **Senior-level releases.** Tag-triggered, test-gated, draft-first, checksum-signed, rollback-documented.

---

## Customization

After `/gtr:setup`:

- **Identity**: edit `PROJECT.yaml`. Run `/gtr:doctor` to catch drift in derived manifests.
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
