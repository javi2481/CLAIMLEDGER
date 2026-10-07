# Delta for Open WebUI Host

## MODIFIED Requirements

### Requirement: Measure Then Card

The host MUST sit outside `src/claimledger/http/` and off the 13-path allowlist. It MUST call `recorded_book()` once per completion and pass that same ledger to `execute`, `ask`, and `measure`. It MUST NOT call `Ledger.seed()`. It MUST call `measure(artifact_hash, question, ledger)` then `render_card`. For a compare result it MAY call the difference function on that same `QueryResult` and pass the string to `render_card`; it MUST NOT calculate the number itself. `card_text` MUST stay first in the same assistant completion and MUST remain exactly that card: seal, chips, ordered rows, kernel values, the difference line only when the card set it, and a sentence the card already set. A page-crop PNG MAY follow that text in the same completion. When the result is a verified series, a Mermaid fence from `draw(series_spec(result))` MUST follow the card and any pictures in that same completion. A last-four-quarters question MUST go through `execute` instead of one compare `query`: the fence MUST include the holes, and the two-figure difference line MUST stay off that completion. A question for every net result of BYMA MUST go through `ask` when the script has periods: the fence MUST copy the verified values, and the two-figure difference line MUST stay off that completion. Without a script that question MUST abstain. The host MUST NOT parse digits or let an LLM choose `21262335`, `21259769`, the difference, or a bar height. `POST /claims/query` MUST stay the only product route, with no added candidates, no `delta`, and no fence. Host tests MAY stub `recorded_book` so they do not open a PDF.

#### Scenario: Consolidated value

- GIVEN a stubbed reader, a stubbed quarterly book, and a consolidated question
- WHEN the host completes
- THEN seal, chips, both rows, and `21262335` MUST appear
- AND `21259769` MUST NOT be the answer

#### Scenario: Parent value

- GIVEN a stubbed reader, a stubbed quarterly book, and a parent question
- WHEN the host completes
- THEN `21259769` and both rows MUST appear

#### Scenario: Picture follows the card

- GIVEN a page-crop PNG is allowed
- WHEN the host completes
- THEN `card_text` MUST be first and that PNG MUST follow in the same completion

#### Scenario: Compare completion draws the series

- GIVEN a stubbed reader, a stubbed quarterly book, and “Comparar resultado neto consolidado 1T26 vs 2T26”
- WHEN the host completes
- THEN card text MUST come first
- AND the Mermaid bar MUST be `bar [21262335, 81956525]`
- AND `60694190` MUST remain on the card difference line and MUST NOT be a bar height

#### Scenario: Single claim and abstain stay card-only

- GIVEN a consolidated question or an abstaining question
- WHEN the host completes
- THEN the body MUST NOT contain a Mermaid fence

#### Scenario: Last four quarters

- GIVEN a stubbed reader, a stubbed quarterly book, and “Compará el resultado neto consolidado de los últimos 4 trimestres”
- WHEN the host completes
- THEN the body MUST start with the card
- AND the bar line MUST be `bar [21262335, 81956525]`
- AND the text MUST contain `Hueco: 2025-09-30` and `Hueco: 2025-12-31`
- AND `60694190` MUST NOT appear

#### Scenario: All net results

- GIVEN a stubbed reader, a stubbed quarterly book, and a script with both book periods
- WHEN the host completes “todos los resultados netos de BYMA”
- THEN the body MUST start with the card
- AND the bar line MUST be `bar [21262335, 81956525]`
- AND `60694190` MUST NOT appear

#### Scenario: HTTP stays one query

- GIVEN `POST /claims/query` and “todos los resultados netos de BYMA”
- WHEN the route answers
- THEN the status MUST be `abstained`
- AND the body MUST NOT contain `21262335` or a Mermaid fence

#### Scenario: Reply uses the quarterly book

- GIVEN `reply`
- WHEN its source is read
- THEN it MUST call `recorded_book` once
- AND it MUST NOT call `Ledger.seed()`
