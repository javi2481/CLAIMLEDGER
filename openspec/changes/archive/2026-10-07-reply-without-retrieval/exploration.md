## Exploration: reply-without-retrieval

### Current State

Open WebUI `reply` still builds card rows by calling DoclingReader retrieval, and the product image installs that stack.

`reply` (`src/claimledger/openwebui/reply.py`) loads `recorded_book()`, then `execute` / `ask`. On the plan/book path it calls `retrieve(artifact_hash, "tables", question)` and uses `series.result`. On the measure path it calls `measure()`, which itself calls `retrieve` before `understand` and `query` (`src/claimledger/eval/measure.py`). `render_card` copies `Candidate.text` into rows and emits the consolidated/parent sentence only when there is exactly one verified claim and `len(rows) == 2` (`src/claimledger/card/card.py`).

`Candidate` is a frozen dataclass (`drawer`, `text`, `ref`) in `src/claimledger/retrieval/drawers.py`. `retrieve` lazy-calls `read_hashed_json`, which constructs `DoclingReader(export_type="json")` and `DoclingNodeParser` (`src/claimledger/retrieval/read.py`). LlamaIndex is not imported at module import time.

`card.py` imports `Candidate` from retrieval. `src/claimledger/agent/tools.py` `search` calls `retrieve`. `src/claimledger/agent/loop.py` dispatches the search tool. `verify` does not call `retrieve`.

`Dockerfile` runs `pip install ".[http,retrieval]"`. The `retrieval` extra is `llama-index-readers-docling==0.5.0` and `llama-index-node-parser-docling==0.5.0`. The `deepseek` extra is `httpx` and is imported only inside the DeepSeek client. CI job 1 runs `tests/eval` with `dev`+`http` only (retrieval tests monkeypatch `read_hashed_json`). CI job 2 installs `retrieval` and runs `tests/retrieval` and `tests/openwebui`.

`Ledger.seed()` stores `evidence=()`. Product `recorded_book()` evidence comes from `extract_recipe`: one `FinancialEvidence` per recipe row, `label` = row label, `text` = cell amount. Gold numbers stay on `Ledger.seed()`. `openspec/specs/docling-ingest/spec.md` still says reply / DoclingReader / Docker `.[retrieval]` are out of scope. `openspec/specs/verify-eval/spec.md` still requires `measure` to call `retrieve` then `understand` then `query`, and to keep both neighbor row texts. `openspec/specs/json-retrieval/spec.md` still requires the hashed-JSON reader and two drawers.

Open WebUI tests in `tests/openwebui/test_host.py` monkeypatch `read_hashed_json` and assert both neighbor strings on the verified consolidated card, the verified parent card, the abstain card, and the compare card. Abstain today still prints those retrieval rows and does not print a verified value.

### Affected Areas

- `src/claimledger/openwebui/reply.py` — plan/book path calls `retrieve`; measure path inherits it
- `src/claimledger/eval/measure.py` — `retrieve` then `understand` then `query`; verify-eval spec
- `src/claimledger/card/card.py` — imports `Candidate` from retrieval; rows and two-row sentence
- `src/claimledger/retrieval/drawers.py` — `Candidate` and `retrieve`
- `src/claimledger/retrieval/read.py` — only `DoclingReader` / `DoclingNodeParser` call site
- `src/claimledger/agent/tools.py` and `src/claimledger/agent/loop.py` — `search` still calls `retrieve`
- `Dockerfile` — `.[http,retrieval]`
- `pyproject.toml` — keep the `retrieval` extra for optional offline RAG; product install drops it
- `tests/openwebui/test_host.py` — fake reader and neighbor-row assertions
- `tests/eval/test_measure.py` — spies `retrieve` and asserts both neighbor candidates
- `tests/card/test_render_card.py` — constructs `Candidate`
- `tests/agent/test_tools.py` — monkeypatches `tools.retrieve`
- `tests/retrieval/test_read.py`, `tests/retrieval/test_drawers.py` — stay with the optional package
- `.github/workflows/pytest.yml` — eval job has no retrieval extra; openwebui job installs it
- `openspec/specs/verify-eval/spec.md`, `openspec/specs/claim-card/spec.md`, `openspec/specs/json-retrieval/spec.md`, `openspec/specs/docling-ingest/spec.md` — deltas, not gold

### Approaches

1. **Evidence rows, Candidate under card, retrieval extra off the image** — Move `Candidate` to `claimledger/card/` (module `card/candidate.py`). `card`, `reply`, and `measure` import it there. `retrieval/drawers.py` may re-export it so optional RAG tests keep a stable import. Replace `retrieve()` in `measure` and both `reply` branches with candidates built from verified claim evidence (`label` / `text`); abstain yields `()`. Keep `retrieval/` and its tests for offline RAG. Dockerfile installs `.[http,deepseek]` when the host client is in the image, otherwise `.[http]`.
   - Pros: Product process no longer calls DoclingReader. Image no longer installs llama-index-docling. Card stays a pure display of `Candidate.text`. Gold and kernel import bans stay put. Retrieval spec can remain for the optional package.
   - Cons: One verified claim does not naturally yield two row strings. Abstain and compare cards lose the neighbor lines the host tests assert today. `measure` call order in verify-eval must change. Agent `search` still reaches DoclingReader unless called out.
   - Effort: Medium

2. **Delete `retrieval/` from the repo** — Remove drawers, reader, extra, and retrieval tests so no DoclingReader remains in tree or image.
   - Pros: No leftover import edge.
   - Cons: Throws away the optional offline RAG the rector still names (`DoclingReader(export_type="json")`). Larger spec deletion. Agent search has nowhere to go. Out of scope for this change.
   - Effort: High

3. **Stub `retrieve` to return `()` and leave `Candidate` in retrieval** — Reply and measure stop using Docling JSON but still import the retrieval package.
   - Pros: Small diff. Abstain rows disappear immediately.
   - Cons: Card and reply still depend on the retrieval package. Dockerfile drop is incomplete relative to the import goal. Two-row sentence never fires. Does not meet “card/reply/measure do not import retrieval”.
   - Effort: Low

### Recommendation

Approach 1. The pinned stack cannot turn a verified `FinancialClaim` into card rows without DoclingReader, and DoclingReader is what the product image must stop installing. The gap to name: card rows are display text, not a second retrieval index. Build them from evidence already on the verified claim. Keep `retrieval/` as optional offline RAG, uninstalled in the product image.

`retrieval/drawers.py` should import `Candidate` from `card/candidate.py`, not the reverse, so card never imports retrieval. Do not add a new library. `dependencies` stays `[]`.

Strict TDD: failing tests first for the moved type, evidence-built rows, empty abstain rows, and a Dockerfile/install assertion that the product extra list has no `retrieval`. Gold expected numbers stay frozen.

### Risks

- Two-row sentence versus one evidence item. `Ledger.seed()` has `evidence=()`. `extract_recipe` stores one cell per claim (`label` plus amount `text`), not the concatenated neighbor strings (`RESULTADO NETO DEL PERÍODO 21.262.335` then the parent line). `_sentence` runs only when `len(rows) == 2` and `len(claims) == 1`. A sibling-row rule (which text, which order) is unspecified. Host tests and `claim-card` still require both texts for verified consolidated and parent.
- Abstain and compare currently print retrieval neighbor rows. Recommended `else ()` clears abstain rows. Compare (`execute` / `ask`) today also calls `retrieve` and the host compare card still expects those two lines above `21262335` and `81956525`. Claim-card allows empty candidates on abstain; it still requires both neighbor texts on the verified single-claim cards.
- `measure` is specified to call `retrieve(artifact_hash, "tables", question)` then `understand` then `query`, and not to drop a row (`openspec/specs/verify-eval/spec.md`, `tests/eval/test_measure.py`). Replacing `retrieve` is a verify-eval delta. `retrieve` must still not call `query` inside the optional package.
- Agent `search` (`tools.py`, `loop.py`) still calls `retrieve`. Reply imports the agent loop, so the product process still has a retrieval edge. Without the extra, a model tool call raises `ImportError` inside `read_hashed_json` (llama imports are lazy, so process start can succeed). Proposal must say whether product search stays optional, fails closed, or stops calling DoclingReader.
- CI and import direction. `tests/eval` runs without the retrieval extra; after this change those tests must not need a monkeypatched reader. Open WebUI tests that install `_install_parsed_reader` must assert evidence rows or empty rows. Moving `Candidate` into card must not create an import cycle and must not pull `llama_index` into card or kernel scans. `docling-ingest` “reply out of scope” becomes false and needs a delta. Gold numbers and the 13-path kernel allowlist stay unchanged.

### Ready for Proposal

Yes. Tell the user: proposal should lock Approach 1, name the evidence-to-two-row rule before spec (sibling text and order, or an explicit sentence-behavior change), state the agent `search` fate, and schedule spec deltas for verify-eval, claim-card, and docling-ingest. Retrieval package and `json-retrieval` stay for optional offline RAG. Next phase is `sdd-propose`.
