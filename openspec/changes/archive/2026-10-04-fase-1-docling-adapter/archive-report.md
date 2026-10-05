# Archive Report: fase-1-docling-adapter

**Change**: fase-1-docling-adapter
**Archived to**: `openspec/changes/archive/2026-10-04-fase-1-docling-adapter/`
**Date**: 2026-10-04
**Persistence**: hybrid
**Verdict**: archived and closed
**Git commit**: not created (explicit instruction)
**Review lineage**: `review-70aa05133f7daa23`
**Review gate**: allow

## Gates

| Gate | Result | Evidence |
|------|--------|----------|
| Native review receipt | allow / approved | Orchestrator `reviewGate.result: allow`; `reviews/receipt.json` `terminal_state: approved`; lineage `review-70aa05133f7daa23`; post-apply validate `allow`; `blockedReasons: []` |
| Task completion | 10/10 `[x]` | Archived `tasks.md` and Engram `#1021`; apply-progress `#1022` |
| Verify | PASS WITH WARNINGS | Engram `#1023`; 0 CRITICAL; 7/7 requirements; 11/11 scenarios; `python -m pytest tests/` exit 0, 184 passed |
| Destructive merge | none | Two new full specs copied. One gold-regression requirement replaced. Frozen numeric contracts preserved. Rector and north-star untouched. Fase 0 archive untouched. |

## Specs Synced

| Domain | Action | Details |
|--------|--------|---------|
| docling-ingest | Created | 3 added, 0 modified, 0 removed. Full spec copied to `openspec/specs/docling-ingest/spec.md` |
| evidence-adapter | Created | 3 added, 0 modified, 0 removed. Full spec copied to `openspec/specs/evidence-adapter/spec.md` |
| gold-regression | Updated | 0 added, 1 modified, 0 removed. `Docling-Free Pytest Demo` replaced in full. Four other requirements preserved, including frozen numbers `21262335`, `21259769`, `81956525`, `81946993`, `60144176`, `70223471`, `36213283`, `-14950948`, `2566`, `122610546`, `143236114`, `114688061`, `-32731536`, `9532`, and prior `22362983` |

The delta `(Previously: ...)` note was change commentary and was not copied into the main spec. Numeric gold was not relaxed. `Ledger.seed()` remains the kernel gold.

Source of truth now includes:

- `openspec/specs/docling-ingest/spec.md`
- `openspec/specs/evidence-adapter/spec.md`
- `openspec/specs/gold-regression/spec.md`

## Archive Contents

- proposal.md ✅
- exploration.md ✅
- specs/{docling-ingest,evidence-adapter,gold-regression}/spec.md ✅
- design.md ✅
- tasks.md ✅ (10/10 complete; no unchecked implementation tasks)
- verify-report.md ✅
- reviews/receipt.json ✅
- archive-report.md ✅ (this file)

Active path `openspec/changes/fase-1-docling-adapter/` no longer exists.
`openspec/changes/archive/2026-09-23-fase-0-kernel/` remains.

## Native Review Receipt

```json
{
  "schema": "gentle-ai.review-receipt/v2",
  "lineage_id": "review-70aa05133f7daa23",
  "generation": 1,
  "base_tree": "82a2f51dc3e3cfd1ecbf2ea1131722f0afd97391",
  "initial_review_tree": "5c9c04a187e9ae8dec3c63d4844f511cb2795471",
  "final_candidate_tree": "a177e8b04fe6e9fed5fd36dfe54fe2b16c72cc13",
  "paths_digest": "sha256:8bb9fddf03389b977fe2ea3b133682d296b75b55fcb2420600ed418d8a0bd136",
  "fix_delta_hash": "sha256:a7626c13452c9b567ba8ebf804fcb3a716b7de2d42e6e6ef5366619d4b501a5b",
  "policy_hash": "sha256:34fb63d7f29f8613cd4431382b1057398a4816f8a4c20fc34677fffc80a184f6",
  "evidence_hash": "sha256:9ad0533f6cd97ed07f09e8b24b1e5131cea8d633249f81c6012daf68485e4466",
  "risk_level": "high",
  "terminal_state": "approved"
}
```

## Observation IDs (traceability)

| Artifact | Engram ID | Sync ID | Topic |
|----------|-----------|---------|-------|
| explore | #1017 | obs-96efcc963fde6893 | sdd/fase-1-docling-adapter/explore |
| proposal | #1018 | obs-ff416308eeda7d7e | sdd/fase-1-docling-adapter/proposal |
| spec | #1020 | obs-99f0e23efefad510 | sdd/fase-1-docling-adapter/spec |
| design | #1019 | obs-193a70368762c357 | sdd/fase-1-docling-adapter/design |
| tasks | #1021 | obs-cbe182b6252332e2 | sdd/fase-1-docling-adapter/tasks |
| apply-progress | #1022 | obs-c0ed919d2bd131d7 | sdd/fase-1-docling-adapter/apply-progress |
| verify-report | #1023 | obs-d1cd145913514edf | sdd/fase-1-docling-adapter/verify-report |
| review/transaction | not found | — | sdd/fase-1-docling-adapter/review/transaction |
| review/ledger | not found | — | sdd/fase-1-docling-adapter/review/ledger |
| review/receipt | not found in Engram | filesystem receipt only | sdd/fase-1-docling-adapter/review/receipt |
| review/gate-context | not found | — | sdd/fase-1-docling-adapter/review/gate-context |

Archive proceeded because orchestrator native status supplied `reviewGate.result: allow` and the filesystem receipt is an approved terminal receipt matching lineage `review-70aa05133f7daa23`. Engram review topics were never persisted.

## Out of scope (honored)

- No git commit
- No new change started
- `docs/documento-rector.md` not edited
- `docs/north-star.md` not edited
- Archived Fase 0 not deleted

## Residual notes (non-blocking)

- Verify verdict is PASS WITH WARNINGS: task 5.1 RED did not fail (extract already matched frozen `RECIPE_ROWS`); `parse.py` statement coverage 36%; `extract.py` branch-adjusted cover 75%; two WARNING assertions in `tests/ingest/test_extract.py`. Zero CRITICAL.
- `AGENTS.md` active-change line now points at the archive paths for this change and Fase 0.

## SDD Cycle Complete

The change has been fully planned, implemented, verified, reviewed (`allow`), and archived. Ready for a later `/sdd-new` if a new change is requested. Not starting a new change.
