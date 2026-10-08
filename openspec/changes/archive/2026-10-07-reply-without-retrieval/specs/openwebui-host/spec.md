# Delta for OpenWebUI-Host

## ADDED Requirements

### Requirement: Product Image Without Retrieval Extra

The product image MUST install `.[http,deepseek]` and MUST NOT install the `retrieval` extra. That extra MAY stay declared for optional offline RAG and its tests. `dependencies` MUST stay `[]`.

#### Scenario: Image extras

- GIVEN the product Dockerfile
- WHEN the install line is read
- THEN it MUST install `.[http,deepseek]` and MUST NOT install `retrieval`

#### Scenario: Declared extra stays off the image

- GIVEN `pyproject.toml` still declares a `retrieval` extra
- WHEN the product image is built
- THEN that extra MUST NOT be installed

## MODIFIED Requirements

### Requirement: Measure Then Card

The host MUST sit outside `src/claimledger/http/` and off the 13-path allowlist. `reply`, `measure`, and card MUST NOT import `claimledger.retrieval` or `DoclingReader` and MUST NOT call `retrieve()`. The host MUST call `recorded_book()` once per completion and pass that same ledger to `execute`, `ask`, and `measure(question, ledger)`, then `render_card`. It MUST NOT call `Ledger.seed()`. Card candidates MUST be one `tables` row per verified evidence item (`text` is `evidence.text` when non-empty, otherwise `label`; `ref` is `evidence.artifact_hash`); abstain or empty evidence MUST yield `()`. It MUST NOT invent neighbor rows. For a compare result it MAY call the difference function on that same `QueryResult` and pass the string to `render_card`; it MUST NOT calculate the number itself. `artifact_hash` MAY select a page crop only. `card_text` MUST stay first and remain exactly that card: seal, chips, ordered rows, kernel values, difference line only when the card set it, and any sentence the card set. A page-crop PNG MAY follow. When the result is a verified series, a Mermaid fence from `draw(series_spec(result))` MUST follow card/pictures. Last-four-quarters MUST go through `execute` (fence with holes; no two-figure difference line). Every net result of BYMA MUST go through `ask` when the script has periods (fence copies verified values; no two-figure difference line); without a script it MUST abstain. After card/pictures/fence, the host MAY append agent-host-gated prose when authorization exists, or MUST append the controlled abstention template when authorization is empty or the gate falls through. Host MUST enforce authorization via verified claims/`authorized_values`; prompt MUST NOT be enforcement. Host MUST NOT let an LLM authorize `21262335`, `21259769`, the difference, or a bar height. `POST /claims/query` MUST stay the only product route (no candidates, no `delta`, no fence). Host tests MAY stub `recorded_book` and MUST NOT stub a Docling reader.

(Previously: `measure(artifact_hash, question, ledger)` after a stubbed reader; verified cards required both neighbor rows.)

#### Scenario: Consolidated value

- GIVEN a quarterly book whose verified consolidated evidence text is `21.262.335`
- WHEN the host completes the consolidated question
- THEN seal, chips, that text, and `21262335` MUST appear; `21259769` MUST NOT be the answer
- AND the two-row sentence MUST NOT appear, and `retrieve` MUST NOT be called

#### Scenario: Parent value

- GIVEN a quarterly book whose verified parent evidence has one text
- WHEN the host completes the parent question
- THEN `21259769` and that evidence text MUST appear, with no invented neighbor

#### Scenario: Picture follows the card

- GIVEN a page-crop PNG is allowed
- WHEN the host completes
- THEN `card_text` MUST be first and that PNG MUST follow in the same completion

#### Scenario: Compare completion draws the series

- GIVEN a quarterly book and “Comparar resultado neto consolidado 1T26 vs 2T26”
- WHEN the host completes
- THEN card first; Mermaid `bar [21262335, 81956525]`; `60694190` on the difference line only, not a bar height
- AND rows MUST come from those claims' evidence, and `retrieve` MUST NOT be called

#### Scenario: Single claim and abstain stay without fence

- GIVEN a consolidated or abstaining question
- WHEN the host completes
- THEN the body MUST NOT contain a Mermaid fence

#### Scenario: Last four quarters

- GIVEN a quarterly book and “Compará el resultado neto consolidado de los últimos 4 trimestres”
- WHEN the host completes
- THEN card first; `bar [21262335, 81956525]`; `Hueco: 2025-09-30` and `Hueco: 2025-12-31`; no `60694190`
- AND `retrieve` MUST NOT be called

#### Scenario: All net results

- GIVEN a quarterly book and a script with both periods
- WHEN the host completes “todos los resultados netos de BYMA”
- THEN card first; `bar [21262335, 81956525]`; no `60694190`
- AND `retrieve` MUST NOT be called

#### Scenario: HTTP stays one query

- GIVEN `POST /claims/query` and “todos los resultados netos de BYMA”
- WHEN the route answers
- THEN status `abstained`; the body MUST NOT contain `21262335` or a Mermaid fence

#### Scenario: Reply uses the quarterly book

- GIVEN `reply`
- WHEN its source is read
- THEN it MUST call `recorded_book` once, MUST NOT call `Ledger.seed()`, and MUST NOT import `claimledger.retrieval` or `DoclingReader`

#### Scenario: Card-first then gated prose or template

- GIVEN agent-host wiring
- WHEN the host answers
- THEN `card_text` first; trailing text MUST be gated verified prose or the controlled abstention template

### Requirement: No Invented Rows

Rows MUST come only from verified claim evidence. Empty evidence, abstain, or a missing hash MUST NOT produce invented neighbor rows. A verified card MUST NOT require a DoclingReader hash. Pytest MUST NOT stub `DoclingReader`. Gitignored artifacts MUST NOT be committed.

(Previously: an unreadable hash blocked the card, and pytest had to stub the reader.)

#### Scenario: Empty evidence invents nothing

- GIVEN a verified result with empty evidence
- WHEN a card is requested
- THEN no neighbor row MUST be invented, and the kernel value MUST still be shown

#### Scenario: No reader stub

- GIVEN host tests
- WHEN pytest runs
- THEN they MUST NOT stub `DoclingReader`, and gitignored artifacts MUST stay uncommitted

### Requirement: Always That Card

One completion MUST start with exactly one `card_text` from `render_card`, including seal `ME ABSTENGO` and compare cards with both claims and, when produced, “Diferencia entre las dos cifras verificadas”. Rows MUST be verified evidence only. A page-crop MAY follow. Host-gated verified prose or the controlled abstention template MAY follow after card/pictures/fence in the same completion. A second chat message MUST NOT appear before or after the card.

(Previously: the compare scenario required a stubbed reader.)

#### Scenario: Abstain keeps card then template

- GIVEN seal `ME ABSTENGO` and empty authorization
- WHEN the host completes
- THEN the abstain card is first; trailing text is only the controlled abstention template; no picture, difference line, invented value, or LLM financial prose

#### Scenario: Compare shows the code difference

- GIVEN a quarterly book and “Comparar resultado neto consolidado 1T26 vs 2T26”
- WHEN the host completes
- THEN the card is first with `21262335`, `81956525`, and “Diferencia entre las dos cifras verificadas” + `60694190`; pictures MAY follow in claim order
- AND neighbor rows MUST NOT be invented
