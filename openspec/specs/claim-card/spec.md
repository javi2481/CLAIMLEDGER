# Claim Card Specification

## Purpose

`render_card(candidates, result)` shows the kernel verdict beside row text.

## Requirements

### Requirement: Pure Display

`render_card` MUST live outside the kernel, take `(candidates, result)` plus, for compare only, an optional difference string already computed, and MUST NOT call `measure`, `retrieve`, `understand`, `query`, `upsert`, or the difference function. Rows MUST be `Candidate.text` in order. The value MUST be `claim.value`. It MUST NOT parse digits.

#### Scenario: No kernel calls

- GIVEN candidates and a `QueryResult`
- WHEN `render_card` runs
- THEN it MUST NOT call `measure`, `retrieve`, `understand`, `query`, `upsert`, or the difference function

### Requirement: Verified Consolidated Card

A verified consolidated claim MUST seal `VERIFICADO`, use chips `BYMA · 1T26 · Consolidado · Resultado neto`, show `21262335`, keep both neighbor texts in order, and use the sentence “encontré estas dos filas; verifiqué la consolidada”. It MUST NOT present `21259769` as the answer.

#### Scenario: Consolidated rows and seal

- GIVEN `RESULTADO NETO DEL PERÍODO 21.262.335` then `Resultado neto atribuible a la sociedad controlante 21.259.769`, and verified value `21262335`
- WHEN `render_card` runs
- THEN the seal MUST be `VERIFICADO`, chips MUST be `BYMA · 1T26 · Consolidado · Resultado neto`, and the value MUST be `21262335`
- AND both texts MUST stay in order, the sentence MUST be “encontré estas dos filas; verifiqué la consolidada”, and `21259769` MUST NOT be the answer

### Requirement: Verified Parent Card

A verified parent claim MUST seal `VERIFICADO`. Chips MUST name the parent scope and MUST NOT say `Consolidado`. The value MUST be `21259769`. Both neighbor texts MUST remain. The sentence MUST name the parent scope and MUST NOT say the consolidated row was verified.

#### Scenario: Parent scope is not consolidated

- GIVEN both neighbor texts and verified value `21259769`
- WHEN `render_card` runs
- THEN the seal MUST be `VERIFICADO`, chips MUST name the parent scope and MUST NOT say `Consolidado`, and the value MUST be `21259769`
- AND both texts MUST remain, and the sentence MUST name the parent scope

### Requirement: Abstain Card

`recipe_no_extract` MUST seal `ME ABSTENGO` and keep that reason. Rows MAY be present. The sentence MUST NOT say a row was verified. `21262335` MUST NOT be the answer. An empty candidate list with an abstain MUST still seal `ME ABSTENGO`.

#### Scenario: recipe_no_extract keeps the reason

- GIVEN both neighbor rows and abstained reason `recipe_no_extract`
- WHEN `render_card` runs
- THEN the seal MUST be `ME ABSTENGO` and the reason MUST stay `recipe_no_extract`
- AND the sentence MUST NOT say a row was verified, and `21262335` MUST NOT be the answer

#### Scenario: Empty candidates still abstain

- GIVEN an empty candidate list and an abstained result
- WHEN `render_card` runs
- THEN the seal MUST be `ME ABSTENGO`

### Requirement: Compare Card

A compare result MUST show claims `21262335` and `81956525`. `render_card` MUST NOT compute the difference and MUST NOT parse digits. It MAY show the difference string that code already computed, on one line labelled exactly “Diferencia entre las dos cifras verificadas”, and only when a string was produced. That line MUST NOT say “segundo trimestre”, “trimestre aislado”, or “claims”. Abstain and single-claim cards MUST NOT show that line. `_METRIC_CHIP` MUST stay `net_income` only.

#### Scenario: Two values and the passed difference

- GIVEN verified compare values `21262335` and `81956525` and the computed string `60694190`
- WHEN `render_card` runs
- THEN both values MUST be shown, and `60694190` MUST appear after “Diferencia entre las dos cifras verificadas”
- AND no “segundo trimestre”, “trimestre aislado”, or “claims” MUST appear on that line

#### Scenario: No string, no line

- GIVEN verified compare values `21262335` and `81956525` and no computed string
- WHEN `render_card` runs
- THEN both values MUST be shown, and no difference line and no `60694190` MUST appear

#### Scenario: Abstain and single cards unchanged

- GIVEN an abstained result or a single verified claim
- WHEN `render_card` runs
- THEN no difference line MUST appear

### Requirement: Seal Follows Query Status

The seal MUST follow `QueryResult.status`: `verified` seals `VERIFICADO` and `abstained` seals `ME ABSTENGO`. It MUST NOT follow `ledger_status`. A recorded claim the result did not verify MUST NOT seal `VERIFICADO`.

#### Scenario: Recorded is not verified

- GIVEN `ledger_status` `recorded` and a result that did not verify
- WHEN `render_card` runs
- THEN the seal MUST NOT be `VERIFICADO`

### Requirement: Package Boundary

The card module MUST NOT import `starlette`, `docling`, `llama_index`, or `open_webui`. `src/claimledger/card/` and `tests/card/` MUST stay off the 13-path allowlist. No new library; `dependencies` MUST stay `[]`. `src/claimledger/__init__.py` MUST stay empty.

#### Scenario: Off the allowlist with no new library

- GIVEN the card module and `pyproject.toml`
- WHEN imports and dependencies are read
- THEN it MUST NOT import `starlette`, `docling`, `llama_index`, or `open_webui`
- AND `dependencies` MUST stay `[]`, and those card paths MUST stay off the allowlist
