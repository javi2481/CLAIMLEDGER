# Archive Report: max-docling-parse

**Change**: max-docling-parse  
**Archived to**: `openspec/changes/archive/2026-10-07-max-docling-parse/`  
**Date**: 2026-10-07  
**Verify verdict**: PASS WITH WARNINGS (377 pytest passed; `/version` smoke OK; live corpus deferred; 0 blockers; 0 CRITICAL)  
**Mode**: hybrid (OpenSpec filesystem + Engram)

## Engram Observation IDs (traceability)

| Artifact | Observation ID | Topic key |
|----------|----------------|-----------|
| proposal | #1153 | `sdd/max-docling-parse/proposal` |
| design | #1154 | `sdd/max-docling-parse/design` |
| spec | #1155 | `sdd/max-docling-parse/spec` |
| tasks | #1156 | `sdd/max-docling-parse/tasks` |
| verify-report | #1158 | `sdd/max-docling-parse/verify-report` |
| archive-report | #1159 | `sdd/max-docling-parse/archive-report` |

Review receipt topics (`sdd/max-docling-parse/review/*`): none found; archive proceeded on orchestrator-confirmed verify PASS WITH WARNINGS with no CRITICAL issues (same pattern as `llm-tools-host`).

## Specs Synced

| Domain | Action | Details |
|--------|--------|---------|
| docling-ingest | Updated | 4 ADDED + 6 MODIFIED requirements; preserved Native Table Grid and Quarterly Book |

### docling-ingest merge detail

- **ADDED**: Docling-Serve Convert Only (3 scenarios)
- **ADDED**: Non-VLM Dual Seal (1 scenario)
- **ADDED**: Serve Version Pin Smoke (1 scenario)
- **ADDED**: Convert Unit Tests Mock HTTP (1 scenario)
- **MODIFIED**: In-Corpus Local PDFs (serve `convert_local`; ban `/v1/convert/source`)
- **MODIFIED**: Hashed Immutable JSON Store (`convert_local` naming)
- **MODIFIED**: Docling Pin Without Graph (serve pin via `/version`; extract_recipe MAY keep `docling_core`)
- **MODIFIED**: Sidecar Page Raster Outside the Hash (PNGs from ZIP referenced)
- **MODIFIED**: DocLang Sidecar On Every Parse (ZIP DocLang; missing `.dclg` ⇒ recompile)
- **MODIFIED**: Corpus Pass Covers Every Sample PDF (compiler `.dclg`; no reconvert when complete)
- **PRESERVED**: Native Table Grid and Body List, Quarterly Book

## Task Completion Gate

15/15 implementation tasks checked `[x]` in archived `tasks.md`. No stale checkboxes.

## Warnings carried into archive

1. Live ten-PDF corpus convert + one-PDF artifact materialization + query-with-serve-stopped deferred (verify PARTIAL on "Ten local files are stored").
2. ZIP member names after first real convert still an open design question.
3. Intentional archive with warnings — no CRITICAL findings.

## Project bookkeeping

- `AGENTS.md`: Active change → `none`; archive list prepends `2026-10-07-max-docling-parse/`
- `openspec/config.yaml`: Active change → `none`; context notes archived max-docling-parse
- Phase 10: still deferred
- `auditoria-stack-nativo/`: still pending on-demand (not moved)

## Archive Contents

- proposal.md ✅
- exploration.md ✅
- design.md ✅
- specs/docling-ingest/spec.md ✅
- tasks.md ✅ (15/15)
- verify-report.md ✅
- archive-report.md ✅

## SDD Cycle Complete

Planned, implemented, verified (PASS WITH WARNINGS), and archived. No commit / no PR per user instruction — commits are user-owned.
