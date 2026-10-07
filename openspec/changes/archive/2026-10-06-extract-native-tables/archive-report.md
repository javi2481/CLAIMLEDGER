# Archive Report: extract-native-tables

**Change**: extract-native-tables
**Archived to**: `openspec/changes/archive/2026-10-06-extract-native-tables/`
**Date**: 2026-10-06
**Persistence**: hybrid
**Verdict**: archived and closed
**Git commit**: not created (the user asked to close the finished work, not to commit)
**Review lineage**: `openspec/changes/auditoria-stack-nativo/runs/2026-10-05/audit.md`

## Gates

| Gate | Result | Evidence |
|------|--------|----------|
| Task completion | 8/8 `[x]` | `tasks.md` tasks 1.1–1.3, 2.1–2.4, 3.1 |
| Verify | PASS WITH WARNINGS | `verify-report.md`: `python -m pytest tests/ -q` 309 passed, 0 failed, exit 0. One suite-order torch failure was fixed by importing torch before Docling, the same guard `parse.py` already uses. `test_wave_c_still_waits` now looks for the archived crop folder |
| Destructive merge | none | `docling-ingest` gained the native grid and body-list requirement. Recipe selection, bbox clamp, and gold stayed. Rector and north-star untouched |

The user asked on 2026-10-06 to close what was already done.

## Specs Synced

| Domain | Action | Details |
|--------|--------|---------|
| docling-ingest | Added | Stored grid, `TableData.grid` when the grid is missing, and `iterate_items` for the body list |

## Archive Contents

- proposal.md
- exploration.md
- design.md
- tasks.md (8/8)
- specs/docling-ingest/spec.md
- verify-report.md
- archive-report.md (this file)

Active path `openspec/changes/extract-native-tables/` no longer exists.

## What stays pending

- `openspec/changes/auditoria-stack-nativo/` stays callable. It is not a wave number.
- Phases 9–13 are not opened.
