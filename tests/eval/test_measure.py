"""Measure joins tables retrieve, understand, and query on a ledger."""

from __future__ import annotations

import ast
import hashlib
import json
from dataclasses import fields
from pathlib import Path
from types import SimpleNamespace

import pytest

import claimledger.ingest.store as ingest_store
import claimledger.ledger as ledger_mod
import claimledger.lookup as lookup_mod
import claimledger.query as query_mod
import claimledger.retrieval.drawers as drawers_mod
from claimledger.claim import FinancialClaim
from claimledger.ledger import RECIPE_ROWS
from claimledger.query import QueryResult
from claimledger.retrieval.drawers import Candidate


CONSOLIDATED_ROW = "RESULTADO NETO DEL PERÍODO 21.262.335"
PARENT_ROW = "Resultado neto atribuible a la sociedad controlante 21.259.769"
CONSOLIDATED_QUESTION = (
    "¿Cuál es el RESULTADO NETO DEL PERÍODO consolidado del 1T26?"
)
PARENT_QUESTION = "resultado atribuible a la controlante 1T26"
CONSOLIDATED_VALUE = "21262335"
PARENT_VALUE = "21259769"
SECOND_QUARTER_VALUE = "81956525"
SEED_UPSERTS = 14
NARRATIVE_TEXT = "política contable de reconocimiento de ingresos"
COMPARE_QUESTION = "Comparar resultado neto consolidado 1T26 vs 2T26"
RECIPE_QUESTIONS = (
    "resultado neto del período en la memoria anual",
    "¿Cuál es el resultado neto consolidado del comunicado de prensa?",
    "¿Cuál es el resultado neto consolidado del deck?",
    "cláusula 5 del contrato",
)
KERNEL_ALLOWLIST = (
    "src/claimledger/identity.py",
    "src/claimledger/digits.py",
    "src/claimledger/evidence.py",
    "src/claimledger/claim.py",
    "src/claimledger/ledger.py",
    "src/claimledger/lookup.py",
    "src/claimledger/query.py",
    "tests/test_identity.py",
    "tests/test_ledger.py",
    "tests/test_lookup.py",
    "tests/test_query.py",
    "tests/test_gold_v1.py",
    "tests/test_gold_v2.py",
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
            _node("Estado de Resultados", "section_header", "#/texts/0"),
            _node(CONSOLIDATED_ROW, "table", "#/tables/1"),
            _node(PARENT_ROW, "table", "#/tables/1"),
            _node("política contable de reconocimiento de ingresos", "text", "#/texts/4"),
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


def _install_parsed_reader(monkeypatch: pytest.MonkeyPatch) -> None:
    from claimledger.retrieval import read as read_mod

    def fake_read(artifact_hash: str) -> list[SimpleNamespace]:
        return _parsed_nodes(ingest_store.load(artifact_hash))

    monkeypatch.setattr(read_mod, "read_hashed_json", fake_read)


def _forbid_io(monkeypatch: pytest.MonkeyPatch) -> dict[str, int]:
    calls = {"load_or_convert": 0, "convert_pdf": 0, "urlopen": 0}

    def _count(key: str):
        def _inner(*_args: object, **_kwargs: object) -> None:
            calls[key] += 1

        return _inner

    monkeypatch.setattr(ingest_store, "load_or_convert", _count("load_or_convert"))
    monkeypatch.setattr(ingest_store, "convert_pdf", _count("convert_pdf"))
    monkeypatch.setattr("claimledger.ingest.parse.convert_pdf", _count("convert_pdf"))
    monkeypatch.setattr("urllib.request.urlopen", _count("urlopen"))
    return calls


def _prepare(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[str, dict[str, int]]:
    artifacts = tmp_path / "docling"
    artifacts.mkdir()
    _use_artifacts(monkeypatch, artifacts)
    digest = _write_artifact(artifacts, _neighbor_payload())
    io_calls = _forbid_io(monkeypatch)
    _install_parsed_reader(monkeypatch)
    return digest, io_calls


def _import_measure():
    import claimledger.eval.measure as measure_mod

    return measure_mod.measure, measure_mod


def _book() -> ledger_mod.Ledger:
    return ledger_mod.Ledger.seed()


class _Calls:
    def __init__(self) -> None:
        self.order: list[str] = []
        self.retrieve_args: list[tuple[object, ...]] = []
        self.understand_args: list[str] = []
        self.intents: list[object] = []
        self.query_intents: list[object] = []
        self.ledgers: list[object] = []
        self.seeded: list[object] = []
        self.query_inside_retrieve = 0
        self.query_from_caller = 0
        self._in_retrieve = False


def _spy_pipeline(monkeypatch: pytest.MonkeyPatch, measure_mod: object) -> _Calls:
    seen = _Calls()
    real_retrieve = drawers_mod.retrieve
    real_understand = lookup_mod.understand
    real_query = query_mod.query
    real_seed = ledger_mod.Ledger.seed

    def spy_retrieve(artifact_hash: str, drawer: str, question: str):
        seen.order.append("retrieve")
        seen.retrieve_args.append((artifact_hash, drawer, question))
        seen._in_retrieve = True
        try:
            return real_retrieve(artifact_hash, drawer, question)
        finally:
            seen._in_retrieve = False

    def spy_understand(question: str):
        seen.order.append("understand")
        seen.understand_args.append(question)
        intent = real_understand(question)
        seen.intents.append(intent)
        return intent

    def spy_query(intent: object, ledger: object):
        seen.order.append("query")
        seen.query_intents.append(intent)
        seen.ledgers.append(ledger)
        if seen._in_retrieve:
            seen.query_inside_retrieve += 1
        else:
            seen.query_from_caller += 1
        return real_query(intent, ledger)

    def spy_seed() -> object:
        ledger = real_seed()
        seen.seeded.append(ledger)
        return ledger

    monkeypatch.setattr(drawers_mod, "retrieve", spy_retrieve)
    monkeypatch.setattr(lookup_mod, "understand", spy_understand)
    monkeypatch.setattr(query_mod, "query", spy_query)
    monkeypatch.setattr(ledger_mod.Ledger, "seed", staticmethod(spy_seed))
    for name, spy in (
        ("retrieve", spy_retrieve),
        ("understand", spy_understand),
        ("query", spy_query),
    ):
        if hasattr(measure_mod, name):
            monkeypatch.setattr(measure_mod, name, spy)
    return seen


def _spy_upsert(monkeypatch: pytest.MonkeyPatch) -> dict[str, int]:
    calls = {"n": 0}
    real_upsert = ledger_mod.Ledger.upsert

    def spy_upsert(self: object, claim: FinancialClaim) -> FinancialClaim:
        calls["n"] += 1
        return real_upsert(self, claim)

    monkeypatch.setattr(ledger_mod.Ledger, "upsert", spy_upsert)
    return calls


def _assert_quiet_io(io_calls: dict[str, int]) -> None:
    assert io_calls["load_or_convert"] == 0
    assert io_calls["convert_pdf"] == 0
    assert io_calls["urlopen"] == 0


def _assert_both_neighbors(candidates: tuple[Candidate, ...]) -> None:
    assert [item.text for item in candidates] == [CONSOLIDATED_ROW, PARENT_ROW]


def _assert_recorded_value(result: QueryResult, value: str, rejected: str) -> None:
    assert isinstance(result, QueryResult)
    assert result.status == "verified"
    assert [claim.value for claim in result.claims] == [value]
    assert rejected not in [claim.value for claim in result.claims]
    assert [claim.ledger_status for claim in result.claims] == ["recorded"]


def test_slice1_call_order_and_both_neighbors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    digest, io_calls = _prepare(tmp_path, monkeypatch)
    measure, measure_mod = _import_measure()
    book = _book()
    seen = _spy_pipeline(monkeypatch, measure_mod)

    candidates, result = measure(digest, CONSOLIDATED_QUESTION, book)

    assert seen.order == ["retrieve", "understand", "query"]
    assert seen.retrieve_args == [(digest, "tables", CONSOLIDATED_QUESTION)]
    assert seen.understand_args == [CONSOLIDATED_QUESTION]
    assert seen.query_intents == seen.intents
    assert seen.ledgers == [book]
    assert seen.seeded == []
    _assert_both_neighbors(candidates)
    assert isinstance(result, QueryResult)
    _assert_quiet_io(io_calls)


def test_measure_queries_the_passed_ledger_and_does_not_seed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    digest, _io_calls = _prepare(tmp_path, monkeypatch)
    measure, _measure_mod = _import_measure()
    book = ledger_mod.Ledger.seed()
    seen = _spy_pipeline(monkeypatch, _measure_mod)

    measure(digest, CONSOLIDATED_QUESTION, book)

    assert seen.ledgers == [book]
    assert seen.seeded == []
    assert "Ledger.seed" not in _repo_file("src/claimledger/eval/measure.py")


def test_omitted_ledger_is_the_quarterly_book(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    digest, io_calls = _prepare(tmp_path, monkeypatch)
    measure, measure_mod = _import_measure()
    book = _book()
    seen = _spy_pipeline(monkeypatch, measure_mod)
    monkeypatch.setattr(measure_mod, "_quarterly_book", lambda: book)

    measure(digest, CONSOLIDATED_QUESTION)

    assert seen.ledgers == [book]
    assert seen.seeded == []
    _assert_quiet_io(io_calls)


def test_slice1_consolidated_21262335(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    digest, io_calls = _prepare(tmp_path, monkeypatch)
    measure, _measure_mod = _import_measure()

    candidates, result = measure(digest, CONSOLIDATED_QUESTION, _book())

    _assert_both_neighbors(candidates)
    _assert_recorded_value(result, CONSOLIDATED_VALUE, PARENT_VALUE)
    _assert_quiet_io(io_calls)


def test_slice1_parent_21259769(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    digest, io_calls = _prepare(tmp_path, monkeypatch)
    measure, _measure_mod = _import_measure()

    candidates, result = measure(digest, PARENT_QUESTION, _book())

    _assert_both_neighbors(candidates)
    _assert_recorded_value(result, PARENT_VALUE, CONSOLIDATED_VALUE)
    _assert_quiet_io(io_calls)


def test_slice1_no_upsert_and_not_verified(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    digest, io_calls = _prepare(tmp_path, monkeypatch)
    measure, _measure_mod = _import_measure()
    book = _book()
    upserts = _spy_upsert(monkeypatch)

    candidates, result = measure(digest, CONSOLIDATED_QUESTION, book)

    assert len(RECIPE_ROWS) == SEED_UPSERTS
    assert upserts["n"] == 0
    assert len(candidates) == 2
    for candidate in candidates:
        assert isinstance(candidate, Candidate)
        assert [field.name for field in fields(candidate)] == ["drawer", "text", "ref"]
        assert "verified" not in candidate.__dict__
        assert not isinstance(candidate, FinancialClaim)
    assert result.status == "verified"
    assert [claim.ledger_status for claim in result.claims] == ["recorded"]
    assert "verified" not in [claim.ledger_status for claim in result.claims]
    _assert_quiet_io(io_calls)


def test_slice1_retrieve_query_count_stays_zero(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    digest, io_calls = _prepare(tmp_path, monkeypatch)
    measure, measure_mod = _import_measure()
    book = _book()
    seen = _spy_pipeline(monkeypatch, measure_mod)

    measure(digest, PARENT_QUESTION, book)

    assert seen.query_inside_retrieve == 0
    assert seen.query_from_caller == 1
    assert seen.order == ["retrieve", "understand", "query"]
    _assert_quiet_io(io_calls)


def _digits(text: str) -> str:
    return "".join(ch for ch in text if ch.isdigit())


def _repo_file(relative: str) -> str:
    return (Path(__file__).resolve().parents[2] / relative).read_text(encoding="utf-8")


def _assigned_strings(tree: ast.AST, name: str) -> tuple[str, ...]:
    for node in tree.body:  # type: ignore[attr-defined]
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
            continue
        return tuple(
            elt.value
            for elt in node.value.elts  # type: ignore[attr-defined]
            if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
        )
    raise AssertionError(f"{name} missing")


def _forbidden_roots(tree: ast.AST) -> frozenset[str]:
    for node in tree.body:  # type: ignore[attr-defined]
        if not isinstance(node, ast.Assign):
            continue
        if not any(
            isinstance(target, ast.Name) and target.id == "FORBIDDEN_IMPORT_ROOTS"
            for target in node.targets
        ):
            continue
        call = node.value
        assert isinstance(call, ast.Call)
        roots = call.args[0]
        assert isinstance(roots, ast.Set)
        return frozenset(
            elt.value
            for elt in roots.elts
            if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
        )
    raise AssertionError("FORBIDDEN_IMPORT_ROOTS missing")


def _allowlist_paths(tree: ast.AST) -> tuple[str, ...]:
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef) or node.name != "_kernel_scan_paths":
            continue
        for stmt in node.body:
            if not isinstance(stmt, ast.Assign):
                continue
            if not any(
                isinstance(target, ast.Name) and target.id == "relatives"
                for target in stmt.targets
            ):
                continue
            return tuple(
                elt.value
                for elt in stmt.value.elts  # type: ignore[attr-defined]
                if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
            )
    raise AssertionError("allowlist missing")


def test_slice2_recipe_no_extract_abstains(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    digest, io_calls = _prepare(tmp_path, monkeypatch)
    measure, _measure_mod = _import_measure()

    for question in RECIPE_QUESTIONS:
        candidates, result = measure(digest, question, _book())

        _assert_both_neighbors(candidates)
        assert any(CONSOLIDATED_VALUE in _digits(item.text) for item in candidates)
        assert result.status == "abstained"
        assert result.reason == "recipe_no_extract"
        assert result.claims == ()
        assert CONSOLIDATED_VALUE not in [claim.value for claim in result.claims]
    _assert_quiet_io(io_calls)


def test_slice2_compare_two_claims(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    digest, io_calls = _prepare(tmp_path, monkeypatch)
    measure, _measure_mod = _import_measure()

    candidates, result = measure(digest, COMPARE_QUESTION, _book())

    _assert_both_neighbors(candidates)
    assert result.status == "verified"
    values = [claim.value for claim in result.claims]
    assert values == [CONSOLIDATED_VALUE, SECOND_QUARTER_VALUE]
    difference = str(abs(int(SECOND_QUARTER_VALUE) - int(CONSOLIDATED_VALUE)))
    assert difference not in values
    assert len(values) == 2
    _assert_quiet_io(io_calls)


def test_slice2_narrative_not_number_source(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    digest, io_calls = _prepare(tmp_path, monkeypatch)
    measure, measure_mod = _import_measure()
    book = _book()
    seen = _spy_pipeline(monkeypatch, measure_mod)

    candidates, result = measure(digest, CONSOLIDATED_QUESTION, book)

    assert seen.retrieve_args == [(digest, "tables", CONSOLIDATED_QUESTION)]
    assert len(seen.retrieve_args) == 1
    _assert_both_neighbors(candidates)
    assert NARRATIVE_TEXT not in [item.text for item in candidates]
    assert all(item.drawer == "tables" for item in candidates)
    _assert_recorded_value(result, CONSOLIDATED_VALUE, PARENT_VALUE)
    assert NARRATIVE_TEXT not in [claim.value for claim in result.claims]
    assert seen.query_inside_retrieve == 0
    _assert_quiet_io(io_calls)


def test_slice2_empty_question_keeps_both_rows(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    digest, io_calls = _prepare(tmp_path, monkeypatch)
    measure, measure_mod = _import_measure()
    book = _book()
    seen = _spy_pipeline(monkeypatch, measure_mod)

    candidates, _result = measure(digest, "", book)

    assert seen.retrieve_args == [(digest, "tables", "")]
    _assert_both_neighbors(candidates)
    _assert_quiet_io(io_calls)


def test_slice2_shared_ref_does_not_select(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    digest, io_calls = _prepare(tmp_path, monkeypatch)
    measure, _measure_mod = _import_measure()

    for question, value, rejected in (
        (CONSOLIDATED_QUESTION, CONSOLIDATED_VALUE, PARENT_VALUE),
        (PARENT_QUESTION, PARENT_VALUE, CONSOLIDATED_VALUE),
    ):
        candidates, result = measure(digest, question, _book())
        assert [item.ref for item in candidates] == ["#/tables/1", "#/tables/1"]
        _assert_both_neighbors(candidates)
        _assert_recorded_value(result, value, rejected)
    _assert_quiet_io(io_calls)


def test_slice2_gold_files_not_edited() -> None:
    v1 = _repo_file("tests/test_gold_v1.py")
    v2 = _repo_file("tests/test_gold_v2.py")
    for source in (v1, v2):
        assert "Ledger.seed()" in source
        assert "retrieve" not in source
        tree = ast.parse(source)
        seed_calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "seed"
        ]
        assert seed_calls
        retrieve_calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and (
                (isinstance(node.func, ast.Name) and node.func.id == "retrieve")
                or (isinstance(node.func, ast.Attribute) and node.func.attr == "retrieve")
            )
        ]
        assert retrieve_calls == []
    assert "-14950948" in v2


def test_slice2_eval_outside_allowlist() -> None:
    source = _repo_file("tests/test_identity.py")
    tree = ast.parse(source)
    modules = _assigned_strings(tree, "KERNEL_MODULES")
    paths = _allowlist_paths(tree)
    forbidden = _forbidden_roots(tree)

    assert "claimledger.eval" not in modules
    assert not any(name.startswith("claimledger.eval") for name in modules)
    assert paths == KERNEL_ALLOWLIST
    assert len(paths) == 13
    assert not any("eval" in path for path in paths)
    assert "llama_index" not in forbidden
    assert forbidden == frozenset({"docling", "docling_graph"})
