# Tasks: Phase 12 Verified Series Chart

## Review Workload Forecast

Estimated changed lines for apply: ~280 (code ~90, tests ~190). SDD artifacts sit beside that. Risk against the 400-line review budget: Low. One slice.

Delivery strategy: one slice on the current branch.

Decision needed before apply: No
Chained PRs recommended: No
**Apply MUST NOT commit and MUST NOT open a PR unless the user asks.** Phases 10, 11, and 13 stay unopened. The orchestrator waits. matplotlib and Artifact wait.

### Closed bounds (apply MUST NOT touch)

`query.py` behavior, `eval/measure.py`, `digits.py`, `ledger.py` (14 `RECIPE_ROWS`), `http/` payload shape, `card/card.py`, `openwebui/text.py`, `openwebui/app.py`, `pyproject.toml` (`dependencies` stays `[]`), `tests/test_identity.py` (13 paths, no `chart`), gold and `cp-*` expected values, `evals/`. No `delta` or chart field on `QueryResult` or `POST /claims/query`. No orchestrator package.

## Slice A

### Phase 1: Host guard

- [x] 1.1 RED: `test_wave_c_still_waits` asserts `"chart"` in package names, keeps `"crop"` and `"period"`, stays disjoint from `{"charts", "orchestrator"}`, and rejects active names starting with `fase-10`, `fase-11`, or `fase-13`. `fase-12-chart` is allowed. Pytest MUST fail because `chart` is not a package yet.

### Phase 2: Series tests (RED first)

- [x] 2.1 RED: `tests/chart/test_series.py`. Compare seed → points `21262335`, `81956525`, labels `1T26`, `2T26`, status `verified`, identities copied. `60694190` is not a point value.
- [x] 2.2 RED: gap `2026-09-30` → partial, empty point labelled with that period, neighbors unchanged.
- [x] 2.3 RED: abstain, one claim, scope mismatch, conflicted claim → `None`.
- [x] 2.4 RED: `draw` bar line is `bar [21262335, 81956525]`; hole draw contains `Hueco: 2026-09-30` and that period is not a bar number; income-tax bars keep the minus signs and omit `-17780588`; `draw(None) == ""`.
- [x] 2.5 RED: AST — `chart/` imports no `docling`; `query.py` and `measure.py` do not import `claimledger.chart`; `QueryResult` fields stay four.
- [x] 2.6 Run `pytest tests/chart/test_series.py`. Behavior tests MUST fail with `ModuleNotFoundError: claimledger.chart`.

### Phase 3: Series (GREEN)

- [x] 3.1 GREEN: `src/claimledger/chart/__init__.py` and `series.py`.
- [x] 3.2 `pytest tests/chart/test_series.py tests/openwebui/test_host.py::test_wave_c_still_waits` MUST be green.

### Phase 4: Host (RED then GREEN)

- [x] 4.1 RED: compare reply equals card text plus the fence. Picture compare equals card, two pictures, then the fence. Consolidated and abstain replies contain no mermaid. HTTP compare dump contains no `mermaid` and no `60694190`. Allowlist excludes `chart`.
- [x] 4.2 GREEN: `reply` appends `draw(series_spec(result))` after pictures.
- [x] 4.3 Full `pytest` green. No commit.
