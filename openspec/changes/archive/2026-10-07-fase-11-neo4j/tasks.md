# Tasks: Phase 11 Cypher Export of the Book

## Review Workload Forecast

Estimated changed lines for apply: under 400. One slice.

**Apply MUST NOT commit and MUST NOT open a PR unless the user asks.** Phase 10 stays unopened. No Neo4j driver. `dependencies` stays `[]`.

### Closed bounds

`query.py` behavior, `understand` behavior, `eval/measure.py`, `chart/series.py`, `digits.py`, `ledger.py`, `http/` payload shape, `card/card.py`, `pyproject.toml`, `tests/test_identity.py` (13 paths), gold. No new `QueryResult` field.

## Slice A

### Phase 1: Host guard

- [x] 1.1 RED: `test_wave_c_still_waits` asserts `"book"` in package names, keeps `crop`, `period`, `chart`, and `orchestrate`, stays disjoint from `{"charts"}`, allows active `fase-11-neo4j`, and rejects names starting with `fase-10`. Pytest MUST fail because `book` is not a package yet.

### Phase 2: Export and book tests (RED first)

- [x] 2.1 RED: `test_build_writes_graph_json_once_and_load_does_not_rebuild` expects `graph.cypher` beside `graph.json`, with `2026-03-31` and without `21262335`. The forbid test requires `CypherExporter` from `docling_graph.core.exporters.cypher_exporter` and still rejects `neo4j`, `FinancialClaim`, and `run_pipeline`.
- [x] 2.2 RED: `tests/book/test_ask.py`. Compare, last four quarters, and YPF return `None`. The book question records two `query` calls, `compare` false, values `21262335` then `81956525`. Parent values are `21259769` then `81946993`. `2026-09-30` is a gap. `60694190` is not a claim value.
- [x] 2.3 RED: AST — `book/` imports no `docling`, `docling_graph`, or `neo4j`. `query.py` and `graph/build.py` do not import `claimledger.book`.
- [x] 2.4 Run pytest. The book behavior tests MUST fail with `ModuleNotFoundError: claimledger.book`. The export assertions MUST fail because the script is not written.

### Phase 3: Export and book (GREEN)

- [x] 3.1 GREEN: `CypherExporter` call in `graph/build.py`. `src/claimledger/book/__init__.py` and `ask.py`.
- [x] 3.2 Store tests, book tests, and `test_wave_c_still_waits` MUST be green.

### Phase 4: Host (RED then GREEN)

- [x] 4.1 RED: with a script, the book reply contains `bar [21262335, 81956525]` and no `60694190`. Without a script the reply abstains and has no `81956525`. HTTP dump of that question is `abstained` and has no `mermaid`. Allowlist excludes `book`.
- [x] 4.2 GREEN: `reply` branches on `ask`.
- [x] 4.3 Full `pytest` green. No commit.
