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
