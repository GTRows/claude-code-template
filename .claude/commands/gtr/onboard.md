---
description: "[TEMPLATE] Onboard an existing project — interactive runbook for IMPLEMENT.md (merge hooks, settings, CLAUDE.md additions)."
---

You are onboarding the **template into the user's existing project**. This is the interactive driver for `IMPLEMENT.md`. Follow it step by step, asking the user once per decision, applying changes only after they confirm. Do NOT batch-confirm; one step at a time so the user can stop cleanly mid-flow.

**Output language.** Read `## Communication` from `CLAUDE.md` and conduct the interview, confirmations, and summaries in that language. File paths, code blocks, and slash-command names stay verbatim. If `## Communication` is missing, default to the language the user wrote the request in.

**Output budget.** Follow `.claude/docs/output-style.md`. One decision per turn. No restatement of the previous decision before asking the next.

## 0. Preflight

Refuse and stop if any of these hold:

- The project does not have a `.git` directory. Tell the user: `Run git init first, commit your existing work, then re-run /gtr:onboard.`
- `git status --porcelain` is non-empty. Tell the user: `Working tree is dirty. Commit or stash, then re-run /gtr:onboard.`
- `.claude/.setup-complete` already exists. Tell the user: `This project is already onboarded. Use /gtr:update to pull the latest template; use /gtr:setup to re-run the wizard idempotently.`

If preflight passes, print:

```
Onboarding from https://github.com/GTRows/claude-code-template

I will:
  1. Clone the latest template tag to a temp dir.
  2. Walk through file-by-file decisions (hooks, commands, settings, docs).
  3. Apply only what you approve.
  4. Run /gtr:setup at the end to fill CLAUDE.md and IDENTITY.yaml.

Proceed? (yes / no)
```

Stop on anything other than `yes`.

## 1. Fetch the template

```bash
TEMPLATE_TAG=$(gh release list --repo GTRows/claude-code-template --limit 1 --json tagName --jq '.[0].tagName' 2>/dev/null \
  || git ls-remote --tags https://github.com/GTRows/claude-code-template.git | awk -F/ '{print $NF}' | grep -E '^v[0-9]+\.[0-9]+\.[0-9]+$' | sort -V | tail -1)
TEMPLATE_DIR=$(mktemp -d)/ccp-onboard
git clone --depth 1 --branch "${TEMPLATE_TAG}" https://github.com/GTRows/claude-code-template.git "${TEMPLATE_DIR}"
```

If the clone fails, stop and report the error.

## 2. Walk the decision matrix

Use the file-by-file rules in `IMPLEMENT.md` (table under `2. File-by-file plan`). For each row:

- Read both the upstream file and the local file (if present).
- Tell the user one line about what changes (e.g. `Will copy .claude/hooks/pre_guard_security.py — does not exist locally.`).
- For ambiguous cases, show the diff and ask `apply / skip / view-full-diff`.

Group sequentially:

### 2a. Hooks (always safe)

Copy every `.claude/hooks/*.py` and `.claude/hooks/optional/*.py` if missing locally. If a hook with the same name exists locally, show the diff and ask.

### 2b. Slash commands (always safe)

Copy every `.claude/commands/*.md`. If a command with the same name exists locally, show the diff and ask.

### 2c. Scripts and tests

Copy `.claude/scripts/manifest.py` and `.claude/hooks/tests/`.

### 2d. Settings merge

`.claude/settings.json` requires deep-merge:
- Union `permissions.deny`, `permissions.ask` (de-duplicate).
- Add hook entries that are not already registered.
- Do NOT touch `permissions.allow`.

Show the proposed merged file before writing.

### 2e. CLAUDE.md additions

If the user has a CLAUDE.md, do NOT overwrite. Offer each missing section individually:

- `## First-time setup check`
- `## Available commands`
- `## Planning workflow (GSD)`
- `## Release` (only if release scaffolding was opted in)
- Commit-authorship line under `## Git and Commits`

Ask `add / skip / customize` per section.

### 2f. Root-level files

For each of `IDENTITY.yaml`, `IMPLEMENT.md`, `RELEASE.md`, `CHANGELOG.md`:
- If missing, ask: `add <file>? (yes / no)`. If yes, copy from template.
- If present, leave alone.

### 2g.b Planning hand-off

Ask the user: `Use GSD for planning? (yes / no / later)`. If yes, after the onboarding commit lands, suggest `/gsd:map-codebase` then `/gsd:new-project` so brief auto-fills from the now-merged template files. Do NOT run those commands inside `/gtr:onboard`.

### 2g. Workflows (opt-in only)

Copy `.github/workflows/ci.yml.template` and `.github/workflows/release.yml.template` (note the `.template` suffix is preserved). Tell the user activation happens via `/gtr:setup` step 10/11.

### 2h. `.gitignore` merge

Append upstream lines that are missing locally. Show the diff before writing. Always include:
```
.claude/settings.local.json
.claude/.setup-complete
```

### 2i. Hook tests gitignore note

Tell the user: `The hook tests directory is included. Add to your existing CI run via .github/workflows/ci.yml.template if you opt into CI in /gtr:setup.`

## 3. Write the manifest

After all approved changes are applied:

```bash
python .claude/scripts/manifest.py --write
```

This snapshots every template-owned file's sha so `/gtr:update` can later detect what the user has touched.

## 4. Stage and commit

Stage only the files you wrote — never use `git add -A`.

```bash
git add <listed-files>
git commit -m "chore: adopt claude-code-template (${TEMPLATE_TAG})"
```

Do NOT push.

## 5. Hand off to /gtr:setup

Tell the user:

```
Template onboarded at ${TEMPLATE_TAG}.

Next: run /gtr:setup to fill in CLAUDE.md / IDENTITY.yaml from your project's
detected stack, install plugins, and complete first-time configuration.
```

Do not invoke `/gtr:setup` automatically — it has its own confirm gates.

## 6. Cleanup

Remove `${TEMPLATE_DIR}` only after the user confirms everything looks right.

## Guardrails

- One decision at a time. Never batch-apply.
- `README.md`, `LICENSE`, `package.json` (and other manifests) are NEVER touched by `/gtr:onboard`.
- If at any point the user types `stop` / `cancel`, stop immediately. Already-applied changes stay staged but uncommitted so the user can review with `git diff --staged`.
- Refuse to onboard a fork of an unrelated project (detect via `git remote get-url origin` not matching template repo). Ask explicit confirmation if the remote is unfamiliar.
