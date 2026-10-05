"""Filename and pack classification. Does not extract claims or mint identities."""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from claimledger.ingest.types import IngestError, StoredDocument

Kind = Literal["eeff", "comunicado", "deck", "memoria", "transcript"]

_ISSUER = "BYMA"
_EEFF_PERIODS = {
    "31-03-2026": "2026-03-31",
    "30-06-2026": "2026-06-30",
}


@dataclass(frozen=True)
class DocumentClass:
    kind: Kind
    issuer: str
    period: str | None


def _fold(text: str) -> str:
    nfd = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in nfd if unicodedata.category(ch) != "Mn").casefold()


# Memoria before EEFF: year-end packs put both tokens in the filename.
_KIND_RULES: tuple[tuple[str, Kind], ...] = (
    ("memoria", "memoria"),
    ("comunicado", "comunicado"),
    ("presentacion", "deck"),
    ("transcripcion", "transcript"),
    ("eeff", "eeff"),
)


def _kind(folded: str) -> Kind:
    for token, kind in _KIND_RULES:
        if token in folded:
            return kind
    raise IngestError(f"unclassified pdf name: {folded}")


def _eeff_period(name: str) -> str:
    for token, period in _EEFF_PERIODS.items():
        if token in name:
            return period
    raise IngestError(f"quarterly EEFF has no pack period: {name}")


def classify(pdf: Path, stored: StoredDocument) -> DocumentClass:
    if not isinstance(pdf, Path) or not isinstance(stored, StoredDocument):
        raise IngestError("classify expects a local pdf Path and a StoredDocument")
    if not stored.artifact_hash:
        raise IngestError("stored document has no artifact hash")
    folded = _fold(pdf.name)
    if "byma" not in folded:
        raise IngestError("issuer is not BYMA")
    kind = _kind(folded)
    period = _eeff_period(pdf.name) if kind == "eeff" else None
    return DocumentClass(kind=kind, issuer=_ISSUER, period=period)
