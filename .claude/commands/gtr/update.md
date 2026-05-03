---
description: "[TEMPLATE] Pull template updates from upstream and merge them without breaking the project's own changes."
---

Pull updates from the upstream template repo (`https://github.com/GTRows/claude-code-template`) into the current project, merge them into existing files when safe, and ask before overwriting anything the user has modified.

**Output language.** Read `## Communication` from `CLAUDE.md` and produce all explanations, conflict prompts, and summaries in that language. File paths, version numbers, and shell commands stay verbatim. If `## Communication` is missing, default to the language the user wrote the request in.

**Output budget.** Follow `.claude/docs/output-style.md`. Show only files that actually changed, conflicts that need a decision, and the final commit hash. Skip "everything is clean" lines.

## Preconditions

1. `.claude/.setup-complete` must exist — refuse if the project has not been set up.
2. Working tree must be clean (`git status --porcelain` is empty). Refuse with: `Commit or stash first — /gtr:update needs a clean tree to write a single update commit.`
3. `gh` authenticated, OR plain `git` available with network access.
4. `.claude/VERSION` exists. If missing, treat current version as `0.0.0`.

## Step 1 — Find the upstream version

Tags are the source of truth — `gh release list` only sees published GitHub Releases and lags behind tags pushed without a release. Always query tags first:

```bash
git ls-remote --tags https://github.com/GTRows/claude-code-template.git \
  | awk -F/ '{print $NF}' | grep -E '^v[0-9]+\.[0-9]+\.[0-9]+$' | sort -V | tail -1
```

If the ls-remote call fails (no network, auth issue), fall back to:

```bash
gh release list --repo GTRows/claude-code-template --limit 1 --json tagName --jq '.[0].tagName'
```

Strip the leading `v`. Compare to `.claude/VERSION` content.

- Equal → tell the user `Already on latest (vX.Y.Z).` and stop.
- Local newer → tell the user `Local version (X) is ahead of upstream (Y). Nothing to pull.` and stop.
- Upstream newer → continue.

## Step 2 — Check the manifest

The project keeps a manifest at `.claude/.template-manifest.json`. Format:

```json
{
  "version": "1.0.0",
  "files": {
    ".claude/hooks/pre_guard_release_files.py": "<sha256-at-install>",
    ".claude/commands/setup.md": "<sha256-at-install>",
    "CLAUDE.md": "<sha256-at-install>"
  }
}
```

**If the manifest is missing** (project predates the manifest system, or `/gtr:setup` was run on an older template version):

1. Tell the user explicitly:
   > No `.claude/.template-manifest.json` found. I will seed one from the current local files. Any file you have already modified will be treated as "untouched", so on the next conflict step I will not be able to detect those edits — you will see them as auto-update candidates instead. This is a one-time bootstrap.

2. Run:
   ```bash
   python .claude/scripts/manifest.py --write
   ```

3. Then continue. From this point forward, `/gtr:update` works precisely.

**If the manifest is present**, continue without asking.

## Step 2.5 — Run schema migrations (BEFORE fetching upstream)

For breaking changes between the project's current `.claude/VERSION` and the
upstream version, the template ships per-version migration scripts under
`.claude/scripts/migrations/`. They handle reshapes that a sha-based file
diff cannot — directory renames, dropped files, identity rename, etc.

1. **Preview** what will run:
   ```bash
   python .claude/scripts/migrations.py --target <upstream-version> --check
   ```
2. If the output is "no migrations to run", continue to step 3.
3. Otherwise show the user the action list and ask: `Apply <N> migration(s)? (yes / no)`.
4. On `yes`:
   ```bash
   python .claude/scripts/migrations.py --target <upstream-version>
   ```
   The runner snapshots `.claude/commands/` to `.claude/commands.pre-vX.Y.Z/`
   before reshaping and bumps `.claude/VERSION` after each migration.
5. If the runner reports any `note` actions (manual review needed),
   surface them to the user before continuing.
6. Re-run `python .claude/scripts/manifest.py --write` so the manifest
   reflects the post-migration filenames. Otherwise step 4 will treat the
   reshape as user modifications.

## Step 3 — Fetch upstream

Clone the upstream tag into a temp dir:

```bash
git clone --depth 1 --branch v<upstream-version> \
  https://github.com/GTRows/claude-code-template.git "$(mktemp -d)/ccp-update"
```

Read the upstream `.claude/.template-manifest.json` if present, otherwise compute hashes ad-hoc for the relevant template-owned paths.

## Step 4 — File-by-file decision

For each path that exists in upstream **and** is template-owned (see exclusion list below):

| State | Action |
|-------|--------|
| Local sha == manifest sha (user has not modified) AND upstream sha differs | **Auto-update** — write upstream content. |
| Local sha == manifest sha AND upstream sha matches | **Skip** — no change. |
| Local sha != manifest sha (user modified) AND upstream sha == manifest sha | **Skip** — only the user changed. |
| Local sha != manifest sha AND upstream sha differs | **Conflict** — show 3-way summary (manifest → local diff, manifest → upstream diff). Ask: `keep / replace / merge-by-hand / skip`. |
| Path missing locally, present upstream | **Add** — write file. |
| Path present locally, missing upstream | Ask `Upstream removed this file — delete locally?` — default `keep`. |

**Excluded paths** (never touched by `/gtr:update`):

```
CHANGELOG.md
IDENTITY.yaml         (identity is per-project — was PROJECT.yaml in v0.1.x)
PROJECT.yaml          (legacy alias; only present pre-v0.2.0)
README.md             (per-project doc)
.claude/.setup-complete
.claude/settings.local.json
.gitignore            (merge by appending only — never overwrite)
.github/workflows/*.yml         (activated workflows are per-project — only touch *.yml.template)
.env*
LICENSE
```

For `.gitignore`, only append upstream lines that are not already present locally.

## Step 5 — Apply, refresh manifest, commit

After all decisions:

1. Apply the writes/adds/deletes the user approved.
2. Recompute `.claude/.template-manifest.json` so each path's sha matches the new file content.
3. Bump `.claude/VERSION` to the upstream version.
4. Stage exactly the files you touched plus `.claude/.template-manifest.json` and `.claude/VERSION`.
5. Commit:
   ```
   chore: update template to v<upstream-version>
   
   Auto-updated: <count> files
   Conflicts resolved: <count> files
   Added: <count> files
   ```
6. Do NOT push. Tell the user to review and push themselves.

## Step 6 — Report

Print:

```
Template updated: v<old> → v<new>

  auto-updated:    <list>
  user-modified:   <list>
  conflicts:       <list>
  added:           <list>
  skipped:         <list>

Review the commit, then `git push` when ready.
```

## Notes

- Never use `git add -A`. Only stage the specific files you wrote.
- Never rewrite the user's hook customisations (e.g. their additions to `PROTECTED_EXACT`). On conflict, default action is always `keep`.
- If the upstream removes a hook the user still has registered in `settings.json`, do NOT silently unregister — ask.
- Run `/gtr:doctor` automatically at the end and surface any new drift.
