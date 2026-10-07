# Design: Phase 11 Cypher Export of the Book

## Technical Approach

`specs/book`, `specs/document-graph`, `specs/openwebui-host`. Architecture Gate: `query` abstains when two periods match and none was named. The Cypher script already lists the periods. Pinned `CypherExporter` writes that script and does not open Neo4j. Custom code is the call plus reading `n.period` lines, because no pinned extra runs the script.

## Architecture Decisions

| Decision | Choice | Rejected | Why |
|---|---|---|---|
| Export | `CypherExporter().export` inside `_export`, sibling `graph.cypher` | A hand-written `MERGE` writer; a Neo4j driver | The pin already emits the script. Tests cannot start a server |
| Ban | Allow the `CypherExporter` import only | Keep the phase 2 name ban | Phase 2 was before this export. The driver and `FinancialClaim` stay banned |
| Cue | Folded `todos` + `resultado` + `neto` | Changing `understand` to accept the plural | `query` and `understand` stay as they are. The plural still means consolidated net income |
| Periods | Regex on `n.period = "..."` then sort | Parse every Cypher statement; read `graph.json` as the book | The script is what Neo4j would load. JSON stays the ingest artifact |
| Numbers | One `query` per period, `compare` false | Put values on Period nodes | Lookup stays the truth |
| Gaps | Unverified periods become `gaps` | `0`; drop them silently from the fence | A named period with no claim is a hole |
| Caller | `reply` after `execute` returns nothing | `POST /claims/query` | The route stays one `query` and abstains |
| Module | `book/ask.py` | Code inside `graph/` that imports `query` | `graph/` must not name `FinancialClaim` |

## Data Flow

```text
build
  JSONExporter → graph.json
  CypherExporter → graph.cypher

reply
  execute → four-quarter run or nothing
  ask(question, ledger, script)
    periods from n.period
    query once per period
  if nothing: measure → card
  else: card without the difference line → fence
```

## File Changes

| File | Action | Description |
|---|---|---|
| `src/claimledger/graph/build.py` | Modify | Call `CypherExporter` |
| `src/claimledger/book/__init__.py` | Create | Empty marker |
| `src/claimledger/book/ask.py` | Create | Cue, period lines, per-period `query` |
| `src/claimledger/openwebui/reply.py` | Modify | Branch on `ask` |
| `tests/graph/test_store.py` | Modify | Script file, digits absent, exporter allowed |
| `tests/book/test_ask.py` | Create | Cue, two calls, parent, gap, AST |
| `tests/openwebui/test_host.py` | Modify | Book reply, HTTP abstain, wave C allows fase 11 |

## Interfaces / Contracts

```python
@dataclass(frozen=True)
class BookRun:
    result: QueryResult
    gaps: tuple[str, ...]

def ask(question: str, ledger: Ledger, script: str) -> BookRun | None: ...
def read_script() -> str: ...
```

`ask` may import `understand`, `Intent`, `query`, and `Ledger`. It does not import `docling` or `docling_graph`. `read_script` reads `graph_json_path().with_suffix(".cypher")` and returns `""` when the file is missing.

## Testing Strategy

| Layer | What to Test | Approach |
|---|---|---|
| Unit | Exporter file; cue refusals; two `query` calls; parent values; gap; AST | In memory. Graph build uses the existing fixture, no PDF |
| Integration | Book reply has the bar and no `60694190`; missing script abstains; HTTP abstains; allowlist 13 | In-process host, stubbed reader, script string |
| E2E | Out of scope | No Neo4j container |

## Migration / Rollout

No migration. Rollback deletes `book/` and removes the exporter call.

## Review Budget Forecast

Estimated apply diff under 400 lines. One slice.

## Open Questions

None. A live Neo4j stays out.
