# Smoke notes (post-archive)

## Serve pin

`GET /version` → `docling-serve` 1.35.0, `docling` 2.130.0 (core/parse may differ).

## ZIP layout locked (live `v1.35.0`)

Not `document.json` / `page-N.png`. Observed members:

- `{stem}.json` (root)
- `{stem}.dclg` (root)
- `artifacts/page_{NNNNNN}_{sha256}.png` (1-based page index in the numeric field)

`convert_local` accepts both this layout and the older `document.json` / `page-N.png` test layout.

## Sync timeout

Default `DOCLING_SERVE_MAX_SYNC_WAIT=120` returns HTTP 504 on EEFF with OCR. Compose sets `7200`. Client httpx timeout is `7200` s.

## Corpus recompile

Force-clear PDF sha → artifact rows, then `load_or_convert` each PDF in `docs/archivos_muestra` (size-asc). Expect new hashes vs pre-OCR corpus.

**Done 2026-10-07** — `DONE ok=10 fail=0` via serve with `MAX_SYNC_WAIT=7200`.

| PDF | artifact hash (prefix) | pngs |
|-----|------------------------|------|
| Transcripcion 2T26 | `e8e1bd1f9df7…` | 7 |
| Comunicado 1T26 | `3b75a73eabf3…` | 6 |
| Presentacion 2T26 | `df233d4b3767…` | 15 |
| Presentacion 1T26 | `ff66a4be8f43…` | 15 |
| Comunicado 2T26 | `f805af05539d…` | 8 |
| EEFF 1T26 | `393618ab1771…` | 81 |
| EEFF 2T26 | `c155f2f0dd7b…` | 85 |
| Memoria 2023 | `34c8aa192de7…` | 186 |
| Memoria 2025 | `0d5032e7340e…` | 190 |
| Memoria 2024 | `e52ffec5581b…` | 169 |

Compose default `CLAIMLEDGER_ARTIFACT_HASH` → EEFF 1T26 `393618ab1771…`.

## Query with serve stopped

`docker compose stop docling-serve` → `load_or_convert` cache hits for all 10 → `recorded_book()` + `query(understand(…))` → `verified`. No serve required.
