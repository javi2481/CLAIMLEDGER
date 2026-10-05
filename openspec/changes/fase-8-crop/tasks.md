# Tasks: Phase 8 Page Crop

## Review Workload Forecast

Estimated changed lines: 630–760 (~160 / ~180 / ~220 / ~140). Delivery strategy: ask-on-risk. Apply batch 1 first. No rector edit. Phases 9–13 stay out.

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: sequential batches on the current branch. No commits and no PRs unless the user later asks.
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | Bbox cut | Batch 1 | `pytest tests/crop/test_crop.py -k crop_bbox` | N/A synthetic RGB | Delete `crop/` and `tests/crop/` |
| 2 | Hash sidecar | Batch 2 | `pytest tests/ingest/test_store.py -k "strip or sidecar or page_images"` | N/A synthetic JSON | Revert `store.py`, `parse.py`, gitignore PNG line |
| 3 | Key/value match | Batch 3 | `pytest tests/crop/test_crop.py -k attach` | N/A stub sidecar | Delete `attach.py` and attach tests |
| 4 | Card then URI | Batch 4 | `pytest tests/openwebui/test_host.py -k "picture or query_card_plain"` | N/A in-process reply | Revert `reply.py` and new host tests |

## Phase 1: crop_bbox (Batch 1)

- [x] 1.1 RED: `tests/crop/test_crop.py::test_crop_bbox_y_window_no_padding`. 10×10 RGB, bbox `(0.2, 0.5, 0.4, 0.6)` → rows `[4, 5)`, cols `[2, 4)` (`floor((1-y1)*H)..ceil((1-y0)*H)`, `floor(x0*W)..ceil(x1*W)`), no padding. `None` or zero area → `None`. Fails `ImportError`. No Pillow in `cut.py`.
- [x] 1.2 GREEN: Empty `src/claimledger/crop/__init__.py` and `crop_bbox(...) -> bytes | None` in `cut.py`. MUST pass. Leave `http/`, `card/card.py`, `measure.py`, `pyproject.toml`, `tests/test_identity.py`.
- [x] 1.3 Retarget `test_wave_c_still_waits` (already red). Allow `crop`. Forbid `chart`, `charts`, `orchestrator`.

## Phase 2: Sidecar hash (Batch 2)

- [x] 2.1 RED: `tests/ingest/test_store.py::test_strip_page_pixels_keeps_hash`. Drop `pages["1"].image` and any `data:image` URI. Hash is sha256 of stripped `canonical_json_bytes` only. Fails `ImportError` or `AttributeError`.
- [x] 2.2 GREEN: `strip_page_pixels` in `store.py`. `load_or_convert` hashes it. `PINNED_DOCLING` stays `2.130.0`. MUST pass.
- [x] 2.3 RED: `tests/ingest/test_store.py::test_sidecar_png_does_not_move_hash`. Stub `parse.last_page_pngs` beside the dict. `<artifact_hash>.p<page_no>.png` leaves the JSON hash unchanged. Empty map writes nothing. `parse.py` sets `generate_page_images = True`; `images_scale` stays `1.0`. Fails: missing file and flag.
- [x] 2.4 GREEN: `page_sidecar` writes the PNG after the hash. `convert_pdf` returns the stripped dict and fills `last_page_pngs` from `pil_image`. Pillow only in `parse.py`. Gitignore `artifacts/docling/*.png`. MUST pass.

## Phase 3: attach (Batch 3)

- [x] 3.1 RED: `tests/crop/test_crop.py::test_attach_matches_identity_key_and_value`. `extract_recipe` with `DocumentClass(kind="eeff", issuer=claim.issuer, period=claim.period)`. Match `identity_key` and `value` plus sidecar → `![crop](data:image/png;base64,...)`. No picture for `21259769`, another value, abstain, or a missing file, and no `source_pdf`. Compare: one each, no delta. Fails `ImportError`.
- [x] 3.2 GREEN: `attach.py` cuts `FinancialEvidence.bbox` via `crop_bbox` (`page` is `page_no`) and encodes PNG. MUST pass. No image on `render_card`.

## Phase 4: Host completion (Batch 4)

- [x] 4.1 RED: `tests/openwebui/test_host.py::test_reply_picture_follows_card`. Match: `card_text` first, then `data:image/png;base64`, same string. Abstain: card only. Compare: card first, no delta, one picture per claim. Keep `_prepare_neighbors` sidecar-free. Fails `AssertionError`.
- [x] 4.2 GREEN: `reply` calls `measure`, `render_card`, `card_text`, `attach`. `return text if not images else text + "\n" + "\n".join(images)`. MUST pass. No route.
- [x] 4.3 `tests/openwebui/test_host.py::test_query_and_card_stay_picture_free`. Query and `render_card` gain no image or bbox. `dependencies` stays `[]`. Allowlist stays 13; `crop/` is off it. Gold stays `21262335` and `21259769`. May already pass.
