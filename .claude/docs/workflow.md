# Workflow tips

## Start sessions with context

Add a `SessionStart` hook to inject project reminders. The template already ships one (`session_check_setup.py`); customise per project if you need stack-specific reminders.

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

## Use CLAUDE.md for architecture decisions

Document *why* decisions were made, not just what they are. Claude will apply that reasoning when making related changes.

## Scope your requests

Instead of "fix the UI", say "fix the scaling bug in `gui.py:MonitorPreviewWidget`". Smaller, precise requests produce better results.

## Use Plan Mode for risky changes

Press `Shift+Tab` twice or use `/plan` to enter plan mode where Claude proposes changes before executing them. Good for refactors and migrations.

## Leverage sub-agents with the Agent tool

For tasks like "explore codebase and find all API calls", Claude can spawn a focused sub-agent that searches without polluting the main context. The OMC plugin's `/oh-my-claudecode:plan`, `/oh-my-claudecode:trace`, `/oh-my-claudecode:autopilot`, and GSD's `/gsd:execute-plan` all use this pattern.

## Windows-specific notes

- Hook commands run in bash (Git Bash). Use `python` not `python3`.
- `$CLAUDE_PROJECT_DIR` is set to the project root automatically.
- For PowerShell notifications: `powershell.exe -Command "..."`.
- Path separators: hooks receive Windows paths. Use `os.path.normpath()` or `Path.as_posix()` in Python.
