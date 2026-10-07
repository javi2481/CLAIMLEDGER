# Proposal: Runtime JSON Book

## Intent

After `max-docling-parse`, Docling Serve is the offline compiler and hashed JSON is the source of truth. `extract_recipe` still loads pinned `docling`/`torch` and uses `iterate_items` / `TableData`, so book/query cannot run without the Docling wheel. This change makes recipe extraction a pure dict walk over body `$ref`s with stored `data.grid` only, splits `httpx` into an `ingest` extra, and aligns CI — without touching Open WebUI `DoclingReader` / Docker `.[retrieval]`.

## Scope

### In Scope
- Pure-JSON `extract_recipe`: body DFS/BFS + `$ref` resolve (incl. nested `groups`); never enter `furniture`
- Grid = non-empty `data.grid` only; missing grid → `IngestError` (no span expansion / `TableData`)
- Remove `PINNED_DOCLING` / pin loaders / torch from extract path
- Spec delta: `docling-ingest` *Native Table Grid and Body List*
- Import-ban tests: `extract` / `ground` / book-query path free of `docling` / `docling_core` / `torch`
- `pyproject.toml`: `[project.optional-dependencies].ingest = [httpx==0.28.1]`; strip httpx from `docling`
- CI: product job docling-free extract/ground where safe; heavy job `ingest`+`docling`+`retrieval`+`http`
- Design/archive: name reply/`DoclingReader` + Dockerfile retrieval follow-up gap

### Out of Scope
- `reply.py`, `retrieval/*`, Dockerfile `.[retrieval]` uninstall
- Gold / recipe row set (`21262335` / `21259769` frozen)
- VLM / phase 10, `auditoria-stack-nativo`, Redis / async serve
- Graph pin (`PINNED_DOCLING_GRAPH`)

## Capabilities

### New Capabilities
- None

### Modified Capabilities
- `docling-ingest`: Replace *Native Table Grid and Body List* — body list from local JSON walk (not `iterate_items`); grid from stored `data.grid` only (not pinned `TableData`); no in-process Docling pin on extract; gold unchanged

## Approach

Locked exploration approach 1 (plan Option B), three apply slices:
1. **A** — Strict TDD: rewrite extract body/grid; ban Docling imports in extract sources
2. **B** — Import-scan book/ground/query path; cache-hit load stays serve-free
3. **C** — `ingest` extra + pytest workflow sync extras

Named gap: Docling libraries do not provide a runtime-free body/grid contract over hashed JSON; custom walk fills that gap only.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `src/claimledger/ingest/extract.py` | Modified | Pure JSON body walk + grid-only; drop pin/torch |
| `openspec/specs/docling-ingest/spec.md` | Modified | Native Table Grid requirement |
| `tests/ingest/test_extract.py` | Modified | Furniture/body RED; import ban; IngestError without grid |
| `tests/ingest/test_gold_compare.py` | Unchanged contract | Must stay green |
| `src/claimledger/ingest/ground.py` | Transitive | Docling-free once extract is pure |
| `pyproject.toml` | Modified | Add `ingest`; httpx off `docling` |
| `.github/workflows/pytest.yml` | Modified | Explicit extras per job |
| `reply.py` / `retrieval/*` / Dockerfile | Unchanged | Documented follow-up |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Flat walk misses nested `groups` tables | Med | Resolve `$ref` into groups; corpus sample has nested refs |
| CI breaks without `ingest` httpx | Med | Phase C before moving convert tests to light job |
| Furniture walk poisons gold | Low | Never enter furniture; gold compare gate |
| Scope creep into reply/retrieval | Med | Explicit out-of-scope + archive gap |

## Rollback Plan

Revert the change branch/PR. Restore prior `extract.py` (iterate_items + pin), prior `docling-ingest` requirement text, prior `pyproject` extras, and prior pytest workflow. Hashed artifacts and gold files are untouched — no data migration.

## Dependencies

- Approved plan: `.cursor/plans/runtime_json_book_followups.plan.md`
- Exploration: `openspec/changes/runtime-json-book/exploration.md`
- Corpus hashed JSON under `artifacts/docling/` (grids present)
- Strict TDD (`openspec/config.yaml`)

## Success Criteria

- [ ] `extract_recipe` has no `docling` / `docling_core` / `torch` / `PINNED_DOCLING`
- [ ] Body tables from JSON walk; furniture excluded; missing grid → `IngestError`
- [ ] `docling-ingest` spec matches body walk + stored-grid-only
- [ ] Book/query path import-scanned docling-free; gold green
- [ ] `ingest` extra + CI jobs aligned; full `python -m pytest` green
- [ ] Reply/retrieval Docker gap named in design/archive

## Proposal question round

Assumptions locked by plan + exploration (user may correct or request a second round):

1. **Outcome:** Product book/query/HTTP claims succeed with hashed JSON + kernel only — Docling wheel not required for that path.
2. **Rule:** Serve remains the only place that materializes grids; runtime never rebuilds from cells/spans.
3. **Slice:** First product slice ends when extract + extras/CI are green; removing `DoclingReader` from reply/image is a later change.
4. **Risk if wrong:** Nested `$ref` incompleteness under-extracts tables vs former `iterate_items` — mitigated by corpus-backed walk tests, not by reintroducing Docling.
