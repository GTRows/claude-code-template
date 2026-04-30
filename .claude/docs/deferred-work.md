# Deferred work (GSD ISSUES.md)

Work that is intentionally postponed lives in `.planning/ISSUES.md` (managed by GSD). Each entry must answer four questions. If you cannot, it is not "deferred", it is "undecided" — keep it out of this file.

- **What** — the change in one line.
- **Why deferred** — concrete reason it is not being done now (cost, risk, missing info, blocked on other work).
- **Trigger** — specific, observable event that turns this back on (version bump, library reaches stable, user count threshold, bug report, etc.).
- **Owner** — person or role responsible for reassessing.

Surface ready-to-act items with `/gsd:consider-issues`.

Do **not** leave TODO comments in code instead — those rot silently.

## Example entry

```
## Switch Postgres to managed instance
- Why deferred: current workload fits the self-hosted container; cost not yet justified
- Trigger: monthly DB CPU > 60% sustained for 7 days, OR team > 5 engineers
- Owner: infra
```
