# Archive Report: runtime-json-book

**Change**: runtime-json-book  
**Archived to**: `openspec/changes/archive/2026-10-07-runtime-json-book/`  
**Date**: 2026-10-07  
**Verify verdict**: PASS WITH WARNINGS (383 pytest passed; 0 blockers; 0 CRITICAL; 14/14 tasks; 10/10 scenarios)  
**Mode**: hybrid (OpenSpec filesystem + Engram)

## Engram Observation IDs (traceability)

| Artifact | Observation ID | Topic key |
|----------|----------------|-----------|
| proposal | #1162 | `sdd/runtime-json-book/proposal` |
| spec | #1163 | `sdd/runtime-json-book/spec` |
| design | #1164 | `sdd/runtime-json-book/design` |
| tasks | #1165 | `sdd/runtime-json-book/tasks` |
| verify-report | #1167 | `sdd/runtime-json-book/verify-report` |
| archive-report | #1168 | `sdd/runtime-json-book/archive-report` |

Review receipt topics (`sdd/runtime-json-book/review/*`): none found; archive proceeded on orchestrator-confirmed verify PASS WITH WARNINGS with no CRITICAL issues (same pattern as `max-docling-parse` / `llm-tools-host`).

## Specs Synced

| Domain | Action | Details |
|--------|--------|---------|
| docling-ingest | Confirmed (pre-merged in apply A.5) | 1 ADDED + 2 MODIFIED already present in `openspec/specs/docling-ingest/spec.md`; archive re-validated match to delta — no further edit |

### docling-ingest merge detail

- **ADDED**: Import-Free Recipe Extract Path (3 scenarios) — already in main
- **MODIFIED**: Docling Pin Without Graph (`extract_recipe` MUST NOT use `docling_core` / in-process pin) — already in main
- **MODIFIED**: Native Table Grid and Body List (body JSON `$ref` walk incl. nested `groups`; non-empty `data.grid` else `IngestError`; no `iterate_items` / `TableData`) — already in main
- **PRESERVED**: All other docling-ingest requirements (serve convert, dual seal, pin smoke, hashed store, sidecars, corpus pass, quarterly book, …)

No destructive REMOVED/RENAMED deltas. No merge warn required.

## Task Completion Gate

14/14 implementation tasks checked `[x]` in archived `tasks.md` (A.1–A.6, B.1–B.3, C.1–C.3, D.1–D.2). No stale checkboxes.

## Warnings carried into archive

1. Optional D.2 manual smoke (cache-hit book/query **without** Docling wheel installed) was not executed in verify — suite ran where Docling remains available for heavy/graph tests.
2. Proposal `Success Criteria` checkboxes remain unchecked in `proposal.md` despite implementation (hygiene only).
3. Cursor plan `.cursor/plans/runtime_json_book_followups.plan.md` left untouched per archive/verify instructions (todos may still show in_progress/pending).
4. Intentional archive with warnings — no CRITICAL findings.

## Follow-ups named (not in this change)

- Open WebUI `reply.py` → drawers → `DoclingReader`; Dockerfile keeps `.[retrieval]` — deferred follow-up (design Known gap / B.3).
- Design open question “Product job adds `--extra ingest`…” closed by CI reality: product job stays `dev`+`http`; ingest extra stays on heavy job only.

## Project bookkeeping

- `AGENTS.md`: Active change → `none`; archive list prepends `2026-10-07-runtime-json-book/`
- `openspec/config.yaml`: Active change → `none`; context notes archived runtime-json-book
- Phase 10: still deferred
- `auditoria-stack-nativo/`: still pending on-demand (not moved)
- `.cursor/plans/runtime_json_book_followups.plan.md`: not edited

## Archive Contents

- proposal.md ✅
- exploration.md ✅
- design.md ✅
- specs/docling-ingest/spec.md ✅
- tasks.md ✅ (14/14)
- verify-report.md ✅
- archive-report.md ✅

## SDD Cycle Complete

Planned, implemented, verified (PASS WITH WARNINGS), and archived. No git commit per user instruction.
