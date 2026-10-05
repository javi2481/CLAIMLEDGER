## Exploration: auditoria-stack-nativo

Architecture is CLOSED. This change is a standing function, not a wave step. Wave numbers stay 0 through 13: phase 8 is still the page crop, phase 1A is the corpus close-out. You call this audit when a review is needed. Calling it does not advance the wave and does not block the crop or phase 9.

User rule, 2026-10-05: do not invent a script for something Docling or any other part of the stack solves natively. If there is no native option, write the code and name the gap. This change is how that rule is executed on the code that already exists.

### Call shape

```text
audit(scope) -> runs/<date>/audit.md
```

- Input: `src/claimledger/` (or a smaller scope named at the call) and the pins in `pyproject.toml` and `docker-compose.yml`.
- Output: one verdict row per custom function. `keep` names the gap. `call-native` or `delete` names the pinned API.
- Effect of the call: the verdict file only. Replacing code is a second, explicit step, one function at a time.
- Repeat: a later call writes a new dated run. Previous runs stay. Nothing is renumbered into phase 8.

The call does not add a script. A person, or an agent following this change, reads the call sites and the pinned docs and writes the table.

### Current State

Pins:

| Piece | Pin | Native job already used |
|-------|-----|-------------------------|
| Docling | `2.130.0` | `DocumentConverter`, `export_to_dict`, `export_to_doclang` |
| docling-graph | `1.9.1` | `GraphConverter`, `GraphMerger`, provenance, `JSONExporter` |
| LlamaIndex | readers and node parser `0.5.0` | `DoclingReader(export_type="json")`, `DoclingNodeParser` |
| Starlette | `1.0.0` | The two HTTP apps |
| Open WebUI | image `v0.11.4-slim` | Draws the completion. It does not calculate |

`AGENTS.md` and `openspec/config.yaml` already carry the rule, so new changes are bound before any call of this audit. `fase-1a-corpus-parse` uses `load_or_convert` and does not add a walker. `fase-8-crop` is the crop. This function implements neither.

Candidates a call should open first. These are not verdicts:

- `ingest/extract.py` walks `body`, expands `table_cells` into a grid, and normalizes bboxes. Docling's `TableData.grid` and provenance may already be that data.
- `ingest/classify.py` reads the filename. Docling does not know BYMA pack class.
- `ingest/store.py` hashes canonical JSON and writes the `.dclg` sibling. The export is native. The hash and manifest are the store contract.
- `retrieval/drawers.py` splits nodes by `label == table`. The node parser already emits that label.
- `graph/schema.py` is the pydantic template docling-graph asks for. `graph/link.py` folds filename and period before that template.
- `identity.py`, `digits.py`, `lookup.py`, `query.py`, `ledger.py`, `card/` decide the financial claim. The stack is forbidden from writing that identity. This is the gap the product exists to fill.
- `openwebui/` copies the card into an OpenAI-compatible completion. Open WebUI does not know the seal.

Rector: Docling parses, DocLang interchanges, docling-graph identifies entities, LlamaIndex retrieves, the kernel verifies, Open WebUI draws. A call that replaces the kernel with a library fails the gate.

### Affected Areas

- `src/claimledger/**/*.py` — read when the function is called.
- Pinned library docs for those five pieces — the comparison source. Training memory is not the source.
- `openspec/changes/auditoria-stack-nativo/runs/` — one folder per call.
- `openspec/specs/native-stack` — the policy, merged on archive. The function stays callable after that.
- Out of this planting: running the function, deleting code, corpus convert, crop, gold edits.

### Approaches

1. **A standing change you call, which writes a dated verdict** — The procedure below is the whole function. No wave number. No scanner. A `call-native` row is applied only in a later explicit step.
   - Pros: Can run before phase 8, during phase 9, or on one file. Does not pretend to be the crop. Repeating it does not create phase 8C.
   - Cons: Each call costs a careful read of the pinned docs. Judgment rows need a named gap or a named API.
   - Effort: Medium per call

2. **A linter or script that flags non-stack code** — A tool scans `src/` whenever someone wants the audit.
   - Pros: The call would be a command.
   - Cons: That command would be a script for a review the pinned stack does not do. The rule forbids it.
   - Effort: Medium — **reject**

3. **Number it as phase 8B and run it once** — One audit, then the change is archived as if the wave moved forward.
   - Pros: Fits the folder habit of `fase-N`.
   - Cons: The crop is phase 8. An audit is not a photo of the row, and a one-shot archive makes the next review look like a new product phase.
   - Effort: Low — **reject**

### Recommendation

Take approach **1**. The change is complete as a procedure. Execute it only when a call is asked for. Do not run it as part of planting.

### Out of Scope Confirmation

- Implementing `fase-1a-corpus-parse` or `fase-8-crop` from inside a call.
- New claims, gold edits, a second parser, MinerU, Markdown as source of truth.
- Replacing the kernel with Docling, docling-graph, or an LLM.
