# Phase 1: Matrix Output Schema Extension (Data Loss Prevention)

## 1. Description and Objective
**Prerequisite for Epic 34: Global Hooks Zero-Compromise Hardening.**
Before replacing `scoring.py` legacy dictionary flattening, we must ensure `LightweightMatrixOutput` and `XaiExtensionType` schemas contain the necessary fields to preserve original LLM evaluation state. The backend operates fundamentally on the `raw_score` which is currently lost from final state persistence if omitted.

## 2. File Scoping
- **TARGET (Modify):** 
  - `backend_v2/models/dtos/lightweight_matrix.py`
  - `backend_v2/models/enums.py`
- **CONTEXT (Read-Only):** 
  - `backend_v2/hooks/scoring.py`

## 3. Implementation Steps
1. **LightweightMatrixOutput Update:** Add `raw_score: float` to `LightweightMatrixOutput` in `backend_v2/models/dtos/lightweight_matrix.py`. This ensures the original 1-N score is preserved before 0.0-1.0 normalization logic runs.
2. **XaiExtensionType Update:** Add `SOURCE_ID = "source_id"` to `XaiExtensionType` in `backend_v2/models/enums.py` to preserve `step_1b_cited_source_id`.
3. Note: `true_atoms` and `false_atoms` do not need schema additions as they are derivable from `evaluated_atoms`.

## 4. Verification & Quality Gate Plan
- **Unit Testing:** Ensure Pydantic schema validation enforces the new attributes accurately.
- **Audit Loop Execution:** `uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/lightweight_matrix.py backend_v2/models/enums.py --openapi --test`
