"""Hashed Docling JSON reader. Local artifact only; no PDF and no URL."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

import claimledger.ingest.store as ingest_store
from claimledger.ingest.types import IngestError


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


def _track_load(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    seen: list[str] = []
    original = ingest_store.load

    def wrapped(artifact_hash: str) -> dict:
        seen.append(artifact_hash)
        return original(artifact_hash)

    monkeypatch.setattr(ingest_store, "load", wrapped)
    return seen


def _write_artifact(root: Path, payload: dict) -> tuple[str, Path, str]:
    raw = _canonical_json_bytes(payload)
    digest = _sha256_hex(raw)
    path = root / f"{digest}.json"
    path.write_bytes(raw)
    return digest, path, raw.decode("utf-8")


def _forbid_conversion_and_url(monkeypatch: pytest.MonkeyPatch) -> dict[str, int]:
    calls = {
        "load_or_convert": 0,
        "convert_pdf": 0,
        "convert_local": 0,
        "urlopen": 0,
    }

    def _count(key: str):
        def _inner(*_args: object, **_kwargs: object) -> None:
            calls[key] += 1

        return _inner

    monkeypatch.setattr(ingest_store, "load_or_convert", _count("load_or_convert"))
    monkeypatch.setattr(
        "claimledger.ingest.parse.convert_pdf",
        _count("convert_pdf"),
    )
    monkeypatch.setattr(
        "claimledger.ingest.parse.convert_local",
        _count("convert_local"),
    )
    monkeypatch.setattr(
        "claimledger.ingest.store.convert_local",
        _count("convert_local"),
    )
    monkeypatch.setattr("urllib.request.urlopen", _count("urlopen"))
    return calls


def _install_reader_doubles(monkeypatch: pytest.MonkeyPatch) -> dict[str, list]:
    import llama_index.node_parser.docling as parser_mod
    import llama_index.readers.docling as reader_mod

    state: dict[str, list] = {
        "export_types": [],
        "paths": [],
        "parser_texts": [],
    }

    class FakeReader:
        def __init__(self, export_type: str = "markdown", **_kwargs: object) -> None:
            self.export_type = export_type
            state["export_types"].append(export_type)

        def load_data(self, file_path: str | Path, **_kwargs: object) -> list:
            path = Path(file_path)
            state["paths"].append(path)
            text = path.read_text(encoding="utf-8")
            return [SimpleNamespace(text=text)]

    class FakeParser:
        def get_nodes_from_documents(self, documents: list) -> list:
            texts = [document.text for document in documents]
            state["parser_texts"].append(texts)
            return [SimpleNamespace(text=text) for text in texts]

    monkeypatch.setattr(reader_mod, "DoclingReader", FakeReader)
    monkeypatch.setattr(parser_mod, "DoclingNodeParser", FakeParser)
    return state


def test_stored_json_reader_uses_json_export_on_local_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from claimledger.retrieval.read import read_hashed_json

    artifacts = tmp_path / "docling"
    artifacts.mkdir()
    payload = {"schema_name": "DoclingDocument", "name": "byma-1t26", "pages": [1]}
    digest, path, text = _write_artifact(artifacts, payload)
    _use_artifacts(monkeypatch, artifacts)
    loaded_hashes = _track_load(monkeypatch)
    calls = _forbid_conversion_and_url(monkeypatch)
    state = _install_reader_doubles(monkeypatch)

    loaded = ingest_store.load(digest)
    nodes = read_hashed_json(digest)

    assert loaded_hashes == [digest, digest]
    assert loaded == payload
    assert nodes[0].text == text
    assert state["export_types"] == ["json"]
    assert state["paths"] == [path]
    assert state["parser_texts"] == [[text]]
    assert path.is_file()
    assert path.parent == artifacts
    assert calls == {
        "load_or_convert": 0,
        "convert_pdf": 0,
        "convert_local": 0,
        "urlopen": 0,
    }


def test_second_artifact_is_read_from_its_own_local_json(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from claimledger.retrieval.read import read_hashed_json

    artifacts = tmp_path / "docling"
    artifacts.mkdir()
    first = {"schema_name": "DoclingDocument", "name": "eeff-a"}
    second = {"schema_name": "DoclingDocument", "name": "eeff-b", "n": 2}
    digest_a, path_a, text_a = _write_artifact(artifacts, first)
    digest_b, path_b, text_b = _write_artifact(artifacts, second)
    _use_artifacts(monkeypatch, artifacts)
    loaded_hashes = _track_load(monkeypatch)
    calls = _forbid_conversion_and_url(monkeypatch)
    state = _install_reader_doubles(monkeypatch)

    nodes_a = read_hashed_json(digest_a)
    nodes_b = read_hashed_json(digest_b)

    assert loaded_hashes == [digest_a, digest_b]
    assert digest_a != digest_b
    assert nodes_a[0].text == text_a
    assert nodes_b[0].text == text_b
    assert nodes_a[0].text != nodes_b[0].text
    assert state["export_types"] == ["json", "json"]
    assert state["paths"] == [path_a, path_b]
    assert state["parser_texts"] == [[text_a], [text_b]]
    assert calls == {
        "load_or_convert": 0,
        "convert_pdf": 0,
        "convert_local": 0,
        "urlopen": 0,
    }


def test_missing_artifact_raises_without_convert_or_url(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from claimledger.retrieval.read import read_hashed_json

    artifacts = tmp_path / "docling"
    artifacts.mkdir()
    _use_artifacts(monkeypatch, artifacts)
    loaded_hashes = _track_load(monkeypatch)
    calls = _forbid_conversion_and_url(monkeypatch)
    state = _install_reader_doubles(monkeypatch)
    missing = "a" * 64

    with pytest.raises(IngestError, match="missing artifact"):
        read_hashed_json(missing)

    assert loaded_hashes == [missing]

    assert state["export_types"] == []
    assert state["paths"] == []
    assert state["parser_texts"] == []
    assert calls == {
        "load_or_convert": 0,
        "convert_pdf": 0,
        "convert_local": 0,
        "urlopen": 0,
    }
    assert not (artifacts / f"{missing}.json").exists()
