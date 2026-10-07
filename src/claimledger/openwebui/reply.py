"""Return one card string from measure then render_card."""

from __future__ import annotations

from claimledger.book.ask import ask, read_script
from claimledger.card.card import render_card
from claimledger.chart.series import draw, series_spec
from claimledger.crop.attach import attach
from claimledger.eval.measure import measure
from claimledger.ledger import Ledger
from claimledger.openwebui.text import card_text
from claimledger.orchestrate.plan import execute
from claimledger.period.difference import difference
from claimledger.query import QueryResult
from claimledger.retrieval.drawers import Candidate, retrieve


def reply(artifact_hash: str, question: str) -> str:
    series = execute(question, Ledger.seed())
    if series is None:
        series = ask(question, Ledger.seed(), read_script())
    if series is None:
        candidates, result = measure(artifact_hash, question)
        gaps: tuple[str, ...] = ()
        subtracted = difference(result)
    else:
        candidates = retrieve(artifact_hash, "tables", question)
        result = series.result
        gaps = series.gaps
        subtracted = None
    return _body(artifact_hash, candidates, result, gaps, subtracted)


def _body(
    artifact_hash: str,
    candidates: tuple[Candidate, ...],
    result: QueryResult,
    gaps: tuple[str, ...],
    subtracted: str | None,
) -> str:
    text = card_text(render_card(candidates, result, subtracted))
    images = attach(artifact_hash, result)
    body = text if not images else text + "\n" + "\n".join(images)
    chart = draw(series_spec(result, gaps=gaps))
    return body if not chart else body + "\n" + chart
