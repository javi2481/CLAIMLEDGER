# Archive Report: fase-0-kernel

**Change**: fase-0-kernel
**Archived to**: `openspec/changes/archive/2026-09-23-fase-0-kernel/`
**Date**: 2026-09-23
**Persistence**: hybrid
**Verdict**: archived and closed
**Git commit**: not created (explicit instruction)

## Gates

| Gate | Result | Evidence |
|------|--------|----------|
| Native review receipt | allow / approved | Orchestrator `reviewGate.result: allow`; `reviews/receipt.json` `terminal_state: approved`; lineage `review-ca68fa7a028e74e2`; post-apply validate `allow`; `blockedReasons: []` |
| Task completion | 16/16 `[x]` | Archived `tasks.md` and Engram `#1004`; apply-progress `#1009` |
| Verify | PASS | Engram `#1010`; 0 CRITICAL; 25/25 requirements; 63/63 scenarios; `pytest tests/` 128 passed |
| Destructive merge | none | Delta specs are full specs (no ADDED/MODIFIED/REMOVED/RENAMED). Main specs already identical. Rector and north-star untouched. |

## Specs Synced

Delta specs had no ADDED / MODIFIED / REMOVED / RENAMED sections. They were full capability specs written when `openspec/specs/` was empty and copied to main during `sdd-spec`. SHA-256 hashes matched before archive; no filesystem merge was required.

| Domain | Action | Details |
|--------|--------|---------|
| identity | Already identical | 5 requirements; hash `2D00A4AE1AC0…` |
| ledger | Already identical | 5 requirements; hash `150FCD59BDD0…` |
| lookup | Already identical | 5 requirements; hash `3FCFB9E99088…` |
| query | Already identical | 5 requirements; hash `F193C313D953…` |
| gold-regression | Already identical | 5 requirements; hash `016FA71E54F0…` |

Source of truth remains:

- `openspec/specs/identity/spec.md`
- `openspec/specs/ledger/spec.md`
- `openspec/specs/lookup/spec.md`
- `openspec/specs/query/spec.md`
- `openspec/specs/gold-regression/spec.md`

## Archive Contents

- proposal.md ✅
- exploration.md ✅
- specs/{identity,ledger,lookup,query,gold-regression}/spec.md ✅
- design.md ✅
- tasks.md ✅ (16/16 complete; no unchecked implementation tasks)
- verify-report.md ✅
- reviews/receipt.json ✅
- archive-report.md ✅ (this file)

Active path `openspec/changes/fase-0-kernel/` no longer exists.

## Native Review Receipt

```json
{
  "schema": "gentle-ai.review-receipt/v2",
  "lineage_id": "review-ca68fa7a028e74e2",
  "generation": 1,
  "base_tree": "903c2924188ab4c1471ea4bcbfa20b4334b042bf",
  "initial_review_tree": "2b823782677f5f92b89868b3d6f417077d6a1ff4",
  "final_candidate_tree": "2b823782677f5f92b89868b3d6f417077d6a1ff4",
  "paths_digest": "sha256:bf72429ba04496b4c1bec2671930db5c02bf367d029936f1b8a8f27379b1d433",
  "fix_delta_hash": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "policy_hash": "sha256:34fb63d7f29f8613cd4431382b1057398a4816f8a4c20fc34677fffc80a184f6",
  "evidence_hash": "sha256:59903fb2b2b0bd9f4183024f1053b492daeacf486bbe3f55b646a0da5cd29917",
  "risk_level": "high",
  "terminal_state": "approved"
}
```

## Observation IDs (traceability)

| Artifact | Engram ID | Sync ID | Topic |
|----------|-----------|---------|-------|
| explore | #1000 | obs-bca23acd006c4f18 | sdd/fase-0-kernel/explore |
| proposal | #1001 | obs-ebc55a588b06dada | sdd/fase-0-kernel/proposal |
| spec | #1002 | obs-b1b85da6d815431c | sdd/fase-0-kernel/spec |
| design | #1003 | obs-028f4cc0a0cc74aa | sdd/fase-0-kernel/design |
| tasks | #1004 | obs-5e89dd7e9d64569e | sdd/fase-0-kernel/tasks |
| apply-progress | #1009 | obs-bf404ae6d1192c9d | sdd/fase-0-kernel/apply-progress |
| verify-report | #1010 | obs-67507b618f9c4fdc | sdd/fase-0-kernel/verify-report |
| apply-complete | #1012 | obs-dc395fd95a28c7c0 | sdd/fase-0-kernel/apply-complete |
| review/transaction | not found | — | sdd/fase-0-kernel/review/transaction |
| review/ledger | not found | — | sdd/fase-0-kernel/review/ledger |
| review/receipt | not found in Engram | filesystem receipt only | sdd/fase-0-kernel/review/receipt |
| review/gate-context | not found | — | sdd/fase-0-kernel/review/gate-context |

Archive proceeded because orchestrator native status supplied `reviewGate.result: allow` and the filesystem receipt is an approved terminal receipt matching lineage `review-ca68fa7a028e74e2`. Engram review topics were never persisted.

## Out of scope (honored)

- No git commit
- No Fase 1 start
- Claimprint not edited
- Rector and north-star not edited

## Residual notes (non-blocking)

- `openspec/config.yaml` context still describes a docs-only repo; verify-report listed this as a suggestion only.
- On-disk `tasks.md` forecast header still shows `ask-on-risk` / `Chain strategy: pending`; Engram `#1004` records resolved `auto-chain` / `feature-branch-chain`. Does not affect task completeness.
- `AGENTS.md` still lists the active change as `openspec/changes/fase-0-kernel/` and was not edited.

## SDD Cycle Complete

The change has been fully planned, implemented, verified, reviewed (`allow`), and archived. Ready for a later `/sdd-new` if a new change is requested. Not starting Fase 1.
