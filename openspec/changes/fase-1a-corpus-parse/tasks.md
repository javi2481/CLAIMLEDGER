# Tasks: Phase 1A Corpus Parse

## Review Workload Forecast

Estimated changed lines: under 50 in git, plus gitignored artifacts. Delivery strategy: one apply batch. No rector edit. No crop, no claim extraction, no commit unless the user asks.

Decision needed before apply: No. The writer already exists.
Chained PRs recommended: No
Chain strategy: none. Artifacts stay gitignored.
400-line budget risk: Low

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | Confirm sidecar contract | None | `pytest tests/ingest/test_store.py -k doclang` | Synthetic `DoclingDocument` | Revert is a no-op if production code is untouched |
| 2 | Corpus pass | None (gitignored) | Manifest has 10 entries; each hash has `.json` and `.dclg` | Local Docling, OCR off | Delete new JSON, new manifest keys, and new `.dclg` |

## Phase 1: Sidecar contract (already implemented)

- [x] 1.1 `load_or_convert` writes `<artifact_hash>.dclg` after a fresh convert and backfills it from cached JSON without `convert_pdf`. Hash stays `canonical_json_bytes`.
- [x] 1.2 `tests/ingest/test_store.py::test_saved_json_is_also_stored_as_doclang` and `test_cached_json_gains_doclang_without_reconvert` lock that behavior with a stubbed converter.

## Phase 2: Corpus pass (apply)

- [ ] 2.1 Run `load_or_convert` on each PDF in `docs/archivos_muestra`. Do not add a second parser.
- [ ] 2.2 The three existing hashes stay `7b7b624ade1011f9fd75931968312ef5c0fa19fe6061bb2cc5eb1491ffaa364f`, `38406b4b606b9eef004d2319b875584a229452c8981a730d0d9c2321eb6dfc2b`, and `b609e48e506b73ee7933329cbdf9cec1eda2fa365afcb71ea7dc525d536fb76c`. Each gains a `.dclg` only.
- [ ] 2.3 The seven missing PDFs each gain JSON and `.dclg` from one local convert. OCR stays off. Pin stays `docling==2.130.0`.
- [ ] 2.4 Do not call `extract_recipe` on comunicado, deck, memoria, or transcript. Do not edit gold, the kernel, retrieval, or `fase-8-crop`.
- [ ] 2.5 Confirm manifest length 10, ten `.dclg` files, and `pytest tests/ingest/test_store.py -k doclang` still green.
