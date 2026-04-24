# Epic 37: Phase 1 - Secondary Scoring Logic Hardening

## 1. Goal Description
Enforce the "Zero-Compromise" Fail-Fast architecture in the secondary scoring hooks (`calculate_evaluation_fidelity_hook`, `evaluate_judge_passivity_hook`) within `backend_v2/hooks/scoring.py`. The goal is to eradicate legacy dictionary-based parsing (`.get()`, `isinstance()`) by migrating to strict Pydantic V2 validation using `StepGuardDTO`, `StepFalsifierDTO`, and `StepPanelDTO`.

## 2. Scope
**TARGET (Modify):**
- `c:\src\quorum\backend_v2\hooks\scoring.py`
- `c:\src\quorum\backend_v2\models\domain\scoring.py` (or equivalent models file to hold the new DTOs)

**CONTEXT (Read-Only):**
- `c:\src\quorum\docs\epic\epic37_hook_directory_zero_compromise.md`
- `c:\src\quorum\.agents\rules\01-python-backend.md`

## 3. Sequence & Implementation Steps
1. **Pydantic Models:** 
   - Define strict Pydantic models: `StepGuardDTO`, `StepFalsifierDTO`, `StepPanelDTO` in the domain models layer.
   - Enforce `model_config = ConfigDict(extra='forbid', frozen=True)`.
2. **API/Hook Implementation (`scoring.py`):**
   - Refactor `calculate_evaluation_fidelity_hook` and `evaluate_judge_passivity_hook`.
   - Remove `isinstance(data, dict)` and `data.get("step_guard")` checks.
   - Inject `.model_validate(data)` for incoming payload parsing. If invalid, allow `ValidationError` to bubble up or wrap in `AppException(ErrorCodes.VALIDATION_FAILED)`.
3. **Fail-Fast Enforcement:**
   - Remove any silent fallbacks or `try-except pass` blocks.
   - Ensure the hook only interacts with strongly-typed DTO attributes.

## 4. Verification & Quality Gate Plan
- **Tools to execute:**
  - `uv run python scripts/backend_audit_loop.py backend_v2/hooks/scoring.py backend_v2/models/domain/scoring.py`
  - Ensure 0 Ruff/MyPy errors.
- **Unit Tests:**
  - Verify that `tests/backend_v2/hooks/test_scoring.py` covers the newly refactored hooks and correctly asserts a fail-fast crash when invalid/missing keys are provided.
