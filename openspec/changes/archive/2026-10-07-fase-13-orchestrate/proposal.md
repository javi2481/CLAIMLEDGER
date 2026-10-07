# Proposal: Phase 13 Fixed Plan Around the Kernel

## Intent

Rector §22. A compound question gets one fixed plan. Each period passes through the same `query`. Verified claims become the series. A period the book does not have stays a hole. No agent writes a number.

## Scope

### In Scope

- Sibling package `src/claimledger/orchestrate/`, off the 13-path allowlist and off `http/`.
- `execute(question, ledger)` returns nothing unless the folded question asks for the last four quarters (`ultimos` + `trimestre` + `4` or `cuatro`) and `understand` returns an identity route.
- The window is four calendar quarter-ends ending at `2026-06-30`: `2025-09-30`, `2025-12-31`, `2026-03-31`, `2026-06-30`.
- Each step copies issuer, statement, scope, and metric from that Intent, sets `compare=False` and that period, and calls `query`. Verified single claims are kept in period order. Any other outcome is a gap period.
- `reply` uses this only when `execute` returns a run. The card lists the verified claims and does not print the two-figure difference. The phase 12 fence receives the gap periods. One-claim and 1T-vs-2T replies stay on `measure`.
- In-memory tests. No `docling`, no `llama_index`, no network, no PDF, no Docker.

### Out of Scope

- LLM plan, analysis agent, chart-type agent, threads, a second route, `delta` or chart fields on `QueryResult`.
- Changing `understand` or `query`. New recipe rows. Phases 10 and 11. matplotlib. Artifact.

## Capabilities

### New Capabilities

- `orchestrate`: fixed four-quarter plan and per-period kernel calls.

### Modified Capabilities

- `openwebui-host`: a last-four-quarters question appends the partial fence. The 1T vs 2T compare stays the difference line and a fence with no holes.

## Approach

`understand` confirms the identity. The plan only supplies periods. `query` confirms each one. `series_spec` already knows how to leave a hole.

## Affected Areas

| Area | Impact |
|------|--------|
| `src/claimledger/orchestrate/` | New |
| `src/claimledger/openwebui/reply.py` | Branch when a run exists |
| `tests/orchestrate/`, `tests/openwebui/test_host.py` | Plan, kernel calls, host fence, allowlist |
| `query.py`, `http/`, gold, `chart/series.py` | Unchanged behavior |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Compare of 1T vs 2T starts going through the plan | Med | The cue is `ultimos` + a count of four. Existing reply tests stay exact |
| A hole rendered as a value | Low | Gaps are period strings passed to `series_spec`. No new digits |
| Kernel import | Low | AST test. Allowlist stays 13 |

## Rollback Plan

Delete `src/claimledger/orchestrate/` and `tests/orchestrate/`. Revert `reply.py` and the host-test edits.

## Dependencies

None. `dependencies` stays `[]`.

## Success Criteria

- [x] Last four quarters verify `21262335` and `81956525` and name holes `2025-09-30` and `2025-12-31`
- [x] Each step calls `query` with `compare=False`
- [x] “1T26 vs 2T26” does not enter the plan and still shows `60694190` on the card
- [x] The four-quarter reply does not show `60694190`
- [x] `POST /claims/query` gains no fence
- [x] `pytest` green
