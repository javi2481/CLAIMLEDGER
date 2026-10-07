# Native stack audit — 2026-10-06

`audit(src/claimledger/) -> runs/2026-10-06/audit.md`

Read-only. No production edit. No new script. The run from 2026-10-05 stays in place. Phases 9–13 stay unopened.

This call re-reads the tree after `extract-native-tables` was applied and archived. The five rows that run marked `delete` or `call-native` are now library calls.

## Pins cited from the installed environment

| Piece | Pinned | Installed | Symbols opened |
|---|---|---|---|
| Docling | `docling==2.130.0` | 2.130.0 | `export_to_dict`, `export_to_doclang`, `DocumentConverter` |
| Docling core (pulled by that pin) | not a separate pin | `docling-core==2.99.0` | `DoclingDocument.iterate_items`, `DEFAULT_CONTENT_LAYERS` = `{ContentLayer.BODY}`, `TableData.grid` |
| docling-graph | `docling-graph==1.9.1` | 1.9.1 | `GraphConverter.pydantic_list_to_graph`, `GraphMerger`, `JSONExporter`, `DocumentOrigin` |
| LlamaIndex | readers and node parser `0.5.0` | 0.5.0 | `DoclingReader`, `DoclingNodeParser` |
| Starlette | `starlette==1.0.0` | 1.0.0 | `Starlette`, `Route` |
| Open WebUI | image `v0.11.4-slim` | compose pin, not imported | draws the completion |

`BoundingBox.normalized` still scales and keeps `coord_origin`. It does not clamp. `docling_graph.core.provenance.identity.identity_key` still locates a graph node. It is not the financial identity.

## What changed since 2026-10-05

| 2026-10-05 row | Now |
|---|---|
| `_grid_from_cells` `delete` | Gone. No `start_row_offset_idx` loop in `extract.py` |
| `_table_grid` `call-native` | Reads `data.grid`. If that list is missing, calls `TableData.grid` |
| `_index_items`, `_ordered_items` `call-native` | Gone |
| `_body_tables` `call-native` | `DoclingDocument.model_validate` then `iterate_items()`. Default layers are body, so furniture stays out |

No new `call-native` or `delete` row.

## Already a direct call

| Function | Call |
|---|---|
| `parse.doclang_from_payload` | `export_to_doclang` |
| `parse.convert_pdf` | `DocumentConverter`, OCR off. Imports torch before Docling |
| `parse._ensure_local_models` | `download_models` |
| `extract._table_grid` | Stored `data.grid` |
| `extract._grid_from_table_data` | `TableData.model_validate(data).grid`, then `model_dump` so the recipe readers still see dicts |
| `extract._body_tables` | `iterate_items`, then the stored table dict with the same `self_ref` |
| `graph.build._convert_and_merge` | `GraphConverter(alias_llm_fn=None)`, `GraphMerger` |
| `graph.build._export` | `JSONExporter.export` |
| `retrieval.read._nodes_from_hashed_json` | `DoclingReader(export_type="json")`, `DoclingNodeParser` |
| `http.app.build_app` | `Starlette` `POST /claims/query` |
| `openwebui.app.build_host` | `Starlette` routes for the slim image |

`_body_tables` still copies the chosen table dict out of the hashed JSON. That join is what the evidence readers use. It is not a second document walk.

## Verdict

`keep` names the gap. This run has no `call-native` and no `delete`.

### Keep — the product gap

Identity, verification, abstention, the seal, and the gold book stay. No pinned API does that job. `alias_llm_fn` stays `None`. Comparing two quarters still returns both verified claims. Subtracting them is phase 9. It is not a library call.

| Function | File | Verdict | Native API or gap | Pin cited |
|---|---|---|---|---|
| `identity_key` | `identity.py` | `keep` | Five-field financial identity | docling-graph 1.9.1 provenance `identity_key` inspected and rejected |
| `fold` | `identity.py` | `keep` | Accent-folded alias and label match | — |
| `normalize_period` | `identity.py` | `keep` | `1T26` / `2T26` to quarterly ids | — |
| `apply_alias` | `identity.py` | `keep` | Claimprint alias table | — |
| `digits_ars` | `digits.py` | `keep` | ARS thousand-dot digits. Gold `21262335` vs `21259769` | — |
| `signed_ars` | `digits.py` | `keep` | Parentheses as a negative amount. Gold `-14950948` | — |
| `validate_claim` | `claim.py` | `keep` | Claim shape | — |
| `FinancialClaim` | `claim.py` | `keep` | The recorded claim | — |
| `validate_evidence` | `evidence.py` | `keep` | Evidence on a recorded claim | — |
| `_validate_bbox` | `evidence.py` | `keep` | Clamped fraction tuple | — |
| `Ledger` | `ledger.py` | `keep` | In-memory book and `Ledger.seed()` | — |
| `understand` | `lookup.py` | `keep` | Question to `Intent` | — |
| `_asks_net_income` | `lookup.py` | `keep` | Net-income phrases | — |
| `_has_pnl_source_metric` | `lookup.py` | `keep` | P&L source tokens | — |
| `_compare_and_period` | `lookup.py` | `keep` | Compare versus one period | — |
| `_identity` | `lookup.py` | `keep` | Intent fields | — |
| `_narrative` | `lookup.py` | `keep` | Narrative route abstains from a number | — |
| `_abstain` | `lookup.py` | `keep` | Unresolved question | — |
| `query` | `query.py` | `keep` | Verified or abstained. Does not subtract | — |
| `_recorded` | `query.py` | `keep` | Only `ledger_status="recorded"` | — |
| `_key_for` | `query.py` | `keep` | Intent plus period to one identity | — |
| `_matching_recorded` | `query.py` | `keep` | Both book periods | — |
| `_verified` | `query.py` | `keep` | Verified result | — |
| `_abstain` | `query.py` | `keep` | Abstained result | — |
| `render_card` | `card/card.py` | `keep` | Seal beside both rows | — |
| `_chip` | `card/card.py` | `keep` | Spanish chip | — |
| `_sentence` | `card/card.py` | `keep` | Sentence when both rows are present | — |
| `_label` | `card/card.py` | `keep` | Closed chip vocabulary | — |
| `card_text` | `openwebui/text.py` | `keep` | Copy the card. Open WebUI does not know the seal | Open WebUI `v0.11.4-slim` |
| `_ficha_rows` | `openwebui/text.py` | `keep` | Two short rows on the card | — |
| `reply` | `openwebui/reply.py` | `keep` | Measure, card, then an optional crop | — |
| `_user_question` | `openwebui/app.py` | `keep` | User turn for `claimledger-card` | — |
| `_completion` | `openwebui/app.py` | `keep` | Completion the slim image displays | Open WebUI `v0.11.4-slim` |
| `measure` | `eval/measure.py` | `keep` | Tables drawer for display. `query(Ledger.seed())` for the number | — |
| `claims_query` | `http/claims.py` | `keep` | Question body to the kernel | Starlette 1.0.0 is only the route |
| `_claim_fields` | `http/claims.py` | `keep` | JSON fields of one claim | — |
| `_evidence` | `http/claims.py` | `keep` | Evidence document, page, and text | — |
| `_json` | `http/claims.py` | `keep` | Verified or abstained JSON | — |

### Keep — ingest, graph, retrieval, crop

| Function | File | Verdict | Native API or gap | Pin cited |
|---|---|---|---|---|
| `_load_pinned_docling` | `ingest/extract.py` | `keep` | On Windows, torch must load before Docling or `c10.dll` fails. The six pins do not set that order | `docling==2.130.0` |
| `extract_recipe` | `ingest/extract.py` | `keep` | Which body table is the consolidated income statement, which column is the quarter, which row is a recipe slot | `alias_llm_fn=None` |
| `_is_consolidated_income_table` | `ingest/extract.py` | `keep` | Gross profit plus controlling interest | — |
| `_is_parent_label` | `ingest/extract.py` | `keep` | Controlling versus non-controlling | — |
| `_claims_from_table` | `ingest/extract.py` | `keep` | Recipe rows become claims | — |
| `_recipe_slot` | `ingest/extract.py` | `keep` | Label to scope and metric | — |
| `_value_column` | `ingest/extract.py` | `keep` | Header date of the quarter | — |
| `_row_starts_body` | `ingest/extract.py` | `keep` | Header versus the first P&L line | — |
| `_period_in_header` | `ingest/extract.py` | `keep` | Period date in the header | — |
| `_column_has_amount` | `ingest/extract.py` | `keep` | Skip a date column with no amount | — |
| `_amount` | `ingest/extract.py` | `keep` | Cell text to `signed_ars` | — |
| `_row_label` | `ingest/extract.py` | `keep` | First filled cell of the row | — |
| `_cell_text` | `ingest/extract.py` | `keep` | Cell `text` | — |
| `_page_no` | `ingest/extract.py` | `keep` | Page for evidence | — |
| `_page_size` | `ingest/extract.py` | `keep` | Page size for the fraction | — |
| `_provenance_bbox` | `ingest/extract.py` | `keep` | Table bbox when the cell has none | — |
| `_cell_bbox` | `ingest/extract.py` | `keep` | Cell bbox for the crop | — |
| `_normalize_bbox` | `ingest/extract.py` | `keep` | Clamped unit square. `BoundingBox.normalized` does not do this | `docling-core==2.99.0` inspected and not a substitute |
| `classify` | `ingest/classify.py` | `keep` | BYMA pack class from the filename | Docling `origin.filename` does not classify a pack |
| `_kind` | `ingest/classify.py` | `keep` | Memoria before EEFF | — |
| `_eeff_period` | `ingest/classify.py` | `keep` | Quarterly date on an EEFF name | — |
| `_fold` | `ingest/classify.py` | `keep` | Fold of the filename | — |
| `load_or_convert` | `ingest/store.py` | `keep` | PDF sha256 to one artifact. Second call does not convert | — |
| `load` | `ingest/store.py` | `keep` | Read one hashed JSON | — |
| `canonical_json_bytes` | `ingest/store.py` | `keep` | Hash is canonical JSON only | — |
| `_sha256_hex` | `ingest/store.py` | `keep` | That digest | — |
| `strip_page_pixels` | `ingest/store.py` | `keep` | Pixels stay out of the hash | — |
| `_without_data_image_uris` | `ingest/store.py` | `keep` | Nested strip | — |
| `_ensure_doclang` | `ingest/store.py` | `keep` | Write the `.dclg` once. The export is already `export_to_doclang` | `docling==2.130.0` |
| `_doclang_path` | `ingest/store.py` | `keep` | Sidecar path | — |
| `_write_page_sidecars` | `ingest/store.py` | `keep` | PNG per page, outside the hash | — |
| `page_sidecar` | `ingest/store.py` | `keep` | `<hash>.p<page>.png` | — |
| `_read_manifest` | `ingest/store.py` | `keep` | PDF sha256 to artifact hash | — |
| `_write_manifest` | `ingest/store.py` | `keep` | That map on disk | — |
| `artifacts_dir` | `ingest/store.py` | `keep` | `artifacts/docling` | — |
| `model_artifacts_path` | `ingest/parse.py` | `keep` | Local model directory | — |
| `_require_pinned_docling` | `ingest/parse.py` | `keep` | Refuse any docling other than 2.130.0 | — |
| `_export_complete` | `ingest/parse.py` | `keep` | Accept only status `success`, then strip pixels | — |
| `_remember_page_pngs` | `ingest/parse.py` | `keep` | Hold rasters until the hash exists | — |
| `_png_bytes` | `ingest/parse.py` | `keep` | PNG bytes of the page Docling rendered | — |
| `fold_documents` | `graph/link.py` | `keep` | Filename and class into the template the graph pin asks for | docling-graph 1.9.1 |
| `_period_id` | `graph/link.py` | `keep` | EEFF period, otherwise a filename token | — |
| `_issuer` | `graph/link.py` | `keep` | One issuer node per name | — |
| `_period` | `graph/link.py` | `keep` | One period node per id | — |
| `_statement` | `graph/link.py` | `keep` | Income statement for EEFF, comunicado, and deck | — |
| `Issuer` | `graph/schema.py` | `keep` | Template the graph pin requires | docling-graph 1.9.1 |
| `Period` | `graph/schema.py` | `keep` | Quarterly period on that template | — |
| `Statement` | `graph/schema.py` | `keep` | `income_statement` | — |
| `Document` | `graph/schema.py` | `keep` | Artifact, kind, and the three edges | — |
| `build` | `graph/build.py` | `keep` | Fold, then the native convert and export | — |
| `_unresolved_period_doubt` | `graph/build.py` | `keep` | Doubt when no token is a quarterly period | — |
| `_stamp_provenance` | `graph/build.py` | `keep` | File-level `DocumentOrigin`. `bind_provenance` needs source chunks this path does not have | docling-graph 1.9.1 |
| `_require_pinned_docling_graph` | `graph/build.py` | `keep` | Refuse any docling-graph other than 1.9.1 | — |
| `graph_json_path` | `graph/build.py` | `keep` | `artifacts/graph/graph.json` | — |
| `load` | `graph/build.py` | `keep` | Read that file | — |
| `retrieve` | `retrieval/drawers.py` | `keep` | One named drawer. The question does not drop a row | LlamaIndex 0.5.0 has no tables/narrative drawer |
| `_one_drawer` | `retrieval/drawers.py` | `keep` | Exactly `tables` or `narrative` | — |
| `_is_table` | `retrieval/drawers.py` | `keep` | `label == "table"` | — |
| `_drawer_of` | `retrieval/drawers.py` | `keep` | Table node or narrative | — |
| `_candidate` | `retrieval/drawers.py` | `keep` | Text plus ref | — |
| `_ref_of` | `retrieval/drawers.py` | `keep` | `self_ref` | — |
| `_doc_items` | `retrieval/drawers.py` | `keep` | `metadata["doc_items"]` | — |
| `_item_field` | `retrieval/drawers.py` | `keep` | Dict or attribute | — |
| `attach` | `crop/attach.py` | `keep` | Picture only when identity and value match | — |
| `_picture` | `crop/attach.py` | `keep` | That match, then the sidecar | — |
| `_crop_sidecar` | `crop/attach.py` | `keep` | Decode the stored page PNG | — |
| `crop_bbox` | `crop/cut.py` | `keep` | Bottom-origin fraction to a top-origin crop, no padding | `TableItem.get_image` would raster again |
| `_clamp` | `crop/cut.py` | `keep` | Pixel bounds | — |
| `_encode_png_rgb` | `crop/cut.py` | `keep` | PNG of that crop | — |
| `_chunk` | `crop/cut.py` | `keep` | PNG chunk | — |

## Counts

| Verdict | Rows |
|---|---|
| `delete` | 0 |
| `call-native` | 0 |
| `keep` | the table above |

## Not in this call

- No function was replaced.
- Gold was not edited.
- Phase 9 was not opened.
