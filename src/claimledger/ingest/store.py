"""Canonical JSON hash store. Load by hash; convert a local file on miss."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from claimledger.ingest.parse import convert_pdf
from claimledger.ingest.types import IngestError, StoredDocument

_REPO_ROOT = Path(__file__).resolve().parents[3]


def artifacts_dir() -> Path:
    return _REPO_ROOT / "artifacts" / "docling"


def canonical_json_bytes(payload: dict) -> bytes:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _manifest_path(root: Path) -> Path:
    return root / "manifest.json"


def _read_manifest(root: Path) -> dict[str, str]:
    path = _manifest_path(root)
    if not path.is_file():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise IngestError("manifest must map pdf sha256 to artifact hash")
    mapping: dict[str, str] = {}
    for pdf_sha, artifact_hash in payload.items():
        if not isinstance(pdf_sha, str) or not isinstance(artifact_hash, str):
            raise IngestError("manifest must map pdf sha256 to artifact hash")
        mapping[pdf_sha] = artifact_hash
    return mapping


def _write_manifest(root: Path, manifest: dict[str, str]) -> None:
    _manifest_path(root).write_text(
        json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def load(artifact_hash: str) -> dict:
    path = artifacts_dir() / f"{artifact_hash}.json"
    if not path.is_file():
        raise IngestError(f"missing artifact {artifact_hash}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise IngestError("artifact JSON must be an object")
    return payload


def load_or_convert(pdf: Path) -> StoredDocument:
    if not isinstance(pdf, Path):
        raise IngestError("source must be a local file path")
    if not pdf.is_file():
        raise IngestError("source must be a local file path")
    resolved = pdf.resolve()
    pdf_sha = _sha256_hex(resolved.read_bytes())
    root = artifacts_dir()
    manifest = _read_manifest(root)
    artifact_hash = manifest.get(pdf_sha)
    if artifact_hash:
        json_path = root / f"{artifact_hash}.json"
        if json_path.is_file():
            return StoredDocument(
                artifact_hash=artifact_hash,
                json_path=json_path,
                source_pdf=resolved,
            )
    payload = convert_pdf(resolved)
    raw = canonical_json_bytes(payload)
    artifact_hash = _sha256_hex(raw)
    root.mkdir(parents=True, exist_ok=True)
    json_path = root / f"{artifact_hash}.json"
    json_path.write_bytes(raw)
    manifest[pdf_sha] = artifact_hash
    _write_manifest(root, manifest)
    return StoredDocument(
        artifact_hash=artifact_hash,
        json_path=json_path,
        source_pdf=resolved,
    )
