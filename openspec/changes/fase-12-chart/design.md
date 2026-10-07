# Design: Phase 12 Verified Series Chart

## Technical Approach

`specs/chart`, `specs/openwebui-host`. Architecture Gate: Open WebUI already renders a Mermaid fence. The gap is that no pinned API knows which digits are verified claims. Custom code is `series_spec` and `draw` in `src/claimledger/chart/`. `query` stays unchanged. `reply` appends the fence after the card and crops.

## Architecture Decisions

| Decision | Choice | Rejected | Why |
|---|---|---|---|
| Module | `chart/series.py`; `series_spec` and `draw` | Field on `QueryResult`; code in `query`, `card`, `http/` | Verifying and drawing are two jobs. The card must not parse digits |
| Series | `verified`, at least two `recorded` claims, same issuer/statement/scope/metric/currency/unit, distinct periods | One claim; any pair; pie | One claim is a card. A pie needs parts and a total this book does not have |
| Holes | `gaps` periods absent from claims → `value is None` | `0`; copy the neighbor; abstain the whole chart | Rector: the bar stays empty. Zero would look like a verified zero |
| Fence | Mermaid `xychart-beta`. `bar` and y-axis ends are claim value strings. Identities under the fence. `Hueco:` for empty points | matplotlib; Artifact; LLM-written Mermaid | Two bars. Later rungs wait. Axis ends are copied values, not a new figure |
| Order | `sorted` by period string | Tuple order | ISO dates sort as strings. 1T26 then 2T26 |
| Labels | `2026-03-31` → `1T26`, `2026-06-30` → `2T26`. Any other period stays the period string | Invent `3T26` | The book has two quarter names |
| Title | `Resultado neto consolidado` / `controlante` for `net_income`. Other metrics keep the metric token | Widen card `_METRIC_CHIP` | Chart owns its title. The card map stays `net_income` only |
| Caller | `reply` only, after `attach` | `measure`; `render_card`; `POST /claims/query` | Host draws. HTTP stays a claim payload |

## Data Flow

```text
reply
  measure → QueryResult
  render_card + difference → card text
  attach → pictures
  series_spec(result) → ChartSpec or None
  draw → mermaid fence or ""
  return card, then pictures, then fence
```

Canonical bars: `21262335`, `81956525`. The card still shows the code difference `60694190`. The fence does not.

## File Changes

| File | Action | Description |
|---|---|---|
| `src/claimledger/chart/__init__.py` | Create | Empty marker |
| `src/claimledger/chart/series.py` | Create | Spec and fence |
| `src/claimledger/openwebui/reply.py` | Modify | Append fence when present |
| `tests/chart/test_series.py` | Create | Pair, hole, refusals, fence, no `docling`, no query import |
| `tests/openwebui/test_host.py` | Modify | Compare body gains the fence; wave C allows fase 12; allowlist excludes `chart` |
| Kernel seven, `card/`, `http/`, `query.py`, `measure.py`, gold | Unchanged | Bounds |

## Interfaces / Contracts

```python
def series_spec(result: QueryResult, gaps: tuple[str, ...] = ()) -> ChartSpec | None: ...
def draw(spec: ChartSpec | None) -> str: ...
```

`series.py` imports only `QueryResult`. `query.py` and `measure.py` never import `claimledger.chart`.

## Testing Strategy

| Layer | What to Test | Approach |
|---|---|---|
| Unit | Pair values and labels; hole `2026-09-30`; refusals; fence bar line; signed tax values copied; `60694190` absent; AST bans | In memory. No `docling`, PDF, network, Docker |
| Integration | Compare reply is card then fence; pictures then fence; single and abstain unchanged; HTTP dump has no mermaid; allowlist 13 excludes `chart` | In-process host |
| E2E | Out of scope | No container, no PDF |

## Threat Matrix

N/A — no routing, shell, subprocess, VCS/PR automation, executable-file classification, or process-integration boundary.

## Migration / Rollout

No migration. Rollback deletes `chart/` and its tests and reverts `reply.py`.

## Review Budget Forecast

Estimated apply diff ~280 lines (code ~90, tests ~190). One slice. Under the 400-line budget.

## Open Questions

None. Matplotlib and the orchestrator stay later.
