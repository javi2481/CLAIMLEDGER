# Open WebUI Host Specification

## Purpose

Slim Open WebUI draws one existing card. The host calls `measure` then `render_card`. For a verified series it appends a Mermaid fence built from that result. For the last four quarters it runs the fixed plan, then that fence with holes. It does not calculate a bar height or a missing quarter.

## Requirements

### Requirement: Measure Then Card

The host MUST sit outside `src/claimledger/http/` and off the 13-path allowlist. It MUST call `measure(artifact_hash, question)` then `render_card`. For a compare result it MAY call the difference function on that same `QueryResult` and pass the string to `render_card`; it MUST NOT calculate the number itself. `card_text` MUST stay first in the same assistant completion and MUST remain exactly that card: seal, chips, ordered rows, kernel values, the difference line only when the card set it, and a sentence the card already set. A page-crop PNG MAY follow that text in the same completion. When the result is a verified series, a Mermaid fence from `draw(series_spec(result))` MUST follow the card and any pictures in that same completion. A last-four-quarters question MUST go through `execute` instead of one compare `query`: the fence MUST include the holes, and the two-figure difference line MUST stay off that completion. The host MUST NOT parse digits or let an LLM choose `21262335`, `21259769`, the difference, or a bar height. `POST /claims/query` MUST stay the only product route, with no added candidates, no `delta`, and no fence.

#### Scenario: Consolidated value

- GIVEN a stubbed reader and a consolidated question
- WHEN the host completes
- THEN seal, chips, both rows, and `21262335` MUST appear
- AND `21259769` MUST NOT be the answer

#### Scenario: Parent value

- GIVEN a stubbed reader and a parent question
- WHEN the host completes
- THEN `21259769` and both rows MUST appear

#### Scenario: Picture follows the card

- GIVEN a page-crop PNG is allowed
- WHEN the host completes
- THEN `card_text` MUST be first and that PNG MUST follow in the same completion

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

#### Scenario: Last four quarters

- GIVEN a stubbed reader and “Compará el resultado neto consolidado de los últimos 4 trimestres”
- WHEN the host completes
- THEN the body MUST start with the card
- AND the bar line MUST be `bar [21262335, 81956525]`
- AND the text MUST contain `Hueco: 2025-09-30` and `Hueco: 2025-12-31`
- AND `60694190` MUST NOT appear

### Requirement: Always That Card

One completion MUST start with exactly that one `card_text` from `render_card`, including seal `ME ABSTENGO` and a compare that shows both claims and, when code produced it, the line “Diferencia entre las dos cifras verificadas”. A page-crop picture MAY follow that text in the same assistant completion. A second message MUST NOT appear before or after the card.

#### Scenario: Abstain is the reply

- GIVEN seal `ME ABSTENGO`
- WHEN the host completes
- THEN that abstain card text MUST be the whole body, with no picture, no difference line, and no invented verified value

#### Scenario: Compare shows the code difference

- GIVEN a stubbed reader and “Comparar resultado neto consolidado 1T26 vs 2T26”
- WHEN the host completes
- THEN card text MUST come first with `21262335`, `81956525`, and “Diferencia entre las dos cifras verificadas” followed by `60694190`
- AND one picture per verified claim MAY follow in claim order, in the same completion

### Requirement: No Invented Rows

A missing or unreadable `artifact_hash` MUST NOT produce invented rows. A live verified card MUST require a configured hash. Pytest MUST stub the reader. Gitignored artifacts MUST NOT be committed.

#### Scenario: Unreadable hash

- GIVEN no readable `artifact_hash`
- WHEN a card is requested
- THEN no row text and no kernel value MUST be invented

#### Scenario: Stubbed reader

- GIVEN host tests
- WHEN pytest runs
- THEN the reader MUST be stubbed and gitignored artifacts MUST stay uncommitted

### Requirement: Features Off

The host MUST expose `GET /v1/models` and `POST /v1/chat/completions`. Assistant content MUST be the card text first, then a page-crop picture only when page-crop allows it, then a Mermaid fence only when a series spec exists, in that same completion. Titles, follow-ups, Knowledge, tools, MCP, Pipelines, Ollama, and Action buttons MUST stay off.

#### Scenario: One card only

- GIVEN one question
- WHEN `POST /v1/chat/completions` runs
- THEN assistant content MUST start with that single card text in one completion
- AND a picture MAY follow only in that same completion
- AND a Mermaid fence MAY follow only in that same completion
- AND no title, follow-up, Knowledge, tool, or MCP text MUST appear

#### Scenario: Models lists no card

- GIVEN the host
- WHEN `GET /v1/models` runs
- THEN it MUST answer and MUST NOT return a card

### Requirement: Slim Screen

The screen opened MUST be only `ghcr.io/open-webui/open-webui:v0.11.4-slim`. It MUST NOT be `latest` or `main`. `manual/ui.py` MAY remain and MUST NOT be that screen.

#### Scenario: Pinned slim image

- GIVEN compose
- WHEN the image is read
- THEN it MUST be `ghcr.io/open-webui/open-webui:v0.11.4-slim`

### Requirement: Closed Bounds

`dependencies` MUST stay `[]`. The HTTP extra pin MUST stay `starlette==1.0.0`. The 13-path allowlist and empty `src/claimledger/__init__.py` MUST stay. `src/claimledger/chart/` and `src/claimledger/orchestrate/` MUST stay off that allowlist. Gold MUST stay `21262335` and `21259769`; `cp-*` expected values MUST stay the pairs. Kernel tests MUST NOT import `docling` and MUST NOT use Docker, network, or PDF. Host tests MUST stay in-process, with no bound port, Docker, network, or PDF. Phases 10 and 11 MUST NOT start. `http-query` and `gold-regression` MUST stay unchanged.

#### Scenario: Allowlist and kernel bans

- GIVEN kernel tests and `pyproject.toml`
- WHEN they run
- THEN `dependencies` MUST be `[]` and the allowlist MUST stay 13 paths
- AND no allowlist path MUST contain `chart` or `orchestrate`
- AND kernel tests MUST NOT import `docling` or use Docker, network, or PDF

#### Scenario: Later phases wait

- GIVEN this change
- WHEN scope is checked
- THEN phases 10 and 11 MUST NOT start
- AND `POST /claims/query` MUST NOT carry `delta`
