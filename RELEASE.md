# Release Runbook

Source of truth for identity and release config: `IDENTITY.yaml`.
Automation: `.github/workflows/release.yml`.
Notes source: `CHANGELOG.md`.

## Versioning rules

- Semantic versioning: `MAJOR.MINOR.PATCH`.
- Breaking change → bump `MAJOR`.
- New feature, no break → bump `MINOR`.
- Bugfix only → bump `PATCH`.
- Pre-release → append `-<tag>.<n>` (e.g. `1.2.0-rc.1`). Allowed tags come from `IDENTITY.yaml#release.prerelease_tags`.
- Git tag format: `v<version>` (e.g. `v1.2.0`). No other prefixes.

## Artifact naming contract

Defined by `IDENTITY.yaml#release.artifact_pattern`. Default:
```
{name}-v{version}-{platform}.{ext}
```
Examples:
- `tab-janitor-v1.2.0-windows-x64.exe`
- `tab-janitor-v1.2.0-linux-x64.tar.gz`

Every artifact is paired with a `SHA256SUMS` entry.

## Preflight checklist

Before cutting a release:

- [ ] All GSD plans included in this version are complete (`/gsd:progress` shows them done).
- [ ] `CHANGELOG.md` has an `## [Unreleased]` section with the actual changes — no stubs.
- [ ] `IDENTITY.yaml#version` matches the target version.
- [ ] Derived manifests (`package.json`, `pyproject.toml`, `Cargo.toml`, etc.) match `IDENTITY.yaml#version`. Run `/gtr:doctor` to verify.
- [ ] CI on `main` is green.
- [ ] Screenshots for any visual changes saved under `assets/release/v<version>/`.

## Cut the release

Use `/gtr:release` to do steps 1–4 mechanically, or do them by hand:

1. Bump `IDENTITY.yaml#version` to the new version.
2. In `CHANGELOG.md`, rename `## [Unreleased]` to `## [x.y.z] - YYYY-MM-DD`. Open a fresh `## [Unreleased]` above it with empty sections.
3. Update derived manifests to match.
4. Commit: `chore(release): v<version>`.
5. Tag: `git tag v<version> -m "Release v<version>"`.
6. Push: `git push && git push --tags`.

The tag push triggers `.github/workflows/release.yml`.

## Workflow behavior

On tag push matching `v*.*.*`:
1. Tests run first. Release aborts on failure.
2. Build matrix runs for each platform in `IDENTITY.yaml#release.platforms`.
3. Artifacts collected into `dist/`. `SHA256SUMS.<platform>` generated per job.
4. Release notes extracted from the `## [x.y.z]` section of `CHANGELOG.md`.
5. A **draft** GitHub Release is created with all artifacts and notes attached.
6. Draft is not auto-published — a maintainer reviews and clicks Publish.

## Post-release

- [ ] Verify artifacts open/install/run on a clean machine for each platform.
- [ ] Verify checksums match.
- [ ] Attach screenshots from `assets/release/v<version>/` to the release body if relevant.
- [ ] Click Publish in GitHub.
- [ ] Announce externally (if applicable).

## Rollback

A broken published release is never silently deleted. Choose one:

- **Patch-forward (preferred)**: cut a new PATCH release with the fix. Mark the broken version as deprecated in `CHANGELOG.md`.
- **Mark pre-release**: demote the broken release to "pre-release" in GitHub and add a notice at the top of the release notes pointing to the fix.
- **Yank** (only when the artifact is actively harmful): delete release assets (not the tag), add a prominent yank notice, and ship a fix.

Never delete a tag that has been pushed publicly.
