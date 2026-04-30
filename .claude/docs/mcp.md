# MCP servers (Model Context Protocol)

MCP servers extend Claude with external tools and data sources.

## Install a server

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

## Scopes

- `local` (default) — this machine only, not shared
- `project` — stored in `.mcp.json`, tracked in git (shared with team)
- `user` — all your projects, not shared

```bash
claude mcp add --scope project --transport http github https://api.githubcopilot.com/mcp/
```

For curated MCP server recommendations, see the OMC plugin's `/oh-my-claudecode:mcp-setup` command.
