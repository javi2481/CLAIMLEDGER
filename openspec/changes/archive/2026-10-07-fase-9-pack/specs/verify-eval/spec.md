# Delta for Verify-Eval

## MODIFIED Requirements

### Requirement: Compare Without Subtraction

Compare MUST return two claims and `measure` MUST NOT subtract. The order MUST stay `retrieve`, then `understand`, then `query(Ledger.seed())`. The difference MUST live outside `measure`, in the sibling difference function; `measure` MUST NOT call it.

(Previously: compare MUST NOT subtract, without naming where subtraction lives.)

#### Scenario: Compare stays two claims

- GIVEN `Ledger.seed()` and “Comparar resultado neto consolidado 1T26 vs 2T26”
- WHEN the caller runs
- THEN verified claims MUST be `21262335` and `81956525`, and no subtracted difference MUST be returned
- AND `60694190` MUST NOT appear in what `measure` returns

#### Scenario: Measure does not call the difference

- GIVEN the caller module
- WHEN its imports and calls are read
- THEN it MUST NOT import or call the difference function, and tests MUST NOT import `docling` or use network, PDF, or Docker
