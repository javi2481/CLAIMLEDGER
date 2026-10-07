```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:58b06d2d5314deedefb0fe962b48bccaa7552e8a6ce056f3483d3eb40803bf17
verdict: pass_with_warnings
blockers: 0
critical_findings: 0
requirements: 10/10
scenarios: 21/22
test_command: python -m pytest
test_exit_code: 0
test_output_hash: sha256:0d8fb943d7e817ac91e51c431c7e22f4b6730600eb7e1bf9f2e38150880bc99a
build_command: python -c "from claimledger.ingest.parse import convert_local, convert_form_fields; from claimledger.ingest.store import load_or_convert; from claimledger.ingest.types import ConvertBundle; f=convert_form_fields(); assert f['ocr_preset']=='rapidocr' and f['target_type']=='zip'; print('import_ok')"
build_exit_code: 0
build_output_hash: sha256:85c9352893f7cbd399674bdd0d9ba56fe9db8c6b2db35b205f32f137214bbd93
```

## Verification Report

**Change**: max-docling-parse
**Version**: docling-ingest delta (serve v1.35.0 / docling 2.130.0)
**Mode**: Strict TDD

### Completeness

| Metric | Value |
|--------|-------|
| Tasks total | 15 |
| Tasks complete | 15 |
| Tasks incomplete | 0 |

All checklist items in `openspec/changes/max-docling-parse/tasks.md` are `[x]`.

### Build & Tests Execution

**Build**: ✅ Passed (no project build tool; import/seal smoke check)

```text
python -c "from claimledger.ingest.parse import convert_local, convert_form_fields; ..."
import_ok
exit 0
```

**Tests**: ✅ 377 passed / ❌ 0 failed / ⚠️ 0 skipped (73 third-party warnings)

```text
python -m pytest -q
377 passed, 73 warnings in 19.94s
EXIT:0
```

**Coverage**: ➖ Not available (openspec `coverage.detected: false`)

### Smoke (Docker)

**Status**: `/version` ✅ PASS; full corpus convert ⚠️ DEFERRED

Observed `GET http://127.0.0.1:5001/version` (HTTP 200):

```json
{
  "docling-serve": "1.35.0",
  "docling": "2.130.0",
  "docling-core": "2.98.0",
  "docling-parse": "7.21.0"
}
```

Pin checks: serve `1.35.0` + docling `2.130.0` ✅. Did **not** require core/parse `==2.130.0` ✅.

Container: `docker compose up -d docling-serve` → image `quay.io/docling-project/docling-serve-cpu:v1.35.0` pulled and healthy.

#### Deferred smoke checklist (remaining)

```text
# 1) Serve already up from verify; or restart:
docker compose up -d docling-serve
# wait until healthy, then:
curl -s http://127.0.0.1:5001/version
# expect docling-serve == 1.35.0 and docling == 2.130.0

# 2) One corpus PDF via load_or_convert (with .[docling] env):
python -c "from pathlib import Path; from claimledger.ingest.store import load_or_convert; p=sorted(Path('docs/archivos_muestra').glob('*.pdf'))[0]; print(load_or_convert(p))"
# expect artifacts/docling/<hash>.json + <hash>.dclg + <hash>.pN.png + manifest.json
# lock ZIP member names if they differ from document.json / document.dclg / page-{n}.png

# 3) Query with serve stopped still serves hashed artifacts:
docker compose stop docling-serve
# run a query/host path that loads hashed JSON only — must succeed without serve
```

### Spec Compliance Matrix

| Requirement | Scenario | Test | Result |
|-------------|----------|------|--------|
| Docling-Serve Convert Only | Posts ZIP convert/file | `tests/ingest/test_convert_local.py` > `test_convert_local_posts_zip_referenced_rapidocr` | ✅ COMPLIANT |
| Docling-Serve Convert Only | Embedded compiler banned | `test_convert_local_happy_path_has_no_embedded_compiler` + `test_ingest_sources_forbid_embedded_compiler_and_url_convert` | ✅ COMPLIANT |
| Docling-Serve Convert Only | Query independent of serve | `tests/test_query.py` (kernel; no serve) + convert_local only in ingest parse/store | ✅ COMPLIANT |
| Non-VLM Dual Seal | Client seal and remote off | `test_convert_local_seal_on_and_off_fields` + `test_compose_remote_services_false_and_no_runtime_depends_on_serve` | ✅ COMPLIANT |
| Serve Version Pin Smoke | /version pin | Live smoke `GET /version` (serve 1.35.0, docling 2.130.0) | ✅ COMPLIANT |
| Convert Unit Tests Mock HTTP | Default pytest offline | Full suite 377 green; convert/store mock httpx ZIP | ✅ COMPLIANT |
| In-Corpus Local PDFs | Directory files are in corpus | `tests/ingest/test_classify.py` > `test_corpus_lists_the_ten_sample_pdfs` | ✅ COMPLIANT |
| In-Corpus Local PDFs | URL convert is forbidden | `test_convert_local_rejects_non_path_and_url` + `test_load_or_convert_rejects_non_path` | ✅ COMPLIANT |
| Hashed Immutable JSON Store | Load or convert by hash | `test_load_existing_artifact_by_canonical_hash` + `test_missing_hash_converts_local_path_only` | ✅ COMPLIANT |
| Hashed Immutable JSON Store | Mismatched bytes are rejected | `test_load_rejects_bytes_that_do_not_match_the_name` | ✅ COMPLIANT |
| Hashed Immutable JSON Store | Cache hit does not reconvert a mismatch | `test_cache_hit_rejects_mismatch_without_reconvert` | ✅ COMPLIANT |
| Docling Pin Without Graph | Pin and graph ban | Smoke `/version` + convert path has no `docling-graph` | ✅ COMPLIANT |
| Docling Pin Without Graph | extract_recipe may keep docling_core | `tests/ingest/test_extract.py` (grid/`docling_core`; pin in extract) | ✅ COMPLIANT |
| Sidecar Page Raster | Sidecar does not move the hash | `test_sidecar_png_from_zip_does_not_move_hash` | ✅ COMPLIANT |
| Sidecar Page Raster | Absorbed pixels are stripped | `test_strip_page_pixels_keeps_hash` | ✅ COMPLIANT |
| Sidecar Page Raster | Hash proof stays synthetic | sidecar/strip tests use synthetic payloads | ✅ COMPLIANT |
| DocLang Sidecar On Every Parse | Fresh convert writes JSON and DocLang | `test_saved_json_stores_zip_doclang` + `test_missing_hash_converts_local_path_only` | ✅ COMPLIANT |
| DocLang Sidecar On Every Parse | Missing DocLang forces recompile | `test_missing_doclang_forces_recompile` | ✅ COMPLIANT |
| DocLang Sidecar On Every Parse | Second call is a no-op | `test_existing_pdf_hash_loads_without_reconvert` | ✅ COMPLIANT |
| Corpus Pass Covers Every Sample PDF | Ten local files are stored | Enumerated by classify; live 10-PDF serve pass not run in verify | ⚠️ PARTIAL |
| Corpus Pass Covers Every Sample PDF | Existing quarterly JSON is not reconverted when complete | `test_existing_pdf_hash_loads_without_reconvert` | ✅ COMPLIANT |
| Corpus Pass Covers Every Sample PDF | Default pytest does not convert the corpus | Full pytest offline; no live corpus convert | ✅ COMPLIANT |

**Compliance summary**: 21/22 scenarios compliant; 1 PARTIAL (live ten-PDF corpus pass)

### Correctness (Static Evidence)

| Requirement | Status | Notes |
|------------|--------|-------|
| Docling-Serve Convert Only | ✅ Implemented | `convert_local` → multipart `/v1/convert/file`; ZIP unpack |
| Non-VLM Dual Seal | ✅ Implemented | Form seal + Compose `REMOTE_SERVICES=false` |
| Serve Version Pin | ✅ Implemented | Image `v1.35.0`; smoke confirmed |
| Mock HTTP unit tests | ✅ Implemented | `test_convert_local` + `test_store` |
| In-corpus / no URL | ✅ Implemented | Path-only `IngestError` |
| Hashed JSON store | ✅ Implemented | strip → hash → `.json`/`.dclg`/PNG/manifest |
| Pin without graph on convert | ✅ Implemented | Pin smoke on serve; no graph on convert path |
| Sidecar PNGs | ✅ Implemented | From ZIP `page-{n}.png` |
| DocLang from ZIP | ✅ Implemented | Missing `.dclg` recompiles; no `export_to_doclang` |
| Corpus pass | ⚠️ Partial live | Mechanics tested; full serve corpus pass deferred |

### Coherence (Design)

| Decision | Followed? | Notes |
|----------|-----------|-------|
| Serve compiles; CLAIMLEDGER hashes/stores | ✅ Yes | |
| httpx multipart ZIP referenced | ✅ Yes | |
| DocLang ZIP-only; missing ⇒ recompile | ✅ Yes | |
| PNGs from ZIP | ✅ Yes | |
| Pin via `/version` | ✅ Yes | Live smoke |
| httpx in `[docling]` | ✅ Yes | `httpx==0.28.1` |
| No claimledger `depends_on` serve | ✅ Yes | only openwebui→claimledger |
| extract_recipe + docling_core stays | ✅ Yes | pin helper moved to extract (documented deviation) |
| Delete embedded converter path | ✅ Yes | absent from `parse.py` |

### TDD Compliance

| Check | Result | Details |
|-------|--------|---------|
| TDD Evidence reported | ✅ | `sdd/max-docling-parse/apply-progress` table present |
| All tasks have tests | ✅ | 1.x–4.x covered; 5.1 docs; 6.1 smoke checklist |
| RED confirmed (tests exist) | ✅ | `tests/ingest/test_convert_local.py`, `test_store.py` |
| GREEN confirmed (tests pass) | ✅ | 377 passed on verify execution |
| Triangulation adequate | ✅ | ZIP/seal/URL/cache/compose cases |
| Safety Net for modified files | ✅ | Reported in apply-progress |

**TDD Compliance**: 6/6 checks passed

### Test Layer Distribution

| Layer | Tests | Files | Tools |
|-------|-------|-------|-------|
| Unit | ~24 (convert+store focus) | `test_convert_local.py`, `test_store.py` | pytest + mock httpx |
| Integration | remainder of suite | ingest/graph/http/host/… | pytest |
| E2E | 0 (browser) | — | not installed |
| Smoke | `/version` live | Docker Compose | docker compose |
| **Total suite** | **377** | | |

### Changed File Coverage

Coverage analysis skipped — no coverage tool detected.

### Assertion Quality

**Assertion quality**: ✅ All assertions verify real behavior (form seal fields, URL reject, ZIP members, cache/recompile, Compose remote=false)

### Quality Metrics

**Linter**: ➖ Not available  
**Type Checker**: ➖ Not available  

### Issues Found

**CRITICAL**: None

**WARNING**:
1. Live ten-PDF corpus pass + one-PDF artifact materialization + query-with-serve-stopped not executed in this verify (only `/version` smoke). Deferred checklist above.
2. Design open questions remain: ZIP member names after first real convert; confirm UI-off env on pin (Compose already sets `DOCLING_SERVE_ENABLE_UI=false`).
3. Proposal success-criteria checkboxes still unchecked in `proposal.md` (cosmetic; tasks/design done).

**SUGGESTION**:
1. After first real ZIP unpack, lock member-name regexes in design if they differ from `document.json` / `document.dclg` / `page-{n}.png`.
2. Plan file todos still show some `in_progress`/`pending` — sync when archiving.

### Verdict

**PASS WITH WARNINGS**

15/15 tasks complete; 377/377 pytest green; `/version` smoke confirms serve `1.35.0` + docling `2.130.0`; one corpus-pass scenario remains PARTIAL pending live serve convert of sample PDFs.
