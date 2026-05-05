---
description: "[TEMPLATE] Multi-agent orchestration: dispatch planner/executor/verifier subagents to run phases end-to-end without manual /clear loops. Default scope: roadmap-wide with milestone-end checkpoints."
---

You are entering **orchestrator mode**. From this point you do not write code, run tests, or modify files yourself. You dispatch the `planner`, `executor`, and `verifier` subagents via the `Task` tool, parse their tail-block output, and decide the next step. Load the `orchestrate` skill (full behavior contract) and follow it strictly.

**Output language.** Read `## Communication` from `CLAUDE.md`. Render the live status stream and the milestone checkpoint prompt in that language. Slash-command names, file paths, sha values, and the protocol JSON itself stay verbatim.

**Output budget.** Per `.claude/docs/output-style.md`. Each worker call is one log line. The milestone checkpoint is ~5 lines. The final summary is ~10 lines. No paragraph-length narration in between.

---

## Argument forms

`$ARGUMENTS` is parsed as follows. Empty arguments default to **roadmap-wide with milestone checkpoints**.

| Form                                  | Scope                                                              |
|---------------------------------------|--------------------------------------------------------------------|
| `/gtr:orchestrate`                    | Current and all later phases in the roadmap. Stop at each milestone end and ask `release / skip-release / stop`. |
| `/gtr:orchestrate <phase-id>`         | One phase only (e.g. `17`, `17-02`). Stop when phase complete.     |
| `/gtr:orchestrate milestone`          | All phases in the **current** milestone only. Stop at milestone end. |
| `/gtr:orchestrate all`                | Same as default `/gtr:orchestrate` (explicit form).                |
| `/gtr:orchestrate forever`            | All phases AND auto-release at every milestone. Continues until `PROJECT.md#success_criteria` are all checked, or a stop condition fires. Implies `--allow-new-phases`. |
| `/gtr:orchestrate resume`             | Re-enter orchestration from the last known cursor. Reconstructs state from `.planning/STATE.md` + git log. |

Flags (any form):

| Flag                       | Effect                                                                                       |
|----------------------------|----------------------------------------------------------------------------------------------|
| `--allow-new-phases`       | Auto-insert new phases when a gap is detected (no prompt). Default: ask first.               |
| `--max-retries <N>`        | Override the per-plan executor retry budget. Default: 3.                                     |
| `--max-replans <N>`        | Override the per-phase planner respawn budget. Default: 2.                                   |
| `--no-verifier`            | Skip the verifier step. Speeds things up but loses the independent check. Not recommended.   |
| `--dry-run`                | Print the spawn plan (which phases, in what order) and exit without spawning anything.       |
| `--auto-release`           | Skip the milestone checkpoint prompt; release automatically. Implied by `forever`.           |

---

## Preflight (abort on any failure)

1. `.claude/.setup-complete` exists. If missing, abort with: "Run `/gtr:setup` first."
2. `.planning/PROJECT.md` and `.planning/ROADMAP.md` both exist. If missing, abort and route to `/gsd:new-project` or `/gsd:create-roadmap`.
3. Working tree is clean (`git status --porcelain` empty). If not, abort: "Commit or stash first — orchestration writes commits."
4. `.planning/STATE.md` exists OR this is the first orchestration run. If missing on a non-first run, abort and tell the user to run `/gsd:progress` once to seed it.
5. Workers are reachable: agents `planner`, `executor`, `verifier` are loaded. If a Task call fails with "unknown subagent", abort.

For `resume`: skip preflight check 3 (clean tree) — resume can pick up after a crash that left files mid-write. But warn the user and ask for confirmation.

---

## Procedure

1. **Resolve scope.** From the argument form + `.planning/ROADMAP.md` + `.planning/STATE.md`, build the ordered list of (phase, sub-plan) tuples to process. Print the list under the heading `ORCHESTRATE PLAN` and ask the user to confirm before spawning the first worker (skip this confirmation in `forever` and `resume` modes).
2. **Loop.** For each (phase, sub-plan) in order:
   1. Spawn `planner` with `phase`, `subplan`, optional `feedback`. Parse tail-block. If `blocked`, follow the new-phase rule from the `orchestrate` skill.
   2. Spawn `executor` with `plan` path. Parse tail-block. On `fail`, follow retry policy.
   3. Unless `--no-verifier`: spawn `verifier` with `plan` and `sha`. Parse tail-block. On `verdict: fail`, route reasons back to executor and retry.
   4. Write a one-line log entry per worker (see `orchestrate` skill).
   5. When a phase is fully closed (all sub-plans verified), append a `phase X done.` line.
3. **Milestone boundary.** When the last phase of a milestone is closed, print the checkpoint block and wait for the user (or auto-release in `forever` / `--auto-release`).
4. **Stop conditions** are checked after every worker call. See the `orchestrate` skill for the full list.
5. **Final summary.** When the scope's queue is empty (or a stop condition halted it), print:
   ```
   Orchestration complete (or halted).
   Phases done: <list>
   Phases halted: <list with reason>
   Total commits: <N>
   Releases cut: <list>
   ```

---

## Spawn prompt templates

Use these when calling the `Task` tool. Replace `{...}` with concrete values.

### Planner

```
Spawn type: planner

Inputs:
  phase: {phase-id}
  subplan: {next un-planned letter, or omit}
  feedback: {prior failure reasons, or omit}

Run /gsd:plan-phase {phase} ({subplan}). Capture the resulting PLAN.md path.
Emit your tail-block as the final line. Don't /clear, don't ask the user
questions, don't implement code.
```

### Executor

```
Spawn type: executor

Inputs:
  plan: {relative-path-to-PLAN.md}
  feedback: {prior failure reasons, or omit}
  max-task-failures: {number, default 1}

Run /gsd:execute-plan {plan}. Atomic commit per task per GSD protocol.
Capture HEAD sha, files changed, test result. Emit tail-block. Don't expand
scope, don't replan, don't /clear.
```

### Verifier

```
Spawn type: verifier

Inputs:
  plan: {relative-path-to-PLAN.md}
  sha: {executor-HEAD-sha}

Read the plan and the diff range up to sha. Run the project's test suite.
Decide pass/fail per the plan's acceptance criteria. Emit tail-block. You
have no Write or Edit — do not patch anything.
```

---

## Tail-block parsing

After each `Task` returns the worker's full output, run:

```bash
echo "{worker-output}" | python .claude/scripts/orchestrate_protocol.py parse
```

The script prints the parsed JSON or exits 1 if no tail-block is present. Treat exit 1 as a worker failure (retry once with stricter wording, then halt).

The script's `emit` subcommand is documented for workers; the orchestrator does not emit, only parses.

---

## When to halt and surface to user

- A `Task` call itself errors (not the worker — the tool). Print the error, stop.
- A worker emits `status: blocked` and the new-phase rule says "ask".
- An executor diff would add an external dependency or change > 500 lines in one commit.
- Retry budgets exhausted on the same phase.
- Verifier `verdict: fail` with the same reasons twice in a row (loop detected).

When halting, leave the working tree as-is (don't try to clean up or revert) so the user can inspect.

---

## Notes

- Orchestration runs in the **main session**, not in a subagent. The orchestrator IS the main Claude. It must keep its own context lean (the whole point of the architecture).
- Workers know the protocol from their agent definitions in `.claude/agents/`. You don't need to repeat the protocol contract in every spawn prompt — keep prompts short.
- For the architecture explainer, see `.claude/docs/orchestration.md`.
