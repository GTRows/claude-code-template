---
description: "[TEMPLATE] Health check the template state: setup marker, plugins, CLAUDE.md placeholders, TODO.md, hooks, secret leakage."
---

Read-only diagnosis of the template's state in this project. Do NOT fix anything without asking. Print results grouped under the headings below.

---

## 1. Setup marker

- Does `.claude/.setup-complete` exist?
- If yes → parse and print `date`, `stack`, `type`.
- If no → state: `Not set up. Run /setup.`

---

## 2. `CLAUDE.md` placeholders

Grep `CLAUDE.md` for:

- `PROJECT_NAME`
- Literal `<!-- ` (unresolved comment blocks)
- Placeholder lines starting with `# npm install / pip install`

Report each remaining placeholder as an unresolved item.

---

## 3. Identity drift (`PROJECT.yaml` is source of truth)

If `PROJECT.yaml` exists, verify no drift against derived files:

| Source of truth | Must match |
|-----------------|-----------|
| `PROJECT.yaml#identity.name` | `package.json#name`, `pyproject.toml#project.name`, `Cargo.toml#package.name` |
| `PROJECT.yaml#version` | `package.json#version`, `pyproject.toml` version, `Cargo.toml` version |
| `PROJECT.yaml#version` | Top version header in `CHANGELOG.md` (first `## [x.y.z]` after `## [Unreleased]`) |
| `PROJECT.yaml#identity.icon` | Path exists on disk |
| `PROJECT.yaml#release.platforms` | Matrix entries in `.github/workflows/release.yml` (if workflow exists) |

Also verify `## [Unreleased]` section exists in `CHANGELOG.md`.

Report each mismatch as: `drift: <path> has <value>, expected <PROJECT.yaml value>`. Do NOT auto-fix.

---

## 4. `TODO.md`

- Count Active, Blocked, Done entries.
- For each Blocked task, parse the `(YYYY-MM-DD)` from its block line. If older than 14 days, list it as potentially stale.

---

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
- If the upstream tag is newer, print: `template update available: vX → vY (run /update)`.
- If `gh` and network are unavailable, print: `cannot reach upstream — skipped version drift check`.

## 9. Template manifest drift

- If `.claude/.template-manifest.json` exists, run:
  ```bash
  python .claude/scripts/manifest.py --check
  ```
- Report the list of paths the user has modified relative to the recorded manifest. This is informational only — modifications are normal. Useful before running `/update` so the user knows which files will hit the conflict path.
- If the manifest is missing, suggest running `/update` (which will regenerate it) or `python .claude/scripts/manifest.py --write` to seed it.

---

## Summary

One-line verdict: **Healthy**, **Needs attention**, or **Not set up**.

If `Needs attention`, list the top 3 issues to address, in priority order.

**Do not modify any files.**
