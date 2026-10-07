# Design: Phase 13 Fixed Plan Around the Kernel

## Technical Approach

`specs/orchestrate`, `specs/openwebui-host`. Architecture Gate: the 1T vs 2T compare is already one `query`. The compound question needs four kernel calls and two holes. Pinned LlamaIndex does not do that. Custom code is the fixed window and the fan-in. No workflow package, no LLM.

## Architecture Decisions

| Decision | Choice | Rejected | Why |
|---|---|---|---|
| Module | `orchestrate/plan.py`; `execute(question, ledger) -> SeriesRun \| None` | Package named as an agent swarm; LlamaIndex Workflow | The plan is known. The pinned extras only read Docling JSON |
| Cue | Folded `ultimos` and `trimestre`, plus `4` or `cuatro` | Every compare; every question | Level 1 and the two-quarter compare stay on `measure` |
| Window | Four quarter-ends ending at `PERIOD_2T26` | A model inventing dates; only the two book periods | The asked count is four. The book can confirm two |
| Step | `Intent` copied from `understand`, `compare=False`, one period, then `query` | One compare Intent; threads | Same engine, deterministic join in period order |
| Holes | Non-verified steps become `gaps` for `series_spec` | `0`; drop the period; abstain the whole series | Rector: the bar stays empty |
| Card | Verified claims only. No difference line on this path | Print `60694190` beside two holes | That line is the two-period difference, not a four-quarter series |
| Caller | `reply` only | `POST /claims/query`; `measure` | Plano B. The HTTP route stays one `query` |
| Join | In period order in the calling thread | A thread pool | Four pure lookups. Order is the contract |

## Data Flow

```text
reply
  execute(question, Ledger.seed())
    understand → identity or None
    for period in window: query(step, ledger)
    SeriesRun(verified claims, gap periods) or None
  if None: measure → card → difference → fence
  else: retrieve → card without difference → fence with gaps
```

## File Changes

| File | Action | Description |
|---|---|---|
| `src/claimledger/orchestrate/__init__.py` | Create | Empty marker |
| `src/claimledger/orchestrate/plan.py` | Create | Cue, window, per-period `query` |
| `src/claimledger/openwebui/reply.py` | Modify | Branch on `execute` |
| `tests/orchestrate/test_plan.py` | Create | Cue, four calls, values, holes, AST |
| `tests/openwebui/test_host.py` | Modify | Compound reply; wave C allows fase 13; allowlist excludes `orchestrate` |
| `query.py`, `measure.py`, `chart/series.py`, `http/`, gold | Unchanged | Bounds |

## Interfaces / Contracts

```python
@dataclass(frozen=True)
class SeriesRun:
    result: QueryResult
    gaps: tuple[str, ...]

def execute(question: str, ledger: Ledger) -> SeriesRun | None: ...
```

`plan.py` may import `understand`, `Intent`, `query`, `QueryResult`, and `Ledger`'s caller-supplied book. It does not import `docling` or `llama_index`.

## Testing Strategy

| Layer | What to Test | Approach |
|---|---|---|
| Unit | Cue refusals; four `query` calls with `compare` false; values `21262335`, `81956525`; gaps; AST | In memory. Monkeypatch `query` to record intents |
| Integration | Compound reply has the bar and both holes and no `60694190`; HTTP dump has no mermaid; allowlist 13 | In-process host, stubbed reader |
| E2E | Out of scope | No container |

## Threat Matrix

N/A — no routing, shell, subprocess, VCS/PR automation, executable-file classification, or process-integration boundary.

## Migration / Rollout

No migration. Rollback deletes `orchestrate/` and reverts `reply.py`.

## Review Budget Forecast

Estimated apply diff ~320 lines (code ~110, tests ~210). One slice. Under the 400-line budget.

## Open Questions

None. Analysis prose and matplotlib stay out.
