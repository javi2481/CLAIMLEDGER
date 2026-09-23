"""Frozen financial evidence. Bbox is optional and normalized 0–1 when present."""

from __future__ import annotations

from dataclasses import dataclass


class EvidenceError(ValueError):
    """Evidence failed integrity checks."""


def _validate_bbox(bbox: tuple[float, float, float, float] | None) -> None:
    if bbox is None:
        return
    x0, y0, x1, y1 = bbox
    if not (0.0 <= x0 <= x1 <= 1.0 and 0.0 <= y0 <= y1 <= 1.0):
        raise EvidenceError("bbox must be normalized 0-1 with x0<=x1 and y0<=y1")


def validate_evidence(evidence: FinancialEvidence) -> None:
    _validate_bbox(evidence.bbox)


@dataclass(frozen=True)
class FinancialEvidence:
    document_id: str
    artifact_hash: str
    page: int
    text: str
    label: str
    bbox: tuple[float, float, float, float] | None = None

    def __post_init__(self) -> None:
        validate_evidence(self)
