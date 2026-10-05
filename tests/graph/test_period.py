"""Period edges from classify or filename tokens. No claim on transcript."""

from __future__ import annotations

from pathlib import Path

import pytest

from claimledger.graph.link import GraphSource, fold_documents
from claimledger.ingest.classify import DocumentClass, classify
from claimledger.ingest.types import StoredDocument

_MEMORIAS = (
    "Memoria-BYMA-y-EEFF-al-31-12-2023.pdf",
    "BYMA-MEMORIA_2024_y_EEFF_31-12-2024.pdf",
    "BYMA-MEMORIA_2025.pdf",
)
_NON_EEFF = (
    ("BYMA_Comunicado_de_Prensa-Resultados-1T26.pdf", "hash-press-1t", "2026-03-31"),
    ("BYMA-Comunicado_de_Prensa-2T26.pdf", "hash-press-2t", "2026-06-30"),
    ("Presentación_de_resultados_BYMA-1T26.pdf", "hash-deck-1t", "2026-03-31"),
    ("Presentacion_de_resultados_BYMA-2T26.pdf", "hash-deck-2t", "2026-06-30"),
    ("BYMA_2T26_Transcripcion_Resultados_ES.pdf", "hash-transcript-2t", "2026-06-30"),
    ("BYMA_1T26_Transcripcion.pdf", "hash-transcript-1t", "2026-03-31"),
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


def test_year_end_memorias_have_no_quarterly_period() -> None:
    classified_rows = [
        _source(filename, f"hash-memoria-{index}")
        for index, filename in enumerate(_MEMORIAS, start=1)
    ]
    for classified, _source_row in classified_rows:
        assert classified.kind == "memoria"
        assert classified.period is None

    graph = fold_documents([source for _classified, source in classified_rows])

    assert graph.periods == ()
    assert graph.statements == ()
    assert {issuer.issuer for issuer in graph.issuers} == {"BYMA"}
    assert len(graph.issuers) == 1
    assert [document.artifact_hash for document in graph.documents] == [
        "hash-memoria-1",
        "hash-memoria-2",
        "hash-memoria-3",
    ]
    for document, (classified, _source_row) in zip(graph.documents, classified_rows, strict=True):
        assert document.kind == "memoria"
        assert document.for_period is None
        assert document.of_statement is None
        assert document.issued_by.issuer == "BYMA"
        assert classified.period is None


def test_memoria_does_not_attach_when_a_quarter_is_also_present() -> None:
    _eeff, eeff = _source("BYMA_-_EEFF_31-03-2026_VF.pdf", "hash-eeff-1t")
    memoria, memoria_source = _source(_MEMORIAS[1], "hash-memoria-2")
    graph = fold_documents([eeff, memoria_source])
    by_hash = {document.artifact_hash: document for document in graph.documents}

    assert by_hash["hash-eeff-1t"].for_period is not None
    assert by_hash["hash-eeff-1t"].for_period.period == "2026-03-31"
    assert by_hash["hash-memoria-2"].for_period is None
    assert {node.period for node in graph.periods} == {"2026-03-31"}
    assert memoria.period is None


@pytest.mark.parametrize(
    ("filename", "digest", "period"),
    (
        ("BYMA_2T26_Transcripcion_Resultados_ES.pdf", "hash-transcript-2t", "2026-06-30"),
        ("BYMA_1T26_Transcripcion.pdf", "hash-transcript-1t", "2026-03-31"),
    ),
)
def test_transcript_may_link_period_and_mints_no_claim(
    filename: str, digest: str, period: str
) -> None:
    classified, source = _source(filename, digest)
    assert classified.kind == "transcript"
    assert classified.period is None

    graph = fold_documents([source])

    assert len(graph.documents) == 1
    document = graph.documents[0]
    assert document.artifact_hash == digest
    assert document.kind == "transcript"
    assert document.for_period is not None
    assert document.for_period.period == period
    assert document.of_statement is None
    assert graph.statements == ()
    assert {type(node).__name__ for node in (*graph.documents, *graph.issuers, *graph.periods)} == {
        "Document",
        "Issuer",
        "Period",
    }
    assert classified.period is None


@pytest.mark.parametrize(("filename", "digest", "period"), _NON_EEFF)
def test_non_eeff_classify_period_stays_none_while_graph_links_token(
    filename: str, digest: str, period: str
) -> None:
    classified, source = _source(filename, digest)
    assert classified.period is None
    assert classified.kind != "eeff"

    graph = fold_documents([source])

    assert classified.period is None
    assert graph.documents[0].artifact_hash == digest
    assert graph.documents[0].for_period is not None
    assert graph.documents[0].for_period.period == period


def test_eeff_uses_document_class_period_not_split_filename() -> None:
    filename = "BYMA_-_EEFF_31-03-2026_VF.pdf"
    classified, source = _source(filename, "hash-eeff-1t")
    assert classified == DocumentClass(kind="eeff", issuer="BYMA", period="2026-03-31")

    graph = fold_documents([source])

    assert graph.documents[0].for_period is not None
    assert graph.documents[0].for_period.period == "2026-03-31"
    assert graph.documents[0].of_statement is not None
    assert graph.documents[0].of_statement.statement == "income_statement"
    assert classified.period == "2026-03-31"


def test_glued_period_token_does_not_link() -> None:
    classified, source = _source("BYMA_Comunicado_1T26extra.pdf", "hash-glued")
    assert classified.kind == "comunicado"
    assert classified.period is None

    graph = fold_documents([source])

    assert graph.periods == ()
    assert graph.documents[0].for_period is None
    assert classified.period is None
