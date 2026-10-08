# Design: Reply Without Retrieval

## Technical Approach

Proposal approach 1. Card rows are display text from verified `FinancialEvidence`, not a DoclingReader index. Named gap: pinned Docling/LlamaIndex has no API that turns a verified `FinancialClaim` into card rows without `DoclingReader`. `Candidate` moves to `card/candidate.py`. `measure` and both `reply` branches build `tables` candidates from evidence. `retrieval/` stays optional offline RAG. Deltas: `verify-eval`, `claim-card`, `openwebui-host`, `docling-ingest`, `agent-host`. Strict TDD. No new library. `dependencies` stays `[]`.

## Architecture Decisions

| Decision | Options | Tradeoff | Choice |
|----------|---------|----------|--------|
| Candidate home | drawers vs `card/candidate.py` | drawers forces card to import retrieval | **`card/candidate.py`**; drawers re-exports |
| Drawer type | import `DrawerName` vs local literal | import cycles (`drawers` → card) | **`Literal["tables","narrative"]` on `Candidate`**; `DrawerName` stays in drawers |
| Row source | `retrieve()` vs evidence | retrieve constructs DoclingReader | **one `Candidate` per verified evidence item** |
| `measure` | keep `artifact_hash` vs `(question, ledger)` | hidden book load | **required `ledger`**; `understand` then `query`; drop `_quarterly_book` |
| Fewer than 2 rows | invent neighbors vs existing gate | invented rows violate the proposal | **still seal**; `_sentence` only when `len(rows)==2` |
| Search without extra | drop tool vs fail open vs `ImportError` | drop removes optional RAG | **`{hits: []}`**; `verify` alone fills `authorized_values` |
| Image extras | `.[http,retrieval]` vs `.[http,deepseek]` | retrieval installs llama-index-docling | **`.[http,deepseek]`** |

## Data Flow

```text
question + Ledger → understand → query → QueryResult
    verified → candidates_from_claims(claims) → Candidate(drawer="tables")
    abstain or evidence=() → ()
    → render_card (imports card.candidate only)
reply plan/book: same helper on series.result (no retrieve)
reply else: measure(question, book); artifact_hash stays for attach() only
search: retrieve() inside try; ImportError → {hits: []}
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `src/claimledger/card/candidate.py` | Create | `Candidate` and `candidates_from_claims` |
| `src/claimledger/card/card.py` | Modify | import `Candidate` from `card.candidate` |
| `src/claimledger/eval/measure.py` | Modify | `measure(question, ledger)`; evidence rows; no `retrieve` |
| `src/claimledger/openwebui/reply.py` | Modify | both branches use the helper; drop retrieval import |
| `src/claimledger/retrieval/drawers.py` | Modify | delete local class; import `Candidate` from card |
| `src/claimledger/agent/tools.py` | Modify | `search` catches `ImportError` |
| `Dockerfile` | Modify | `pip install ".[http,deepseek]"` |
| `tests/eval/test_measure.py` | Modify | evidence rows; no reader stub or `retrieve` spy |
| `tests/openwebui/test_host.py` | Modify | evidence or empty rows; drop neighbor-reader stub |
| `tests/card/test_render_card.py` | Modify | import `Candidate` from `card.candidate` |
| `tests/agent/test_tools.py` | Modify | `ImportError` returns empty hits |

Unchanged: `card/__init__.py` (no re-export), `pyproject.toml` `retrieval` extra, `retrieval/` tests, kernel allowlist, gold, CI job that still installs `retrieval` for `tests/retrieval`.

## Interfaces / Contracts

```python
@dataclass(frozen=True)
class Candidate:
    drawer: Literal["tables", "narrative"]
    text: str
    ref: str

def candidates_from_claims(claims: tuple[FinancialClaim, ...]) -> tuple[Candidate, ...]:
    # text = item.text or item.label; ref = item.artifact_hash; drawer = "tables"
```

`measure(question: str, ledger: Ledger) -> tuple[tuple[Candidate, ...], QueryResult]` returns `(candidates_from_claims(result.claims) if result.status == "verified" else (), result)`. Callers pass the book; `reply` already has `recorded_book()`.

`search` imports `retrieve` inside the function. `ImportError` returns `{"hits": []}`. `loop._execute_tool` extends `authorized_values` only when `name == "verify"`.

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | builder; seal with 0–1 rows; two-row sentence absent | pytest; no docling |
| Unit | `measure`: understand then query; seed `evidence=()` → `()` | no `retrieve` spy |
| Integration | reply plan/book/query | evidence text and frozen values |
| Unit | `search` `ImportError` | monkeypatch `retrieve` to raise |
| E2E | none | no browser runner |

RED before production edits. Gold numbers stay frozen.

## Threat Matrix

N/A — no new routing, shell, subprocess, VCS/PR automation, executable-file classification, or process-integration boundary. The Dockerfile only changes an existing pip extra list.

## Migration / Rollout

No migration. Rollback: restore `retrieve` in `measure` and `reply`, `Candidate` in drawers, and Dockerfile `.[http,retrieval]`. `retrieval/` stays in tree.

## Open Questions

- [ ] None. Spec deltas stay with sdd-spec; this design follows the proposal.
