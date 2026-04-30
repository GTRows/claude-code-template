---
description: "[TEMPLATE] Prepare a release: bump version, move Unreleased in CHANGELOG, commit, tag. Does not push."
---

You are preparing a release. `$ARGUMENTS` is the target version (e.g. `1.2.3` or `1.2.0-rc.1`).

If empty, print usage and stop:

```
/gtr:release <version>

version   semver: MAJOR.MINOR.PATCH[-prerelease]
          examples: 1.2.3, 2.0.0, 1.2.0-rc.1
```

---

## Preflight — abort on any failure

| # | Check | Abort if |
|---|-------|----------|
| 1 | `git status --porcelain` is empty | Uncommitted changes exist. |
| 2 | Current branch is `main` (or project's release branch) | On some other branch. |
| 3 | `IDENTITY.yaml` exists at repo root | Missing. |
| 4 | `CHANGELOG.md` has `## [Unreleased]` with at least one non-empty bullet | Missing or empty. See remediation below. |
| 5 | `$ARGUMENTS` matches semver regex `^\d+\.\d+\.\d+(-[A-Za-z][A-Za-z0-9.]*)?$` | Invalid. |
| 6 | Tag `v<version>` does not exist (`git rev-parse v<version>` fails) | Tag already exists. |
| 7 | `IDENTITY.yaml#version` is less than `$ARGUMENTS` (split-by-dot compare) | Version not going forward. |
| 8 | If pre-release, its tag (`alpha`, `beta`, `rc`, ...) is in `IDENTITY.yaml#release.prerelease_tags` | Tag not allowed. |

On any failure: stop and report which check failed. Do not touch the repo.

### Remediation hints

If a check fails, surface the specific fix instead of just the abort:

- **Check 4 (CHANGELOG missing or empty)**:
  - File missing → `/gtr:setup` was likely run with release scaffolding off. Tell the user: "CHANGELOG.md is missing. Either re-run `/gtr:setup` and pick `yes` for release scaffolding, or copy the template skeleton manually from the upstream repo's CHANGELOG.md."
  - File present but `## [Unreleased]` is empty or has only empty subsections → tell the user: "Add at least one bullet under `## [Unreleased]` in CHANGELOG.md before running `/gtr:release` again. Bullets describe what changed since the last release."
  - File present but `## [Unreleased]` heading is missing → tell the user: "Add a `## [Unreleased]` section at the top of CHANGELOG.md (above the most recent version section) with the change bullets."
- **Check 1 (uncommitted changes)**: list the offending files; suggest `git stash` or commit.
- **Check 7 (version not going forward)**: print current and target; suggest the next valid bump.
- **Check 8 (prerelease tag not allowed)**: print allowed tags from `IDENTITY.yaml#release.prerelease_tags`.

---

## Mechanical steps

### 1. Bump `IDENTITY.yaml`

Replace the `version:` line with `version: <new-version>`.

### 2. Rotate `CHANGELOG.md`

- Find the `## [Unreleased]` heading.
- Insert a fresh block above it:
  ```
  ## [Unreleased]

  ### Added
  ### Changed
  ### Deprecated
  ### Removed
  ### Fixed
  ### Security

  ```
- Rename the original `## [Unreleased]` to `## [<version>] - <today's ISO date>`.
- Remove empty subsections (headings with no bullets) from the renamed block.

### 3. Sync derived manifests (only if present — do NOT create)

| File | Field to update |
|------|----------------|
| `package.json` | `"version"` |
| `pyproject.toml` | `version = "..."` under `[project]` or `[tool.poetry]` |
| `Cargo.toml` | `version = "..."` under `[package]` |

### 4. Stage and commit

```bash
git add IDENTITY.yaml CHANGELOG.md <any-synced-manifests>
git commit -m "chore(release): v<version>"
```

### 5. Tag

```bash
git tag -a v<version> -m "Release v<version>"
```

---

## Do NOT push

`/gtr:release` never pushes automatically. Print the next steps and stop:

```
Prepared v<version>.

Review the commit and tag, then push:
  git push && git push --tags

The release workflow will produce a draft GitHub Release.
Review artifacts and publish manually.
```
