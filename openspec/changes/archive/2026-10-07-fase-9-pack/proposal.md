# Proposal: Phase 9 Period Pack and Compare Subtraction

## Intent

Rector §20: two verified claims side by side; code computes the difference. The pack half is built. Gap named by the 2026-10-06 audit: no pinned API subtracts two verified claims.

## Scope

### In Scope

- Sibling package outside the seven kernel modules (e.g. `src/claimledger/period/`). One function reads the `QueryResult` `query` produced.
- Returns a signed canonical digit string only when `status == "verified"`, exactly two claims, same issuer, statement, scope, metric, currency, unit, different periods, both `recorded`. Else nothing.
- Later period minus earlier period. `signed_ars` shape.
- Not a `FinancialClaim`. No `identity_key`. Never upserted. Never read by gold.
- `render_card` shows that string; it does not compute it. Labelled as the difference between two verified claims, never a standalone second quarter.
- Written note: pack is satisfied by `fold_documents`, `GraphMerger(conflicts="keep-all")`, `Ledger.upsert`, `extract_recipe`.
- In-memory tests on `Ledger.seed()`. No `docling`, network, PDF, Docker.

### Out of Scope

- `delta` on `QueryResult` or `POST /claims/query`. Second merger, corpus walker, non-EEFF recipe. 15th `RECIPE_ROWS` row. Widening `_METRIC_CHIP`.
- Phases 10–13, MinerU, Markdown SoT, LLM identity, kernel-skipping agent, relaxing gold, Pipelines, Knowledge RAG.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `claim-card`: Retire "MUST NOT subtract or show a delta". Card MUST NOT compute; MAY show what code computed.
- `openwebui-host`: Retire "Subtraction … MUST wait" and "no subtraction or delta added". One completion, card text then crop.
- `query`: Subtraction lives outside `query`. Still two claims, no delta field.
- `verify-eval`: `measure` does not subtract; subtraction lives outside it.

`gold-regression`, `http-query`, `document-graph`, `ledger`, `lookup` unchanged.

## Approach

Exploration approach 1. Arithmetic on two verified strings, gated on matching identity fields. `dependencies` stays `[]`.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| Subtraction package + tests | New | Guarded difference |
| `card/card.py` | Modified | Shows passed string |
| `openwebui/text.py` | Modified | Card order kept |
| `query.py`, `ledger.py`, `digits.py`, `graph/`, `ingest/`, `http/` | Unchanged | Four fields; 14 rows |
| `tests/test_query.py`, `evals/`, gold tests | Unchanged | 13 paths; `cp-03` pair |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Sign or order flip | Med | Later minus earlier; `-14950948` tests |
| Mismatched pair | Med | Refuse; no number |
| Cumulative 2T26 read as quarter | Med | Difference label only |
| Gold or allowlist drift | Low | Untouched |
| `gross_profit` card | Low | Not fixed here |

## Rollback Plan

Delete the package and tests. Revert card and host lines and four deltas. `query`, gold, ledger, graph untouched. No migration.

## Dependencies

- Archived phases 0–8.

## Success Criteria

- [ ] 1T26→2T26 consolidated net income yields `60694190` from the new function only.
- [ ] `query` returns two claims; `QueryResult` has four fields; `60694190` absent from query and gold.
- [ ] Mismatched or same-period pairs yield no number.
- [ ] `cp-*` pairs, `-14950948`, 13 paths, `dependencies` `[]` unchanged.

## Resolved product choices

1. Screen label: “Diferencia entre las dos cifras verificadas”. Same Spanish voice as the card sentence. It MUST NOT say “segundo trimestre” or “trimestre aislado”.
2. The difference reaches the screen in this phase. Rector §20: two verified claims side by side, and code computes the difference.
3. A positive result has no `+`. That is the `signed_ars` shape. Do not change `signed_ars`.
