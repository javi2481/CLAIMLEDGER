"""One graph.json write. Load does not convert. No extraction backends."""

from __future__ import annotations

import ast
import importlib
import json
from pathlib import Path

import pytest

from claimledger.graph.build import build, graph_json_path, load

_build_module = importlib.import_module("claimledger.graph.build")
from claimledger.graph.link import GraphSource
from claimledger.ingest.classify import classify
from claimledger.ingest.types import StoredDocument

REPO_ROOT = Path(__file__).resolve().parents[2]
GRAPH_ROOT = REPO_ROOT / "src" / "claimledger" / "graph"

_FORBIDDEN_CALLS = frozenset(
    {
        "run_pipeline",
        "ProvenanceBinder",
        "bind_provenance",
        "extract_recipe",
    }
)
_FORBIDDEN_NAMES = frozenset(
    {
        "FinancialClaim",
        "VLMConfig",
        "LLMConfig",
        "CypherExporter",
        "Neo4j",
    }
)
_FORBIDDEN_IMPORT_PARTS = (
    "neo4j",
    "llm_clients",
    "cypher",
    "run_pipeline",
    "ProvenanceBinder",
)


def _source(filename: str, artifact_hash: str) -> GraphSource:
    classified = classify(
        Path(filename),
        StoredDocument(
            artifact_hash=artifact_hash,
            json_path=Path(artifact_hash),
            source_pdf=Path(filename),
        ),
    )
    return GraphSource(
        filename=filename,
        classified=classified,
        artifact_hash=artifact_hash,
    )


def _use_graph_file(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    path = tmp_path / "artifacts" / "graph" / "graph.json"
    monkeypatch.setattr(_build_module, "graph_json_path", lambda: path)
    return path


def _imported_modules(tree: ast.AST) -> set[str]:
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.add(node.module)
    return found


def _module_level_imports(tree: ast.AST) -> set[str]:
    found: set[str] = set()
    for node in getattr(tree, "body", []):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.add(node.module)
    return found


def test_default_graph_path_is_repo_artifact() -> None:
    assert graph_json_path() == REPO_ROOT / "artifacts" / "graph" / "graph.json"


def test_build_writes_graph_json_once_and_load_does_not_rebuild(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = _use_graph_file(monkeypatch, tmp_path)
    source = _source("BYMA_-_EEFF_31-03-2026_VF.pdf", "hash-eeff-1t")

    written = build([source])
    assert written == path
    assert path.is_file()
    first = json.loads(path.read_text(encoding="utf-8"))
    documents = [node for node in first["nodes"] if node.get("__class__") == "Document"]
    assert len(documents) == 1
    assert documents[0]["artifact_hash"] == "hash-eeff-1t"
    assert documents[0]["kind"] == "eeff"
    assert documents[0]["__provenance__"] == {
        "document_id": "hash-eeff-1t",
        "source": "BYMA_-_EEFF_31-03-2026_VF.pdf",
    }
    assert {node["period"] for node in first["nodes"] if node.get("__class__") == "Period"} == {
        "2026-03-31"
    }

    build([source])
    assert sorted(item.name for item in path.parent.iterdir()) == ["graph.json"]

    marker = {
        "nodes": [
            {
                "id": "disk-marker",
                "artifact_hash": "hash-eeff-1t",
                "__class__": "Document",
            }
        ],
        "edges": [],
        "metadata": {"node_count": 1, "edge_count": 0},
        "graph": {},
    }
    path.write_text(json.dumps(marker), encoding="utf-8")
    assert load() == marker
    assert load()["nodes"][0]["id"] == "disk-marker"


def test_graph_package_forbids_pipeline_llm_vlm_binder_neo4j_and_pl() -> None:
    sources = sorted(GRAPH_ROOT.glob("*.py"))
    assert [path.name for path in sources] == [
        "__init__.py",
        "build.py",
        "link.py",
        "schema.py",
    ]
    build_tree = ast.parse((GRAPH_ROOT / "build.py").read_text(encoding="utf-8"))
    build_text = (GRAPH_ROOT / "build.py").read_text(encoding="utf-8")
    assert "docling_graph" not in {
        name.split(".")[0] for name in _module_level_imports(build_tree)
    }
    assert any(
        name == "docling_graph" or name.startswith("docling_graph.")
        for name in _imported_modules(build_tree)
    )
    assert "alias_llm_fn=None" in build_text
    assert 'conflicts="keep-all"' in build_text
    assert "export_format=None" in build_text
    assert "JSONExporter" in build_text
    assert "GraphConverter" in build_text
    assert "GraphMerger" in build_text
    assert "MergePolicy" in build_text
    assert "NodeIDRegistry" in build_text
    assert 'version("docling-graph")' in build_text
    assert "1.9.1" in build_text

    for path in sources:
        text = path.read_text(encoding="utf-8")
        tree = ast.parse(text)
        calls = {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        methods = {
            node.func.attr
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        }
        names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
        assert _FORBIDDEN_CALLS.isdisjoint(calls | methods | names)
        assert _FORBIDDEN_NAMES.isdisjoint(names)
        assert "ledger_status" not in text
        assert "extract_recipe" not in text
        for module in _imported_modules(tree):
            lowered = module.lower()
            assert not any(part.lower() in lowered for part in _FORBIDDEN_IMPORT_PARTS)


def test_package_exports_build_and_load_without_top_level_docling_graph() -> None:
    import claimledger.graph as graph_pkg

    assert graph_pkg.build is build
    assert graph_pkg.load is load
    tree = ast.parse((GRAPH_ROOT / "__init__.py").read_text(encoding="utf-8"))
    imported = _imported_modules(tree)
    assert imported
    assert not any(
        name.split(".")[0] in {"docling", "docling_graph"} for name in imported
    )
