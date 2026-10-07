# Delta for Query

## MODIFIED Requirements

### Requirement: Compare Returns Two Claims Without Delta

A compare Intent MUST return `verified` and two claims with the same scope/metric and different periods. `query` MUST NOT compute or return a difference. `QueryResult` MUST keep exactly four fields: `status`, `reason`, `claims`, `identity`; it MUST NOT gain a `delta` or `difference` field. Compare `expected_identity` MUST use `*` in period (example: `BYMA|*|income_statement|consolidated|gross_profit`). If only one period can be demonstrated, query MUST abstain with `incomplete_comparison`.

(Previously: compare MUST NOT subtract "until Fase 9"; subtraction now lives outside `query`, which still never subtracts.)

#### Scenario: Net income both quarters

- GIVEN recipe rows for 1T26 and 2T26 consolidated net income
- WHEN “Comparar resultado neto consolidado 1T26 vs 2T26” is queried
- THEN status MUST be `verified` and the two values MUST be `21262335` and `81956525`
- AND no delta field or subtracted amount MUST be present, and `60694190` MUST NOT be a returned value

#### Scenario: QueryResult keeps four fields

- GIVEN the `QueryResult` dataclass
- WHEN its fields are read
- THEN they MUST be exactly `status`, `reason`, `claims`, `identity`

#### Scenario: Compare identity keeps wildcard period

- GIVEN a comparison case
- WHEN the result identities are checked
- THEN the gold identity MUST remain `BYMA|*|…`
- AND each returned claim MUST keep its own concrete period

#### Scenario: One-sided compare abstains

- GIVEN a compare Intent whose ledger has only one of the two periods
- WHEN query runs
- THEN status MUST be `abstained`
- AND reason MUST be `incomplete_comparison`

## ADDED Requirements

### Requirement: Compare Difference Outside Query

A single function in a sibling package outside the seven kernel modules MUST read the `QueryResult` that `query` already produced. It MUST return a signed canonical digit string (the `signed_ars` shape; a positive result has no leading `+`) only when status is `verified`, there are exactly two claims, both share issuer, statement, scope, metric, currency, and unit, their periods differ, and both are `recorded`. Otherwise it MUST return nothing. The result MUST be later period minus earlier period. It MUST NOT be a `FinancialClaim`, MUST NOT have an `identity_key`, MUST NOT be upserted, and MUST NOT be read by the gold harness. Its package and tests MUST stay off the 13-path allowlist; its tests MUST NOT import `docling` and MUST NOT use network, PDF, or Docker. `digits.py` MUST stay unchanged.

#### Scenario: Net income difference

- GIVEN `query` on `Ledger.seed()` for 1T26 vs 2T26 consolidated net income
- WHEN the function reads that result
- THEN it MUST return `60694190` (`81956525` minus `21262335`)

#### Scenario: Negative side keeps its sign

- GIVEN a verified pair of consolidated `income_tax`, `-14950948` (1T26) and `-32731536` (2T26)
- WHEN the function reads it
- THEN it MUST return `-17780588`

#### Scenario: Mismatched pair yields no number

- GIVEN two claims that differ in scope, metric, currency, or unit
- WHEN the function reads them
- THEN it MUST return nothing

#### Scenario: Same period, abstain, or one claim yields no number

- GIVEN two claims with the same period, an `abstained` result, a single claim, or a claim that is not `recorded`
- WHEN the function reads it
- THEN it MUST return nothing

### Requirement: Query and Pack Stay Separate

The period pack MUST be satisfied by `fold_documents`, `GraphMerger(conflicts="keep-all")`, `Ledger.upsert`, and `extract_recipe`. This change MUST NOT add a second merger, a corpus walker, or a 15th `RECIPE_ROWS` row. `query` MUST keep running on the ledger it is given and MUST NOT call the pack or the difference function.

#### Scenario: No second merger and fourteen rows

- GIVEN this change
- WHEN `src/claimledger/` and `RECIPE_ROWS` are read
- THEN no new merger MUST exist, and `RECIPE_ROWS` MUST stay 14 rows
- AND `query` MUST NOT import the difference package
