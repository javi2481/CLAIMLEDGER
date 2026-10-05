# Proposal: Fase 1 Docling Evidence Adapter

## Proposal question round

Closed. Settled: kernel cannot read PDFs; jurado sees EEFF `21.262.335`; 10-PDF corpus; P&L from 2 EEFF only; eight classify-only; `recipe_no_extract` + gold frozen; no MinerU/VLM/Markdown-SoT; kernel tests docling-free; hashed JSON + 14 evidenced rows; gap = `Ledger.seed()`; local convert if missing; comunicado `21262335` ≠ identity; memoria year-end out of recipe; approach 1; Out non-goals; risk = gold leak from the eight.

## Intent

Add Truth-plane parse so 14 recipe rows carry hashed JSON, page, bbox, and locator from two EEFF, not seed.

## Architecture Gate

Docling is allowed because the kernel cannot read a PDF. Graph, LlamaIndex, HTTP, UI, VLM, MinerU fail the gate. Markdown is not SoT.

## Scope

**In:** parse 10 local PDFs → `artifacts/docling/<sha256>.json` (load-from-hash); grid → 14 recipe P&L from two EEFF (`BYMA`, pack/cover period); classify eight (`comunicado|deck|memoria|transcript`) with zero P&L identities; ingest tests vs gold; optional fresh-Ledger upsert; narrow AST to 7 kernel modules + 6 named `tests/test_*.py`.

**Out:** Graph, LlamaIndex, HTTP, UI, VLM, MinerU, Markdown-SoT, `press_v1`/`presentation_v1`, pack merge, memoria year-end P&L, replacing `Ledger.seed()`, `docling-graph`, lookup/query deltas, consolidado vs controlante.

## Capabilities

### New Capabilities

- `docling-ingest`: local PDF → hashed immutable DoclingDocument JSON; load-from-hash; convert locally if missing (no URL). Pin `docling==2.130.0`.
- `evidence-adapter`: grid/provenance → `FinancialEvidence` + recipe P&L from two EEFF; classify non-EEFF; ignore furniture; no consolidado/controlante.

### Modified Capabilities

- `gold-regression`: Docling-free scan = kernel files only, not `tests/ingest/` or `src/claimledger/ingest/`.

## Approach

Exploration **approach 1**. `src/claimledger/ingest/` + `tests/ingest/`. Kernel stays docling-free. JSON SoT. Gold stays `Ledger.seed()`. A/B table test, not two parsers.

## Affected Areas

- New: `src/claimledger/ingest/`, `tests/ingest/`, `artifacts/docling/`
- Modified: `tests/test_{identity,gold_v1,gold_v2}.py` (narrow AST); `openspec/specs/gold-regression/spec.md`
- Input: `docs/archivos_muestra/*.pdf`
- Pin stays: `pyproject.toml` `docling==2.130.0` (no graph import)
- Consume: `src/claimledger/{evidence,ledger}.py` (filled evidence; seed stays)
- No delta: `identity`, `ledger`, `lookup`, `query`

## Risks

- Model download / memoria ~190 pp → local `artifacts_path` + hash store
- AST break / eight mint identity → narrow scan first; classify-only
- Parse misses gold → fix mapping; never relax gold/VLM/MinerU
- Kernel gold → ingest / Graph import / furniture → keep seed; metadata pin; JSON only
- >400-line PR → `sdd-tasks` chained slices

## Rollback Plan

Delete `src/claimledger/ingest/`, `tests/ingest/`, `artifacts/docling/`. Revert AST-scan narrow. Leave kernel, seed, gold, and `recipe_no_extract`. Pin stays declared; kernel stays docling-free.

## Dependencies

Fase 0 kernel. Extra `docling==2.130.0`. Local corpus PDFs. No URLs. No `docling-graph`.

## Success Criteria

- [ ] 10 PDFs hashed; missing artifact converts locally only
- [ ] 14 EEFF recipe rows match frozen gold (values, neighbor, tax)
- [ ] Eight classified; zero P&L identities
- [ ] Kernel pytest green, docling-free, and still seeded
- [ ] Gate-failed pieces absent
