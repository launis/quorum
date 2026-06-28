# Phase 3: Prompt Escape Hatch & Validation

Source: Epic Phase 2.3, 2.4, and Appendix E.3

## Target Files (Modify)
- `backend_v2/models/prompts/field_prompts.py`
- `backend_v2/services/orchestrator/prompt_compiler.py`
- `backend_v2/services/llm_task_executor.py`

## Requirements
1. **Field Prompts**: 
   - Update `DESC_EXACT_QUOTES` (or similar prompt constants) to include the Escape Hatch: *"Jos sääntö on negatiivinen rajoite ja teksti noudattaa sitä, palauta tyhjä lista []. Tyhjä lista on täysin oikea vastaus faktojen puuttuessa."*
2. **Prompt Compiler (`prompt_compiler.py`)**: 
   - Update `get_schema_healing_prompt()` (the `is_logical_error` branch).
   - Inject the Escape Hatch to break infinite DLQ loops: *"JOS nämä lähteet eivät sisällä väitettäsi, PALAUTA TYHJÄ LISTA []. Älä keksi lähteitä."*
3. **Semantic Validation (`llm_task_executor.py`)**: 
   - In `_perform_semantic_validation()`, add explicit validation for `used_evidence_ids`.
   - Ensure every ID in `used_evidence_ids` is present in the `alias_map`. If not, raise `SemanticEvidenceError` utilizing the new `resolve()` method from `alias_registry.py`.

## Architectural Invariants & Hardening Mandate
- **Rule 47 (prompt_compiler_immutability)**: Although usually locked, this Epic grants explicit permission to modify `get_schema_healing_prompt()` to add the Escape Hatch. DO NOT modify other parts of the compiler.
- **Rule 18 (rfc7807_dual_reporting_strict)**: `SemanticEvidenceError` should inherit or be mapped to `AppException` properly if it bubbles beyond the retry loop.
- **Rule 20 (the_self_healing_ban)**: Do not attempt to Regex-patch the `used_evidence_ids`. Rely strictly on Pydantic and the DLQ retry loop to force the LLM to fix it.

## Documentation Update
Update `docs/architecture/06_evaluation_and_scoring.md` regarding the Escape Hatch logic and negative constraint handling.

## Testing & Quality Gate Plan
- **Integration Tests**: Verify that `get_schema_healing_prompt` correctly outputs the Escape Hatch string when a `SemanticEvidenceError` is caught during the retry loop.
- **Verification**: Run `uv run python scripts/backend_audit_loop.py backend_v2/models/prompts/field_prompts.py backend_v2/services/orchestrator/prompt_compiler.py --test`

---
### Session Handover
To execute this Epic iteratively, start a NEW chat session and run: `/tier5-resume --target docs/epic/EPIC_88_Unified_Forensic_Traceability_tracker.md`
