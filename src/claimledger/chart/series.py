"""Copy a verified series into a Mermaid fence. Does not verify or subtract."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from claimledger.query import QueryResult

ChartStatus = Literal["verified", "partial"]

_PERIOD_LABEL = {"2026-03-31": "1T26", "2026-06-30": "2T26"}
_SCOPE_TITLE = {"consolidated": "consolidado", "parent_attributable": "controlante"}
_METRIC_TITLE = {"net_income": "Resultado neto"}


@dataclass(frozen=True)
class ChartPoint:
    label: str
    value: str | None
    identity: str | None


@dataclass(frozen=True)
class ChartSpec:
    title: str
    points: tuple[ChartPoint, ...]
    status: ChartStatus


def series_spec(result: QueryResult, gaps: tuple[str, ...] = ()) -> ChartSpec | None:
    claims = result.claims
    if result.status != "verified" or len(claims) < 2:
        return None
    first = claims[0]
    if any(claim.ledger_status != "recorded" for claim in claims):
        return None
    if any(_same_series(first, claim) is False for claim in claims):
        return None
    if len({claim.period for claim in claims}) != len(claims):
        return None

    by_period = {claim.period: claim for claim in claims}
    points: list[ChartPoint] = []
    for period in sorted(set(by_period) | set(gaps)):
        claim = by_period.get(period)
        if claim is None:
            points.append(ChartPoint(_PERIOD_LABEL.get(period, period), None, None))
        else:
            points.append(
                ChartPoint(
                    _PERIOD_LABEL.get(period, period),
                    claim.value,
                    claim.identity_key,
                )
            )
    if not any(point.value is not None for point in points):
        return None
    status: ChartStatus = (
        "verified" if all(point.value is not None for point in points) else "partial"
    )
    metric = _METRIC_TITLE.get(first.metric, first.metric)
    scope = _SCOPE_TITLE.get(first.scope, first.scope)
    return ChartSpec(f"{metric} {scope}", tuple(points), status)


def draw(spec: ChartSpec | None) -> str:
    if spec is None:
        return ""
    filled = [point for point in spec.points if point.value is not None]
    holes = [point for point in spec.points if point.value is None]
    labels = ", ".join(f'"{point.label}"' for point in filled)
    bars = ", ".join(point.value for point in filled if point.value is not None)
    low = min(filled, key=lambda point: int(point.value or "0"))
    high = max(filled, key=lambda point: int(point.value or "0"))
    lines = [
        "```mermaid",
        "xychart-beta",
        f'    title "{spec.title}"',
        f"    x-axis [{labels}]",
        f'    y-axis "ARS" {low.value} --> {high.value}',
        f"    bar [{bars}]",
        "```",
    ]
    lines.extend(point.identity for point in filled if point.identity)
    lines.extend(f"Hueco: {point.label}" for point in holes)
    return "\n".join(lines)


def _same_series(left: object, right: object) -> bool:
    fields = ("issuer", "statement", "scope", "metric", "currency", "unit")
    return all(getattr(left, field) == getattr(right, field) for field in fields)
