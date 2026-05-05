---
name: orchestrate
description: Behavior rules for the orchestrator session. Loaded by /gtr:orchestrate. Encodes how the orchestrator dispatches planner/executor/verifier workers, parses tail-block results, applies retry policy, and decides milestone checkpoints. Don't load manually unless you are running an orchestration loop.
---

# Orchestrate skill

The orchestrator is the **only** Claude session running when `/gtr:orchestrate` is active. It does not write code, run tests, or modify files directly. It dispatches three subagent types — `planner`, `executor`, `verifier` — via the Task tool, parses their structured tail-block output, and decides the next step. All real work happens in the workers' fresh contexts and is freed when the worker exits.

## Mental model

```
Orchestrator (lives whole session, ~5-15k context per phase)
  |
  +--> Task(planner)   -> spawns fresh worker
  |       returns tail-block JSON, exits, frees its context
  |
  +--> Task(executor)  -> spawns fresh worker
  |       atomic commits in real repo, exits with HEAD sha
  |
  +--> Task(verifier)  -> spawns fresh worker (read-only)
          returns pass/fail verdict, exits
```

The orchestrator never does the work. It dispatches, parses, decides.

## Dispatch protocol

For every worker spawn:

1. Build the spawn prompt with the worker's required inputs (phase number, plan path, feedback, etc.). Include the orchestrator's expectation: emit a tail-block as the final line.
2. Call the Task tool with `subagent_type: planner | executor | verifier` and the prompt.
3. Capture the worker's full output text. Pass it to `python .claude/scripts/orchestrate_protocol.py parse` (stdin) to extract the tail-block JSON. If parsing fails, treat as `{"status":"fail","reason":"missing tail-block"}` and retry once with stricter wording.
4. Persist a short log line in the orchestrator's running summary: `<role> -> <status> [<key field>]`. The user sees this stream live.

## Retry policy

- Planner blocked → orchestrator decides: insert dependency phase (default off — ask user) or abort current branch.
- Executor fail → spawn executor again with `feedback: <reason>`. Counter +1. Default max 3 attempts on the same plan.
- Executor 3x fail → spawn planner with `feedback: <executor-reasons>` to revise the plan. Counter resets. Default max 2 plan-respawns per phase.
- Verifier fail (`status: ok`, `verdict: fail`) → spawn executor again with `feedback: <verifier-reasons>`. Same retry counter as executor fail.
- Verifier blocked → halt phase, ask user (cannot verify means cannot ship).

When all retries exhausted: HALT, write the phase to the failure section of the orchestrator log, ask the user.

## Stop conditions (always active)

- A worker emits `status: fail` past retry budget.
- Verifier returns `verdict: fail` with the same reasons twice in a row (loop detected).
- Executor would add a new external dependency (detect via diff: `package.json#dependencies`, `requirements.txt`, `Cargo.toml#dependencies`, `pyproject.toml`). Always pause and ask.
- Executor would change > 500 lines in a single commit (unless plan explicitly authorises). Pause and ask.
- Token exhaustion → Claude Code session crash. Resume by re-running `/gtr:orchestrate resume`.
- User Ctrl+C / interrupt.

## Milestone checkpoints

At the end of each milestone (last phase committed and verified), the orchestrator stops and prints:

```
ORCHESTRATE CHECKPOINT
Milestone <N> (<release-version>) complete.
  <count> phases, <count> commits, tests <pass|fail>.
Action? (release / skip-release / stop)
```

- `release` → invoke `/gtr:release <version>`. After release, continue to next milestone.
- `skip-release` → don't release, just continue to next milestone.
- `stop` → exit orchestration cleanly. Print resume hint.

In `forever` mode the default is `release` (no prompt). Other stop conditions still apply.

## New-phase detection (default OFF)

While running, if the executor or verifier reports a missing prerequisite that warrants a new phase (e.g. "phase 17 requires a database migration that doesn't exist"), the orchestrator:

- Default mode: pauses, prints the gap, asks `Approve insert-phase 16.1 "<title>"? (yes / no / edit)`. On yes, runs `/gsd:insert-phase 16 "<title>"`, plans+executes+verifies the new phase, then resumes phase 17 from where it stopped.
- `--allow-new-phases`: skips the prompt, inserts the phase, runs it, resumes — but verifier runs in strict mode for inserted phases (any test fail = halt).

## Resume protocol

`/gtr:orchestrate resume` reconstructs state from durable artifacts:

1. Read `.planning/STATE.md` for the cursor (current phase, last action).
2. Read git log since the last `chore(release):` commit. Match commit messages to plan task IDs.
3. Read `.planning/phases/*/SUMMARY.md` to detect closed plans.
4. Compute: what was the last plan executed? Was it verified? What's the next un-planned phase?
5. Resume from that point. Print the inferred state for the user to confirm before continuing.

State persistence to a JSON file is intentionally NOT in v0.7.0 — the above is good enough to resume reliably. v0.7.1 may add `.planning/orchestration/state.json` for richer crash recovery (retry counters, in-flight worker types).

## Logging

Every worker call writes one line to the orchestrator's live status stream:

```
[hh:mm:ss] phase 17-02 planner   ok       path=.planning/phases/17-body-metrics/17-02-PLAN.md
[hh:mm:ss] phase 17-02 executor  ok       sha=abc1234 files=8 tests=pass
[hh:mm:ss] phase 17-02 verifier  ok       verdict=pass
[hh:mm:ss] phase 17-02 done.
```

Keep these single-line. The orchestrator's main context budget depends on this.

## What the orchestrator must NOT do

- Don't read source files just to "understand the project". Workers do that. The orchestrator only reads `.planning/` artifacts and git log.
- Don't run tests or builds itself. Verifier does that.
- Don't write or edit code files. Executor does that.
- Don't push to remote, create releases, or modify CI. Those stay manual or get explicit user approval at milestone checkpoints.
- Don't call `/clear`. Defeats the purpose — workers' contexts are already isolated.
