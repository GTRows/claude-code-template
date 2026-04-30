# Custom slash commands and recommended plugins

## Custom slash commands

Files under `.claude/commands/*.md` become `/<name>` slash commands. Files under `.claude/commands/<ns>/*.md` become `/<ns>:<name>` slash commands. The frontmatter `description` shows in `/help`. The body is the prompt Claude runs.

## Included in this template

| Command | Purpose |
|---------|---------|
| `/gtr:menu` | Interactive entry point — pick what to do, Claude routes to the right command. |
| `/gtr:setup` | First-time project wizard. Detects stack, fills CLAUDE.md, installs plugins, hands off planning to GSD, writes setup marker. |
| `/gtr:onboard` | Interactive runbook to merge the template into an existing project. |
| `/gtr:update` | Pull template updates from upstream and merge non-destructively. |
| `/gtr:doctor` | Read-only health check. |
| `/gtr:release <ver>` | Prepare a release: bump IDENTITY.yaml, rotate CHANGELOG, commit, tag. Never pushes. |
| `/gtr:help` | Detailed reference for `/gtr:*` and `/gsd:*` commands. |
| `/gtr:new-migration` | Creates a new DB migration file following the project's conventions. |

All template commands have `[TEMPLATE]` as the first word in their frontmatter description so they sort together in `/help` and are easy to tell apart from plugin commands.

Name project commands to avoid collisions with Anthropic plugins (e.g. `/review` is taken by the pr-review-toolkit plugin — use template-prefixed names).

## Recommended plugins (install globally)

`/gtr:setup` installs these automatically. They are listed here for manual reference. Plugins live in user scope and become available in every project.

Certain (installed in every project):

| Plugin | What it does |
|--------|--------------|
| `code-simplifier@claude-plugins-official` | Reviews changed code for redundancy and over-engineering |
| `commit-commands@claude-plugins-official` | `/commit`, `/commit-push-pr`, `/clean_gone` |
| `pr-review-toolkit@claude-plugins-official` | Multi-aspect PR review (comments, tests, errors, types, code, simplify) |
| `claude-md-management@claude-plugins-official` | `/revise-claude-md` + claude-md-improver skill |
| `skill-creator@claude-plugins-official` | Author new skills |
| `security-guidance@claude-plugins-official` | Session-scoped soft reminders for dangerous patterns |
| `oh-my-claudecode@omc` | Autopilot, ralph, ultrawork, deep-dive, plan, team — and **GSD planning** which the template hands off to. |

Conditional (install when the stack matches):

| Plugin | Install for |
|--------|-------------|
| `frontend-design@claude-code-plugins` | Any project with a UI layer |

## Manual install / verify

```bash
# omc marketplace must be added first (custom upstream)
claude plugin marketplace add https://github.com/Yeachan-Heo/oh-my-claudecode
claude plugin install <plugin>@<marketplace>
claude plugin list
```

Plugin-based skills show up as `plugin-name:skill-name` or directly as `skill-name` in the available-skills list. Do not copy plugin source into `.claude/skills/` — keep plugins global and only bundle project-specific skills into `.claude/skills/`.

## Task trackers (compatible, not bundled)

Vibe Kanban and similar external task boards are compatible with this template's `.planning/` flow — they are not mutually exclusive. Treat external boards as the source of truth for cross-team work; keep `.planning/` for the handful of items the AI assistant is actively driving. Do not mirror one into the other.

## Useful Claude Code built-ins

| Command | What it does |
|---------|-------------|
| `/memory` | View and manage Claude's memory and loaded rules |
| `/mcp` | Check MCP server status |
| `/config` | Edit settings |
| `/clear` | Clear context (new session) |
| `/compact` | Compress context when it gets long |
| `Shift+Tab` | Toggle auto-accept edits mode |
| `Ctrl+R` | Interrupt Claude mid-response |
