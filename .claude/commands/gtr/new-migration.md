---
description: "[TEMPLATE] Scaffold a new database migration matching the project's detected migration tool."
---

Create a new database migration for: `$ARGUMENTS`

**Output language.** Read `## Communication` from `CLAUDE.md` and conduct the interview and any explanatory output in that language. The migration file content itself stays in English (it is code). File paths, tool names, and command output stay verbatim. If `## Communication` is missing, default to the language the user wrote the request in.

## 1. Detect the migration tool

Check, in this order, and stop at the first match:

| Tool | Signal | Migration dir | File naming |
|------|--------|---------------|-------------|
| **Alembic** (Python / SQLAlchemy) | `alembic.ini` exists | `alembic/versions/` (read `script_location` from `alembic.ini`) | `<auto>_<slug>.py`. Generate with `alembic revision -m "<title>"` (autogenerate if `--autogenerate` is appropriate). |
| **Django** | `manage.py` + `*/migrations/` dirs | per-app `<app>/migrations/` | `<NNNN>_<slug>.py`. Generate with `python manage.py makemigrations <app> -n "<slug>"`. |
| **Prisma** | `prisma/schema.prisma` exists | `prisma/migrations/<timestamp>_<slug>/migration.sql` | Generate with `npx prisma migrate dev --name "<slug>"`. |
| **Knex** | `knexfile.js` / `knexfile.ts` | `migrations/` (read `migrations.directory` from `knexfile`) | `<timestamp>_<slug>.{js,ts}`. Generate with `npx knex migrate:make <slug>`. |
| **TypeORM** | `ormconfig.*` or `data-source.ts` referencing migrations | `src/migrations/` (or as configured) | `<timestamp>-<PascalSlug>.ts`. Generate with `npm run typeorm migration:create src/migrations/<PascalSlug>`. |
| **sqlx (Rust)** | `migrations/` dir + `Cargo.toml` with `sqlx` | `migrations/` | `<timestamp>_<slug>.sql` (up) and optional `<timestamp>_<slug>.down.sql`. Generate with `sqlx migrate add <slug>`. |
| **diesel (Rust)** | `diesel.toml` exists | `migrations/<timestamp>_<slug>/up.sql` + `down.sql` | Generate with `diesel migration generate <slug>`. |
| **Flyway** | `db/migration/` dir with `V<n>__*.sql` files | `db/migration/` | `V<n>__<slug>.sql`. Compute `<n>` as max existing `V` number + 1. |
| **goose / atlas / sql-migrate** | tool config or `migrations/` with their conventions | per tool | per tool. |
| **none of the above** | a `migrations/` or `db/migrations/` dir exists | as found | mimic the latest file's naming convention. |
| **truly nothing** | no migration tool detected | — | stop and ask the user which tool to use; do not invent one. |

Prefer the tool's own scaffolder over hand-writing the file when it exists. Hand-write only when the tool does not provide a generator (Flyway, raw SQL fallback) or the user explicitly asks.

## 2. Write the migration

Whatever tool you used:

- Use `IF NOT EXISTS` / `IF EXISTS` guards where the dialect supports them.
- Add indexes on all foreign keys and commonly queried columns.
- Set explicit constraints (`NOT NULL`, `DEFAULT`, `CHECK`, `UNIQUE`) — do not rely on the dialect's defaults.
- Add a short SQL/Python comment explaining any non-obvious decision.
- For destructive changes (drop column, drop table, change type with data loss): **stop and confirm** with the user before proceeding. Document the rollback path. If the project uses `down`/`downgrade` hooks, fill them.

## 3. Update sibling artifacts

If the project has any of these, keep them in sync:

- ORM models / entities / dataclasses.
- Generated typed clients (`prisma generate`, `sqlx prepare`, etc.).
- Schema documentation (`docs/DATABASE.md`, `db/README.md`).
- Test fixtures or seed scripts.

Do not change application code that is unrelated to the schema change.

## 4. Verification

If the project supports it, run a dry-run of the migration locally before reporting completion. For Alembic: `alembic upgrade head --sql > /tmp/migration.sql`. For Prisma: `npx prisma migrate diff --from-empty --to-schema-datamodel`. For Flyway: `flyway info`. Capture any errors.

## 5. Report

- Path to the new migration file.
- Tool used and why (which signal matched).
- One-line summary of the schema change.
- Any follow-up changes required in application code.
- Rollback path (for destructive changes only).
