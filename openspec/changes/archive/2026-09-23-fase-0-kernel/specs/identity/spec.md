# Identity Specification

## Purpose

Define the frozen five-field financial identity, period and money normals, Claimprint alias table, and claim/evidence shape for the Fase 0 kernel. Value is a component, not identity.

## Requirements

### Requirement: Five-Field Identity Key

The system MUST identify a claim as `identity_key = issuer|period|statement|scope|metric`. Value, currency, unit, and provenance MUST NOT enter the key. Construction SHALL fail when `identity_key` is inconsistent with the five fields.

#### Scenario: Consistent key constructs

- GIVEN issuer `BYMA`, period `2026-03-31`, statement `income_statement`, scope `consolidated`, metric `net_income`
- WHEN a claim is constructed with matching `identity_key` `BYMA|2026-03-31|income_statement|consolidated|net_income`
- THEN construction MUST succeed

#### Scenario: Inconsistent key is rejected

- GIVEN five fields for consolidated net income at `2026-03-31`
- WHEN `identity_key` is any other string
- THEN construction MUST fail with an error
- AND no claim MUST be stored

#### Scenario: Neighbor values are distinct identities

- GIVEN values `21262335` and `21259769`
- WHEN both claims share issuer, period, and statement but differ in scope/metric
- THEN they MUST be two identities
- AND the values MUST NOT be treated as the identity

### Requirement: Claimprint Alias Mapping

The system MUST rewrite Claimprint v1 `scope|metric` pairs through the frozen alias table only. Document labels MUST be locators, not IDs. Gold rows with `period=*` or `expected_identity=null` MUST be ported unchanged.

| v1 (`scope\|metric`) | statement | scope | metric |
|---|---|---|---|
| `consolidado\|resultado_neto` | `income_statement` | `consolidated` | `net_income` |
| `controlante\|resultado_atribuible_controladora` | `income_statement` | `parent_attributable` | `net_income` |
| `consolidado\|resultado_bruto` | `income_statement` | `consolidated` | `gross_profit` |
| `consolidado\|resultado_operativo` | `income_statement` | `consolidated` | `operating_income` |
| `consolidado\|resultado_antes_impuesto` | `income_statement` | `consolidated` | `income_before_tax` |
| `consolidado\|impuesto_ganancias` | `income_statement` | `consolidated` | `income_tax` |
| `consolidado\|resultado_no_controlante` | `income_statement` | `consolidated` | `nci_income` |

#### Scenario: Canonical neighbor alias

- GIVEN v1 key `consolidado|resultado_neto` and period `2026-03-31`
- WHEN aliases are applied
- THEN `expected_identity` MUST be `BYMA|2026-03-31|income_statement|consolidated|net_income`

#### Scenario: Alias table is one-to-one

- GIVEN the seven v1 keys in the table
- WHEN `aliases.json` is checked
- THEN each v1 key MUST map to exactly one 5-field English identity
- AND no extra Fase 0 alias MUST be invented

#### Scenario: Wildcard and null identities port

- GIVEN gold `expected_identity` with `period=*` or `null`
- WHEN the case is ported
- THEN the wildcard or null MUST remain
- AND the system MUST NOT invent a period or identity

### Requirement: Canonical Period Before Identity

The system MUST normalize period to `2026-03-31` or `2026-06-30` before composing `identity_key`. After `fold` (lowercase, no accents), 1T26 tokens MUST map to `2026-03-31` and 2T26 tokens MUST map to `2026-06-30`.

| Canonical | Tokens after fold |
|---|---|
| `2026-03-31` | `1t26`, `1t 26`, `marzo`, `2026-03-31`, `31 de marzo`, `primer trimestre` |
| `2026-06-30` | `2t26`, `2t 26`, `junio`, `2026-06-30`, `30 de junio`, `segundo trimestre` |

#### Scenario: First quarter tokens

- GIVEN a folded token from the 1T26 set
- WHEN period is normalized
- THEN the result MUST be `2026-03-31`

#### Scenario: Second quarter tokens

- GIVEN a folded token from the 2T26 set
- WHEN period is normalized
- THEN the result MUST be `2026-06-30`

### Requirement: Digit and Signed Money

`digits_ars` MUST strip thousand dots and MUST NOT treat a comma as a decimal. Empty or `None` MUST become `None`. `signed_ars` MUST treat parentheses as negative. Claim `value` MUST be a digit string with optional leading `-`. The system MUST NOT store floats or compact forms such as `21,26 M`. Pilot `currency` MUST be `ARS`. `unit` MUST be `null` or `"ARS"`. Income tax MUST keep its sign (`-14950948`, `-32731536`).

#### Scenario: Thousand dots collapse

- GIVEN text `21.262.335`
- WHEN `digits_ars` runs
- THEN the result MUST be `21262335`

#### Scenario: Parentheses are negative

- GIVEN text `(14.950.948)`
- WHEN `signed_ars` runs
- THEN the result MUST be `-14950948`

#### Scenario: Empty money is null

- GIVEN empty string or `None`
- WHEN `digits_ars` runs
- THEN the result MUST be `None`

#### Scenario: Compact millions are forbidden

- GIVEN a compact form such as `21,26 M`
- WHEN a claim value is produced
- THEN the system MUST NOT accept that form as `21262335`

### Requirement: Frozen Evidence and Claim Shape

`FinancialEvidence` MUST expose `document_id`, `artifact_hash`, `page`, `text`, optional `bbox`, and `label`. `FinancialClaim` MUST expose `identity_key`, the five identity fields, `value`, `currency`, `unit`, `evidence[]`, and `ledger_status` of `recorded` or `conflicted`. The claim MUST NOT store rector §7 `verification_status`. `artifact_hash` and `bbox` MAY be empty in Fase 0. If `bbox` is present, coordinates MUST be in `[0, 1]` with `x0≤x1` and `y0≤y1`.

#### Scenario: Recorded claim without verification field

- GIVEN a valid identity and value
- WHEN a claim is constructed
- THEN `ledger_status` MUST be `recorded` or later `conflicted`
- AND the object MUST NOT expose `verification_status`

#### Scenario: Invalid bbox is rejected

- GIVEN a bbox outside `[0, 1]` or with inverted corners
- WHEN evidence is constructed
- THEN construction MUST fail
