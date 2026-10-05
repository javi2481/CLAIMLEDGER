"""Same-id clashes stay on __conflicts__. Unknown aliases become doubt."""

from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest

from claimledger.graph.build import build, load

_build_module = importlib.import_module("claimledger.graph.build")
from claimledger.graph.link import GraphSource
from claimledger.ingest.classify import DocumentClass, classify
from claimledger.ingest.types import StoredDocument

_EDGE_LABELS = frozenset({"ISSUED_BY", "FOR_PERIOD", "OF_STATEMENT"})


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


def _use_graph_file(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    path = tmp_path / "artifacts" / "graph" / "graph.json"
    monkeypatch.setattr(_build_module, "graph_json_path", lambda: path)
    return path


def _built(sources: list[GraphSource], path: Path) -> dict:
    written = build(sources)
    assert written == path
    loaded = load()
    assert loaded == json.loads(path.read_text(encoding="utf-8"))
    return loaded


def _documents(payload: dict) -> dict[str, dict]:
    documents = {
        node["artifact_hash"]: node
        for node in payload["nodes"]
        if node.get("__class__") == "Document"
    }
    assert documents
    return documents


def _assert_no_conflicted_status(payload: dict) -> None:
    encoded = json.dumps(payload)
    assert "ledger_status" not in encoded
    assert "conflicted" not in encoded
    for node in payload["nodes"]:
        assert node.get("ledger_status") != "conflicted"
        assert "ledger_status" not in node


@pytest.mark.parametrize(
    ("rows", "kept_kind", "dropped_kind"),
    (
        (
            (
                ("BYMA_-_EEFF_31-03-2026_VF.pdf", "hash-clash"),
                ("BYMA_Comunicado_de_Prensa-Resultados-1T26.pdf", "hash-clash"),
            ),
            "eeff",
            "comunicado",
        ),
        (
            (
                ("Presentacion_de_resultados_BYMA-1T26.pdf", "hash-clash-deck"),
                ("BYMA_1T26_Transcripcion.pdf", "hash-clash-deck"),
            ),
            "deck",
            "transcript",
        ),
    ),
)
def test_kind_clash_stays_on_conflicts_and_not_ledger_status(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    rows: tuple[tuple[str, str], ...],
    kept_kind: str,
    dropped_kind: str,
) -> None:
    path = _use_graph_file(monkeypatch, tmp_path)
    classified_rows = [_source(filename, digest) for filename, digest in rows]
    digest = rows[0][1]
    payload = _built([source for _classified, source in classified_rows], path)

    documents = _documents(payload)
    assert list(documents) == [digest]
    document = documents[digest]
    assert document["kind"] == kept_kind
    assert document["__conflicts__"] == [
        {"field": "kind", "value": dropped_kind, "source": "graph-object-1"}
    ]
    assert document["__provenance__"] == {
        "document_id": digest,
        "source": rows[0][0],
    }
    _assert_no_conflicted_status(payload)
    assert {node["__class__"] for node in payload["nodes"]} <= {
        "Document",
        "Issuer",
        "Period",
        "Statement",
    }
    assert "FinancialClaim" not in {node["__class__"] for node in payload["nodes"]}


def test_unknown_alias_sets_doubt_and_mints_no_period(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = _use_graph_file(monkeypatch, tmp_path)
    filename = "BYMA_Comunicado_aliasdesconocido.pdf"
    classified, source = _source(filename, "hash-alias")
    assert classified.kind == "comunicado"
    assert classified.period is None

    payload = _built([source], path)

    assert classified.period is None
    documents = _documents(payload)
    document = documents["hash-alias"]
    assert document["doubt"] == "unrecognized period token: 'aliasdesconocido'"
    assert document["kind"] == "comunicado"
    assert document["__provenance__"] == {
        "document_id": "hash-alias",
        "source": filename,
    }
    assert "://" not in document["__provenance__"]["source"]
    assert {node["__class__"] for node in payload["nodes"]} == {
        "Document",
        "Issuer",
        "Statement",
    }
    assert not any(edge.get("label") == "FOR_PERIOD" for edge in payload["edges"])
    assert {edge["label"] for edge in payload["edges"]} <= _EDGE_LABELS
    _assert_no_conflicted_status(payload)


def test_year_end_memoria_doubt_stays_off_the_eeff_quarter(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = _use_graph_file(monkeypatch, tmp_path)
    memoria_classified, memoria = _source(
        "Memoria-BYMA-y-EEFF-al-31-12-2023.pdf", "hash-memoria"
    )
    _eeff_classified, eeff = _source("BYMA_-_EEFF_31-03-2026_VF.pdf", "hash-eeff-1t")
    assert memoria_classified.kind == "memoria"
    assert memoria_classified.period is None

    payload = _built([memoria, eeff], path)

    assert memoria_classified.period is None
    documents = _documents(payload)
    assert documents["hash-memoria"]["doubt"] == "unrecognized period token: '2023'"
    assert documents["hash-memoria"]["kind"] == "memoria"
    assert documents["hash-eeff-1t"]["doubt"] is None
    assert documents["hash-eeff-1t"]["__provenance__"]["document_id"] == "hash-eeff-1t"
    assert {node["period"] for node in payload["nodes"] if node["__class__"] == "Period"} == {
        "2026-03-31"
    }
    period_ids = {
        node["id"] for node in payload["nodes"] if node.get("__class__") == "Period"
    }
    memoria_id = documents["hash-memoria"]["id"]
    eeff_id = documents["hash-eeff-1t"]["id"]
    assert not any(
        edge["source"] == memoria_id
        and edge["target"] in period_ids
        and edge["label"] == "FOR_PERIOD"
        for edge in payload["edges"]
    )
    assert any(
        edge["source"] == eeff_id
        and edge["target"] in period_ids
        and edge["label"] == "FOR_PERIOD"
        for edge in payload["edges"]
    )


def test_resolved_transcript_links_period_without_doubt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = _use_graph_file(monkeypatch, tmp_path)
    filename = "BYMA_2T26_Transcripcion_Resultados_ES.pdf"
    classified, source = _source(filename, "hash-transcript-2t")
    assert classified.kind == "transcript"
    assert classified.period is None

    payload = _built([source], path)

    assert classified.period is None
    documents = _documents(payload)
    document = documents["hash-transcript-2t"]
    assert document["doubt"] is None
    assert document["kind"] == "transcript"
    assert document["__provenance__"] == {
        "document_id": "hash-transcript-2t",
        "source": filename,
    }
    assert {node["__class__"] for node in payload["nodes"]} == {
        "Document",
        "Issuer",
        "Period",
    }
    assert {node["period"] for node in payload["nodes"] if node["__class__"] == "Period"} == {
        "2026-06-30"
    }
    assert any(edge.get("label") == "FOR_PERIOD" for edge in payload["edges"])
    assert not any(edge.get("label") == "OF_STATEMENT" for edge in payload["edges"])
    assert "FinancialClaim" not in {node["__class__"] for node in payload["nodes"]}
