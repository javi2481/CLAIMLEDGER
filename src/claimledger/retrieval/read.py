"""Read an existing hashed Docling JSON artifact. JSON export only."""

from __future__ import annotations

from pathlib import Path

import claimledger.ingest.store as ingest_store

_JSON_EXPORT = "json"


def read_hashed_json(artifact_hash: str) -> list:
    ingest_store.load(artifact_hash)
    path = ingest_store.artifacts_dir() / f"{artifact_hash}.json"
    return _nodes_from_hashed_json(path)


def _nodes_from_hashed_json(path: Path) -> list:
    from llama_index.node_parser.docling import DoclingNodeParser
    from llama_index.readers.docling import DoclingReader

    reader = DoclingReader(export_type=_JSON_EXPORT)
    documents = reader.load_data(file_path=path)
    parser = DoclingNodeParser()
    return parser.get_nodes_from_documents(documents)
