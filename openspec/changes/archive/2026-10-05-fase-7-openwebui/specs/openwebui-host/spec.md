# Open WebUI Host Specification

## Purpose

Slim Open WebUI draws one existing card. The host calls `measure` then `render_card`.

## Requirements

### Requirement: Measure Then Card

The host MUST sit outside `src/claimledger/http/` and off the 13-path allowlist. It MUST call `measure(artifact_hash, question)` then `render_card`. The body MUST copy only that card: seal, chips, ordered rows, kernel values, and a sentence the card already set. It MUST NOT parse digits or let an LLM choose `21262335` or `21259769`. `POST /claims/query` MUST stay the only product route, with no added candidates.

#### Scenario: Consolidated value

- GIVEN a stubbed reader and a consolidated question
- WHEN the host completes
- THEN seal, chips, both rows, and `21262335` MUST appear
- AND `21259769` MUST NOT be the answer

#### Scenario: Parent value

- GIVEN a stubbed reader and a parent question
- WHEN the host completes
- THEN `21259769` and both rows MUST appear

### Requirement: Always That Card

One completion MUST be exactly that one `render_card`, including seal `ME ABSTENGO` and a compare that shows both claims and no delta. A second message MUST NOT appear before or after the card.

#### Scenario: Abstain is the reply

- GIVEN seal `ME ABSTENGO`
- WHEN the host completes
- THEN that abstain card MUST be the whole body, with no invented verified value

#### Scenario: Compare has no delta

- GIVEN a compare card with no delta
- WHEN the host completes
- THEN that card MUST be the body, with no subtraction or delta added

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

The host MUST expose `GET /v1/models` and card-only `POST /v1/chat/completions`. Titles, follow-ups, Knowledge, tools, MCP, Pipelines, Ollama, and Action buttons MUST stay off.

#### Scenario: One card only

- GIVEN one question
- WHEN `POST /v1/chat/completions` runs
- THEN assistant content MUST be that single card
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

`dependencies` MUST stay `[]`. The HTTP extra pin MUST stay `starlette==1.0.0`. The 13-path allowlist and empty `src/claimledger/__init__.py` MUST stay. Gold MUST stay `21262335` and `21259769`. Kernel tests MUST NOT import `docling` and MUST NOT use Docker, network, or PDF. Host tests MUST stay in-process, with no bound port, Docker, network, or PDF. Crop, subtraction, charts, and the orchestrator MUST wait. Wave C MUST NOT start. `claim-card`, `http-query`, `verify-eval`, and `gold-regression` MUST stay unchanged.

#### Scenario: Allowlist and kernel bans

- GIVEN kernel tests and `pyproject.toml`
- WHEN they run
- THEN `dependencies` MUST be `[]` and the allowlist MUST stay 13 paths
- AND kernel tests MUST NOT import `docling` or use Docker, network, or PDF

#### Scenario: Wave C waits

- GIVEN this change
- WHEN scope is checked
- THEN crop, subtraction, charts, and the orchestrator MUST still wait
