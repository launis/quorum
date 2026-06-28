# Phase 5: Async Fuzzy Matching & Worker Pre-Calculation

Source: Epic Phase 2.5, 2.8, and 2.8.1

## Target Files (Modify)
- `backend_v2/services/llm_task_executor.py` (or relevant post-processing hook like `backend_v2/hooks/validation.py`)
- `backend_v2/services/mcp/anchor_validation_service.py` (if adjustment is needed)

## Requirements
1. **Async Pre-Calculation (CRITICAL RULE)**: 
   - Fuzzy matching (`calculate_fuzzy_score()`) MUST NOT be executed synchronously during `BlueprintTransformer` (API GET requests) due to O(N*M) complexity.
   - It MUST be executed asynchronously during the Worker phase (after LLM returns the payload).
2. **Execution Logic**:
   - For every quote in the returned `quotes` list, iterate through all MCP sources defined in `used_evidence_ids`.
   - Call `AnchorValidationService.calculate_fuzzy_score()` against the MCP raw source text.
   - If the score exceeds `get_lexical_fuzz_threshold(locale)`, map the quote to that source ID and mark it as `is_mcp_verified = True`.
   - Store this computed relationship (e.g. `is_mcp_verified` and the `source_reference`) into the permanent `execution_trace` or directly into the saved model for this execution.
3. **Didactic DLQ (Semantic Sanity Check)**:
   - If `used_evidence_ids` is provided but the fuzzy match completely fails (no text found), raise `SemanticEvidenceError`: *"Sitaattia ei löydy fyysisesti lähteestä. Älä tiivistä, kopioi sanatarkasti."*

## Architectural Invariants & Hardening Mandate
- **Rule 34 (blocking_the_fastapi_thread)**: Enforce asynchronous pre-calculation in the worker thread. Never block the FastAPI event loop with O(N*M) fuzzy matching.
- **Rule 48 (synthesis_pure_functions)**: Ensure the downstream reporting API remains a pure O(1) projection layer by persisting these relationships now.

## Documentation Update
Update `docs/architecture/06_evaluation_and_scoring.md` regarding the Async Pre-Calculation architecture for Evidence validation.

## Testing & Quality Gate Plan
- **Unit Tests**: Test the worker loop's interaction with `AnchorValidationService`.
- **Verification**: Run `uv run python scripts/backend_audit_loop.py backend_v2/services/llm_task_executor.py --test`

---
### Session Handover
To execute this Epic iteratively, start a NEW chat session and run: `/tier5-resume --target docs/epic/EPIC_88_Unified_Forensic_Traceability_tracker.md`
