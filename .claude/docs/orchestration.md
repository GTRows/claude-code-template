# Orchestration architecture

This doc explains how `/gtr:orchestrate` runs phases end-to-end without the `/clear` + manual-command loop. Read this once; after that, day-to-day use is just typing `/gtr:orchestrate` and watching the live status stream.

## The problem

Manual GSD flow burns wall-clock time on context juggling:

```
/clear  ->  /gtr:next  ->  /gsd:plan-phase 17     (plan)
/clear  ->  /gtr:next  ->  /gsd:execute-plan ...  (execute)
/clear  ->  /gtr:next  ->  /gsd:verify-work       (verify)
/clear  ->  /gtr:next  ->  /gsd:plan-phase 17 ... (next sub-plan)
...
```

Each `/clear` is free, but the human in the loop is the bottleneck. And consolidating the work into a single long-lived session triggers Claude Code's auto-compact at ~70% context usage, which loses fidelity.

## The solution: orchestrator + workers

```
Orchestrator (main session, lives the whole time)
  |  reads .planning/ artifacts, parses worker tail-blocks, decides next step
  |
  |   ----- spawn (Task tool, fresh context) ----->
  |                                                |
  +-- planner   (one PLAN.md, then exit)           |  fresh context per spawn,
  +-- executor  (one PLAN.md execution, then exit) |  closed when worker exits,
  +-- verifier  (one verdict, then exit)           |  orchestrator only sees
                                                   |  the parsed tail-block
```

The orchestrator **never writes code**. It dispatches workers and parses their structured output. Each worker is one `Task` tool call with `subagent_type: planner | executor | verifier`. The worker runs in its own Claude session with a focused system prompt (see `.claude/agents/<name>.md`) and exits when it has emitted the protocol tail-block.

## The protocol

Workers print human-readable narrative for context, then a single tail line as their final output:

```
<<orchestrate-result>>{"status":"ok","path":"...","summary":"..."}<<end>>
```

The orchestrator pipes the worker's full output through `python .claude/scripts/orchestrate_protocol.py parse` to extract the JSON. Everything before the tail is context-only — it never enters the orchestrator's window.

Schema:

| Field      | Required | Who emits it             | Meaning                                              |
|------------|----------|--------------------------|------------------------------------------------------|
| `status`   | always   | every worker             | `ok` (the worker did its job, regardless of verdict), `fail` (worker hit its retry budget), `blocked` (worker can't proceed without orchestrator decision) |
| `path`     | planner  | planner only             | relative path to the written PLAN.md                 |
| `summary`  | optional | every worker             | one-line description for the orchestrator log       |
| `sha`      | executor | executor only            | HEAD commit SHA after execution                      |
| `files`    | optional | executor                 | int — files changed in the plan's commit range       |
| `tests`    | optional | executor                 | `pass` / `fail` / `not-run`                          |
| `verdict`  | verifier | verifier only            | `pass` / `fail`                                      |
| `reasons`  | optional | verifier (with `fail`)   | list of failure reasons                              |
| `reason`   | with fail/blocked | any worker      | short explanation                                    |
| `suggestion` | with blocked | any worker          | concrete next step the orchestrator should take      |

Note: a verifier `verdict: fail` still emits `status: ok` because the verifier itself succeeded — it just observed broken work. `status: blocked` is reserved for "I literally cannot proceed without help" (e.g. no test command exists, plan is unreadable).

## Argument forms and scope

`/gtr:orchestrate <args>`. The default scope is **roadmap-wide with milestone-end checkpoints**.

| Form                          | Scope                                                         |
|-------------------------------|---------------------------------------------------------------|
| (empty)                       | Current and all later phases. Stop at each milestone end and ask. |
| `<phase-id>`                  | One phase only (`17`, `17-02`).                               |
| `milestone`                   | Current milestone only.                                       |
| `all`                         | Same as empty (explicit form).                                |
| `forever`                     | All phases, auto-release at every milestone, until `PROJECT.md#success_criteria` are all met. |
| `resume`                      | Re-enter from the last cursor (reconstructed from `STATE.md` + git log). |

Flags: `--allow-new-phases`, `--max-retries N`, `--max-replans N`, `--no-verifier`, `--dry-run`, `--auto-release`. See `/gtr:help orchestrate` for the full reference.

## Milestone checkpoints

After the last phase of a milestone closes, the orchestrator stops and prints:

```
ORCHESTRATE CHECKPOINT
Milestone <N> (<v>) complete.
  <phases> phases, <commits> commits, tests <pass|fail>.
Action? (release / skip-release / stop)
```

This is the natural release breakpoint — you decide whether what was just built is ship-worthy. `release` invokes `/gtr:release <v>`; `skip-release` continues without releasing; `stop` exits cleanly. `forever` mode and the `--auto-release` flag skip this prompt and pick `release`.

## New-phase detection

While running, a worker may emit `status: blocked` with a suggestion like "phase 17 needs phase 16.1 first (database migration)". By default the orchestrator pauses and asks before inserting a phase. With `--allow-new-phases`, it inserts via `/gsd:insert-phase` and runs the new phase immediately, with verifier in strict mode.

This keeps the human in the loop for roadmap shape decisions while letting the orchestrator handle execution autonomously.

## Retry policy

| Event                                                   | Action                                                          |
|---------------------------------------------------------|-----------------------------------------------------------------|
| Executor `status: fail`                                 | Respawn executor with the failure reasons as feedback. Counter +1. |
| Executor counter hits `--max-retries` (default 3)       | Respawn planner with executor's reasons. Counter resets.        |
| Planner respawns hit `--max-replans` (default 2)        | Halt. Ask user.                                                 |
| Verifier `verdict: fail` with same reasons twice in a row | Halt. Loop detected.                                          |
| Worker `status: blocked`                                | Apply the new-phase rule, or halt and ask.                     |
| Verifier `status: blocked`                              | Halt. Cannot ship without verification.                        |

## Stop conditions

- A retry budget is exhausted (above).
- An executor diff would add a new external dependency (detected via `package.json#dependencies`, `requirements.txt`, `Cargo.toml#dependencies`, `pyproject.toml`). Always pause.
- An executor diff would change > 500 lines in a single commit, unless the plan explicitly authorises.
- Token budget exhausted → Claude Code crash. Resume by running `/gtr:orchestrate resume` in a fresh session.
- User Ctrl+C.
- (`forever` only) `PROJECT.md#success_criteria` are all checked.

## Resume

`/gtr:orchestrate resume` reconstructs state from durable artifacts:

1. `.planning/STATE.md` — the GSD cursor (current phase, last action).
2. Git log since the last `chore(release):` commit — matches commits to plan task IDs.
3. `.planning/phases/*/SUMMARY.md` — closed plans.

From those it computes: last plan executed, was it verified, what's the next un-planned phase. It prints the inferred state and waits for one confirmation before continuing.

State persistence to a JSON file is not in v0.7.0. The above reconstruction works because GSD already writes durable artifacts at every step. v0.7.1 may add `.planning/orchestration/state.json` for richer crash recovery (in-flight worker types, retry counters), but the reconstruction approach is enough to get back on track.

## Token budget

Approximate per-phase costs (rough, varies with project size):

| Actor          | Tokens / phase | Lifecycle                              |
|----------------|----------------|----------------------------------------|
| Orchestrator   | 5-15k          | Lives the whole orchestration session  |
| Planner worker | 30-50k         | One spawn, exits after PLAN.md written |
| Executor worker| 50-100k        | One spawn, exits after commits + summary |
| Verifier worker| 20-40k         | One spawn, exits after verdict         |

Orchestrator's main window grows by ~10k per phase (just the log lines and tail-block JSON, not worker narratives). 4 phases ~= 40k. No `/clear` needed. Workers eat their own context, then close.

## What the orchestrator must NOT do

- Don't read source files just to "understand the project". Workers do that. The orchestrator only reads `.planning/` artifacts and git log.
- Don't run tests or builds. Verifier does.
- Don't write or edit code. Executor does.
- Don't push, release, or modify CI without explicit user approval at a milestone checkpoint.
- Don't `/clear`. Defeats the architecture.

## Limits and caveats

- **Sequential, not parallel.** `Task` calls block until the worker exits. This isn't a performance optimisation — it's a context-isolation trick. If you want parallelism for independent work, see `oh-my-claudecode:ultrawork`, but be aware GSD's roadmap is usually sequentially dependent.
- **Workers cannot pass state to each other directly.** They communicate via files (PLAN.md, commits, SUMMARY.md) and the orchestrator-mediated tail-blocks.
- **A worker's "I'm done" report is intent, not truth.** That's why `verifier` exists — independent confirmation. Don't disable it (`--no-verifier`) unless you have a strong external check.
- **GSD plugin dependency.** Workers call `/gsd:plan-phase`, `/gsd:execute-plan`, `/gsd:verify-work`. If GSD isn't installed, orchestration aborts at preflight.
- **Subagent token costs.** Each spawn pays the system-prompt cost for the agent. Cheap relative to the alternative (long single-window context with auto-compact), but it is a cost — not free.

## Testing the system

You can dry-run without spawning anything:

```
/gtr:orchestrate 17 --dry-run
```

The orchestrator prints the spawn queue (which phases, in what order, expected workers per phase) and exits. Use this when changing scope flags to confirm the queue matches your intent.

For a smoke test of just the protocol (no orchestration):

```bash
python .claude/scripts/orchestrate_protocol.py emit --status ok --field path=foo --field summary="hi" \
  | python .claude/scripts/orchestrate_protocol.py parse
```

Should print the JSON back. If not, something is wrong with the script — file an issue.
