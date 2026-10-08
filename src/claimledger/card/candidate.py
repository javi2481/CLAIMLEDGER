"""Display rows for a verified card. Not a retrieval drawer."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from claimledger.claim import FinancialClaim


@dataclass(frozen=True)
class Candidate:
    drawer: Literal["tables", "narrative"]
    text: str
    ref: str


def candidates_from_claims(claims: tuple[FinancialClaim, ...]) -> tuple[Candidate, ...]:
    return tuple(
        Candidate(
            drawer="tables",
            text=item.text or item.label,
            ref=item.artifact_hash,
        )
        for claim in claims
        for item in claim.evidence
    )
