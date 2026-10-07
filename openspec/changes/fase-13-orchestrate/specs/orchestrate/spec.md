# Orchestrate Specification

## Purpose

Run a fixed plan for one compound question. Each period is verified by `query`. The package does not retrieve a number from a model and does not import LlamaIndex.

## Requirements

### Requirement: Plan Only the Last Four Quarters

`execute` MUST live in `src/claimledger/orchestrate/`, off the 13-path allowlist. It MUST return nothing unless the folded question contains `ultimos` and `trimestre`, and the question contains `4` or the fold contains `cuatro`, and `understand` returns route `identity` with statement, scope, and metric set. “Comparar resultado neto consolidado 1T26 vs 2T26” MUST return nothing. An abstaining question MUST return nothing even if it also says “últimos 4 trimestres”.

#### Scenario: Compare of two named quarters is not a plan

- GIVEN “Comparar resultado neto consolidado 1T26 vs 2T26”
- WHEN `execute` runs on `Ledger.seed()`
- THEN it MUST return nothing

#### Scenario: Off-corpus stays off the plan

- GIVEN a question `understand` abstains, including “últimos 4 trimestres”
- WHEN `execute` runs
- THEN it MUST return nothing

### Requirement: One Kernel Call per Period

The window MUST be `2025-09-30`, `2025-12-31`, `2026-03-31`, `2026-06-30`, in that order. Each step MUST call `query` with `compare` false and that period, keeping issuer, statement, scope, and metric from `understand`. A verified step MUST contribute that one claim. Any other step MUST be a gap. Claims MUST stay in period order. Gap periods MUST be `2025-09-30` and `2025-12-31` for consolidated net income on `Ledger.seed()`. The claim values MUST be `21262335` and `81956525`. `60694190` MUST NOT be a claim value. The package MUST NOT import `docling` or `llama_index`. `query` and `measure` MUST NOT import `claimledger.orchestrate`.

#### Scenario: Two verified quarters and two holes

- GIVEN “Compará el resultado neto consolidado de los últimos 4 trimestres” and `Ledger.seed()`
- WHEN `execute` runs
- THEN four `query` calls MUST run, each with `compare` false
- AND the claim values MUST be `21262335` then `81956525`
- AND the gaps MUST be `2025-09-30` then `2025-12-31`
