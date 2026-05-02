---
description: "[TEMPLATE] Detailed help for /gtr:* and /gsd:* commands. Pass a topic or command name as argument; no args prints the table of contents."
---

You are the **template help system**. Job: explain commands and topics in depth so the user does not have to memorise GSD or `/gtr:*` namespaces.

**Output language.** Read `## Communication` from `CLAUDE.md` and render every human-readable phrase in that language — including the **right-hand description column** of the table-of-contents code block, the section labels above it (e.g. "TOPICS — high-level guides", "GTR COMMANDS — template lifecycle"), the INTENT cheat-sheet phrases in quotes, and every "Why / After this / Topic" body paragraph below.

Keep these tokens verbatim, regardless of language:
- Slash-command names: `/gtr:setup`, `/gsd:plan-phase`, `/commit`, etc.
- File paths and filenames: `CLAUDE.md`, `IDENTITY.yaml`, `.planning/PROJECT.md`, `.claude/.setup-complete`.
- Shell commands inside code blocks: `git push`, `python .claude/scripts/manifest.py --write`.
- Version strings: `v0.6.0`, `0.6.3`.
- Markdown / YAML / config keys: `## Communication`, `release.platforms`, `### Added`.

So a TOC line like `/gtr:doctor    Read-only health check (also predictive)` becomes (when language is Turkish): `/gtr:doctor    Salt-okunur sağlık kontrolü (ön-öngörülü de)`. The slash token stays, the description is translated.

If `## Communication` is missing, default to the language the user wrote the request in. Do **not** fall back to English just because this file is written in English — translate as you print.

`$ARGUMENTS` is the lookup target. Three cases:

1. **No arguments** → print the table of contents (section "Table of contents" below), then a **state-aware "From here" plan** rendered live from the current project's state (see "How to render From here" below). Do NOT dump the full static workflow — the user has already done some of it. Show only the remaining steps in order.
2. **A command name** (e.g. `setup`, `gtr:setup`, `gsd:plan-phase`) → print the corresponding "Command" entry. Match leniently: bare names map to `/gtr:*` first, then `/gsd:*`.
3. **A topic** (e.g. `workflow`, `planning`, `release`, `hooks`, `manifest`, `migration`) → print the "Topic" entry. The full lifecycle (every step, including the ones already done) lives under `Topic: workflow` for users who want the deep version.

Apart from the no-args "From here" block, do not output project-specific analysis, git status, or other freelance suggestions.

---

## How to render "From here" (no-args only)

After the table of contents, inspect the project state with the **Read** tool (not shell — Bash on Windows is Git Bash; PowerShell `Test-Path` will fail). Treat "file does not exist" as a normal signal.

Probe in parallel:
- `.claude/.setup-complete`
- `CLAUDE.md` (look for `## Communication`)
- `IDENTITY.yaml` (is `identity.name` still `PROJECT_NAME`?)
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/STATE.md`
- `.planning/codebase/STACK.md` (was `/gsd:map-codebase` run?)
- Glob `.planning/phases/*/` (any phase directory?) and `.planning/phases/*/*-PLAN.md` (any plan?). For each plan, check sibling `SUMMARY.md` (plan finished) vs missing (plan in progress).

Also Glob `**/*.{py,ts,tsx,js,jsx,go,rs,java,kt,rb,php}` excluding `.claude/`, `node_modules/`, `dist/`, `build/`. 10+ matches => brownfield.

Build a status set, then emit ONLY the remaining steps in order. Each step is one line: a short verb-led label, the exact slash command, and a one-clause why. Cap the list at 5 items; if more remain, end with "... after that, /gtr:help workflow has the full chain."

Skip-rules (do NOT print a step if its precondition is already satisfied):

| Step | Skip when |
|------|-----------|
| Setup                 | `.claude/.setup-complete` exists AND `IDENTITY.yaml#identity.name` is filled (not `PROJECT_NAME`) AND `CLAUDE.md` has `## Communication` |
| Map existing codebase | greenfield (few/no source files) OR `.planning/codebase/STACK.md` already present |
| Project vision        | `.planning/PROJECT.md` exists |
| Roadmap               | `.planning/ROADMAP.md` exists |
| Plan first phase      | any `.planning/phases/*/*-PLAN.md` exists |
| Execute current plan  | most recent `PLAN.md` already has sibling `SUMMARY.md` |
| Verify                | already verified (skip if `.planning/STATE.md` records verify, OR no plan has been executed yet) |
| Release               | no completed milestone in `.planning/ROADMAP.md` yet |

Format:

```
From here (3 steps left):
  1. <Verb-led label>           <command>
       <one-clause why>
  2. <Verb-led label>           <command>
       <one-clause why>
  3. <Verb-led label>           <command>
       <one-clause why>

For a single-step recommendation see /gtr:next.
For the complete lifecycle see /gtr:help workflow.
```

Translate the labels and "why" lines to the conversation language; keep slash commands and file paths verbatim.

Edge cases:
- Brand-new project with nothing done yet → show 4-5 steps starting at `/gtr:setup`.
- Mid-plan (PLAN exists, no SUMMARY) → first step is `/gsd:execute-plan <path>` followed by verify, then plan next phase.
- Everything done in current milestone → first step is `/gsd:complete-milestone`, then `/gtr:release <version>`.
- All milestones shipped, nothing pending → print `From here: nothing to do — pick the next milestone with /gsd:new-milestone, or /gtr:doctor for a health check.`

---

## Table of contents

```
TOPICS — high-level guides
  workflow      Big picture: from empty repo to shipped release (start here)
  planning      How GSD works, when to use it, when to skip it
  release       Cutting and shipping a release end-to-end
  hooks         Guard hooks, customisation, exit codes
  manifest      Template manifest and what /gtr:update uses it for
  migration     Versioned migrations between template versions
  onboarding    Adopting the template into an existing project
  permissions   allow / ask / deny layers in settings.json

GTR COMMANDS — template lifecycle
  /gtr:next              "What should I do right now?" (state-aware advisor)
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

INTENT -> COMMAND (quick map — pick the row that matches what you want to do)
  "What should I do right now?"                       /gtr:next
  "Set up this project for the first time"            /gtr:setup
  "Read my whole project, summarise structure"        /gsd:map-codebase
  "Define the project's vision and goals"             /gsd:new-project
  "Turn the vision into ordered phases (roadmap)"     /gsd:create-roadmap
  "Walk the roadmap, pick the next phase, plan it"    /gsd:progress  ->  /gsd:plan-phase <N>
  "Break one phase into 5+ atomic tasks"              /gsd:plan-phase <N>
  "Run the whole plan, do every task in order"        /gsd:execute-plan <path-to-PLAN.md>
  "Where am I right now? What is next?"               /gsd:progress
  "Resume after a break"                              /gsd:resume-work
  "Stop mid-plan and save context"                    /gsd:pause-work
  "Append a new phase to the current milestone"       /gsd:add-phase
  "Squeeze an urgent task between two phases"         /gsd:insert-phase <after-N> "<description>"
  "Manually test what was just built"                 /gsd:verify-work
  "Plan fixes from UAT issues"                        /gsd:plan-fix
  "Mark milestone done and prepare next version"      /gsd:complete-milestone
  "Health check the template state"                   /gtr:doctor
  "Cut a release (bump version, tag, etc.)"           /gtr:release <version>
  "Pull upstream template updates into this project"  /gtr:update
  "Forgot the command name"                           /gtr:menu  (or  /gtr:help <name>)

Recommended learning path:
  1. /gtr:help workflow      — see how the pieces connect end-to-end
  2. /gtr:help planning      — understand the GSD model in depth
  3. /gtr:help onboarding    — if applying to existing project
  4. /gtr:help release       — when ready to ship
```

---

## Reference: full lifecycle (printed only via `/gtr:help workflow`)

This is the canonical, state-blind list of every step. The no-args case prints only the **remaining** steps via the "How to render From here" instructions above; this section is the deep reference for users who want to see the whole chain.

1. **Setup** — `/gtr:setup` (asks language first, fills CLAUDE.md and IDENTITY.yaml, installs plugins, writes `.claude/.setup-complete`).
2. **Read existing code** (only if brownfield) — `/gsd:map-codebase` produces `.planning/codebase/*.md` so later plans see real architecture.
3. **Vision** — `/gsd:new-project` writes `.planning/PROJECT.md` (why, constraints, success criteria).
4. **Roadmap** — `/gsd:create-roadmap` turns the vision into ordered phases in `.planning/ROADMAP.md`.
5. **Plan one phase** — `/gsd:plan-phase <N>` writes `.planning/phases/<NN>-<name>/<NN>-<P>-PLAN.md` with concrete atomic tasks (this is where one piece of work is split into many tasks).
6. **Execute** — `/gsd:execute-plan <path>` runs every task in the plan in order, atomic commit per task. This is the "run them sequentially" command.
7. **Verify** — `/gsd:verify-work` for manual UAT; failed cases feed `/gsd:plan-fix`.
8. **Loop** — back to step 5 for the next phase. `/gsd:progress` always tells you where you are.
9. **Release** — `/gtr:doctor` -> `/gtr:release <version>` -> `git push --tags`.
10. **Maintain** — `/gtr:update` for upstream template changes, `/gtr:doctor` periodically.

If you forget the command name at any point: `/gtr:menu` (interactive) or `/gtr:help <command-or-topic>` (specific lookup). For the deep version of this list, see `Topic: workflow` below.

---

## Topic: workflow

The whole template-plus-GSD lifecycle, in order. Read this first if you have just cloned the template and do not know where to start.

### Mental model in one paragraph

The template owns *how the project runs* (hooks, identity, releases, updates, onboarding). GSD owns *what to build next* (vision, roadmap, phase plans, execution). You set up the project once with `/gtr:setup`, then you alternate between **planning a phase** and **executing it**, and once a milestone is done you cut a release with `/gtr:release`.

### 0. First-time setup (once per clone)

- **New project / fresh clone**: run `/gtr:setup`. It asks for conversation language *first*, then detects the stack, fills `CLAUDE.md` and `IDENTITY.yaml`, installs plugins, writes `.claude/.setup-complete`. From this point every later prompt and slash-command output speaks the language you picked.
- **Existing project (template adopted into a live repo)**: run `/gtr:onboard` first to merge template files non-destructively, then `/gtr:setup`.
- Stuck on what command to run? `/gtr:menu` is a numbered routing menu.

### 1. Frame the project (once per project, then per milestone)

- Brand-new code: `/gsd:new-project` writes `.planning/PROJECT.md` (vision, constraints, success criteria), then `/gsd:create-roadmap` breaks the vision into phases.
- Existing code: run `/gsd:map-codebase` *first* — it spawns parallel `Explore` agents to produce `.planning/codebase/*.md` (stack, architecture, conventions) so the brief sees real context, not assumptions.
- Want to refine before committing to a roadmap? `/gsd:discuss-milestone` interviews you about scope before any artefact is written.

### 2. Plan one phase at a time

Pick the next phase number from `.planning/ROADMAP.md` and run `/gsd:plan-phase <N>`. Output lands at `.planning/phases/<NN>-<name>/<NN>-<P>-PLAN.md`. Helpers, all optional:

- `/gsd:list-phase-assumptions <N>` — show how Claude is interpreting the phase before it commits to a plan. Catch misreadings cheaply.
- `/gsd:research-phase <N>` — niche research before planning (libraries, APIs, prior art).
- `/gsd:discuss-phase <N>` — Socratic interview to extract constraints you might not have written down.

Multiple plans per phase are supported (`<NN>-01-PLAN.md`, `<NN>-02-PLAN.md`, ...) — useful when a phase has parallel workstreams.

### 3. Execute the plan

Run `/gsd:execute-plan <path-to-PLAN.md>`. Strategy is auto-selected from the plan's checkpoint markup:

- **No checkpoints** → fully autonomous in a worktree-isolated subagent. Main context stays at ~5%. This is the cheap, default mode.
- **Verify checkpoints** → segmented; subagent runs autonomous segments, you review at each gate.
- **Decision checkpoints** → executes in main context for back-and-forth.

Per-task atomic commits land as work proceeds. When the plan finishes, a `SUMMARY.md` is written next to `PLAN.md` and a metadata commit closes the loop.

### 4. Verify and iterate

- `/gsd:verify-work` walks you through manual user-acceptance testing of what just shipped. Issues you record become input for `/gsd:plan-fix`, which produces a follow-up fix plan you execute the same way.
- Repeat until the phase is closed in `.planning/STATE.md`.

### 5. Resume / pause / interrupt

- Coming back after a break? `/gsd:resume-work` restores context from `.planning/STATE.md` and the most recent SUMMARY. `/gsd:progress` is the lighter version — visual progress bar and "what's next" routing.
- Need to stop mid-plan? `/gsd:pause-work` writes a `.continue-here` handoff so the next session picks up cleanly.
- Urgent fix between phases? `/gsd:insert-phase 5 "fix critical auth bug"` makes phase 5.1 without renumbering everything else.

### 6. Cut a release (per milestone)

When the milestone's phases are all closed:

1. `/gtr:doctor` — preflight: CHANGELOG has unreleased entries, `IDENTITY.yaml` and derived manifests agree, plugin pin is fresh.
2. `/gtr:release <version>` — bumps `IDENTITY.yaml#version`, rotates `CHANGELOG.md` (`[Unreleased]` → `[<version>] - <date>`, fresh `[Unreleased]` on top), commits as `chore(release): v<version>`, tags `v<version>`. Never pushes.
3. Manually: `git push && git push --tags`.
4. The `release.yml` workflow drafts a GitHub release. Review the draft, attach screenshots, click Publish.

After the release, `/gsd:complete-milestone` archives the milestone and prepares the next version's roadmap section.

### 7. Keep current

- `/gtr:update` — pulls upstream template changes, runs migrations, reconciles via the sha-keyed manifest. Single update commit, never pushes.
- `/gtr:doctor` — periodic health check (drift, secret leakage, hook registration).

### Quick decision tree

- "Where do I start?" → `/gtr:setup` if `.claude/.setup-complete` is missing, else `/gsd:progress`.
- "What do I do next?" → `/gsd:progress` always answers this.
- "Lost the thread after a long break?" → `/gsd:resume-work`.
- "Need urgent fix between phases?" → `/gsd:insert-phase`.
- "Tiny one-off change (5 lines)?" → just edit and commit. GSD is for non-trivial work.
- "Forgot a command name?" → `/gtr:menu` (interactive) or `/gtr:help <name>` (specific lookup).

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

**Concrete walkthrough (greenfield):**

1. `/gsd:new-project` — interview about vision, constraints, success criteria. Output: `.planning/PROJECT.md` + `.planning/config.json`. In template-managed projects the brief auto-fills from `IDENTITY.yaml` / `CLAUDE.md` / `README.md` and you only confirm or tweak.
2. `/gsd:create-roadmap` — turns the vision into ordered phases. Output: `.planning/ROADMAP.md` (e.g. phase 1 = "auth scaffold", phase 2 = "user CRUD", phase 3 = "billing"). Phases are deliberately coarse-grained; planning happens later, per phase.
3. `/gsd:plan-phase 1` — produces `.planning/phases/01-auth-scaffold/01-01-PLAN.md` with concrete tasks and verification gates. Optionally first run `/gsd:list-phase-assumptions 1` to see how Claude is interpreting the phase.
4. `/gsd:execute-plan .planning/phases/01-auth-scaffold/01-01-PLAN.md` — runs the plan. Atomic commits per task. When the plan finishes, a `SUMMARY.md` lands next to `PLAN.md`.
5. `/gsd:verify-work` — manual UAT. Issues found here become `/gsd:plan-fix` input.
6. Loop: `/gsd:plan-phase 2`, execute, verify, ... until the milestone is closed.
7. Milestone done? `/gsd:complete-milestone` archives it and prepares the next version.

**Concrete walkthrough (brownfield — existing repo):**

The only difference is step 0 — run `/gsd:map-codebase` first. It produces `.planning/codebase/STACK.md`, `ARCHITECTURE.md`, `STRUCTURE.md`, `CONVENTIONS.md`, `TESTING.md`, `INTEGRATIONS.md`, `CONCERNS.md`. Subsequent `/gsd:new-project` and `/gsd:plan-phase` runs read those files so plans respect the existing structure instead of inventing parallel scaffolding.

**Execution strategies (auto-selected by /gsd:execute-plan):**
- *No checkpoints* → fully autonomous in a worktree-isolated subagent. Main context ~5%. Cheap, default.
- *Verify checkpoints* → segmented; each segment runs autonomous, you confirm at each gate.
- *Decision checkpoints* → runs in main context for back-and-forth Q&A.

**When to skip GSD:** very small one-off changes (single bug fix, doc tweak, rename, comment fix). Don't bother creating a plan for a 5-line change. Planning has overhead — it pays off when the work has multiple steps, takes more than one session, or needs to be resumable.

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

## Command: /gtr:next

State-aware advisor. Reads the project's state (setup marker, IDENTITY, CLAUDE.md, `.planning/*`, source-file count) and prints the **single next command** to run, with a short reason and the likely follow-ups.

Use this when you do not know what to do — e.g. just cloned the template, or just came back to the project after a break, or finished a plan and are not sure whether to verify, plan the next phase, or cut a release.

Output layout:

```
RIGHT NOW
  <command>

WHY
  <one-line reason from observed state>

AFTER THIS (likely next steps)
  <next 1-3 commands>

PROJECT STATE
  <bullet list of what was found>
```

Does **not** execute the recommended command. Print-and-stop is the default. If you reply with "do it", the advisor dispatches.

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
- The conversation language for the project is set in `CLAUDE.md` `## Communication`. Help output is rendered in that language — including the description column of the TOC code block. Only slash-command names, file paths, version strings, and shell commands stay verbatim.
