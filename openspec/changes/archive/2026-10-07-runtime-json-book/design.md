# Design: Runtime JSON Book

## Technical Approach

Proposal approach 1 / plan Option B: hashed JSON SoT; `extract_recipe` = pure body `$ref` walk (nested `groups`) + stored `data.grid` only. Slices A→B→C, Strict TDD. Spec delta: `docling-ingest` *Native Table Grid and Body List*. Named gap: Docling has no runtime-free body/grid API over hashed JSON — local walk only. No new layers.

## Architecture Decisions

| Decision | Options | Tradeoff | Choice |
|----------|---------|----------|--------|
| Body list | `$ref` walk vs `iterate_items` vs `content_layer` filter | Walk drops torch; filter misses nesting | **DFS from `payload["body"]`**; never `furniture` |
| Missing grid | `IngestError` vs `TableData` | Serve writes grids; rebuild re-pins | **Non-empty `data.grid` else `IngestError`** |
| Pin helpers | Delete vs leave | Dead code still implies pin | **Delete `PINNED_DOCLING`, `_require_pinned_docling`, `_load_pinned_docling`, `_grid_from_table_data`** |
| Reply / Docker | Remove vs gap | Plan OOS | **Unchanged**; archive follow-up |
| httpx | `ingest` extra vs under `docling` | Convert without Docling wheel | **`ingest=[httpx==0.28.1]`; strip from `docling`** |

## Data Flow

```text
hashed JSON → _body_tables (DFS $ref, #/groups→#/tables) → _table_grid(data.grid)
                    │ never furniture              │ empty/missing → IngestError
                    └──────────────────────────────▼
                                          recipe → Ledger → query
```

### Phase A — Body `$ref` walk

1. Start at `payload["body"]` only; never visit `furniture`.
2. Stack/queue + `seen` refs (cycle-safe).
3. Resolve each child `$ref` `#/<collection>/<index>` on the payload root (`groups`, `tables`, `texts`, …).
4. Collect `#/tables/N` objects once from `payload["tables"]`.
5. Recurse into nodes with `children` — **nested `groups` required** (live corpus body→groups→tables; flat fixtures still work).
6. `_table_grid`: non-empty `data.grid` list-of-rows, else `IngestError`. No `TableData` / span expansion.
7. Drop pin/torch/`importlib.metadata.version` from `extract.py`.

### Phase B — Import-scan + gap

Source/AST ban on `extract.py`, `ground.py`, book→query graph: `docling`, `docling_core`, `torch`, `PINNED_DOCLING`. No `recorded_book`/`query` API change. **Gap (design+archive):** `reply.py` → drawers → `DoclingReader`; Dockerfile keeps `.[retrieval]`.

### Phase C — Extras / CI

`ingest = ["httpx==0.28.1"]`; `docling` keeps pins only (no httpx).

| Job | Sync | Pytest |
|-----|------|--------|
| Kernel | `dev` | unchanged |
| Product w/o Docling | `dev`+`http` | http/card/chart/period/orchestrate/book/eval |
| Ingest/graph/retrieval | `dev`+`ingest`+`docling`+`retrieval`+`http` (+`deepseek` if openwebui needs) | ingest/graph/retrieval/crop/openwebui |

Keep full `tests/ingest` on the heavy job; `convert_local` mocks need `ingest` not Docling wheel.

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `src/claimledger/ingest/extract.py` | Modify | Walk + grid-only; delete pin/torch helpers |
| `openspec/specs/docling-ingest/spec.md` | Modify | Walk + stored grid / `IngestError` |
| `tests/ingest/test_extract.py` | Modify | Nested-group/furniture RED; import ban; missing-grid error |
| `tests/ingest/test_gold_compare.py` | Verify | Green; gold frozen |
| `pyproject.toml` | Modify | Add `ingest`; strip httpx from `docling` |
| `.github/workflows/pytest.yml` | Modify | Explicit extras matrix |
| `openspec/changes/runtime-json-book/design.md` | Create | This doc |
| `reply.py` / `retrieval/*` / Dockerfile | Unchanged | Gap only |

## Interfaces / Contracts

- Public `extract_recipe(stored, cls)` unchanged.
- `_body_tables` / `_table_grid` as above; spec scenarios drop `iterate_items`/`TableData` language.

## Testing Strategy (TDD order)

| Order | What | Approach |
|-------|------|----------|
| A1 RED | Furniture+body → body only | Nested `groups` fixture |
| A2 RED | No `data.grid` → `IngestError` | Cells-only table |
| A3 RED | Source ban docling/torch/PINNED | Read `extract.py` |
| A4 GREEN | Walk + grid-only + delete helpers | Min code |
| A5 | Gold / existing extract | `pytest tests/ingest` |
| B | Import-scan extract/ground/book | Same ban |
| C | CI sync extras | Workflow |

## Threat Matrix

N/A — no routing/shell/subprocess/VCS-PR/process boundary (CI only changes `uv sync --extra` lists).

## Migration / Rollout

No migration. Rollback = revert PR (extract + extras + workflow). Artifacts/gold untouched.

## Known gap (archive follow-up)

`reply.py` → RAG drawers → `DoclingReader` still requires in-process Docling. Dockerfile keeps `.[retrieval]`. This change does **not** remove that path; document at archive as deferred follow-up. Book / `extract_recipe` / `query` / HTTP claims stay import-free.

## Open Questions

- [x] Nested groups in walk — locked (corpus).
- [x] Reply/retrieval gap — document only (see Known gap).
- [ ] Product job adds `--extra ingest` only if it runs convert tests; else keep ingest tests on heavy job.
