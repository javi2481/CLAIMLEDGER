# Archive Report: fase-11-neo4j

**Change**: fase-11-neo4j
**Archived to**: `openspec/changes/archive/2026-10-07-fase-11-neo4j/`
**Date**: 2026-10-07
**Persistence**: hybrid
**Verdict**: archived and closed
**Git commit**: not created (the user asked to implement the phase, not to commit)
**Review lineage**: none in this change folder

## Gates

| Gate | Result | Evidence |
|------|--------|----------|
| Task completion | 10/10 `[x]` | `tasks.md` tasks 1.1, 2.1–2.4, 3.1–3.2, 4.1–4.3. No `- [ ]` remains |
| Verify | pass | `verify-report.md`: `python -m pytest -q` 334 passed, 0 failed, 0 skipped, exit 0 |
| Destructive merge | none on gold | The phase 2 name ban on `CypherExporter` is lifted on purpose. Claim values stay out of the script |

## Specs Synced

| Domain | Action | Details |
|--------|--------|---------|
| book | Added | New `openspec/specs/book/spec.md`. Periods from the script. One `query` per period |
| document-graph | Modified | `build` writes `graph.cypher`. A Neo4j driver stays absent. The script has the period and not `21262335` |
| openwebui-host | Modified | The book question draws the fence. HTTP stays abstained. Phase 10 stays unopened. Allowlist excludes `book` |

Not touched: `gold-regression`, `query`, `claim-card`, `http-query`, `chart`, `orchestrate`.

## What did not move

- Gold numbers stay frozen: `21262335`, `21259769`, `81956525`, `81946993`.
- `60694190` is not a claim value and is absent from the book reply.
- `query` still abstains when the period is unnamed and two claims match. The book calls it once per period.
- Rector and north-star untouched.

## Guard retarget

`test_wave_c_still_waits` required an active `fase-11-neo4j` during apply. The archive points it at `openspec/changes/archive/*-fase-11-neo4j` and rejects an active name starting with `fase-10` or `fase-11`. Package `book` stays required.

## AGENTS.md

Closing status line set by this archive:

> Active change: none. Deferred: phase 10, VLM second reader, until there is a GPU to run it. Pending: `openspec/changes/auditoria-stack-nativo/` (on demand, not a wave step). Archived: `openspec/changes/archive/2026-10-07-fase-11-neo4j/`, then the existing archive list.

## Archive Contents

- proposal.md
- exploration.md
- specs/book/spec.md
- specs/document-graph/spec.md
- specs/openwebui-host/spec.md
- design.md
- tasks.md (10/10 complete)
- verify-report.md
- archive-report.md (this file)

Active path `openspec/changes/fase-11-neo4j/` no longer exists after the move.

## What stays pending

- Phase 10 stays deferred. There is no GPU to run the VLM second reader.
- `openspec/changes/auditoria-stack-nativo/` stays an on-demand call.
