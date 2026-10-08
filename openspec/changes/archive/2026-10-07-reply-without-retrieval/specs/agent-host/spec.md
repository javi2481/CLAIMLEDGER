# Delta for Agent-Host

## MODIFIED Requirements

### Requirement: Search Never Authorizes

`search` MAY call `retrieve`. When that call succeeds, hits MUST be Docling-JSON text/page/ref only. When `retrieve` raises `ImportError`, `search` MUST return empty hits and MUST NOT raise. `search` MUST NOT return `verified` or `authorized_values`. Evidence and empty hits MUST NOT authorize a figure. `verify` remains the only tool that fills `authorized_values`.

(Previously: `search` had to return LlamaIndex hits and had no empty-hits path when the extra was missing.)

#### Scenario: Search is context only

- GIVEN a hit whose text contains digits
- WHEN `search` runs
- THEN the result has text/page/ref only — never `verified`/`authorized_values`

#### Scenario: Evidence is not authorization

- GIVEN only search text with `21.262.335`
- WHEN the gate runs
- THEN that figure MUST NOT be authorized

#### Scenario: ImportError returns empty hits

- GIVEN `retrieve` raises `ImportError`
- WHEN `search` runs
- THEN hits MUST be empty
- AND `authorized_values` MUST stay empty, and the completion MUST NOT see that exception
