"""Period edges from DocumentClass or whole filename tokens."""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from claimledger.graph.schema import Document, Issuer, Period, Statement
from claimledger.identity import normalize_period
from claimledger.ingest.classify import DocumentClass

_SEPARATORS = re.compile(r"[\s._\-]+")
_STATEMENT_KINDS = frozenset({"eeff", "comunicado", "deck"})


@dataclass(frozen=True)
class GraphSource:
    filename: str
    classified: DocumentClass
    artifact_hash: str


@dataclass(frozen=True)
class FoldedGraph:
    documents: tuple[Document, ...]
    issuers: tuple[Issuer, ...]
    periods: tuple[Period, ...]
    statements: tuple[Statement, ...]


def fold_documents(sources: Sequence[GraphSource]) -> FoldedGraph:
    issuers: dict[str, Issuer] = {}
    periods: dict[str, Period] = {}
    statements: dict[str, Statement] = {}
    documents: list[Document] = []
    for source in sources:
        issuer = _issuer(issuers, source.classified.issuer)
        period = _period(periods, _period_id(source))
        statement = _statement(statements, source.classified.kind)
        documents.append(
            Document(
                artifact_hash=source.artifact_hash,
                kind=source.classified.kind,
                issued_by=issuer,
                for_period=period,
                of_statement=statement,
            )
        )
    return FoldedGraph(
        documents=tuple(documents),
        issuers=tuple(issuers.values()),
        periods=tuple(periods.values()),
        statements=tuple(statements.values()),
    )


def _period_id(source: GraphSource) -> str | None:
    if source.classified.kind == "eeff":
        return source.classified.period
    for token in _SEPARATORS.split(Path(source.filename).stem):
        if not token:
            continue
        try:
            return normalize_period(token)
        except ValueError:
            continue
    return None


def _issuer(cache: dict[str, Issuer], issuer: str) -> Issuer:
    found = cache.get(issuer)
    if found is None:
        found = Issuer.model_validate({"issuer": issuer})
        cache[issuer] = found
    return found


def _period(cache: dict[str, Period], period: str | None) -> Period | None:
    if period is None:
        return None
    found = cache.get(period)
    if found is None:
        found = Period(period=period)
        cache[period] = found
    return found


def _statement(cache: dict[str, Statement], kind: str) -> Statement | None:
    if kind not in _STATEMENT_KINDS:
        return None
    found = cache.get("income_statement")
    if found is None:
        found = Statement(statement="income_statement")
        cache["income_statement"] = found
    return found
