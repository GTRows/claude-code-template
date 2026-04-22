---
description: "[TEMPLATE] Manage persistent project tasks in TODO.md. Subcommands: list, next, add, done, block, update, plan."
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
