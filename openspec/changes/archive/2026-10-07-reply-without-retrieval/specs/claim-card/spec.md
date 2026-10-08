# Delta for Claim-Card

## ADDED Requirements

### Requirement: Candidate Location

`Candidate` MUST live in `claimledger.card.candidate` with `drawer`, `text`, and `ref`. `drawer` MUST be `tables` or `narrative`. Card rendering MUST import that type and MUST NOT import `claimledger.retrieval`, `retrieval.drawers`, or `DoclingReader`. `retrieval.drawers` MAY re-export the same type.

#### Scenario: Card owns Candidate

- GIVEN `src/claimledger/card/`
- WHEN imports are read
- THEN `Candidate` MUST be defined in `card.candidate`
- AND card modules MUST NOT import `claimledger.retrieval` or `DoclingReader`

#### Scenario: Drawers may re-export

- GIVEN `retrieval.drawers` exposes `Candidate`
- WHEN that binding is read
- THEN it MUST be the card type, and card MUST NOT import drawers

## MODIFIED Requirements

### Requirement: Verified Consolidated Card

A verified consolidated claim MUST seal `VERIFICADO`, use chips `BYMA · 1T26 · Consolidado · Resultado neto`, and show `21262335`. Rows MUST be the given `Candidate.text` values in order and MUST NOT be invented. When there are exactly two rows, the sentence MUST be “encontré estas dos filas; verifiqué la consolidada”. When there are fewer than two rows, the card MUST still seal `VERIFICADO`, MUST omit that sentence, and a claim-only sentence MAY appear and MUST NOT claim two rows. It MUST NOT present `21259769` as the answer.

(Previously: both neighbor texts and the two-row sentence were always required.)

#### Scenario: Two rows keep the sentence

- GIVEN `RESULTADO NETO DEL PERÍODO 21.262.335` then `Resultado neto atribuible a la sociedad controlante 21.259.769`, and verified value `21262335`
- WHEN `render_card` runs
- THEN the seal MUST be `VERIFICADO`, chips MUST be `BYMA · 1T26 · Consolidado · Resultado neto`, and the value MUST be `21262335`
- AND both texts MUST stay in order, the sentence MUST be “encontré estas dos filas; verifiqué la consolidada”, and `21259769` MUST NOT be the answer

#### Scenario: Fewer than two rows still seals

- GIVEN one evidence row and verified value `21262335`
- WHEN `render_card` runs
- THEN the seal MUST be `VERIFICADO` and the value MUST be `21262335`
- AND “encontré estas dos filas; verifiqué la consolidada” MUST NOT appear, and no second row MUST be invented

### Requirement: Verified Parent Card

A verified parent claim MUST seal `VERIFICADO`. Chips MUST name the parent scope and MUST NOT say `Consolidado`. The value MUST be `21259769`. Rows MUST be the given candidate texts and MUST NOT be invented. When there are exactly two rows, the sentence MUST name the parent scope and MUST NOT say the consolidated row was verified. When there are fewer than two rows, the card MUST still seal `VERIFICADO` and MUST omit any sentence that claims two rows. A claim-only sentence MAY appear.

(Previously: both neighbor texts were required on every parent card.)

#### Scenario: Parent scope is not consolidated

- GIVEN both neighbor texts and verified value `21259769`
- WHEN `render_card` runs
- THEN the seal MUST be `VERIFICADO`, chips MUST name the parent scope and MUST NOT say `Consolidado`, and the value MUST be `21259769`
- AND both texts MUST remain, and the sentence MUST name the parent scope

#### Scenario: One parent row still seals

- GIVEN one evidence row and verified value `21259769`
- WHEN `render_card` runs
- THEN the seal MUST be `VERIFICADO` and the value MUST be `21259769`
- AND no second row MUST be invented, and no sentence MUST claim two rows

### Requirement: Package Boundary

The card module MUST NOT import `starlette`, `docling`, `llama_index`, `open_webui`, `claimledger.retrieval`, or `DoclingReader`. `src/claimledger/card/` and `tests/card/` MUST stay off the 13-path allowlist. No new library; `dependencies` MUST stay `[]`. `src/claimledger/__init__.py` MUST stay empty. Kernel tests MUST NOT import `docling`.

(Previously: the import ban did not name `claimledger.retrieval` or `DoclingReader`.)

#### Scenario: Off the allowlist with no new library

- GIVEN the card module and `pyproject.toml`
- WHEN imports and dependencies are read
- THEN it MUST NOT import `starlette`, `docling`, `llama_index`, `open_webui`, `claimledger.retrieval`, or `DoclingReader`
- AND `dependencies` MUST stay `[]`, and those card paths MUST stay off the allowlist
