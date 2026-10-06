# Native stack audit — 2026-10-05

`audit(src/claimledger/) -> runs/2026-10-05/audit.md`

Read-only. No production edit. No new script. Phases 9–13 stay unopened. Phase 1A and the page crop were not applied from this call.

## Pins cited from the installed environment

| Piece | Pinned | Installed | Symbols opened |
|---|---|---|---|
| Docling | `docling==2.130.0` | 2.130.0 | `DocumentConverter`, `PdfPipelineOptions`, `export_to_dict`, `export_to_doclang` |
| Docling core (pulled by that pin) | not a separate pin | `docling-core==2.99.0` | `DoclingDocument.iterate_items`, `DEFAULT_CONTENT_LAYERS`, `TableData.grid`, `BoundingBox.normalized` |
| docling-graph | `docling-graph==1.9.1` | 1.9.1 | `GraphConverter.pydantic_list_to_graph`, `GraphMerger`, `JSONExporter`, `DocumentOrigin`, `provenance.binder.bind_provenance` |
| LlamaIndex | readers and node parser `0.5.0` | 0.5.0 | `DoclingReader`, `DoclingNodeParser` (`HierarchicalChunker`) |
| Starlette | `starlette==1.0.0` | 1.0.0 | `Starlette`, `Route` |
| Open WebUI | image `v0.11.4-slim` | compose pin, not imported | draws the completion; it does not calculate |

`DEFAULT_CONTENT_LAYERS` on this install is `{ContentLayer.BODY}`. `TableData.grid` is a computed field: the same span expansion that `_grid_from_cells` copies, and `export_to_dict` already serializes it. `BoundingBox.normalized` scales to a 1×1 page and keeps `coord_origin`. It does not clamp and it does not drop the origin. `docling_graph.core.provenance.identity.identity_key` is a graph-node locator. It is not the financial identity.

## Already a direct call

These functions are the pinned call. They are not verdict rows.

| Function | Call |
|---|---|
| `parse.doclang_from_payload` | `DoclingDocument.model_validate` then `export_to_doclang` |
| `parse.convert_pdf` | `DocumentConverter` with `PdfPipelineOptions(do_ocr=False)` |
| `parse._ensure_local_models` | `docling.utils.model_downloader.download_models` |
| `graph.build._convert_and_merge` | `GraphConverter(alias_llm_fn=None).pydantic_list_to_graph`, `GraphMerger` |
| `graph.build._export` | `JSONExporter.export` |
| `retrieval.read._nodes_from_hashed_json` | `DoclingReader(export_type="json")`, `DoclingNodeParser` |
| `http.app.build_app` | `Starlette` route `POST /claims/query` |
| `openwebui.app.build_host` | `Starlette` routes for `/v1` models and completions |

## Verdict

`keep` names the gap. `call-native` or `delete` names the API that already does that job. A replacement is a later step, one function at a time. This file does not apply it.

### Call the pin

| Function | File | Verdict | Native API or gap | Pin cited |
|---|---|---|---|---|
| `_grid_from_cells` | `ingest/extract.py` | `delete` | `TableData.grid` is already on each table as `data.grid` after `export_to_dict`. The helper repeats that computed field. | `docling==2.130.0` (`docling-core==2.99.0`, `TableData.grid`) |
| `_table_grid` | `ingest/extract.py` | `call-native` | Read `data.grid`. If a payload has cells and no grid, call `TableData.model_validate(data).grid`. Do not keep a second span loop. | same |
| `_index_items` | `ingest/extract.py` | `call-native` | `DoclingDocument.model_validate(payload).iterate_items`. Default layer set is body, so furniture is already excluded. | `docling==2.130.0` (`DoclingDocument.iterate_items`, `DEFAULT_CONTENT_LAYERS`) |
| `_ordered_items` | `ingest/extract.py` | `call-native` | same walk | same |
| `_body_tables` | `ingest/extract.py` | `call-native` | same walk, then keep items that are tables | same |

Order risk on the walk: `extract_recipe` keeps the first claim per `(scope, metric)`. `iterate_items` must be checked against the current body order before the swap. Existing extract tests have to fail first if that order changes. Kernel tests stay free of a `docling` import.

Recommended later steps, still not done here: delete `_grid_from_cells` first; then replace the three walkers together, because they only exist to feed `_body_tables`.

### Keep — the product gap

Identity, verification, abstention, the seal, and the gold book stay. No pinned API does that job. `alias_llm_fn` stays `None`.

| Function | File | Verdict | Native API or gap | Pin cited |
|---|---|---|---|---|
| `identity_key` | `identity.py` | `keep` | Five-field financial identity `issuer\|period\|statement\|scope\|metric`. The graph package's `identity_key` locates a node in a chunk. | docling-graph 1.9.1 provenance identity, inspected and rejected for this job |
| `fold` | `identity.py` | `keep` | Accent-folded match for those aliases and labels | — |
| `normalize_period` | `identity.py` | `keep` | Pack tokens `1T26` / `2T26` to `2026-03-31` / `2026-06-30` | — |
| `apply_alias` | `identity.py` | `keep` | Claimprint alias table in `evals/aliases.json` | — |
| `digits_ars` | `digits.py` | `keep` | ARS thousand-dot digits. Gold `21262335` vs `21259769` | — |
| `signed_ars` | `digits.py` | `keep` | Parentheses as a negative tax amount. Gold `-14950948` | — |
| `validate_claim` | `claim.py` | `keep` | Claim shape before the book accepts it | — |
| `FinancialClaim` | `claim.py` | `keep` | The recorded claim | — |
| `validate_evidence` | `evidence.py` | `keep` | Evidence required on a recorded claim | — |
| `_validate_bbox` | `evidence.py` | `keep` | Clamped fraction tuple on that evidence | — |
| `Ledger` | `ledger.py` | `keep` | In-memory book and `Ledger.seed()`. Gold numbers live here and were not edited | — |
| `understand` | `lookup.py` | `keep` | Lexical question to `Intent`. No press or deck route | — |
| `_asks_net_income` | `lookup.py` | `keep` | Phrase set for net income | — |
| `_has_pnl_source_metric` | `lookup.py` | `keep` | P&L source tokens | — |
| `_compare_and_period` | `lookup.py` | `keep` | Compare versus a single period | — |
| `_identity` | `lookup.py` | `keep` | Intent fields for one identity | — |
| `_narrative` | `lookup.py` | `keep` | Narrative route abstains from a number | — |
| `_abstain` | `lookup.py` | `keep` | Unresolved question | — |
| `query` | `query.py` | `keep` | Read-only verdict: verified or abstained. Does not subtract | — |
| `_recorded` | `query.py` | `keep` | Only `ledger_status="recorded"` | — |
| `_key_for` | `query.py` | `keep` | Intent plus period to one identity key | — |
| `_matching_recorded` | `query.py` | `keep` | Both book periods for compare and ambiguity | — |
| `_verified` | `query.py` | `keep` | Verified result | — |
| `_abstain` | `query.py` | `keep` | Abstained result | — |
| `render_card` | `card/card.py` | `keep` | Seal `VERIFICADO` / `ME ABSTENGO` beside both rows | — |
| `_chip` | `card/card.py` | `keep` | Spanish chip for issuer, period, scope, metric | — |
| `_sentence` | `card/card.py` | `keep` | One sentence when both rows are on the card | — |
| `_label` | `card/card.py` | `keep` | Closed chip vocabulary | — |
| `card_text` | `openwebui/text.py` | `keep` | Copy the card into the assistant string. Open WebUI does not know the seal | Open WebUI `v0.11.4-slim` |
| `_ficha_rows` | `openwebui/text.py` | `keep` | Two short rows on the card; longer text stays off | — |
| `reply` | `openwebui/reply.py` | `keep` | Measure, then the card, then an optional crop in the same completion | — |
| `_user_question` | `openwebui/app.py` | `keep` | Read the user turn for model `claimledger-card` | — |
| `_completion` | `openwebui/app.py` | `keep` | OpenAI-shaped completion the slim image displays | Open WebUI `v0.11.4-slim` |
| `measure` | `eval/measure.py` | `keep` | Tables drawer for display; `query(Ledger.seed())` for the number. The drawer does not drop the row | — |
| `claims_query` | `http/claims.py` | `keep` | Question body to the kernel. No rows, no card | Starlette 1.0.0 is only the route |
| `_claim_fields` | `http/claims.py` | `keep` | JSON fields of one verified claim | — |
| `_evidence` | `http/claims.py` | `keep` | Evidence document, page, and text | — |
| `_json` | `http/claims.py` | `keep` | Verified or abstained JSON | — |

### Keep — ingest, graph, retrieval, crop

| Function | File | Verdict | Native API or gap | Pin cited |
|---|---|---|---|---|
| `classify` | `ingest/classify.py` | `keep` | BYMA pack class from the filename: memoria, comunicado, deck, transcript, EEFF | Docling `origin.filename` does not classify a pack |
| `_kind` | `ingest/classify.py` | `keep` | Token order, memoria before EEFF | — |
| `_eeff_period` | `ingest/classify.py` | `keep` | `31-03-2026` / `30-06-2026` on an EEFF name | — |
| `_fold` | `ingest/classify.py` | `keep` | Same fold, used on the filename | — |
| `extract_recipe` | `ingest/extract.py` | `keep` | Which body table is the consolidated income statement, which column is the quarter, and which row is a recipe slot. EEFF 1T26 and 2T26 only | docling-graph must not mint this identity (`alias_llm_fn=None`) |
| `_is_consolidated_income_table` | `ingest/extract.py` | `keep` | Gross profit plus controlling interest on one grid | — |
| `_is_parent_label` | `ingest/extract.py` | `keep` | Controlling vs non-controlling label | — |
| `_claims_from_table` | `ingest/extract.py` | `keep` | Recipe rows become `FinancialClaim` values | — |
| `_recipe_slot` | `ingest/extract.py` | `keep` | Label to `(scope, metric)`, including tax and NCI | — |
| `_value_column` | `ingest/extract.py` | `keep` | Header date `31/03/2026` or `30/06/2026` | — |
| `_row_starts_body` | `ingest/extract.py` | `keep` | Header versus the first P&L line | — |
| `_period_in_header` | `ingest/extract.py` | `keep` | Period date inside the header cells | — |
| `_column_has_amount` | `ingest/extract.py` | `keep` | Skip a date column that has no amount | — |
| `_amount` | `ingest/extract.py` | `keep` | Cell text to `signed_ars` | — |
| `_row_label` | `ingest/extract.py` | `keep` | Row label from the first filled cell | — |
| `_cell_text` | `ingest/extract.py` | `keep` | Cell `text` field | — |
| `_page_no` | `ingest/extract.py` | `keep` | Page from item provenance for evidence | — |
| `_page_size` | `ingest/extract.py` | `keep` | Page size in points for the fraction | — |
| `_provenance_bbox` | `ingest/extract.py` | `keep` | Table provenance bbox when the cell has none | — |
| `_cell_bbox` | `ingest/extract.py` | `keep` | Cell bbox for the crop | — |
| `_normalize_bbox` | `ingest/extract.py` | `keep` | Clamped unit square for `FinancialEvidence`, origin dropped. `BoundingBox.normalized` scales and keeps `coord_origin`. It does not do this contract | `docling-core==2.99.0` `BoundingBox.normalized`, inspected and not a substitute |
| `load_or_convert` | `ingest/store.py` | `keep` | PDF sha256 to one artifact. Second call does not convert again | — |
| `load` | `ingest/store.py` | `keep` | Read one hashed JSON | — |
| `canonical_json_bytes` | `ingest/store.py` | `keep` | Hash is canonical JSON only | — |
| `_sha256_hex` | `ingest/store.py` | `keep` | That digest | — |
| `strip_page_pixels` | `ingest/store.py` | `keep` | Page images and data-URIs stay out of the hash | — |
| `_without_data_image_uris` | `ingest/store.py` | `keep` | Same strip, nested | — |
| `_ensure_doclang` | `ingest/store.py` | `keep` | Write the `.dclg` sibling once. The export itself is already `export_to_doclang` | `docling==2.130.0` |
| `_doclang_path` | `ingest/store.py` | `keep` | Sidecar path beside the hash | — |
| `_write_page_sidecars` | `ingest/store.py` | `keep` | PNG per page, outside the hash | — |
| `page_sidecar` | `ingest/store.py` | `keep` | `<hash>.p<page>.png` | — |
| `_read_manifest` | `ingest/store.py` | `keep` | PDF sha256 to artifact hash | — |
| `_write_manifest` | `ingest/store.py` | `keep` | Same map on disk | — |
| `artifacts_dir` | `ingest/store.py` | `keep` | `artifacts/docling` | — |
| `model_artifacts_path` | `ingest/parse.py` | `keep` | Local model directory | — |
| `_require_pinned_docling` | `ingest/parse.py` | `keep` | Refuse any docling other than 2.130.0 at runtime | — |
| `_export_complete` | `ingest/parse.py` | `keep` | Accept only conversion status `success`, then strip pixels | — |
| `_remember_page_pngs` | `ingest/parse.py` | `keep` | Hold page rasters until the hash exists, so the sidecar can be named | — |
| `_png_bytes` | `ingest/parse.py` | `keep` | PNG bytes of the page image Docling already rendered | — |
| `fold_documents` | `graph/link.py` | `keep` | Filename and `DocumentClass` into the template the graph pin asks for | docling-graph 1.9.1 does not parse BYMA filenames |
| `_period_id` | `graph/link.py` | `keep` | EEFF period, otherwise a filename token | — |
| `_issuer` | `graph/link.py` | `keep` | One `Issuer` node per name | — |
| `_period` | `graph/link.py` | `keep` | One `Period` node per id | — |
| `_statement` | `graph/link.py` | `keep` | Income statement only for EEFF, comunicado, and deck | — |
| `Issuer` | `graph/schema.py` | `keep` | Pydantic template docling-graph requires (`graph_id_fields`) | docling-graph 1.9.1 |
| `Period` | `graph/schema.py` | `keep` | Quarterly period on that template | — |
| `Statement` | `graph/schema.py` | `keep` | `income_statement` on that template | — |
| `Document` | `graph/schema.py` | `keep` | Artifact, kind, and the three edges | — |
| `build` | `graph/build.py` | `keep` | Fold, convert, stamp, export. The convert and export lines are already native | — |
| `_unresolved_period_doubt` | `graph/build.py` | `keep` | Doubt string when no filename token is a quarterly period | — |
| `_stamp_provenance` | `graph/build.py` | `keep` | File-level `DocumentOrigin` after objects are folded. `bind_provenance` locates chunk anchors in source text this path does not have | docling-graph 1.9.1 `DocumentOrigin`; `bind_provenance` inspected and not a substitute |
| `_require_pinned_docling_graph` | `graph/build.py` | `keep` | Refuse any docling-graph other than 1.9.1 | — |
| `graph_json_path` | `graph/build.py` | `keep` | `artifacts/graph/graph.json` | — |
| `load` | `graph/build.py` | `keep` | Read that file | — |
| `retrieve` | `retrieval/drawers.py` | `keep` | One named drawer. The question does not drop a row | LlamaIndex 0.5.0 `DoclingNodeParser` emits elements; it has no tables/narrative drawer |
| `_one_drawer` | `retrieval/drawers.py` | `keep` | Exactly `tables` or `narrative` | — |
| `_is_table` | `retrieval/drawers.py` | `keep` | Drawer membership from `doc_items[].label == "table"` | — |
| `_drawer_of` | `retrieval/drawers.py` | `keep` | Table node to `tables`, otherwise `narrative` | — |
| `_candidate` | `retrieval/drawers.py` | `keep` | Text plus ref, not a filtered hit | — |
| `_ref_of` | `retrieval/drawers.py` | `keep` | `self_ref` off the node metadata | — |
| `_doc_items` | `retrieval/drawers.py` | `keep` | Read `metadata["doc_items"]` | — |
| `_item_field` | `retrieval/drawers.py` | `keep` | Dict or attribute access on one item | — |
| `attach` | `crop/attach.py` | `keep` | Picture only when identity and value match the verified claim | — |
| `_picture` | `crop/attach.py` | `keep` | That match, then the sidecar crop | — |
| `_crop_sidecar` | `crop/attach.py` | `keep` | Decode the stored page PNG | — |
| `crop_bbox` | `crop/cut.py` | `keep` | Bottom-origin fraction to a top-origin RGB crop, no padding. `TableItem.get_image` would raster again at question time | `docling==2.130.0` `TableItem.get_image`, inspected and not a substitute |
| `_clamp` | `crop/cut.py` | `keep` | Pixel bounds of that crop | — |
| `_encode_png_rgb` | `crop/cut.py` | `keep` | PNG of the cropped RGB. None of the six pins encode this crop | — |
| `_chunk` | `crop/cut.py` | `keep` | PNG chunk for that encoder | — |

## Counts

| Verdict | Rows |
|---|---|
| `delete` | 1 (`_grid_from_cells`) |
| `call-native` | 4 (the grid read and the body walk) |
| `keep` | the rest of the table |

Direct calls listed above are outside the counts.

## Not in this call

- No function was replaced.
- Gold in `Ledger.seed()` was read and left as-is.
- No audit script, linter, or package was added.
- `docling_graph` provenance `identity_key` stays unused by the kernel.
