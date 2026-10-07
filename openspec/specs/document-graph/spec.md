# Document-Graph Specification

## Purpose

Ingest-time graph. The same build writes a Cypher script. The script is not a second book of claim values.

## Requirements

### Requirement: Entities, Write Once, Import

Nodes MUST be only Document, Issuer, Period, and Statement. FinancialClaim, scope, metric, value, P&L extraction, `run_pipeline`, and a Neo4j driver MUST be absent. The graph MUST be written once as `graph.json`, and the same build MUST write `graph.cypher` with `CypherExporter`. The script MUST NOT contain a claim value. A question MUST NOT rebuild it. Only `src/claimledger/graph/` MAY import `docling-graph==1.9.1`.

#### Scenario: Closed pack

- GIVEN a period pack, one stored graph, and kernel, ingest, and graph imports
- WHEN it is built, a question is asked, and imports are checked
- THEN only those four types MUST exist, with no rebuild or P&L, and only the graph package MAY import `docling-graph==1.9.1`

#### Scenario: Script has the period and not the digits

- GIVEN one stored EEFF for 1T26
- WHEN `build` runs
- THEN `graph.cypher` MUST contain `2026-03-31`
- AND it MUST NOT contain `21262335`
- AND the directory MUST contain only `graph.json` and `graph.cypher`

### Requirement: IDs, Fold, Conflict

Issuer MUST be `BYMA`. Periods MUST be `2026-03-31` and `2026-06-30`. Statement MUST be `income_statement`. Document id MUST be the artifact hash. Same-period EEFF, comunicado, and deck MUST share those ids. Same id MUST fold. A clash MUST stay visible and MUST NOT set `ledger_status` to `conflicted`.

#### Scenario: Quarterly ids

- GIVEN EEFF, comunicado, and deck for 1T26 and 2T26
- WHEN the graph is built
- THEN periods MUST be `2026-03-31` for 1T26 and `2026-06-30` for 2T26, with shared `BYMA`, `income_statement`, and artifact-hash Document ids

#### Scenario: Clash

- GIVEN one id with two values for one attribute
- WHEN that id folds
- THEN both values MUST stay visible and `ledger_status` MUST NOT be `conflicted`

### Requirement: Classify, Doubt, Memoria, Transcript

Non-EEFF classify period MUST stay unset and MUST NOT be written back. Unknown alias or period MUST be recorded human doubt with no LLM. Year-end memoria MUST be a Document and MUST NOT fold into `2026-03-31` or `2026-06-30`. A transcript resolved to `2026-06-30` MAY link that Period and MUST NOT mint a claim.

#### Scenario: Edges

- GIVEN a comunicado with period unset, an unknown token, a year-end memoria, and a transcript for `2026-06-30`
- WHEN the graph is built
- THEN classify MUST stay unset, doubt MUST be recorded with no LLM, memoria MUST stay off both periods, and the transcript MAY link `2026-06-30` with no claim
