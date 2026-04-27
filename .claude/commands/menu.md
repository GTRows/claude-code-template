---
description: "[TEMPLATE] Interactive menu — pick what you want to do, Claude picks the right command."
---

You are the **template menu**. Your job: ask the user what they want, then route to the right slash command (or do the action inline if trivial).

## Behavior

1. Read `TODO.md` Active count (if file exists). Read `.claude/.setup-complete` to detect first-run state.
2. Print the menu below, adapted to current state:
   - If `.claude/.setup-complete` is missing, put `Set up this project (/setup)` as option 1 and mark everything else as `(run /setup first)`.
   - If Active is empty, hide `Run all tasks` and `Pick the next task`.
   - If `PROJECT.yaml` is missing, hide release-related options.
3. Ask the user to pick by number or short keyword.
4. Route to the right command. For multi-mode commands, ask the follow-up here so you do not bounce the user through two prompts.

## Menu template

```
What do you want to do?

  Setup & health
    1. Set up this project                  /setup
    2. Run a health check                   /doctor
    3. Pull template updates                /update

  Tasks
    4. See what's on the list               /task list
    5. Pick the next task                   /task next
    6. Run all tasks end-to-end             /task run
    7. Add a new task                       /task add
    8. Plan a roadmap from a goal           /task roadmap

  Release
    9. Prepare a release                    /release
   10. Cut a pre-release / RC               /release (prerelease)

  Reference
   11. Show every template command          /tpl
   12. Refresh CLAUDE.md from learnings     /revise-claude-md (plugin)
```

## Follow-up questions per option

When the user picks a multi-mode command, ask the routing question **before** invoking it, so Claude already knows the answer when the command runs.

| Pick | Follow-up question | Then run |
|------|--------------------|----------|
| 6 (run all) | `Mode? normal (small queue) / isolated (8+ tasks, each in its own subagent)` | `/task run` (with chosen mode) |
| 7 (add) | `One-line title?` | `/task add <title>` |
| 8 (roadmap) | `One-line goal? (e.g. "ship MVP of feature X")` | `/task roadmap <goal>` |
| 9 (release) | `Target version? (e.g. 1.2.3)` | `/release <version>` |
| 10 (prerelease) | `Target version with suffix? (e.g. 1.2.0-rc.1)` | `/release <version>` |

For single-mode picks (1, 2, 3, 4, 5, 11, 12), invoke directly.

## Guardrails

- Never list more options than the menu above. Do not invent commands.
- Always show the current Active task count next to options 4-6 if Active is non-empty.
- If the user types a slash command directly (e.g. `/task list`), bypass the menu and pass through.
- The menu is for discovery, not for replacing direct invocation.
