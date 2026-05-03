---
description: "[TEMPLATE] Set or change the conversation language for this project. Writes/updates the ## Communication block in CLAUDE.md and syncs .claude/.setup-complete."
---

You are the **template language configurator**. Job: bind a single conversation language for this project so every later `/gtr:*` and `/gsd:*` command speaks it.

**Output budget.** Follow `.claude/docs/output-style.md`. The whole exchange is two short messages: one question (skipped if `$ARGUMENTS` already names a language) and one confirmation. No preamble, no recap.

---

## 1. Resolve the target language

`$ARGUMENTS` may already contain the language. Accept English names (`Turkish`, `English`, `German`), native names (`Türkçe`, `Deutsch`, `Français`), or ISO 639-1 codes (`tr`, `en`, `de`). Normalise to the English name (e.g. `tr` -> `Turkish`, `Türkçe` -> `Turkish`).

If `$ARGUMENTS` is empty, ask exactly:

> Which language should I speak with you in this project? (English / Türkçe / Deutsch / Français / Español / ... — pick one)

Default suggestion: detect from the language the user wrote `/gtr:set-language` in.

---

## 2. Update `CLAUDE.md`

Read `CLAUDE.md`. Two cases:

**Case A — `## Communication` section is missing.** Append this block at the end of the file (before any trailing whitespace), with `<Language>` replaced by the chosen language:

```
## Communication

- Speak with the user in <Language>. All conversational responses,
  prompts, summaries, questions, and slash-command output (including
  /gtr:help, /gtr:doctor, /gsd:* commands) must be in this language.
- Code, identifiers, comments, commit messages, and file contents
  must always be in English regardless of conversation language.
- Status lines, table headers, and command names stay verbatim
  (e.g. `/gtr:setup`, `IDENTITY.yaml`) — do not translate them.
```

**Case B — `## Communication` section already exists.** Replace only the language token in the first bullet (`Speak with the user in <Language>.`). Leave the rest of the bullets untouched. Do not duplicate the section.

---

## 3. Sync `.claude/.setup-complete`

If the marker file exists, read it and update the `language:` line to the new language. Preserve every other line. If the line is missing, append `language: <Language>` on its own line. If the marker file does not exist, skip this step silently — `/gtr:setup` writes it on first run.

---

## 4. Confirm

Print exactly one line in the **new** language, then stop:

> Conversation language set to <Language>. Future `/gtr:*` and `/gsd:*` output will follow.

For Turkish: `Konuşma dili Türkçe olarak ayarlandı. Bundan sonraki /gtr:* ve /gsd:* çıktıları bu dilde olacak.`

Do not list what you changed. Do not narrate the steps. The single confirmation line is the entire output.

---

## Notes

- Idempotent. Re-running with the same language is a no-op.
- Does **not** translate existing CLAUDE.md prose, ADRs, plan files, or commit history. Only the binding rule changes.
- Does **not** restart Claude Code or reload its session — the new language takes effect on the next `/gtr:*` or `/gsd:*` invocation that reads `## Communication`.
