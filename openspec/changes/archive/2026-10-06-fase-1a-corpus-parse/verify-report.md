## Verification Report

**Change**: fase-1a-corpus-parse
**Date**: 2026-10-06
**Mode**: Strict TDD
**Verdict**: PASS WITH WARNINGS

### Completeness

| Metric | Value |
|--------|-------|
| Tasks total | 7 |
| Tasks complete | 7 |
| Tasks incomplete | 0 |

Tasks 1.1–1.2 and 2.1–2.5 are `[x]`.

### Build & Tests

No build command is configured.

`python -m pytest tests/ -q` exited 0: 309 passed, 0 failed, 73 warnings, 18.56s. The same run covers `extract-native-tables`.

On disk, `artifacts/docling/manifest.json` has 10 entries. Each hash has a JSON and a non-empty `.dclg`. These hashes are unchanged: `7b7b624ade1011f9fd75931968312ef5c0fa19fe6061bb2cc5eb1491ffaa364f`, `38406b4b606b9eef004d2319b875584a229452c8981a730d0d9c2321eb6dfc2b`, `b609e48e506b73ee7933329cbdf9cec1eda2fa365afcb71ea7dc525d536fb76c`.

### Requirements

The delta has 2 requirements and 6 scenarios.

| Requirement | Result |
|-------------|--------|
| DocLang sidecar on every parse | Covered by `tests/ingest/test_store.py` doclang tests. The corpus pass wrote ten sidecars. |
| Corpus pass covers every sample PDF | Manifest length 10. Protected hashes unchanged. |

Warning: ingest tests open the two quarterly EEFF through `load_or_convert`. That is a cache read, not the corpus pass. Kernel tests do not import `docling` and do not open those PDFs.

Gold numbers were not edited.
