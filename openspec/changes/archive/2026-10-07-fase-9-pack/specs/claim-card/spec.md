# Delta for Claim Card

## MODIFIED Requirements

### Requirement: Compare Card

A compare result MUST show claims `21262335` and `81956525`. `render_card` MUST NOT compute the difference and MUST NOT parse digits. It MAY show the difference string that code already computed, on one line labelled exactly “Diferencia entre las dos cifras verificadas”, and only when a string was produced. That line MUST NOT say “segundo trimestre”, “trimestre aislado”, or “claims”. Abstain and single-claim cards MUST NOT show that line. `_METRIC_CHIP` MUST stay `net_income` only.

(Previously: a compare card MUST NOT subtract or show a delta.)

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

### Requirement: Pure Display

`render_card` MUST live outside the kernel, take `(candidates, result)` plus, for compare only, an optional difference string already computed, and MUST NOT call `measure`, `retrieve`, `understand`, `query`, `upsert`, or the difference function. Rows MUST be `Candidate.text` in order. The value MUST be `claim.value`. It MUST NOT parse digits.

(Previously: `render_card` took only `(candidates, result)`.)

#### Scenario: No kernel calls

- GIVEN candidates and a `QueryResult`
- WHEN `render_card` runs
- THEN it MUST NOT call `measure`, `retrieve`, `understand`, `query`, `upsert`, or the difference function
