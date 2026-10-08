"""Return one card string from measure then render_card, then gated prose or template."""

from __future__ import annotations

from claimledger.agent.gate import gate_prose
from claimledger.agent.loop import LoopOutcome, run as run_agent
from claimledger.agent.template import ABSTENTION_TEMPLATE
from claimledger.book.ask import ask, read_script
from claimledger.card.candidate import Candidate, candidates_from_claims
from claimledger.card.card import render_card
from claimledger.chart.series import draw, series_spec
from claimledger.crop.attach import attach
from claimledger.eval.measure import measure
from claimledger.ingest.ground import recorded_book
from claimledger.openwebui.text import card_text
from claimledger.orchestrate.plan import execute
from claimledger.period.difference import difference
from claimledger.query import QueryResult


def reply(artifact_hash: str, question: str) -> str:
    book = recorded_book()
    series = execute(question, book)
    if series is None:
        series = ask(question, book, read_script())
    if series is None:
        candidates, result = measure(question, book)
        gaps: tuple[str, ...] = ()
        subtracted = difference(result)
    else:
        result = series.result
        candidates = (
            candidates_from_claims(result.claims) if result.status == "verified" else ()
        )
        gaps = series.gaps
        subtracted = None
    body = _body(artifact_hash, candidates, result, gaps, subtracted)
    trailing = _agent_trailing(question, artifact_hash)
    return f"{body}\n{trailing}"


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


def _agent_trailing(question: str, artifact_hash: str) -> str:
    outcome = run_agent(question, artifact_hash=artifact_hash)
    return _gate_outcome(outcome, question=question, artifact_hash=artifact_hash)


def _gate_outcome(
    outcome: LoopOutcome,
    *,
    question: str,
    artifact_hash: str,
) -> str:
    if outcome.abstained or not outcome.authorized_values:
        return ABSTENTION_TEMPLATE

    def regenerate() -> str:
        again = run_agent(question, artifact_hash=artifact_hash)
        return again.content

    gated = gate_prose(
        outcome.content,
        outcome.authorized_values,
        regenerate=regenerate,
    )
    return gated.text
