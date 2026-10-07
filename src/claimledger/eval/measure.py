"""Join one tables drawer with identity and Claim Query on a ledger."""

from __future__ import annotations

from claimledger.ledger import Ledger
from claimledger.lookup import understand
from claimledger.query import QueryResult, query
from claimledger.retrieval.drawers import Candidate, retrieve


def measure(
    artifact_hash: str,
    question: str,
    ledger: Ledger | None = None,
) -> tuple[tuple[Candidate, ...], QueryResult]:
    candidates = retrieve(artifact_hash, "tables", question)
    intent = understand(question)
    book = ledger if ledger is not None else _quarterly_book()
    result = query(intent, book)
    return candidates, result


def _quarterly_book() -> Ledger:
    from claimledger.ingest.ground import recorded_book

    return recorded_book()
