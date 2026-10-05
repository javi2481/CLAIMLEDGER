"""Return one card string from measure then render_card."""

from __future__ import annotations

from claimledger.card.card import render_card
from claimledger.eval.measure import measure
from claimledger.openwebui.text import card_text


def reply(artifact_hash: str, question: str) -> str:
    candidates, result = measure(artifact_hash, question)
    return card_text(render_card(candidates, result))
