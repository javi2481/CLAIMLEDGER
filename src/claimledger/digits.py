"""ARS printed amounts: thousand dots, optional parentheses. Not an entity."""

from __future__ import annotations

from typing import Any


def digits_ars(value: Any) -> str | None:
    """Keep thousand-dot digits. 21.262.335 → 21262335. Empty/None → None."""
    if value is None:
        return None
    text = str(value).strip().replace(" ", "")
    if not text:
        return None
    if "," in text or text.casefold().endswith("m"):
        return None
    if text.count(".") >= 1:
        parts = text.split(".")
        if all(part.isdigit() for part in parts) and all(
            len(part) == 3 for part in parts[1:]
        ):
            return "".join(parts)
    digits = "".join(ch for ch in text if ch.isdigit())
    return digits or None


def signed_ars(value: Any) -> str | None:
    """Parentheses mean negative. (14.950.948) → -14950948."""
    if value is None:
        return None
    text = str(value).strip().replace(" ", "")
    if not text:
        return None
    negative = text.startswith("(") and text.endswith(")")
    inner = text[1:-1] if negative else text
    digits = digits_ars(inner)
    if not digits:
        return None
    return f"-{digits}" if negative else digits
