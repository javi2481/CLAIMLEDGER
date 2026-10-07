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
