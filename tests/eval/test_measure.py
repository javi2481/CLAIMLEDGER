"""Measure is understand then query. Rows come from verified evidence."""

from __future__ import annotations

import ast
import inspect
from dataclasses import replace
from pathlib import Path

import pytest

import claimledger.ledger as ledger_mod
import claimledger.lookup as lookup_mod
import claimledger.query as query_mod
from claimledger.card.candidate import Candidate
from claimledger.claim import FinancialClaim
from claimledger.evidence import FinancialEvidence
from claimledger.identity import identity_key
from claimledger.ledger import RECIPE_ROWS, Ledger
from claimledger.query import QueryResult


CONSOLIDATED_QUESTION = (
    "¿Cuál es el RESULTADO NETO DEL PERÍODO consolidado del 1T26?"
)
PARENT_QUESTION = "resultado atribuible a la controlante 1T26"
COMPARE_QUESTION = "Comparar resultado neto consolidado 1T26 vs 2T26"
CONSOLIDATED_VALUE = "21262335"
PARENT_VALUE = "21259769"
SECOND_QUARTER_VALUE = "81956525"
EVIDENCE_TEXT = "21.262.335"
LABEL = "RESULTADO NETO DEL PERÍODO"
SHARED_HASH = "shared-artifact"
NARRATIVE_TEXT = "política contable de reconocimiento de ingresos"
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
REPO = Path(__file__).resolve().parents[2]


def _import_measure():
    import claimledger.eval.measure as measure_mod

    return measure_mod.measure, measure_mod


def _evidence(text: str, label: str = LABEL, digest: str = SHARED_HASH) -> FinancialEvidence:
    return FinancialEvidence(
        document_id="#/tables/1",
        artifact_hash=digest,
        page=1,
        text=text,
        label=label,
    )


def _attach(
    book: Ledger,
    period: str,
    scope: str,
    evidence: tuple[FinancialEvidence, ...],
) -> None:
    key = identity_key("BYMA", period, "income_statement", scope, "net_income")
    current = book.get(key)
    assert current is not None
    book.upsert(replace(current, evidence=evidence))


class _Calls:
    def __init__(self) -> None:
        self.order: list[str] = []
        self.understand_args: list[str] = []
        self.intents: list[object] = []
        self.query_intents: list[object] = []
        self.ledgers: list[object] = []
        self.seeded: list[object] = []


def _spy_pipeline(monkeypatch: pytest.MonkeyPatch, measure_mod: object) -> _Calls:
    seen = _Calls()
    real_understand = lookup_mod.understand
    real_query = query_mod.query
    real_seed = ledger_mod.Ledger.seed

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
        return real_query(intent, ledger)

    def spy_seed() -> object:
        ledger = real_seed()
        seen.seeded.append(ledger)
        return ledger

    monkeypatch.setattr(lookup_mod, "understand", spy_understand)
    monkeypatch.setattr(query_mod, "query", spy_query)
    monkeypatch.setattr(measure_mod, "understand", spy_understand)
    monkeypatch.setattr(measure_mod, "query", spy_query)
    monkeypatch.setattr(ledger_mod.Ledger, "seed", staticmethod(spy_seed))
    return seen


def _measure_source() -> str:
    return (REPO / "src" / "claimledger" / "eval" / "measure.py").read_text(encoding="utf-8")


def _repo_file(relative: str) -> str:
    return (REPO / relative).read_text(encoding="utf-8")


def test_measure_signature_is_question_and_ledger() -> None:
    measure, _measure_mod = _import_measure()
    assert tuple(inspect.signature(measure).parameters) == ("question", "ledger")
    source = _measure_source()
    assert "artifact_hash" not in source
    assert "retrieve" not in source
    assert "recorded_book" not in source
    assert "Ledger.seed" not in source
    assert "difference" not in source
    assert "docling" not in source


def test_understand_then_query_on_the_passed_ledger(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    measure, measure_mod = _import_measure()
    book = Ledger.seed()
    seen = _spy_pipeline(monkeypatch, measure_mod)

    candidates, result = measure(CONSOLIDATED_QUESTION, book)

    assert seen.order == ["understand", "query"]
    assert seen.understand_args == [CONSOLIDATED_QUESTION]
    assert seen.query_intents == seen.intents
    assert seen.ledgers == [book]
    assert seen.seeded == []
    assert candidates == ()
    assert isinstance(result, QueryResult)
    assert result.status == "verified"
    assert [claim.value for claim in result.claims] == [CONSOLIDATED_VALUE]


def test_seed_rows_are_empty_for_consolidated_and_parent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    measure, _measure_mod = _import_measure()
    book = Ledger.seed()
    monkeypatch.setattr(
        "claimledger.ingest.ground.recorded_book",
        lambda: (_ for _ in ()).throw(AssertionError("recorded_book")),
    )

    consolidated, consolidated_result = measure(CONSOLIDATED_QUESTION, book)
    parent, parent_result = measure(PARENT_QUESTION, book)

    assert consolidated == ()
    assert parent == ()
    assert [claim.value for claim in consolidated_result.claims] == [CONSOLIDATED_VALUE]
    assert PARENT_VALUE not in [claim.value for claim in consolidated_result.claims]
    assert [claim.ledger_status for claim in consolidated_result.claims] == ["recorded"]
    assert [claim.value for claim in parent_result.claims] == [PARENT_VALUE]
    assert CONSOLIDATED_VALUE not in [claim.value for claim in parent_result.claims]
    assert [claim.ledger_status for claim in parent_result.claims] == ["recorded"]


def test_evidence_text_is_one_tables_row() -> None:
    measure, _measure_mod = _import_measure()
    book = Ledger.seed()
    _attach(book, "2026-03-31", "consolidated", (_evidence(EVIDENCE_TEXT, digest="h1"),))

    candidates, result = measure(CONSOLIDATED_QUESTION, book)

    assert len(candidates) == 1
    assert isinstance(candidates[0], Candidate)
    assert candidates[0].drawer == "tables"
    assert candidates[0].text == EVIDENCE_TEXT
    assert candidates[0].ref == "h1"
    assert not hasattr(candidates[0], "rank")
    assert not hasattr(candidates[0], "score")
    assert result.claims[0].value == CONSOLIDATED_VALUE
    assert NARRATIVE_TEXT not in [item.text for item in candidates]


def test_blank_evidence_text_uses_the_label() -> None:
    measure, _measure_mod = _import_measure()
    book = Ledger.seed()
    _attach(book, "2026-03-31", "consolidated", (_evidence("", LABEL, digest="h-blank"),))

    candidates, result = measure(CONSOLIDATED_QUESTION, book)

    assert [(item.drawer, item.text, item.ref) for item in candidates] == [
        ("tables", LABEL, "h-blank")
    ]
    assert result.claims[0].value == CONSOLIDATED_VALUE


def test_two_evidence_items_stay_and_shared_hash_adds_no_neighbor() -> None:
    measure, _measure_mod = _import_measure()
    book = Ledger.seed()
    shared = (
        _evidence(EVIDENCE_TEXT, LABEL, SHARED_HASH),
        _evidence("21.259.769", "controlante", SHARED_HASH),
    )
    _attach(book, "2026-03-31", "consolidated", shared)
    _attach(
        book,
        "2026-03-31",
        "parent_attributable",
        (_evidence("21.259.769", "controlante", SHARED_HASH),),
    )

    consolidated, consolidated_result = measure(CONSOLIDATED_QUESTION, book)
    parent, parent_result = measure(PARENT_QUESTION, book)

    assert [item.text for item in consolidated] == [EVIDENCE_TEXT, "21.259.769"]
    assert [item.ref for item in consolidated] == [SHARED_HASH, SHARED_HASH]
    assert len(consolidated) == 2
    assert all(item.drawer == "tables" for item in consolidated)
    assert [item.text for item in parent] == ["21.259.769"]
    assert consolidated_result.claims[0].value == CONSOLIDATED_VALUE
    assert parent_result.claims[0].value == PARENT_VALUE


def test_abstain_yields_no_candidates() -> None:
    measure, _measure_mod = _import_measure()
    book = Ledger.seed()
    _attach(book, "2026-03-31", "consolidated", (_evidence(EVIDENCE_TEXT),))

    for question in RECIPE_QUESTIONS:
        candidates, result = measure(question, book)
        assert candidates == ()
        assert result.status == "abstained"
        assert result.reason == "recipe_no_extract"
        assert result.claims == ()
        assert CONSOLIDATED_VALUE not in [claim.value for claim in result.claims]


def test_compare_returns_two_claims_and_not_the_difference() -> None:
    measure, _measure_mod = _import_measure()
    book = Ledger.seed()

    candidates, result = measure(COMPARE_QUESTION, book)

    assert candidates == ()
    assert result.status == "verified"
    values = [claim.value for claim in result.claims]
    assert values == [CONSOLIDATED_VALUE, SECOND_QUARTER_VALUE]
    assert "60694190" not in values
    assert len(values) == 2


def test_compare_evidence_rows_have_no_rank() -> None:
    measure, _measure_mod = _import_measure()
    book = Ledger.seed()
    _attach(book, "2026-03-31", "consolidated", (_evidence(EVIDENCE_TEXT, digest="a"),))
    _attach(
        book,
        "2026-06-30",
        "consolidated",
        (_evidence("81.956.525", "RESULTADO NETO DEL PERÍODO", digest="b"),),
    )

    candidates, result = measure(COMPARE_QUESTION, book)

    assert [item.text for item in candidates] == [EVIDENCE_TEXT, "81.956.525"]
    assert all(item.drawer == "tables" for item in candidates)
    assert all(not hasattr(item, "rank") for item in candidates)
    assert [claim.value for claim in result.claims] == [
        CONSOLIDATED_VALUE,
        SECOND_QUARTER_VALUE,
    ]
    assert "60694190" not in [claim.value for claim in result.claims]


def test_measure_does_not_upsert(monkeypatch: pytest.MonkeyPatch) -> None:
    measure, _measure_mod = _import_measure()
    book = Ledger.seed()
    calls = {"n": 0}
    real_upsert = Ledger.upsert

    def spy_upsert(self: Ledger, claim: FinancialClaim) -> FinancialClaim:
        calls["n"] += 1
        return real_upsert(self, claim)

    monkeypatch.setattr(Ledger, "upsert", spy_upsert)
    candidates, result = measure(CONSOLIDATED_QUESTION, book)

    assert len(RECIPE_ROWS) == 14
    assert calls["n"] == 0
    assert candidates == ()
    assert result.status == "verified"
    assert [claim.ledger_status for claim in result.claims] == ["recorded"]


def test_measure_tests_do_not_import_docling() -> None:
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module)
    assert names
    assert all(name != "docling" and not name.startswith("docling.") for name in names)


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
    assert 'ID_01_VALUE = "21262335"' in v1
    assert '"21259769"' in v1
    assert "-14950948" in v2


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
