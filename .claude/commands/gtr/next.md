---
description: "[TEMPLATE] State-aware advisor: tells you the single next command to run based on the project's current state."
---

You are the **template advisor**. Job: read the project's state, decide the single most useful next command, and tell the user. Do NOT do the work — just point.

**Output budget.** Follow `.claude/docs/output-style.md`. The full response should fit in ~12 lines: 1 command + 1 reason + 2-3 likely next steps + a 5-bullet state snapshot. No paragraphs.

**Output language.** Read `## Communication` from `CLAUDE.md` and produce all explanations in that language. Slash-command names (`/gtr:setup`, `/gsd:plan-phase`), file paths, and code identifiers stay verbatim. If `## Communication` is missing, default to the language the user wrote the request in.

---

## 1. Read state in parallel

Use the **Read** tool, not shell commands (Bash on Windows is Git Bash; PowerShell-style `Test-Path` will fail). Try each of these and treat "file does not exist" as a normal signal — do not retry with another shell:

- `.claude/.setup-complete` (setup marker)
- `CLAUDE.md` (look for `## Communication` and `PROJECT_NAME` literal)
- `IDENTITY.yaml` (look for `name:` value — if it is `PROJECT_NAME` or empty, identity is unfilled)
- `.planning/PROJECT.md` (project vision present?)
- `.planning/ROADMAP.md` (roadmap present?)
- `.planning/STATE.md` (current GSD position, if any)
- `.planning/codebase/STACK.md` (was `/gsd:map-codebase` run?)

Also list `.planning/phases/` (Glob: `.planning/phases/*/`) to see whether any phase directory exists, and `.planning/phases/*/*-PLAN.md` to know whether a plan has been authored.

For brownfield detection, Glob `**/*.{py,ts,tsx,js,jsx,go,rs,java,kt,rb,php}` (ignore `.claude/`, `node_modules/`, `dist/`, `build/`). If 10+ source files exist outside `.claude/`, treat the repo as **brownfield**.

For "in-flight plan" detection, look for the most recent `PLAN.md` under `.planning/phases/` and check whether a sibling `SUMMARY.md` exists (plan finished) or not (plan is open / running).

---

## 2. Decide the next action

Apply these rules in order. The first one that matches is the answer.

| # | Condition | RIGHT NOW                                | Reason |
|---|-----------|-------------------------------------------|--------|
| 1 | No `.claude/.setup-complete`                                                              | `/gtr:setup`                                | Project has not been set up. Setup asks for language first, then fills CLAUDE.md and IDENTITY.yaml. |
| 2 | Setup done; `IDENTITY.yaml#identity.name` is still `PROJECT_NAME` or empty               | `/gtr:setup`                                | Identity file is still placeholder. Re-run setup; it is idempotent. |
| 3 | Setup done; `CLAUDE.md` has no `## Communication` section                                | `/gtr:setup`                                | Conversation language was not bound. Re-run setup so future commands speak your language. |
| 4 | Setup done; brownfield (10+ source files); `.planning/codebase/STACK.md` missing         | `/gsd:map-codebase`                         | Existing code must be indexed before any plan, otherwise plans will invent parallel scaffolding. |
| 5 | Setup done; brownfield; STACK.md present; no `.planning/PROJECT.md`                      | `/gsd:new-project`                          | Codebase is indexed but the project's vision and constraints are not written. |
| 6 | Setup done; greenfield (few/no source files); no `.planning/PROJECT.md`                  | `/gsd:new-project`                          | Brand-new project. Start with the vision. |
| 7 | `PROJECT.md` exists; no `.planning/ROADMAP.md`                                           | `/gsd:create-roadmap`                       | Vision is set but it has not been split into ordered phases. |
| 8 | ROADMAP.md exists; no phase has a `PLAN.md` yet                                          | `/gsd:plan-phase 1`                         | Roadmap is in place. Plan the first phase to get a concrete task list. |
| 9 | A `PLAN.md` exists for the current phase; sibling `SUMMARY.md` is missing                | `/gsd:execute-plan <path-to-PLAN.md>`       | A plan is ready and unfinished. Execute it — every task runs in order with atomic commits. Use the path of the most recent `PLAN.md`. |
| 10| The most recent plan has SUMMARY.md but `/gsd:verify-work` has not been run yet (no fix plan, no verify entry in STATE.md) | `/gsd:verify-work`                          | Last plan finished without manual UAT. Verify before moving on. |
| 11| Verify produced issues; no fix plan                                                      | `/gsd:plan-fix`                             | UAT recorded issues. Plan the fixes the same way as a regular phase. |
| 12| All phases in the current milestone are closed in STATE.md                               | `/gtr:release <version>`                    | Milestone is done. Cut a release. |
| 13| Setup done; STATE.md present; user just opened a session and you cannot tell where they are | `/gsd:progress`                             | Default fallback — let GSD's own progress reporter explain the current cursor. |
| 14| None of the above (rare)                                                                 | `/gtr:menu`                                 | Couldn't infer a next step. Open the interactive menu. |

If multiple rules look applicable, pick the lowest-numbered one — the table is ordered from earliest-stage to latest-stage.

---

## 3. Print the answer

Use exactly this layout. Translate prose to the conversation language; keep command names, paths, and section labels verbatim.

```
RIGHT NOW
  <the single command from the table>

WHY
  <one or two short sentences from the table's reason column,
   adapted to the actual project state you observed>

AFTER THIS (likely next steps)
  <next 1-3 commands the user will probably run, in order>

PROJECT STATE
  - Setup complete:       <yes (date) | no>
  - Conversation language: <value from ## Communication | not set>
  - Identity (IDENTITY.yaml): <name (filled) | placeholder>
  - Project vision (.planning/PROJECT.md): <yes | missing>
  - Roadmap (.planning/ROADMAP.md): <yes | missing>
  - Codebase indexed (.planning/codebase/): <yes | no | n/a (greenfield)>
  - Active plan: <relative path to most recent PLAN.md | none>
  - Active plan finished: <yes (SUMMARY.md present) | in progress | n/a>
```

Examples of `AFTER THIS`:

- After `/gtr:setup` → `/gsd:map-codebase` (brownfield) or `/gsd:new-project` (greenfield).
- After `/gsd:new-project` → `/gsd:create-roadmap`.
- After `/gsd:create-roadmap` → `/gsd:plan-phase 1`.
- After `/gsd:plan-phase <N>` → `/gsd:execute-plan <path>`.
- After `/gsd:execute-plan` → `/gsd:verify-work`.
- After `/gsd:verify-work` (no issues) → `/gsd:plan-phase <N+1>` or `/gtr:release <version>` if milestone is done.

---

## 4. Do not do the work

You are an advisor. Print the answer and stop. Do not invoke the recommended command yourself; the user runs it.

If the user replies "do it" or "go ahead", then dispatch — but the default is print-and-stop.
