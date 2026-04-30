---
description: "[TEMPLATE] Scaffold a new Architecture Decision Record under docs/adr/."
---

Create a new ADR (Architecture Decision Record) for: `$ARGUMENTS`

ADRs capture significant technical decisions: why a choice was made, what was considered, what the trade-offs are. They live under `docs/adr/` and are numbered sequentially.

## Steps

1. Ensure `docs/adr/` exists. If not, create it and seed `docs/adr/0001-record-architecture-decisions.md` (a meta-ADR explaining the team adopts ADRs) — only on the very first call.
2. Find the highest existing ADR number under `docs/adr/`. Next number is that + 1, zero-padded to 4 digits.
3. Slugify the title from `$ARGUMENTS` (lowercase, hyphenated, ASCII).
4. Create the new file at `docs/adr/<NNNN>-<slug>.md` using the template below.
5. Open it for the user to fill the body. Do NOT auto-fill the Decision section unless the user provided enough detail in `$ARGUMENTS` to do so honestly.

## Template

```
# <NNNN>. <Title>

- Status: Proposed
- Date: <YYYY-MM-DD>
- Deciders: <names or roles>

## Context

<What is the problem? What are the forces at play? Stick to facts and constraints, not opinions.>

## Decision

<The decision in one or two sentences. Active voice. "We will use X."

If the decision is not yet made, mark Status: Proposed and leave this section as a question.>

## Consequences

### Positive

- <Concrete benefits — capabilities unlocked, simplifications, etc.>

### Negative

- <Concrete costs — complexity added, future migrations needed, lock-in.>

### Neutral

- <Things that change but are neither clearly good nor bad.>

## Alternatives considered

- **<Alternative 1>** — why rejected.
- **<Alternative 2>** — why rejected.

## References

- <Links to issues, PRs, prior art, papers.>
```

## Status lifecycle

`Proposed` → `Accepted` → (later) `Deprecated` or `Superseded by <NNNN>`. Never delete an old ADR; supersede it. Old ADRs are history, not garbage.

## Conventions

- One decision per ADR. If you need bullet lists of unrelated decisions, write multiple ADRs.
- Keep them short (1 page). If an ADR runs long, the decision is probably not crisp enough.
- Date stamps use `YYYY-MM-DD`, status changes append a line at the top of the file with the new status and date — keep history.
- Link related ADRs at the bottom of each one (`## References`).

## Report

- Path of the new ADR.
- Suggested next step: `Run /gsd:plan-phase if this decision changes a phase plan, or open a PR with the ADR as the only change to capture the decision in git history.`
