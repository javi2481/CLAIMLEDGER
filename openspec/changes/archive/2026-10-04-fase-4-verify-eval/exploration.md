## Exploration: fase-4-verify-eval

Architecture is CLOSED. Phases 4 and 5 are this one change: put tables-drawer candidates in front of the existing Claim Query, then measure the neighbor trap, gold v1 45 and v2 26, and abstention. Gold numbers stay frozen, including `21262335` vs `21259769`. HTTP (`fase-6-http`) and the Open WebUI ficha (`fase-7-ficha`) stay out.

### Current State

Wave A and fases 1–3 are archived. Nothing in `src/` calls `retrieve` except `src/claimledger/retrieval/drawers.py`. Nothing in retrieval calls `query` or `Ledger.upsert`.

A question becomes an identity only in `understand` (`src/claimledger/lookup.py`). It folds the Spanish text and applies a closed phrase order. Issuer is always `BYMA`. The order is: YPF price → `off_corpus`; memoria, comunicado, deck, or contrato plus a P&L cue → `recipe_no_extract`; narrative cues without a net-income ask → route `narrative`; otherwise scope, metric, period, and compare. There is no LLM and no read of a table node. `query` (`src/claimledger/query.py`) then builds `identity_key` from that `Intent` and reads `Ledger`. It returns `verified` or `abstained`. It accepts only `ledger_status="recorded"`. It does not take candidates, does not rank text, and does not mutate the book. Compare already returns two claims and has no delta. `Ledger.seed()` still owns the fourteen kernel rows, with empty `evidence`.

The neighbor trap is already proved on that seeded book, without retrieval:

- `tests/test_query.py` verifies consolidated `21262335` and parent `21259769` as two keys. The unused row stays in the book.
- `tests/test_gold_v1.py` runs the 45 cases as `query(understand(question), Ledger.seed())`. Neighbor cases require the frozen value and reject the other numbers. Narrative `na-*` stays `"skip": true`.
- `tests/test_gold_v2.py` runs all 26 the same way, including tax `-14950948`.
- Ingest already stored the page-4 rows as two claims (scope/metric), not a tie. That is fase 1. Recorded is not verified.

Retrieval (`retrieve(artifact_hash, drawer, question)`) returns `Candidate(drawer, text, ref)` from one named drawer. `question` does not drop a row: the same tables call returns both neighbor texts for a consolidated ask, a parent ask, and an empty string (`tests/retrieval/test_drawers.py`). Both rows in that fixture share `ref` `#/tables/1`, so ref cannot separate them. Candidates are not `FinancialClaim`, not `verified` or `abstained`, and the drawer tests count `query` and `upsert` at zero. The reader forces `DoclingReader(export_type="json")`. Pins already present: `docling==2.130.0`, `docling-graph==1.9.1`, `llama-index-readers-docling==0.5.0`, `llama-index-node-parser-docling==0.5.0`.

The 13-path kernel scan is an explicit tuple in `tests/test_identity.py` (seven modules plus six kernel tests). `retrieval/` is outside it. Kernel tests must not import `docling` or `llama_index`. Importing the seven kernel modules must not load `llama_index`.

What the code cannot do yet: one measured path that shows both table candidates and then the same query choosing the requested identity. `query` still never sees a candidate. Gold never calls `retrieve`.

### Affected Areas

- `src/claimledger/query.py` — read. Stays the judge: `Intent` + `Ledger` → `verified` | `abstained`. Do not import retrieval here. Do not accept a ranker.
- `src/claimledger/lookup.py` — read. `understand` stays the identity resolver. Do not derive scope or metric from candidate text.
- `src/claimledger/ledger.py` — read. `Ledger.seed()` stays the kernel book. This change must not upsert from a candidate.
- `src/claimledger/retrieval/drawers.py` and `read.py` — read. `retrieve` stays one drawer, candidates only, and must still not call `query`.
- `tests/test_query.py`, `tests/test_gold_v1.py`, `tests/test_gold_v2.py` — read. They already measure the trap, 45, 26, and abstention on seed. Do not point them at retrieval or relax numbers.
- `tests/retrieval/test_drawers.py` — read. Keeps the seal that retrieval does not choose, verify, or write.
- `openspec/specs/json-retrieval/spec.md` — candidates only; choosing is not this capability. A later delta may say a caller may place those candidates in front of `query`. Do not weaken the seal inside `retrieve`.
- `openspec/specs/query/spec.md` and `openspec/specs/gold-regression/spec.md` — neighbor, compare-without-delta, `recipe_no_extract`, frozen numbers, 13-path scan. Deltas must preserve those scenarios.
- New measured caller and tests, outside the 13 paths (a sibling package such as `src/claimledger/eval/`, with tests outside `tests/test_*.py`). Not one of the seven kernel modules. Not a new file under `ingest/`.

### Approaches

1. **Sibling measured caller in front of the same query** — A new module outside the seven kernel files calls `retrieve(artifact_hash, "tables", question)`, then `understand(question)`, then `query(intent, Ledger.seed())`. `retrieve` and `query` keep their current signatures. The caller does not upsert and does not mark a candidate verified. Measurement, not a new ranker: both neighbor texts are in the tables candidates; the verified value is the frozen number for the asked identity (`21262335` consolidated, `21259769` parent); the other row was a candidate and is not the answer. If `understand` abstains (`recipe_no_extract`, `off_corpus`, `unresolved_identity`), `query` still abstains and a candidate that contains `21262335` must not become the answer. Gold 45 and 26 stay on `query(understand, Ledger.seed())` in the existing harness. The new tests sit off the 13-path scan and may follow the drawer-test pattern of a stubbed reader (no PDF, no network). Narrative stays a separate drawer and is not a number source. Compare stays two claims, no subtraction.
   - Pros: matches rector §12 (candidates, then identity, then the kernel), §14 (product metric is the proved claim), and §23 (the trap lives in Query; two recorded claims). Keeps `retrieve` from calling `query`. Keeps `llama_index` off the kernel snapshot. Uses code that already exists. Same `ref` on both rows does not matter, because Query selects by identity and the measure reads row text.
   - Cons: `query` itself still does not take a candidate argument. The join is the caller. Seeded claims have empty evidence, so the join cannot be `candidate.ref` → `FinancialEvidence`. Coverage is “both row texts present,” which is what `retrieve` returns today; there is no rank, so Recall@k / MRR are not a new index.
   - Effort: Medium

2. **Optional candidates argument on `query`** — Change `query(intent, ledger, candidates=...)` so the scanned kernel module sees the rows.
   - Pros: the judge function literally receives the rows.
   - Cons: `query.py` is one of the seven scanned modules. Importing retrieval there couples the kernel to the reader package. Gold and `test_query.py` call `query(intent, ledger)` with no artifact; a required candidate list would force JSON into kernel tests or a second code path that is approach 1 inside the kernel file. Seed evidence is empty, so the kernel still decides by identity, and the extra argument does not choose the row. Drawer tests monkeypatch `query` and expect zero calls from `retrieve`; folding the caller into `query.py` does not fix that and risks the snapshot.
   - Effort: Medium — **reject** (does not choose better than approach 1, and it puts retrieval on the kernel side of the scan)

3. **Let `retrieve` choose, or let an LLM / Markdown / a ledger write choose** — Filter rows inside `retrieve` by the question, mark the winner `verified`, parse candidate text into a `FinancialClaim` and upsert, or skip `understand` / `query`.
   - Pros: fewer calls.
   - Cons: `test_question_does_not_choose_between_neighbor_rows` and `openspec/specs/json-retrieval/spec.md` forbid choice inside retrieval. An LLM-written identity and Markdown-as-truth are closed out. Upsert from a candidate makes recorded look like verified and duplicates `extract_recipe`. Skipping the kernel is forbidden. Both fixture rows share `#/tables/1`, so a ref tie-break cannot pick the row either.
   - Effort: High — **reject**

### Recommendation

Take approach **1**.

1. New measured caller lives outside the seven kernel modules and outside `retrieve`. It does not join the 13-path tuple. `src/claimledger/__init__.py` stays empty.
2. Call order for a number question: tables candidates from `retrieve` (question still does not drop a row), identity from `understand` (not from candidate text), verdict from `query(intent, Ledger.seed())`. One drawer per call. Do not merge the narrative drawer into the number path.
3. The measure asserts candidate coverage and the kernel verdict together. Both neighbor texts are present. Consolidated verifies `21262335`. Parent verifies `21259769`. The other number is not the verified claim. `ledger_status` on the seed stays `recorded`.
4. Gold v1 45 and v2 26 stay the existing seed harness, same frozen strings, including `21262335`, `21259769`, and `-14950948`. This change runs that harness unchanged. It does not re-encode those numbers from Markdown or from an LLM.
5. Abstention stays closed. `recipe_no_extract` (memoria, comunicado, deck, contrato) still abstains even when a tables candidate contains a gold number. Narrative `na-*` stays skip. Compare stays two claims and does not subtract.
6. `retrieve` remains candidates only. Pins stay the versions already in `pyproject.toml`. No new library.

**In this change:** the caller above; a pytest demonstration that both rows were retrieved and Query picked the asked identity; gold 45+26 and abstention still green on `Ledger.seed()`.

**Waits for fase 6:** `POST /claims/query`, any HTTP body, and a server. **Waits for fase 7:** the Open WebUI ficha, seal, and chips. Also out: orchestrator, VLM, MinerU, Neo4j, subtraction (fase 9), relaxing gold, an agent that skips the kernel.

### Risks

- **Same ref on both rows.** The drawer fixture gives both neighbors `#/tables/1`. Selecting by ref ties them. The measure must use row text plus Query’s identity, not ref, and must not upsert a claim to break the tie.
- **Empty seed evidence.** `Ledger.seed()` stores `evidence=()`. A join from `candidate.ref` to evidence cannot prove the kernel trap. Keep seed for the numbers; use candidate text only as the retrieval observation.
- **Retrieval mistaken for the judge.** If the new caller, or a change inside `retrieve`, sets `verified` or calls `upsert`, fase 3’s seal breaks and recorded becomes verified.
- **Abstention overridden by a nearby number.** A comunicado question must stay `recipe_no_extract` even if the tables drawer contains `21.262.335`.
- **Kernel scan.** A new `src/claimledger/*.py` module must not be added to `KERNEL_MODULES` or the 13-path tuple, and kernel tests must not import it if that import loads `llama_index`. Prefer a subpackage and a stubbed reader in the new tests, same as `tests/retrieval/test_drawers.py`.
- **Gold rewritten through retrieval.** Pointing `test_gold_v1.py` / `test_gold_v2.py` at Docling JSON would pull `llama_index` into the scanned tests and would relax the seed contract. Leave those files on `Ledger.seed()`.
- **Ranking scope.** Rector §14 names Recall@k and MRR. `retrieve` returns every node in the named drawer and does not score. This change measures coverage of the two rows plus the proved claim. Do not add a ranker or a new library to invent MRR.
- **400-line review budget.** One caller plus focused tests should stay small. `sdd-tasks` should forecast it. Not a reason to fold the caller into `query.py`.

### Ready for Proposal

Yes. Placement, the call order, and the measure (candidates in front, same query, frozen gold, abstention unchanged) are resolved. Orchestrator should run `sdd-propose` for `fase-4-verify-eval` and should not write product code, specs, design, or tasks in this phase. Do not start fase 6. Do not commit.
