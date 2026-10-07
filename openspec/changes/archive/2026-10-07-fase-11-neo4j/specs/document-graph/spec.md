# Document-Graph Specification

## Purpose

Ingest-time graph. The same build writes a Cypher script. The script is not a second book of claim values.

## Requirements

### Requirement: Cypher Script Beside the JSON

`build` MUST write `graph.cypher` in the same directory as `graph.json` by calling `CypherExporter` from `docling-graph==1.9.1`. A second build MUST leave only those two files. `load` MUST still read the JSON and MUST NOT rebuild. The script MUST name the period `2026-03-31` for the 1T fixture and MUST NOT contain `21262335` or `81956525`. `graph/` MUST NOT import a Neo4j driver, MUST NOT name `FinancialClaim`, and MUST NOT call `run_pipeline`.

#### Scenario: Script has the period and not the digits

- GIVEN one stored EEFF for 1T26
- WHEN `build` runs
- THEN `graph.cypher` MUST contain `2026-03-31`
- AND it MUST NOT contain `21262335`
- AND the directory MUST contain only `graph.json` and `graph.cypher`
