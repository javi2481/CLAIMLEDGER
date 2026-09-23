"""Frozen financial claim. ledger_status only; identity_key must match five fields."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

from claimledger.evidence import FinancialEvidence
from claimledger.identity import identity_key

LedgerStatus = Literal["recorded", "conflicted"]

_VALUE_RE = re.compile(r"^-?\d+$")
_LEDGER_STATUSES = frozenset({"recorded", "conflicted"})


class ClaimError(ValueError):
    """Claim failed integrity checks."""


def validate_claim(claim: FinancialClaim) -> None:
    expected = identity_key(
        claim.issuer, claim.period, claim.statement, claim.scope, claim.metric
    )
    if claim.identity_key != expected:
        raise ClaimError(
            "identity_key inconsistent with issuer|period|statement|scope|metric"
        )
    if not isinstance(claim.value, str) or _VALUE_RE.fullmatch(claim.value) is None:
        raise ClaimError("value must be a digit string with optional leading minus")
    if claim.currency != "ARS":
        raise ClaimError("currency must be ARS")
    if claim.unit not in (None, "ARS"):
        raise ClaimError('unit must be null or "ARS"')
    if claim.ledger_status not in _LEDGER_STATUSES:
        raise ClaimError("ledger_status must be recorded or conflicted")


@dataclass(frozen=True)
class FinancialClaim:
    identity_key: str
    issuer: str
    period: str
    statement: str
    scope: str
    metric: str
    value: str
    currency: str
    unit: str | None
    evidence: tuple[FinancialEvidence, ...]
    ledger_status: LedgerStatus

    def __post_init__(self) -> None:
        validate_claim(self)
