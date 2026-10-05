```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:988fd3ca0b00c0750545a1a6fb0ba2579df6a0778b41ce6458faf4cb0a16102d
verdict: pass
blockers: 0
critical_findings: 0
requirements: 8/9
scenarios: 21/22
test_command: python -m pytest tests/ -q
test_exit_code: 0
test_output_hash: sha256:988fd3ca0b00c0750545a1a6fb0ba2579df6a0778b41ce6458faf4cb0a16102d
build_command: ""
build_exit_code: 0
build_output_hash: sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

## Verification Report

**Change**: fase-8-crop
**Version**: N/A
**Mode**: Strict TDD

`evidence_revision` and `test_output_hash` are the SHA-256 of the raw `python -m pytest tests/ -q` stdout+stderr after the order-isolation fix (6312 bytes, Windows CRLF, 72 CRLF newlines, 0 bare LF). `build_command` in `openspec/config.yaml` is empty, so no build process was started. `build_output_hash` is the SHA-256 of empty output. `build_exit_code: 0` records that absence, not a compiler run.

Canonical verification-evidence bytes are that pytest capture, preserved at `C:\Users\Equipo\AppData\Local\Temp\fase8-crop-pytest.bin`. The preimage is not this markdown file. This report does not archive the change.

Counted from `openspec/changes/fase-8-crop/specs/page-crop/spec.md`, `specs/docling-ingest/spec.md`, and `specs/openwebui-host/spec.md`, matching Engram `sdd/fase-8-crop/spec` (#1090): **9 requirements, 22 scenarios**.

### Completeness
| Metric | Value |
|--------|-------|
| Tasks total | 12 |
| Tasks complete | 12 |
| Tasks incomplete | 0 |

All twelve checkboxes in `openspec/changes/fase-8-crop/tasks.md` are `[x]` (1.1–1.3, 2.1–2.4, 3.1–3.2, 4.1–4.3). Full suite was allowed to run.

Engram `sdd/fase-8-crop/tasks` (#1094) and `sdd/fase-8-crop/apply-progress` (#1096) match that checklist.

### Build & Tests Execution
**Build**: ➖ No build command configured (`build_command: ""`)

**Tests**: ✅ 307 passed / 0 failed / 0 skipped (73 warnings)
```text
python -m pytest tests/ -q
exit 0
........................................................................ [ 23%]
........................................................................ [ 46%]
........................................................................ [ 70%]
........................................................................ [ 93%]
...................                                                      [100%]
307 passed, 73 warnings in 18.64s
```

The first full run, before the fix below, exited 1: `1 failed, 306 passed, 73 warnings in 23.22s` (sha256 `ef7a895a16132b606705a6f6a63c13348165c52f487115ee7b35f7172667b3cb`). The only failure was `tests/openwebui/test_host.py::test_reply_picture_follows_card`. The same assertion in `tests/crop/test_crop.py::test_attach_matches_identity_key_and_value` fails when that file is collected after a graph test, and passes in the default order because `tests/crop` runs before `tests/graph`. Neither failure came from `fase-8a-corpus-parse` or `fase-8b-native-stack`. Those trees were not edited.

The assertion required `docling` to be absent from `sys.modules` at the start of the test. Graph tests import Docling, so the crop tests failed after them even though `crop/` and `reply` do not import `docling`. Strict TDD on that defect:

1. RED already observed: `assert not True` at the process-wide module check.
2. The check was replaced with an AST scan of the crop package, `reply.py`, and the owning test, plus a before/after module delta.
3. A probe `import docling` inside `reply` failed the new assertion for the right reason: `AssertionError: assert ['reply.py'] == []` (`python -m pytest tests/openwebui/test_host.py::test_reply_picture_follows_card -q`, exit 1). That import was removed. `reply.py` is back to `measure`, `render_card`, `card_text`, then `attach`.
4. Focused re-run after `tests/graph/test_conflict.py`: 7 passed, exit 0.
5. Full suite once: 307 passed, exit 0. That run is the hashed preimage.

The 73 warnings are Docling and docling-graph deprecations inside graph tests. Crop tests added none. Gold numbers stayed frozen. `tests/test_gold_v1.py` and `tests/test_gold_v2.py` passed. The six kernel test files do not import `docling`. `dependencies = []`. The HTTP extra pin is `starlette==1.0.0`. `src/claimledger/__init__.py` is empty.

**Coverage**: mean of the pytest-cov Cover column on the six changed production modules is 90.2%. Config threshold is 0. Cached `openspec/config.yaml` still says coverage was not detected; pytest-cov 7.1.0 is installed and was used for this extra run only.

A second command, `python -m pytest tests/crop/test_crop.py tests/ingest/test_store.py tests/openwebui/test_host.py --cov=claimledger.crop --cov=claimledger.ingest.store --cov=claimledger.ingest.parse --cov=claimledger.openwebui.reply --cov-branch --cov-report=term-missing -q --tb=no`, exited 0 (36 passed). That run is not the hashed preimage. `parse.py` is under 80% because the live `convert_pdf` path is stubbed.

### Spec Compliance Matrix
| Requirement | Scenario | Test | Result |
|-------------|----------|------|--------|
| Stored Bbox Cut | Y flip and no padding | `tests/crop/test_crop.py > test_crop_bbox_y_window_no_padding`, `test_crop_bbox_other_window_matches_source_pixels` | ✅ COMPLIANT |
| Stored Bbox Cut | Stored cell box is the cut | `tests/crop/test_crop.py > test_attach_matches_identity_key_and_value` (cell bbox `(0.2, 0.5, 0.4, 0.6)`, not the table box) | ✅ COMPLIANT |
| Stored Bbox Cut | No box yields no picture | `tests/crop/test_crop.py > test_crop_bbox_y_window_no_padding` (`None` and zero-area return `None`) | ✅ COMPLIANT |
| Matching Claim Picture | Key and value match | `tests/crop/test_crop.py > test_attach_matches_identity_key_and_value` | ✅ COMPLIANT |
| Matching Claim Picture | Neighbor value yields no picture | `tests/crop/test_crop.py > test_attach_matches_identity_key_and_value` | ✅ COMPLIANT |
| Matching Claim Picture | Abstain or missing sidecar | `tests/crop/test_crop.py > test_attach_matches_identity_key_and_value`; `tests/openwebui/test_host.py > test_reply_picture_follows_card` | ✅ COMPLIANT |
| Matching Claim Picture | Compare has no delta | `tests/crop/test_crop.py > test_attach_matches_identity_key_and_value`; `tests/openwebui/test_host.py > test_reply_picture_follows_card` | ✅ COMPLIANT |
| Query and Card Stay Picture-Free | Query and card stay plain | `tests/openwebui/test_host.py > test_query_and_card_stay_picture_free` | ✅ COMPLIANT |
| Synthetic Tests and Closed Bounds | Synthetic cut, allowlist, and gold | `tests/crop/test_crop.py > test_crop_bbox_y_window_no_padding`, `test_attach_matches_identity_key_and_value`; `tests/openwebui/test_host.py > test_query_and_card_stay_picture_free`, `test_reply_picture_follows_card` | ✅ COMPLIANT |
| Synthetic Tests and Closed Bounds | Later work stays out | `tests/openwebui/test_host.py > test_wave_c_still_waits`; padding and PDF open are covered elsewhere | ⚠️ PARTIAL |
| Sidecar Page Raster Outside the Hash | Sidecar does not move the hash | `tests/ingest/test_store.py > test_sidecar_png_does_not_move_hash` | ✅ COMPLIANT |
| Sidecar Page Raster Outside the Hash | Absorbed pixels are stripped | `tests/ingest/test_store.py > test_strip_page_pixels_keeps_hash`, `test_page_images_capture_uses_pil_image` | ✅ COMPLIANT |
| Sidecar Page Raster Outside the Hash | Hash proof stays synthetic | `tests/ingest/test_store.py > test_strip_page_pixels_keeps_hash`, `test_sidecar_png_does_not_move_hash` | ✅ COMPLIANT |
| Measure Then Card | Consolidated value | `tests/openwebui/test_host.py > test_reply_consolidated_21262335` | ✅ COMPLIANT |
| Measure Then Card | Parent value | `tests/openwebui/test_host.py > test_reply_parent_21259769_both_rows` | ✅ COMPLIANT |
| Measure Then Card | Picture follows the card | `tests/openwebui/test_host.py > test_reply_picture_follows_card` | ✅ COMPLIANT |
| Always That Card | Abstain is the reply | `tests/openwebui/test_host.py > test_reply_picture_follows_card`, `test_reply_abstain_adds_no_verified_value` | ✅ COMPLIANT |
| Always That Card | Compare has no delta | `tests/openwebui/test_host.py > test_reply_picture_follows_card`, `test_reply_compare_copies_both_values_without_delta` | ✅ COMPLIANT |
| Features Off | One card only | `tests/openwebui/test_host.py > test_completions_returns_only_the_card`, `test_stream_is_one_card_then_done` | ✅ COMPLIANT |
| Features Off | Models lists no card | `tests/openwebui/test_host.py > test_models_lists_only_claimledger_card` | ✅ COMPLIANT |
| Closed Bounds | Allowlist and kernel bans | `tests/openwebui/test_host.py > test_query_and_card_stay_picture_free`, `test_host_stays_off_claims_route_and_allowlist`; `tests/http/test_app.py > test_http_extra_pins_starlette_only`; `tests/test_identity.py > test_import_scan_stays_clean`, `test_kernel_modules_importable` | ✅ COMPLIANT |
| Closed Bounds | Wave C waits | `tests/openwebui/test_host.py > test_wave_c_still_waits` | ✅ COMPLIANT |

**Compliance summary**: 21/22 scenarios compliant, 1 partial

`test_wave_c_still_waits` asserts package `crop`, disjointness from `chart`, `charts`, and `orchestrator`, that `fase-8-crop` is an active change, and that no active name starts with fase-9 through fase-13. It does not name MinerU or another viewer. `test_crop_bbox_y_window_no_padding` locks the unpadded window. `test_attach_matches_identity_key_and_value` raises if a `.pdf` is opened. Those pieces cover padding and question-time re-raster. MinerU and another viewer have no assertion, so "Later work stays out" stays partial.

`test_reply_picture_follows_card` calls `reply` and requires `card_text` first, one `data:image/png;base64` on the consolidated match, abstain with no picture, and compare with two different pictures and no delta in the card prefix. `test_query_and_card_stay_picture_free` reads `POST /claims/query` for consolidated, parent, and compare, asserts no `bbox` or image, and checks `ClaimCard` fields, `dependencies == []`, allowlist length 13, and gold `21262335` / `21259769`. Those tests passed inside this suite.

### Correctness (Static Evidence)
| Requirement | Status | Notes |
|------------|--------|-------|
| Stored Bbox Cut | ✅ Implemented | `crop_bbox` lives in `src/claimledger/crop/cut.py`, outside `http/` and off the 13-path allowlist. Rows are `floor((1-y1)*H)..ceil((1-y0)*H)`, columns `floor(x0*W)..ceil(x1*W)`. `None` or zero area returns `None`. No Pillow in `cut.py`. |
| Matching Claim Picture | ✅ Implemented | `attach` uses `extract_recipe` on `identity_key` and `value`, then `page_sidecar` and `crop_bbox`. Abstain, other value, missing file, and zero area return no picture. Compare keeps claim order and does not subtract. |
| Query and Card Stay Picture-Free | ✅ Implemented | `claims_query` evidence keys stay `document_id`, `page`, `text`. `ClaimCard` has no image field. `render_card` / `card_text` do not append a PNG. |
| Synthetic Tests and Closed Bounds | ⚠️ Partial | Synthetic pixels, no crop `docling` import, allowlist 13, `dependencies = []`, and frozen gold are tested. Phases 9–13 are banned by name. MinerU and another viewer are not named by a test. |
| Sidecar Page Raster Outside the Hash | ✅ Implemented | `strip_page_pixels` drops page `image` and `data:image` URIs before `canonical_json_bytes`. `page_sidecar` is `artifacts/docling/<artifact_hash>.p<page_no>.png`. `generate_page_images = True`. `images_scale` is not reassigned. `PINNED_DOCLING` stays `2.130.0`. Sidecar tests stub `convert_pdf` with synthetic JSON. |
| Measure Then Card | ✅ Implemented | `reply` calls `measure`, then `render_card`, then `card_text`, then `attach`. The PNG string is appended only when `attach` returns pictures. Consolidated and parent neighbor tests still show the kernel values. |
| Always That Card | ✅ Implemented | Abstain text is the card alone. Compare keeps both values, rejects a delta in the card prefix, and may append one picture per verified claim. |
| Features Off | ✅ Implemented | `GET /v1/models` returns only `claimledger-card`. `POST /v1/chat/completions` sends the `reply` string. Compose still turns titles, follow-ups, Ollama, Knowledge, and MCP off. |
| Closed Bounds | ✅ Implemented | `dependencies = []`, `starlette==1.0.0`, allowlist length 13, empty root `__init__.py`, and frozen gold passed. Kernel tests do not import `docling`. Host tests stay in-process. |

### Coherence (Design)
| Decision | Followed? | Notes |
|----------|-----------|-------|
| Module `crop/cut.py`, `crop/attach.py`, off `http/` and off the allowlist | ✅ Yes | |
| Rectangle is stored `FinancialEvidence.bbox`; no padding; no origin field | ✅ Yes | Cell box wins over table `prov` in the attach fixture. |
| Half-open Y window | ✅ Yes | 10×10 bbox `(0.2, 0.5, 0.4, 0.6)` is rows `[4, 5)`, columns `[2, 4)`. |
| Raster is row-major RGB; Pillow stays out of `cut.py` | ✅ Yes | Pillow is used in `attach.py` and `parse.py`. |
| Sidecar `artifacts/docling/<artifact_hash>.p<page_no>.png` after `strip_page_pixels` | ✅ Yes | `.gitignore` contains `artifacts/docling/*.png`. |
| `generate_page_images = True`; `images_scale` stays `1.0` | ✅ Yes | No `images_scale` assignment in `parse.py`. |
| Match via `extract_recipe` on identity key and value | ✅ Yes | |
| `reply` appends `![crop](data:image/png;base64,...)` after `card_text` | ✅ Yes | `build_host` still sends that one string. |
| Miss path is the card only; no question-time PDF raster | ✅ Yes | Abstain and missing sidecar return no picture. `.pdf` open is rejected in the attach test. |
| `dependencies` stay `[]`; pin `docling==2.130.0` | ✅ Yes | |
| Phases 9–13 stay out | ✅ Yes | `test_wave_c_still_waits` passed. Active siblings `fase-8a-corpus-parse` and `fase-8b-native-stack` are allowed by that test and were not part of this failure. |

### TDD Compliance
| Check | Result | Details |
|-------|--------|---------|
| TDD Evidence reported | ✅ | Engram `sdd/fase-8-crop/apply-progress` (#1096) has a TDD table for tasks 1.1–4.3. |
| All tasks have tests | ✅ | 12/12 tasks name tests in `tests/crop/test_crop.py`, `tests/ingest/test_store.py`, or `tests/openwebui/test_host.py`. Those files exist. |
| RED confirmed (tests exist) | ✅ | Apply recorded ImportError / AssertionError reds. This verify re-ran the suite-order failure, then confirmed the replacement assertion fails when `reply.py` imports `docling`. |
| GREEN confirmed (tests pass) | ✅ | Focused run after graph tests: 7 passed. Full suite: 307 passed, exit 0. |
| Triangulation adequate | ✅ | Two crop windows. Attach covers match, neighbor value, abstain, missing sidecar, and compare order. Host picture covers match, abstain, and compare. |
| Safety Net for modified files | ✅ | Apply-progress records pre-edit runs for store and host. This verify ran the failing tests before editing the assertions. |

**TDD Compliance**: 6/6 checks passed

---

### Test Layer Distribution
| Layer | Tests | Files | Tools |
|-------|-------|-------|-------|
| Unit | 9 | 3 | pytest |
| Integration | 0 | 0 | not installed |
| E2E | 0 | 0 | not installed |
| **Total** | **9** | **3** | |

The nine tests are the three in `tests/crop/test_crop.py`, `test_strip_page_pixels_keeps_hash`, `test_sidecar_png_does_not_move_hash`, `test_page_images_capture_uses_pil_image`, `test_reply_picture_follows_card`, `test_query_and_card_stay_picture_free`, and `test_wave_c_still_waits`. They use synthetic RGB or JSON, stub `convert_pdf`, or call `reply` / `claims_query` in-process. No browser, bound port, Docker daemon, network, or PDF parse. Older host tests that use `TestClient` were not added by this change.

---

### Changed File Coverage
| File | Line % | Branch % | Uncovered Lines | Rating |
|------|--------|----------|-----------------|--------|
| `src/claimledger/crop/__init__.py` | 100% | 100% | — | ✅ Excellent |
| `src/claimledger/crop/attach.py` | 91% | 15/18 | L31, L45, L52 | ⚠️ Acceptable |
| `src/claimledger/crop/cut.py` | 92% | 10/12 | L40, L42 | ⚠️ Acceptable |
| `src/claimledger/ingest/parse.py` | 67% | 12/16 | L16, L20–23, L34, L52, L54, L87–108 | ⚠️ Low |
| `src/claimledger/ingest/store.py` | 91% | 40/48 | L60, L78, L82, L101, L119, L139 | ⚠️ Acceptable |
| `src/claimledger/openwebui/reply.py` | 100% | 100% | — | ✅ Excellent |

**Average changed file coverage**: 90.2% (mean of the Cover column). Statement-weighted total for these six modules: 86% (275 statements, 33 missed).

`parse.py` L87–108 is `convert_pdf`, which these tests stub so they do not import Docling or open a PDF. No other changed production file is under 80%.

---

### Assertion Quality
| File | Line | Assertion | Issue | Severity |
|------|------|-----------|-------|----------|
| `tests/openwebui/test_host.py` | 691 | `assert "false" in compose` | Runs once per feature flag but does not check that flag's value. Any other `false` in the file satisfies it. Pre-existing; this change did not add it. | WARNING |

**Assertion quality**: 0 CRITICAL, 1 WARNING

The docling checks walk real source files. A probe import in `reply.py` made `test_reply_picture_follows_card` fail. Empty attach results sit next to a non-empty match in the same test. No tautology and no ghost loop.

---

### Quality Metrics
**Linter**: ➖ Not available (cached capabilities: `linter: not_detected`)
**Type Checker**: ➖ Not available (cached capabilities: `type_checker: not_detected`)

### Issues Found
**CRITICAL**: None

**WARNING**: "Later work stays out" does not assert MinerU or another viewer. Phases 9–13, chart packages, the unpadded crop window, and the PDF-open guard did pass.

**WARNING**: `src/claimledger/ingest/parse.py` line coverage is 67%. The missed block is the live Docling convert, which crop and sidecar tests are required not to run.

**WARNING**: `test_compose_pins_slim_screen` does not bind each feature flag to `false`.

**SUGGESTION**: `POST /v1/chat/completions` is not given a sidecar fixture. `build_host` returns `reply`, and `test_reply_picture_follows_card` covers that string. Clamp edges in `cut.py` (L40, L42) and the missing-JSON / empty-evidence branches in `attach.py` are uncovered.

### Verdict
PASS WITH WARNINGS
21/22 scenarios have a covering test that passed in this run. One scenario is partial. The suite is green (307 passed, 0 failed, 0 skipped, exit 0). The first failure was inside fase-8-crop and is fixed. Parallel changes `fase-8a-corpus-parse` and `fase-8b-native-stack` did not fail a test and were not edited. This report does not archive the change.
