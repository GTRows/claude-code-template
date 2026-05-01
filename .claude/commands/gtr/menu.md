---
description: "[TEMPLATE] Interactive menu — pick what you want to do, Claude routes to the right command (template or GSD)."
---

You are the **template menu**. Job: ask the user what they want, route to the right slash command. Never invent commands. The menu is the friendly face; the actual work happens in `/gtr:*` (template) or `/gsd:*` (planning).

**Output language.** Read `## Communication` from `CLAUDE.md` and produce all conversational text (menu labels, questions, summaries) in that language. Slash-command names (`/gtr:setup`, `/gsd:plan-phase`), file paths, and code identifiers stay verbatim. If `## Communication` is missing, default to the language the user wrote their request in.

## Behavior

1. **Detect state in parallel:**
   - `.claude/.setup-complete` exists?
   - `IDENTITY.yaml` (or legacy `PROJECT.yaml`) exists?
   - `.planning/` directory exists?
   - `.planning/STATE.md` exists?
2. **Adapt the menu:**
   - If `.claude/.setup-complete` is missing → option 1 stays primary, gray out everything else with `(run /gtr:setup first)` annotation.
   - If `.planning/` is missing → planning options 5-9 invite "start a new plan" rather than "continue".
   - If no identity file exists → hide release options.
3. **Print the menu** (template below).
4. **Ask the user to pick by number or short keyword.**
5. **Gather follow-up answers up front** so the dispatched command does not have to re-prompt.
6. **Dispatch** the corresponding slash command.

## Menu template

```
What do you want to do?

  Setup & health
    1. Set up this project                       /gtr:setup
    2. Health check                              /gtr:doctor
    3. Pull template updates                     /gtr:update
    4. Onboard an existing project               /gtr:onboard

  Planning (powered by GSD)
    5. Start planning a new project              /gsd:new-project
    6. Map an existing codebase first            /gsd:map-codebase
    7. See progress / continue work              /gsd:progress
    8. Plan the next phase                       /gsd:plan-phase
    9. Execute current plan                      /gsd:execute-plan

  Release
   10. Prepare a release                         /gtr:release

  Reference
   11. Detailed help                             /gtr:help
   12. Refresh CLAUDE.md                         /revise-claude-md (plugin)
```

## Follow-up questions per option

| Pick | Follow-up question | Dispatched command |
|------|--------------------|-------------------|
| 5 (new project planning) | `Workflow mode: interactive (confirm each decision) or yolo (auto-approve)?` | `/gsd:new-project` |
| 6 (map codebase) | `Existing repo path? (default: current dir)` | `/gsd:map-codebase` |
| 8 (plan phase) | `Phase number?` | `/gsd:plan-phase <N>` |
| 9 (execute plan) | If multiple `PLAN.md` exist: `Which plan? (numbered list)`. Otherwise default to next un-executed plan. | `/gsd:execute-plan <path>` |
| 10 (release) | `Target version? (e.g. 1.2.3 or 1.2.0-rc.1)` | `/gtr:release <version>` |
| 11 (help) | `Topic? (empty for table of contents, or a command name)` | `/gtr:help [topic]` |

For single-mode picks (1, 2, 3, 4, 7, 12), invoke directly without follow-up.

## First-run hint

If `.claude/.setup-complete` is missing AND `.planning/` is missing, after printing the menu add:

```
First time? Recommended path:
  1 → /gtr:setup           (template scaffolding)
  5 → /gsd:new-project     (project vision and roadmap)
  8 → /gsd:plan-phase 1    (concrete plan)
  9 → /gsd:execute-plan    (build it)

Or pick option 11 (help) for a guided walkthrough.
```

## Guardrails

- Never list more options than the menu above. Do not invent commands.
- If the user types a direct slash command (e.g. `/gsd:progress`), bypass the menu and pass through.
- The menu is for discovery, not for replacing direct invocation.
- Do not output additional commentary, status, or analysis beyond the menu and the follow-up question for the picked option.
