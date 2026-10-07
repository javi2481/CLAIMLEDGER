"""Fixed four-quarter plan. Each period goes through query. No invented bar."""

from __future__ import annotations

import ast
from pathlib import Path

from claimledger.ledger import Ledger
from claimledger.query import query

_COMPARE = "Comparar resultado neto consolidado 1T26 vs 2T26"
_SERIES = "Compará el resultado neto consolidado de los últimos 4 trimestres"
_ABSTAIN = "resultado neto de los últimos 4 trimestres en el comunicado de prensa"
_WINDOW = ("2025-09-30", "2025-12-31", "2026-03-31", "2026-06-30")
_GAPS = ("2025-09-30", "2025-12-31")


def test_named_compare_and_abstain_are_not_a_plan() -> None:
    from claimledger.orchestrate.plan import execute

    assert execute(_COMPARE, Ledger.seed()) is None
    assert execute(_ABSTAIN, Ledger.seed()) is None


def test_each_quarter_is_one_kernel_call(monkeypatch) -> None:
    import claimledger.orchestrate.plan as plan_module
    from claimledger.orchestrate.plan import execute

    calls = []

    def spy(intent, ledger):
        calls.append(intent)
        return query(intent, ledger)

    monkeypatch.setattr(plan_module, "query", spy)
    run = execute(_SERIES, Ledger.seed())

    assert run is not None
    assert [step.period for step in calls] == list(_WINDOW)
    assert [step.compare for step in calls] == [False, False, False, False]
    assert [step.scope for step in calls] == ["consolidated"] * 4
    assert [step.metric for step in calls] == ["net_income"] * 4
    assert [claim.value for claim in run.result.claims] == ["21262335", "81956525"]
    assert run.gaps == _GAPS
    assert "60694190" not in [claim.value for claim in run.result.claims]


def test_orchestrate_stays_off_kernel_and_llamaindex() -> None:
    repo = Path(__file__).resolve().parents[2]
    package = repo / "src" / "claimledger" / "orchestrate"
    for path in package.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            assert not any(
                name == "docling"
                or name.startswith("docling.")
                or name == "llama_index"
                or name.startswith("llama_index.")
                for name in names
            )

    for relative in (
        "src/claimledger/query.py",
        "src/claimledger/eval/measure.py",
        "src/claimledger/card/card.py",
        "src/claimledger/http/claims.py",
    ):
        tree = ast.parse((repo / relative).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            modules: list[str] = []
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                modules = [node.module]
            assert not any(
                name == "claimledger.orchestrate" or name.startswith("claimledger.orchestrate.")
                for name in modules
            )
