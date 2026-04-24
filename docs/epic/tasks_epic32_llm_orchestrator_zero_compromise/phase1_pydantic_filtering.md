# Phase 1: Replacing `_strip_heavy_keys` with Pydantic Filtering

## Objective
Refactor `LLMNodeStrategy.execute` by removing the recursive duck-typing dictionary mutation `_strip_heavy_keys` and replacing it with strict Pydantic model validation (`LLMContextFilter`). This enforces the Zero-Compromise pledge and Code-is-the-Truth mandate by blocking unstructured state mutations.

## Architecture Sequence
1. **Pydantic Models**: Define `LLMContextFilter` in `backend_v2/models/dtos/orchestrator.py` (or within `llm.py`).
2. **API/Service**: Replace `_strip_heavy_keys` logic inside `LLMNodeStrategy` with `.model_validate()` and `.model_dump(exclude_unset=True)`.

## Scope Definitions
### TARGET (Modify)
- `c:\src\quorum\backend_v2\services\orchestrator\strategies\llm.py`
- `c:\src\quorum\backend_v2\models\dtos\orchestrator.py` (New file)
- `c:\src\quorum\backend_v2\tests\unit\test_llm_context_filter.py` (New file)

### CONTEXT (Read-Only)
- `c:\src\quorum\docs\epic\epic32_llm_orchestrator_zero_compromise.md`
- `c:\src\quorum\.agents\rules\01-python-backend.md`

## Implementation Steps
1. `[x]` Create `backend_v2/models/dtos/orchestrator.py`.
2. `[x]` Define `LLMContextFilter` class inheriting from Pydantic `BaseModel`.
3. `[x]` Add a `@model_validator(mode='before')` or recursive filter that actively drops `shuffled_atoms` and correctly extracts booleans from `evaluations` list elements. Ensure `quote` and `reasoning` are purged from atoms dynamically.
4. `[x]` Modify `backend_v2/services/orchestrator/strategies/llm.py`:
   - `[x]` Import `LLMContextFilter`.
   - `[x]` Remove `def _strip_heavy_keys(obj: Any) -> None:`.
   - `[x]` Refactor `_strip_heavy_keys(llm_context_data)` to `llm_context_data = LLMContextFilter.model_validate(llm_context_data).model_dump(exclude_unset=True)`.
   - `[x]` Ensure the returned dict retains the required nested structure safely.
5. `[x]` Extract the logic as a pure testable function if it necessitates complex tree traversals.

## Verification & Quality Gate Plan
- **New Unit Tests:** `backend_v2/tests/unit/test_llm_context_filter.py` using `PydanticModel.model_construct()` and isolated dictionary inputs.
- **Audit Tooling:** 
  - `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/llm.py backend_v2/models/dtos/orchestrator.py backend_v2/tests/unit/test_llm_context_filter.py --test`
- **Criteria:** 0 Warnings on Ruff, 100% Strict Type Coverage (Mypy), and Pytest passing for isolated logic.
