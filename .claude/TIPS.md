# Tips index

This file is a thin index. The long-form reference lives under `.claude/docs/`.

| Topic | File |
|-------|------|
| Hooks (active, optional, exit codes, events, env vars) | [.claude/docs/hooks.md](docs/hooks.md) |
| MCP servers (install, scopes) | [.claude/docs/mcp.md](docs/mcp.md) |
| Custom slash commands and recommended plugins | [.claude/docs/commands.md](docs/commands.md) |
| Permissions (`allow` / `ask` / `deny` layers) | [.claude/docs/permissions.md](docs/permissions.md) |
| Releases (tag pipeline, IDENTITY.yaml, CHANGELOG) | [.claude/docs/releases.md](docs/releases.md) |
| First-time setup flow | [.claude/docs/setup-flow.md](docs/setup-flow.md) |
| Deferred work (GSD ISSUES.md) | [.claude/docs/deferred-work.md](docs/deferred-work.md) |
| CLAUDE.md best practices | [.claude/docs/claude-md-best-practices.md](docs/claude-md-best-practices.md) |
| Workflow tips (Plan Mode, sub-agents, Windows) | [.claude/docs/workflow.md](docs/workflow.md) |

For per-command help see `/gtr:help <command>`. For per-topic guides see `/gtr:help <topic>` (planning, release, hooks, manifest, migration, onboarding, permissions).

## Configuration files at a glance

```
~/.claude/settings.json          # Personal settings (all projects)
~/.claude/CLAUDE.md              # Personal instructions (all projects)
.claude/settings.json            # Project settings (tracked in git)
.claude/settings.local.json      # Local overrides (gitignored)
.claude/hooks/                   # Hook scripts (registered by default)
.claude/hooks/optional/          # Optional hooks (opt-in, not registered)
.claude/commands/                # Custom slash commands (root namespace)
.claude/commands/gtr/            # Template's `/gtr:*` commands
.claude/scripts/                 # Helper scripts (manifest, migrations)
.claude/docs/                    # Long-form reference (this directory)
.claude/rules/                   # Optional topic-split CLAUDE.md rules
CLAUDE.md                        # Project instructions (tracked in git)
IDENTITY.yaml                    # Identity and release config (tracked)
.planning/                       # GSD planning artifacts (optional, opt-in)
```
