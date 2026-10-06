## Exploration: fase-8-crop

Architecture is CLOSED. This change supplies only the visual proof rector §20 names for phase 8: a crop of the page zone Docling already marked, shown beside the verified claim. It is our picture of that zone. It is not another platform's PDF viewer. The wave C gate in `docs/plan-implementacion.md` ("¿La ficha ya convence sin foto?") is open because the user explicitly asked to continue with phase 8 on 2026-10-05. A design that exists only because it looks nice stays rejected. Out of this change, and still waiting: phase 9 period pack / subtraction, phase 10 VLM, phase 11 Neo4j, phase 12 charts, phase 13 orchestrator. Also out: Pipelines, Knowledge RAG, MinerU.

### Current State

`docs/documento-rector.md` §20: "Más adelante (Fase 8). Recorte propio: la zona de la página que Docling ya marcó, junto al claim. No es el visor de otra plataforma. Es nuestra prueba visual." §13 says the small API contract does not carry that image on day one, and that evidence later gains a page crop (row or table image, Docling box). §21: CLAIMLEDGER verifies; Open WebUI draws the card, the crop, and the chart. North star: the page crop comes after the card. Do not copy another platform's trick.

`docs/informe-arquitectura.md` phase table: "8 — Recorte | Foto de la zona de la página (bbox Docling) | Prueba visual propia". `docs/stack-oportunidades.md`: own crop of the Docling bbox beside the claim. `docs/plan-implementacion.md` wave C lists the phase 8 gate and says a "porque queda lindo" answer is no. Phases 0–7 are archived. Active change: none. Annotated tag `mvp` sits on the fase-7-openwebui close. Phases 9–13 stay waiting.

`FinancialEvidence.bbox` in `src/claimledger/evidence.py` is optional and, when present, normalized 0–1 with `x0<=x1` and `y0<=y1`. Ingest already fills it. `extract_recipe` in `src/claimledger/ingest/extract.py` reads the hashed Docling JSON. For each recipe cell it sets `bbox = _cell_bbox(cell, page_size) or table_bbox`. `_cell_bbox` reads the cell `bbox`. The fallback `_provenance_bbox` reads the table `prov` bbox. `_normalize_bbox` divides `l`/`r` by page width and `b`/`t` by page height, sorts each pair, and clamps. It does not read `coord_origin`. The extract fixture in `tests/ingest/test_extract.py` stamps `coord_origin: BOTTOMLEFT` on both the cell and the table `prov`. A cell `b=400`, `t=420` on a page of height 800 becomes stored `y0=0.5`, `y1=0.525`, measured from the bottom of the page. An image whose row 0 is the top of the page is not that axis.

`convert_pdf` in `src/claimledger/ingest/parse.py` builds `PdfPipelineOptions(do_ocr=False)` and returns `result.document.export_to_dict()`. It does not set `generate_page_images` and it does not write a page raster. `load_or_convert` stores `artifacts/docling/{artifact_hash}.json` from `canonical_json_bytes`. The hash is those bytes. `StoredDocument` keeps `source_pdf` only in memory. The manifest maps PDF sha256 to artifact hash. It does not store a path back to the PDF and it does not store a PNG. Current Docling docs show page rasters as `page.image.pil_image` when page images are generated, saved beside the document rather than used as a viewer ([export figures](https://docling-project.github.io/docling/_generated/examples/export_figures), [pipeline options](https://docling-project.github.io/docling/reference/pipeline_options)). Those pages describe the current docs. They are not a proof of the pin `docling==2.130.0`. Pixels must not enter the hashed JSON.

`Ledger.seed()` records recipe rows with `evidence=()`. `measure` retrieves the tables drawer, then `understand`, then `query(intent, Ledger.seed())`. The verified claim therefore has no bbox. `Candidate` is `drawer`, `text`, `ref`. It has no box. `render_card` copies seal, chips, row texts, and kernel `values`. It does not look at evidence. `card_text` copies that `ClaimCard` into one string. `reply` is `card_text(render_card(*measure(...)))`. The host completion's assistant `content` is that string. `openspec/specs/openwebui-host/spec.md` says one completion is exactly that card, a second message must not appear before or after it, and "Crop, subtraction, charts, and the orchestrator MUST wait."

`POST /claims/query` is the only route in `src/claimledger/http/`. `openspec/specs/http-query/spec.md` allows `status`, `claim` (`issuer`, `period`, `statement`, `scope`, `metric`, `value`, `currency`), and `evidence`. It forbids `answer`, `identity`, `identity_key`, `unit`, `ledger_status`, `artifact_hash`, `label`, and `bbox`. Seed evidence on that route is `[]`. Compare must not add `delta`.

`dependencies` in `pyproject.toml` stays `[]`. The docling extra pins `docling==2.130.0` and `docling-graph==1.9.1`. The HTTP extra pin is `starlette==1.0.0`. The 13-path allowlist in `tests/test_identity.py` is seven kernel modules and six kernel tests. Kernel tests must not import `docling`, and must not use the network, a PDF, or Docker. Host tests stay in-process and off those 13 paths.

No crop module exists. No page PNG exists in the store. The card can be shown without a photo. The photo the rector asks for cannot be produced from the JSON coordinates alone.

### Affected Areas

- `src/claimledger/evidence.py` — read. The stored bbox is the crop rectangle. Do not add an origin field and do not change validation.
- `src/claimledger/ingest/extract.py` — read. Cell bbox, else table `prov`, already normalized. The crop consumes that tuple. Do not make extract choose `21262335` or `21259769` a second time.
- `src/claimledger/ingest/parse.py` and `src/claimledger/ingest/store.py` — the hashed JSON has page size and provenance, not a raster. A page image has to be saved beside that JSON without entering `canonical_json_bytes`.
- `src/claimledger/ledger.py` — read. `Ledger.seed()` evidence is empty. Query stays on the seed. The crop is not a reason to put ingest evidence onto the seed.
- `src/claimledger/card/card.py` and `openspec/specs/claim-card/spec.md` — read. Seal, chips, and row text stay here. The card does not grow an image.
- `src/claimledger/eval/measure.py` — read. Still `retrieve`, then `understand`, then `query(Ledger.seed())`. Do not make `measure` crop.
- `src/claimledger/openwebui/reply.py`, `text.py`, `app.py`, and `openspec/specs/openwebui-host/spec.md` — the completion is the card string. A spec delta has to retire only the "crop MUST wait" sentence. Card text stays first in the same completion.
- `src/claimledger/http/` and `openspec/specs/http-query/spec.md` — read. Do not add the crop, `bbox`, or any extra field to `POST /claims/query`.
- `tests/test_identity.py` — read. The 13-path tuple stays. Crop code and crop tests stay off it.
- `pyproject.toml` — `dependencies` stays `[]`. No new extra for a viewer. Pillow is already how Docling exposes `page.image.pil_image` inside the docling extra. Do not pin a second PDF stack.
- `manual/ui.py` — read. It prints phase-6 JSON. It is not the crop surface.

### Approaches

1. **Crop the stored bbox on a sidecar page raster, and append that PNG after the card** — A function outside the kernel and outside `src/claimledger/http/` cuts a caller-supplied raster with the bbox extract already stored. Tests feed synthetic pixels (a known width, height, and a colored rectangle). They do not import `docling`, open a PDF, use the network, or start Docker. The Y axis of the stored tuple is the bottom-origin fraction `_normalize_bbox` writes (`y0 = min(b, t) / height`). The cut flips that axis onto a top-origin image: image top `= 1 - y1`, image bottom `= 1 - y0`. X is unchanged. No padding is added. At conversion, while the Docling document is still in memory, page rasters are written under the artifact directory and outside `canonical_json_bytes`, so the artifact hash does not move. The host still calls `measure` then `render_card`. `card_text` is unchanged and comes first. For each verified claim, the crop is attached only when extract's evidence for that same `identity_key` and the same `value` has a bbox and the sidecar page exists. Abstain stays the card alone. The bytes go in the same assistant completion (markdown image). Open WebUI draws that image. `POST /claims/query` is untouched.
   - Pros: Uses the bbox Docling's provenance already became. The kernel still picks the claim. A mismatch of value yields no picture, so the photo cannot swap `21262335` and `21259769`. Pytest proves the rectangle without a PDF. The hash stays the hash of the JSON. No second product route. No viewer.
   - Cons: `openspec/specs/openwebui-host/spec.md` currently says the completion is exactly the card and that the crop waits. This change needs a spec delta that keeps the card text first and allows only this picture after it. Cell-first evidence means the picture is the value cell whenever the cell has a bbox (the extract fixture always does); the table `prov` box is only the fallback. A live photo needs both the existing artifact hash and the new sidecar. The pin's `export_to_dict` image behavior has to be checked so pixels never join the hashed bytes.
   - Effort: Medium

2. **Put the crop on `POST /claims/query`** — Add an image, or `bbox`, to the evidence JSON. Rector §13 says evidence later gains the crop, and the small contract did not expect it on day one.
   - Pros: One response would carry the claim and the picture.
   - Cons: `openspec/specs/http-query/spec.md` forbids `bbox` and the extra identity fields, and it fixes seed evidence at `[]`. The seed claim has no box. Stuffing a picture into that body edits an archived contract and still does not create pixels. The host already sits outside that package and already has the card.
   - Effort: Medium — **reject**

3. **Another platform's viewer** — Open WebUI's PDF or citation viewer, a RAGFlow-style viewer, pdf.js, or a MinerU bbox sidecar, pointed at the source file.
   - Pros: The page would be on screen quickly.
   - Cons: Rector §20, the north star, and the stack doc forbid that. It is not our crop of the marked zone. MinerU stays out. The manifest does not even keep the PDF path.
   - Effort: Medium — **reject**

4. **Re-open the PDF at question time with a second rasterizer** — Find the file again and render the page outside Docling.
   - Pros: Avoids storing PNGs.
   - Cons: Rector says a claim is rebuilt by reading the artifact, not by parsing the PDF again. A second rasterizer can disagree with the box Docling marked. The PDF path is not in the manifest. Kernel and host tests must not open a PDF.
   - Effort: Medium — **reject**

5. **Let `render_card` or an LLM/VLM emit the picture** — The card grows an image field, or a model looks at the page and describes the zone.
   - Pros: The picture would sit in the same object as the seal.
   - Cons: The card spec is seal, chips, and row text, and it must not parse digits. Phase 10 is the VLM, and only when standard parse fails gold. A model must not choose the neighbor. Padding or a nicer frame exists only because it looks nice.
   - Effort: Medium — **reject**

6. **Crop the table `prov` box instead of `FinancialEvidence.bbox`** — Always photograph the whole income-statement table so both neighbor labels are visible.
   - Pros: A value cell is a thin strip. The table zone shows the row label.
   - Cons: Extract already chose the rectangle: cell bbox, else table `prov`. A second rectangle is a new mark. The card already prints both row texts. The photo is proof of the box stored on that claim, not a second layout.
   - Effort: Low — **reject**

### Recommendation

Take approach **1**. The user opened the phase 8 gate. The crop is the picture of `FinancialEvidence.bbox` (cell, else table `prov`), flipped from the bottom-origin fractions extract stores onto a top-origin page raster. No padding. No second box. No viewer.

Page PNGs are a sidecar written at conversion from the Docling page image, outside `canonical_json_bytes`. Confirm against pin `docling==2.130.0` that `export_to_dict()` does not absorb those pixels; if it would, strip them before the hash. Do not trust the current website default for `generate_page_images` as the pin's default.

The host keeps `measure` then `render_card`. `card_text` stays the card. The picture follows in the same completion only for a verified claim whose extract evidence matches that `identity_key` and that `value`, and whose sidecar page exists. Abstain has no picture. Compare may show one picture per verified claim, in claim order, and still must not compute a delta. `POST /claims/query` does not gain fields. `render_card` does not gain an image. `dependencies` stays `[]`. The 13-path allowlist stays. Crop tests use synthetic pixels.

**In this change:** the rectangle cut, the sidecar page raster that does not change the artifact hash, the host completion that places that picture after the unchanged card text, and in-process tests with synthetic pixels.

**Waits:** phase 9 period pack / subtraction, phase 10 VLM, phase 11 Neo4j, phase 12 charts, phase 13 orchestrator. Also still out: Pipelines, Knowledge RAG, MinerU, a third-party PDF viewer, any extra field on `POST /claims/query`, and any edit that lets an LLM choose `21262335` or `21259769`.

### Risks

- **Bottom-origin bbox on a top-origin image.** `_normalize_bbox` ignores `coord_origin` and stores `b`/`t` over page height. Treating `y0` as the top of the image photographs the wrong band. The cut flips Y. The stored tuple stays as it is.
- **Cell-thin picture.** When the cell has a bbox, evidence stores that cell, not the table `prov` box. The photo can be only the amount. That is the stored mark. Do not pad it to make it nicer. Both row texts remain on the card.
- **Seed evidence is empty.** `query(Ledger.seed())` does not carry the box. Resolving the picture from HTTP JSON, or from `Candidate`, invents a source. Match extract evidence on `identity_key` and `value`. A value mismatch yields no image.
- **Hash drift.** Embedding page images in the JSON that `canonical_json_bytes` hashes changes `artifact_hash` and breaks anything pinned to today's digest. The sidecar stays outside those bytes. Check the pin. Do not relax gold.
- **Archived host wording.** "Exactly that card" and "crop MUST wait" are the current spec. Shipping the picture without a delta contradicts the archive. The delta allows the picture after the card text and retires only the crop wait.
- **Second claims route or a fatter JSON.** Mounting the crop on `src/claimledger/http/` or adding `bbox` or an image field breaks `http-query`.
- **Kernel scan, Docling, PDF, Docker.** Putting the crop on `_kernel_scan_paths`, or opening a PDF from a kernel or host test, breaks the allowlist and the kernel rule. Synthetic pixels only.
- **Missing sidecar.** No page file means the card alone. Do not invent a rectangle or re-render with another library.
- **Open WebUI image markdown.** The completion has to stay one assistant message. If a data URI is stripped, a file URL still has to be our PNG, served without a new claims route and without their viewer. Confirm that on the pinned `v0.11.4-slim` screen. Do not change the image pin.
- **400-line review budget.** Rectangle, sidecar, host delta, and tests can approach the budget. `sdd-tasks` still forecasts it.

### Ready for Proposal

Yes. Nothing found here stops `sdd-propose`. The orchestrator should tell the user that phase 8 crops the bbox already stored on `FinancialEvidence`, from a page raster saved beside the hashed JSON, and that Open WebUI draws that picture after the existing card. The kernel still chooses the number. `POST /claims/query` stays unchanged. Phases 9–13 stay waiting. Do not start `sdd-propose` inside this phase. Do not commit.

Sources:
- [Export figures](https://docling-project.github.io/docling/_generated/examples/export_figures)
- [Pipeline options](https://docling-project.github.io/docling/reference/pipeline_options)
