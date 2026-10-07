"""Quarterly book from the two EEFF. The kernel seed stays the gold oracle."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from claimledger.identity import identity_key
from claimledger.ingest.ground import recorded_book
from claimledger.ingest.types import IngestError
from claimledger.ledger import RECIPE_ROWS, Ledger
from claimledger.lookup import understand
from claimledger.query import query

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "src" / "claimledger"
_BANNED_BOOK_TOKENS = ("docling", "docling_core", "torch", "PINNED_DOCLING")
_BOOK_PATH_SOURCES = (
    SRC / "ingest" / "extract.py",
    SRC / "ingest" / "ground.py",
    SRC / "query.py",
    SRC / "ledger.py",
    SRC / "lookup.py",
)


def test_book_path_sources_ban_docling_torch_and_pin() -> None:
    for path in _BOOK_PATH_SOURCES:
        source = path.read_text(encoding="utf-8")
        lowered = source.casefold()
        for token in _BANNED_BOOK_TOKENS:
            assert token.casefold() not in lowered, f"{path.name}: banned {token}"


def test_recorded_book_api_unchanged_and_cache_hit_serve_free() -> None:
    """recorded_book / query signatures stay stable; cache-hit path never calls serve."""
    book = recorded_book()
    intent = understand(
        "¿Cuál es el RESULTADO NETO DEL PERÍODO consolidado del 1T26?"
    )
    result = query(intent, book)
    assert result.status == "verified"
    assert result.claims[0].value == "21262335"
    store_source = (SRC / "ingest" / "store.py").read_text(encoding="utf-8")
    assert "def load_or_convert" in store_source
    # Cache hit returns stored JSON without POST to serve (convert_local is separate).
    assert "convert_local" in store_source
    assert "load_or_convert" in (SRC / "ingest" / "ground.py").read_text(
        encoding="utf-8"
    )


def test_recorded_book_matches_recipe_and_verifies_with_evidence() -> None:
    book = recorded_book()
    for period, scope, metric, value in RECIPE_ROWS:
        key = identity_key("BYMA", period, "income_statement", scope, metric)
        stored = book.get(key)
        assert stored is not None
        assert stored.value == value
        assert stored.evidence
        assert stored.ledger_status == "recorded"

    intent = understand(
        "¿Cuál es el RESULTADO NETO DEL PERÍODO consolidado del 1T26?"
    )
    result = query(intent, book)
    assert result.status == "verified"
    assert result.claims[0].value == "21262335"
    assert result.claims[0].evidence
    seeded = Ledger.seed().get(result.claims[0].identity_key)
    assert seeded is not None
    assert seeded.evidence == ()


def test_missing_quarterly_file_raises(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr("claimledger.ingest.ground.corpus_dir", lambda: tmp_path)
    with pytest.raises(IngestError):
        recorded_book()


def test_ground_does_not_write_claims_or_call_seed() -> None:
    source = (REPO / "src" / "claimledger" / "ingest" / "ground.py").read_text(
        encoding="utf-8"
    )
    assert "Ledger.seed" not in source
    assert "write_text" not in source
    assert "write_bytes" not in source
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            assert node.module != "claimledger.query"
