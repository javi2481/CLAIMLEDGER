# Delta for Open WebUI Host

## MODIFIED Requirements

### Requirement: Measure Then Card

The host MUST sit outside `src/claimledger/http/` and off the 13-path allowlist. It MUST call `measure(artifact_hash, question)` then `render_card`. `card_text` MUST stay first in the same assistant completion and MUST remain exactly that card: seal, chips, ordered rows, kernel values, and a sentence the card already set. A page-crop PNG MAY follow that text in the same completion. The host MUST NOT parse digits or let an LLM choose `21262335` or `21259769`. `POST /claims/query` MUST stay the only product route, with no added candidates.

(Previously: the body copied only the card and had no picture after it.)

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

### Requirement: Always That Card

One completion MUST start with exactly that one `card_text` from `render_card`, including seal `ME ABSTENGO` and a compare that shows both claims and no delta. A page-crop picture MAY follow that text in the same assistant completion. A second message MUST NOT appear before or after the card.

(Previously: the completion was exactly the card, with no following picture.)

#### Scenario: Abstain is the reply

- GIVEN seal `ME ABSTENGO`
- WHEN the host completes
- THEN that abstain card text MUST be the whole body, with no picture and no invented verified value

#### Scenario: Compare has no delta

- GIVEN a compare card with no delta
- WHEN the host completes
- THEN that card text MUST come first, with no subtraction or delta added
- AND one picture per verified claim MAY follow in claim order

### Requirement: Features Off

The host MUST expose `GET /v1/models` and `POST /v1/chat/completions`. Assistant content MUST be the card text first, then a page-crop picture only when page-crop allows it, in that same completion. Titles, follow-ups, Knowledge, tools, MCP, Pipelines, Ollama, and Action buttons MUST stay off.

(Previously: `POST /v1/chat/completions` was card-only, with no picture after the card text.)

#### Scenario: One card only

- GIVEN one question
- WHEN `POST /v1/chat/completions` runs
- THEN assistant content MUST start with that single card text in one completion
- AND a picture MAY follow only in that same completion
- AND no title, follow-up, Knowledge, tool, or MCP text MUST appear

#### Scenario: Models lists no card

- GIVEN the host
- WHEN `GET /v1/models` runs
- THEN it MUST answer and MUST NOT return a card

### Requirement: Closed Bounds

`dependencies` MUST stay `[]`. The HTTP extra pin MUST stay `starlette==1.0.0`. The 13-path allowlist and empty `src/claimledger/__init__.py` MUST stay. Gold MUST stay `21262335` and `21259769`. Kernel tests MUST NOT import `docling` and MUST NOT use Docker, network, or PDF. Host tests MUST stay in-process, with no bound port, Docker, network, or PDF. Subtraction, charts, and the orchestrator MUST wait. Phases 9–13 MUST NOT start. `claim-card`, `http-query`, `verify-eval`, and `gold-regression` MUST stay unchanged.

(Previously: crop waited with subtraction, charts, and the orchestrator, and Wave C MUST NOT start.)

#### Scenario: Allowlist and kernel bans

- GIVEN kernel tests and `pyproject.toml`
- WHEN they run
- THEN `dependencies` MUST be `[]` and the allowlist MUST stay 13 paths
- AND kernel tests MUST NOT import `docling` or use Docker, network, or PDF

#### Scenario: Wave C waits

- GIVEN this change
- WHEN scope is checked
- THEN subtraction, charts, and the orchestrator MUST still wait
- AND phases 9–13 MUST NOT start
