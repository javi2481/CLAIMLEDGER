# Design: Phase 1A Corpus Parse

## Technical Approach

`specs/docling-ingest` delta in this change. This change closes phase 1's corpus. Phase 8 remains the crop. Architecture Gate: the kernel cannot read a PDF, and DocLang is interchange beside the JSON, not a second parser and not a question hop. `load_or_convert` already implements the write. This phase runs it on the ten local sample PDFs. It does not add a module.

## Architecture Decisions

| Decision | Choice | Rejected | Why |
|---|---|---|---|
| Place in the plan | Phase 1 close-out | A phase 8 sibling | The crop does not need the other eight PDFs. Phase 9 does, later |
| Writer | Existing `load_or_convert` | A new batch script; MinerU; Markdown | One hash, one JSON, one sidecar |
| Sidecar path | `artifacts/docling/<artifact_hash>.dclg` | A `.doclang` name; embedding DocLang in the JSON | `store._doclang_path` and `.gitignore` already use `.dclg` |
| Backfill | `export_to_doclang()` of the stored dict when `.dclg` is missing | Reconvert the two EEFF and the transcript | Those hashes are already the SoT |
| Fresh parse | `convert_pdf`: local path, OCR off, pin `2.130.0` | URL, VLM, a second pipeline | Same function the two EEFF already used |
| When | Explicit corpus pass during apply | Default `pytest` | Memorias are large. Kernel tests stay PDF-free |
| Claims | No `extract_recipe` on the eight non-EEFF files | Filling the ledger from press or year-end memorias | That is phase 9. Gold stays the 14 quarterly rows |
| Crop | Not in this change | Page PNGs in the same edit | `fase-8-crop` owns rasters. This change must leave `_ensure_doclang` in place for that edit |

## Data Flow

For each PDF in `docs/archivos_muestra`:

1. Hash the PDF bytes and read `artifacts/docling/manifest.json`.
2. If the manifest points at an existing `<artifact_hash>.json` and the `.dclg` is missing, write DocLang from that JSON and return. `convert_pdf` does not run.
3. If the JSON is missing, `convert_pdf` returns `export_to_dict()`. The hash is `canonical_json_bytes`. The JSON is written, then `.dclg` from that same payload, then the manifest entry.
4. Retrieval and `query` are not called. The seed ledger is not updated.

The three hashes that must survive unchanged:

- `7b7b624ade1011f9fd75931968312ef5c0fa19fe6061bb2cc5eb1491ffaa364f` (1T26 EEFF)
- `38406b4b606b9eef004d2319b875584a229452c8981a730d0d9c2321eb6dfc2b` (2T26 EEFF)
- `b609e48e506b73ee7933329cbdf9cec1eda2fa365afcb71ea7dc525d536fb76c` (2T26 transcript)

## File Changes

| File | Change |
|------|--------|
| `src/claimledger/ingest/store.py` | None expected. `_ensure_doclang` stays |
| `src/claimledger/ingest/parse.py` | None expected. `doclang_from_payload` stays |
| `tests/ingest/test_store.py` | None expected. Synthetic tests stay the contract |
| `artifacts/docling/` | Apply only. Seven JSON files, ten `.dclg` files, manifest grows to 10 entries |
| `openspec/specs/docling-ingest/spec.md` | Merged on archive, not during apply |

## Verification

- `pytest tests/ingest/test_store.py -k doclang` stays green without a corpus PDF.
- After the corpus pass, manifest length is 10, each target JSON exists, each `.dclg` is non-empty, and the three hashes above are unchanged.
- `pytest` on the kernel paths does not import `docling`.

## Rollback

Remove the seven new JSON files and their manifest keys. Remove `.dclg` files added by this pass. Keep the three original JSON files. No data migration.
