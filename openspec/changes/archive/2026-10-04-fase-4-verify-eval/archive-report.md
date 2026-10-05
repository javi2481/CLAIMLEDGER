# Archive Report: fase-4-verify-eval

**Change**: fase-4-verify-eval
**Archived to**: `openspec/changes/archive/2026-10-04-fase-4-verify-eval/`
**Date**: 2026-10-04
**Persistence**: hybrid
**Verdict**: archived and closed
**Git commit**: not created (explicit instruction)
**Review lineage**: `review-92dfe8609a7c9e79`
**Review gate**: allow

## Gates

| Gate | Result | Evidence |
|------|--------|----------|
| Native review receipt | allow / approved | Orchestrator `reviewGate.result: allow`; change-local `reviews/receipt.json` `terminal_state: approved`; native `.git/gentle-ai/review-transactions/v2/review-92dfe8609a7c9e79/review-receipt.json` `terminal_state: approved`; lineage `review-92dfe8609a7c9e79`; post-apply validate `allow`; `store_revision` `sha256:4b8312eed95e28b651ad49b55379f89bbb82d550d9c807856f29cd1ede832095`; `candidate_tree` `f74857b1091e42c04c59b93e8567ced1cf94ca1d`; `fix_delta` empty; `base_relationship_valid` true |
| Task completion | 4/4 `[x]` | Archived `tasks.md` and Engram `#1048` (1.1, 1.2, 2.1, 2.2). No unchecked implementation tasks. |
| Verify | PASS | Engram `#1050`; 0 CRITICAL; 9/9 requirements; 19/19 scenarios; `python -m pytest tests/` exit 0, 236 passed; evidence `sha256:efdf4f9255a7d2653ff49480f279f017301fb6a64a7d83cb3297eafaf01de669` |
| Destructive merge | none | One new full spec copied. One gold-regression requirement replaced. Frozen numeric contracts preserved. Rector and north-star untouched. Fase 0, Fase 1, Fase 2, and Fase 3 archives untouched. |

## Specs Synced

| Domain | Action | Details |
|--------|--------|---------|
| verify-eval | Created | 8 added, 0 modified, 0 removed. Full spec copied to `openspec/specs/verify-eval/spec.md` (Sibling Caller, Call Order, Neighbor Measure, Abstain Beside a Gold Number, Compare Without Subtraction, One Tables Drawer, Row Text Plus Identity, No Rank Metric) |
| gold-regression | Updated | 0 added, 1 modified, 0 removed. `Docling-Free Pytest Demo` replaced in full, including scenarios `Eval stays off the scan` and `Gold harness stays on seed`. Four other requirements preserved, including frozen numbers `21262335`, `21259769`, `81956525`, `81946993`, `60144176`, `70223471`, `36213283`, `-14950948`, `2566`, `122610546`, `143236114`, `114688061`, `-32731536`, `9532`, and prior `22362983` |

The delta `(Previously: scan excluded ingest, graph, and retrieval; gold stayed on Ledger.seed() with no Docling JSON ban on the v1/v2 harness.)` note was change commentary and was not copied into the main spec. Numeric gold was not relaxed. Gold v1 (45) and v2 (26) stay on `query(understand(question), Ledger.seed())` and MUST NOT point at Docling JSON or `llama_index`. `src/claimledger/eval/` and `tests/eval/` stay outside the 13-path scan.

Source of truth now includes:

- `openspec/specs/verify-eval/spec.md`
- `openspec/specs/gold-regression/spec.md`

## Archive Contents

- proposal.md ✅
- exploration.md ✅
- specs/{verify-eval,gold-regression}/spec.md ✅
- design.md ✅
- tasks.md ✅ (4/4 complete; no unchecked implementation tasks)
- verify-report.md ✅
- reviews/receipt.json ✅
- archive-report.md ✅ (this file)

Active path `openspec/changes/fase-4-verify-eval/` no longer exists.
`openspec/changes/archive/2026-10-04-fase-3-retrieval/` remains.
`openspec/changes/archive/2026-10-04-fase-2-graph-ingest/` remains.
`openspec/changes/archive/2026-10-04-fase-1-docling-adapter/` remains.
`openspec/changes/archive/2026-09-23-fase-0-kernel/` remains.

## Native Review Receipt

Filesystem mirror `reviews/receipt.json` matches `.git/gentle-ai/review-transactions/v2/review-92dfe8609a7c9e79/review-receipt.json`. Review-state `state` is `approved`. `store_revision` is `sha256:4b8312eed95e28b651ad49b55379f89bbb82d550d9c807856f29cd1ede832095`.

```json
{
  "schema": "gentle-ai.review-receipt/v2",
  "lineage_id": "review-92dfe8609a7c9e79",
  "generation": 1,
  "base_tree": "82a2f51dc3e3cfd1ecbf2ea1131722f0afd97391",
  "initial_review_tree": "f74857b1091e42c04c59b93e8567ced1cf94ca1d",
  "final_candidate_tree": "f74857b1091e42c04c59b93e8567ced1cf94ca1d",
  "paths_digest": "sha256:bda8ca2ea96cfbd43425a7e452f18307141a07103f0bb3de08720801ab0b471c",
  "fix_delta_hash": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "policy_hash": "sha256:34fb63d7f29f8613cd4431382b1057398a4816f8a4c20fc34677fffc80a184f6",
  "evidence_hash": "sha256:efdf4f9255a7d2653ff49480f279f017301fb6a64a7d83cb3297eafaf01de669",
  "risk_level": "high",
  "terminal_state": "approved"
}
```

`fix_delta_hash` is the empty-bytes digest. Base relationship is valid: `base_tree` `82a2f51dc3e3cfd1ecbf2ea1131722f0afd97391`. Initial and current snapshots share `candidate_tree` `f74857b1091e42c04c59b93e8567ced1cf94ca1d`, `paths_digest` `sha256:bda8ca2ea96cfbd43425a7e452f18307141a07103f0bb3de08720801ab0b471c`, and `policy_hash` `sha256:34fb63d7f29f8613cd4431382b1057398a4816f8a4c20fc34677fffc80a184f6`. Evidence matches the verify report. Post-apply validate result is `allow`.

## Observation IDs (traceability)

| Artifact | Engram ID | Sync ID | Topic |
|----------|-----------|---------|-------|
| explore | #1043 | obs-94bb4609e0465f82 | sdd/fase-4-verify-eval/explore |
| proposal | #1045 | obs-ce7307e3595340ee | sdd/fase-4-verify-eval/proposal |
| spec | #1046 | obs-931f9c90959bb778 | sdd/fase-4-verify-eval/spec |
| design | #1047 | obs-f413328db9881319 | sdd/fase-4-verify-eval/design |
| tasks | #1048 | obs-8821133b761e47ed | sdd/fase-4-verify-eval/tasks |
| apply-progress | #1049 | obs-6a6f8332cee17de6 | sdd/fase-4-verify-eval/apply-progress |
| verify-report | #1050 | obs-a82c8bc745fcdfac | sdd/fase-4-verify-eval/verify-report |
| review/transaction | not found | — | sdd/fase-4-verify-eval/review/transaction |
| review/ledger | not found | — | sdd/fase-4-verify-eval/review/ledger |
| review/receipt | not found in Engram | filesystem receipt only | sdd/fase-4-verify-eval/review/receipt |
| review/gate-context | not found | — | sdd/fase-4-verify-eval/review/gate-context |
| archive-report | #1051 | obs-b6609363abed98dc | sdd/fase-4-verify-eval/archive-report |

Archive proceeded because orchestrator native status supplied `reviewGate.result: allow`, the native receipt and the change-local mirror are approved terminal receipts for lineage `review-92dfe8609a7c9e79`, and post-apply validate is `allow`. Engram review topics were never persisted. The frozen ledger lives in `.git/gentle-ai/review-transactions/v2/review-92dfe8609a7c9e79/review-state.json`.

## Out of scope (honored)

- No git commit
- No Fase 6 started (`fase-6-http` not created)
- Production code not edited
- `docs/documento-rector.md` not edited
- `docs/north-star.md` not edited
- Archived Fase 0, Fase 1, Fase 2, and Fase 3 not deleted

## Residual notes (non-blocking)

- Verify verdict is PASS: 0 CRITICAL. 9/9 requirements and 19/19 scenarios. pytest 236 passed.
- Canonical `openspec/specs/gold-regression/spec.md` now carries the eval exclusion and the seed-only gold harness that verify found only in the delta.
- `AGENTS.md` active change is none. This archive path is listed before the Fase 3, Fase 2, Fase 1, and Fase 0 archives.

## SDD Cycle Complete

The change has been fully planned, implemented, verified, reviewed (`allow`), and archived. Ready for a later `/sdd-new` if a new change is requested. Not starting a new change.
