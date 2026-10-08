"""Verify authorizes; search finds evidence only."""

from __future__ import annotations

from typing import Any

from claimledger.book.ask import ask, read_script
from claimledger.claim import FinancialClaim
from claimledger.ingest.ground import recorded_book
from claimledger.ledger import Ledger
from claimledger.lookup import understand
from claimledger.orchestrate.plan import execute
from claimledger.query import QueryResult, query


def verify(question: str, ledger: Ledger | None = None) -> dict[str, Any]:
    book = ledger if ledger is not None else recorded_book()
    result = _resolve(question, book)
    if result.status != "verified":
        return {"status": "abstained", "claims": [], "authorized_values": []}
    claims = [_project_claim(claim) for claim in result.claims]
    authorized = [claim["value"] for claim in claims]
    return {
        "status": "verified",
        "claims": claims,
        "authorized_values": authorized,
    }


def search(artifact_hash: str, question: str) -> dict[str, Any]:
    try:
        from claimledger.retrieval.drawers import retrieve
    except ImportError:
        return {"hits": []}
    candidates = retrieve(artifact_hash, "tables", question)
    hits = [
        {"text": candidate.text, "ref": candidate.ref, "page": None}
        for candidate in candidates
    ]
    return {"hits": hits}


def _resolve(question: str, book: Ledger) -> QueryResult:
    series = execute(question, book)
    if series is not None:
        return series.result
    series = ask(question, book, read_script())
    if series is not None:
        return series.result
    return query(understand(question), book)


def _project_claim(claim: FinancialClaim) -> dict[str, Any]:
    return {
        "identity_key": claim.identity_key,
        "issuer": claim.issuer,
        "period": claim.period,
        "statement": claim.statement,
        "scope": claim.scope,
        "metric": claim.metric,
        "value": claim.value,
        "currency": claim.currency,
        "unit": claim.unit,
        "ledger_status": claim.ledger_status,
    }
