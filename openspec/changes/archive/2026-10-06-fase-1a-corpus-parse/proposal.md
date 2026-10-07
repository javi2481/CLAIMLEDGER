# Proposal: Phase 1A Corpus Parse

## Intent

Phase 1 is not finished on disk. The seven sample PDFs that have no Docling artifact must be parsed locally, and every parse must leave a DocLang file beside the hashed JSON. This is that close-out. It is not the page crop, and it does not start phase 9. Phase 9 needs these artifacts later.

## Scope

### In Scope

- One `load_or_convert` per PDF in `docs/archivos_muestra` (10 files).
- Missing JSON: local `convert_pdf`, then `artifacts/docling/<artifact_hash>.json` and `<artifact_hash>.dclg`.
- JSON already present and `.dclg` missing: write DocLang from that JSON. Do not reconvert.
- Spec delta on `docling-ingest`. The hash stays `canonical_json_bytes`. DocLang stays out of the hash.
- Pin stays `docling==2.130.0`. OCR stays off. No URL.

### Out of Scope

- Phase 8 (`fase-8-crop`) page rasters, card pictures, and host changes.
- Recipe extraction from comunicado, deck, memoria, or transcript.
- Gold, `Ledger.seed()`, lookup routes, graph rebuild, retrieval reindex.
- The on-demand native-stack audit.
- MinerU, Markdown as source of truth, VLM, HTTP, Open WebUI.
- Committing gitignored artifacts. Rector text stays as it is.

## Capabilities

### New Capabilities

- None. This is the existing ingest store applied to the whole corpus.

### Modified Capabilities

- `docling-ingest`: Each persisted artifact MUST have a sibling `.dclg` from `export_to_doclang` of that same JSON. The corpus pass MUST cover all 10 local sample PDFs. Default pytest MUST NOT convert those PDFs.

## Approach

Approach 1. `load_or_convert` is already the writer (`store._ensure_doclang`, `parse.doclang_from_payload`). Synthetic tests already cover a fresh convert and a cache backfill. Apply runs that function on the corpus. It does not add a second parser.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `ingest/store.py`, `ingest/parse.py` | Unchanged behavior | Sidecar write already present |
| `tests/ingest/test_store.py` | Unchanged contract | Synthetic `.dclg` tests stay |
| `docs/archivos_muestra/*.pdf` | Read | Seven converts, three backfills |
| `artifacts/docling/` | New files | JSON for seven PDFs; `.dclg` for all ten |
| `openspec/specs/docling-ingest` | Delta | Sidecar plus corpus pass |
| Kernel, gold, `http/`, `openwebui/` | Unchanged | The question still reads `Ledger.seed()` |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Memoria convert time | High | Explicit apply step, not default pytest |
| Reconvert of the two EEFF | Med | Cache hit writes `.dclg` only |
| Crop edit drops the sidecar call | Med | Spec requires `.dclg` on every persist |
| DocLang treated as the question hop | Low | Retrieval and query keep reading JSON and the seed |

## Rollback Plan

Delete the seven new JSON files, their manifest entries, and every `.dclg` this pass wrote. Leave the three existing JSON hashes. Revert the spec delta. Do not touch gold, the kernel, or the crop change.

## Dependencies

- Archived phase 1 ingest (`load_or_convert`, pin `docling==2.130.0`).
- Local PDFs in `docs/archivos_muestra`.
- Models under `artifacts/docling/models/` when a convert needs them.

## Success Criteria

- [ ] All 10 sample PDFs have `artifacts/docling/<artifact_hash>.json` and a sibling `.dclg`.
- [ ] The three existing hashes do not change.
- [ ] A second `load_or_convert` on a parsed PDF does not call `convert_pdf`.
- [ ] `.dclg` bytes are not part of `artifact_hash`.
- [ ] Non-EEFF parses create no recipe claims.
- [ ] Kernel pytest stays free of Docling, PDFs, and the network.
