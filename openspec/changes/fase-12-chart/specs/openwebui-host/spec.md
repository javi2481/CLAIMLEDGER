# Open WebUI Host Specification

## Purpose

Slim Open WebUI draws one existing card. The host calls `measure` then `render_card`. For a verified series it appends a Mermaid fence built from that result. It does not calculate bar heights.

## Requirements

### Requirement: Series Fence After the Card

The host MUST append `draw(series_spec(result))` after `card_text` and after any page-crop pictures, in the same completion, only when the spec exists. `card_text` MUST stay first. A single verified claim and an abstention MUST NOT gain a fence. The fence MUST show `21262335` and `81956525` for the consolidated compare and MUST NOT show `60694190` inside the fence. `POST /claims/query` MUST stay the only product route and MUST NOT carry the fence, `delta`, or `60694190`.

#### Scenario: Compare completion draws the series

- GIVEN a stubbed reader and “Comparar resultado neto consolidado 1T26 vs 2T26”
- WHEN the host completes
- THEN card text MUST come first
- AND the Mermaid bar MUST be `bar [21262335, 81956525]`
- AND `60694190` MUST remain on the card difference line and MUST NOT be a bar height

#### Scenario: Single claim and abstain stay card-only

- GIVEN a consolidated question or an abstaining question
- WHEN the host completes
- THEN the body MUST NOT contain a Mermaid fence

### Requirement: Chart Stays Off the Kernel

`src/claimledger/chart/` MUST stay off the 13-path allowlist. Kernel tests MUST NOT import `docling`. Phases 10, 11, and 13 MUST NOT start. The orchestrator package MUST NOT exist.

#### Scenario: Allowlist excludes chart

- GIVEN `tests/test_identity.py`
- WHEN the allowlist is read
- THEN it MUST stay 13 paths
- AND no path MUST contain `chart`
