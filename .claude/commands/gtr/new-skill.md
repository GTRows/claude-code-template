---
description: "[TEMPLATE] Scaffold a project-specific Claude Code skill under .claude/skills/."
---

Create a new project-specific skill for: `$ARGUMENTS`

Project-specific skills live under `.claude/skills/<slug>/`. They differ from plugin-provided skills:

- **Plugins** are installed globally (user scope), shared across all projects. Reach for plugins for general-purpose capabilities (review, planning, scaffolding).
- **Project skills** stay inside `.claude/skills/`, tracked in git. Reach for them when the capability is specific to *this* project's domain (e.g. domain glossary, internal API patterns, deployment runbook).

If the user asks for something that is general-purpose, suggest `/skill-creator:skill-creator` (plugin) instead — do not bloat `.claude/skills/`.

## Steps

1. Slugify the title from `$ARGUMENTS` (lowercase, hyphenated, ASCII).
2. Refuse if `.claude/skills/<slug>/` already exists.
3. Create the directory and write `.claude/skills/<slug>/SKILL.md` using the template below.
4. Confirm whether the skill needs auxiliary files (datasets, regex tables, code references). If yes, mention they go alongside `SKILL.md` in the same dir.
5. Tell the user the skill is enabled the next time Claude Code reloads its skill index.

## Template

```markdown
---
name: <slug>
description: One sentence that begins with the trigger condition.
  Example: "Use when the user asks about <domain X>; explain in terms of <project Y>."
---

# <Title>

## When to use

- Trigger 1 (concrete signal — file pattern, keyword, error message).
- Trigger 2.

Skip if: <when this skill should NOT activate, to avoid over-firing>.

## Inputs the skill expects

- <user request shape>
- <auxiliary file locations, if any>

## Outputs / behavior

- <what Claude should do step by step>
- <any specific format the answer must take>

## Project-specific knowledge

<The body. Domain glossary, internal API patterns, mental models the user
would otherwise have to re-explain every session. Be concrete and short —
this is loaded into Claude's context whenever the skill triggers.>

## Anti-patterns

- <what NOT to do that would otherwise be Claude's default>
```

## Conventions

- Keep `SKILL.md` under 200 lines. Skills are loaded into context — long ones are expensive.
- Trigger description is the **most important** part. Bad triggers either fire constantly or never. Use concrete file patterns, keywords, or error markers.
- Reference plugin skills with `<plugin-name>:<skill-name>` when relevant. Do not duplicate plugin functionality.
- Auxiliary files (regex tables, terminology, examples) go in the same dir as `SKILL.md`. The skill body can reference them with relative paths.

## Report

- Path to the new skill directory.
- One-line trigger condition.
- Suggested next step: open the file and fill the body, then commit.
