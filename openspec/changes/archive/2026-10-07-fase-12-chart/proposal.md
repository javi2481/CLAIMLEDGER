# Proposal: Phase 12 Verified Series Chart

## Intent

Rector §21: each bar is a verified claim. The backend emits `title`, `points[]`, `status`. Open WebUI draws. A missing period stays empty. Nobody invents the next number so the chart looks full.

## Scope

### In Scope

- Sibling package `src/claimledger/chart/`, off the 13-path allowlist and off `http/`.
- `series_spec(result, gaps=())` reads a `QueryResult`. It returns a spec only for a verified series: two or more `recorded` claims, same issuer, statement, scope, metric, currency, and unit, distinct periods. Otherwise nothing.
- Each filled point copies `claim.value` and `identity_key`. A period listed in `gaps` and absent from the claims is a point with no value. No interpolation. The difference `60694190` is not a point.
- `draw(spec)` emits one Mermaid `xychart-beta` fence from those points, then each identity, then `Hueco:` lines for empty points. Axis ends are claim values, not a new figure.
- `reply` appends that fence after the card and after any page crops, only when a spec exists. A single claim and an abstention stay unchanged.
- In-memory tests. No `docling`, network, PDF, or Docker.

### Out of Scope

- matplotlib, Artifact, D3, pie charts, click-through boards.
- Orchestrator, fan-out, a fourth quarter in the ledger, a 15th `RECIPE_ROWS` row.
- `delta`, `points`, or `chart` on `QueryResult` or `POST /claims/query`.
- Phases 10, 11, and 13. MinerU. Markdown as source of truth. LLM-written identity. Relaxing gold.

## Capabilities

### New Capabilities

- `chart`: spec and Mermaid fence for a verified series.

### Modified Capabilities

- `openwebui-host`: a compare completion may append the fence after the card and pictures. The card text stays first. HTTP stays picture-free and chart-free.

## Approach

Same shape as `period/difference.py`: read the result `query` already produced. Do not change `query`. The host calls the new functions. The card does not.

## Affected Areas

| Area | Impact |
|------|--------|
| `src/claimledger/chart/` | New. Spec + fence |
| `src/claimledger/openwebui/reply.py` | Append fence when a series exists |
| `tests/chart/`, `tests/openwebui/test_host.py` | Series, holes, host order, allowlist |
| `query.py`, `http/`, gold, `card/` | Unchanged behavior |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| A hole rendered as `0` | Med | Empty points are `Hueco:` lines. They are absent from `bar []` |
| Chart number that is not a claim | Med | Fence digits in `bar` and axis ends are copied claim values. Tests forbid `60694190` |
| Kernel import of the chart package | Low | AST test. Allowlist stays 13 |

## Rollback Plan

Delete `src/claimledger/chart/` and `tests/chart/`. Revert `reply.py` and the host-test edits. The card and `POST /claims/query` never learned the chart.

## Dependencies

None. Open WebUI already renders Mermaid. No new pin.

## Success Criteria

- [x] Compare reply shows `21262335` and `81956525` as bar heights and does not show `60694190` in the fence
- [x] A listed missing period is `Hueco:` and is not a bar
- [x] Single-claim and abstain replies are unchanged
- [x] `POST /claims/query` has no chart and no `60694190`
- [x] `pytest` green. No `docling` import in `chart/`
