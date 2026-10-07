# Tasks: Phase 13 Fixed Plan Around the Kernel

## Review Workload Forecast

Estimated changed lines for apply: ~320 (code ~110, tests ~210). One slice. Under the 400-line review budget.

**Apply MUST NOT commit and MUST NOT open a PR unless the user asks.** Phases 10 and 11 stay unopened. No LlamaIndex workflow pin. `dependencies` stays `[]`.

### Closed bounds

`query.py` behavior, `understand` behavior, `eval/measure.py`, `chart/series.py`, `digits.py`, `ledger.py`, `http/` payload shape, `card/card.py`, `pyproject.toml`, `tests/test_identity.py` (13 paths), gold. No new `QueryResult` field.

## Slice A

### Phase 1: Host guard

- [x] 1.1 RED: `test_wave_c_still_waits` asserts `"orchestrate"` in package names, keeps `crop`, `period`, and `chart`, stays disjoint from `{"charts"}`, and rejects active names starting with `fase-10` or `fase-11`. `fase-13-orchestrate` is allowed. Pytest MUST fail because `orchestrate` is not a package yet.

### Phase 2: Plan tests (RED first)

- [x] 2.1 RED: `tests/orchestrate/test_plan.py`. Compare question and an abstaining “últimos 4 trimestres” question return `None`.
- [x] 2.2 RED: the compound question records four `query` calls, `compare` false, periods in window order, values `21262335` then `81956525`, gaps `2025-09-30` then `2025-12-31`. `60694190` is not a claim value.
- [x] 2.3 RED: AST — `orchestrate/` imports no `docling` or `llama_index`. `query.py`, `measure.py`, `card.py`, and `http/claims.py` do not import `claimledger.orchestrate`.
- [x] 2.4 Run pytest. Behavior tests MUST fail with `ModuleNotFoundError: claimledger.orchestrate`.

### Phase 3: Plan (GREEN)

- [x] 3.1 GREEN: `src/claimledger/orchestrate/__init__.py` and `plan.py`.
- [x] 3.2 Chart tests, plan tests, and `test_wave_c_still_waits` MUST be green.

### Phase 4: Host (RED then GREEN)

- [x] 4.1 RED: compound reply contains `bar [21262335, 81956525]`, both `Hueco:` lines, and no `60694190`. HTTP dump of that question contains no `mermaid`. Allowlist excludes `orchestrate`.
- [x] 4.2 GREEN: `reply` branches on `execute`.
- [x] 4.3 Full `pytest` green. No commit.
