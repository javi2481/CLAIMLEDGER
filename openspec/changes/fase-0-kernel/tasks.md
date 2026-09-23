# Tasks: Fase 0 Financial Claims kernel

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 1200–1900 authored (gold excluded) |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 → 8 |
| Delivery strategy | ask-on-risk |
| Chain strategy | pending |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: pending
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | Skeleton | PR 1 | `pytest tests/test_identity.py -k pins` | N/A pytest demo | `pyproject.toml`, empty package |
| 2 | Identity | PR 2 | `pytest tests/test_identity.py` | N/A in-memory | `identity.py`, `digits.py`, `aliases.json` |
| 3 | Claim | PR 3 | `pytest tests/test_identity.py` | N/A in-memory | `claim.py`, `evidence.py` |
| 4 | Ledger | PR 4 | `pytest tests/test_ledger.py` | N/A in-memory | `ledger.py` |
| 5 | Lookup | PR 5 | `pytest tests/test_lookup.py` | N/A in-memory | `lookup.py` |
| 6 | Query | PR 6 | `pytest tests/test_query.py` | N/A in-memory | `query.py` |
| 7 | Gold v1 | PR 7 | `pytest tests/test_gold_v1.py` | N/A seed | `identity_v1.json`, `test_gold_v1.py` |
| 8 | Gold v2 | PR 8 | `pytest tests/test_gold_v2.py` | N/A seed | `identity_v2.json`, `test_gold_v2.py` |

`feature-branch-chain`: PR1=tracker; PRn=PR n−1.

## Phase 1: Skeleton (commit 1)

- [x] 1.1 RED: `tests/test_identity.py` import 7 empty modules; pins unused; no `docling`.
- [x] 1.2 GREEN: `pyproject.toml` >=3.11, pytest, pin metadata + empty `src/claimledger/{__init__,identity,digits,evidence,claim,ledger,lookup,query}.py`.

## Phase 2: Identity + digits (commit 2)

- [x] 2.1 RED: `tests/test_identity.py` neighbor keys; fold+period; `digits_ars`/`signed_ars` fixtures; empty→None; aliases 1:1.
- [x] 2.2 GREEN: `identity.py` (`identity_key`, `fold`, period, alias) + `digits.py` + `evals/aliases.json` (7 rows).

## Phase 3: Claim + evidence (commit 3)

- [x] 3.1 RED: `tests/test_identity.py` consistent/inconsistent key; no `verification_status`; bad bbox; reject `21,26 M`.
- [x] 3.2 GREEN: `claim.py` + `evidence.py` frozen + `validate_*`; `ledger_status` only.

## Phase 4: Ledger upsert (commit 4)

- [x] 4.1 RED: `tests/test_ledger.py` recorded/append; other `22362983` conflicted both kept; 14-row seed; prior not current; ingest≠verified.
- [x] 4.2 GREEN: `ledger.py` thin `dict[str, FinancialClaim]`; no `store.py`; in-module seed.

## Phase 5: Lookup (commit 5)

- [x] 5.1 RED: `tests/test_lookup.py` fold; YPF `off_corpus`; recipe_no_extract sources; narrative; vs→compare; metric order; no `rejected`.
- [x] 5.2 GREEN: `lookup.py` `Intent`; 9-step order; issuer BYMA.

## Phase 6: Query (commit 6)

- [x] 6.1 RED: `tests/test_query.py` `21262335`/`21259769`; compare 2 claims no delta; closed abstentions; no mutate; no `rejected`.
- [x] 6.2 GREEN: `query.py` `QueryResult` `{verified,abstained}`; read-only `Ledger.get`.

## Phase 7: Gold v1 (commit 7)

- [ ] 7.1 RED: `tests/test_gold_v1.py` `id-01`=`21262335`; `nb-01` rejects; `cp-01` wildcard; `na-*` skip; no-docling scan.
- [ ] 7.2 GREEN: port `evals/identity_v1.json` (45); alias-only IDs; numbers frozen.

## Phase 8: Gold v2 (commit 8)

- [ ] 8.1 RED: `tests/test_gold_v2.py` `v2-id-04`=`-14950948`; `v2-cp-*` no delta; no press/deck gold.
- [ ] 8.2 GREEN: port `evals/identity_v2.json` (26); alias-only IDs.

Threat matrix N/A. Split Phase 5 if >400.
