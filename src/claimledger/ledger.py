"""In-memory financial book. Thin Ledger over dict[identity_key, FinancialClaim]."""

from __future__ import annotations

from dataclasses import replace

from claimledger.claim import FinancialClaim
from claimledger.identity import identity_key

RECIPE_ROWS: tuple[tuple[str, str, str, str], ...] = (
    ("2026-03-31", "consolidated", "net_income", "21262335"),
    ("2026-03-31", "parent_attributable", "net_income", "21259769"),
    ("2026-03-31", "consolidated", "gross_profit", "60144176"),
    ("2026-03-31", "consolidated", "operating_income", "70223471"),
    ("2026-03-31", "consolidated", "income_before_tax", "36213283"),
    ("2026-03-31", "consolidated", "income_tax", "-14950948"),
    ("2026-03-31", "consolidated", "nci_income", "2566"),
    ("2026-06-30", "consolidated", "net_income", "81956525"),
    ("2026-06-30", "parent_attributable", "net_income", "81946993"),
    ("2026-06-30", "consolidated", "gross_profit", "122610546"),
    ("2026-06-30", "consolidated", "operating_income", "143236114"),
    ("2026-06-30", "consolidated", "income_before_tax", "114688061"),
    ("2026-06-30", "consolidated", "income_tax", "-32731536"),
    ("2026-06-30", "consolidated", "nci_income", "9532"),
)


class Ledger:
    """Isolated in-memory book. No module-level shared state. No disk cache."""

    def __init__(self) -> None:
        self._book: dict[str, FinancialClaim] = {}

    def upsert(self, claim: FinancialClaim) -> FinancialClaim:
        existing = self._book.get(claim.identity_key)
        if existing is None:
            stored = replace(claim, ledger_status="recorded")
        elif existing.value == claim.value:
            stored = replace(
                existing,
                evidence=existing.evidence + claim.evidence,
                ledger_status="recorded",
            )
        else:
            stored = replace(
                existing,
                evidence=existing.evidence + claim.evidence,
                ledger_status="conflicted",
            )
        self._book[claim.identity_key] = stored
        return stored

    def get(self, key: str) -> FinancialClaim | None:
        return self._book.get(key)

    @classmethod
    def seed(cls) -> Ledger:
        ledger = cls()
        for period, scope, metric, value in RECIPE_ROWS:
            key = identity_key("BYMA", period, "income_statement", scope, metric)
            ledger.upsert(
                FinancialClaim(
                    identity_key=key,
                    issuer="BYMA",
                    period=period,
                    statement="income_statement",
                    scope=scope,
                    metric=metric,
                    value=value,
                    currency="ARS",
                    unit=None,
                    evidence=(),
                    ledger_status="recorded",
                )
            )
        return ledger
