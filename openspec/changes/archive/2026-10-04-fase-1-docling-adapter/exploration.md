## Exploration: Fase 1 Docling Evidence Adapter

Architecture is CLOSED. This change **adds parse**: local BYMA PDF → hashed immutable `DoclingDocument` JSON → Evidence Adapter (grid, not Markdown) → recipe P&L rows vs frozen gold. It does not invent Graph, LlamaIndex, HTTP, UI, VLM, MinerU, or Markdown-as-SoT.

### Current State

Wave A (`fase-0-kernel`) is archived. Inspected on branch `fase-0-kernel`, not guessed.

Kernel (CodeGraph: 7 modules, in-memory `Ledger` over `dict[identity_key, FinancialClaim]`):

- `src/claimledger/{identity,digits,evidence,claim,ledger,lookup,query}.py` — no `docling` import.
- `Ledger.seed()` upserts the 14 recipe rows. `query` is read-only. `recorded` ≠ `verified`.
- `FinancialEvidence.artifact_hash` / `bbox` may be empty. Gold still names `expected_source_page: 4` and locator `RESULTADO NETO DEL PERÍODO`.
- Lookup already abstains `recipe_no_extract` for memoria / comunicado / deck+P&L / contrato. That must stay.

Tests and pins:

- Kernel suite: `tests/test_{identity,ledger,lookup,query,gold_v1,gold_v2}.py`.
- AST scans in `test_identity.py` and `test_gold_*.py` walk `tests/*.py` (non-recursive) **and** `src/claimledger/*.py`. A flat `tests/test_adapter.py` or `src/claimledger/adapter.py` that imports `docling` **breaks Fase 0**.
- `pyproject.toml` already pins optional extra `docling==2.130.0` and `docling-graph==1.9.1`. Graph stays unused (Fase 2).
- Gold numbers are frozen (`21262335` vs `21259769`, tax `-14950948`, …). Kernel gold still seeds; it must not start parsing PDFs.

Corpus — **all 10** PDFs in `docs/archivos_muestra/` (user 2026-09-23). Folder READMEs still describe a Claimprint MinerU demo; that is not product.

| Class | Files |
|-------|--------|
| EEFF (recipe extract) | `BYMA_-_EEFF_31-03-2026_VF.pdf` (1T26), `BYMA - EEFF 30-06-2026.pdf` (2T26) |
| Comunicado | `BYMA_Comunicado_de_Prensa-Resultados-1T26.pdf`, `BYMA-Comunicado_de_Prensa-2T26.pdf` |
| Deck | `Presentación_de_resultados_BYMA-1T26.pdf`, `Presentacion_de_resultados_BYMA-2T26.pdf` |
| Transcript | `BYMA_2T26_Transcripcion_Resultados_ES.pdf` |
| Memoria | `Memoria-BYMA-y-EEFF-al-31-12-2023.pdf`, `BYMA-MEMORIA_2024_y_EEFF_31-12-2024.pdf`, `BYMA-MEMORIA_2025.pdf` |

Closed facts this change must not reopen:

- SoT of parse = lossless Docling JSON (`export_to_dict` / `TableData.grid` keeps spans). Markdown flattens merged cells.
- Adapter is technical, not business: `TableItem` / `TableData.grid` / `ProvenanceItem`. Ignore furniture. Add document context (issuer `BYMA`, period from pack/cover). **Does not** decide consolidado vs controlante.
- Not every row is a candidate — only recipe-recognized P&L labels.
- Comunicado/deck/memoria/transcript are **in corpus**. Lookup still abstains if the question attributes P&L to those sources. Adapter may classify them; it must not invent EEFF identity from them.
- Architecture Gate: Docling is allowed because the kernel cannot read a real PDF. Graph, LlamaIndex, HTTP, UI, VLM, MinerU are not.

### Affected Areas

- `src/claimledger/ingest/` (**create**) — parse, hashed JSON store, Evidence Adapter, document classifier. Kernel modules stay import-docling-free.
- `tests/ingest/` (**create**) — the only tests that may import `docling`. Not `tests/test_*.py`.
- `tests/test_identity.py`, `tests/test_gold_v1.py`, `tests/test_gold_v2.py` — **narrow** AST scan to `src/claimledger` kernel files + `tests/test_{identity,ledger,lookup,query,gold_v1,gold_v2}.py` (no `rglob` over `tests/` or `ingest/`).
- `openspec/specs/gold-regression/spec.md` — delta: Docling-free applies to the kernel scan, not to `tests/ingest/`.
- `pyproject.toml` — keep exact `docling==2.130.0`. Do not import `docling-graph`. Ingest tests use the `docling` extra.
- `src/claimledger/evidence.py` / `ledger.py` — consume filled `artifact_hash`, page, bbox, label from adapter; do not replace `Ledger.seed()` in kernel gold.
- `src/claimledger/lookup.py` / `query.py` — **no Fase 1 identity routes** for press/deck/memoria.
- `docs/archivos_muestra/*.pdf` — local inputs only. `artifacts/docling/<sha256>.json` — immutable parse store (new).
- Out of scope: Graph, retrieval, HTTP, UI, VLM, MinerU, `press_v1` / `presentation_v1`, year-end memoria P&L, pack merge (Fase 9).

### Approaches

1. **Ingest subpackage + hashed JSON for all 10 + extract only the two EEFF** — `src/claimledger/ingest/` + `tests/ingest/`. Parse every PDF once to `artifacts/docling/<sha256>.json`. Adapter walks `TableData.grid` on the two EEFF and emits the 14 recipe candidates (issuer/period from pack). The other eight get a document class (`comunicado` \| `deck` \| `memoria` \| `transcript`) and **zero** P&L identities. Kernel gold stays seeded. Ingest tests compare extracted rows to frozen gold (values, neighbor pair, tax sign, page/locator when present). Ledger may upsert those 14 rows with real evidence; query is unchanged.
   - Pros: smallest gate-legal path; matches rector §23 and the 10-PDF corpus rule; existing AST glob is non-recursive but the scan is narrowed on purpose; hashed JSON is the reconstruct SoT (no re-parse); lookup `recipe_no_extract` stays honest; kernel demo remains `pytest` without Docling.
   - Cons: memorias are large (~190 pages) so first parse is slow; Docling may download layout/table models unless `artifacts_path` is local; JSON blobs are bulky.
   - Effort: Medium

2. **Sibling package + extract P&L from every document** — `src/claimledger_ingest/` isolated from kernel scans; treat comunicado/deck/memoria tables as identity sources (rector §23 later example: slide appends `evidence[]`).
   - Pros: second package never touches kernel AST even before the scan narrows; pack-style evidence appears early.
   - Cons: invents EEFF identity from non-EEFF sources; fights lookup abstention and gold `recipe_no_extract`; memorias contain **year-end** EEFF (2023/2024/2025) outside the 14-row recipe; extra package is structure the rector does not name; Fase 9 work in Fase 1.
   - Effort: High — **reject**

3. **Flat kernel module + live PDF every test / parse only the two EEFF** — `src/claimledger/adapter.py` + `tests/test_adapter.py`; convert PDFs on each pytest; skip the eight non-EEFF files.
   - Pros: fewest new paths; no artifact directory.
   - Cons: **breaks** current `tests/*.py` + `src/claimledger/*.py` scans; violates “all 10 PDFs are the corpus”; live convert needs models/network and is slow/flaky; ledger would re-parse to reconstruct (forbidden by §23); two-PDF-only leaves comunicado/deck/memoria unclassified.
   - Effort: Medium (hidden cost in red kernel tests) — **reject**

Hashed-store detail (inside approach 1): persist `sha256(canonical_json)` → file; ledger points at the hash + `#/tables/n` + bbox. Tests **load JSON first**; `DocumentConverter` runs only when the artifact is missing (local, no URL). Do not use Claimprint `store.py`. Do not commit a Markdown sidecar as SoT.

### Recommendation

Take approach **1** — the smallest path the gate allows:

1. New capability lives under `src/claimledger/ingest/` (parse / hash-store / adapter / classify). Not a new product layer: it is the Evidence Adapter rector §23 already names.
2. Fase 1 tests live in `tests/ingest/`. Narrow kernel AST scans to the seven kernel modules + the six named `tests/test_*.py` files. Delta the gold-regression “Docling-Free” scenario accordingly.
3. Parse **all 10** PDFs to hashed immutable JSON. Extract recipe P&L **only** from the two quarterly EEFF. Classify the other eight; emit no P&L identity from them (even if the PDF prints `21.262.335` or a year-end estado).
4. Adapter uses `TableItem` / `TableData.grid` / `ProvenanceItem`. Ignore furniture. Document context: issuer `BYMA`, period from pack/cover (`1T26` → `2026-03-31`, `2T26` → `2026-06-30`). Recipe labels locate rows; consolidado vs controlante stays resolver + recipe, not the adapter.
5. Compare extracted 14 rows to frozen gold. Optional: upsert into a fresh `Ledger` with filled evidence. **Do not** switch `test_gold_*.py` off `Ledger.seed()`.
6. Pin stays `docling==2.130.0` (no `>=`). Standard PDF pipeline only. Table-structure A/B is a **test** that picks a winner against gold; not two production parsers. No VLM extra. No `docling-graph` import. No network URLs.
7. Strict TDD: failing ingest test first; kernel suite must stay green and docling-free after the scan narrow.

### Risks

- **Model/network on first convert.** Docling layout/table models may download. Mitigate with local `artifacts_path` and “load hashed JSON if present”. Tests must not fetch PDFs.
- **Memoria parse cost.** Three ~190-page PDFs. First-time convert is slow; hashed JSON makes later runs cheap. Still required so they are in-corpus artifacts.
- **AST / spec mismatch.** Leaving the scan as `tests/*.py` + `src/claimledger/*.py` will fail the moment ingest is flat-packaged. Narrow explicitly; do not rely on today’s non-recursive glob.
- **Gold leakage from the eight.** Comunicado/deck almost certainly repeat the neighbor numbers. Extracting them would mint identities and later collide with `recipe_no_extract`. Classify-only is the guard.
- **Parse A/B loses.** If grid/page/locator miss gold: investigate conversion/serialization/mapping. Do not relax expected values. Do not call VLM. Do not install MinerU.
- **Replacing kernel seed.** Wiring gold v1/v2 to live ingest would import Docling into the kernel demo. Forbidden.
- **Graph pin temptation.** `docling-graph==1.9.1` is declared metadata. Importing it fails the Architecture Gate (Fase 2).
- **Markdown / furniture.** `export_to_markdown` flattens spans; headers/footers pollute issuer/period. JSON + ignore furniture only.
- **400-line review budget.** Ingest + tests + artifacts will exceed one PR. `sdd-tasks` should forecast chained slices (scan narrow → hash store → EEFF extract vs gold → classify-eight). Not a design fork.

### Ready for Proposal

Yes. Architecture is closed; Fase 0 already owns identity/ledger/lookup/query/gold. Fase 1 only adds the missing Truth-plane parse. Placement, store, and extract-vs-classify are resolved above. Orchestrator should tell the user: proceed to `sdd-propose` for `fase-1-docling-adapter`; do not write product code until propose → spec → design → tasks complete.
