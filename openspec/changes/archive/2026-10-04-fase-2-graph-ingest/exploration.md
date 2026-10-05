## Exploration: fase-2-graph-ingest

Architecture is CLOSED. This change writes a **simple ingest-time graph** (Document, Issuer, Period, Statement) so documents of the same period can share stable IDs the kernel already resolved. `FinancialClaim` stays in the ledger. No P&L extraction in the graph. No rebuild on a question. Zero LLM.

### Current State

Wave A (`fase-0-kernel`) and Wave B Fase 1 (`fase-1-docling-adapter`) are archived. Inspected on branch `fase-0-kernel`. Fase 1 product files are on disk and **uncommitted**. Do not commit them in this change.

Kernel (CodeGraph: seven modules, in-memory `Ledger` over `dict[identity_key, FinancialClaim]`):

- `src/claimledger/{identity,digits,evidence,claim,ledger,lookup,query}.py`. `src/claimledger/__init__.py` is empty and is not part of the scan.
- `identity_key` is `issuer|period|statement|scope|metric`. Canonical period IDs are `PERIOD_1T26` = `2026-03-31` and `PERIOD_2T26` = `2026-06-30`. `normalize_period` already maps `1t26` / `2t26` (and the Spanish month phrases) onto those IDs. `apply_alias` is a closed table; an unknown alias raises `KeyError`.
- Issuer constant `BYMA`. Statement constant `income_statement` (`lookup.STATEMENT_INCOME` and `ingest.extract._STATEMENT`).
- `Ledger.upsert` folds evidence when the **claim** value matches and sets `ledger_status="conflicted"` when it does not. That is claim-value conflict, not document merge. `Ledger.seed()` still owns kernel gold. `query` is read-only. Lookup still abstains `recipe_no_extract` for comunicado / deck / memoria P&L questions.

Fase 1 ingest (outside the kernel scan):

- `src/claimledger/ingest/{types,store,parse,classify,extract}.py`. Hashed Docling JSON at `artifacts/docling/<sha256>.json`. Pin in use: `docling==2.130.0` inside `parse.convert_pdf` (lazy import).
- `classify` sets `issuer="BYMA"` for every corpus PDF and sets `period` **only** for the two quarterly EEFF. Comunicado, deck, memoria, and transcript keep `period=None` on purpose (`tests/ingest/test_classify.py`). They mint zero P&L identities. `extract_recipe` returns claims only for quarterly EEFF.
- `tests/ingest/test_store.py` globs `src/claimledger/ingest/*.py` (non-recursive), asserts that exact six-file list, and forbids the source tokens `docling-graph` and `docling_graph`.
- Main spec `openspec/specs/gold-regression/spec.md` (Docling-Free Pytest Demo): the seven kernel modules and six named tests MUST NOT import `docling` or `docling-graph`. `ingest/` MAY import `docling==2.130.0` and MUST NOT import `docling-graph`.

Pins (`pyproject.toml` optional extra `docling`): `docling==2.130.0` and `docling-graph==1.9.1`. The graph pin is declared and unused. Kernel AST allowlist is an **equality set of 13 paths** in `tests/test_{identity,gold_v1,gold_v2}.py` (7 modules + `tests/test_{identity,ledger,lookup,query,gold_v1,gold_v2}.py`). A new package is safe only while it stays off that set and off the ingest source inventory.

`test_identity.py::test_kernel_modules_importable` also asserts `"docling_graph" not in sys.modules` for the **whole process**, not only as a result of importing the seven modules.

What the kernel cannot do, and why Graph passes the Architecture Gate (§24): the ledger merges **claims** that already share a five-field key. It has no Document / Issuer / Period / Statement book that can fold EEFF + comunicado + deck of one period without minting a `FinancialClaim`. Classify deliberately withholds period on the non-EEFF files so they cannot become P&L identity. That gap is document identity, not retrieval and not a second claim extractor.

Rector tension, resolved for this change: §6 and §8 describe `graph_id_fields` as the five claim fields. §15 Fase 2, §20, and §24 lock the MVP graph to Document / Issuer / Period / Statement and leave `FinancialClaim` outside. This change follows §15 / §24. Scope, metric, and value stay in the ledger.

Docling Graph 1.9.1 (research notes in-repo, not a new design): same-ID merge folds nodes and **records** conflicts; provenance bookkeeping is deterministic and is not an LLM call. The library also ships LLM/VLM extraction (`run_pipeline`, model config) and Neo4j export. Those paths fail this change's zero-LLM lock and the Fase 11 / Fase 13 gates.

### Affected Areas

- `src/claimledger/graph/` (**create**, sibling of `ingest/`) — simple graph built at ingest from kernel IDs plus `StoredDocument` / `DocumentClass`. The only production tree that may import `docling_graph`.
- `tests/graph/` (**create**) — graph tests. Not `tests/test_*.py`. Not `tests/ingest/`.
- `openspec/specs/gold-regression/spec.md` — delta only: graph package MAY import `docling-graph==1.9.1`; kernel scan and `ingest/` stay forbidden. Do not add graph paths to the 13-path allowlist.
- `tests/test_identity.py` — possible narrow of the process-global `sys.modules` check so a later `pytest tests/` can import the graph library without failing the kernel demo. AST allowlist stays.
- `src/claimledger/ingest/` — **read**, do not teach it `docling_graph`. Do not change `DocumentClass.period` for comunicado/deck (Fase 1 tests freeze `None`).
- `src/claimledger/{identity,lookup,ledger,query}.py` — **read**. Reuse `BYMA`, `normalize_period`, `income_statement`. Do not import the graph package from these modules.
- `pyproject.toml` — pin already `docling-graph==1.9.1`. No version bump.
- `artifacts/graph/` (**create at apply**, gitignored) — ingest-time graph artifact, separate from hashed Docling JSON.
- Out of scope paths: LlamaIndex, HTTP, Open WebUI, VLM, MinerU, Neo4j, orchestrator, `press_v1`, `presentation_v1`.

### Approaches

1. **Sibling `src/claimledger/graph/` + `tests/graph/`, deterministic graph only** — Pydantic entities Document, Issuer, Period, Statement. IDs come from the kernel (`BYMA`, `normalize_period` / the two quarterly period constants, `income_statement`) and from `StoredDocument.artifact_hash`. Document→Period for comunicado and deck is a **graph edge**, not a write to `DocumentClass.period`. Same ID folds; a disagreeing attribute is stored as a conflict. Unknown period/alias is a recorded human-in-the-loop doubt, not an LLM guess and not a dropped document. Build once at ingest. `query` does not rebuild. `docling_graph` is imported lazily inside the builder (same pattern as `convert_pdf`). No `run_pipeline`, no LLM config, no VLM, no Neo4j.
   - Pros: kernel allowlist and the ingest six-file forbid-scan stay green; matches the sealed “ingest MUST NOT import docling-graph” sentence; uses the pin for the job the kernel cannot do (document merge); claim gold and `recipe_no_extract` stay untouched.
   - Cons: a second subpackage; gold-regression needs a one-sentence permission for that package; full-suite `sys.modules` check is order-sensitive unless narrowed; docling-graph must be installed for graph tests only.
   - Effort: Medium

2. **Extend `src/claimledger/ingest/` with `graph.py` (or `ingest/graph/`)** — same entities, living next to parse/classify/extract.
   - Pros: one Truth-plane package; kernel 13-path scan still ignores `ingest/`; a nested subpackage would even dodge today's non-recursive `*.py` glob.
   - Cons: breaks `test_ingest_sources_forbid_url_httpsource_and_docling_graph` (exact file list plus forbidden tokens) and the main gold-regression requirement that ingest MUST NOT import `docling-graph`. A nested package that “passes” the glob is a hole, not a design. Mixes the sealed parser with the graph library. Importing graph from `ingest/__init__.py` would load `docling_graph` for every ingest caller.
   - Effort: Medium — **reject**

3. **Put nodes in the seven kernel modules, or call the LLM/VLM pipeline, or hand-roll a dict, or use Neo4j** — `graph.py` beside `ledger.py`, `run_pipeline` over the PDFs, or a database.
   - Pros: fewer packages, or “the library already extracts”.
   - Cons: a kernel module that imports `docling_graph` fails the 13-path AST scan and `test_kernel_modules_importable`. LLM/VLM extraction violates zero-LLM and “do not extract the P&L”. A hand-rolled dict ignores the declared pin and reimplements merge the rector says not to reimplement. Neo4j is Fase 11 and fails the gate. Rebuilding on `query` violates §15 and §22.
   - Effort: High — **reject**

### Recommendation

Take approach **1**.

1. New code lives in `src/claimledger/graph/` and `tests/graph/`. Kernel `__init__.py` stays empty. Ingest `__init__.py` does not re-export the graph.
2. Entities are only Document, Issuer, Period, Statement. `FinancialClaim` (scope, metric, value, evidence) is not a graph node. Do not call `extract_recipe` to populate the graph.
3. Stable IDs already resolved by the kernel: issuer `BYMA`; period `2026-03-31` or `2026-06-30` via `normalize_period` when the filename token is one the kernel knows; statement `income_statement` for the quarterly pack. Document id is `artifact_hash`.
4. Merge EEFF + comunicado + deck of the same period onto those shared Issuer / Period / Statement nodes. Same ID folds. A conflict is stored on the node. Do not overwrite and do not hide it. Do not reuse `ledger_status="conflicted"` for this; that flag stays a claim-value fact inside `Ledger`.
5. Leave `classify` unchanged (`period=None` on non-EEFF). The graph reads the filename through `normalize_period` when linking Document to Period.
6. An unresolved alias or period token is a recorded doubt for a human. No LLM. Year-end memoria stays a Document and does not fold into `2026-03-31` / `2026-06-30`. The 2T26 transcript may attach to Period `2026-06-30` because `normalize_period` already resolves that token; it still mints no claim.
7. Persist the graph once next to ingest (`artifacts/graph/`, not inside the hashed Docling JSON). Questions only read it. `Ledger.seed()` and kernel gold stay the demo.
8. Use docling-graph **graph management** (schema, stable id, deterministic merge, provenance bookkeeping) at pin `1.9.1`. Do not call extraction backends.
9. Strict TDD. Graph tests live under `tests/graph/`. If verify runs `pytest tests/`, narrow `test_kernel_modules_importable` so it asserts that **importing the seven kernel modules** does not load `docling` or `docling_graph`, instead of asserting a process-global absence. Do not widen the 13-path allowlist.

### Non-goals

- Fase 3 retrieval, LlamaIndex, `DoclingReader`, dense or sparse indexes.
- HTTP, Open WebUI, ficha, pipelines.
- VLM, MinerU, OCR changes, a second PDF parser.
- Neo4j, Cypher, or any graph database as the book.
- Orchestrator, agents, tools, workflows.
- P&L extraction inside the graph; scope/metric/value nodes; moving `FinancialClaim` into the graph.
- Rebuilding or merging the graph on each question.
- LLM or VLM alias resolution; writing `identity_v1` / `identity_v2`.
- Relaxing gold numbers; replacing `Ledger.seed()`; changing `recipe_no_extract`.
- Porting `press_v1` or `presentation_v1`.
- Editing `DocumentClass.period` for comunicado or deck.
- Committing uncommitted Fase 1 files. Starting Fase 3.

### Risks

- **Process-global import ban.** `test_kernel_modules_importable` fails if any earlier test in the same pytest process imported `docling_graph`. Lazy import plus a before/after snapshot on the seven kernel modules is the small spec delta. Leaving the assertion as written makes `pytest tests/` red the first time a graph test builds a real graph.
- **Ingest seal.** Putting graph code under `ingest/` fails the source-token test and the gold-regression MUST NOT. Do not “fix” that by weakening the ingest forbid.
- **Classify period is None on purpose.** Writing `2026-03-31` onto comunicado `DocumentClass.period` turns a Fase 1 freeze into identity. Period belongs on the graph edge.
- **Claim-shaped graph.** Adding scope/metric because §8 lists them pulls `FinancialClaim` into the graph and starts P&L extraction. §15 / §24 win for this change.
- **Library default is extraction.** `run_pipeline` and LLM model config are the documented happy path of docling-graph. Using them violates zero-LLM. The allowed slice is schema, id, merge, and provenance bookkeeping fed by kernel IDs.
- **Two conflict mechanisms.** Document-attribute conflict in the graph and `ledger_status="conflicted"` on a claim must stay distinct. Folding them hides one of the two facts.
- **Memoria / transcript fold.** Year-end memoria filenames do not resolve through `normalize_period` to the quarterly IDs. Forcing them onto 1T26/2T26 invents a period. Transcript may share the period node and must not mint a claim.
- **Uncommitted Fase 1.** `src/claimledger/ingest/`, `tests/ingest/`, artifacts, and a leftover `openspec/changes/fase-1-docling-adapter/` sit beside the archive. Do not commit them. Do not revive the leftover folder. The closed copy is `openspec/changes/archive/2026-10-04-fase-1-docling-adapter/`.
- **400-line review budget.** Schema, merge tests, gold-regression delta, and the `sys.modules` narrow may exceed one review. `sdd-tasks` should forecast slices (package + forbid tests, then period merge, then conflict/HITL). Not a design fork.

### Ready for Proposal

Yes. Placement, entity set, ID source, and the ingest/kernel boundary are resolved. Orchestrator should run `sdd-propose` for `fase-2-graph-ingest` and should not write product code, specs, design, or tasks in this phase. Do not start Fase 3. Do not commit.
