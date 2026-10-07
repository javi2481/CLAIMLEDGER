# Chart Specification

## Purpose

Turn a verified series into a chart spec and a Mermaid fence. Open WebUI draws that fence. This package does not verify, does not subtract, and does not invent a bar.

## Requirements

### Requirement: Series Spec Copies Claim Values

`series_spec` MUST live in `src/claimledger/chart/`, off the 13-path allowlist. It MUST accept a `QueryResult` and an optional tuple of gap periods. It MUST return a spec only when status is `verified`, there are at least two claims, every claim is `recorded`, and all claims share issuer, statement, scope, metric, currency, and unit, with distinct periods. Otherwise it MUST return nothing. Each filled point MUST copy that claim’s `value` and `identity_key`. Points MUST be ordered by period. The spec MUST NOT contain a subtracted amount. `60694190` MUST NOT be a point value of the consolidated net-income pair.

#### Scenario: Two verified quarters

- GIVEN `query` on `Ledger.seed()` for consolidated net income 1T26 vs 2T26
- WHEN `series_spec` reads that result
- THEN the points MUST be `21262335` then `81956525`
- AND labels MUST be `1T26` then `2T26`
- AND status MUST be `verified`
- AND `60694190` MUST NOT be a point value

#### Scenario: Not a series

- GIVEN an abstained result, a single verified claim, two claims that differ in scope or metric, or a claim that is not `recorded`
- WHEN `series_spec` reads it
- THEN it MUST return nothing

### Requirement: A Missing Period Is a Hole

A period passed in `gaps` that is not among the claims MUST become a point with no value, ordered with the others by period. That point MUST NOT receive an interpolated number, zero, or a copy of a neighbor. Status MUST be `partial` when any point has no value and at least one point has a value. The hole label for an unknown period MUST be the period string itself.

#### Scenario: Third quarter stays empty

- GIVEN the verified consolidated net-income pair and gap period `2026-09-30`
- WHEN `series_spec` reads them
- THEN one point MUST have no value and label `2026-09-30`
- AND the other two values MUST stay `21262335` and `81956525`
- AND status MUST be `partial`

### Requirement: Mermaid Fence Does Not Calculate

`draw` MUST emit one `xychart-beta` fence whose `bar` entries and y-axis ends are filled point values, then each filled identity, then a `Hueco:` line per empty point. Empty points MUST NOT appear in `bar`. `draw(None)` MUST return an empty string. The fence MUST NOT contain `60694190` for the net-income pair. Negative claim values MUST be copied with their sign. The package MUST NOT import `docling`. `query` and `measure` MUST NOT import `claimledger.chart`.

#### Scenario: Fence matches the pair

- GIVEN the spec for consolidated net income 1T26 and 2T26
- WHEN `draw` runs
- THEN the bar line MUST be `bar [21262335, 81956525]`
- AND both identity keys MUST follow the fence
- AND `60694190` MUST NOT appear

#### Scenario: Hole is named, not drawn

- GIVEN a partial spec whose empty point is labelled `2026-09-30`
- WHEN `draw` runs
- THEN the text MUST contain `Hueco: 2026-09-30`
- AND `bar` MUST NOT contain that period’s slot as a number
