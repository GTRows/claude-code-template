# Output style for /gtr:* commands

Hard rules. Apply to every slash-command response unless the command's own file overrides explicitly.

## Length budget

- Total response under 25 lines unless the user asked for depth.
- No paragraphs longer than 2 sentences.
- No "summary of what I just did" at the end.
- No preamble ("Sure!", "Here is...", "Let me explain...").
- No restating the question.

## Structure

- Lead with the answer or the action. Reasoning, if any, comes after.
- Use bullets, not prose, when the answer has 3+ items.
- Section headings only when the response covers 3+ distinct sections. One-section answers stay flat.
- Use tables only when comparing 4+ items across 2+ axes.

## What to skip

- Re-explaining the user's project state back to them.
- "I will now do X. After that I will Y" plans for one-step jobs.
- Caveats about edge cases the user did not ask about.
- Repeating section headings copied from the command file.
- Repeating the same fact in two places.

## Code, paths, commands

- Keep code blocks as short as possible. One-line snippets do not need fences.
- File paths in inline code: `CLAUDE.md`, `.planning/PROJECT.md`.
- Slash commands stay verbatim, never translated.

## Anti-examples

Bad:

> Great question! To create a roadmap, you will want to use the `/gsd:create-roadmap` command. This command takes the project vision from `.planning/PROJECT.md` and turns it into ordered phases stored in `.planning/ROADMAP.md`. Once that file exists, you can plan individual phases with `/gsd:plan-phase <N>`, then execute each plan with `/gsd:execute-plan <path>`. Let me know if you have any other questions!

Good:

> `/gsd:create-roadmap`. Reads `.planning/PROJECT.md`, writes `.planning/ROADMAP.md`.

Bad:

> ## Setup status
>
> Setup has been completed. The setup marker file `.claude/.setup-complete` exists.
>
> ## CLAUDE.md status
>
> The `## Communication` section is present and configured for Turkish.

Good:

> Setup: done. Language: Turkish.

## Translation

Translate prose. Never translate slash commands, file paths, code, or version strings. See `/gtr:help` "Output language" directive for the full rule.
