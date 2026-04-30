---
description: Create a new database migration file
---

Create a new database migration for: $ARGUMENTS

Steps:
1. Read the project's database documentation (commonly `docs/DATABASE.md`, `db/README.md`, or the schema source) to understand existing tables, columns, and conventions.
2. Locate the migrations directory (e.g. `db/migrations/`, `backend/src/main/resources/db/migration/`, `prisma/migrations/`, `supabase/migrations/`). Identify the latest migration and its naming convention (Flyway `V{n}__name.sql`, timestamp-prefixed, sequential, etc.).
3. Create a new migration file using that convention. Never edit an existing migration.
4. Write the migration:
   - Use `IF NOT EXISTS` / `IF EXISTS` guards where the tool supports them.
   - Add indexes on all foreign keys and commonly queried columns.
   - Set explicit constraints (`NOT NULL`, `DEFAULT`, `CHECK`, `UNIQUE`) rather than relying on defaults.
   - Add a short SQL comment explaining any non-obvious decision.
   - For destructive changes (drop column, drop table, change type with data loss): stop and confirm with the user before proceeding, and document the rollback path.
5. Update schema documentation to reflect the change.
6. Update ORM models / entities / generated clients if the project has them.
7. If the project uses a testing fixture or seed script, update it to remain compatible.

Report:
- Path to the new migration file
- Summary of the schema change
- Any follow-up changes required in application code
