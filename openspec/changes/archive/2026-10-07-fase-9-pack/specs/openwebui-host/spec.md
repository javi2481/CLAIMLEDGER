# Delta for Open WebUI Host

## MODIFIED Requirements

### Requirement: Measure Then Card

The host MUST sit outside `src/claimledger/http/` and off the 13-path allowlist. It MUST call `measure(artifact_hash, question)` then `render_card`. For a compare result it MAY call the difference function on that same `QueryResult` and pass the string to `render_card`; it MUST NOT calculate the number itself. `card_text` MUST stay first in the same assistant completion and MUST remain exactly that card: seal, chips, ordered rows, kernel values, the difference line only when the card set it, and a sentence the card already set. A page-crop PNG MAY follow that text in the same completion. The host MUST NOT parse digits or let an LLM choose `21262335`, `21259769`, or the difference. `POST /claims/query` MUST stay the only product route, with no added candidates and no `delta`.

(Previously: the card text had no difference line and the host never touched subtraction.)

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

One completion MUST start with exactly that one `card_text` from `render_card`, including seal `ME ABSTENGO` and a compare that shows both claims and, when code produced it, the line “Diferencia entre las dos cifras verificadas”. A page-crop picture MAY follow that text in the same assistant completion. A second message MUST NOT appear before or after the card.

(Previously: a compare card showed both claims and no delta.)

#### Scenario: Abstain is the reply

- GIVEN seal `ME ABSTENGO`
- WHEN the host completes
- THEN that abstain card text MUST be the whole body, with no picture, no difference line, and no invented verified value

#### Scenario: Compare shows the code difference

- GIVEN a stubbed reader and “Comparar resultado neto consolidado 1T26 vs 2T26”
- WHEN the host completes
- THEN card text MUST come first with `21262335`, `81956525`, and “Diferencia entre las dos cifras verificadas” followed by `60694190`
- AND one picture per verified claim MAY follow in claim order, in the same completion

### Requirement: Closed Bounds

`dependencies` MUST stay `[]`. The HTTP extra pin MUST stay `starlette==1.0.0`. The 13-path allowlist and empty `src/claimledger/__init__.py` MUST stay. Gold MUST stay `21262335` and `21259769`; `cp-*` expected values MUST stay the pairs. Kernel tests MUST NOT import `docling` and MUST NOT use Docker, network, or PDF. Host tests MUST stay in-process, with no bound port, Docker, network, or PDF. Charts and the orchestrator MUST wait. Phases 10–13 MUST NOT start. `http-query` and `gold-regression` MUST stay unchanged.

(Previously: subtraction waited, phases 9–13 MUST NOT start, and `claim-card` and `verify-eval` stayed unchanged.)

#### Scenario: Allowlist and kernel bans

- GIVEN kernel tests and `pyproject.toml`
- WHEN they run
- THEN `dependencies` MUST be `[]` and the allowlist MUST stay 13 paths
- AND kernel tests MUST NOT import `docling` or use Docker, network, or PDF

#### Scenario: Later phases wait

- GIVEN this change
- WHEN scope is checked
- THEN charts and the orchestrator MUST still wait, and phases 10–13 MUST NOT start
- AND `POST /claims/query` MUST NOT carry `delta`
