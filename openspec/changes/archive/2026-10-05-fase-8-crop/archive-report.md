# Archive Report: fase-8-crop

**Change**: fase-8-crop
**Archived to**: `openspec/changes/archive/2026-10-05-fase-8-crop/`
**Date**: 2026-10-05
**Persistence**: hybrid
**Verdict**: archived and closed
**Git commit**: not created (the user asked to archive, not to commit)
**Review lineage**: none in this change folder

## Gates

| Gate | Result | Evidence |
|------|--------|----------|
| Task completion | 12/12 `[x]` | `tasks.md` tasks 1.1–1.3, 2.1–2.4, 3.1–3.2, 4.1–4.3 |
| Verify | PASS WITH WARNINGS | `verify-report.md`: `python -m pytest tests/ -q` 307 passed, 0 failed, 0 skipped, exit 0. Requirements 8/9. Scenarios 21/22, one partial. 0 blockers, 0 critical findings. Evidence `sha256:988fd3ca0b00c0750545a1a6fb0ba2579df6a0778b41ce6458faf4cb0a16102d` |
| Destructive merge | none | New spec `page-crop` copied. `openwebui-host` updated in place for the picture after the card. `docling-ingest` gained the page-PNG sidecar requirement. Gold `21262335` and `21259769` unchanged. Rector and north-star untouched |

The partial scenario is "Later work stays out": the verify report marks it partial because the test does not assert MinerU or another viewer by name. Phases 9–13 stay out of this archive. The user asked to archive the finished crop on 2026-10-05. There is no `reviews/receipt.json` in this change.

## Specs Synced

| Domain | Action | Details |
|--------|--------|---------|
| page-crop | Created | Full spec copied to `openspec/specs/page-crop/spec.md` |
| openwebui-host | Modified | Card text stays first. A page-crop PNG may follow in the same completion. Crop no longer waits. Subtraction, charts, and the orchestrator still wait. Phases 9–13 stay unstarted |
| docling-ingest | Added | Sidecar page raster outside the hash. Pin stays `docling==2.130.0` |

`claim-card`, `http-query`, `verify-eval`, and `gold-regression` were not rewritten.

## Archive Contents

- proposal.md
- exploration.md
- specs/page-crop/spec.md
- specs/openwebui-host/spec.md
- specs/docling-ingest/spec.md
- design.md
- tasks.md (12/12 complete)
- verify-report.md
- archive-report.md (this file)

Active path `openspec/changes/fase-8-crop/` no longer exists.

## What stays pending

- `openspec/changes/fase-1a-corpus-parse/` is the active change. The corpus pass is not run.
- `openspec/changes/auditoria-stack-nativo/` stays pending as an on-demand call. It is not a wave number and it was not part of this archive.
- Phases 9–13 are not opened.
