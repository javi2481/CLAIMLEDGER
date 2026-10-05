# Proposal: Phase 8 Page Crop

## Intent

Open WebUI must show the marked-zone photo after the card. Coordinates cannot. Architecture Gate: the crop exists only for that gap.

## Scope

### In Scope

- Crop stored `FinancialEvidence.bbox` (cell, else table `prov`) from a sidecar beside the hashed JSON.
- Y-flip to a top-origin image. No padding. Pixels stay out of `canonical_json_bytes`.
- Card text, then the PNG, on key and value match. Abstain or no sidecar: none. Compare: one each, no delta.
- Synthetic-pixel tests. No `docling`, PDF, network, or Docker in kernel tests.

### Out of Scope

- Query JSON, another viewer, PDF re-raster, `render_card` or LLM picture, table-box crop.
- Padding, origin field, seed evidence, gold, `dependencies`, 13-path allowlist.
- Phases 9–13, Pipelines, Knowledge RAG, MinerU. Rector unedited in apply.

## Capabilities

### New Capabilities

- `page-crop`: Stored-bbox cut. Y-flip, no padding. Match `identity_key` and `value`; sidecar required.

### Modified Capabilities

- `openwebui-host`: Picture after card text in the same message. Retire only "crop MUST wait".
- `docling-ingest`: Sidecar rasters at conversion. Pin `docling==2.130.0` must not hash pixels.

Other specs stay unchanged.

## Approach

Approach 1. Off the kernel and `http/`, cut the stored bbox on a caller raster. Synthetic pixels. Sidecar outside the hash. Host calls `measure` then `render_card`. Kernel picks the number. Pin `v0.11.4-slim`. `dependencies` stays `[]`.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| Crop function | New | Stored bbox, Y-flip, no padding |
| `ingest/parse.py`, `ingest/store.py` | Modified | Sidecar; hash stays JSON |
| `openwebui/reply.py` | Modified | Picture after `card_text` |
| Crop and host tests | New | Synthetic pixels; in-process |
| `card/`, `measure.py`, `http/` | Unchanged | No image, no new fields |
| `pyproject.toml`, `test_identity.py` | Unchanged | `[]`; 13 paths |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Y axis | High | Top `1-y1`; bottom `1-y0` |
| Neighbor or hash | Med | Match key and value |
| Stripped image | Med | Our PNG; same pin |

## Rollback Plan

Remove crop, sidecars, host append, and tests. Restore "crop waits". Leave card, query, gold, allowlist, and hashes. No migration.

## Dependencies

- Matching extract evidence (`identity_key`, `value`).
- Page image at conversion, pin `docling==2.130.0`.
- `ghcr.io/open-webui/open-webui:v0.11.4-slim`. Do not commit gitignored artifacts.

## Success Criteria

- [ ] `21262335` and `21259769` stay. The picture follows only that value.
- [ ] Abstain is the card alone. Compare adds no delta.
- [ ] The sidecar does not change `artifact_hash`.
- [ ] `POST /claims/query` and `render_card` stay picture-free.
- [ ] Synthetic-pixel tests. Kernel bans, 13 paths, and `dependencies` `[]` stay.
