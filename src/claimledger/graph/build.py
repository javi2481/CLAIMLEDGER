"""Convert folded documents once and write artifacts/graph/graph.json."""

from __future__ import annotations

import json
import re
from collections.abc import Sequence
from pathlib import Path

from claimledger.graph.link import GraphSource, fold_documents
from claimledger.graph.schema import Document
from claimledger.identity import normalize_period

PINNED_DOCLING_GRAPH = "1.9.1"
_SEPARATORS = re.compile(r"[\s._\-]+")
_REPO_ROOT = Path(__file__).resolve().parents[3]


def graph_json_path() -> Path:
    return _REPO_ROOT / "artifacts" / "graph" / "graph.json"


def build(sources: Sequence[GraphSource]) -> Path:
    folded = fold_documents(sources)
    documents: list[Document] = []
    for source, document in zip(sources, folded.documents, strict=True):
        document.doubt = _unresolved_period_doubt(source, document)
        documents.append(document)
    merged = _convert_and_merge(documents)
    _stamp_provenance(merged, sources)
    path = graph_json_path()
    _export(merged, path)
    return path


def load() -> dict:
    payload = json.loads(graph_json_path().read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("graph JSON must be an object")
    return payload


def _unresolved_period_doubt(source: GraphSource, document: Document) -> str | None:
    if document.for_period is not None:
        return None
    last_error: str | None = None
    for token in _SEPARATORS.split(Path(source.filename).stem):
        if not token:
            continue
        try:
            normalize_period(token)
        except ValueError as exc:
            last_error = str(exc)
        else:
            return None
    return last_error


def _require_pinned_docling_graph() -> None:
    from importlib.metadata import version

    installed = version("docling-graph")
    if installed != PINNED_DOCLING_GRAPH:
        raise ValueError(
            f"docling-graph {installed} does not match pin {PINNED_DOCLING_GRAPH}"
        )


def _convert_and_merge(documents: Sequence[Document]):
    _require_pinned_docling_graph()
    from docling_graph.core.converters.graph_converter import GraphConverter
    from docling_graph.core.converters.node_id_registry import NodeIDRegistry
    from docling_graph.core.merge.merger import GraphMerger
    from docling_graph.core.merge.policy import MergePolicy

    registry = NodeIDRegistry()
    graphs = []
    for document in documents:
        converter = GraphConverter(alias_llm_fn=None, registry=registry)
        graph, _metadata = converter.pydantic_list_to_graph([document])
        graphs.append(graph)
    merger = GraphMerger(
        graphs,
        policy=MergePolicy(conflicts="keep-all", export_format=None),
    )
    merged, _report = merger.merge()
    return merged


def _stamp_provenance(graph, sources: Sequence[GraphSource]) -> None:
    from docling_graph.core.provenance.models import DocumentOrigin

    paths: dict[str, str] = {}
    for source in sources:
        paths.setdefault(source.artifact_hash, source.filename)
    for _node_id, data in graph.nodes(data=True):
        if data.get("__class__") != "Document":
            continue
        digest = data.get("artifact_hash")
        if not isinstance(digest, str) or digest not in paths:
            continue
        origin = DocumentOrigin(document_id=digest, source=paths[digest])
        data["__provenance__"] = {
            "document_id": origin.document_id,
            "source": origin.source,
        }


def _export(graph, path: Path) -> None:
    from docling_graph.core.exporters.json_exporter import JSONExporter

    JSONExporter().export(graph, path)
