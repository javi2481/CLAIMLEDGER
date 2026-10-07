# Proposal: Phase 11 Cypher Export of the Book

## Intent

Rector §20. The book already has two periods. A question for every net result of BYMA lists those periods from the Cypher script and verifies each one with `query`. The script does not hold the digits. No Neo4j server is started.

## Scope

### In Scope

- `build` writes `graph.cypher` beside `graph.json` by calling `CypherExporter` from `docling-graph==1.9.1`. Default style stays `merge`.
- The script names Document, Issuer, Period, and Statement. It MUST NOT contain `21262335` or `81956525`.
- Sibling package `src/claimledger/book/`, off the 13-path allowlist. `ask(question, ledger, script)` returns nothing unless the question asks for every net result (`todos` + `resultado` + `neto`) and is not the last-four-quarters plan, not YPF, and not a recipe abstention.
- Periods come from `n.period = "..."` in the script, sorted. Each step calls `query` with `compare` false. A period that does not verify is a gap. No new digit is written.
- `reply` uses `ask` only when the four-quarter plan returns nothing and the script has periods. `POST /claims/query` for that question stays abstained.
- The phase 2 ban on the name `CypherExporter` is lifted for that one import. A Neo4j driver, `run_pipeline`, and `FinancialClaim` stay banned inside `graph/`.

### Out of Scope

- A live Neo4j server, the Neo4j Python driver, Docker, and a new HTTP route.
- Changing `query` or `understand`. New gold numbers. Phase 10. An LLM writing Cypher or digits.

## Capabilities

### New Capabilities

- `book`: read periods from the exported script and verify each with `query`.

### Modified Capabilities

- `document-graph`: `build` also writes `graph.cypher`. Claim values stay out. A Neo4j driver stays absent.
- `openwebui-host`: the book question draws the verified series. The HTTP route stays abstained. Phase 10 stays unopened.

## Approach

`CypherExporter` already writes the script. Custom code is the call, plus reading period properties out of that script because the pin does not open a database. `query` remains the only source of a number.

## Affected Areas

| Area | Impact |
|------|--------|
| `src/claimledger/graph/build.py` | Call `CypherExporter` |
| `src/claimledger/book/` | New |
| `src/claimledger/openwebui/reply.py` | Branch when `ask` returns a run |
| `tests/graph/test_store.py`, `tests/book/`, `tests/openwebui/test_host.py` | Script, periods, host, allowlist |
| `query.py`, gold, `http/` payload shape | Unchanged behavior |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Claim digits land in the script | Low | The graph has no claim nodes. The store test forbids `21262335` in the script |
| “1T vs 2T” or the four-quarter question enters `ask` | Med | The cue requires `todos`. `execute` runs first. Existing reply tests stay exact |
| Kernel imports `docling` | Low | `book/` does not import it. Allowlist stays 13 |

## Rollback Plan

Delete `src/claimledger/book/` and `tests/book/`. Remove the `CypherExporter` call. Revert `reply.py` and the host-test edits. Restore the `CypherExporter` name ban.

## Dependencies

None. `dependencies` stays `[]`. No Neo4j driver extra.

## Success Criteria

- [x] `graph.cypher` is a `MERGE` script with `2026-03-31` and without `21262335`
- [x] “todos los resultados netos de BYMA” verifies `21262335` then `81956525` via two `query` calls
- [x] A period in the script that does not verify is a gap, not a new number
- [x] `POST /claims/query` for that question stays abstained and has no fence
- [x] `pytest` green
