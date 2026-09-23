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

Kernel modules and tests MUST NOT import `docling` or `docling-graph`. Pins `docling==2.130.0` and `docling-graph==1.9.1` MAY be declared in `pyproject.toml` and MUST NOT be imported by Fase 0 tests. The suite MUST use in-memory seeds only: no network, no PDF, no HTTP, no REPL. Green `pytest` MUST be the Fase 0 demo artifact. `press_v1` and `presentation_v1` MUST NOT be ported in this change.

#### Scenario: Import scan stays clean

- GIVEN `src/claimledger` and `tests`
- WHEN the suite is collected or executed
- THEN no module MUST import `docling` or `docling-graph`

#### Scenario: Pins are declared metadata

- GIVEN `pyproject.toml`
- WHEN Fase 0 tests run
- THEN those pins MAY be listed as metadata
- AND test code MUST NOT import them

#### Scenario: Press and deck gold stay out

- GIVEN the Fase 0 evals tree
- WHEN the change is inspected
- THEN `press_v1` and `presentation_v1` MUST be absent
- AND comunicado/deck P&L questions in identity gold MUST stay `recipe_no_extract` abstentions
