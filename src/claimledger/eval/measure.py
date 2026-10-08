"""Join identity and Claim Query. Rows are verified evidence."""

from __future__ import annotations

from claimledger.card.candidate import Candidate, candidates_from_claims
from claimledger.ledger import Ledger
from claimledger.lookup import understand
from claimledger.query import QueryResult, query


def measure(
    question: str,
    ledger: Ledger,
) -> tuple[tuple[Candidate, ...], QueryResult]:
    intent = understand(question)
    result = query(intent, ledger)
    if result.status != "verified":
        return (), result
    return candidates_from_claims(result.claims), result
