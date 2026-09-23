# Proposal: Fase 0 deterministic Financial Claims kernel

## Intent

Portfolio kernel: identity / verify / abstain plus frozen gold. Prove "no verified claim → no answer" without Docling or agents.

## Scope

### In Scope
- 7-module skeleton + `pyproject.toml` (Python `>=3.11`, pytest; pins declared only)
- Frozen claim/evidence; 5-field `identity_key`; period + `digits_ars` / `signed_ars`
- In-memory `Ledger` upsert (same id+value appends evidence; other value → `conflicted`)
- Lookup → `Intent`; query → `verified` | `abstained` (compare = two claims)
- Port gold v1 (45) + v2 (26) + aliases; narrative `skip: true`
- In-memory tests: no network, PDF, or docling

### Out of Scope
- New layers/agents/HTTP/UI or later stack (Graph, Docker, VLM)
- Evidence Adapter, Docling parse, press/presentation gold, subtraction (Fase 9)
- Git/CodeGraph init; Claimprint `store.py`; rector §7 `verification_status`

## Capabilities

> `openspec/specs/` is empty.

### New Capabilities
- `identity`: 5-field key, aliases, period, digits, frozen models
- `ledger`: in-memory upsert; `recorded` | `conflicted`; query does not mutate
- `lookup`: fold + closed phrase order → `Intent`; no press/deck identity
- `query`: `Intent` + ledger → `verified` (1 or 2 claims) or `abstained`; neighbor via `reject_values`
- `gold-regression`: v1/v2 numeric contracts; IDs rewritten only via aliases

### Modified Capabilities
None

## Approach

Architecture CLOSED. Strict TDD, 8-commit order. Thin `Ledger` over `dict[identity_key, FinancialClaim]`. Frozen dataclasses + `validate_*`. `Intent` in `lookup.py`; query DTO in `query.py`. Seed 14 recipe rows; prior `22362983` is not current. Port Claimprint thesis/order, not `store.py`. Declare pins; never import in tests.

## Affected Areas

- `pyproject.toml` — package, pytest, declare pins
- `src/claimledger/{identity,digits,evidence,claim,ledger,lookup,query}.py` — exact skeleton
- `evals/{identity_v1,identity_v2,aliases}.json` — ported gold
- `tests/test_{identity,ledger,lookup,query,gold_v1,gold_v2}.py` — in-memory tests

## Risks

- Stamp `verified` on ingest (High) → query-only status; claim has `ledger_status`
- Port `store.py` or press/deck routes (Med) → in-memory `Ledger`; `recipe_no_extract`
- Gold rewrite mutates numbers (Med) → freeze values; aliases rewrite IDs
- Compare subtracts (Med) → two claims only; delta is Fase 9
- Pin import / oversized PR (High) → no docling in tests; slice by commit order

## Rollback Plan

Delete new package/tests/evals/`pyproject.toml` and this folder. Revert any commit that imports docling or adds a layer.

## Dependencies

- Claimprint (read, do not copy): thesis, money, gold, recipe
- Docs: `documento-rector.md`, `north-star.md`, `fase-0.md`
- pytest at implement time

## Success Criteria

- [ ] `pytest` green; suite never imports docling
- [ ] Inconsistent `identity_key` vs five fields errors at construct
- [ ] Neighbor `21262335` verified; `21259769` not chosen
- [ ] Same id, other value → `conflicted`; both evidences kept
- [ ] Ambiguous period with two book periods → `abstained`
- [ ] Gold intact; narrative skipped; pins declared; 8-commit order; no new layers
