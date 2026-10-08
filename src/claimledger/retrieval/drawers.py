"""Tables and narrative drawers. One named drawer; candidates only."""

from __future__ import annotations

from typing import Literal, cast

from claimledger.card.candidate import Candidate

DrawerName = Literal["tables", "narrative"]

_DRAWERS = frozenset({"tables", "narrative"})
_TABLE_LABEL = "table"


def retrieve(
    artifact_hash: str, drawer: DrawerName, question: str
) -> tuple[Candidate, ...]:
    """Return one drawer's candidates. `question` does not drop a row."""
    chosen = _one_drawer(drawer)
    from claimledger.retrieval.read import read_hashed_json

    nodes = read_hashed_json(artifact_hash)
    return tuple(
        _candidate(node, chosen) for node in nodes if _drawer_of(node) == chosen
    )


def _one_drawer(drawer: object) -> DrawerName:
    if isinstance(drawer, str) and drawer in _DRAWERS:
        return cast(DrawerName, drawer)
    raise ValueError("name exactly one drawer: tables or narrative")


def _doc_items(node: object) -> list[object]:
    metadata = getattr(node, "metadata", None)
    if not isinstance(metadata, dict):
        return []
    items = metadata.get("doc_items")
    if not isinstance(items, list):
        return []
    return items


def _item_field(item: object, key: str) -> object:
    if isinstance(item, dict):
        return item.get(key)
    return getattr(item, key, None)


def _is_table(node: object) -> bool:
    return any(_item_field(item, "label") == _TABLE_LABEL for item in _doc_items(node))


def _drawer_of(node: object) -> DrawerName:
    if _is_table(node):
        return "tables"
    return "narrative"


def _ref_of(node: object) -> str:
    for item in _doc_items(node):
        ref = _item_field(item, "self_ref")
        if isinstance(ref, str) and ref:
            return ref
    return ""


def _candidate(node: object, drawer: DrawerName) -> Candidate:
    text = getattr(node, "text", "")
    return Candidate(drawer=drawer, text=str(text), ref=_ref_of(node))
