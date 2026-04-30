# Permissions

Three layers in `.claude/settings.json#permissions`:

- `allow` — pre-approve a call, no prompt shown
- `ask` — prompt the user even if the call would normally be silent
- `deny` — block outright, no way to approve in-session

## Defense in depth

Combine `deny` (the cheapest layer — just pattern matching) with Python hooks (the strictest layer — full content inspection). Hooks can catch things the pattern matcher misses (hardcoded secrets inside code), but pattern matching in `deny` is faster and catches the blatant cases early.

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

## Pattern syntax

- `Bash(npm:*)` — any command starting with `npm`
- `Edit(src/**)` — edits under `src/`
- `Bash` — all Bash (no restriction)

## Anti-patterns

- **Never hardcode absolute paths** like `D:/Workspace/...` in `settings.local.json`. Use `${CLAUDE_PROJECT_DIR}` or glob patterns. Hardcoded paths are not portable across machines and break for teammates.
- `settings.local.json` is personal and gitignored. Don't push it.
- Project-wide rules go in `settings.json` (tracked). Personal allowlists go in `settings.local.json` (not tracked).
