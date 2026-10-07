# Delta for Open WebUI Host

## MODIFIED Requirements

### Requirement: Measure Then Card

The host MUST sit outside `src/claimledger/http/` and off the 13-path allowlist. It MUST call `recorded_book()` once per completion and pass that same ledger to `execute`, `ask`, and `measure`. It MUST NOT call `Ledger.seed()`. It MUST call `measure(artifact_hash, question, ledger)` then `render_card`. For a compare result it MAY call the difference function on that same `QueryResult` and pass the string to `render_card`; it MUST NOT calculate the number itself. `card_text` MUST stay first and remain exactly that card: seal, chips, ordered rows, kernel values, difference line only when the card set it, and any sentence the card set. A page-crop PNG MAY follow. When the result is a verified series, a Mermaid fence from `draw(series_spec(result))` MUST follow card/pictures. Last-four-quarters MUST go through `execute` (fence with holes; no two-figure difference line). Every net result of BYMA MUST go through `ask` when the script has periods (fence copies verified values; no two-figure difference line); without a script it MUST abstain. After card/pictures/fence, the host MAY append agent-host-gated prose when authorization exists, or MUST append the controlled abstention template when authorization is empty or the gate falls through. Host MUST enforce authorization via verified claims/`authorized_values`; prompt MUST NOT be enforcement. Host MUST NOT let an LLM authorize `21262335`, `21259769`, the difference, or a bar height. `POST /claims/query` MUST stay the only product route (no candidates, no `delta`, no fence). Host tests MAY stub `recorded_book`.
(Previously: card-only; host MUST NOT parse digits or let an LLM choose gold figures.)

#### Scenario: Consolidated value

- GIVEN stubbed reader, stubbed quarterly book, consolidated question
- WHEN host completes
- THEN seal, chips, both rows, and `21262335` MUST appear; `21259769` MUST NOT be the answer

#### Scenario: Parent value

- GIVEN stubbed reader, stubbed quarterly book, parent question
- WHEN host completes
- THEN `21259769` and both rows MUST appear

#### Scenario: Picture follows the card

- GIVEN a page-crop PNG is allowed
- WHEN host completes
- THEN `card_text` MUST be first and that PNG MUST follow in the same completion

#### Scenario: Compare completion draws the series

- GIVEN stubbed reader/book and “Comparar resultado neto consolidado 1T26 vs 2T26”
- WHEN host completes
- THEN card first; Mermaid `bar [21262335, 81956525]`; `60694190` on difference line only, not a bar height

#### Scenario: Single claim and abstain stay without fence

- GIVEN consolidated or abstaining question
- WHEN host completes
- THEN body MUST NOT contain a Mermaid fence

#### Scenario: Last four quarters

- GIVEN stubbed reader/book and “Compará el resultado neto consolidado de los últimos 4 trimestres”
- WHEN host completes
- THEN card first; `bar [21262335, 81956525]`; `Hueco: 2025-09-30` and `Hueco: 2025-12-31`; no `60694190`

#### Scenario: All net results

- GIVEN stubbed reader/book and script with both periods
- WHEN host completes “todos los resultados netos de BYMA”
- THEN card first; `bar [21262335, 81956525]`; no `60694190`

#### Scenario: HTTP stays one query

- GIVEN `POST /claims/query` and “todos los resultados netos de BYMA”
- WHEN route answers
- THEN status `abstained`; body MUST NOT contain `21262335` or a Mermaid fence

#### Scenario: Reply uses the quarterly book

- GIVEN `reply`
- WHEN source is read
- THEN it MUST call `recorded_book` once and MUST NOT call `Ledger.seed()`

#### Scenario: Card-first then gated prose or template

- GIVEN agent-host wiring
- WHEN host answers
- THEN `card_text` first; trailing text MUST be gated verified prose or the controlled abstention template

### Requirement: Always That Card

One completion MUST start with exactly one `card_text` from `render_card`, including seal `ME ABSTENGO` and compare cards with both claims and, when produced, “Diferencia entre las dos cifras verificadas”. A page-crop MAY follow. Host-gated verified prose or the controlled abstention template MAY follow after card/pictures/fence in the same completion. A second chat message MUST NOT appear before or after the card.
(Previously: abstain card was the whole body; no post-card text.)

#### Scenario: Abstain keeps card then template

- GIVEN seal `ME ABSTENGO` and empty authorization
- WHEN host completes
- THEN abstain card first; trailing text is only the controlled abstention template; no picture, difference line, invented value, or LLM financial prose

#### Scenario: Compare shows the code difference

- GIVEN stubbed reader and “Comparar resultado neto consolidado 1T26 vs 2T26”
- WHEN host completes
- THEN card first with `21262335`, `81956525`, and “Diferencia entre las dos cifras verificadas” + `60694190`; pictures MAY follow in claim order

### Requirement: Features Off

Host MUST expose `GET /v1/models` and `POST /v1/chat/completions`. Assistant content MUST be card first, then optional page-crop, then optional Mermaid fence, then gated prose or controlled abstention template, in one completion. Titles, follow-ups, Knowledge, Open WebUI tools, MCP, Pipelines, Ollama, and Action buttons MUST stay off. The CLAIMLEDGER agent loop MUST run inside the host, not as Open WebUI tools/Pipelines.
(Previously: content ended at card/picture/fence.)

#### Scenario: One card only

- GIVEN one question
- WHEN `POST /v1/chat/completions` runs
- THEN single card text first; optional picture/fence/gated-prose-or-template in same completion; no title, follow-up, Knowledge, Open WebUI tool, or MCP text

#### Scenario: Models lists no card

- GIVEN the host
- WHEN `GET /v1/models` runs
- THEN it answers and MUST NOT return a card

### Requirement: Closed Bounds

`dependencies` MUST stay `[]`. HTTP extra pin MUST stay `starlette==1.0.0`. Optional DeepSeek HTTP client extra MAY be pinned. 13-path allowlist and empty `src/claimledger/__init__.py` MUST stay. `chart/`, `orchestrate/`, `book/`, and `agent/` MUST stay off the allowlist. Gold MUST stay `21262335` and `21259769`; `cp-*` pairs unchanged. Kernel tests MUST NOT import `docling` or use Docker/network/PDF. Host/agent tests in-process, no bound port/Docker; DeepSeek mocked; search MAY be stubbed. `DEEPSEEK_API_KEY` MUST come from `.env` into claimledger only and MUST NEVER be committed. Phase 10 MUST NOT start. `http-query` and `gold-regression` unchanged.
(Previously: no `agent/`; no DeepSeek env/extra.)

#### Scenario: Allowlist and kernel bans

- GIVEN kernel tests and `pyproject.toml`
- WHEN they run
- THEN `dependencies` `[]`; allowlist 13 paths; no path contains `chart`, `orchestrate`, `book`, or `agent`; kernel tests ban docling/Docker/network/PDF

#### Scenario: Later phases wait

- GIVEN this change
- WHEN scope is checked
- THEN phase 10 MUST NOT start; `POST /claims/query` MUST NOT carry `delta`
