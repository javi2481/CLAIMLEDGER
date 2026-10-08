# Native stack audit — 2026-10-08

`audit(src/claimledger/) -> runs/2026-10-08/audit.md`

Read-only. No production edit. No new script. The runs from 2026-10-05, 2026-10-06, and 2026-10-07 stay in place. This call does not open a phase.

The call carries a second product reading. That reading is accepted where the tree still matches it. Rows below correct the parts the archived changes already moved.

## Pins cited

Same pins as 2026-10-07: Docling `2.130.0`, docling-graph `1.9.1`, LlamaIndex docling readers and node parser `0.5.0`, Starlette `1.0.0`, Open WebUI `v0.11.4-slim`.

`uv.lock` records Starlette `1.0.0` with dependencies `anyio` and `typing-extensions` only. It does not depend on `httpx`. `httpx==0.28.1` is pinned on the `ingest` extra and again on the `deepseek` extra. The `http` extra is `starlette==1.0.0` alone. The `dev` extra is `pytest==9.1.1` alone.

## What the tree already closed

| Change | Archived | Effect on this reading |
|---|---|---|
| `max-docling-parse` | 2026-10-07 | Docling Serve compiles. Seal turns picture description, chart extraction, formula, and code enrichment **off**. `DOCLING_SERVE_ENABLE_REMOTE_SERVICES=false`. Claimledger does not `depends_on` serve. |
| `runtime-json-book` | 2026-10-07 | `extract_recipe` walks `body` `$ref` and reads `data.grid` only. No in-process Docling pin on that path. |
| `reply-without-retrieval` | 2026-10-07 | `measure`, `reply`, and the card do not import `claimledger.retrieval` or `DoclingReader`. Dockerfile installs `.[http,deepseek]`, not `.[retrieval]`. |

`measure` is now `understand` then `query(intent, ledger)`. On `verified` it builds display rows from the claim evidence. It does not call `retrieve`.

## Product sentence this call keeps

CLAIMLEDGER today is a deterministic extractor and identity resolver with abstention over a closed financial corpus. It is not a general financial-claim verifier.

```text
question → Intent → identity_key → Ledger recorded|conflicted → query → verified|abstained
```

`query` does not receive retrieval candidates. `verified` means: a recorded claim satisfies the requested identity and is not `conflicted`. The ledger is not mutated by the verdict.

The stronger product, candidate adjudication, is not this tree. It stays future work. No pinned API does financial identity, conflict, or abstention. Those rows stay `keep`.

Two levels stay distinct. The kernel (`FinancialClaim`, `Ledger`, `query`, identity, abstention) is general. The pilot (`lookup.py`, `extract_recipe` labels, `BYMA`, `1T26`/`2T26`, `income_statement`) is a closed Spanish recipe. They are not the same layer.

Graph stays off the critical path: Document, Issuer, Period, Statement, and the three edges. No `FinancialClaim` node. `book/ask.py` reads period literals from the Cypher export with `n.period = "..."`. That is a demo control plane. The book is the financial truth. `query` is the judge.

Open WebUI still does not decide claim, value, identity, or difference. One `CLAIMLEDGER_ARTIFACT_HASH` can crop the wrong quarter while the book verifies the right one. That is evidence presentation.

Phase 10 in the rector stays a VLM second reader for financial verification, and it stays deferred. Docling VLM enrichment (picture description, chart extraction, formula, code) is a different sentence. The sealed compiler profile has that enrichment off. Turning it on is a new compiler profile, not the close-out of `max-docling-parse`.

`manifest.json` maps PDF sha256 to one artifact hash. It does not record compiler profile, compiler version, or an options fingerprint. A second profile on the same PDF needs that reservation before it shares a gold artifact. Not implemented in this call.

## Corrections to the supplied reading

1. `measure` no longer calls `retrieve`. The numerical decision was already `query` without candidates. The product path now also drops the drawer from the reply. LlamaIndex remains an optional extra for `retrieval/` tests. It is not on the reply path.
2. The Dockerfile does not install `.[http,retrieval]`. It installs `.[http,deepseek]`. `.dockerignore` still excludes `docs/` and `artifacts/`. `recorded_book` still requires the two quarterly PDFs to exist under `docs/archivos_muestra` before it consults the manifest (`load_or_convert` rejects a missing file). Compose mounts `./artifacts/docling` and does not mount `docs`. The container still cannot build the book. The retrieval-extra diagnosis does not.
3. The README no longer says LlamaIndex candidates decide the number. It does say the active change is `ground-ledger`. That change is archived. `AGENTS.md` has no active change. `docs/documento-rector.md` §14 still writes the E2E as `question → retrieval → candidates → verified claim`, and §15 still draws `LlamaIndex retrieve` on the MVP path. That documentary overclaim is open. The code path is not that chain.
4. `max-docling-parse` is archived with chart extraction off. "Close Docling Serve" is done. Enabling `chart2csv` is a later profile, and its output would be candidate data, not a `FinancialClaim`.
5. Runtime JSON for recipe, book, and `query` is archived. The residual seam is the PDF gate in `recorded_book` / `load_or_convert`, plus the image that does not contain the corpus.

## Defect named, not replaced

`extract_recipe` keeps the first claim per `(scope, metric)`:

```text
found: dict[tuple[str, str], FinancialClaim] = {}
found.setdefault(key, claim)
```

`Ledger.upsert` would mark the same identity with a different value as `conflicted`. A second valid claim in the same document never reaches `upsert`. The extractor can hide an intra-document conflict. This is a `keep` gap, not a `call-native` row. No pinned API emits the recipe. The fix, when asked, is to emit every valid claim and let `upsert` decide. Not in this call.

`retrieve(artifact_hash, drawer, question)` still ignores `question` and returns the whole drawer. The docstring says so. That remains `keep`: LlamaIndex `DoclingNodeParser` emits elements and has no tables/narrative drawer and no financial ranker. The product reply does not call it.

## CI

`.github/workflows/pytest.yml` product job installs `dev` + `http` and runs `tests/http`. Those tests import `starlette.testclient.TestClient`, and the fallback imports `httpx`. Neither extra on that job pins `httpx`. The heavy job does, via `ingest` and `deepseek`. Adding `httpx==0.28.1` to `dev`, or to `http`, is still the right close. Not applied here. A pending status on an old commit is not a green CI signal.

## Verdict

No `call-native`. No `delete`. Unchanged `keep` rows from `runs/2026-10-07/audit.md` stay, except the rows whose gap text is now wrong.

| Function | File | Verdict | Native API or gap | Pin cited |
|---|---|---|---|---|
| `extract_recipe` | `ingest/extract.py` | `keep` | Recipe labels and column. Local `setdefault` drops a second value before `Ledger.upsert` can conflict | No pin extracts this P&L recipe |
| `_body_tables` | `ingest/extract.py` | `keep` | Local `$ref` walk of `body`. Furniture skipped. Not `iterate_items` | Docling Serve writes the JSON |
| `_table_grid` | `ingest/extract.py` | `keep` | Stored `data.grid` or `IngestError`. No `TableData` | — |
| `measure` | `eval/measure.py` | `keep` | `understand` then `query`. Rows from verified evidence only. Does not call `retrieve` | — |
| `retrieve` | `retrieval/drawers.py` | `keep` | Named drawer. `question` does not drop a row. Off the product reply | LlamaIndex 0.5.0 |
| `query` | `query.py` | `keep` | Recorded-identity lookup. Does not adjudicate candidates. Does not mutate the book | — |
| `periods_in_script` | `book/ask.py` | `keep` | Periods from Cypher text. Not the product control plane | `CypherExporter` does not list periods |
| `recorded_book` | `ingest/ground.py` | `keep` | Two PDFs must exist, then hashed JSON, then `upsert`. Image has no `docs/` | — |

`_load_pinned_docling` and `_grid_from_table_data` are gone from `extract.py`. They are not rows of this run.

## Counts for rows restated here

| Verdict | Rows |
|---|---|
| `delete` | 0 |
| `call-native` | 0 |
| `keep` (restated) | 8 |

## Work this call does not start

Order that matches the tree, not a new stack:

1. Honesty in the rector and the README: verified lookup and abstention; drawer exposure is not the reply path.
2. Emit every valid recipe claim so `upsert` can conflict. Separate change. Strict TDD. Gold numbers unchanged.
3. Docker book: the runtime must be able to read the compiled artifacts without a `docs/` corpus inside the image, or the image must contain that corpus. One of those, not both stories.
4. Pin `httpx` on the extra the product pytest job actually installs.
5. Leave retrieval ranking, candidate adjudication, chart-extraction profile, compiler-profile manifest, and phase 10 until those four are asked.

## Not in this call

- No function was replaced.
- Gold was not edited.
- Kernel tests were not changed and still must not import `docling`.
