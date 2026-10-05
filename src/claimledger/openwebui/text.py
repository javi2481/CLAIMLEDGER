"""Copy one ClaimCard into the assistant string."""

from __future__ import annotations

from claimledger.card.card import ClaimCard

_FICHA_ROW_MAX = 240


def _ficha_rows(rows: tuple[str, ...]) -> tuple[str, ...]:
    filled = tuple(row for row in rows if row)
    if len(filled) == 2 and all(len(row) <= _FICHA_ROW_MAX for row in filled):
        return filled
    return ()


def card_text(card: ClaimCard) -> str:
    parts: list[str] = []
    if card.seal:
        parts.append(card.seal)
    parts.extend(chip for chip in card.chips if chip)
    parts.extend(_ficha_rows(card.rows))
    parts.extend(value for value in card.values if value)
    if card.sentence:
        parts.append(card.sentence)
    if card.reason:
        parts.append(card.reason)
    return "\n".join(parts)
