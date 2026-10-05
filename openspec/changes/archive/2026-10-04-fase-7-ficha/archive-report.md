# Archive Report: fase-7-ficha

**Change**: fase-7-ficha
**Archived to**: `openspec/changes/archive/2026-10-04-fase-7-ficha/`
**Date**: 2026-10-04
**Persistence**: hybrid
**Verdict**: archived and closed
**Git commit**: not created (explicit instruction)
**Review lineage**: `review-bd24a3dd49888a5f`
**Review gate**: allow

## Gates

| Gate | Result | Evidence |
|------|--------|----------|
| Native review receipt | allow / approved | Orchestrator `reviewGate.result: allow`; change-local `reviews/receipt.json` `terminal_state: approved`; native `.git/gentle-ai/review-transactions/v2/review-bd24a3dd49888a5f/review-receipt.json` `terminal_state: approved`; lineage `review-bd24a3dd49888a5f`; post-apply validate `allow`; `store_revision` `sha256:ef0e493ed886799a4cb46afe122285a71d8266d1333f41af9f0e1cb652a2cb5c`; `evidence_hash` `sha256:8daaf6bb5d6256adf1276b174601a9f26ca877ec371e4e6d3313b7c8327779be`; `candidate_tree` `7eb3d67b5fbf6a95c6856be2aa5620072fce8e20`; `fix_delta` empty; `base_relationship_valid` true |
| Task completion | 4/4 `[x]` | Archived `tasks.md` and Engram `#1068` (1.1, 1.2, 2.1, 2.2). No unchecked implementation tasks. |
| Verify | PASS | Engram `#1070`; 0 CRITICAL; 8/8 requirements; 17/17 scenarios. Canonical verify capture is 280 passed, evidence `sha256:d95ce0fb75ad2ca3478a10a19f0d23fe1f464c80ffc8874a96c68c0473017dfa`. A later chip fix passed 281; that evidence is `sha256:8daaf6bb5d6256adf1276b174601a9f26ca877ec371e4e6d3313b7c8327779be` and is not a CRITICAL. |
| Destructive merge | none | One new full spec copied. One gold-regression requirement replaced. Frozen numeric contracts preserved. Rector and north-star untouched. Fase 0 through Fase 6 archives untouched. |

Older lineage `review-881a16ff96640658` was ignored. It captured nothing and is not this delivery.

## Specs Synced

| Domain | Action | Details |
|--------|--------|---------|
| claim-card | Created | 7 added, 0 modified, 0 removed. Full spec copied to `openspec/specs/claim-card/spec.md` (Pure Display, Verified Consolidated Card, Verified Parent Card, Abstain Card, Compare Card, Seal Follows Query Status, Package Boundary) |
| gold-regression | Updated | 0 added, 1 modified, 0 removed. `Docling-Free Pytest Demo` replaced in full, including scenario `Card stays off the scan`. Four other requirements preserved, including frozen numbers `21262335`, `21259769`, `81956525`, `81946993`, `60144176`, `70223471`, `36213283`, `-14950948`, `2566`, `122610546`, `143236114`, `114688061`, `-32731536`, `9532`, and prior `22362983` |

The delta `(Previously: the 13-path scan excluded http and did not name the card package.)` note was change commentary and was not copied into the main spec. Numeric gold was not relaxed. `src/claimledger/card/` and `tests/card/` stay outside the 13-path scan. Kernel tests MUST NOT import the card if that would load a UI stack.

Source of truth now includes:

- `openspec/specs/claim-card/spec.md`
- `openspec/specs/gold-regression/spec.md`

## Archive Contents

- proposal.md ✅
- exploration.md ✅
- specs/{claim-card,gold-regression}/spec.md ✅
- design.md ✅
- tasks.md ✅ (4/4 complete; no unchecked implementation tasks)
- verify-report.md ✅
- reviews/receipt.json ✅
- archive-report.md ✅ (this file)

Active path `openspec/changes/fase-7-ficha/` no longer exists.
`openspec/changes/archive/2026-10-04-fase-6-http/` remains.
`openspec/changes/archive/2026-10-04-fase-4-verify-eval/` remains.
`openspec/changes/archive/2026-10-04-fase-3-retrieval/` remains.
`openspec/changes/archive/2026-10-04-fase-2-graph-ingest/` remains.
`openspec/changes/archive/2026-10-04-fase-1-docling-adapter/` remains.
`openspec/changes/archive/2026-09-23-fase-0-kernel/` remains.

## Native Review Receipt

Filesystem mirror `reviews/receipt.json` matches `.git/gentle-ai/review-transactions/v2/review-bd24a3dd49888a5f/review-receipt.json`. Review-state `state` is `approved`. `store_revision` is `sha256:ef0e493ed886799a4cb46afe122285a71d8266d1333f41af9f0e1cb652a2cb5c`. Current snapshot `candidate_tree` is `7eb3d67b5fbf6a95c6856be2aa5620072fce8e20`, matching `final_candidate_tree`.

```json
{
  "schema": "gentle-ai.review-receipt/v2",
  "lineage_id": "review-bd24a3dd49888a5f",
  "generation": 1,
  "base_tree": "82a2f51dc3e3cfd1ecbf2ea1131722f0afd97391",
  "initial_review_tree": "7eb3d67b5fbf6a95c6856be2aa5620072fce8e20",
  "final_candidate_tree": "7eb3d67b5fbf6a95c6856be2aa5620072fce8e20",
  "paths_digest": "sha256:03066532c95a20704758e9de3e153fce11f26bdea3dfbabb6fbefe2524b1437f",
  "fix_delta_hash": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "policy_hash": "sha256:34fb63d7f29f8613cd4431382b1057398a4816f8a4c20fc34677fffc80a184f6",
  "evidence_hash": "sha256:8daaf6bb5d6256adf1276b174601a9f26ca877ec371e4e6d3313b7c8327779be",
  "risk_level": "high",
  "terminal_state": "approved"
}
```

`fix_delta_hash` is the empty-bytes digest. Base relationship is valid: `base_tree` `82a2f51dc3e3cfd1ecbf2ea1131722f0afd97391`. Initial and current snapshots share `candidate_tree` `7eb3d67b5fbf6a95c6856be2aa5620072fce8e20`, `paths_digest` `sha256:03066532c95a20704758e9de3e153fce11f26bdea3dfbabb6fbefe2524b1437f`, and `policy_hash` `sha256:34fb63d7f29f8613cd4431382b1057398a4816f8a4c20fc34677fffc80a184f6`. Receipt evidence is the later 281-pass hash. Post-apply validate result is `allow`.

## Observation IDs (traceability)

| Artifact | Engram ID | Sync ID | Topic |
|----------|-----------|---------|-------|
| explore | #1063 | obs-c6e853b6ffec45fd | sdd/fase-7-ficha/explore |
| proposal | #1065 | obs-4a7274e5149fb588 | sdd/fase-7-ficha/proposal |
| spec | #1066 | obs-5a27c010fe2182bd | sdd/fase-7-ficha/spec |
| design | #1067 | obs-e468db047aa3329d | sdd/fase-7-ficha/design |
| tasks | #1068 | obs-f7982617009d2497 | sdd/fase-7-ficha/tasks |
| apply-progress | #1069 | obs-8ddc1ff63b3a3689 | sdd/fase-7-ficha/apply-progress |
| verify-report | #1070 | obs-ed96a5cb43e54c17 | sdd/fase-7-ficha/verify-report |
| review/transaction | not found | — | sdd/fase-7-ficha/review/transaction |
| review/ledger | not found | — | sdd/fase-7-ficha/review/ledger |
| review/receipt | not found in Engram | filesystem receipt only | sdd/fase-7-ficha/review/receipt |
| review/gate-context | not found | — | sdd/fase-7-ficha/review/gate-context |
| archive-report | #1071 | obs-5477a01c5af9bd13 | sdd/fase-7-ficha/archive-report |

Archive proceeded because orchestrator native status supplied `reviewGate.result: allow`, the native receipt and the change-local mirror are approved terminal receipts for lineage `review-bd24a3dd49888a5f`, and post-apply validate is `allow`. Engram review topics were never persisted. The frozen ledger lives in `.git/gentle-ai/review-transactions/v2/review-bd24a3dd49888a5f/review-state.json`.

## Out of scope (honored)

- No git commit
- No Fase 8 started
- Production code not edited
- `docs/documento-rector.md` not edited
- `docs/north-star.md` not edited
- Archived Fase 0, Fase 1, Fase 2, Fase 3, Fase 4, and Fase 6 not deleted

## Residual notes (non-blocking)

- Verify verdict is PASS: 0 CRITICAL. 8/8 requirements and 17/17 scenarios. The verify YAML still records the 280-pass capture. One sentence was added to `verify-report.md` before the move: a later chip fix for 2T26 and ValueError passed 281, evidence `sha256:8daaf6bb5d6256adf1276b174601a9f26ca877ec371e4e6d3313b7c8327779be`. Engram `#1070` remains the 280-pass observation.
- The two verify warnings (unknown token fallback, missing `2T26`) describe that 280 capture. The approved review evidence covers the later chip fix. They are not CRITICAL.
- Canonical `openspec/specs/gold-regression/spec.md` now carries the card exclusion that verify found only in the delta.
- `AGENTS.md` active change is none. This archive path is listed before the Fase 6, Fase 4, Fase 3, Fase 2, Fase 1, and Fase 0 archives.

## SDD Cycle Complete

The change has been fully planned, implemented, verified, reviewed (`allow`), and archived. Ready for a later `/sdd-new` if a new change is requested. Not starting a new change.
