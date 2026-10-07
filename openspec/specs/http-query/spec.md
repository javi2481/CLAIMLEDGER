# HTTP Query Specification

## Purpose

One route, `POST /claims/query`, in front of `understand` then `query` on `Ledger.seed()`. `query` stays the judge.

## Requirements

### Requirement: Sibling In-Process Route

The system MUST expose only `POST /claims/query` from `src/claimledger/http/`, outside the seven kernel modules. The app MUST run in-process. The only new pin MUST be `starlette==1.0.0`. FastAPI, Flask, and uvicorn MUST NOT be pinned. Tests MUST NOT bind a port. Kernel modules and the six kernel tests MUST NOT import `starlette`. `src/claimledger/http/` and `tests/http/` MUST stay off the 13-path allowlist. `src/claimledger/__init__.py` MUST stay empty.

#### Scenario: Pin is starlette 1.0.0 only

- GIVEN `pyproject.toml`
- WHEN dependencies are read
- THEN `starlette==1.0.0` MUST be pinned
- AND FastAPI, Flask, and uvicorn MUST NOT be pinned

#### Scenario: Tests do not bind a port

- GIVEN the route
- WHEN a test calls `POST /claims/query`
- THEN the call MUST stay in-process
- AND it MUST NOT bind a port

#### Scenario: Kernel and allowlist exclude HTTP

- GIVEN the seven kernel modules and the six kernel tests
- WHEN those modules are imported and the 13-path allowlist is read
- THEN they MUST NOT import `starlette`
- AND `src/claimledger/http/` and `tests/http/` MUST stay off that allowlist

### Requirement: Question Calls Understand Then Query

A JSON object with a string `question` MUST call `understand(question)` then `query` on the ledger from `recorded_book()`. The route MUST NOT call `Ledger.seed()`, `measure`, `retrieve`, or `upsert`.

#### Scenario: Body question only

- GIVEN body `{"question": "..."}`
- WHEN `POST /claims/query` runs
- THEN the order MUST be `recorded_book`, then `understand`, then `query` on that ledger
- AND `Ledger.seed()`, `measure`, `retrieve`, and `upsert` MUST NOT run on the route

### Requirement: Verified Rector JSON

A single verified claim MUST be HTTP 200. The body MUST contain `status`, `claim` (`issuer`, `period`, `statement`, `scope`, `metric`, `value`, `currency`), and `evidence`. It MUST NOT contain `answer`, `identity`, `identity_key`, `unit`, `ledger_status`, `artifact_hash`, `label`, or `bbox`. JSON `status` MUST be `QueryResult.status`. `claims_query` on `Ledger.seed()` MUST return `evidence` `[]`. The route MUST forward evidence from the book `recorded_book` returned.

#### Scenario: Consolidated net income

- GIVEN the quarterly book and “¿Cuál es el RESULTADO NETO DEL PERÍODO consolidado del 1T26?”
- WHEN the route runs
- THEN HTTP status MUST be 200, `status` MUST be `verified`, and `claim.value` MUST be `21262335`
- AND claim MUST be issuer `BYMA`, period `2026-03-31`, statement `income_statement`, scope `consolidated`, metric `net_income`, currency `ARS`
- AND `answer`, `identity`, `identity_key`, `unit`, `ledger_status`, `artifact_hash`, `label`, and `bbox` MUST be absent

#### Scenario: Parent is not consolidated

- GIVEN the quarterly book and a 1T26 resultado atribuible a la controlante question
- WHEN the route runs
- THEN `claim.value` MUST be `21259769`
- AND `21262335` MUST NOT be that value

#### Scenario: Income tax keeps the sign

- GIVEN the quarterly book and “impuesto a las ganancias consolidado 1T26”
- WHEN the route runs
- THEN `claim.value` MUST be `-14950948`

#### Scenario: Seed evidence is empty

- GIVEN `claims_query` on `Ledger.seed()`
- WHEN the JSON is read
- THEN `evidence` MUST be `[]`

#### Scenario: Route forwards book evidence

- GIVEN a book whose verified claim has evidence
- WHEN the route runs on that book
- THEN `evidence` MUST contain that `document_id`, `page`, and `text`
- AND `evidence` MUST NOT be `[]`

### Requirement: Abstain Reasons Pass Through

A kernel abstain MUST be HTTP 200 as `{"status": "abstained", "reason": "<kernel reason>"}` with no claim and no value. Reasons MUST stay in `off_corpus`, `recipe_no_extract`, `unresolved_identity`, `no_matching_claim`, `incomplete_comparison`, `ambiguous_period`. The route MUST NOT rewrite any of them to `no_verified_claim`.

#### Scenario: Recipe sources keep recipe_no_extract

- GIVEN a P&L question about memoria, comunicado, deck, or contrato
- WHEN the route runs
- THEN reason MUST be `recipe_no_extract`
- AND it MUST NOT be `no_verified_claim`

#### Scenario: Off corpus passes through

- GIVEN “¿Cuál fue el precio de cierre de YPF en BYMA el 3 de enero?”
- WHEN the route runs
- THEN reason MUST be `off_corpus`

#### Scenario: Closed set is unchanged

- GIVEN a kernel reason in that closed set
- WHEN the route returns abstained
- THEN `reason` MUST equal that kernel string

### Requirement: Compare Returns Two Claims

Compare on this route MUST be HTTP 200 with `claims` length 2, values `21262335` and `81956525`, and each item’s seed `evidence` `[]`. The body MUST NOT include `delta` or a subtracted number.

#### Scenario: Both quarters and no delta

- GIVEN “Comparar resultado neto consolidado 1T26 vs 2T26” on `Ledger.seed()`
- WHEN the route runs
- THEN `claims` length MUST be 2
- AND the values MUST be `21262335` and `81956525`
- AND no `delta` field and no subtracted number MUST be present

### Requirement: Bad Body Is Not a Kernel Abstain

A body that is not a JSON object with a string `question` MUST NOT call `understand` and MUST NOT be reported as a kernel abstain. Its HTTP status MUST be 400. A kernel `verified` or `abstained` result MUST be HTTP 200.

#### Scenario: Bad body skips the kernel

- GIVEN a non-object body, or an object whose `question` is missing or not a string
- WHEN the route runs
- THEN `understand` MUST NOT be called
- AND the response MUST NOT be a kernel abstain
- AND HTTP status MUST be 400

#### Scenario: Kernel results are HTTP 200

- GIVEN a kernel `verified` or `abstained` result
- WHEN the route returns it
- THEN HTTP status MUST be 200
