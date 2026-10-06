# Page Crop Specification

## Purpose

Cut the stored extract bbox on a caller raster.

## Requirements

### Requirement: Stored Bbox Cut

The crop MUST sit outside the kernel and outside `src/claimledger/http/`. It MUST cut a caller raster on stored `FinancialEvidence.bbox` (cell bbox, else table `prov`). It MUST NOT pad, add an origin field, or pick a second rectangle. Stored fractions MUST be bottom-origin (`y0 = min(b, t) / height`, `y0 <= y1`). The cut MUST flip Y to a top-origin image: top = `1 - y1`, bottom = `1 - y0`, X unchanged. No bbox, no raster, or zero area MUST yield no picture.

#### Scenario: Y flip and no padding

- GIVEN bbox `x0=0.2`, `y0=0.5`, `x1=0.4`, `y1=0.6`
- WHEN the crop cuts a caller raster
- THEN rows MUST run from `1 - y1` to `1 - y0` and columns from `x0` to `x1`, with no padding

#### Scenario: Stored cell box is the cut

- GIVEN a stored cell bbox
- WHEN the crop runs
- THEN it MUST cut that bbox and MUST NOT use the table `prov` box

#### Scenario: No box yields no picture

- GIVEN no bbox, or a zero-area bbox
- WHEN the crop runs
- THEN it MUST yield no picture

### Requirement: Matching Claim Picture

A picture MUST follow only when extract evidence for that verified claim matches its `identity_key` and its `value`, and the sidecar page exists. Abstain MUST be the card alone. Compare MUST show one picture per verified claim, in claim order, and MUST NOT add a delta. `21262335` and `21259769` MUST NOT change. The kernel MUST still choose the number.

#### Scenario: Key and value match

- GIVEN matching evidence for `21262335` and a sidecar
- WHEN the picture is resolved
- THEN that PNG MUST be attached and `21259769` MUST NOT be pictured for it

#### Scenario: Neighbor value yields no picture

- GIVEN verified `21262335` and extract evidence for that key with another value
- WHEN the picture is resolved
- THEN no picture MUST be attached and `21262335` MUST stay

#### Scenario: Abstain or missing sidecar

- GIVEN an abstain, or a match with no sidecar
- WHEN the picture is resolved
- THEN no picture MUST be attached and the PDF MUST NOT be re-rasterized

#### Scenario: Compare has no delta

- GIVEN two verified claims in order, each with a sidecar
- WHEN pictures are resolved
- THEN one picture per claim MUST follow that order and no delta MUST be computed

### Requirement: Query and Card Stay Picture-Free

`POST /claims/query` MUST gain no fields, including `bbox` and an image. `render_card` MUST NOT gain an image. An LLM or VLM MUST NOT emit the picture. MinerU and another viewer MUST NOT be used.

#### Scenario: Query and card stay plain

- GIVEN `POST /claims/query` and `render_card`
- WHEN each result is read
- THEN the query MUST omit `bbox` and any image, and the card MUST omit an image

### Requirement: Synthetic Tests and Closed Bounds

Crop tests MUST use synthetic pixels. Crop tests and kernel tests MUST NOT import `docling` or use a PDF, network, or Docker. `dependencies` MUST stay `[]`. Crop code and tests MUST stay off the 13-path allowlist. Gold numbers MUST NOT change. Phases 9–13, Pipelines, Knowledge RAG, MinerU, padding, and a question-time re-raster MUST stay out.

#### Scenario: Synthetic cut, allowlist, and gold

- GIVEN a crop test and gold `21262335` and `21259769`
- WHEN the cut runs and the allowlist is read
- THEN pixels MUST be synthetic, with no `docling`, PDF, network, or Docker
- AND those paths MUST stay off the 13 paths, `dependencies` MUST be `[]`, and the gold values MUST stay

#### Scenario: Later work stays out

- GIVEN this change
- WHEN scope is checked
- THEN phases 9–13, MinerU, another viewer, padding, and a question-time re-raster MUST stay out
