# Verify-Eval Specification

## Purpose

Sibling caller: tables candidates, then identity, then Claim Query on seed.

## Requirements

### Requirement: Sibling Caller

The caller MUST live in `src/claimledger/eval/` with tests in `tests/eval/`, outside the seven kernel modules and outside `retrieve`. It MUST NOT upsert, mark a candidate `verified`, or import `llama_index` into a kernel module. `retrieve` MUST NOT call `query`. Tests MUST NOT use a PDF, the network, or Docker.

#### Scenario: Outside kernel and retrieve

- GIVEN the seven kernel modules and `retrieve`
- WHEN the caller and `tests/eval/` load
- THEN both MUST stay outside them, and a kernel import MUST NOT load `llama_index`

#### Scenario: No upsert and no verified candidate

- GIVEN tables candidates and `Ledger.seed()`
- WHEN the caller runs
- THEN it MUST NOT upsert or mark a candidate `verified`, `retrieve` MUST NOT call `query`, and `ledger_status` MUST stay `recorded`

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

### Requirement: Neighbor Measure

Both neighbor row texts MUST be table candidates. Consolidated MUST verify `21262335`. Parent MUST verify `21259769`. The other number MUST NOT be the verified answer. `ledger_status` MUST stay `recorded`.

#### Scenario: Consolidated verifies 21262335

- GIVEN both neighbor texts as table candidates and `Ledger.seed()`
- WHEN the question is “¿Cuál es el RESULTADO NETO DEL PERÍODO consolidado del 1T26?”
- THEN both texts MUST be candidates, the verified value MUST be `21262335`, `21259769` MUST NOT be the answer, and `ledger_status` MUST stay `recorded`

#### Scenario: Parent verifies 21259769

- GIVEN the same candidates and `Ledger.seed()`
- WHEN the question asks resultado atribuible a la controlante 1T26
- THEN the verified value MUST be `21259769`, `21262335` MUST NOT be the answer, and `ledger_status` MUST stay `recorded`

### Requirement: Abstain Beside a Gold Number

A `recipe_no_extract` question about memoria, comunicado, deck, or contrato MUST abstain even when a tables candidate contains `21262335`.

#### Scenario: No-extract sources abstain beside 21262335

- GIVEN a tables candidate whose text contains `21262335`
- WHEN the question is a P&L ask about memoria, comunicado, deck, or contrato
- THEN status MUST be `abstained` with `recipe_no_extract`, and `21262335` MUST NOT be the verified answer

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

### Requirement: One Tables Drawer

This caller MUST use one drawer per call. The narrative drawer MUST NOT be a number source.

#### Scenario: Narrative is not a number source

- GIVEN tables nodes and narrative nodes
- WHEN the caller answers a number question
- THEN it MUST call `retrieve` once with `"tables"`, and a narrative node MUST NOT supply the number

### Requirement: Row Text Plus Identity

Selection MUST use row text plus identity, not `ref`. Both neighbors MAY share `#/tables/1`.

#### Scenario: Shared ref does not select

- GIVEN both neighbor texts share `ref` `#/tables/1`
- WHEN consolidated and parent questions run
- THEN both texts MUST stay candidates, and the verified value MUST follow identity (`21262335` or `21259769`), not `ref`

### Requirement: No Rank Metric

The caller MUST NOT compute Recall@k or MRR, add a ranker, or add a library.

#### Scenario: Both rows without a rank

- GIVEN both neighbor texts in the tables drawer
- WHEN the caller measures them
- THEN both texts MUST be present, with no Recall@k, MRR, rank score, or new library
