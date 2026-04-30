---
description: "[TEMPLATE] First-time project setup wizard. Detects stack, fills CLAUDE.md, installs plugins, hands off planning to GSD, writes setup marker."
---

You are the **template setup wizard**. Run this once per project. It is idempotent — safe to re-run to refresh detected values.

`$ARGUMENTS` may include `--extras`. When present, **skip steps 1–11 entirely** and run only step 12 (Optional scaffolding) plus the closing manifest refresh and summary. Use this when the user already finished core setup and wants to add LICENSE / SECURITY.md / ADR / dependabot etc. without re-answering the stack-detection and language questions.

Do not narrate each step while running. Execute them, then print the summary in the final step.

---

## 1. Preflight

Check if `.claude/.setup-complete` exists.

- **Exists** → tell the user setup was already done (show `date` from the marker). Ask if they want to re-run. If no, stop.
- **Missing** → continue.

---

## 2. Detect the stack

Do NOT ask the user what the stack is. Detect it by reading files. Run these in parallel:

- `package.json` (Node/JS/TS — inspect `dependencies`, `scripts`, `engines`)
- `pyproject.toml` / `requirements.txt` / `Pipfile` (Python)
- `go.mod` (Go)
- `Cargo.toml` (Rust)
- `pom.xml` / `build.gradle` / `build.gradle.kts` (Java/Kotlin)
- `composer.json` (PHP)
- `Gemfile` (Ruby)
- Frontend hints: `index.html`, `next.config.*`, `vite.config.*`, `tsconfig.json`, `tailwind.config.*`
- Containerization: `Dockerfile`, `docker-compose.*`
- CI: `.github/workflows/`
- Directory layout: `src/`, `app/`, `backend/`, `frontend/`, `api/`, `web/`
- `README.md` first paragraph for a one-line description

Summarize detection in one short paragraph. **Confirm with the user** before proceeding. Absorb corrections.

---

## 3. Fill `IDENTITY.yaml` (single source of truth)

`IDENTITY.yaml` at repo root is the canonical identity and release config. Every other manifest derives from it.

If missing, copy the template skeleton. Then fill:

| Field | Source |
|-------|--------|
| `identity.name` | kebab-case from directory name, `package.json#name`, or `pyproject.toml#project.name`. Must match repo slug. |
| `identity.display_name` | Ask. Propose Title-Cased `name` as default. |
| `identity.description` | README first paragraph, or ask. |
| `identity.homepage` | `package.json#homepage`, else empty. |
| `identity.license` | `LICENSE` header or `package.json#license`. Ask if ambiguous. |
| `identity.icon` | `assets/icon.*`, `static/icon.*`, `src-tauri/icons/`. If none, leave as `assets/icon.png` and add a line to `.claude/setup-followups.md`. |
| `version` | Highest of `package.json#version` / `pyproject.toml` / `Cargo.toml`. Default `0.1.0`. Flag drift. |
| `release.platforms` | Infer from stack (Electron → windows+macos; CLI binary → windows-x64+linux-x64+macos-arm64; web-only → empty). |

If any derived manifest disagrees with `IDENTITY.yaml#version` after filling, sync it to `IDENTITY.yaml`'s value and add a line to `.claude/setup-followups.md` to verify downstream.

---

## 4. Fill `CLAUDE.md`

Replace placeholder blocks using values from `IDENTITY.yaml`:

- `PROJECT_NAME` → `identity.name`
- `Description` → `identity.description`
- `Tech Stack` → from detection
- `Platform` → from detection

**Development Commands**: pull from `package.json#scripts`, Python entry points, `Makefile`, etc. Placeholders you cannot fill confidently stay as-is and become follow-ups captured in `.claude/setup-followups.md`.

**Sections to leave placeholder** when the code doesn't tell you — add a line to `.claude/setup-followups.md` instead of fabricating:
- `Architecture / Entry Flow`
- `Module Breakdown`
- `Data Storage`
- Git commit scopes

If `PROJECT_NAME` appears as literal text elsewhere (README, docs), replace it too.

---

## 5. Branch strategy (fork or primary)

Ask exactly one question:

> Is this repo a **fork** of an upstream project, or your **primary/own** repo?

Append to `CLAUDE.md` under a new `## Branch Strategy` section:

- **Fork**:
  ```
  This is a fork. `main` tracks upstream.
  - Never commit directly to `main`.
  - Use `feature/<name>` or `fix/<name>` branches.
  - One PR per feature. Rebase onto upstream before opening.
  ```
- **Primary**:
  ```
  This is the primary repo. Use feature branches for non-trivial work;
  small fixes can go on `main` if the project convention allows.
  ```

---

## 6. Commit authorship

Append under `## Git and Commits` in `CLAUDE.md`:

```
- Commits are authored by the user via local git config.
  Do NOT add `Co-Authored-By: Claude` trailers.
```

---

## 7. Conversation language and project i18n

Two separate questions — ask them together, in one message:

**a. Conversation language**

> What language should I speak with you in this project? (English / Türkçe / Deutsch / ... — pick one)

Whatever the user picks, append a binding rule to `CLAUDE.md` under a new `## Communication` section:

```
- Speak with the user in <Language>. All conversational responses,
  prompts, summaries, and questions must be in this language.
- Code, identifiers, comments, commit messages, and file contents
  must always be in English regardless of conversation language.
- Slash command output formatting (tables, status lines) stays English.
```

This rule overrides any default. Do not switch languages mid-project unless the user re-runs `/gtr:setup`.

**b. Project localization (i18n)**

> Will this project ship to end users in multiple languages? (yes / no / later)

- **no** → no further action.
- **later** → add a `setup-i18n` follow-up line to `.claude/setup-followups.md`: "i18n strategy decided".
- **yes** → ask one follow-up: `Which UI languages will you support? (comma-separated, e.g. en, tr, de)`. Then append to `CLAUDE.md` under `## Localization`:
  ```
  - Supported UI languages: <list>.
  - Default / fallback: <first in list>.
  - Translation source format: TBD (gettext, JSON, ICU, ...) — set when picking the i18n library.
  - User-facing strings must NOT be hard-coded. Wrap them in the
    project's translation function.
  ```
  Add `pick-i18n-lib` follow-up to `.claude/setup-followups.md`: "i18n library installed, default + at least one non-default locale rendering".

---

## 8. Install recommended plugins

Tell the user which plugins you will install and why. These are installed globally (user scope) and become available in every project:

| Plugin | Marketplace | Purpose |
|--------|-------------|---------|
| `code-simplifier` | `claude-plugins-official` | Reviews changed code for redundancy |
| `commit-commands` | `claude-plugins-official` | `/commit`, `/commit-push-pr` |
| `pr-review-toolkit` | `claude-plugins-official` | Multi-aspect PR review |
| `claude-md-management` | `claude-plugins-official` | `/revise-claude-md` + improver skill |
| `skill-creator` | `claude-plugins-official` | Author new skills |
| `security-guidance` | `claude-plugins-official` | Session-scoped security reminders |
| `oh-my-claudecode` | `omc` | Autopilot, ralph, ultrawork, deep-dive, plan, and more advanced agents |
| `frontend-design` | `claude-code-plugins` | Only if the project has a UI |

**Step 8a — register custom marketplaces first.** Run `claude plugin marketplace list`; if `omc` is missing, add it:

```bash
claude plugin marketplace add https://github.com/Yeachan-Heo/oh-my-claudecode
```

The other two marketplaces (`claude-plugins-official`, `claude-code-plugins`) ship with Claude Code; you do not need to add them.

**Step 8b — install plugins.** Run `claude plugin list` first. Skip anything already installed. Install the rest:

```bash
claude plugin install <name>@<marketplace>
```

Users running Claude Code with `--dangerously-skip-permissions` get silent installs; otherwise they get one prompt per plugin.

**Step 8c — pin the installed set.** After installs land, write the pin file so `/gtr:doctor` can flag drift later:

```bash
python .claude/scripts/plugins.py --pin
```

This records `name@marketplace` for every currently installed plugin into `.claude/plugin-pin.json` (committed). The next `/gtr:doctor` run uses it to detect uninstalled or missing plugins.

---

## 9. Planning hand-off (GSD)

Ask exactly:

> Do you want to use **GSD** for planning and execution? (recommended)
> - **yes**   → I will run `/gsd:new-project` next (and `/gsd:map-codebase` first if this is an existing codebase). The brief is auto-filled from `IDENTITY.yaml` / `CLAUDE.md` / `README.md`; you only confirm or tweak.
> - **no**    → skip planning. Template still works for hooks, releases, onboarding, doctor.
> - **later** → captured in `.claude/setup-followups.md` (gitignored). `/gtr:doctor` surfaces it.

For every `CLAUDE.md` section you could **not** fill in step 4, capture it in `.claude/setup-followups.md` (one line per gap with the section name). These become natural seeds for the first GSD plan when the user later runs `/gsd:plan-phase 1`.

Do **NOT** create `TODO.md` or `DEFERRED.md` — both are removed in v0.2.0. Planning lives under `.planning/` (managed by GSD) or not at all.

---

## 10. CI scaffolding (opt-in)

Ask:

> Do you want CI (lint + test on push/PR) wired up? (yes / no / later)

- **no** → skip.
- **later** → add `setup-ci` follow-up to `.claude/setup-followups.md`: "CI scaffolding decision revisited".
- **yes** →
  1. If `.github/workflows/ci.yml` is missing and `ci.yml.template` exists, copy template → `ci.yml`. Do NOT delete the `.template`.
  2. Tell the user which `REPLACE` markers to customise (runtime setup, lint command, test command).
  3. Add `ci-verify` follow-up to `.claude/setup-followups.md`: "push a dummy commit to a branch and confirm the CI job runs green".

---

## 11. Release scaffolding (opt-in)

Ask:

> Do you want release automation for this project? (yes / no / later)

- **no** → skip entirely. Do not create `CHANGELOG.md`, `RELEASE.md`, or the workflow.
- **later** → add `setup-release` follow-up to `.claude/setup-followups.md`: "release scaffolding decision revisited".
- **yes** →
  1. If `CHANGELOG.md` is missing at repo root, copy the template skeleton.
  2. If `RELEASE.md` is missing at repo root, copy the template skeleton.
  3. If `.github/workflows/release.yml` is missing and `release.yml.template` exists, copy template → `release.yml`. Do NOT delete the `.template`.
  4. Tell the user which `REPLACE` markers to customise (test command, per-platform build command).
  5. Reconcile `IDENTITY.yaml#release.platforms` with the workflow matrix. Ask which platforms to enable; prune the rest from both files.
  6. Add `release-verify` follow-up to `.claude/setup-followups.md`: "dry-run a pre-release tag (e.g. `v0.0.1-rc.1`) and confirm the draft release appears on GitHub".

---

## 12. Optional scaffolding (opt-in, batched)

Ask the user once, listing every option:

> Want any of these scaffolding files? Reply with comma-separated numbers, `all`, or `none`.
>
>   1. `LICENSE` (MIT default — ask the year and copyright holder)
>   2. `SECURITY.md` (vulnerability disclosure policy)
>   3. `CONTRIBUTING.md` (PR / commit / branching guidance from this CLAUDE.md)
>   4. `.github/CODEOWNERS` (auto-request reviewers)
>   5. `.github/dependabot.yml` (weekly dependency updates)
>   6. `.pre-commit-config.yaml` (pre-commit framework — runs lint/format on staged files)
>   7. `.env.example` (env-var template; only meaningful if the project uses dotenv)

For each picked option:

- `LICENSE` → write the MIT text with `<year>` / `<owner>` filled in. Update `IDENTITY.yaml#identity.license` to `MIT`.
- `SECURITY.md` → minimal disclosure policy (email contact, expected response time, supported versions table — fill from `IDENTITY.yaml`).
- `CONTRIBUTING.md` → derive from this CLAUDE.md's `Git and Commits`, `Code Standards`, `File Organization` sections.
- `.github/CODEOWNERS` → ask for the user's GitHub handle, default `* @<handle>`.
- `.github/dependabot.yml` → infer ecosystem from detection in step 2 (npm, pip, cargo, gomod, ...).
- `.pre-commit-config.yaml` → infer hooks from stack (ruff for Python, prettier for JS, etc.); leave a comment block of suggested hooks the user can opt into.
- `.env.example` → only if the project already imports `dotenv` / uses `os.environ.get` patterns. Scan top-level source for variable names and stub them with empty values.

For files the user did not pick, do nothing — do not add follow-ups for them.

---

## 13. Hooks sanity check

- Read `PROTECTED_EXACT` in `.claude/hooks/pre_guard_release_files.py`. If the project has lock or manifest files not yet listed (`Cargo.lock`, `yarn.lock`, `pnpm-lock.yaml`, `Pipfile.lock`, `poetry.lock`, `go.sum`, ...), suggest additions and wait for user confirmation. Do NOT edit the hook without approval.
- If the project uses Windows-specific native APIs (detected `winreg` / `ctypes` imports, `SystemParametersInfo`), offer to register `.claude/hooks/optional/pre_warn_win32_danger.py` in `.claude/settings.json`.

---

## 14. Write the setup marker

Create `.claude/.setup-complete` with exactly this content (no trailing whitespace):

```
version: 1
date: <today's ISO date, YYYY-MM-DD>
stack: <one-line stack summary from step 2>
type: <fork|primary>
```

Ensure `.claude/.setup-complete` is listed in `.gitignore` — the marker is per-clone, not per-repo.

Then write the template manifest so `/gtr:update` can later detect which files the user has modified:

```bash
python .claude/scripts/manifest.py --write
```

Add `.claude/.template-manifest.json` to git so it ships with the project.

---

## 15. Summary

Print a short summary:

- What you filled in `CLAUDE.md`
- Follow-ups captured in `.claude/setup-followups.md`
- Plugins installed
- Fork or primary
- Whether CI and release scaffolding were activated
- Next step — usually `/gsd:new-project` (if planning was opted in) or `/gtr:menu` for the option list
