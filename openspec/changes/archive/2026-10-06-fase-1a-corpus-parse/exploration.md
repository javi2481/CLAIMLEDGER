## Exploration: fase-1a-corpus-parse

Architecture is CLOSED. This change finishes phase 1. Archived `fase-1-docling-adapter` already required every PDF in `docs/archivos_muestra` to be local corpus and the parse to persist as hashed Docling JSON. Seven of those files were never converted, and the three that were converted have no DocLang sibling. Phase 1A parses the rest and makes the DocLang sidecar a required product of every parse.

It is not phase 8. Phase 8 stays the page crop (`fase-8-crop`). Phase 9 (several documents, subtraction in code) is why the rest of the corpus has to exist on disk. This change does not open phase 9, answer a question, or extract a new claim.

`fase-8-crop` also plans to edit `ingest/store.py`. This change only keeps the DocLang file beside the hashed JSON. It does not write page PNGs.

### Current State

`docs/archivos_muestra/` holds 10 local BYMA PDFs. The folder README still describes a MinerU demo. That is not the product parser. Inspected 2026-10-05 by hashing each PDF and reading `artifacts/docling/manifest.json`.

| PDF | Docling JSON | DocLang `.dclg` |
|-----|--------------|-----------------|
| `BYMA_-_EEFF_31-03-2026_VF.pdf` | yes, 81 pages, hash `7b7b624ade1011f9fd75931968312ef5c0fa19fe6061bb2cc5eb1491ffaa364f` | missing |
| `BYMA - EEFF 30-06-2026.pdf` | yes, 85 pages, hash `38406b4b606b9eef004d2319b875584a229452c8981a730d0d9c2321eb6dfc2b` | missing |
| `BYMA_2T26_Transcripcion_Resultados_ES.pdf` | yes, 7 pages, hash `b609e48e506b73ee7933329cbdf9cec1eda2fa365afcb71ea7dc525d536fb76c` | missing |
| `BYMA_Comunicado_de_Prensa-Resultados-1T26.pdf` | no | no |
| `BYMA-Comunicado_de_Prensa-2T26.pdf` | no | no |
| `Presentación_de_resultados_BYMA-1T26.pdf` | no | no |
| `Presentacion_de_resultados_BYMA-2T26.pdf` | no | no |
| `Memoria-BYMA-y-EEFF-al-31-12-2023.pdf` | no | no |
| `BYMA-MEMORIA_2024_y_EEFF_31-12-2024.pdf` | no | no |
| `BYMA-MEMORIA_2025.pdf` | no | no |

Seven PDFs have never been converted. The three that have JSON were converted before the sidecar existed, so `load_or_convert` was not run again.

`load_or_convert` in `src/claimledger/ingest/store.py` already writes the sidecar. On a fresh convert it calls `doclang_from_payload` after `canonical_json_bytes` and stores `artifacts/docling/<artifact_hash>.dclg`. On a cache hit, if that file is missing, it builds the sidecar from the stored JSON and does not call `convert_pdf`. `parse.doclang_from_payload` validates the payload as `DoclingDocument` and calls `export_to_doclang()`. The artifact hash is the JSON bytes only. `.gitignore` already ignores `artifacts/docling/*.json` and `artifacts/docling/*.dclg`.

`tests/ingest/test_store.py` covers both paths with a synthetic `DoclingDocument` and a stubbed `convert_pdf`: `test_saved_json_is_also_stored_as_doclang` and `test_cached_json_gains_doclang_without_reconvert`. Those tests do not open the corpus.

`openspec/specs/docling-ingest/spec.md` still stops at hashed JSON. It does not require the `.dclg` file, and the ten files are not all persisted. Recipe extract stays the two quarterly EEFF. Classify still names the other eight and emits no P&L identity from them. `Ledger.seed()` stays the book the question reads. Kernel tests stay off Docling, off the network, and off PDFs.

Rector §5: DocLang is interchange (`DoclingDocument` ↔ DocLang), not a hop on each question. Retrieval keeps reading the JSON.

### Affected Areas

- `src/claimledger/ingest/store.py` and `src/claimledger/ingest/parse.py` — read. The sidecar write is already there. Apply must not add a second writer.
- `tests/ingest/test_store.py` — read. Synthetic sidecar tests stay. A corpus presence check, if added, must not convert inside the default kernel suite.
- `docs/archivos_muestra/*.pdf` — the seven missing inputs, local paths only.
- `artifacts/docling/` — three JSON files gain a `.dclg` without reconvert; seven PDFs gain JSON plus `.dclg` by one local convert each.
- `openspec/specs/docling-ingest/spec.md` — delta only. JSON remains the hash. DocLang is the sibling file.
- Out of scope: `fase-8-crop` page PNGs, recipe rows from comunicado / deck / memoria / transcript, gold numbers, graph rebuild, LlamaIndex reindex, HTTP, Open WebUI, MinerU, VLM. The on-demand native-stack audit is a separate change.

### Approaches

1. **Run the existing `load_or_convert` once per corpus PDF** — The three cached JSON files take the backfill branch (`export_to_doclang`, no `convert_pdf`). The seven missing files take `convert_pdf` (local path, OCR off, pin `docling==2.130.0`) and then the same sidecar write. Spec delta records both. Default `pytest` keeps using the synthetic tests. The corpus pass is an explicit apply step because the memorias are large.
   - Pros: No new parser. Hash stays the JSON. A second call does not reconvert. DocLang is produced by the same function that already persists the artifact. Non-EEFF files stay classified and unextracted.
   - Cons: First convert of three memorias is slow and local. Artifacts stay gitignored, so a fresh clone does not receive them. `fase-8-crop` also plans to edit `store.py`; the sidecar write must stay when that change lands.
   - Effort: Medium (mostly wall time on the memorias)

2. **A new batch parser, or MinerU, or Markdown sidecars** — Another command walks the folder and writes a second format as the source of truth.
   - Pros: A script name would look like a phase.
   - Cons: The store already does the walk's one step. MinerU and Markdown-as-SoT are forbidden. A second writer can diverge from `canonical_json_bytes`.
   - Effort: Medium — **reject**

3. **Convert the ten PDFs inside default `pytest`** — A kernel or ingest test calls `convert_pdf` whenever an artifact is missing.
   - Pros: The suite would fail until the corpus exists, then pass.
   - Cons: Kernel tests must not open a PDF or import Docling. A missing memoria would turn every `pytest` into a multi-hour convert. The synthetic tests already lock the sidecar contract.
   - Effort: Low to write, high to run — **reject**

4. **Extract claims from the eight non-EEFF parses in this phase** — Turn press, decks, the transcript, and year-end memorias into ledger rows so a complex question can run immediately.
   - Pros: The parses would feed the book at once.
   - Cons: That is phase 9 pack work and later orchestration. Lookup still abstains when a P&L figure is attributed to those sources. Gold stays the 14 quarterly recipe rows.
   - Effort: High — **reject**

### Recommendation

Take approach **1**.

1. Keep `load_or_convert` as the only writer. Fresh convert and cache-hit backfill both leave `<artifact_hash>.dclg` beside the JSON. The hash does not include the DocLang bytes.
2. Delta `docling-ingest`: every persisted artifact MUST have that sibling, and the corpus pass MUST cover all 10 local PDFs. Default pytest MUST stay on synthetic documents.
3. Apply calls `load_or_convert` once per file in `docs/archivos_muestra`. Do not reconvert the three existing JSON files. Do not extract recipe claims from the other eight.
4. Do not edit the rector. Do not implement `fase-8-crop` here. Do not number this change as phase 8.

### Risks

- A memoria convert can run for a long time and can fail if local Docling models are missing. `convert_pdf` already downloads models into `artifacts/docling/models/` when they are absent. OCR stays off.
- `export_to_doclang()` on an 80-page EEFF must match the stored JSON, not a second conversion.
- Crop's later edit of `store.py` can drop the `_ensure_doclang` call. The delta spec is the guard.

### Out of Scope Confirmation

- Page-crop PNGs, Open WebUI pictures, query JSON changes.
- New identities, gold edits, `Ledger.seed()` replacement.
- Graph merge, LlamaIndex index rebuild, Neo4j, VLM, agents.
- MinerU, Markdown as SoT, URL fetch.
- Committing the JSON or `.dclg` blobs.
