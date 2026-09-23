## Exploration: Fase 0 deterministic Financial Claims kernel

Architecture is CLOSED. This change implements only the Fase 0 kernel
contract (`docs/fase-0.md`) against `docs/documento-rector.md` §15, §16,
§23–§25 and `docs/north-star.md`. No new layers, agents, or stack.

### Current State

CLAIMLEDGER is docs-only. Inspected, not guessed:

- No `.git`, no `src/`, no `tests/`, no `pyproject.toml`, no CI, no pytest.
- OpenSpec exists as `openspec/config.yaml` only (`strict_tdd: true`,
  persistence hybrid). No `openspec/specs/` content and no prior change
  folder.
- `.codegraph/` is absent. `gentle-ai codegraph init` fails with git
  exit 128 (root is not a recognized git project). Structural analysis
  therefore used rector + Fase 0 + the frozen Claimprint neighbor
  (`C:\Users\Equipo\Claimprint`), not CodeGraph.
- Product code does not exist. The first SDD change *is* the kernel.

Closed product facts that this change must not reopen:

- Two planes: Truth/Data (deterministic ingest) vs Agent/Interaction.
- Kernel: identity / verify / abstain. No LLM stage for identity.
- `identity_key = issuer|period|statement|scope|metric`. Value is a
  component, not identity.
- Status vocabulary is closed: pipeline `candidate`; ledger
  `recorded` | `conflicted`; query `verified` | `rejected` (store-side
  neighbor not chosen) | `abstained`. `recorded` ≠ `verified`.
- Fase 0 has no Docling, Evidence Adapter, Graph, LlamaIndex, Docker,
  Open WebUI, VLM, HTTP API, or press/presentation gold.
- Pins (`docling==2.130.0`, `docling-graph==1.9.1`) are declared
  metadata only. Kernel tests MUST NOT import docling.
- Python floor for this change: `>=3.11` (Fase 0). Rector §16 still
  states the ecosystem floor `>=3.10` for later Docling work.
- Canonical neighbor: `BYMA|2026-03-31|income_statement|consolidated|net_income = 21262335`
  vs `...|parent_attributable|net_income = 21259769`.
- Gold `identity_v1` (45) + `identity_v2` (26) are frozen numeric
  contracts. Rewrite IDs via the alias table only.

Claimprint neighbor (read, do not copy the repo):

- `Claim` is a frozen dataclass with `validate_claim`.
- Lookup is lexical (`understand` → `Intent` → `lookup`). No embeddings.
- `schemas/store.py` is a **disk JSON extract cache**, not a ledger.
  Do not port it. Fase 0 upsert (`same id+value` → append evidence;
  `same id+other value` → `conflicted`) is new.
- `schemas/money.py` (`digits_ars`, `signed_ars`) ports as-is.
- Press / presentation identity routes stay out of Fase 0.

Rector §7 still shows `verification_status` on `FinancialClaim`.
Fase 0 supersedes that field for implementation: the claim stores
`ledger_status` (`recorded` | `conflicted`); query returns
`verified` | `abstained` and does not mutate the book.

### Affected Areas

All of these are **to be created** (nothing to edit):

- `pyproject.toml` — package `claimledger`, Python `>=3.11`, pytest;
  pins declared, not imported by kernel tests.
- `src/claimledger/identity.py` — 5-field `identity_key`, alias table,
  period normalize (`1T26` → `2026-03-31`).
- `src/claimledger/digits.py` — `digits_ars` / `signed_ars`.
- `src/claimledger/evidence.py` — `FinancialEvidence` (hash/bbox may
  be empty in Fase 0).
- `src/claimledger/claim.py` — `FinancialClaim` + consistency checks.
- `src/claimledger/ledger.py` — in-memory upsert.
- `src/claimledger/lookup.py` — question → `Intent` (Claimprint thesis,
  Fase 0 order only).
- `src/claimledger/query.py` — `Intent` + ledger → `verified` |
  `abstain`. Compare returns two claims; does not subtract (Fase 9).
- `evals/identity_v1.json`, `evals/identity_v2.json`, `evals/aliases.json`
  — ported gold; numbers intact; IDs rewritten; narrative `skip: true`.
- `tests/test_identity.py`, `test_ledger.py`, `test_lookup.py`,
  `test_query.py`, `test_gold_v1.py`, `test_gold_v2.py` — in-memory;
  no network, no PDF, no docling import.

Out of scope (closed later phases): Evidence Adapter, Graph, retrieval,
HTTP API, UI, orchestrator, VLM, Neo4j, crop, charts, `press_v1`,
`presentation_v1`.

### Approaches

Compare **only** implementation details Fase 0 left open. Do not
compare architectures.

1. **Thin in-memory `Ledger` over `dict[identity_key, FinancialClaim]`**
   — one class in `ledger.py` with `upsert` / `get` / seed-friendly
   iteration. Tests construct a fresh instance and upsert the 14 recipe
   rows.
   - Pros: matches the named `ledger.py` module; no global state;
     upsert and conflict rules stay in one place; two test ledgers
     are cheap; later persistence can wrap the same API without
     inventing a repository layer now.
   - Cons: still a small class to write; dict lookup is enough for
     14 rows (acceptable).
   - Effort: Low

2. **Bare module-level dict + functions**
   — `ledger.py` exposes `upsert(store, claim)` on a caller-owned
   `dict`, or a process-global map.
   - Pros: fewest types.
   - Cons: global reset in tests; easy to leak state across gold
     cases; weaker home for `conflicted` evidence append; drifts from
     “ledger is a book” language in §23.
   - Effort: Low

3. **Repository / Protocol / ABC store**
   — abstract `ClaimStore` plus in-memory impl “for later Neo4j”.
   - Pros: none in Fase 0.
   - Cons: invents a layer the rector forbids until the Architecture
     Gate; extra files not in the skeleton; delays TDD.
   - Effort: Medium — **reject**

4. **Exact 7-module skeleton vs collapse vs extra files**
   - **Exact skeleton** (`identity`, `digits`, `evidence`, `claim`,
     `ledger`, `lookup`, `query`): maps 1:1 to the Fase 0 commit
     order and test files. Keep `Intent` inside `lookup.py` and
     `QueryResult` inside `query.py`. **Recommend.** Effort: Low
   - **Collapse** (e.g. `models.py` + `kernel.py`): fights the
     commit order (one step at a time) and mixes period/digits
     with upsert/lookup. Effort: Low, but higher review risk.
   - **Extra files** (`intent.py`, `status.py`, `seed.py`, adapters):
     invents structure. Effort: Medium — **reject**

5. **Model style (form left open: “forma, no código final”)**
   - **Frozen dataclasses + `validate_*` (stdlib)**: same pattern as
     Claimprint `Claim` / `validate_claim`; no extra dep; identity
     consistency fails at construct time. **Recommend.** Effort: Low
   - **Pydantic**: not a Fase 0 dependency (pytest only). Effort: Low
     plus a new pin — **reject for this change**
   - **Bare dicts**: cannot enforce `identity_key` vs five fields.
     Effort: Low — **reject**

### Recommendation

Take the **smallest TDD-first path**:

1. Follow the Fase 0 repo skeleton and **8-commit order** exactly.
2. Represent the book as a **thin `Ledger` class wrapping
   `dict[str, FinancialClaim]`**. No disk store, no Protocol, no
   Claimprint `store.py`.
3. Use **frozen dataclasses** and explicit validators. Put `Intent`
   in `lookup.py` and the query DTO in `query.py`.
4. Seed gold tests from the 14 recipe rows (plus the explicit
   “prior `22362983` is not current net_income” rule). Do not parse.
5. Port lookup **thesis and phrase order** from Claimprint; drop
   press/deck identity. Comparison returns two verified claims.
6. Declare pins in `pyproject.toml`; never import them in Fase 0 tests.

RED-GREEN-REFACTOR per commit: failing test first, then the matching
module. Stop if a test wants Docling — that test is out of phase.

Do not treat rector §7 `verification_status` as the claim field.
Do not init git or CodeGraph as part of this product change
(orchestrator / later delivery may do that separately).

### Risks

- **Recorded vs verified confusion.** Implementers may stamp
  `verified` on ingest. Query must not mutate the ledger.
- **Porting Claimprint `store.py` or extract.** That cache is PDF/
  MinerU-era. Fase 0 is an in-memory upsert book.
- **Press/deck lookup leakage.** Claimprint `lookup.py` still has
  those routes; Fase 0 must omit them (`recipe_no_extract` only).
- **Gold rewrite mistakes.** IDs change via `aliases.json`; numeric
  expected values (`21262335`, `81956525`, `-14950948`, …) stay
  frozen. Narrative cases stay `skip: true`.
- **Comparison overreach.** Fase 0 returns two claims; subtraction
  is Fase 9.
- **Pin import creep.** Declaring `docling` in `pyproject.toml` must
  not pull it into kernel tests.
- **Python floor mismatch.** Implement `>=3.11` now; do not reopen
  the rector §16 `>=3.10` ecosystem note as a product decision.
- **No git.** CodeGraph and later PR slices need a repo; that is
  delivery setup, not kernel architecture.
- **400-line review budget.** Gold JSON + seven modules + tests will
  likely exceed one PR later; `sdd-tasks` should forecast chained
  slices along the existing 8-commit order. Not a Fase 0 design fork.

### Ready for Proposal

Yes. Architecture is closed and Fase 0 already names models, states,
lookup order, gold rules, skeleton, closure criteria, and commit
order. The only implementation choices left (ledger dict vs extra
split vs model library) are resolved above. Orchestrator should tell
the user: proceed to `sdd-propose` for `fase-0-kernel`; do not start
product code until propose → spec → design → tasks complete.
