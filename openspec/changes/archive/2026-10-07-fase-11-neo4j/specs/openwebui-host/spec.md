# Open WebUI Host Specification

## Purpose

The host draws the card. For every net result of BYMA it reads the Cypher script, verifies each period, and appends the fence. The HTTP route does not.

## Requirements

### Requirement: Book Series After the Card

When `ask` returns a run, `reply` MUST render the card from the verified claims, MUST NOT append the two-figure difference line, and MUST append the phase 12 fence. For “todos los resultados netos de BYMA” with a script of both book periods, the fence MUST contain `bar [21262335, 81956525]` and MUST NOT contain `60694190`. Without a script the reply MUST abstain and MUST NOT show `81956525`. `POST /claims/query` for that question MUST stay abstained and MUST NOT contain a Mermaid fence. Phase 10 MUST NOT start. `src/claimledger/book/` MUST stay off the 13-path allowlist.

#### Scenario: All net results

- GIVEN a stubbed reader and a script with both book periods
- WHEN the host completes “todos los resultados netos de BYMA”
- THEN the body MUST start with the card
- AND the bar line MUST be `bar [21262335, 81956525]`
- AND `60694190` MUST NOT appear

#### Scenario: HTTP stays one query

- GIVEN `POST /claims/query` and “todos los resultados netos de BYMA”
- WHEN the route answers
- THEN the status MUST be `abstained`
- AND the body MUST NOT contain `21262335` or a Mermaid fence
