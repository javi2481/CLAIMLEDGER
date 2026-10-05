# Gold-Regression Specification

## Purpose

Freeze Claimprint identity gold as CLAIMLEDGER regression contracts. Numbers MUST NOT be relaxed. IDs MAY change only through aliases. Kernel tests MUST NOT import docling.

## Requirements

### Requirement: Frozen Numeric Contracts

The system MUST port `identity_v1` (45 cases) and `identity_v2` (26 cases). Numeric `expected_value(s)` MUST stay intact, including `21262335`, `21259769`, `81956525`, `81946993`, `60144176`, `70223471`, `36213283`, `-14950948`, `2566`, `122610546`, `143236114`, `114688061`, `-32731536`, `9532`. The suite MUST NOT reinterpret, round, or replace those figures.

#### Scenario: v1 identity case keeps the neighbor number

- GIVEN ported case `id-01`
- WHEN the gold file is read
- THEN `expected_value` MUST be `21262335`
- AND `expected_identity` MUST be the aliased 5-field key

#### Scenario: v2 tax keeps the minus sign

- GIVEN ported case `v2-id-04`
- WHEN the gold file is read
- THEN `expected_value` MUST be `-14950948`
- AND the harness MUST require that exact string

#### Scenario: Relaxing a gold number is forbidden

- GIVEN any v1 or v2 numeric expectation
- WHEN a test or port changes that number
- THEN the change MUST be treated as a contract failure
- AND the suite MUST NOT be marked green

### Requirement: Alias-Only Identity Rewrite

Ported cases MUST keep `id`, `partition`, `route`, `question`, `expected_value(s)`, `expected_period(s)`, `expected_source_page`, `expected_provenance`, `reject_values`, and `skip`. Only `expected_identity` MAY change, and only via `aliases.json`.

#### Scenario: Alias file is the rewrite table

- GIVEN original v1 `scope|metric` keys
- WHEN `evals/aliases.json` is tested
- THEN each key MUST map one-to-one to the Fase 0 English 5-field form

#### Scenario: Comparison wildcard identity

- GIVEN case `cp-01`
- WHEN it is ported
- THEN `expected_identity` MUST be `BYMA|*|income_statement|consolidated|net_income`
- AND `expected_values` MUST remain `["21262335", "81956525"]`

#### Scenario: Null identity ports as null

- GIVEN an abstention case with `expected_identity=null`
- WHEN it is ported
- THEN `expected_identity` MUST stay null
- AND `expected_value` MUST stay null

### Requirement: Partition Contracts

Identity and neighbor cases MUST verify exactly one `expected_value`. If `reject_values` exist, those numbers MUST NOT be the answer. Comparison cases MUST return two verified claims and MUST NOT subtract. Abstention cases MUST be `abstained` with no claim. Narrative cases `na-01`… MUST be ported with `"skip": true` and the layer-2 harness MUST NOT run them.

#### Scenario: Neighbor rejects prior and parent

- GIVEN case `nb-01` with `reject_values` `["21259769", "22362983"]`
- WHEN the harness runs
- THEN the verified value MUST be `21262335`
- AND neither rejected number MUST be chosen

#### Scenario: Comparison does not invent a delta

- GIVEN any `cp-*` or `v2-cp-*` case
- WHEN the harness runs
- THEN two verified claims MUST be returned
- AND no subtracted difference MUST be asserted

#### Scenario: Narrative stays skipped

- GIVEN `na-01` through `na-10`
- WHEN gold is ported
- THEN each case MUST have `"skip": true`
- AND the harness MUST NOT invent a number for “explicá el crecimiento”

### Requirement: Prior Figure Stays Non-Current

`22362983` MUST remain only a reject/prior figure. It MUST NOT be seeded as current `net_income` and MUST NOT become an `expected_value` for current-period net income.

#### Scenario: Prior appears only as reject

- GIVEN neighbor cases that list `22362983` in `reject_values`
- WHEN the seeded book and gold are checked
- THEN current 1T26 consolidated net income MUST be `21262335`
- AND `22362983` MUST NOT be the current value for that identity

### Requirement: Docling-Free Pytest Demo

The Docling-free scan MUST apply only to seven kernel modules `src/claimledger/*.py` (not `ingest/`, not `graph/`, not `retrieval/`, not `eval/`, not `http/`) and `tests/test_{identity,ledger,lookup,query,gold_v1,gold_v2}.py`. Those kernel modules, the six named kernel tests, and ingest MUST NOT import `llama_index`. Those kernel modules and tests MUST NOT import `docling` or `docling-graph`. `src/claimledger/ingest/` and `tests/ingest/` MAY import `docling==2.130.0` and MUST NOT import `docling-graph`. `src/claimledger/graph/` and `tests/graph/` MAY import `docling-graph==1.9.1`. `src/claimledger/retrieval/` and `tests/retrieval/` MAY import the retrieval library. `src/claimledger/eval/` and `tests/eval/` MUST stay outside the 13-path scan. `src/claimledger/http/` and `tests/http/` MUST stay outside the 13-path scan. Those kernel modules and the six named kernel tests MUST NOT import `starlette`. The seven-module import snapshot MUST NOT load `docling`, `docling-graph`, or `llama_index` as a result of importing the kernel. Pins `docling==2.130.0` and `docling-graph==1.9.1` MAY stay in `pyproject.toml`. Kernel gold MUST remain `Ledger.seed()`. Gold v1 (45 cases) and v2 (26 cases) MUST stay on `query(understand(question), Ledger.seed())` and MUST NOT be pointed at Docling JSON or `llama_index`. Frozen values, including `21262335`, `21259769`, and `-14950948`, MUST NOT be relaxed. Ingest tests MAY compare recipe rows to gold without replacing seed. Numeric gold MUST NOT be relaxed. Kernel suite: in-memory seeds only; no network, PDF, HTTP, or REPL. Green kernel `pytest` is the Fase 0 demo. `press_v1` and `presentation_v1` MUST NOT be ported. `src/claimledger/card/` and `tests/card/` MUST stay outside the 13-path scan, and kernel tests MUST NOT import the card if that would load a UI stack.

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

#### Scenario: Card stays off the scan

- GIVEN the 13-path scan
- WHEN `src/claimledger/card/` and `tests/card/` are present
- THEN both MUST stay outside it
- AND kernel tests MUST NOT import the card if that would load a UI stack
