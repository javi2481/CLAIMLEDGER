# Book Specification

## Purpose

Answer “todos los resultados netos de BYMA” from the exported Cypher script and the kernel. The script names periods. `query` supplies each number.

## Requirements

### Requirement: Periods Come From the Script

`ask` MUST live in `src/claimledger/book/`, off the 13-path allowlist. It MUST return nothing unless the folded question contains `todos`, `resultado`, and `neto`. It MUST return nothing for YPF, for a recipe abstention, for “Comparar resultado neto consolidado 1T26 vs 2T26”, and for the last-four-quarters question. Periods MUST be read from `n.period = "..."` lines, with duplicates dropped, and MUST be sorted. The package MUST NOT import `docling`, `docling_graph`, or `neo4j`.

#### Scenario: Not a book question

- GIVEN the 1T vs 2T compare, the last-four-quarters question, or a YPF price question
- WHEN `ask` runs
- THEN it MUST return nothing

#### Scenario: Periods are ordered

- GIVEN a script that sets `n.period` to `2026-06-30` and `2026-03-31`
- WHEN the periods are read
- THEN the order MUST be `2026-03-31` then `2026-06-30`

### Requirement: One Kernel Call per Period

Each period MUST call `query` with `compare` false, keeping issuer, statement, scope, and metric. For “todos los resultados netos de BYMA” on `Ledger.seed()` the values MUST be `21262335` then `81956525`. `60694190` MUST NOT be a claim value. A period that does not verify MUST be a gap and MUST NOT become `0` or a copied neighbor. “todos los resultados netos de la controlante” MUST use the parent values `21259769` then `81946993`. `query` and `graph/build.py` MUST NOT import `claimledger.book`.

#### Scenario: Two verified quarters

- GIVEN “todos los resultados netos de BYMA”, `Ledger.seed()`, and a script with `2026-03-31` and `2026-06-30`
- WHEN `ask` runs
- THEN two `query` calls MUST run, each with `compare` false
- AND the claim values MUST be `21262335` then `81956525`
- AND `60694190` MUST NOT be a claim value

#### Scenario: Missing period is a gap

- GIVEN the same question and a script that also sets `n.period` to `2026-09-30`
- WHEN `ask` runs
- THEN `2026-09-30` MUST be a gap
- AND the claim values MUST stay `21262335` and `81956525`
