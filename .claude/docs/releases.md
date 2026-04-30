# Releases

Senior-level release flow baked into the template. Key principles:

- **Single source of truth for identity.** `IDENTITY.yaml` at repo root owns `name`, `display_name`, `version`, `icon`, license, and release config. Every derived file (package.json, installer metadata, GH release title, tag name, artifact file name) follows it. No drift by design. `/gtr:doctor` reports any drift; fix by updating the derived file.
- **Changelog-driven notes.** `CHANGELOG.md` in Keep-a-Changelog format. The release workflow extracts the body of the `## [x.y.z]` section matching the pushed tag and uses it as the GitHub release notes. No ad-hoc descriptions.
- **Tag-triggered, test-gated, draft-first.** `.github/workflows/release.yml` runs on push of `v*.*.*` tags. It runs tests first, verifies a CHANGELOG entry exists for the version, builds in a matrix per platform, computes SHA-256 checksums, creates a **draft** GitHub Release with artifacts + notes attached, and stops. A maintainer publishes manually.
- **Versioning.** Semver only. Tag format `v<version>`. Pre-release suffixes (`-rc.1`, `-beta.2`, ...) must match `IDENTITY.yaml#release.prerelease_tags` — workflow detects and flags the release as pre-release automatically.
- **Artifact naming contract.** `{name}-v{version}-{platform}.{ext}`. Binary name matches `IDENTITY.yaml#identity.name`, so repo slug, binary, and release asset all agree.
- **Screenshots.** Under `assets/release/v<version>/`. Embed into the draft release body manually before publishing.
- **Rollback.** Never delete a pushed tag. Patch-forward, or mark the broken release as pre-release with a notice. See `RELEASE.md` for procedures.

## Mechanics handled by `/gtr:release <version>`

1. Validates version (semver regex), tag doesn't exist, `CHANGELOG.md#Unreleased` has content, working tree clean.
2. Bumps `IDENTITY.yaml#version`.
3. Rotates `CHANGELOG.md`: renames `## [Unreleased]` → `## [version] - <date>`, inserts a fresh `## [Unreleased]`.
4. Syncs `package.json` / `pyproject.toml` / `Cargo.toml` version if they exist.
5. Commits and tags locally. Does **not** push — you review, then `git push && git push --tags`.

When `/gtr:setup` detects that a project wants release automation, it copies `release.yml.template` to `.github/workflows/release.yml` and flags the REPLACE markers (test command, per-platform build command) for customization.

See also `RELEASE.md` at repo root for the end-to-end runbook (preflight checklist, post-release checks, rollback procedures).
