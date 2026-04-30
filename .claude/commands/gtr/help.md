---
description: "[TEMPLATE] Detailed help for /gtr:* and /gsd:* commands. Pass a topic or command name as argument; no args prints the table of contents."
---

You are the **template help system**. Job: explain commands and topics in depth so the user does not have to memorise GSD or `/gtr:*` namespaces.

`$ARGUMENTS` is the lookup target. Three cases:

1. **No arguments** → print the table of contents (section "Table of contents" below).
2. **A command name** (e.g. `setup`, `gtr:setup`, `gsd:plan-phase`) → print the corresponding "Command" entry. Match leniently: bare names map to `/gtr:*` first, then `/gsd:*`.
3. **A topic** (e.g. `planning`, `release`, `hooks`, `manifest`, `migration`) → print the "Topic" entry.

Print only the requested entry. Do not output project-specific analysis, git status, or next-step suggestions.

---

## Table of contents

```
TOPICS — high-level guides
  planning      How GSD works, when to use it, when to skip it
  release       Cutting and shipping a release end-to-end
  hooks         Guard hooks, customisation, exit codes
  manifest      Template manifest and what /gtr:update uses it for
  migration     Versioned migrations between template versions
  onboarding    Adopting the template into an existing project
  permissions   allow / ask / deny layers in settings.json

GTR COMMANDS — template lifecycle
  /gtr:menu              Interactive entry point
  /gtr:setup             First-time wizard (also /gtr:setup --extras)
  /gtr:onboard           Merge template into an existing project
  /gtr:update            Pull upstream changes + run migrations
  /gtr:doctor            Read-only health check (also predictive)
  /gtr:release           Bump, rotate CHANGELOG, commit, tag
  /gtr:new-migration     Scaffold a DB migration
  /gtr:new-adr           Scaffold an Architecture Decision Record under docs/adr/
  /gtr:new-skill         Scaffold a project-specific skill under .claude/skills/
  /gtr:new-rule          Scaffold a path-scoped rule under .claude/rules/
  /gtr:help              This help

GSD COMMANDS — planning and execution
  /gsd:new-project       Initialise project vision and roadmap
  /gsd:create-roadmap    Build the roadmap from PROJECT.md
  /gsd:map-codebase      Brownfield: index existing code first
  /gsd:plan-phase        Detailed plan for one phase
  /gsd:execute-plan      Run a plan in an isolated subagent
  /gsd:progress          Where am I, what's next?
  /gsd:resume-work       Restore context after a break
  /gsd:pause-work        Save context mid-plan
  /gsd:insert-phase      Decimal phase between two existing phases
  /gsd:add-phase         Append phase to current milestone
  /gsd:remove-phase      Remove a future phase, renumber
  /gsd:consider-issues   Review .planning/ISSUES.md against codebase
  /gsd:complete-milestone  Archive milestone, prepare next version
  /gsd:plan-fix          Plan UAT fixes from /gsd:verify-work
  /gsd:verify-work       Manual user acceptance testing
  /gsd:research-phase    Ecosystem research before planning a niche phase
  /gsd:list-phase-assumptions  Surface Claude's assumptions before planning
  /gsd:discuss-phase     Articulate vision before planning
  /gsd:discuss-milestone  Decide what next milestone should ship
  /gsd:new-milestone     Create new milestone for existing project
  /gsd:resume-task       Resume an interrupted subagent execution
  /gsd:help              GSD's own command reference

Recommended learning path:
  1. /gtr:help planning      — understand the GSD model first
  2. /gtr:help onboarding    — if applying to existing project
  3. /gtr:help release       — when ready to ship
```

---

## Topic: planning

GSD (Get Shit Done) is a plugin that owns *planning and execution*. The template owns *everything else* (hooks, release pipeline, identity, update mechanism, onboarding).

**Why GSD instead of /task?**
Plans live on disk under `.planning/`. `/gsd:execute-plan` runs each plan in a worktree-isolated subagent, so the main context stays at ~5% usage. This is the token-efficient model. The previous `/task run` approach kept everything in the main context and burned tokens linearly with task count.

**Mental model:**
```
PROJECT.md  -> WHY (vision, constraints, success criteria)
ROADMAP.md  -> WHEN (phases, milestone boundaries)
PLAN.md     -> WHAT (concrete tasks, verification gates)
SUMMARY.md  -> WHAT HAPPENED (per-plan retrospective)
STATE.md    -> WHERE AM I NOW (current position, decisions)
ISSUES.md   -> DEFERRED WORK (with triggers)
```

**Typical session shape:**
- New project: `/gsd:new-project` → `/gsd:create-roadmap` → `/gsd:plan-phase 1` → `/gsd:execute-plan <path>`.
- Existing codebase: `/gsd:map-codebase` *first*, then the same chain.
- Resuming: `/gsd:progress` shows where you are; offers next action.
- Mid-plan interruption: `/gsd:pause-work` writes a `.continue-here` handoff.
- Urgent insertion: `/gsd:insert-phase 5 "fix critical auth bug"` makes phase 5.1.

**When to skip GSD:** very small one-off changes (single bug fix, doc tweak). Don't bother creating a plan for a 5-line change.

---

## Topic: release

End-to-end release flow:

1. **Preflight (`/gtr:doctor`)** — verifies CHANGELOG has unreleased entries, IDENTITY.yaml + derived manifests agree, plans for this version are marked complete.
2. **Cut (`/gtr:release <version>`)** — bumps `IDENTITY.yaml#version`, rotates `CHANGELOG.md` (renames `[Unreleased]` → `[<version>] - <date>`, inserts fresh `[Unreleased]`), syncs derived manifests if present, commits as `chore(release): v<version>`, tags `v<version>`. **Never pushes.**
3. **Push** — manually: `git push && git push --tags`.
4. **Workflow** — `.github/workflows/release.yml` triggers on `v*.*.*`. Test-gates, matrix-builds, generates per-platform `SHA256SUMS`, creates a **draft** release with notes from CHANGELOG.
5. **Publish** — review the draft on GitHub, attach screenshots from `assets/release/v<version>/`, click Publish.
6. **Rollback** — patch-forward (preferred), demote to pre-release, or yank assets. Never delete a published tag. See `RELEASE.md`.

---

## Topic: hooks

Guard hooks live in `.claude/hooks/` and are registered in `.claude/settings.json`.

| Hook | Event | Effect |
|------|-------|--------|
| `pre_guard_release_files.py` | PreToolUse Write/Edit | Blocks edits to identity, build, release, lock files. |
| `pre_guard_security.py` | PreToolUse Write/Edit | Blocks dangerous patterns (innerHTML, eval, shell=True, ...). |
| `pre_guard_env_secrets.py` | PreToolUse Write/Edit | Blocks hardcoded secrets and writes to `.env*`. |
| `post_validate_syntax.py` | PostToolUse Write/Edit | Validates Python / JS / JSON syntax after writes. |
| `session_check_setup.py` | SessionStart | Reminds to run `/gtr:setup` if marker missing. |
| `pre_check_setup.py` | UserPromptSubmit | Same reminder, soft (never blocks). |

**Customisation:** every hook has a clearly-marked `CONFIGURATION` block at the top — add new patterns there. Run the test suite afterwards: `python -m pytest .claude/hooks/tests`.

**Exit codes:** `0` = allow, `2` = block + send stderr to Claude.

---

## Topic: manifest

`.claude/.template-manifest.json` is a sha-256 snapshot of every template-owned file at install time. `/gtr:update` uses it to detect which files the user has modified vs which are still pristine, so upstream changes can be auto-applied to untouched files and conflict-prompted only for modified ones.

Generate or refresh: `python .claude/scripts/manifest.py --write`.
Check drift: `python .claude/scripts/manifest.py --check`.

The manifest is regenerated by `/gtr:setup` (after first run) and by `/gtr:update` (after applying upstream changes). It is committed to git.

---

## Topic: migration

Breaking template changes ship a per-version migration script under `.claude/scripts/migrations/v{X}_{Y}_{Z}.py`. Each script exports `plan(root)` and `apply(root, actions)`. The runner (`.claude/scripts/migrations.py`) discovers, orders, dry-runs, and applies them.

Order in `/gtr:update`:
1. Find upstream version.
2. Check manifest exists (seed if not).
3. **Run migrations** between current and upstream version (this step).
4. Fetch upstream files and reconcile against manifest.
5. Refresh manifest.

Always idempotent. Always snapshots to `.claude/commands.pre-v{X}.{Y}.{Z}/` before reshaping. Always bumps `.claude/VERSION` after each successful migration so partial runs are recoverable.

---

## Topic: onboarding

Two ways to apply the template to an *existing* project:

1. **`/gtr:onboard`** — interactive driver. Walks every file decision (apply / skip / view-diff). Your `README.md`, `package.json`, and existing configs are never touched. Recommended.
2. **Manual via IMPLEMENT.md** — read `IMPLEMENT.md` for the full file-by-file plan and apply by hand.

Both end with a hand-off to `/gtr:setup` for stack detection and CLAUDE.md filling.

---

## Topic: permissions

Three layers in `.claude/settings.json#permissions`:

- **deny** — pattern-matched veto. `rm -rf`, `git push --force`, `.env` reads, private key reads. Fast, no introspection.
- **ask** — prompt the user before allowing. `git push`, `npm publish`, edits to `.claude/`.
- **allow** — pre-approved, no prompt. Project-wide rules in `settings.json`; per-user allowlists in `settings.local.json` (gitignored).

Defense in depth: pattern matching catches blatant cases cheaply, hooks catch subtle ones (e.g. hardcoded secrets inside otherwise-allowed file types).

---

## Command: /gtr:setup

First-time project wizard. Detects the stack, fills `CLAUDE.md`, writes `IDENTITY.yaml`, installs recommended plugins, hands off planning to GSD on opt-in, writes the setup marker.

**Variants:**
- `/gtr:setup` — core flow only.
- `/gtr:setup --extras` — also offers ADR scaffolding, SECURITY.md, CONTRIBUTING.md, CODEOWNERS, dependabot, pre-commit, `.env.example`. Use after the core flow if you want them, or pass it to the first run if you already know you want extras.

**Idempotent.** Re-running refreshes detected values without overwriting your edits.

**Output marker:** `.claude/.setup-complete` (gitignored — per-clone, not per-repo).

---

## Command: /gtr:menu

Interactive entry point. Reads project state (`.claude/.setup-complete`, `IDENTITY.yaml`, `.planning/`) and shows the appropriate numbered menu, asks follow-up questions up front, dispatches the right slash command.

Use this when you do not remember the exact command name.

---

## Command: /gtr:doctor

Read-only health check. Reports:
- Setup marker presence and date.
- CLAUDE.md placeholder text still present.
- Identity drift (`IDENTITY.yaml` vs derived manifests).
- `.planning/` state if GSD is in use.
- Plugin status against the recommended set.
- Hook registration matches files on disk.
- Secret leakage in tracked files.
- Template version drift vs upstream.
- Manifest drift (which template-owned files the user has modified).
- Predictive flags: stale CHANGELOG, no recent release, etc.

Never modifies anything.

---

## Command: /gtr:update

Pulls template updates from `https://github.com/GTRows/claude-code-template`, runs migrations, reconciles file changes via the sha-keyed manifest, prompts on conflicts. Single update commit. Never pushes.

See **Topic: migration** for the run order, and **Topic: manifest** for what the sha tracking does.

---

## Command: /gtr:onboard

Interactive runbook to merge the template into an existing project. Per-file confirmation. Skips `README.md`, `package.json`, and other consumer-owned files. Hands off to `/gtr:setup` afterwards.

See **Topic: onboarding**.

---

## Command: /gtr:release

Mechanical release prep. Bumps version, rotates CHANGELOG, syncs derived manifests, commits, tags. **Never pushes.** Push is always manual after review.

See **Topic: release** for the full flow including the GitHub Actions workflow.

---

## Command: /gtr:new-migration

Scaffolds a database migration following detected conventions. Recognises Alembic (Python), Prisma (Node), sqlx (Rust), and a generic SQL fallback.

---

## Command: /gsd:new-project

Initialise a new project's vision and configuration. Creates `.planning/PROJECT.md` and `.planning/config.json`. Asks for workflow mode (interactive or yolo) up front.

In template-managed projects, the brief auto-fills from `IDENTITY.yaml` + `CLAUDE.md` + `README.md` so you only confirm or tweak.

---

## Command: /gsd:execute-plan

Runs a `PLAN.md` file. Strategy is auto-selected:
- **No checkpoints** → fully autonomous in a subagent. Main context ~5%.
- **Verify checkpoints** → segmented; subagent runs autonomous segments, main context handles checkpoints.
- **Decision checkpoints** → executes in the main context.

Per-task atomic commits. Plan completion produces `SUMMARY.md` and a metadata commit.

---

## Command: /gsd:progress

Reads `.planning/STATE.md` and `.planning/ROADMAP.md`, prints visual progress, recent SUMMARY content, and the next action. Routes to `/gsd:execute-plan` if a plan exists, or `/gsd:plan-phase` if one is missing.

Use this to start every working session — it restores context cheaply.

---

## Command: /gsd:plan-phase

Creates a detailed `PLAN.md` for one phase. Output goes under `.planning/phases/<NN>-<name>/<NN>-<P>-PLAN.md`. Multiple plans per phase supported (`<NN>-01`, `<NN>-02`, ...).

Pair with `/gsd:list-phase-assumptions` first if you want to see how Claude is interpreting the phase before committing to a plan.

---

## Command: /gsd:map-codebase

Brownfield bootstrap. Spawns parallel `Explore` subagents to produce `.planning/codebase/` documents (STACK, ARCHITECTURE, STRUCTURE, CONVENTIONS, TESTING, INTEGRATIONS, CONCERNS).

Run this **before** `/gsd:new-project` on existing repos so the brief sees real context.

---

## Notes

- For commands not listed above, run `/gsd:help` for GSD's own reference.
- All template commands are namespaced under `/gtr:*`. All planning commands are under `/gsd:*`. Plugin commands live in plugin-specific namespaces (e.g. `/commit-commands:commit`).
- The conversation language for the project is set in `CLAUDE.md` `## Communication`. Help output stays English regardless of conversation language.
