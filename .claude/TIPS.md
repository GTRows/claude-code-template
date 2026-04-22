# Claude Code - Tips, Plugins & Workflow Guide

A reference for getting the most out of Claude Code on this project.

---

## Configuration Files Overview

```
~/.claude/settings.json          # Personal settings (all projects)
~/.claude/CLAUDE.md              # Personal instructions (all projects)
.claude/settings.json            # Project settings (tracked in git)
.claude/settings.local.json      # Local overrides (gitignored)
.claude/hooks/                   # Hook scripts (registered by default)
.claude/hooks/optional/          # Optional hooks (opt-in, not registered)
.claude/commands/                # Custom slash commands
.claude/rules/                   # Optional topic-split rules
CLAUDE.md                        # Project instructions (tracked in git)
DEFERRED.md                      # Postponed work with explicit triggers (optional)
```

---

## Hooks

Hooks are shell commands that run automatically at lifecycle events.
They are configured in `.claude/settings.json`.

### Active Hooks in This Template

| Hook | Event | What it does |
|------|-------|--------------|
| `pre_guard_release_files.py` | PreToolUse Write/Edit | Blocks editing protected release/build files |
| `pre_guard_security.py` | PreToolUse Write/Edit | Blocks dangerous patterns (innerHTML, eval, SQL injection, etc.) |
| `pre_guard_env_secrets.py` | PreToolUse Write/Edit | Blocks hardcoded secrets and writing to .env files |
| `post_validate_syntax.py` | PostToolUse Write/Edit | Validates syntax (Python, JS, JSON) after writes |
| `session_check_setup.py` | SessionStart | Injects a `/setup` reminder when the marker is missing |
| `pre_check_setup.py` | UserPromptSubmit | Injects the same reminder on every prompt until setup is done (does not block) |

### Optional Hooks (opt-in)

Located under `.claude/hooks/optional/`. Not registered in `settings.json` by default.
Enable per project by copying the registration snippet into `settings.json`.

| Hook | Use case |
|------|----------|
| `pre_warn_win32_danger.py` | Windows projects using `winreg` / `ctypes` / `SystemParametersInfo`. Warns on HKLM writes, UAC elevation, advapi32 calls. |

### Hook Exit Codes

- `0` = allow, continue normally
- `2` = **block** + send stderr to Claude as feedback (Claude will retry/fix)
- other = non-fatal warning (shown in verbose mode only)

### Adding a New Hook

1. Create a Python script in `.claude/hooks/`
2. Read JSON from `sys.stdin` -- it contains `tool_name` and `tool_input`
3. Print error message to `sys.stderr` and `sys.exit(2)` to block
4. Register it in `.claude/settings.json` under the right event

```python
import json, sys

data = json.load(sys.stdin)
tool_input = data.get("tool_input", {})
# ... your logic ...
sys.exit(0)  # allow
```

### Available Events

| Event | When |
|-------|------|
| `PreToolUse` | Before a tool runs (can block) |
| `PostToolUse` | After a tool succeeds |
| `UserPromptSubmit` | Before Claude processes your message |
| `Stop` | After Claude finishes responding |
| `Notification` | When Claude needs your attention |
| `SessionStart` | On session start/resume |

---

## MCP Servers (Model Context Protocol)

MCP servers extend Claude with external tools and data sources.

### Install a Server

```bash
# HTTP server (recommended)
claude mcp add --transport http github https://api.githubcopilot.com/mcp/

# Stdio (local process)
claude mcp add --transport stdio myserver -- python /path/to/server.py

# List installed servers
claude mcp list

# Check status inside Claude Code
/mcp
```

### Scopes

- `local` (default) -- this machine only, not shared
- `project` -- stored in `.mcp.json`, tracked in git (shared with team)
- `user` -- all your projects, not shared

```bash
claude mcp add --scope project --transport http github https://api.githubcopilot.com/mcp/
```

---

## Custom Slash Commands

Files under `.claude/commands/*.md` become `/command-name` slash commands.
The frontmatter `description` shows in `/help`. The body is the prompt Claude runs.

### Included in This Template

| Command | Purpose |
|---------|---------|
| `/setup` | First-time project wizard. Detects stack, fills CLAUDE.md, installs plugins, writes setup marker. |
| `/task <sub>` | Manage persistent TODO.md tasks (list, next, add, done, block, update, plan). |
| `/doctor` | Read-only health check (setup marker, plugins, placeholders, identity drift, hooks, secrets). |
| `/release <ver>` | Prepare a release: bump PROJECT.yaml, rotate CHANGELOG, commit, tag. Never pushes. |
| `/tpl` | Lists every template command, hook, and file — the discovery entry point. |
| `/new-migration` | Creates a new DB migration file following the project's conventions. |

All template commands have `[TEMPLATE]` as the first word in their frontmatter
description so they sort together in `/help` and are easy to tell apart from
plugin commands.

Name project commands to avoid collisions with Anthropic plugins
(e.g. `/review` is taken by the pr-review-toolkit plugin — use `/tpl` or
template-prefixed names).

---

## Recommended Plugins (install globally)

`/setup` installs these automatically. They are listed here for manual reference.
Plugins live in user scope and become available in every project.

Certain (installed in every project):

| Plugin | What it does |
|--------|--------------|
| `code-simplifier@claude-plugins-official` | Reviews changed code for redundancy and over-engineering |
| `commit-commands@claude-plugins-official` | `/commit`, `/commit-push-pr`, `/clean_gone` |
| `pr-review-toolkit@claude-plugins-official` | Multi-aspect PR review (comments, tests, errors, types, code, simplify) |
| `claude-md-management@claude-plugins-official` | `/revise-claude-md` + claude-md-improver skill |
| `skill-creator@claude-plugins-official` | Author new skills |
| `security-guidance@claude-plugins-official` | Session-scoped soft reminders for dangerous patterns |

Conditional (install when the stack matches):

| Plugin | Install for |
|--------|-------------|
| `frontend-design@claude-code-plugins` | Any project with a UI layer |

### Manual install / verify

```bash
claude plugin install <plugin>@<marketplace>
claude plugin list
```

Plugin-based skills show up as `plugin-name:skill-name` or directly as
`skill-name` in the available-skills list. Do not copy plugin source into
`.claude/skills/` — keep plugins global and only bundle project-specific
skills into `.claude/skills/`.

### Task trackers (compatible, not bundled)

Vibe Kanban and similar external task boards are compatible with this template's
`TODO.md` flow — they are not mutually exclusive. Treat external boards as the
source of truth for cross-team work; keep `TODO.md` for the handful of items
the AI assistant is actively driving. Do not mirror one into the other.

---

## Permissions (settings.local.json)

Three layers:

- `allow` — pre-approve a call, no prompt shown
- `ask` — prompt the user even if the call would normally be silent
- `deny` — block outright, no way to approve in-session

Defense in depth: combine `deny` (the cheapest layer — just pattern matching)
with Python hooks (the strictest layer — full content inspection). Hooks can
catch things the pattern matcher misses (hardcoded secrets inside code), but
pattern matching in `deny` is faster and catches the blatant cases early.

```json
{
  "permissions": {
    "allow": [
      "Bash(python:*)",
      "Bash(git:*)",
      "Edit(src/**)"
    ],
    "ask": [
      "Bash(git push:*)",
      "Write(.github/workflows/**)"
    ],
    "deny": [
      "Bash(rm -rf:*)",
      "Bash(git push --force:*)",
      "Bash(git reset --hard:*)",
      "Read(**/.env)",
      "Read(**/*.pem)",
      "Write(**/.env)"
    ]
  }
}
```

Pattern syntax:
- `Bash(npm:*)` — any command starting with `npm`
- `Edit(src/**)` — edits under `src/`
- `Bash` — all Bash (no restriction)

### Anti-patterns

- **Never hardcode absolute paths** like `D:/Workspace/...` in `settings.local.json`.
  Use `${CLAUDE_PROJECT_DIR}` or glob patterns. Hardcoded paths are not portable
  across machines and break for teammates.
- `settings.local.json` is personal and gitignored. Don't push it.
- Project-wide rules go in `settings.json` (tracked). Personal allowlists go
  in `settings.local.json` (not tracked).

---

## Releases

Senior-level release flow baked into the template. Key principles:

- **Single source of truth for identity.** `PROJECT.yaml` at repo root owns `name`, `display_name`, `version`, `icon`, license, and release config. Every derived file (package.json, installer metadata, GH release title, tag name, artifact file name) follows it. No drift by design. `/doctor` reports any drift; fix by updating the derived file.
- **Changelog-driven notes.** `CHANGELOG.md` in Keep-a-Changelog format. The release workflow extracts the body of the `## [x.y.z]` section matching the pushed tag and uses it as the GitHub release notes. No ad-hoc descriptions.
- **Tag-triggered, test-gated, draft-first.** `.github/workflows/release.yml` runs on push of `v*.*.*` tags. It runs tests first, verifies a CHANGELOG entry exists for the version, builds in a matrix per platform, computes SHA-256 checksums, creates a **draft** GitHub Release with artifacts + notes attached, and stops. A maintainer publishes manually.
- **Versioning.** Semver only. Tag format `v<version>`. Pre-release suffixes (`-rc.1`, `-beta.2`, ...) must match `PROJECT.yaml#release.prerelease_tags` — workflow detects and flags the release as pre-release automatically.
- **Artifact naming contract.** `{name}-v{version}-{platform}.{ext}`. Binary name matches `PROJECT.yaml#identity.name`, so repo slug, binary, and release asset all agree.
- **Screenshots.** Under `assets/release/v<version>/`. Embed into the draft release body manually before publishing.
- **Rollback.** Never delete a pushed tag. Patch-forward, or mark the broken release as pre-release with a notice. See `RELEASE.md` for procedures.

Mechanics handled by `/release <version>`:
1. Validates version (semver regex), tag doesn't exist, `CHANGELOG.md#Unreleased` has content, working tree clean.
2. Bumps `PROJECT.yaml#version`.
3. Rotates `CHANGELOG.md`: renames `## [Unreleased]` → `## [version] - <date>`, inserts a fresh `## [Unreleased]`.
4. Syncs `package.json` / `pyproject.toml` / `Cargo.toml` version if they exist.
5. Commits and tags locally. Does **not** push — you review, then `git push && git push --tags`.

When `/setup` detects that a project wants release automation, it copies `release.yml.template` to `.github/workflows/release.yml` and flags the REPLACE markers (test command, per-platform build command) for customization.

---

## First-Time Setup Flow

When you clone this template into a new project, the setup state is:

1. `.claude/.setup-complete` does not exist.
2. `CLAUDE.md` has `PROJECT_NAME` and placeholder blocks.
3. `TODO.md` exists with empty sections.
4. The `SessionStart` and `UserPromptSubmit` hooks inject a reminder into Claude's context (soft nudge, no blocking).

The reminder tells Claude to recommend `/setup` before starting implementation
work. It does not stop the user from asking read-only questions or doing
template maintenance.

Run `/setup` once. It:
1. Detects the stack from `package.json`, `pyproject.toml`, `go.mod`, etc.
2. Fills CLAUDE.md placeholders with concrete values.
3. Opens TODO tasks for sections it could not fill (architecture, module breakdown, data storage, commit scopes).
4. Asks whether this is a fork or primary repo; appends the right branch strategy block.
5. Installs the recommended plugins via `claude plugin install`.
6. Writes `.claude/.setup-complete` and adds it to `.gitignore`.

After `/setup` finishes, the reminder hook goes silent and normal work proceeds.
`/setup` is idempotent — re-running it refreshes detected values.

---

## DEFERRED.md Convention (optional)

For work you postpone intentionally — "we'll do this when X happens" —
log it in a root-level `DEFERRED.md` instead of a TODO comment in code.

Each entry should have:
- **What** — one line describing the deferred work
- **Why deferred** — the reason it is not being done now
- **Trigger** — the concrete condition that unblocks it
- **Owner** — who brings it back on the table

Example:

```markdown
## Switch Postgres to managed instance
- Why deferred: current workload fits the self-hosted container; cost not yet justified
- Trigger: monthly DB CPU > 60% sustained for 7 days, OR team > 5 engineers
- Owner: infra
```

Why this works: TODO comments rot silently in code. `DEFERRED.md` makes the
decision explicit and gives you a trigger to revisit it.

---

## CLAUDE.md Best Practices

- Keep it under 200 lines -- longer files waste context
- Use concrete rules, not vague guidelines
- Split into topic files using `.claude/rules/*.md` for large projects
- Use `@filename` imports to reference other docs
- Use path-specific rules (only loaded for matching files):

```markdown
---
paths:
  - "src/**/*.py"
---
# Python-specific rules for this module
- Use type hints on all public functions
```

---

## Useful Claude Code Commands

| Command | What it does |
|---------|-------------|
| `/memory` | View and manage Claude's memory & loaded rules |
| `/mcp` | Check MCP server status |
| `/config` | Edit settings |
| `/clear` | Clear context (new session) |
| `/compact` | Compress context when it gets long |
| `Shift+Tab` | Toggle auto-accept edits mode |
| `Ctrl+R` | Interrupt Claude mid-response |

---

## Workflow Tips

### Start sessions with context
Add a `SessionStart` hook to inject project reminders:
```json
{
  "hooks": {
    "SessionStart": [{
      "matcher": "startup",
      "hooks": [{
        "type": "command",
        "command": "echo 'Reminder: English only. No emojis. Run tests before commit.'"
      }]
    }]
  }
}
```

### Use CLAUDE.md for architecture decisions
Document *why* decisions were made, not just what they are.
Claude will apply that reasoning when making related changes.

### Scope your requests
Instead of "fix the UI", say "fix the scaling bug in `gui.py:MonitorPreviewWidget`".
Smaller, precise requests produce better results.

### Use Plan Mode for risky changes
Press `Shift+Tab` twice or use `/plan` to enter plan mode where Claude
proposes changes before executing them. Good for refactors and migrations.

### Leverage sub-agents with the Agent tool
For tasks like "explore codebase and find all API calls", Claude
can spawn a focused sub-agent that searches without polluting the main context.

---

## Windows-Specific Notes

- Hook commands run in bash (Git Bash). Use `python` not `python3`.
- `$CLAUDE_PROJECT_DIR` is set to the project root automatically.
- For PowerShell notifications: `powershell.exe -Command "..."`
- Path separators: hooks receive Windows paths, use `os.path.normpath()` in Python.

---

## Environment Variables Claude Code Provides to Hooks

| Variable | Value |
|----------|-------|
| `CLAUDE_PROJECT_DIR` | Absolute path to project root |
| `CLAUDE_SESSION_ID` | Current session ID |
| `CLAUDE_TOOL_NAME` | Name of the tool being called (in hook input JSON) |
