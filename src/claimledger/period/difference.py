"""Later minus earlier on a verified pair. Plain string, never upserted."""

from __future__ import annotations

from claimledger.query import QueryResult

_GATE_FIELDS = ("issuer", "statement", "scope", "metric", "currency", "unit")


def difference(result: QueryResult) -> str | None:
    if result.status != "verified" or len(result.claims) != 2:
        return None
    first, second = result.claims
    if any(
        getattr(first, field) != getattr(second, field) for field in _GATE_FIELDS
    ):
        return None
    if first.period == second.period:
        return None
    if first.ledger_status != "recorded" or second.ledger_status != "recorded":
        return None
    earlier, later = sorted(result.claims, key=lambda claim: claim.period)
    return str(int(later.value) - int(earlier.value))
