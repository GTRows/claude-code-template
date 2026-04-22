---
description: "[TEMPLATE] First-time project setup wizard. Detects stack, fills CLAUDE.md, installs plugins, creates task files, writes setup marker."
---

You are the **template setup wizard**. Run this once per project. It is idempotent — safe to re-run to refresh detected values.

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

## 3. Fill `PROJECT.yaml` (single source of truth)

`PROJECT.yaml` at repo root is the canonical identity and release config. Every other manifest derives from it.

If missing, copy the template skeleton. Then fill:

| Field | Source |
|-------|--------|
| `identity.name` | kebab-case from directory name, `package.json#name`, or `pyproject.toml#project.name`. Must match repo slug. |
| `identity.display_name` | Ask. Propose Title-Cased `name` as default. |
| `identity.description` | README first paragraph, or ask. |
| `identity.homepage` | `package.json#homepage`, else empty. |
| `identity.license` | `LICENSE` header or `package.json#license`. Ask if ambiguous. |
| `identity.icon` | `assets/icon.*`, `static/icon.*`, `src-tauri/icons/`. If none, leave as `assets/icon.png` and open a TODO. |
| `version` | Highest of `package.json#version` / `pyproject.toml` / `Cargo.toml`. Default `0.1.0`. Flag drift. |
| `release.platforms` | Infer from stack (Electron → windows+macos; CLI binary → windows-x64+linux-x64+macos-arm64; web-only → empty). |

If any derived manifest disagrees with `PROJECT.yaml#version` after filling, sync it to `PROJECT.yaml`'s value and open a TODO to verify downstream.

---

## 4. Fill `CLAUDE.md`

Replace placeholder blocks using values from `PROJECT.yaml`:

- `PROJECT_NAME` → `identity.name`
- `Description` → `identity.description`
- `Tech Stack` → from detection
- `Platform` → from detection

**Development Commands**: pull from `package.json#scripts`, Python entry points, `Makefile`, etc. Placeholders you cannot fill confidently stay as-is and become TODO tasks in step 8.

**Sections to leave placeholder** when the code doesn't tell you — open a follow-up TODO instead of fabricating:
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

## 7. Install recommended plugins

Tell the user which plugins you will install and why. These are installed globally (user scope) and become available in every project:

| Plugin | Purpose |
|--------|---------|
| `code-simplifier@claude-plugins-official` | Reviews changed code for redundancy |
| `commit-commands@claude-plugins-official` | `/commit`, `/commit-push-pr` |
| `pr-review-toolkit@claude-plugins-official` | Multi-aspect PR review |
| `claude-md-management@claude-plugins-official` | `/revise-claude-md` + improver skill |
| `skill-creator@claude-plugins-official` | Author new skills |
| `security-guidance@claude-plugins-official` | Session-scoped security reminders |
| `frontend-design@claude-code-plugins` | Only if the project has a UI |

Run `claude plugin list` first. Skip anything already installed. Install the rest:

```bash
claude plugin install <name>@<marketplace>
```

Users running Claude Code with `--dangerously-skip-permissions` get silent installs; otherwise they get one prompt per plugin.

---

## 8. Create task files

- Ensure `TODO.md` exists at repo root. Copy the template skeleton if missing (Active / Blocked / Done sections).
- Ensure `DEFERRED.md` exists at repo root. Copy the template skeleton if missing.

For every `CLAUDE.md` section you could not fill in step 4, append a task to `TODO.md → Active`:

```
- [setup-N] Document {section} in CLAUDE.md
  - Acceptance: {section} has concrete content, no `<!-- … -->` placeholders remain
```

`N` is sequential, starting at 1 (`setup-1`, `setup-2`, ...).

---

## 9. CI scaffolding (opt-in)

Ask:

> Do you want CI (lint + test on push/PR) wired up? (yes / no / later)

- **no** → skip.
- **later** → open TODO `setup-ci`, acceptance: "CI scaffolding decision revisited".
- **yes** →
  1. If `.github/workflows/ci.yml` is missing and `ci.yml.template` exists, copy template → `ci.yml`. Do NOT delete the `.template`.
  2. Tell the user which `REPLACE` markers to customise (runtime setup, lint command, test command).
  3. Open TODO `ci-verify`, acceptance: "push a dummy commit to a branch and confirm the CI job runs green".

---

## 10. Release scaffolding (opt-in)

Ask:

> Do you want release automation for this project? (yes / no / later)

- **no** → skip entirely. Do not create `CHANGELOG.md`, `RELEASE.md`, or the workflow.
- **later** → open TODO `setup-release`, acceptance: "release scaffolding decision revisited".
- **yes** →
  1. If `CHANGELOG.md` is missing at repo root, copy the template skeleton.
  2. If `RELEASE.md` is missing at repo root, copy the template skeleton.
  3. If `.github/workflows/release.yml` is missing and `release.yml.template` exists, copy template → `release.yml`. Do NOT delete the `.template`.
  4. Tell the user which `REPLACE` markers to customise (test command, per-platform build command).
  5. Reconcile `PROJECT.yaml#release.platforms` with the workflow matrix. Ask which platforms to enable; prune the rest from both files.
  6. Open TODO `release-verify`, acceptance: "dry-run a pre-release tag (e.g. `v0.0.1-rc.1`) and confirm the draft release appears on GitHub".

---

## 11. Hooks sanity check

- Read `PROTECTED_EXACT` in `.claude/hooks/pre_guard_release_files.py`. If the project has lock or manifest files not yet listed (`Cargo.lock`, `yarn.lock`, `pnpm-lock.yaml`, `Pipfile.lock`, `poetry.lock`, `go.sum`, ...), suggest additions and wait for user confirmation. Do NOT edit the hook without approval.
- If the project uses Windows-specific native APIs (detected `winreg` / `ctypes` imports, `SystemParametersInfo`), offer to register `.claude/hooks/optional/pre_warn_win32_danger.py` in `.claude/settings.json`.

---

## 12. Write the setup marker

Create `.claude/.setup-complete` with exactly this content (no trailing whitespace):

```
version: 1
date: <today's ISO date, YYYY-MM-DD>
stack: <one-line stack summary from step 2>
type: <fork|primary>
```

Ensure `.claude/.setup-complete` is listed in `.gitignore` — the marker is per-clone, not per-repo.

---

## 13. Summary

Print a short summary:

- What you filled in `CLAUDE.md`
- TODO tasks you left open (with their ids)
- Plugins installed
- Fork or primary
- Whether CI and release scaffolding were activated
- Next step — usually `/task list` or starting the first TODO task
