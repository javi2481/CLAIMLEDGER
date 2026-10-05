# Delta for Gold Regression

## MODIFIED Requirements

### Requirement: Docling-Free Pytest Demo

The Docling-free scan MUST apply only to seven kernel modules `src/claimledger/*.py` (not `ingest/`, not `graph/`, not `retrieval/`, not `eval/`, not `http/`) and `tests/test_{identity,ledger,lookup,query,gold_v1,gold_v2}.py`. Those kernel modules, the six named kernel tests, and ingest MUST NOT import `llama_index`. Those kernel modules and tests MUST NOT import `docling` or `docling-graph`. `src/claimledger/ingest/` and `tests/ingest/` MAY import `docling==2.130.0` and MUST NOT import `docling-graph`. `src/claimledger/graph/` and `tests/graph/` MAY import `docling-graph==1.9.1`. `src/claimledger/retrieval/` and `tests/retrieval/` MAY import the retrieval library. `src/claimledger/eval/` and `tests/eval/` MUST stay outside the 13-path scan. `src/claimledger/http/` and `tests/http/` MUST stay outside the 13-path scan. Those kernel modules and the six named kernel tests MUST NOT import `starlette`. The seven-module import snapshot MUST NOT load `docling`, `docling-graph`, or `llama_index` as a result of importing the kernel. Pins `docling==2.130.0` and `docling-graph==1.9.1` MAY stay in `pyproject.toml`. Kernel gold MUST remain `Ledger.seed()`. Gold v1 (45 cases) and v2 (26 cases) MUST stay on `query(understand(question), Ledger.seed())` and MUST NOT be pointed at Docling JSON or `llama_index`. Frozen values, including `21262335`, `21259769`, and `-14950948`, MUST NOT be relaxed. Ingest tests MAY compare recipe rows to gold without replacing seed. Numeric gold MUST NOT be relaxed. Kernel suite: in-memory seeds only; no network, PDF, HTTP, or REPL. Green kernel `pytest` is the Fase 0 demo. `press_v1` and `presentation_v1` MUST NOT be ported.

(Previously: the 13-path scan excluded eval and did not ban `starlette` on kernel modules or the six kernel tests.)

#### Scenario: Import scan stays clean

- GIVEN the seven kernel modules and the six named kernel tests
- WHEN those modules are imported
- THEN those and ingest MUST NOT import `llama_index`, and those modules MUST NOT import `docling` or `docling-graph`
- AND ingest, graph, and retrieval paths MUST stay outside that scan

#### Scenario: Pins are declared metadata

- GIVEN `pyproject.toml`
- WHEN kernel tests run
- THEN pins MAY be metadata; kernel tests MUST NOT import them; ingest MAY import `docling==2.130.0` and MUST NOT import `docling-graph`
- AND `src/claimledger/graph/` and `tests/graph/` MAY import `docling-graph==1.9.1`

#### Scenario: Press and deck gold stay out

- GIVEN the Fase 0 evals tree
- WHEN the change is inspected
- THEN `press_v1` and `presentation_v1` MUST be absent, and comunicado/deck P&L questions MUST stay `recipe_no_extract`

#### Scenario: Kernel absence ignores a later graph load

- GIVEN the seven kernel modules imported without `docling` or `docling-graph`
- WHEN `tests/graph/` later loads `docling-graph==1.9.1`
- THEN that load MUST NOT fail the kernel check

#### Scenario: Retrieval off the snapshot

- GIVEN a kernel import snapshot with no `llama_index`
- WHEN retrieval imports the retrieval library
- THEN that import MAY succeed with no LlamaIndex version named
- AND the snapshot MUST still show no `llama_index`

#### Scenario: Eval stays off the scan

- GIVEN the 13-path scan
- WHEN `src/claimledger/eval/` and `tests/eval/` are present
- THEN both MUST stay outside it, and a kernel module MUST NOT import `llama_index`

#### Scenario: Gold harness stays on seed

- GIVEN gold v1 (45) and v2 (26), including `21262335`, `21259769`, and `-14950948`
- WHEN the gold harness runs
- THEN each case MUST call `query(understand(question), Ledger.seed())` and MUST NOT read Docling JSON or import `llama_index`

#### Scenario: HTTP stays off the scan

- GIVEN the 13-path scan
- WHEN `src/claimledger/http/` and `tests/http/` are present
- THEN both MUST stay outside it
- AND the seven kernel modules and the six kernel tests MUST NOT import `starlette`
