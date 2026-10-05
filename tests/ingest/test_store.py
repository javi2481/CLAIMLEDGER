"""Hashed Docling JSON store. Local Path convert only."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

import pytest

from claimledger.ingest.parse import convert_pdf
from claimledger.ingest.store import artifacts_dir, load, load_or_convert
from claimledger.ingest.types import IngestError, StoredDocument

REPO_ROOT = Path(__file__).resolve().parents[2]
INGEST_ROOT = REPO_ROOT / "src" / "claimledger" / "ingest"
FORBIDDEN_SOURCE_TOKENS = (
    "HttpSource",
    "docling-graph",
    "docling_graph",
    "llama_index",
    "http://",
    "https://",
)


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
    monkeypatch.setattr(
        "claimledger.ingest.store.artifacts_dir",
        lambda: root,
    )


def test_load_existing_artifact_by_canonical_hash(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    payload = {"b": 1, "a": "ñ", "nested": {"z": 2, "y": [3, 1]}}
    raw = _canonical_json_bytes(payload)
    digest = _sha256_hex(raw)
    artifacts = tmp_path / "docling"
    artifacts.mkdir()
    (artifacts / f"{digest}.json").write_bytes(raw)
    _use_artifacts(monkeypatch, artifacts)

    loaded = load(digest)

    assert loaded == payload
    assert _sha256_hex(_canonical_json_bytes(loaded)) == digest


def test_load_second_artifact_is_a_different_document(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    first = {"doc": "one", "n": 1}
    second = {"doc": "two", "n": 2}
    artifacts = tmp_path / "docling"
    artifacts.mkdir()
    digests = []
    for payload in (first, second):
        raw = _canonical_json_bytes(payload)
        digest = _sha256_hex(raw)
        (artifacts / f"{digest}.json").write_bytes(raw)
        digests.append(digest)
    _use_artifacts(monkeypatch, artifacts)

    assert load(digests[0]) == first
    assert load(digests[1]) == second
    assert digests[0] != digests[1]


def test_missing_hash_converts_local_path_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pdf = tmp_path / "local-only.pdf"
    pdf.write_bytes(b"%PDF-1.4 local")
    artifacts = tmp_path / "docling"
    _use_artifacts(monkeypatch, artifacts)
    seen: list[Path] = []

    def fake_convert(source: Path) -> dict:
        seen.append(source)
        assert isinstance(source, Path)
        assert source.is_file()
        return {"kind": "converted", "name": source.name}

    monkeypatch.setattr("claimledger.ingest.parse.convert_pdf", fake_convert)
    monkeypatch.setattr("claimledger.ingest.store.convert_pdf", fake_convert)

    stored = load_or_convert(pdf)

    assert seen == [pdf.resolve()]
    assert isinstance(stored, StoredDocument)
    assert stored.source_pdf == pdf.resolve()
    assert stored.json_path == artifacts / f"{stored.artifact_hash}.json"
    on_disk = stored.json_path.read_bytes()
    assert _sha256_hex(on_disk) == stored.artifact_hash
    assert on_disk == _canonical_json_bytes(json.loads(on_disk))
    assert load(stored.artifact_hash) == {"kind": "converted", "name": pdf.name}
    pdf_sha = _sha256_hex(pdf.read_bytes())
    manifest = json.loads((artifacts / "manifest.json").read_text(encoding="utf-8"))
    assert manifest[pdf_sha] == stored.artifact_hash

    stored_again = load_or_convert(pdf)

    assert stored_again.artifact_hash == stored.artifact_hash
    assert seen == [pdf.resolve()]


def test_distinct_pdfs_persist_distinct_hashes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    artifacts = tmp_path / "docling"
    _use_artifacts(monkeypatch, artifacts)
    pdf_a = tmp_path / "a.pdf"
    pdf_b = tmp_path / "b.pdf"
    pdf_a.write_bytes(b"%PDF-1.4 A")
    pdf_b.write_bytes(b"%PDF-1.4 B")

    def fake_convert(source: Path) -> dict:
        return {"kind": "converted", "name": source.name, "size": source.stat().st_size}

    monkeypatch.setattr("claimledger.ingest.parse.convert_pdf", fake_convert)
    monkeypatch.setattr("claimledger.ingest.store.convert_pdf", fake_convert)

    stored_a = load_or_convert(pdf_a)
    stored_b = load_or_convert(pdf_b)

    assert stored_a.artifact_hash != stored_b.artifact_hash
    assert load(stored_a.artifact_hash)["name"] == "a.pdf"
    assert load(stored_b.artifact_hash)["name"] == "b.pdf"


def test_existing_pdf_hash_loads_without_reconvert(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pdf = tmp_path / "cached.pdf"
    pdf.write_bytes(b"%PDF-1.4 cached")
    payload = {"kind": "cached", "n": 7}
    raw = _canonical_json_bytes(payload)
    digest = _sha256_hex(raw)
    artifacts = tmp_path / "docling"
    artifacts.mkdir()
    (artifacts / f"{digest}.json").write_bytes(raw)
    pdf_sha = _sha256_hex(pdf.read_bytes())
    (artifacts / "manifest.json").write_text(
        json.dumps({pdf_sha: digest}),
        encoding="utf-8",
    )
    _use_artifacts(monkeypatch, artifacts)

    def boom(source: Path) -> dict:
        raise AssertionError(f"reconvert of {source}")

    monkeypatch.setattr("claimledger.ingest.parse.convert_pdf", boom)
    monkeypatch.setattr("claimledger.ingest.store.convert_pdf", boom)

    stored = load_or_convert(pdf)

    assert stored == StoredDocument(
        artifact_hash=digest,
        json_path=artifacts / f"{digest}.json",
        source_pdf=pdf.resolve(),
    )
    assert load(digest) == payload


def test_load_or_convert_rejects_non_path(tmp_path: Path) -> None:
    with pytest.raises(IngestError):
        load_or_convert("https://example.invalid/file.pdf")  # type: ignore[arg-type]
    with pytest.raises(IngestError):
        load_or_convert(tmp_path / "missing.pdf")


def test_ingest_sources_forbid_url_httpsource_and_docling_graph() -> None:
    sources = sorted(INGEST_ROOT.glob("*.py"))
    assert [path.name for path in sources] == [
        "__init__.py",
        "classify.py",
        "extract.py",
        "parse.py",
        "store.py",
        "types.py",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in sources)
    for token in FORBIDDEN_SOURCE_TOKENS:
        assert token not in combined

    parse_source = (INGEST_ROOT / "parse.py").read_text(encoding="utf-8")
    tree = ast.parse(parse_source)
    imported = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imported_from = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }
    assert any(name == "docling" or name.startswith("docling.") for name in imported | imported_from)
    assert not any("graph" in name for name in imported | imported_from)
    assert "DocumentConverter" in parse_source
    assert "do_ocr=False" in parse_source or "do_ocr = False" in parse_source
    assert "artifacts_path" in parse_source
    assert "2.130.0" in parse_source


def test_default_artifact_root_is_repo_docling_dir() -> None:
    assert artifacts_dir() == REPO_ROOT / "artifacts" / "docling"


def test_convert_pdf_rejects_non_path() -> None:
    with pytest.raises(IngestError):
        convert_pdf("https://example.invalid/file.pdf")  # type: ignore[arg-type]


def test_partial_success_is_not_exported() -> None:
    from types import SimpleNamespace

    from claimledger.ingest.parse import _export_complete

    partial = SimpleNamespace(
        status=SimpleNamespace(name="PARTIAL_SUCCESS", value="partial_success"),
        document=SimpleNamespace(export_to_dict=lambda: {"pages": []}),
    )
    with pytest.raises(IngestError, match="success"):
        _export_complete(partial)

    complete = SimpleNamespace(
        status=SimpleNamespace(name="SUCCESS", value="success"),
        document=SimpleNamespace(export_to_dict=lambda: {"pages": [{"ok": True}]}),
    )
    assert _export_complete(complete) == {"pages": [{"ok": True}]}

    parse_source = (INGEST_ROOT / "parse.py").read_text(encoding="utf-8")
    assert "return _export_complete(result)" in parse_source
