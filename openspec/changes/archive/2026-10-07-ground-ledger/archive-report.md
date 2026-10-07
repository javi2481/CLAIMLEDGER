# Archive Report: ground-ledger

**Change**: ground-ledger
**Archived to**: `openspec/changes/archive/2026-10-07-ground-ledger/`
**Date**: 2026-10-07
**Persistence**: hybrid
**Verdict**: archived and closed (intentional-with-warnings)
**Git commit**: not created (user asked not to commit)
**Review lineage**: none in this change folder; no Engram `sdd/ground-ledger/review/*` observations

## Gates

| Gate | Result | Evidence |
|------|--------|----------|
| Task completion | 8/8 `[x]` | `tasks.md` tasks 1.1–1.6, 2.1–2.2. No `- [ ]` remains |
| Verify | pass_with_warnings | `verify-report.md`: `python -m pytest` 344 passed, 0 failed, 0 skipped, exit 0. CRITICAL 0. Blockers 0 |
| Destructive merge | none | ADDED Quarterly Book; MODIFIED Hash Store, Call Order, Compare, HTTP question/JSON, Measure Then Card. No REMOVED. Gold untouched |

## Engram Observation IDs (traceability)

| Artifact | Observation ID | Notes |
|----------|----------------|-------|
| proposal | — | Not in Engram; filesystem only |
| spec | — | Not in Engram; filesystem only |
| design | — | Not in Engram; filesystem only |
| tasks | — | Not in Engram; filesystem only |
| verify-report | #1137 | `sdd/ground-ledger/verify-report` |
| apply-progress | — | Missing (verify WARNING; TDD reconstructed from tasks+tests) |
| review/* | — | Missing; archive proceeded on explicit orchestrator/user request with PASS WITH WARNINGS and 0 product blockers |

## Specs Synced

| Domain | Action | Details |
|--------|--------|---------|
| docling-ingest | Updated | ADDED Quarterly Book (2 scenarios). MODIFIED Hashed Immutable JSON Store (+2 mismatch scenarios) |
| verify-eval | Updated | MODIFIED Call Order (+omitted-ledger scenario; no seed on product path). MODIFIED Compare Without Subtraction (ledger argument) |
| http-query | Updated | MODIFIED Question Calls Understand Then Query (`recorded_book`). MODIFIED Verified Rector JSON (+route forwards book evidence) |
| openwebui-host | Updated | MODIFIED Measure Then Card (one book per completion; +Reply uses the quarterly book) |

Not touched: `gold-regression`, `query`, `ledger`, `book`, `orchestrate`, `chart`, `document-graph`, `json-retrieval`, `page-crop`, `claim-card`, `identity`, `lookup`, `evidence-adapter`.

## What did not move

- Gold numbers stay frozen: `21262335`, `21259769`.
- Kernel tests keep `Ledger.seed()`. Kernel modules and gold files were not reopened.
- Phase 10 stays deferred. No GPU for VLM second reader.
- `openspec/changes/auditoria-stack-nativo/` stays pending on demand.
- Rector and north-star untouched.

## Archive-time repairs

- Proposal success-criteria checkboxes ticked `[x]` per verify WARNING (“Archive may tick them”); criteria satisfied by the compliance matrix (26/26).

## AGENTS.md

Closing status line set by this archive:

> Active change: none. Deferred: phase 10, VLM second reader, until there is a GPU to run it. Pending: `openspec/changes/auditoria-stack-nativo/` (on demand, not a wave step). Archived: `openspec/changes/archive/2026-10-07-ground-ledger/`, then the existing archive list.

## `openspec/config.yaml`

Context line updated: Active change cleared (none). Phase 10 deferred and auditoria on-demand unchanged.

## Archive Contents

- proposal.md (success criteria checked at archive)
- specs/docling-ingest/spec.md
- specs/verify-eval/spec.md
- specs/http-query/spec.md
- specs/openwebui-host/spec.md
- design.md
- tasks.md (8/8 complete)
- verify-report.md
- archive-report.md (this file)

Active path `openspec/changes/ground-ledger/` no longer exists after the move.

## What stays pending

- Phase 10 stays deferred. There is no GPU to run the VLM second reader.
- `openspec/changes/auditoria-stack-nativo/` stays an on-demand call.
- Optional: persist a retrospective `sdd/ground-ledger/apply-progress` if the audit trail must match earlier phases (verify SUGGESTION only).
