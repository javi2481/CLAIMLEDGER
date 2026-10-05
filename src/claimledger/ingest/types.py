"""Frozen ingest records."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class IngestError(ValueError):
    """Ingest failed integrity checks."""


@dataclass(frozen=True)
class StoredDocument:
    artifact_hash: str
    json_path: Path
    source_pdf: Path
