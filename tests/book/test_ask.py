"""Book question lists periods from the script and verifies each with query."""

from __future__ import annotations

import ast
from pathlib import Path

from claimledger.book.ask import ask, periods_in_script
from claimledger.ledger import Ledger
from claimledger.query import query as real_query

_SCRIPT = """
MERGE (n:Period {id: "2026-06-30"})
SET n.period = "2026-06-30";
MERGE (n:Period {id: "2026-03-31"})
SET n.period = "2026-03-31";
"""
_BOOK = "todos los resultados netos de BYMA"
_PARENT = "todos los resultados netos de la controlante"
_COMPARE = "Comparar resultado neto consolidado 1T26 vs 2T26"
_SERIES = "Compará el resultado neto consolidado de los últimos 4 trimestres"
_REPO = Path(__file__).resolve().parents[2]


def test_other_questions_are_not_a_book() -> None:
    ledger = Ledger.seed()
    assert ask(_COMPARE, ledger, _SCRIPT) is None
    assert ask(_SERIES, ledger, _SCRIPT) is None
    assert ask("precio de cierre de YPF el 3 de enero", ledger, _SCRIPT) is None


def test_periods_follow_the_calendar() -> None:
    assert periods_in_script(_SCRIPT) == ("2026-03-31", "2026-06-30")


def test_book_question_queries_each_period(monkeypatch) -> None:
    calls = []

    def _record(intent, ledger):
        calls.append(intent)
        return real_query(intent, ledger)

    monkeypatch.setattr("claimledger.book.ask.query", _record)
    run = ask(_BOOK, Ledger.seed(), _SCRIPT)

    assert run is not None
    assert [item.period for item in calls] == ["2026-03-31", "2026-06-30"]
    assert all(item.compare is False for item in calls)
    assert [item.value for item in run.result.claims] == ["21262335", "81956525"]
    assert run.gaps == ()
    assert "60694190" not in {item.value for item in run.result.claims}


def test_parent_book_uses_parent_values() -> None:
    run = ask(_PARENT, Ledger.seed(), _SCRIPT)

    assert run is not None
    assert [item.value for item in run.result.claims] == ["21259769", "81946993"]


def test_missing_period_is_a_gap() -> None:
    script = _SCRIPT + 'SET n.period = "2026-09-30";\n'
    run = ask(_BOOK, Ledger.seed(), script)

    assert run is not None
    assert run.gaps == ("2026-09-30",)
    assert [item.value for item in run.result.claims] == ["21262335", "81956525"]
    assert "0" not in {item.value for item in run.result.claims}


def test_book_package_does_not_import_docling_or_neo4j() -> None:
    root = _REPO / "src" / "claimledger" / "book"
    for path in root.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        modules = {
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        }
        modules.update(
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        )
        lowered = " ".join(modules).lower()
        assert "docling" not in lowered
        assert "neo4j" not in lowered
    for relative in (
        "src/claimledger/query.py",
        "src/claimledger/graph/build.py",
    ):
        text = (_REPO / relative).read_text(encoding="utf-8")
        assert "claimledger.book" not in text
