# Lookup Specification

## Purpose

Define lexical fold-and-order resolution from a Spanish question to an `Intent`. Fase 0 MUST NOT invent press/deck identities. Comunicado or deck plus P&L MUST abstain as `recipe_no_extract`.

## Requirements

### Requirement: Fold Then Closed Phrase Order

The system MUST `fold` the question (lowercase, strip accents) and then apply this order without inventing identity. Press/deck identity routes MUST NOT be added.

1. YPF + precio/cierre/3 de enero → `off_corpus`
2. memoria + resultado/neto/eeff → `recipe_no_extract`
3. comunicado + neto/consolidado/controlante/bruto/impuesto → `recipe_no_extract`
4. presentación/slides/deck + those same P&L metrics → `recipe_no_extract`
5. contrato/cláusula → `recipe_no_extract`
6. narrative cues (`explica`, `crecimiento de ingresos`, `politica contable`, …) and the question does not ask for neto → route `narrative`
7. compare if compar/vs/versus/mayor/diferencia/ambos períodos
8. resolve 1T / 2T / both
9. metric order: no controlante → controlante/atribuible (unless “no el atribuible”) → bruto → operativo → antes de impuesto → impuesto a las ganancias → default consolidated `net_income`

#### Scenario: Accents fold before matching

- GIVEN question text with accents such as `trimestre`
- WHEN lookup folds
- THEN matching MUST use the folded form
- AND phrase order MUST still apply

#### Scenario: YPF rule wins over default neto

- GIVEN “Precio de YPF el 3 enero”
- WHEN lookup runs
- THEN Intent MUST be `off_corpus`
- AND default consolidated net income MUST NOT be applied

### Requirement: Issuer Is Always BYMA

For this gold, issuer MUST be `BYMA`. Lookup MUST NOT extract issuer from the question. YPF plus precio/cierre/3 de enero MUST yield `off_corpus` even if the text mentions BYMA.

#### Scenario: YPF close is off corpus

- GIVEN “¿Cuál fue el precio de cierre de YPF en BYMA el 3 de enero?”
- WHEN lookup runs
- THEN Intent MUST carry abstain reason `off_corpus`
- AND no P&L identity MUST be produced

#### Scenario: Ordinary EEFF question stays BYMA

- GIVEN “¿Cuál es el RESULTADO NETO DEL PERÍODO consolidado del 1T26?”
- WHEN lookup runs
- THEN issuer MUST be `BYMA`
- AND the Intent MUST NOT parse another issuer from the text

### Requirement: Non-EEFF Sources Refuse to Invent

Memoria plus resultado/neto/eeff, comunicado plus P&L metrics, presentación/slides/deck plus those P&L metrics, and contrato/cláusula MUST yield `recipe_no_extract`. That refusal MUST be the portfolio demonstration that the kernel does not invent from comunicado or deck.

#### Scenario: Comunicado plus neto abstains

- GIVEN “¿Cuál es el resultado neto consolidado del comunicado de prensa?”
- WHEN lookup runs
- THEN Intent MUST be `recipe_no_extract`
- AND no EEFF identity MUST be returned

#### Scenario: Deck plus P&L abstains

- GIVEN a question that attributes a P&L metric (neto, consolidado, controlante, bruto, or impuesto) to presentación, slides, or deck
- WHEN lookup runs
- THEN Intent MUST be `recipe_no_extract`

#### Scenario: Memoria and contract abstain

- GIVEN “resultado neto del período en la memoria anual” or “cláusula 5 del contrato”
- WHEN lookup runs
- THEN Intent MUST be `recipe_no_extract`

### Requirement: Narrative Route Invents No Number

Narrative cues without a neto ask MUST set route `narrative`. Lookup MUST NOT invent a numeric identity for growth or policy questions.

#### Scenario: Growth narrative is narrative

- GIVEN a folded question with `explica` or `crecimiento de ingresos` that does not ask for neto
- WHEN lookup runs
- THEN route MUST be `narrative`
- AND no claim identity MUST be resolved

#### Scenario: Neto ask is not narrative

- GIVEN a question that asks for resultado neto
- WHEN lookup runs
- THEN route MUST NOT be `narrative` solely because explanatory words appear

### Requirement: Compare, Period, and Metric Resolution

If compar/vs/versus/mayor/diferencia/ambos períodos appear, or both quarter tokens appear, Intent MUST set compare and MUST set period to none. Metric MUST follow the closed order. Lookup MUST NOT return `rejected`. Abstain reasons MUST be only `off_corpus`, `recipe_no_extract`, `no_matching_claim`, `incomplete_comparison`, `ambiguous_period`, `unresolved_identity`.

#### Scenario: Versus marks compare

- GIVEN “Comparar resultado neto consolidado 1T26 vs 2T26”
- WHEN lookup runs
- THEN compare MUST be true
- AND period MUST be none

#### Scenario: Single quarter binds period

- GIVEN a neto consolidado question that contains only 1T26 tokens
- WHEN lookup runs
- THEN period MUST be `2026-03-31`
- AND compare MUST be false

#### Scenario: Default metric is consolidated net income

- GIVEN an EEFF question with no more specific metric
- WHEN lookup runs
- THEN scope/metric MUST be `consolidated` / `net_income`

#### Scenario: Parenthetical controlante wins unless excluded

- GIVEN “resultado atribuible a la controlante 1T26”
- WHEN lookup runs
- THEN scope/metric MUST be `parent_attributable` / `net_income`
- AND “no el atribuible” MUST keep consolidated net income

#### Scenario: Rejected is not a lookup return

- GIVEN any question
- WHEN lookup returns
- THEN the result MUST be an Intent
- AND the status MUST NOT be `rejected`
