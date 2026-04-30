# Implementing this template into an existing project

You are reading this because a user asked you (Claude Code) to implement
[claude-code-template](https://github.com/GTRows/claude-code-template) into
their existing project.

Follow this runbook exactly. Do not ad-lib. Ask before any destructive action.

---

## 0. Preconditions

Confirm before touching anything:

- The user's project already has a `.git` directory. If not, stop and tell them to `git init` first.
- The working tree is clean (`git status --porcelain` is empty). If not, stop and ask the user to commit or stash first.
- The user agrees this template will add files to their repo root, `.claude/`, and `.github/`.

Tell the user a one-line summary of what you are about to do and wait for confirmation.

---

## 1. Fetch the template payload

Clone the template to a temp directory:

```bash
git clone --depth 1 https://github.com/GTRows/claude-code-template.git /tmp/ccp-template
```

Read, do NOT blindly copy. Decide per-file whether to merge, skip, or ask.

---

## 2. File-by-file plan

| Source file | Action | Rule |
|-------------|--------|------|
| `.claude/hooks/*.py` | **Copy as-is** | Safe — does not exist in target. |
| `.claude/commands/*.md` | **Copy as-is** | Adds template commands. |
| `.claude/settings.json` | **Merge** | See section 3 below. Never overwrite. |
| `.claude/TIPS.md` | **Copy** | Reference doc. |
| `.claude/VERSION` | **Copy** | Template version pin. |
| `CLAUDE.md` | **Merge carefully** | See section 4. |
| `IDENTITY.yaml` | **Create if missing** | If present, leave it alone. |
| `.planning/` | **Defer to GSD** | Do NOT create. After onboarding, suggest `/gsd:new-project` (or `/gsd:map-codebase` then `/gsd:new-project` for brownfield). The template no longer ships TODO.md / DEFERRED.md — planning is GSD's job. |
| `CHANGELOG.md` | **Ask** | Only if the project does not already have one. |
| `RELEASE.md` | **Ask** | Only if the user wants release automation. |
| `.github/workflows/release.yml.template` | **Copy as `.template`** | Do NOT activate without asking. |
| `.github/workflows/ci.yml.template` | **Copy as `.template`** | Do NOT activate without asking. |
| `.github/PULL_REQUEST_TEMPLATE.md` | **Merge or skip** | Merge only if target has none. |
| `.gitignore` | **Merge** | Append missing lines; do not duplicate. |
| `.editorconfig` | **Copy if missing** | Do NOT overwrite. |
| `README.md` | **NEVER touch** | The user's README stays theirs. |
| `IMPLEMENT.md` | **Skip** | This file is for you, not for the target repo. |

---

## 3. Merging `.claude/settings.json`

If the target has no `.claude/settings.json`, copy ours wholesale.

If one exists:

- Deep-merge `permissions.deny`, `permissions.ask` — union, de-duplicated.
- Deep-merge `hooks.<Event>[].hooks` — add ours if the matching command is not already registered.
- Do NOT remove anything the user had.
- Do NOT touch `permissions.allow` (user-specific).

Show the user the diff before writing.

---

## 4. Merging `CLAUDE.md`

If the target has no `CLAUDE.md`, copy ours and then run `/gtr:setup` (section 8).

If one exists, do NOT overwrite. Instead, offer to add only the sections that are missing:

- `## First-time setup check`
- `## Available commands`
- `## Task workflow`
- `## Release` (only if the user opted into release automation)
- Commit-authorship line under existing `## Git and Commits` if absent.

Show each proposed section to the user and ask yes/no individually.

---

## 5. Hook sanity

The template protects release/build files and blocks secrets. If the target project uses stacks the hooks do not yet cover, offer to extend `PROTECTED_EXACT` in `.claude/hooks/pre_guard_release_files.py`:

- Rust: `Cargo.lock`
- Node pnpm: `pnpm-lock.yaml`
- Node yarn: `yarn.lock`
- Python Poetry: `poetry.lock`
- Python pipenv: `Pipfile.lock`

Do NOT edit the hook without explicit approval.

---

## 6. `.gitignore` merge

Append any lines from the template `.gitignore` that are missing in the target. Always include:

```
.claude/settings.local.json
.claude/.setup-complete
```

Preserve target ordering and comments.

---

## 7. First commit

Stage only what you added or merged. Never use `git add -A` — it may sweep in unrelated dirty files the user forgot about.

Commit message:

```
chore: adopt claude-code-template (<short-sha-or-tag>)
```

Do NOT push. Let the user review and push themselves.

---

## 8. Run `/gtr:setup`

Tell the user:

> I have merged the template. Run `/gtr:setup` now to let me detect your stack
> and fill in `CLAUDE.md` / `IDENTITY.yaml`.

`/gtr:setup` is idempotent. It will not re-do anything that is already filled in.

---

## 9. Clean up

Remove `/tmp/ccp-template` only after the user confirms everything looks right.

---

## Non-goals

- Do NOT install plugins silently — `/gtr:setup` will ask.
- Do NOT rewrite the user's existing CI or release workflows.
- Do NOT change the user's commit message style or branch strategy unless asked.
- Do NOT delete anything the user had before.
