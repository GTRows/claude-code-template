# CLAUDE.md best practices

- Keep it under ~200 lines. Longer files waste context on every turn.
- Use concrete rules, not vague guidelines. "Use type hints on public functions" beats "write idiomatic code".
- Split into topic files using `.claude/rules/*.md` for large projects.
- Use `@filename` imports to reference other docs (saves duplication).
- Use path-specific rules (only loaded for matching files):

```markdown
---
paths:
  - "src/**/*.py"
---
# Python-specific rules for this module
- Use type hints on all public functions
- Prefer pathlib over os.path
```

## What goes in CLAUDE.md vs PROJECT.md (GSD) vs IDENTITY.yaml

- **CLAUDE.md** — coding rules, conventions, "what NOT to do", architecture pointers. Read every turn.
- **`.planning/PROJECT.md`** (GSD) — vision, success criteria, scope boundaries. Read when planning.
- **`IDENTITY.yaml`** — machine-readable identity (name, version, license, platforms). Read when releasing or generating manifests.

Three different files because they have three different audiences and read cadences. Do not merge them.
