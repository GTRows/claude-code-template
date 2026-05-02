---
description: "[TEMPLATE] Health check the template state: setup marker, plugins, CLAUDE.md placeholders, planning state (GSD), hooks, secret leakage."
---

Read-only diagnosis of the template's state in this project. Do NOT fix anything without asking. Print results grouped under the headings below.

**Output budget.** Follow `.claude/docs/output-style.md`. One short line per check. Skip checks that pass with no notes — only surface findings worth acting on. Cap the whole report at ~30 lines unless drift is severe.

**Output language.** Read `## Communication` from `CLAUDE.md` and render all explanations, summaries, and recommendations in that language. Section headings, file paths, code blocks, and tool output stay verbatim. If `## Communication` is missing, default to the language the user wrote the request in.

---

## 1. Setup marker

- Does `.claude/.setup-complete` exist?
- If yes → parse and print `date`, `stack`, `type`.
- If no → state: `Not set up. Run /gtr:setup.`

---

## 2. `CLAUDE.md` placeholders

Run the structural checker:

```bash
python .claude/scripts/claude_md_check.py
```

It reports common sections that are present, missing, or still placeholders. None are strictly required — projects may rename or omit any. Surface its output verbatim and treat missing sections as informational, not as failures.

Then grep for legacy markers too:

- `PROJECT_NAME`
- Literal `<!-- ` (unresolved comment blocks)
- Placeholder lines starting with `# npm install / pip install`

Report each remaining hit.

---

## 3. Identity drift (`IDENTITY.yaml` is source of truth)

If `IDENTITY.yaml` exists, verify no drift against derived files:

| Source of truth | Must match |
|-----------------|-----------|
| `IDENTITY.yaml#identity.name` | `package.json#name`, `pyproject.toml#project.name`, `Cargo.toml#package.name` |
| `IDENTITY.yaml#version` | `package.json#version`, `pyproject.toml` version, `Cargo.toml` version |
| `IDENTITY.yaml#version` | Top version header in `CHANGELOG.md` (first `## [x.y.z]` after `## [Unreleased]`) |
| `IDENTITY.yaml#identity.icon` | Path exists on disk |
| `IDENTITY.yaml#release.platforms` | Matrix entries in `.github/workflows/release.yml` (if workflow exists) |

Also verify `## [Unreleased]` section exists in `CHANGELOG.md`.

Report each mismatch as: `drift: <path> has <value>, expected <IDENTITY.yaml value>`. Do NOT auto-fix.

---

## 4. Planning state (`.planning/`)

If `.planning/` exists, this project uses GSD:
- Print current milestone and phase from `.planning/STATE.md`.
- Print phase counts from `.planning/ROADMAP.md`: completed / in-progress / pending.
- If `.planning/ISSUES.md` exists, count open vs closed entries.
- If a phase has been in-progress for more than 14 days (compare timestamps in STATE.md), flag it as potentially stalled.

If `.planning/` does NOT exist, print one line: `No GSD planning artifacts found. Run /gsd:new-project to start, or skip if you do not want phase-based planning.`

No `TODO.md` / `DEFERRED.md` checks — those files were dropped in v0.2.0.


## 5. Installed plugins

Run `claude plugin list`. Cross-check against the recommended set:

**Certain** — should always be installed:
- `code-simplifier@claude-plugins-official`
- `commit-commands@claude-plugins-official`
- `pr-review-toolkit@claude-plugins-official`
- `claude-md-management@claude-plugins-official`
- `skill-creator@claude-plugins-official`
- `security-guidance@claude-plugins-official`
- `oh-my-claudecode@omc` — also verify the `omc` marketplace exists via `claude plugin marketplace list`

**Conditional** — only if the project has a UI:
- `frontend-design@claude-code-plugins`

Report any missing certain-set plugins.

Then run the pin checker:

```bash
python .claude/scripts/plugins.py --check
```

It compares the currently installed plugins against `.claude/plugin-pin.json` (written by `/gtr:setup` after install). Surface the output: missing plugins are flagged, extras are informational.

---

## 6. Hooks

Read `.claude/settings.json`. Confirm:

| Event | Hook file |
|-------|-----------|
| PreToolUse `Write\|Edit` | `pre_guard_release_files.py` |
| PreToolUse `Write\|Edit` | `pre_guard_security.py` |
| PreToolUse `Write\|Edit` | `pre_guard_env_secrets.py` |
| PostToolUse `Write\|Edit` | `post_validate_syntax.py` |
| SessionStart | `session_check_setup.py` |
| UserPromptSubmit | `pre_check_setup.py` |

For each registered hook, confirm the file exists on disk.

---

## 7. Secret leakage

Grep the repo for tracked secrets:

- Files matching `.env` (but NOT `.env.example`)
- Private key markers: `BEGIN RSA PRIVATE KEY`, `BEGIN OPENSSH PRIVATE KEY`, `BEGIN EC PRIVATE KEY`
- Common token prefixes: `sk_live_`, `ghp_`, `xoxb-`, `AKIA`

Exclude: `node_modules/`, `.venv/`, `dist/`, `build/`, `.git/`.

Report only file paths and line numbers — **never print the secret itself**.

---

## 8. Template version

- If `.claude/VERSION` exists, print its content.
- Run `gh release list --repo GTRows/claude-code-template --limit 1 --json tagName --jq '.[0].tagName'` (or `git ls-remote --tags` fallback) to fetch the upstream latest tag.
- If the upstream tag is newer, print: `template update available: vX → vY (run /gtr:update)`.
- If `gh` and network are unavailable, print: `cannot reach upstream — skipped version drift check`.

## 9. Template manifest drift

- If `.claude/.template-manifest.json` exists, run:
  ```bash
  python .claude/scripts/manifest.py --check
  ```
- Report the list of paths the user has modified relative to the recorded manifest. This is informational only — modifications are normal. Useful before running `/gtr:update` so the user knows which files will hit the conflict path.
- If the manifest is missing, suggest running `/gtr:update` (which will regenerate it) or `python .claude/scripts/manifest.py --write` to seed it.

## 10. Predictive health (informational, never blocking)

These are heuristics that surface problems before they bite. Local data only — no network.

- **CHANGELOG churn**: count bullet lines under `## [Unreleased]` in `CHANGELOG.md`. If `> 30`, flag: "Unreleased section is large — consider cutting a release."
- **Release recency**: read the most recent `## [<version>] - <YYYY-MM-DD>` line. If older than 90 days AND `## [Unreleased]` has at least one bullet, flag: "Last release was <N> days ago and there is unreleased work."
- **Plan staleness**: if `.planning/STATE.md` reports an in-flight plan whose timestamp is older than 14 days, flag: "Phase <N> appears stalled."
- **Manifest drift volume**: if `python .claude/scripts/manifest.py --check` reports more than 5 modified files, flag: "Significant manifest drift — `/gtr:update` will require many conflict decisions."
- **Migration backlog**: run `python .claude/scripts/migrations.py --check` against the upstream version (already known from section 8). If migrations are pending, flag: "Schema migrations pending."

Each flag is one short line. Do not score or rank — let the user decide.

## 11. Token usage summary (last 7 days)

If `.claude/usage-log.jsonl` exists, read the last 7 days of records and print:

```
total tokens (last 7 days): <N>
sessions:                   <count>
avg session:                <total / count>
top model:                  <most-used model name>
heaviest session:           <ts>  <total_tokens>  duration <s>
```

If the heaviest single session is more than 5x the average, flag: "One session burned <N>x the average — review what command was running then."

If the file does not exist, print: `no usage log yet (the SessionEnd hook records each session's tokens)`.

## 12. Hook block audit (last 7 days)

If `.claude/hook-audit.log` exists, read the last 7 days of records and print:

```
total blocks (last 7 days):  <N>
by hook:
  pre_guard_release_files:   <count>
  pre_guard_security:        <count>
  pre_guard_env_secrets:     <count>
top blocked path:            <path>  (<count> blocks)
```

If a single hook fired more than 50 times in 7 days, flag: "Hook <name> is blocking unusually often — check its CONFIGURATION block; pattern may be too aggressive for this project."

If the file does not exist, print: `no hook block audit yet (every guard-hook block is recorded)`.

---

## Summary

One-line verdict: **Healthy**, **Needs attention**, or **Not set up**.

If `Needs attention`, list the top 3 issues to address, in priority order.

**Do not modify any files.**
