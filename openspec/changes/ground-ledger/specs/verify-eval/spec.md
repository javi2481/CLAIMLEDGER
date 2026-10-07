# Delta for Verify-Eval

## MODIFIED Requirements

### Requirement: Call Order

A number question MUST call `retrieve(artifact_hash, "tables", question)`, then `understand(question)`, then `query` on the ledger the caller passed. When no ledger is passed, that ledger MUST be `recorded_book()`. The caller MUST NOT call `Ledger.seed()`. The question MUST NOT drop a row. Identity MUST come from `understand` and MUST NOT be parsed from candidate text. Tests that pass a ledger MUST NOT open a PDF.

#### Scenario: Retrieve, then understand, then query

- GIVEN an artifact hash, a number question, and an explicit ledger
- WHEN the caller runs
- THEN the order MUST be `retrieve(artifact_hash, "tables", question)`, then `understand(question)`, then `query` on that same ledger
- AND `Ledger.seed()` MUST NOT be called

#### Scenario: Omitted ledger is the quarterly book

- GIVEN an artifact hash and a number question, and no ledger argument
- WHEN the caller runs
- THEN `query` MUST receive the ledger from `recorded_book()`

#### Scenario: Question does not drop a row

- GIVEN both neighbor row texts in the tables drawer
- WHEN the question is consolidated, parent, or an empty string
- THEN both row texts MUST remain table candidates

#### Scenario: Identity is not parsed from candidate text

- GIVEN a tables candidate whose text contains `21262335`
- WHEN `understand` runs
- THEN identity MUST come from the question, and scope and metric MUST NOT be parsed from that text

### Requirement: Compare Without Subtraction

Compare MUST return two claims and `measure` MUST NOT subtract. The order MUST stay `retrieve`, then `understand`, then `query` on the ledger the caller passed. The difference MUST live outside `measure`, in the sibling difference function; `measure` MUST NOT call it. `measure` MUST NOT call `Ledger.seed()`.

#### Scenario: Compare stays two claims

- GIVEN `Ledger.seed()` passed as the ledger and “Comparar resultado neto consolidado 1T26 vs 2T26”
- WHEN the caller runs
- THEN verified claims MUST be `21262335` and `81956525`, and no subtracted difference MUST be returned
- AND `60694190` MUST NOT appear in what `measure` returns

#### Scenario: Measure does not call the difference

- GIVEN the caller module
- WHEN its imports and calls are read
- THEN it MUST NOT import or call the difference function, and tests that pass a ledger MUST NOT import `docling` or use network, PDF, or Docker
