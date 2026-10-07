## Exploration: runtime-json-book

Architecture is CLOSED. Approved plan (do not edit): `.cursor/plans/runtime_json_book_followups.plan.md`. Thesis after `max-docling-parse`: Docling Serve = offline compiler; hashed JSON = SoT; CLAIMLEDGER = verification kernel. This change removes the last in-process Docling dependency from `extract_recipe` / book / query, splits `httpx` into a new `ingest` extra, and aligns CI. Open WebUI `DoclingReader` / Docker `.[retrieval]` stay out of scope (documented follow-up).

### Current State

Inspected via CodeGraph + source (not guessed).

| Area | Today | Plan target |
|------|--------|-------------|
| Body tables | `_body_tables` → pin/`torch` → `DoclingDocument.iterate_items` + `TableItem` | Walk `payload["body"]` children (resolve `$ref` into `groups` / nested nodes); collect `#/tables/N`; **never** enter `furniture` |
| Grid | Prefer `data.grid`; else `_grid_from_table_data` → `TableData.grid` | `data.grid` only (non-empty list); else `IngestError` — no span expansion |
| Pin | `PINNED_DOCLING = "2.130.0"` + `_require_pinned_docling` / `_load_pinned_docling` in `extract.py` | Remove entirely from extract path |
| Book | `recorded_book` → `load_or_convert` → `classify` → `extract_recipe` → `Ledger.upsert` | Same join; extract no longer imports docling; query stays ledger-only |
| Spec | `Native Table Grid and Body List` still requires `iterate_items` + `TableData` fallback | MODIFY: local JSON walk + stored grid only |
| Extras | `httpx==0.28.1` under `[docling]` and `[deepseek]`; no `[ingest]` | `ingest = [httpx==0.28.1]`; remove httpx from `docling` |
| CI | Product: `dev`+`http`; Ingest job: `--all-extras` | Product may run docling-free extract/ground; ingest job: explicit `ingest`+`docling`+`retrieval`+`http` (+ deepseek if needed) |
| Reply / image | `reply.py` → `retrieval.drawers` → `DoclingReader`; Dockerfile `.[http,retrieval]` | **Unchanged**; archive/design name the gap |

**Corpus evidence** (live hashed artifact under `artifacts/docling/`): `body` / `furniture` are dict nodes with `children` `$ref`s; tables are reached by resolving refs through `groups` (not only direct body children); sample file has 143 body-reachable tables, all with non-empty `data.grid`, furniture table refs = 0. Synthetic fixtures in `tests/ingest/test_extract.py` already place furniture vs body via `_document(...)`.

**Call path (product book):**

`recorded_book` → `load_or_convert` (cache hit: no serve) → `classify` → `extract_recipe` (**docling_core today**) → `query` / HTTP claims / agent tools (ledger only).

`query.py` itself has no Docling imports. Coupling is `ground` → `extract`.

### Affected Areas

- `src/claimledger/ingest/extract.py` — replace `_body_tables` / `_table_grid` / remove pin+torch+`TableData`
- `openspec/specs/docling-ingest/spec.md` — MODIFY *Native Table Grid and Body List* (+ scenarios)
- `tests/ingest/test_extract.py` — RED furniture/body walk; ban `docling`/`docling_core`/`torch`/`PINNED_DOCLING` in source; flip `iterate_items` / cells-without-grid expectations to `IngestError`
- `tests/ingest/test_gold_compare.py`, gold recipe rows — must stay green; `21262335` / `21259769` frozen
- `src/claimledger/ingest/ground.py` — no API change expected; becomes docling-free transitively once extract is pure
- `pyproject.toml` — add `[ingest]`; strip httpx from `[docling]`
- `.github/workflows/pytest.yml` — align sync extras per plan jobs
- `tests/ingest/test_convert_local.py` — needs `httpx` via `ingest` extra (not docling wheel)
- Design/archive — document reply/`DoclingReader` + Dockerfile `retrieval` follow-up gap
- Out of scope (do not edit for this change): `src/claimledger/openwebui/reply.py`, `src/claimledger/retrieval/*`, Dockerfile retrieval install, gold numeric values, graph pin (`PINNED_DOCLING_GRAPH`)

### Approaches

1. **Pure JSON body walk + grid-only (plan Option B)** — Local DFS/BFS from `payload["body"]`, resolve `$ref` against payload collections (`tables`, `groups`, …), ignore `furniture`; grid = `data.grid` or `IngestError`.
   - Pros: Matches approved thesis; removes torch/Windows pin hack from recipe; lets CI run extract without Docling wheel; corpus already has grids
   - Cons: Must correctly resolve nested groups (fixtures are flat; live JSON is nested); tests that require `iterate_items` / `TableData` must be rewritten under Strict TDD
   - Effort: Medium

2. **Keep `docling_core` for body/grid, only drop `docling` package pin** — Still imports Docling types at runtime.
   - Pros: Smaller code delta
   - Cons: Violates approved plan; torch order / pin remain; product CI still needs Docling for extract
   - Effort: Low — **rejected**

3. **Filter tables by `content_layer == "body"` without tree walk** — Skip furniture by field, ignore body tree.
   - Pros: Tiny implementation
   - Cons: Diverges from plan (“walk payload body children”); weaker equivalence to former `iterate_items` default layers; furniture-as-wrong-layer edge cases
   - Effort: Low — **rejected** as primary design

### Recommendation

Implement **approach 1** in three apply slices (A extract pure JSON → B import-scan / book path → C `ingest` extra + CI), Strict TDD, gold unchanged. Spec delta must replace *iterate_items* / *TableData* language with body walk + stored-grid-or-`IngestError`. Leave `reply` / retrieval Docker as an explicit follow-up in design and archive.

### Risks

- Nested `$ref` walk must resolve `groups` (live corpus); flat fixture-only walk would miss real tables
- Existing tests (`test_body_tables_come_from_iterate_items`, `test_cells_without_grid_match_stored_grid`, soft `TableData` asserts) will fail until rewritten — correct RED targets
- CI product job today lacks `httpx`; moving convert/extract tests without adding `ingest` (or keeping them on the heavy job) will break CI
- Dockerfile still installs `retrieval` (and not `ingest`); cold convert in-container remains a separate gap — out of scope but must be named
- Accidental gold/recipe drift if furniture walk incorrectly includes poisoned tables

### Gaps vs current code (lock checklist)

1. `extract.py` still loads pinned `docling` + `torch` and uses `DoclingDocument.iterate_items` / `TableData.grid` fallback instead of a pure body `$ref` walk + `data.grid`-only / `IngestError`.
2. Main spec *Native Table Grid and Body List* still mandates `iterate_items` and missing-grid via pinned `TableData`.
3. Extract tests still assert `iterate_items` in source and cells-without-grid success via library rebuild; no failing import-ban for `docling` / `docling_core` / `torch` / `PINNED_DOCLING`.
4. No `ingest` extra; `httpx` remains under `[docling]`; pytest workflow still uses `dev`+`http` / `--all-extras` rather than the planned `ingest`+`docling`+`retrieval`+`http` split.
5. Book/query path is still Docling-coupled through `extract_recipe`; `reply`/`DoclingReader` and Docker `.[retrieval]` intentionally untouched (follow-up gap to document in design/archive).

### Ready for Proposal

Yes. Orchestrator should run `sdd-propose` for `runtime-json-book` with the locked three-phase scope above; English OpenSpec artifacts; Strict TDD; gold `21262335` / `21259769` unchanged.
