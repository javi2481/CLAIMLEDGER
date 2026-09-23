"""Five-field identity, fold, period tokens, and Claimprint alias rewrite."""

from __future__ import annotations

import json
import unicodedata
from functools import lru_cache
from pathlib import Path

PERIOD_1T26 = "2026-03-31"
PERIOD_2T26 = "2026-06-30"

_TOKENS_1T26 = frozenset(
    {
        "1t26",
        "1t 26",
        "marzo",
        "2026-03-31",
        "31 de marzo",
        "primer trimestre",
    }
)
_TOKENS_2T26 = frozenset(
    {
        "2t26",
        "2t 26",
        "junio",
        "2026-06-30",
        "30 de junio",
        "segundo trimestre",
    }
)

_ALIASES_PATH = Path(__file__).resolve().parents[2] / "evals" / "aliases.json"


def identity_key(
    issuer: str, period: str, statement: str, scope: str, metric: str
) -> str:
    return f"{issuer}|{period}|{statement}|{scope}|{metric}"


def fold(text: str) -> str:
    nfd = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in nfd if unicodedata.category(ch) != "Mn").casefold()


def normalize_period(text: str) -> str:
    token = fold(text)
    if token in _TOKENS_1T26:
        return PERIOD_1T26
    if token in _TOKENS_2T26:
        return PERIOD_2T26
    raise ValueError(f"unrecognized period token: {text!r}")


@lru_cache(maxsize=1)
def _alias_table() -> dict[str, tuple[str, str, str]]:
    rows = json.loads(_ALIASES_PATH.read_text(encoding="utf-8"))
    return {
        row["v1"]: (row["statement"], row["scope"], row["metric"]) for row in rows
    }


def apply_alias(v1: str) -> tuple[str, str, str]:
    return _alias_table()[v1]
