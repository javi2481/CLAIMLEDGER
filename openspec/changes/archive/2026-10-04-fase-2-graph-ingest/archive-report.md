# Archive Report: fase-2-graph-ingest

**Change**: fase-2-graph-ingest
**Archived to**: `openspec/changes/archive/2026-10-04-fase-2-graph-ingest/`
**Date**: 2026-10-04
**Persistence**: hybrid
**Verdict**: archived and closed
**Git commit**: not created (explicit instruction)
**Review lineage**: `review-3d266977f51431c5`
**Review gate**: allow

## Gates

| Gate | Result | Evidence |
|------|--------|----------|
| Native review receipt | allow / approved | Orchestrator `reviewGate.result: allow`; `reviews/receipt.json` `terminal_state: approved`; lineage `review-3d266977f51431c5`; post-apply validate `allow`; `blockedReasons: []` |
| Task completion | 8/8 `[x]` | Archived `tasks.md` and Engram `#1029`; apply-progress `#1030` |
| Verify | PASS WITH WARNINGS | Engram `#1031`; 0 CRITICAL; 4/4 requirements; 8/8 scenarios; `python -m pytest tests/` exit 0, 212 passed |
| Destructive merge | none | One new full spec copied. One gold-regression requirement replaced. Frozen numeric contracts preserved. Rector and north-star untouched. Fase 0 and Fase 1 archives untouched. |

## Specs Synced

| Domain | Action | Details |
|--------|--------|---------|
| document-graph | Created | 3 added, 0 modified, 0 removed. Full spec copied to `openspec/specs/document-graph/spec.md` |
| gold-regression | Updated | 0 added, 1 modified, 0 removed. `Docling-Free Pytest Demo` replaced in full, including scenario `Kernel absence ignores a later graph load`. Four other requirements preserved, including frozen numbers `21262335`, `21259769`, `81956525`, `81946993`, `60144176`, `70223471`, `36213283`, `-14950948`, `2566`, `122610546`, `143236114`, `114688061`, `-32731536`, `9532`, and prior `22362983` |

The delta `(Previously: ...)` note was change commentary and was not copied into the main spec. Numeric gold was not relaxed. `Ledger.seed()` remains the kernel gold. `src/claimledger/graph/` and `tests/graph/` MAY import `docling-graph==1.9.1`. Kernel and ingest stay forbidden from that import.

Source of truth now includes:

- `openspec/specs/document-graph/spec.md`
- `openspec/specs/gold-regression/spec.md`

## Archive Contents

- proposal.md ✅
- exploration.md ✅
- specs/{document-graph,gold-regression}/spec.md ✅
- design.md ✅
- tasks.md ✅ (8/8 complete; no unchecked implementation tasks)
- verify-report.md ✅
- reviews/receipt.json ✅
- archive-report.md ✅ (this file)

Active path `openspec/changes/fase-2-graph-ingest/` no longer exists.
`openspec/changes/archive/2026-10-04-fase-1-docling-adapter/` remains.
`openspec/changes/archive/2026-09-23-fase-0-kernel/` remains.

## Native Review Receipt

Filesystem mirror `reviews/receipt.json` matches `.git/gentle-ai/review-transactions/v2/review-3d266977f51431c5/review-receipt.json` and the frozen review-state hashes.

```json
{
  "schema": "gentle-ai.review-receipt/v2",
  "lineage_id": "review-3d266977f51431c5",
  "generation": 1,
  "base_tree": "82a2f51dc3e3cfd1ecbf2ea1131722f0afd97391",
  "initial_review_tree": "cbd885b2d93585253aa4074f1c87eb3ecb51ac8c",
  "final_candidate_tree": "cbd885b2d93585253aa4074f1c87eb3ecb51ac8c",
  "paths_digest": "sha256:ebfd10b5f712ff3315f7cd8a48d4cfdbbd1af18f234e6c83e47775c8ad672054",
  "fix_delta_hash": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "policy_hash": "sha256:34fb63d7f29f8613cd4431382b1057398a4816f8a4c20fc34677fffc80a184f6",
  "evidence_hash": "sha256:a5b2cb05225a5c51a18022560c7db4fdf9a0fa5f9079abdf8e6a66587b70399c",
  "risk_level": "high",
  "terminal_state": "approved"
}
```

Review-state `state` is `approved`. Lens findings are empty. `fix_delta_hash` is the empty-bytes digest. Base relationship is unchanged: `base_tree` `82a2f51dc3e3cfd1ecbf2ea1131722f0afd97391`.

## Observation IDs (traceability)

| Artifact | Engram ID | Sync ID | Topic |
|----------|-----------|---------|-------|
| explore | #1025 | obs-60f5e8da14e3adcb | sdd/fase-2-graph-ingest/explore |
| proposal | #1026 | obs-e217ed8735f4966a | sdd/fase-2-graph-ingest/proposal |
| design | #1027 | obs-ca98d87f0e292cb7 | sdd/fase-2-graph-ingest/design |
| spec | #1028 | obs-0985b147d8557555 | sdd/fase-2-graph-ingest/spec |
| tasks | #1029 | obs-79ae5d16930cc98e | sdd/fase-2-graph-ingest/tasks |
| apply-progress | #1030 | obs-8a1cadf7ddbe9365 | sdd/fase-2-graph-ingest/apply-progress |
| verify-report | #1031 | obs-8f70df0c88679f84 | sdd/fase-2-graph-ingest/verify-report |
| review/transaction | not found | — | sdd/fase-2-graph-ingest/review/transaction |
| review/ledger | not found | — | sdd/fase-2-graph-ingest/review/ledger |
| review/receipt | not found in Engram | filesystem receipt only | sdd/fase-2-graph-ingest/review/receipt |
| review/gate-context | not found | — | sdd/fase-2-graph-ingest/review/gate-context |

Archive proceeded because orchestrator native status supplied `reviewGate.result: allow` and the filesystem receipt is an approved terminal receipt matching lineage `review-3d266977f51431c5`. Engram review topics were never persisted. The frozen ledger lives in `.git/gentle-ai/review-transactions/v2/review-3d266977f51431c5/review-state.json`.

## Out of scope (honored)

- No git commit
- No Fase 3 started
- `docs/documento-rector.md` not edited
- `docs/north-star.md` not edited
- Archived Fase 0 and Fase 1 not deleted

## Residual notes (non-blocking)

- Verify verdict is PASS WITH WARNINGS: `Document.doubt` is set in `build.py` while the design table names `link.py`; `pyproject.toml` gained `addopts = "--import-mode=importlib"`; `tests/graph/test_store.py` lines 153–162 assert source text. Zero CRITICAL.
- Canonical `openspec/specs/gold-regression/spec.md` now carries the Fase 2 graph permission that verify found only in the delta.
- `AGENTS.md` active change is none. This archive path is listed with the Fase 1 and Fase 0 archives.

## SDD Cycle Complete

The change has been fully planned, implemented, verified, reviewed (`allow`), and archived. Ready for a later `/sdd-new` if a new change is requested. Not starting a new change.
