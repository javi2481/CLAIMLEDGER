# Archive Report: fase-6-http

**Change**: fase-6-http
**Archived to**: `openspec/changes/archive/2026-10-04-fase-6-http/`
**Date**: 2026-10-04
**Persistence**: hybrid
**Verdict**: archived and closed
**Git commit**: not created (explicit instruction)
**Review lineage**: `review-0f10b11351e1ba2b`
**Review gate**: allow

## Gates

| Gate | Result | Evidence |
|------|--------|----------|
| Native review receipt | allow / approved | Orchestrator `reviewGate.result: allow`; change-local `reviews/receipt.json` `terminal_state: approved`; native `.git/gentle-ai/review-transactions/v2/review-0f10b11351e1ba2b/review-receipt.json` `terminal_state: approved`; lineage `review-0f10b11351e1ba2b`; post-apply validate `allow`; `store_revision` `sha256:13fc81d3a140b34e0cbbc2825f669601b9e3c9d73b5dc7f2826970887da355e8`; `candidate_tree` `1bb1f45e705309ddde420b6e757822a9b4efea7d`; `fix_delta` empty; `base_relationship_valid` true |
| Task completion | 4/4 `[x]` | Archived `tasks.md` and Engram `#1058` (1.1, 1.2, 2.1, 2.2). No unchecked implementation tasks. |
| Verify | PASS | Engram `#1060`; 0 CRITICAL; 7/7 requirements; 22/22 scenarios; `python -m pytest tests/` exit 0, 271 passed; evidence `sha256:5d9e2ee3f9a3b714c4336863d4431e591d9c5c38e1293e516527518d5e44726c` |
| Destructive merge | none | One new full spec copied. One gold-regression requirement replaced. Frozen numeric contracts preserved. Rector and north-star untouched. Fase 0, Fase 1, Fase 2, Fase 3, and Fase 4 archives untouched. |

## Specs Synced

| Domain | Action | Details |
|--------|--------|---------|
| http-query | Created | 6 added, 0 modified, 0 removed. Full spec copied to `openspec/specs/http-query/spec.md` (Sibling In-Process Route, Question Calls Understand Then Query, Verified Rector JSON, Abstain Reasons Pass Through, Compare Returns Two Claims, Bad Body Is Not a Kernel Abstain) |
| gold-regression | Updated | 0 added, 1 modified, 0 removed. `Docling-Free Pytest Demo` replaced in full, including scenario `HTTP stays off the scan`. Four other requirements preserved, including frozen numbers `21262335`, `21259769`, `81956525`, `81946993`, `60144176`, `70223471`, `36213283`, `-14950948`, `2566`, `122610546`, `143236114`, `114688061`, `-32731536`, `9532`, and prior `22362983` |

The delta `(Previously: the 13-path scan excluded eval and did not ban starlette on kernel modules or the six kernel tests.)` note was change commentary and was not copied into the main spec. Numeric gold was not relaxed. `src/claimledger/http/` and `tests/http/` stay outside the 13-path scan. Kernel modules and the six kernel tests MUST NOT import `starlette`.

Source of truth now includes:

- `openspec/specs/http-query/spec.md`
- `openspec/specs/gold-regression/spec.md`

## Archive Contents

- proposal.md ✅
- exploration.md ✅
- specs/{http-query,gold-regression}/spec.md ✅
- design.md ✅
- tasks.md ✅ (4/4 complete; no unchecked implementation tasks)
- verify-report.md ✅
- reviews/receipt.json ✅
- archive-report.md ✅ (this file)

Active path `openspec/changes/fase-6-http/` no longer exists.
`openspec/changes/archive/2026-10-04-fase-4-verify-eval/` remains.
`openspec/changes/archive/2026-10-04-fase-3-retrieval/` remains.
`openspec/changes/archive/2026-10-04-fase-2-graph-ingest/` remains.
`openspec/changes/archive/2026-10-04-fase-1-docling-adapter/` remains.
`openspec/changes/archive/2026-09-23-fase-0-kernel/` remains.

## Native Review Receipt

Filesystem mirror `reviews/receipt.json` matches `.git/gentle-ai/review-transactions/v2/review-0f10b11351e1ba2b/review-receipt.json`. Review-state `state` is `approved`. `store_revision` is `sha256:13fc81d3a140b34e0cbbc2825f669601b9e3c9d73b5dc7f2826970887da355e8`.

```json
{
  "schema": "gentle-ai.review-receipt/v2",
  "lineage_id": "review-0f10b11351e1ba2b",
  "generation": 1,
  "base_tree": "82a2f51dc3e3cfd1ecbf2ea1131722f0afd97391",
  "initial_review_tree": "1bb1f45e705309ddde420b6e757822a9b4efea7d",
  "final_candidate_tree": "1bb1f45e705309ddde420b6e757822a9b4efea7d",
  "paths_digest": "sha256:7e296509808ee42aac1431b9db2dcfe4289016d990b9dd422106708dbae1bcfb",
  "fix_delta_hash": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "policy_hash": "sha256:34fb63d7f29f8613cd4431382b1057398a4816f8a4c20fc34677fffc80a184f6",
  "evidence_hash": "sha256:5d9e2ee3f9a3b714c4336863d4431e591d9c5c38e1293e516527518d5e44726c",
  "risk_level": "high",
  "terminal_state": "approved"
}
```

`fix_delta_hash` is the empty-bytes digest. Base relationship is valid: `base_tree` `82a2f51dc3e3cfd1ecbf2ea1131722f0afd97391`. Initial and current snapshots share `candidate_tree` `1bb1f45e705309ddde420b6e757822a9b4efea7d`, `paths_digest` `sha256:7e296509808ee42aac1431b9db2dcfe4289016d990b9dd422106708dbae1bcfb`, and `policy_hash` `sha256:34fb63d7f29f8613cd4431382b1057398a4816f8a4c20fc34677fffc80a184f6`. Evidence matches the verify report. Post-apply validate result is `allow`.

## Observation IDs (traceability)

| Artifact | Engram ID | Sync ID | Topic |
|----------|-----------|---------|-------|
| explore | #1053 | obs-e6af0c8e33f447db | sdd/fase-6-http/explore |
| proposal | #1055 | obs-b3978e5d8709a6e5 | sdd/fase-6-http/proposal |
| spec | #1056 | obs-c52ee30350453976 | sdd/fase-6-http/spec |
| design | #1057 | obs-2046a561daca60a0 | sdd/fase-6-http/design |
| tasks | #1058 | obs-6f095e660592bef9 | sdd/fase-6-http/tasks |
| apply-progress | #1059 | obs-9b61fb882c93da01 | sdd/fase-6-http/apply-progress |
| verify-report | #1060 | obs-0478f0ce79e4c061 | sdd/fase-6-http/verify-report |
| review/transaction | not found | — | sdd/fase-6-http/review/transaction |
| review/ledger | not found | — | sdd/fase-6-http/review/ledger |
| review/receipt | not found in Engram | filesystem receipt only | sdd/fase-6-http/review/receipt |
| review/gate-context | not found | — | sdd/fase-6-http/review/gate-context |
| archive-report | #1061 | obs-68943bb646064f3a | sdd/fase-6-http/archive-report |

Archive proceeded because orchestrator native status supplied `reviewGate.result: allow`, the native receipt and the change-local mirror are approved terminal receipts for lineage `review-0f10b11351e1ba2b`, and post-apply validate is `allow`. Engram review topics were never persisted. The frozen ledger lives in `.git/gentle-ai/review-transactions/v2/review-0f10b11351e1ba2b/review-state.json`.

## Out of scope (honored)

- No git commit
- No Fase 7 started (`fase-7-ficha` not created)
- Production code not edited
- `docs/documento-rector.md` not edited
- `docs/north-star.md` not edited
- Archived Fase 0, Fase 1, Fase 2, Fase 3, and Fase 4 not deleted

## Residual notes (non-blocking)

- Verify verdict is PASS: 0 CRITICAL. 7/7 requirements and 22/22 scenarios. pytest 271 passed.
- Canonical `openspec/specs/gold-regression/spec.md` now carries the HTTP exclusion and the kernel `starlette` ban that verify found only in the delta.
- `AGENTS.md` active change is none. This archive path is listed before the Fase 4, Fase 3, Fase 2, Fase 1, and Fase 0 archives.

## SDD Cycle Complete

The change has been fully planned, implemented, verified, reviewed (`allow`), and archived. Ready for a later `/sdd-new` if a new change is requested. Not starting a new change.
