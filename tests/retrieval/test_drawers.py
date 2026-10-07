"""Two retrieval drawers. Candidates only; one drawer per call."""

from __future__ import annotations

import hashlib
import json
from dataclasses import FrozenInstanceError, fields
from pathlib import Path
from types import SimpleNamespace

import pytest

import claimledger.ingest.store as ingest_store
import claimledger.ledger as ledger_mod
import claimledger.query as query_mod
from claimledger.claim import FinancialClaim


CONSOLIDATED_ROW = "RESULTADO NETO DEL PERÍODO 21.262.335"
PARENT_ROW = "Resultado neto atribuible a la sociedad controlante 21.259.769"
SECTION_HEADER = "Estado de Resultados"
NARRATIVE = "política contable de reconocimiento de ingresos"
OTHER_TABLE = "Ingresos por servicios 100"
OTHER_NOTE = "nota al pie del estado"


def _canonical_json_bytes(payload: dict) -> bytes:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _use_artifacts(monkeypatch: pytest.MonkeyPatch, root: Path) -> None:
    monkeypatch.setattr(ingest_store, "artifacts_dir", lambda: root)


def _write_artifact(root: Path, payload: dict) -> str:
    raw = _canonical_json_bytes(payload)
    digest = _sha256_hex(raw)
    (root / f"{digest}.json").write_bytes(raw)
    return digest


def _node(text: str, label: str, ref: str) -> dict[str, str]:
    return {"text": text, "label": label, "ref": ref}


def _neighbor_payload() -> dict:
    return {
        "parsed_nodes": [
            _node(SECTION_HEADER, "section_header", "#/texts/0"),
            _node(CONSOLIDATED_ROW, "table", "#/tables/1"),
            _node(PARENT_ROW, "table", "#/tables/1"),
            _node(NARRATIVE, "text", "#/texts/4"),
        ]
    }


def _other_payload() -> dict:
    return {
        "parsed_nodes": [
            _node(OTHER_TABLE, "table", "#/tables/2"),
            _node(OTHER_NOTE, "text", "#/texts/9"),
        ]
    }


def _parsed_nodes(payload: dict) -> list[SimpleNamespace]:
    return [
        SimpleNamespace(
            text=item["text"],
            metadata={"doc_items": [{"self_ref": item["ref"], "label": item["label"]}]},
        )
        for item in payload["parsed_nodes"]
    ]


def _forbid_side_effects(monkeypatch: pytest.MonkeyPatch) -> dict[str, int]:
    calls = {
        "load_or_convert": 0,
        "convert_pdf": 0,
        "convert_local": 0,
        "urlopen": 0,
        "query": 0,
        "upsert": 0,
    }

    def _count(key: str):
        def _inner(*_args: object, **_kwargs: object) -> None:
            calls[key] += 1

        return _inner

    monkeypatch.setattr(ingest_store, "load_or_convert", _count("load_or_convert"))
    monkeypatch.setattr(
        "claimledger.ingest.parse.convert_pdf", _count("convert_pdf")
    )
    monkeypatch.setattr(
        "claimledger.ingest.parse.convert_local", _count("convert_local")
    )
    monkeypatch.setattr(
        "claimledger.ingest.store.convert_local", _count("convert_local")
    )
    monkeypatch.setattr("urllib.request.urlopen", _count("urlopen"))
    monkeypatch.setattr(query_mod, "query", _count("query"))
    monkeypatch.setattr(ledger_mod.Ledger, "upsert", _count("upsert"))
    return calls


def _install_parsed_reader(
    monkeypatch: pytest.MonkeyPatch,
) -> list[str]:
    from claimledger.retrieval import read as read_mod

    seen: list[str] = []

    def fake_read(artifact_hash: str) -> list[SimpleNamespace]:
        seen.append(artifact_hash)
        return _parsed_nodes(ingest_store.load(artifact_hash))

    monkeypatch.setattr(read_mod, "read_hashed_json", fake_read)
    return seen


def _prepare(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, payload: dict
) -> tuple[str, dict[str, int], list[str]]:
    artifacts = tmp_path / "docling"
    artifacts.mkdir()
    _use_artifacts(monkeypatch, artifacts)
    digest = _write_artifact(artifacts, payload)
    calls = _forbid_side_effects(monkeypatch)
    seen = _install_parsed_reader(monkeypatch)
    return digest, calls, seen


def test_tables_call_returns_no_narrative_nodes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from claimledger.retrieval.drawers import retrieve

    digest, calls, seen = _prepare(tmp_path, monkeypatch, _neighbor_payload())

    found = retrieve(digest, "tables", "resultado neto")

    assert seen == [digest]
    assert [item.text for item in found] == [CONSOLIDATED_ROW, PARENT_ROW]
    assert [item.drawer for item in found] == ["tables", "tables"]
    assert SECTION_HEADER not in [item.text for item in found]
    assert NARRATIVE not in [item.text for item in found]
    assert calls["query"] == 0
    assert calls["upsert"] == 0
    assert calls["load_or_convert"] == 0
    assert calls["convert_pdf"] == 0
    assert calls["convert_local"] == 0
    assert calls["urlopen"] == 0


def test_narrative_call_returns_no_table_nodes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from claimledger.retrieval.drawers import retrieve

    digest, calls, seen = _prepare(tmp_path, monkeypatch, _neighbor_payload())

    found = retrieve(digest, "narrative", "política contable")

    assert seen == [digest]
    assert [item.text for item in found] == [SECTION_HEADER, NARRATIVE]
    assert [item.drawer for item in found] == ["narrative", "narrative"]
    assert [item.ref for item in found] == ["#/texts/0", "#/texts/4"]
    assert CONSOLIDATED_ROW not in [item.text for item in found]
    assert PARENT_ROW not in [item.text for item in found]
    assert calls["query"] == 0
    assert calls["upsert"] == 0


def test_both_neighbor_rows_are_table_candidates(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from claimledger.retrieval.drawers import retrieve

    digest, _calls, _seen = _prepare(tmp_path, monkeypatch, _neighbor_payload())

    found = retrieve(digest, "tables", "¿cuál fila elijo?")

    assert len(found) == 2
    assert found[0].text == CONSOLIDATED_ROW
    assert found[1].text == PARENT_ROW
    assert found[0].ref == "#/tables/1"
    assert found[1].ref == "#/tables/1"
    assert found[0] != found[1]


def test_candidate_has_no_claim_status(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from claimledger.retrieval.drawers import Candidate, retrieve

    digest, calls, _seen = _prepare(tmp_path, monkeypatch, _neighbor_payload())

    found = retrieve(digest, "tables", "resultado neto")
    candidate = found[0]

    assert isinstance(found, tuple)
    assert isinstance(candidate, Candidate)
    assert [field.name for field in fields(candidate)] == ["drawer", "text", "ref"]
    assert not isinstance(candidate, FinancialClaim)
    assert "verified" not in candidate.__dict__
    assert "abstained" not in candidate.__dict__
    with pytest.raises(FrozenInstanceError):
        candidate.drawer = "narrative"  # type: ignore[misc]
    assert candidate.drawer == "tables"
    assert calls["query"] == 0
    assert calls["upsert"] == 0


def test_question_does_not_choose_between_neighbor_rows(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from claimledger.retrieval.drawers import retrieve

    digest, _calls, seen = _prepare(tmp_path, monkeypatch, _neighbor_payload())

    consolidated = retrieve(digest, "tables", "resultado neto consolidado")
    parent = retrieve(digest, "tables", "resultado atribuible a la controlante")
    blank = retrieve(digest, "tables", "")

    assert consolidated == parent == blank
    assert [item.text for item in consolidated] == [CONSOLIDATED_ROW, PARENT_ROW]
    assert seen == [digest, digest, digest]


def test_second_artifact_splits_its_own_nodes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from claimledger.retrieval.drawers import retrieve

    artifacts = tmp_path / "docling"
    artifacts.mkdir()
    _use_artifacts(monkeypatch, artifacts)
    first = _write_artifact(artifacts, _neighbor_payload())
    second = _write_artifact(artifacts, _other_payload())
    calls = _forbid_side_effects(monkeypatch)
    seen = _install_parsed_reader(monkeypatch)

    tables = retrieve(second, "tables", "ingresos")
    narrative = retrieve(second, "narrative", "nota")

    assert first != second
    assert seen == [second, second]
    assert [item.text for item in tables] == [OTHER_TABLE]
    assert [item.ref for item in tables] == ["#/tables/2"]
    assert [item.text for item in narrative] == [OTHER_NOTE]
    assert [item.ref for item in narrative] == ["#/texts/9"]
    assert calls["query"] == 0
    assert calls["upsert"] == 0


def test_naming_both_drawers_or_unknown_drawer_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from claimledger.retrieval.drawers import retrieve

    digest, calls, seen = _prepare(tmp_path, monkeypatch, _neighbor_payload())

    with pytest.raises(ValueError, match="one drawer"):
        retrieve(digest, "tables,narrative", "resultado neto")
    with pytest.raises(ValueError, match="one drawer"):
        retrieve(digest, ("tables", "narrative"), "resultado neto")
    with pytest.raises(ValueError, match="one drawer"):
        retrieve(digest, "pictures", "resultado neto")

    assert seen == []
    assert calls["query"] == 0
    assert calls["upsert"] == 0
    assert calls["load_or_convert"] == 0
    assert calls["urlopen"] == 0
