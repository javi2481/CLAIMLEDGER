## Exploration: fase-3-retrieval

Architecture is CLOSED. This change indexes hashed Docling JSON into **two drawers** — tables (numbers) and narrative (explain later) — and returns **candidates**. It does not answer, verify, or write a claim. `DoclingReader` must be constructed with `export_type="json"`. The Reader default is markdown and is forbidden as source of truth. Mixing the drawers is the neighbor-row failure mode.

### Current State

Wave A (`fase-0-kernel`) and Wave B Fase 1 (`fase-1-docling-adapter`) and Fase 2 (`fase-2-graph-ingest`) are archived. Inspected on branch `fase-0-kernel`. Fase 1 and Fase 2 product files are on disk and **uncommitted**. Do not commit them in this change. Do not start Fase 4.

Kernel (CodeGraph: seven modules; `query` is a read of `Ledger`, not a search of document structure):

- `src/claimledger/{identity,digits,evidence,claim,ledger,lookup,query}.py`. `src/claimledger/__init__.py` is empty and is not part of the scan. Ingest and graph are not re-exported from it.
- `query(intent, ledger)` returns `verified` or `abstained` from recorded claims. It does not load Docling JSON, does not rank rows, and does not return an unverified candidate list.
- `Ledger.seed()` still owns kernel gold. Numeric expectations stay frozen (`21262335` consolidated vs `21259769` parent). Narrative gold `na-*` stays `"skip": true`.

Fase 1 ingest (outside the kernel scan):

- `src/claimledger/ingest/{__init__,types,store,parse,classify,extract}.py`. Canonical artifact is hashed Docling JSON: `artifacts/docling/<sha256>.json`, written by `canonical_json_bytes` + SHA-256. `store.load(artifact_hash)` reads that object. `parse.convert_pdf` lazy-imports `docling==2.130.0` and stores `export_to_dict()`.
- `extract_recipe` walks `#/tables/` body items (furniture ignored) and mints claims only for the two quarterly EEFF. That is recipe extraction, not retrieval. Comunicado, deck, memoria, and transcript still mint zero P&L identities.
- `tests/ingest/test_store.py` globs `src/claimledger/ingest/*.py` (non-recursive), asserts that exact six-file list, and forbids source tokens `HttpSource`, `docling-graph`, `docling_graph`, `http://`, `https://`. `parse.py` may import `docling` and must not import a `graph` module.

Fase 2 graph (sibling package, also outside the scan):

- `src/claimledger/graph/` may import `docling-graph==1.9.1` lazily inside `build`. Nodes are Document, Issuer, Period, Statement. Document id is `artifact_hash`. `FinancialClaim` stays in the ledger. `query` does not rebuild the graph.
- `tests/test_identity.py::test_graph_init_outside_kernel_allowlist` asserts `len(allowlist) == 13` and that `src/claimledger/graph/__init__.py` is not on it.
- `test_kernel_modules_importable` snapshots `sys.modules` for `docling` and `docling_graph` around the seven kernel imports. A later graph load must not fail that check.

Gold-regression (`openspec/specs/gold-regression/spec.md`, Docling-Free Pytest Demo): the 13 paths are the seven kernel modules plus `tests/test_{identity,ledger,lookup,query,gold_v1,gold_v2}.py`. Those MUST NOT import `docling` or `docling-graph`. `ingest/` MAY import `docling==2.130.0` and MUST NOT import `docling-graph`. `graph/` and `tests/graph/` MAY import `docling-graph==1.9.1`. `FORBIDDEN_IMPORT_ROOTS` in the kernel tests is `{"docling", "docling_graph"}` only. Nothing in `src/` imports `llama_index` today.

**LlamaIndex pin:** none in `pyproject.toml`. `[project].dependencies` is `[]`. Optional extra `docling` lists only `docling==2.130.0` and `docling-graph==1.9.1`. `docs/stack-oportunidades.md` records a **tentative** note `llama-index-readers-docling==0.5.0` (“validar contra Docling 2.130 en Fase 3”). That sentence is not a project pin. This exploration does not lock a version.

What the kernel, ingest, and graph cannot do, and why LlamaIndex passes the Architecture Gate (§24) **only as retrieval over structure**: `query` looks up an already resolved intent in the ledger. `extract_recipe` maps a closed recipe onto EEFF grids. The graph folds document identity. None of them answers “where are the candidate table rows, kept apart from narrative, for this question?” Rector §6, §12, and §20 require that search: both neighbor figures (`21.262.335` and `21.259.769`) come back as candidates; the kernel later chooses. Markdown flattens merged cells and is how a chat eats the adjacent row. Orchestration, HTTP, Open WebUI, VLM, MinerU, Neo4j, and an agent that skips the kernel do **not** pass for this change.

### Affected Areas

- `src/claimledger/retrieval/` (**create**, sibling of `ingest/` and `graph/`) — index hashed JSON with `DoclingReader(export_type="json")` and `DoclingNodeParser`; two drawers; retrieve candidates. Not one of the seven kernel modules.
- `tests/retrieval/` (**create**) — retrieval tests. Not `tests/test_*.py`. Not `tests/ingest/`. Not `tests/graph/`.
- `openspec/specs/gold-regression/spec.md` — later delta only: name the retrieval package as outside the 13-path scan; kernel and ingest seals stay. Do not add retrieval paths to the allowlist.
- `pyproject.toml` — no LlamaIndex pin exists. A later phase may add one after validating it against `docling==2.130.0`. Do not invent the version in explore.
- `src/claimledger/ingest/` — **read**. Source of hashed JSON via `store.load`. Do not add a seventh ingest module. Do not import `llama_index` or `docling_graph` here.
- `src/claimledger/graph/` — **read**. Document identity stays here. Retrieval does not rebuild the graph and does not import `docling-graph` unless a later spec proves the graph package is the wrong reader (it is not).
- `src/claimledger/query.py` and the other six kernel modules — **unchanged**. Retrieval must not be imported from them. `query` still does not verify index hits.
- `src/claimledger/__init__.py` — stays empty. Do not re-export retrieval.
- Out of scope paths: Fase 4 verify/eval, HTTP, Open WebUI, VLM, MinerU, Neo4j, orchestrator, workflows, agents.

### Approaches

1. **Sibling `src/claimledger/retrieval/` + `tests/retrieval/`, two drawers over hashed JSON** — Read `artifacts/docling/<hash>.json` (the Fase 1 store). Force `DoclingReader(export_type="json")` into `DoclingNodeParser`. Split nodes into a **tables** drawer (numbers; neighbor rows stay separate candidates) and a **narrative** drawer (explain later; not a number source). Retrieve returns candidates only. Lazy-import LlamaIndex inside this package, same pattern as `convert_pdf` / `graph.build`. Kernel `__init__.py` stays empty. Ingest file list and forbid-scan stay. The 13-path allowlist stays. Graph stays the only `docling-graph` importer.
   - Pros: matches §6 / §15 row Fase 3 / §20 “Cuando buscamos” / §24; keeps Markdown off the SoT; keeps the neighbor rows from sharing one mixed bag; survives the AST allowlist and the ingest forbid-scan; same boundary Fase 2 already proved for graph.
   - Cons: a third subpackage; gold-regression needs a sentence that retrieval is outside the scan; kernel tests do not name `llama_index` in `FORBIDDEN_IMPORT_ROOTS` today, so the seal is “do not import it from the 13 paths,” not a new forbidden root, unless propose adds that root without widening the path set; no project pin yet.
   - Effort: Medium

2. **Put indexing inside `src/claimledger/ingest/`** — Reader and drawers next to `store.py` / `extract.py`.
   - Pros: one Truth-plane package; the 13-path scan already ignores `ingest/`.
   - Cons: `openspec/specs/docling-ingest/spec.md` says LlamaIndex MUST NOT be used in ingest. A seventh `ingest/*.py` file fails the exact six-file list in `test_ingest_sources_forbid_url_httpsource_and_docling_graph`. A nested package that dodges the glob is a hole. It couples the sealed parser to a reader whose default export is markdown, and it sits beside `extract_recipe`, which already interprets tables as claims. Retrieval must not become a second extractor.
   - Effort: Medium — **reject**

3. **Put retrieval in one of the seven kernel modules (especially `query.py`), or one mixed index, or orchestration now** — search inside `query`, a single bag of table+narrative nodes, or a LlamaIndex workflow/agent that returns the number.
   - Pros: fewer packages, or the library can also orchestrate.
   - Cons: retrieval inside the seven kernel modules is forbidden. Importing `llama_index` or `docling` there fails the spirit of the 13-path scan (and fails the AST scan if those roots are imported). One mixed drawer is the neighbor-row failure mode in §20. Orchestration, HTTP, Open WebUI, and an agent that skips the kernel fail §24 for Fase 3. `query` returning `verified` from the index would skip the kernel contract and start Fase 4.
   - Effort: High — **reject**

### Recommendation

Take approach **1**.

1. New code lives in `src/claimledger/retrieval/` and `tests/retrieval/`. Do not add files under the seven kernel modules, under `ingest/`, or under `graph/`.
2. Input is the hashed Docling JSON already stored by Fase 1 (`store.load` / `artifacts/docling/<artifact_hash>.json`). Do not re-parse the PDF as the retrieval source of truth. Do not persist Markdown.
3. Call `DoclingReader` with `export_type="json"` (override the markdown default), then `DoclingNodeParser`. Two drawers: tables for numbers, narrative for later explanation. A query for a number reads the tables drawer. Narrative nodes must not be merged into that drawer.
4. The public result of this phase is a **candidate list** (both neighbor rows may appear). It is not a `QueryResult`, not `verified` / `abstained`, and not a ledger write. `query.py` stays the judge and is not wired here.
5. Keep the 13-path equality set and the ingest six-file forbid-scan (no `docling-graph` in ingest). Kernel tests MUST NOT import `docling`. Prefer they also do not import `llama_index` by never importing retrieval from those modules. Adding `llama_index` to `FORBIDDEN_IMPORT_ROOTS` is optional and must not grow the path set. `graph/` remains the only package that may import `docling-graph`.
6. Do not treat `llama-index-readers-docling==0.5.0` as pinned. `pyproject.toml` has no LlamaIndex pin. Propose may validate a pin against `docling==2.130.0`; this phase does not choose a version that was not read from the project file.
7. Strict TDD when apply starts. This explore does not write tests or production code.

### Non-goals

- Fase 4–5 verify, eval, and the measured neighbor trap (`retrieval → query`).
- Orchestration, workflows, agents, or any path that skips the kernel.
- HTTP `POST /claims/query`, Open WebUI, ficha, pipelines.
- VLM, MinerU, Neo4j, a second parser, OCR changes.
- Markdown as retrieval source of truth, or leaving `DoclingReader` on its markdown default.
- One mixed drawer of tables and narrative.
- Answering, verifying, or upserting a claim from retrieval.
- Relaxing gold numbers; running `na-*`; replacing `Ledger.seed()`.
- Putting retrieval inside the seven kernel modules or inside `ingest/`.
- Rebuilding the Fase 2 graph on a question. Importing `docling-graph` from retrieval or ingest.
- Committing uncommitted Fase 1 or Fase 2 files. Starting Fase 4.

### Risks

- **Reader default is markdown.** Shipping `DoclingReader()` without `export_type="json"` flattens table cells and recreates the neighbor-row bug. The override has to be tested, not assumed.
- **Mixed drawers.** One index that returns a narrative chunk beside `21262335` / `21259769` is the failure mode §20 names. Drawer split is the requirement, not an optimization.
- **Retrieval mistaken for the judge.** §12 step 1 is candidates; steps 2–5 are the kernel. Returning `verified` here starts Fase 4 and can skip the kernel.
- **Ingest seal.** A new file under `src/claimledger/ingest/` fails the six-file inventory. Do not weaken that test to “allow LlamaIndex.”
- **13-path allowlist.** Importing LlamaIndex from `query.py` or another scanned module breaks the kernel demo. Keep retrieval off that set. The current forbidden roots do not include `llama_index`; absence depends on placement until a spec adds the root.
- **No project pin.** `pyproject.toml` does not pin LlamaIndex. The `0.5.0` line in `docs/stack-oportunidades.md` is tentative. Applying an unvalidated pin, or inventing another version, is out of this phase.
- **Docling import transitively.** A retrieval test that loads the Reader will import `docling`. The kernel snapshot in `test_kernel_modules_importable` must stay a before/after check of the seven modules. Do not widen it back to a process-global ban, and do not let retrieval code run inside those imports.
- **Second extractor.** `extract_recipe` already emits EEFF claims from table grids. Retrieval indexes structure for search. It must not mint identities, rewrite gold, or replace the recipe.
- **Uncommitted Fase 1 and Fase 2.** Ingest, graph, and their tests are on disk beside the archives. Do not commit them with this change.
- **400-line review budget.** Package, JSON override, two drawers, and a gold-regression sentence may need slices. `sdd-tasks` should forecast that. Not a design fork.

### Ready for Proposal

Yes. Package placement, the JSON override, the two drawers, and the candidate-not-answer boundary are resolved. Orchestrator should run `sdd-propose` for `fase-3-retrieval` and should not write product code, specs, design, or tasks in this phase. Do not start Fase 4. Do not commit.
