# EPIC 93 Phase 2: Pipeline Unification and God Code Elimination

## Source: Epic 93, Section 3.2

### Objective
Eliminate the two-pipe system by completely destroying the "God Code" (`backend_v2/hooks/synthesis.py`). Transfer its synthesis and extraction responsibilities to the declarative `prompt_blocks` pipeline (Pipe A). Introduce `matrix_reducer.py` to prevent LLM token explosion.

### Target Files (Modify)
- `backend_v2/hooks/synthesis.py` (DELETE)
- `backend_v2/services/orchestrator/matrix_reducer.py` (NEW)
- `backend_v2/seed/seed_data.json`

### Context Files (Read-Only)
- `backend_v2/hooks/reporting.py`
- `c:\src\quorum\.agents\rules\01-python-backend.md`

### Architectural Mandates
- **the_no_legacy_mandate**: Obsolete code and ALL fallback chains MUST be ruthlessly deleted.
- **database_schema_hallucination**: Do NOT alter the SSOT root array structures in `seed_data.json`. Add the new nodes to the `prompt_blocks` collection.
- **Epic Phase 0 Prerequisite**: Semantic output must remain unchanged.

### Implementation Details
1.  **Introduce `matrix_reducer.py`:**
    *   Create a DAG node / service that strips heavy metadata from chunk evaluation JSONs, producing a distilled core dataset for the synthesis LLM.
2.  **Destroy `backend_v2/hooks/synthesis.py`:**
    *   Ruthlessly delete the file and all associated regex string-splitting hacks (e.g. `|||`).
3.  **Update `seed_data.json`:**
    *   Inject the synthesis prompts (formerly in `synthesis.py`) natively into the `prompt_blocks` SSOT. Wire them via the `dependencies` array in the `workflows` to run sequentially after `matrix_reducer`.

### Destructive Operation Inventory
- `backend_v2/hooks/synthesis.py`:
  - `TextConsolidationHook`: MAPPED -> `prompt_blocks` in `seed_data.json` and logic to `matrix_reducer.py`.
  - `RegexParser`: INTENTIONALLY DROPPED — Reason: Eradicated by `QuoteEvidenceDTO`.

### Bidirectional Integration Check
- **Producer:** `matrix_reducer.py` distilling data.
- **Consumer:** The LLM Task Executor reading the distilled state for synthesis block execution.

### Testing & Quality Gate Plan
1.  **Unit Tests:** Create `tests/unit/services/orchestrator/test_matrix_reducer.py`.
2.  **Integration Tests:** Verify workflow DAG traversal natively triggers the new synthesis blocks.
3.  **Verification:** Execute `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/ --test`.

### Session Handover
To execute this Epic iteratively, start a NEW chat session and run: `/tier5-resume --target docs/epic/epic_93_tracker.md`
