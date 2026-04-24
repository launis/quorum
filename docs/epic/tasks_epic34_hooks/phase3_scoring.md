# Phase 3: Refactoring Scoring Key-Guessing

## 1. Description and Objective
**Epic 34: Global Hooks Zero-Compromise Hardening.**
The `enforce_passivity_penalty_hook` and `normalize_matrix_scores_hook` rely on inspecting string prefixes (`k.startswith("matrix_")`). The objective is to destroy duck-typed key matching and replace it with strict `LightweightMatrixOutput` validation, enforcing explicit Evaluation blocks.

## 2. File Scoping
- **TARGET (Modify):** 
  - `backend_v2/hooks/scoring.py`
- **CONTEXT (Read-Only):** 
  - `backend_v2/models/dtos/lightweight_matrix.py`

## 3. Implementation Steps
1. [x] **Remove Prefix Magic:** Replace `startswith("matrix_")` and `endswith("_justification")` matching with strict Evaluation block DTO fetching.
2. [x] **Pydantic Validation:** Map the scoring values through explicit `PromptBlock` or `LightweightMatrixOutput` models directly instead of looping over dictionary keys dynamically.
3. [x] **Replace Flattening:** Replace legacy dictionary flattening in `normalize_matrix_scores_hook` with strict schema mapping.
4. [x] **O(1) Map Pre-computation:** Replace nested dictionary iteration loops with O(1) pre-computed lookup dictionaries for performance scaling.

## 4. Verification & Quality Gate Plan
- **Unit Testing:** Test `enforce_passivity_penalty_hook` and `normalize_matrix_scores_hook` isolated pure functions. Use `PydanticModel.model_construct()` for testing the orchestrator integration.
- **UI Traceability Check:** Ensure that the XAI extension visibility for `_justification` and `_cited_source_id` still works flawlessly.
- **Audit Loop Execution:** `uv run python scripts/backend_audit_loop.py backend_v2/hooks/scoring.py --test`
