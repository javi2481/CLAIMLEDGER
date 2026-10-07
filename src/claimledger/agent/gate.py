"""Host authorization gate over LLM prose."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from claimledger.agent.normalize import extract_financial_values
from claimledger.agent.template import ABSTENTION_TEMPLATE


@dataclass(frozen=True)
class GateResult:
    allowed: bool
    text: str


def gate_prose(
    prose: str,
    authorized_values: list[str] | tuple[str, ...],
    *,
    regenerate: Callable[[], str] | None = None,
) -> GateResult:
    if not authorized_values:
        return GateResult(allowed=False, text=ABSTENTION_TEMPLATE)

    if _prose_authorized(prose, authorized_values):
        return GateResult(allowed=True, text=prose)

    if regenerate is not None:
        second = regenerate()
        if _prose_authorized(second, authorized_values):
            return GateResult(allowed=True, text=second)

    return GateResult(allowed=False, text=ABSTENTION_TEMPLATE)


def _prose_authorized(
    prose: str,
    authorized_values: list[str] | tuple[str, ...],
) -> bool:
    found = extract_financial_values(prose)
    allowed = set(authorized_values)
    return all(value in allowed for value in found)
