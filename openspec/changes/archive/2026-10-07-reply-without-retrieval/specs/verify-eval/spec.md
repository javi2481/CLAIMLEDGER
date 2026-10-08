# Delta for Verify-Eval

## MODIFIED Requirements

### Requirement: Call Order

`measure(question, ledger)` MUST call `understand(question)`, then `query` on the ledger the caller passed. The ledger argument MUST be required. `measure` MUST NOT take `artifact_hash`, call `retrieve`, call `recorded_book()`, or call `Ledger.seed()`. Candidates MUST be built only after `query`, from verified claim evidence. Identity MUST come from `understand` and MUST NOT be parsed from candidate text. Tests that pass a ledger MUST NOT open a PDF or import `docling`.

(Previously: `retrieve(artifact_hash, "tables", question)` then `understand` then `query`; omitted ledger loaded `recorded_book()`.)

#### Scenario: Understand, then query

- GIVEN a number question and an explicit ledger
- WHEN `measure` runs
- THEN the order MUST be `understand(question)`, then `query` on that same ledger
- AND it MUST NOT call `retrieve`, `recorded_book()`, or `Ledger.seed()`

#### Scenario: Ledger is required

- GIVEN `measure`
- WHEN its signature is read
- THEN it MUST be `measure(question, ledger)` and MUST NOT accept `artifact_hash`

#### Scenario: Verified evidence is not dropped

- GIVEN a verified claim with two evidence items
- WHEN the question verifies that claim
- THEN both items MUST remain table candidates, and no extra neighbor MUST be invented

#### Scenario: Abstain yields no candidates

- GIVEN a question that abstains
- WHEN `measure` runs
- THEN candidates MUST be `()`

#### Scenario: Identity is not parsed from candidate text

- GIVEN a tables candidate whose text contains `21262335`
- WHEN `understand` runs
- THEN identity MUST come from the question, and scope and metric MUST NOT be parsed from that text

### Requirement: Neighbor Measure

Verified values MUST stay frozen. Consolidated MUST verify `21262335`. Parent MUST verify `21259769`. The other number MUST NOT be the verified answer. `ledger_status` MUST stay `recorded`. Candidates MUST be one `tables` row per verified evidence item: text MUST be `evidence.text` when non-empty, otherwise `evidence.label`; ref MUST be `evidence.artifact_hash`. `Ledger.seed()` evidence is empty, so those candidates MUST be `()`. Neighbor retrieval rows MUST NOT be required.

(Previously: both neighbor row texts had to be table candidates.)

#### Scenario: Consolidated verifies 21262335

- GIVEN `Ledger.seed()` and “¿Cuál es el RESULTADO NETO DEL PERÍODO consolidado del 1T26?”
- WHEN `measure` runs
- THEN the verified value MUST be `21262335`, candidates MUST be `()`, `21259769` MUST NOT be the answer, and `ledger_status` MUST stay `recorded`

#### Scenario: Parent verifies 21259769

- GIVEN `Ledger.seed()` and a resultado atribuible a la controlante 1T26 question
- WHEN `measure` runs
- THEN the verified value MUST be `21259769`, candidates MUST be `()`, `21262335` MUST NOT be the answer, and `ledger_status` MUST stay `recorded`

#### Scenario: Evidence becomes tables candidates

- GIVEN a verified claim whose evidence text is `21.262.335`
- WHEN `measure` runs
- THEN one candidate MUST use drawer `tables`, that text, and that item's `artifact_hash`

#### Scenario: Blank text uses the label

- GIVEN verified evidence with empty text and label `RESULTADO NETO DEL PERÍODO`
- WHEN candidates are built
- THEN text MUST be that label

### Requirement: Compare Without Subtraction

Compare MUST return two claims and `measure` MUST NOT subtract. The order MUST stay `understand`, then `query` on the ledger the caller passed. `measure` MUST NOT call `retrieve`. The difference MUST live outside `measure`; `measure` MUST NOT call it. `measure` MUST NOT call `Ledger.seed()`.

(Previously: order was `retrieve`, then `understand`, then `query`.)

#### Scenario: Compare stays two claims

- GIVEN `Ledger.seed()` and “Comparar resultado neto consolidado 1T26 vs 2T26”
- WHEN `measure` runs
- THEN verified claims MUST be `21262335` and `81956525`, and no subtracted difference MUST be returned
- AND `60694190` MUST NOT appear in what `measure` returns
- AND `retrieve` MUST NOT be called

#### Scenario: Measure does not call the difference

- GIVEN the caller module
- WHEN its imports and calls are read
- THEN it MUST NOT import or call the difference function, and tests that pass a ledger MUST NOT import `docling` or use network, PDF, or Docker

### Requirement: One Tables Drawer

Evidence candidates MUST use drawer `tables` only. The caller MUST NOT call `retrieve`. The narrative drawer MUST NOT be a number source.

(Previously: the caller had to call `retrieve` once with `"tables"`.)

#### Scenario: Narrative is not a number source

- GIVEN narrative nodes and a number question
- WHEN the caller runs
- THEN it MUST NOT call `retrieve`, every candidate MUST use drawer `tables`, and a narrative node MUST NOT supply the number

### Requirement: Row Text Plus Identity

Selection MUST use identity, not `ref`. Evidence items MAY share one `artifact_hash`. The verified value MUST NOT be chosen from `ref`.

(Previously: both neighbor texts could share `#/tables/1` and both had to stay candidates.)

#### Scenario: Shared ref does not select

- GIVEN two evidence items that share one `artifact_hash`
- WHEN consolidated and parent questions run
- THEN the verified value MUST follow identity (`21262335` or `21259769`), not `ref`

### Requirement: No Rank Metric

The caller MUST NOT compute Recall@k or MRR, add a ranker, or add a library. Evidence candidates MUST appear without a rank score.

(Previously: both neighbor texts had to be present with no rank.)

#### Scenario: Evidence rows without a rank

- GIVEN verified evidence texts
- WHEN the caller measures them
- THEN those texts MUST be candidates, with no Recall@k, MRR, rank score, or new library
