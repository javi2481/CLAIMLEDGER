# Evidence-Adapter Specification

## Purpose

Recipe P&L from two quarterly EEFF only. Classify the other eight. Fill `FinancialEvidence` from grid/provenance.

## Requirements

### Requirement: Recipe P&L From Two EEFF Only

The adapter MUST extract recipe P&L identities only from the two quarterly EEFF. Issuer MUST be `BYMA`. Period MUST come from pack/cover (`1T26` → `2026-03-31`, `2T26` → `2026-06-30`). The adapter MUST NOT decide consolidado vs controlante. Furniture MUST NOT mint identity.

#### Scenario: Two EEFF emit recipe rows

- GIVEN hashed JSON for the two quarterly EEFF
- WHEN the adapter extracts recipe P&L
- THEN it MUST emit recipe rows with issuer `BYMA` and pack/cover period
- AND it MUST NOT choose consolidado vs controlante or mint identity from furniture

### Requirement: Eight Classify With Zero P&L Identities

The other eight PDFs MUST be classified `comunicado|deck|memoria|transcript` with zero P&L identities. Comunicado `21262335` and memoria year-end P&L MUST NOT become identity. Lookup `recipe_no_extract` MUST stay (identity refusal, not out-of-corpus).

#### Scenario: Eight mint zero identities

- GIVEN each of the eight non-EEFF corpus PDFs
- WHEN the adapter classifies it
- THEN class MUST be `comunicado`, `deck`, `memoria`, or `transcript`
- AND zero P&L identities MUST be minted, including comunicado `21262335` and memoria year-end P&L

#### Scenario: Lookup refusal stays

- GIVEN a P&L question attributed to comunicado, deck, or memoria
- WHEN lookup runs after ingest
- THEN Intent MUST remain `recipe_no_extract`

### Requirement: Evidence Fields From Grid Provenance

Recipe rows MUST fill `FinancialEvidence` `page`, `bbox`, `label`, `artifact_hash`, `document_id`, and `text` from grid/provenance. `label` is the locator, not identity. Present `bbox` MUST be `[0, 1]` with `x0≤x1` and `y0≤y1`. Markdown MUST NOT be evidence SoT.

#### Scenario: EEFF evidence is filled

- GIVEN a recipe P&L cell from EEFF grid/provenance
- WHEN evidence is minted
- THEN `page`, `bbox`, `label`, `artifact_hash`, `document_id`, and `text` MUST be present
