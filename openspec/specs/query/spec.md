# Query Specification

## Purpose

Define how an `Intent` plus the in-memory ledger becomes `verified` (one or two claims) or `abstained`. Compare MUST return two claims and MUST NOT subtract until Fase 9. The Fase 0 demo artifact is pytest green; HTTP and REPL MUST NOT be required.

## Requirements

### Requirement: Verified Single Claim or No Answer

When Intent names one identity and the ledger has exactly one matching non-conflicted current claim, query MUST return `verified` and that one claim. If no unique demonstrable claim exists, query MUST return `abstained` and MUST NOT emit a value. No verified claim MUST mean no answer.

#### Scenario: Canonical consolidated net income

- GIVEN the recipe-seeded ledger
- WHEN the question is “¿Cuál es el RESULTADO NETO DEL PERÍODO consolidado del 1T26?”
- THEN status MUST be `verified`
- AND the claim value MUST be `21262335`
- AND identity MUST be `BYMA|2026-03-31|income_statement|consolidated|net_income`

#### Scenario: Missing claim abstains

- GIVEN a ledger that has no matching key for the Intent
- WHEN query runs
- THEN status MUST be `abstained`
- AND reason MUST be `no_matching_claim`
- AND no claim or value MUST be returned

### Requirement: Neighbor Is Not Chosen

When gold supplies `reject_values`, query MUST NOT return those numbers. For the canonical neighbor, consolidated MUST verify `21262335` and MUST NOT choose `21259769`. `rejected` MUST remain a store-side fact, not a query return.

#### Scenario: Consolidated neighbor trap

- GIVEN both `21262335` and `21259769` in the book
- WHEN a consolidated net-income 1T26 question is queried
- THEN the verified value MUST be `21262335`
- AND `21259769` MUST NOT be the answer

#### Scenario: Parent question chooses the neighbor

- GIVEN the same seeded book
- WHEN the question asks for resultado atribuible a la controlante 1T26
- THEN the verified value MUST be `21259769`
- AND `21262335` MUST NOT be the answer

### Requirement: Compare Returns Two Claims Without Delta

A compare Intent MUST return `verified` and two claims with the same scope/metric and different periods. The system MUST NOT compute or return a difference. Compare `expected_identity` MUST use `*` in period (example: `BYMA|*|income_statement|consolidated|gross_profit`). If only one period can be demonstrated, query MUST abstain with `incomplete_comparison`.

#### Scenario: Net income both quarters

- GIVEN recipe rows for 1T26 and 2T26 consolidated net income
- WHEN “Comparar resultado neto consolidado 1T26 vs 2T26” is queried
- THEN status MUST be `verified`
- AND the two values MUST be `21262335` and `81956525`
- AND no delta field or subtracted amount MUST be present

#### Scenario: Compare identity keeps wildcard period

- GIVEN a comparison case
- WHEN the result identities are checked
- THEN the gold identity MUST remain `BYMA|*|…`
- AND each returned claim MUST keep its own concrete period

#### Scenario: One-sided compare abstains

- GIVEN a compare Intent whose ledger has only one of the two periods
- WHEN query runs
- THEN status MUST be `abstained`
- AND reason MUST be `incomplete_comparison`

### Requirement: Closed Abstention

Abstention MUST return `abstained`, a closed reason, no claim, and no value. Reasons MUST be only `off_corpus`, `recipe_no_extract`, `no_matching_claim`, `incomplete_comparison`, `ambiguous_period`, `unresolved_identity`. An EEFF metric with no period token and two book periods MUST be `ambiguous_period`.

#### Scenario: YPF price abstains off corpus

- GIVEN “¿Cuál fue el precio de cierre de YPF en BYMA el 3 de enero?”
- WHEN query runs
- THEN status MUST be `abstained` with `off_corpus`
- AND no claim MUST be returned

#### Scenario: Comunicado P&L abstains as recipe no extract

- GIVEN “¿Cuál es el resultado neto consolidado del comunicado de prensa?”
- WHEN query runs
- THEN status MUST be `abstained` with `recipe_no_extract`

#### Scenario: Ambiguous period abstains

- GIVEN two book periods for consolidated net income and a question with no period token and no compare cue
- WHEN query runs
- THEN status MUST be `abstained` with `ambiguous_period`

### Requirement: Query Return Shape and Demo Surface

Query MUST return only `verified` or `abstained`. It MUST NOT return `rejected`. The Fase 0 demo artifact MUST be a green pytest run. HTTP, REPL, UI, and network MUST NOT be required to demonstrate the kernel.

#### Scenario: No rejected query status

- GIVEN a neighbor sitting unused in the ledger
- WHEN query answers the requested identity
- THEN status MUST be `verified` or `abstained`
- AND status MUST NOT be `rejected`

#### Scenario: Pytest is the demo

- GIVEN the Fase 0 kernel suite
- WHEN the demo is produced
- THEN `pytest` MUST be green
- AND no HTTP server or REPL session MUST be required
