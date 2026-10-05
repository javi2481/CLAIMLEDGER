"""Join one tables drawer with identity and Claim Query on the seed ledger."""

from __future__ import annotations

from claimledger.ledger import Ledger
from claimledger.lookup import understand
from claimledger.query import QueryResult, query
from claimledger.retrieval.drawers import Candidate, retrieve


def measure(
    artifact_hash: str, question: str
) -> tuple[tuple[Candidate, ...], QueryResult]:
    candidates = retrieve(artifact_hash, "tables", question)
    intent = understand(question)
    result = query(intent, Ledger.seed())
    return candidates, result
