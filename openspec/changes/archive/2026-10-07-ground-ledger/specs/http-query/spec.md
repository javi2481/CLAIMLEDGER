# Delta for HTTP Query

## MODIFIED Requirements

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
