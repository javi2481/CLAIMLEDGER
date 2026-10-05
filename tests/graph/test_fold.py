"""Same-period documents share issuer, period, and statement. No claim."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from claimledger.graph.link import GraphSource, fold_documents
from claimledger.graph.schema import (
    FOR_PERIOD,
    ISSUED_BY,
    OF_STATEMENT,
    Document,
    Issuer,
    Period,
    Statement,
)
from claimledger.ingest.classify import DocumentClass, classify
from claimledger.ingest.types import StoredDocument

REPO_ROOT = Path(__file__).resolve().parents[2]

_PACKS = (
    (
        "2026-03-31",
        (
            ("BYMA_-_EEFF_31-03-2026_VF.pdf", "eeff", "hash-eeff-1t"),
            ("BYMA_Comunicado_de_Prensa-Resultados-1T26.pdf", "comunicado", "hash-press-1t"),
            ("Presentación_de_resultados_BYMA-1T26.pdf", "deck", "hash-deck-1t"),
        ),
    ),
    (
        "2026-06-30",
        (
            ("BYMA - EEFF 30-06-2026.pdf", "eeff", "hash-eeff-2t"),
            ("BYMA-Comunicado_de_Prensa-2T26.pdf", "comunicado", "hash-press-2t"),
            ("Presentacion_de_resultados_BYMA-2T26.pdf", "deck", "hash-deck-2t"),
        ),
    ),
)


def _source(filename: str, artifact_hash: str) -> tuple[DocumentClass, GraphSource]:
    classified = classify(
        Path(filename),
        StoredDocument(
            artifact_hash=artifact_hash,
            json_path=Path(artifact_hash),
            source_pdf=Path(filename),
        ),
    )
    return classified, GraphSource(
        filename=filename,
        classified=classified,
        artifact_hash=artifact_hash,
    )


def _edge_label(model: type, field_name: str) -> str:
    extra = model.model_fields[field_name].json_schema_extra
    assert isinstance(extra, dict)
    label = extra["edge_label"]
    assert isinstance(label, str)
    return label


def test_schema_is_four_entities_with_spec_edges() -> None:
    assert Document.model_config["graph_id_fields"] == ["artifact_hash"]
    assert Issuer.model_config["graph_id_fields"] == ["issuer"]
    assert Period.model_config["graph_id_fields"] == ["period"]
    assert Statement.model_config["graph_id_fields"] == ["statement"]
    assert _edge_label(Document, "issued_by") == ISSUED_BY == "ISSUED_BY"
    assert _edge_label(Document, "for_period") == FOR_PERIOD == "FOR_PERIOD"
    assert _edge_label(Document, "of_statement") == OF_STATEMENT == "OF_STATEMENT"


@pytest.mark.parametrize(("period", "rows"), _PACKS)
def test_same_period_pack_shares_issuer_period_statement_and_hash(
    period: str, rows: tuple[tuple[str, str, str], ...]
) -> None:
    classified_rows = [_source(filename, digest) for filename, _kind, digest in rows]
    graph = fold_documents([source for _classified, source in classified_rows])

    assert {issuer.issuer for issuer in graph.issuers} == {"BYMA"}
    assert len(graph.issuers) == 1
    assert {node.period for node in graph.periods} == {period}
    assert len(graph.periods) == 1
    assert {node.statement for node in graph.statements} == {"income_statement"}
    assert len(graph.statements) == 1
    assert [document.artifact_hash for document in graph.documents] == [
        digest for _filename, _kind, digest in rows
    ]
    assert [document.kind for document in graph.documents] == [
        kind for _filename, kind, _digest in rows
    ]

    issuer = graph.issuers[0]
    period_node = graph.periods[0]
    statement = graph.statements[0]
    for document in graph.documents:
        assert document.issued_by == issuer
        assert document.for_period == period_node
        assert document.of_statement == statement
        assert type(document).__name__ == "Document"


def test_both_quarters_fold_one_issuer_and_one_statement() -> None:
    sources = [
        source
        for _period, rows in _PACKS
        for filename, _kind, digest in rows
        for _classified, source in (_source(filename, digest),)
    ]
    graph = fold_documents(sources)

    assert {issuer.issuer for issuer in graph.issuers} == {"BYMA"}
    assert len(graph.issuers) == 1
    assert {node.period for node in graph.periods} == {"2026-03-31", "2026-06-30"}
    assert len(graph.periods) == 2
    assert {node.statement for node in graph.statements} == {"income_statement"}
    assert len(graph.statements) == 1
    assert len(graph.documents) == 6
    by_hash = {document.artifact_hash: document for document in graph.documents}
    assert by_hash["hash-eeff-1t"].for_period is not None
    assert by_hash["hash-eeff-1t"].for_period.period == "2026-03-31"
    assert by_hash["hash-press-2t"].for_period is not None
    assert by_hash["hash-press-2t"].for_period.period == "2026-06-30"
    assert by_hash["hash-eeff-1t"].issued_by == by_hash["hash-deck-2t"].issued_by
    assert by_hash["hash-eeff-1t"].of_statement == by_hash["hash-deck-2t"].of_statement
    assert by_hash["hash-eeff-1t"].for_period != by_hash["hash-deck-2t"].for_period


def test_fold_mints_no_financial_claim_and_does_not_call_extract_recipe() -> None:
    _classified, source = _source("BYMA_-_EEFF_31-03-2026_VF.pdf", "hash-eeff-1t")
    graph = fold_documents([source])
    nodes = (
        *graph.documents,
        *graph.issuers,
        *graph.periods,
        *graph.statements,
    )
    assert nodes
    assert {type(node).__name__ for node in nodes} == {
        "Document",
        "Issuer",
        "Period",
        "Statement",
    }

    for relative in (
        "src/claimledger/graph/schema.py",
        "src/claimledger/graph/link.py",
    ):
        tree = ast.parse((REPO_ROOT / relative).read_text(encoding="utf-8"))
        names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
        attrs = {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
        assert "extract_recipe" not in names | attrs
        assert "FinancialClaim" not in names
