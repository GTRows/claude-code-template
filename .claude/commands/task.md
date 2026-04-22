---
description: "[TEMPLATE] Manage persistent project tasks in TODO.md. Subcommands: list, next, run, add, done, block, update, plan."
---

You are managing **persistent, cross-session tasks** stored in `TODO.md` at the repo root.

## Two-tier task model

| Layer | Scope | Tool |
|-------|-------|------|
| `TODO.md` | Durable, cross-session work. Each task has id `t-<n>`, acceptance line, status (Active / Blocked / Done). | This command. |
| `TaskCreate` | Ephemeral subtask list for the current session. Decomposition of the in-flight TODO task. | Built-in. |

Do not mirror `TODO.md` entries into `TaskCreate`, or vice versa.

---

## Invocation

The user invoked `/task $ARGUMENTS`. Parse:

- First whitespace-separated token → subcommand.
- Everything after → args for that subcommand.
- If `$ARGUMENTS` is empty → print the Usage block and stop.

### Usage

```
/task list                  — show Active and Blocked tasks
/task next                  — pick the next Active task and start working on it
/task run                   — work through all Active tasks sequentially, end-to-end
/task add <title>           — append a new Active task
/task done <id>             — move task to Done after verification gate
/task block <id> <reason>   — move task to Blocked with a reason
/task update <id> <text>    — edit an existing task's title or acceptance
/task plan <id>             — break a task into TaskCreate subtasks for this session
```

---

## Before any subcommand

Read `TODO.md`. If it does not exist, create it with the skeleton:

```
# TODO

## Active
## Blocked
## Done
```

Task format inside sections:

```
- [t-42] Short imperative title
  - Acceptance: one-line objective criterion
  - Notes: optional free text (only if meaningfully useful)
```

Ids are monotonic (`t-<n>`). Derive next id by scanning existing ids across all sections and adding 1. Never reuse.

---

## Subcommands

### `list`

Print Active tasks, then Blocked tasks (with reasons). Do not show Done — the user can open the file.

### `next`

1. Pick the lowest-id Active task that is not already in progress.
2. Move it to the top of Active if not already there (order = priority).
3. Announce `Working on {id}: {title}` in one line.
4. Use `TaskCreate` to break it into concrete session subtasks (same shape as `plan`).
5. Start the first subtask.

### `run`

Work through the entire Active queue sequentially, end-to-end per task. Stops only when the queue is empty OR a task cannot complete without human input.

**Preflight (before starting the loop)**

1. Read `TODO.md` Active section. If empty, report `No Active tasks.` and stop.
2. `git status --porcelain` must be empty. If not, stop and ask the user to commit or stash.
3. Print the Active queue (ids + titles, in order).
4. Ask exactly once: `Run <N> Active tasks sequentially? This will edit code, run tests, and create commits. (yes/no)`
5. On anything other than `yes`, stop.

**Per-task procedure**

For each task in Active, lowest id first:

1. Announce: `[task t-<id>] <title>`
2. Read the acceptance criterion. If ambiguous, stop the run and ask the user to clarify (`/task update <id> acceptance: ...`).
3. Break the task into `TaskCreate` subtasks (same as `plan`). Typical shape:
   - Implement the change.
   - Add or update tests that cover the change.
   - Run the test suite.
   - Run lint / type check if the project has one.
4. Execute subtasks in order. Mark each completed as soon as it passes.
5. If tests or lint fail: attempt **one** focused fix. If still failing, stop the run and report which subtask failed.
6. Stage only files touched for this task. Do NOT use `git add -A`.
7. Commit with message `<type>(<scope>): <title> (t-<id>)`. Scope comes from the task or the module touched.
8. Run the `done` verification gate against the task (acceptance met, test exists or waived, commit references id, clean tree for relevant files).
9. On pass → move task to Done with today's date. Continue to the next task.
10. On fail → stop the run and report which gate check failed. Leave the task in Active.

**Abort conditions (stop the run, keep unfinished tasks in Active)**

- `done` gate fails for the current task.
- Tests cannot be made to pass with one fix attempt.
- A protected file needs a user confirmation that the run cannot provide.
- A hook blocks a write and the block is not trivially resolvable.
- Task acceptance is ambiguous or requires a design decision.
- The user interrupts.

**After the loop**

Print a summary:
- Tasks completed (with ids)
- Tasks remaining in Active
- Tasks that caused the abort, if any

Do NOT push. The user pushes when satisfied.

**Non-goals**

- No "skip the test" mode. If the task is testable, tests must pass before `done`.
- Does not touch Blocked tasks.
- Does not install new dependencies or change the stack without asking.

### `add <title>`

Append to Active with the next id. If the title is ambiguous, ask the user for the acceptance line. Otherwise draft a reasonable acceptance and ask for confirmation.

### `done <id>` — verification gate

Do NOT just move the task. Enforce every check below:

1. Acceptance criterion is actually met (verify by inspection, not assertion).
2. If the change is testable, a test exists OR the user explicitly waived it in this session.
3. A commit references the task id (e.g. `feat(api): add rate limit (t-42)`).
4. `git status` is clean for files relevant to the task.

On any failure: report which check failed and stop. Do not move the task.

On success: move to Done with a dated line:

```
- [t-42] 2026-04-21 — Short imperative title
```

### `block <id> <reason>`

Move the task to Blocked. Append `- Blocked: <reason> (YYYY-MM-DD)` under the task.

### `update <id> <text>`

- `<text>` starts with `acceptance:` → replace the Acceptance line.
- Otherwise → replace the title.
- Preserve id and position.

### `plan <id>`

Use `TaskCreate` to break the TODO task into session subtasks. Each subtask should be independently verifiable and typically take one tool round-trip or one file edit. Do NOT modify `TODO.md`.

---

## Guardrails

- Never delete tasks. To retire one, move to Done with a reason, or ask the user first.
- Never rewrite ids.
- Keep `TODO.md` terse — no narrative, no status emojis, no date-stamped progress logs. That belongs in commits.
- If a subcommand would touch more than 5 tasks at once, confirm with the user before writing.
