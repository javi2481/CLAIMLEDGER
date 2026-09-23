# Ledger Specification

## Purpose

Define the in-memory financial book: upsert, conflict, seed, and the rule that query never mutates ingest state. `recorded` is not `verified`.

## Requirements

### Requirement: In-Memory Upsert Book

The system MUST keep claims in an in-memory ledger keyed by `identity_key`. A first matching contract MUST store the claim as `recorded`. The same identity and same value MUST append evidence and remain `recorded`. The ledger MUST NOT be Claimprint `store.py` and MUST NOT write disk extract caches.

#### Scenario: First upsert is recorded

- GIVEN an empty ledger and claim `BYMA|2026-03-31|income_statement|consolidated|net_income` = `21262335`
- WHEN the claim is upserted
- THEN `ledger_status` MUST be `recorded`
- AND a later get by that key MUST return the same value

#### Scenario: Same identity and value appends evidence

- GIVEN a recorded claim with one evidence
- WHEN a second evidence with the same identity and value is upserted
- THEN `ledger_status` MUST stay `recorded`
- AND `evidence[]` MUST contain both items

### Requirement: Conflict Preserves Both Evidences

The same identity with a different value MUST become `conflicted`. The system MUST NOT overwrite the first value. Both evidences MUST remain.

#### Scenario: Other value marks conflict

- GIVEN recorded identity `BYMA|2026-03-31|income_statement|consolidated|net_income` = `21262335`
- WHEN a claim with the same key and value `22362983` is upserted
- THEN `ledger_status` MUST be `conflicted`
- AND the original value MUST still be recoverable from the kept evidences

#### Scenario: Conflict keeps both evidences

- GIVEN two upserts of the same identity with different values
- WHEN the book is read
- THEN both evidences MUST be present
- AND neither evidence MUST be dropped to hide the conflict

### Requirement: Query Does Not Mutate the Book

A query MUST NOT change `ledger_status`, values, or `evidence[]`. Query `verified` MUST NOT be written onto the claim.

#### Scenario: Verified answer leaves recorded intact

- GIVEN a recorded recipe claim
- WHEN query returns `verified` for that identity
- THEN the stored `ledger_status` MUST still be `recorded`

#### Scenario: Abstention leaves the book unchanged

- GIVEN a seeded ledger
- WHEN query returns `abstained`
- THEN every stored claim MUST be byte-equal to its pre-query state

### Requirement: Recipe Seed Without Prior as Current

Fase 0 MUST seed the fourteen recipe rows below. Prior figure `22362983` MUST NOT be seeded as current-period `net_income`. Neighbor pair `21262335` and `21259769` MUST both exist as distinct keys.

| period | scope | metric | value |
|---|---|---|---|
| `2026-03-31` | `consolidated` | `net_income` | `21262335` |
| `2026-03-31` | `parent_attributable` | `net_income` | `21259769` |
| `2026-03-31` | `consolidated` | `gross_profit` | `60144176` |
| `2026-03-31` | `consolidated` | `operating_income` | `70223471` |
| `2026-03-31` | `consolidated` | `income_before_tax` | `36213283` |
| `2026-03-31` | `consolidated` | `income_tax` | `-14950948` |
| `2026-03-31` | `consolidated` | `nci_income` | `2566` |
| `2026-06-30` | `consolidated` | `net_income` | `81956525` |
| `2026-06-30` | `parent_attributable` | `net_income` | `81946993` |
| `2026-06-30` | `consolidated` | `gross_profit` | `122610546` |
| `2026-06-30` | `consolidated` | `operating_income` | `143236114` |
| `2026-06-30` | `consolidated` | `income_before_tax` | `114688061` |
| `2026-06-30` | `consolidated` | `income_tax` | `-32731536` |
| `2026-06-30` | `consolidated` | `nci_income` | `9532` |

#### Scenario: Fourteen recipe rows are present

- GIVEN a gold-seeded ledger
- WHEN all recipe keys are read
- THEN exactly those fourteen current values MUST be present

#### Scenario: Prior figure is not current net income

- GIVEN the gold seed
- WHEN `BYMA|2026-03-31|income_statement|consolidated|net_income` is read
- THEN the current value MUST be `21262335`
- AND `22362983` MUST NOT be stored as that key's current value

### Requirement: Recorded Is Not Verified

`ledger_status` MUST be only `recorded` or `conflicted`. Pipeline `candidate` MUST NOT be a ledger status. Query `verified` and store-side `rejected` MUST NOT be persisted as `ledger_status`.

#### Scenario: Ingest never stamps verified

- GIVEN a successful upsert
- WHEN the claim is inspected
- THEN `ledger_status` MUST be `recorded`
- AND it MUST NOT equal `verified`

#### Scenario: Conflicted is not a verified answer

- GIVEN a `conflicted` claim
- WHEN query is asked for that identity
- THEN the system MUST NOT return `verified` from ingest status alone
