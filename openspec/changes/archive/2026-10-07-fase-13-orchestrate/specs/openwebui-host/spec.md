# Open WebUI Host Specification

## Purpose

The host draws the card. For the last four quarters it runs the fixed plan, then the phase 12 fence with holes. It does not calculate a missing quarter.

## Requirements

### Requirement: Compound Series After the Card

When `execute` returns a run, `reply` MUST render the card from that run’s verified claims, MUST NOT append the two-figure difference line, and MUST append `draw(series_spec(result, gaps))`. The fence MUST contain `bar [21262335, 81956525]`, `Hueco: 2025-09-30`, and `Hueco: 2025-12-31`. `60694190` MUST NOT appear in that completion. A one-claim reply and the 1T-vs-2T compare MUST stay on `measure`. `POST /claims/query` MUST NOT contain a Mermaid fence.

#### Scenario: Last four quarters

- GIVEN a stubbed reader and “Compará el resultado neto consolidado de los últimos 4 trimestres”
- WHEN the host completes
- THEN the body MUST start with the card
- AND the bar line MUST be `bar [21262335, 81956525]`
- AND both hole labels MUST appear
- AND `60694190` MUST NOT appear

### Requirement: Orchestrate Stays Off the Kernel

`src/claimledger/orchestrate/` MUST stay off the 13-path allowlist. Phases 10 and 11 MUST NOT start.

#### Scenario: Allowlist excludes orchestrate

- GIVEN `tests/test_identity.py`
- WHEN the allowlist is read
- THEN it MUST stay 13 paths
- AND no path MUST contain `orchestrate`
