"""In-memory book from the two quarterly statements.

Gap: no pinned API joins two hashed Docling documents into the ledger
query reads. Docling parses. extract_recipe maps the recipe. Ledger.upsert
records. This module is that join. It does not write a claim cache.
"""

from __future__ import annotations

from pathlib import Path

from claimledger.ingest.classify import classify
from claimledger.ingest.extract import extract_recipe
from claimledger.ingest.store import load_or_convert
from claimledger.ingest.types import IngestError
from claimledger.ledger import Ledger

_QUARTERLY_EEFF = (
    "BYMA_-_EEFF_31-03-2026_VF.pdf",
    "BYMA - EEFF 30-06-2026.pdf",
)


def corpus_dir() -> Path:
    return Path(__file__).resolve().parents[3] / "docs" / "archivos_muestra"


def recorded_book() -> Ledger:
    root = corpus_dir()
    ledger = Ledger()
    for name in _QUARTERLY_EEFF:
        pdf = root / name
        if not pdf.is_file():
            raise IngestError(f"missing quarterly EEFF {name}")
        stored = load_or_convert(pdf)
        classified = classify(pdf, stored)
        for claim in extract_recipe(stored, classified):
            ledger.upsert(claim)
    return ledger
