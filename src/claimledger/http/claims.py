"""JSON map from a question body through understand then query. No Starlette."""

from __future__ import annotations

from claimledger.claim import FinancialClaim
from claimledger.evidence import FinancialEvidence
from claimledger.ledger import Ledger
from claimledger.lookup import understand
from claimledger.query import QueryResult, query

_CLAIM_FIELDS = (
    "issuer",
    "period",
    "statement",
    "scope",
    "metric",
    "value",
    "currency",
)


def claims_query(body: dict[str, object], ledger: Ledger) -> dict[str, object]:
    question = body.get("question")
    if not isinstance(question, str):
        return {}
    intent = understand(question)
    return _json(query(intent, ledger))


def _claim_fields(claim: FinancialClaim) -> dict[str, object]:
    return {name: getattr(claim, name) for name in _CLAIM_FIELDS}


def _evidence(items: tuple[FinancialEvidence, ...]) -> list[dict[str, object]]:
    return [
        {"document_id": item.document_id, "page": item.page, "text": item.text}
        for item in items
    ]


def _json(result: QueryResult) -> dict[str, object]:
    if result.status == "abstained":
        return {"status": "abstained", "reason": result.reason}
    if len(result.claims) == 2:
        claims: list[dict[str, object]] = []
        for claim in result.claims:
            item = _claim_fields(claim)
            item["evidence"] = _evidence(claim.evidence)
            claims.append(item)
        return {"status": result.status, "claims": claims}
    claim = result.claims[0]
    return {
        "status": result.status,
        "claim": _claim_fields(claim),
        "evidence": _evidence(claim.evidence),
    }
