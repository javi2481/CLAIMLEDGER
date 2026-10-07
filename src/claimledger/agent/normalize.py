"""Normalize financial digit forms; exempt dates, pages, period labels."""

from __future__ import annotations

import re

_DATE = re.compile(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b")
_PAGE = re.compile(r"\b(?:p[aá]gina)\s+\d+\b", re.IGNORECASE)
_PERIOD = re.compile(r"\b\d[QTqt]\d{2}\b")
_AMOUNT = re.compile(
    r"\$?\s*\d{1,3}(?:[.\s,]\d{3})+(?!\d)"
    r"|\$\s*\d+"
    r"|\b\d{5,}\b"
)


def normalize_amount(raw: str) -> str | None:
    text = str(raw).strip().replace("$", "").strip()
    if not text:
        return None
    negative = text.startswith("-")
    if negative:
        text = text[1:].strip()
    if not re.fullmatch(r"\d{1,3}(?:[.\s,]\d{3})+|\d+", text):
        # Allow internal spaces only as thousand separators already covered;
        # also accept pure digit runs after stripping separators below.
        compact = re.sub(r"[.\s,]", "", text)
        if compact.isdigit():
            return f"-{compact}" if negative else compact
        return None
    digits = re.sub(r"[.\s,]", "", text)
    if not digits.isdigit():
        return None
    return f"-{digits}" if negative else digits


def extract_financial_values(prose: str) -> list[str]:
    masked = _DATE.sub(" ", prose)
    masked = _PAGE.sub(" ", masked)
    masked = _PERIOD.sub(" ", masked)
    found: list[str] = []
    seen: set[str] = set()
    for match in _AMOUNT.finditer(masked):
        canonical = normalize_amount(match.group(0))
        if canonical is None or canonical in seen:
            continue
        # Skip tiny leftovers that look like page/period scraps (1–2 digits)
        if len(canonical.lstrip("-")) <= 2:
            continue
        seen.add(canonical)
        found.append(canonical)
    return found
