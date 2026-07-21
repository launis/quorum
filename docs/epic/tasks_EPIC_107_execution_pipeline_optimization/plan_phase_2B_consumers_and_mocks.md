# Phase 2B: Guard Step Fusion - Consumers & Mocks

## Goal
Refactor all downstream consumers (scoring, judge) to read security data from the unified Input Processing output state instead of the deleted Guard step, and update tests/mocks.

## Target Files (Modify)
- `@[c:\src\quorum\backend_v2\models\domain\scoring.py]`
- `@[c:\src\quorum\backend_v2\hooks\scoring.py]`
- `@[c:\src\quorum\backend_v2\models\domain\judge.py]`
- `@[c:\src\quorum\backend_v2\llm\mock_data.py]`

## Step-by-Step Instructions

1. **Update `scoring.py`:**
   - In `StepGuardDTO`, refactor it to read security data from the unified Input Processing output state instead of a separate `step_guard` key.

2. **Update `hooks/scoring.py`:**
   - REFACTOR the `sanitization_result` accessor to read from the Input Processing state context instead of `step_guard`.

3. **Update `judge.py`:**
   - In `JudgeInput`, replace `step_guard: GuardOutput | None` with `step_input_processing: InputProcessingOutputDTO | None`.
   - Import `InputProcessingOutputDTO` from `backend_v2.models.domain.security`.

4. **Update `mock_data.py`:**
   - DELETE `MOCK_GUARD_OUTPUT`.
   - Update `MOCK_INPUT_PROCESSING_OUTPUT` (or equivalent) to include `is_safe`, `rejection_reason`, and `security_check` to reflect the new fused schema.

5. **Update Documentation & Directory Laws:**
   - Update `docs/architecture/` and `.agents/rules/04_directory_reference.md` if necessary to document the removal of the standalone Guard step and its consolidation into Input Processing.

## Testing & Quality Gate Plan
- **Baseline:** Record the current passing test count.
- **Unit Tests:** Fix `test_guard.py` by deleting it or migrating tests to test `security.py`'s `InputProcessingOutputDTO`.
- **Integration Tests:** Ensure scoring and judge mocks work seamlessly.
- **Audit Loop:** Run `uv run python scripts/backend_audit_loop.py backend_v2/ --test` (Universal Quality Gate).

---
# Session Handover
To execute this Epic iteratively, start a NEW chat session and run the `/tier5-resume` command found at the bottom of your tracker.
