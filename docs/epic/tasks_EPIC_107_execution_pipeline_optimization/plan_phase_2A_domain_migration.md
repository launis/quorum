# Phase 2A: Guard Step Fusion - Domain Migration

## Goal
Implement the core domain DTO for the unified Input Processing step by migrating security features out of the standalone Guard step. Delete the legacy `guard.py` domain model.

## Target Files (Modify)
- `@[c:\src\quorum\backend_v2\models\domain\security.py]`
- `@[c:\src\quorum\backend_v2\models\state.py]`
- `@[c:\src\quorum\backend_v2\models\domain\judge.py]`
- `@[c:\src\quorum\backend_v2\models\domain\scoring.py]`
- `@[c:\src\quorum\backend_v2\models\domain\__init__.py]`

## Target Files (Delete)
- `@[c:\src\quorum\backend_v2\models\domain\guard.py]`
- `@[c:\src\quorum\backend_v2\tests\unit\test_guard_models.py]`
- `@[c:\src\quorum\backend_v2\tests\unit\models\domain\test_guard.py]`

## Destructive Operation Inventory: `guard.py`
- `GuardInput` — INTENTIONALLY DROPPED — Reason: Redundant. Input logic unified.
- `TaintedDataContent` — INTENTIONALLY DROPPED — Reason: Tainted data concepts merged.
- `SecurityCheck` — MIGRATED to `security.py`.
- `GuardDTO` — INTENTIONALLY DROPPED — Reason: Replaced by InputProcessingOutputDTO.
- `GuardOutput` — INTENTIONALLY DROPPED — Reason: Replaced by InputProcessingOutputDTO.
- `SanitizationResult` — INTENTIONALLY DROPPED — Reason: `SanitizationResultDTO` already exists in `security.py`.

## Step-by-Step Instructions

1. **Migrate to `security.py`:**
   - Migrate `SecurityCheck` from `guard.py` to `security.py` (Delete `SanitizationResult` entirely as `SanitizationResultDTO` exists).
   - Create `InputProcessingOutputDTO(ReasoningTraceDTO)` in `security.py` with `model_config = ConfigDict(strict=True, extra='forbid')`. (Ensure `ReasoningTraceDTO` is imported from `backend_v2.models.domain.base`).
   - Add fields `is_safe: bool` and `rejection_reason: Annotated[str | None, Field(description="Reason for rejection if unsafe")] = None`.
   - Nest `security_check: SecurityCheck | None = None` inside `InputProcessingOutputDTO`.
   - Add `@model_validator(mode='after')` to `InputProcessingOutputDTO` to throw `ValueError` if `is_safe` is `False` but `rejection_reason` is missing (forcing Schema Healing).
   - *Producer Verification:* The `Input Processing` step's LLM prompt in `seed_data.json` will produce this JSON structure.

2. **Update `state.py`:**
   - In `WorkflowState` class, delete the `step_guard` property accessor.
   - Add a new property accessor `step_input_processing` that returns `self.get_context("step_input_processing", InputProcessingOutputDTO)`.
   - Ensure imports correctly reference `InputProcessingOutputDTO` from `backend_v2.models.domain.security`.

3. **Update Blast Radius Dependencies:**
   - **`judge.py`**: Replace `step_guard: Annotated[GuardOutput | None, ...]` with `step_input_processing: Annotated[InputProcessingOutputDTO | None, ...]` in `JudgeInput`.
   - **`scoring.py`**: Delete `TaintedDataContent` from imports and references. Update `StepGuardDTO` to use `InputProcessingOutputDTO` or remove it if obsolete.
   - **`__init__.py`**: Remove all exports mapping to `guard.py` and replace with `security.py` equivalents.

4. **Delete `guard.py` and Tests:**
   - Delete `backend_v2/models/domain/guard.py` completely.
   - Delete `backend_v2/tests/unit/test_guard_models.py` and `backend_v2/tests/unit/models/domain/test_guard.py`.

## Testing & Quality Gate Plan
- **Baseline:** Record the current passing test count.
- **Unit Tests:** Verify that `InputProcessingOutputDTO` validation fails correctly when `is_safe=False` without a reason.
- **Audit Loop:** Run `uv run python scripts/backend_audit_loop.py backend_v2/models/domain --test` to verify schema validation and type checking.

---
# Session Handover
To execute this Epic iteratively, start a NEW chat session and run the `/tier5-resume` command found at the bottom of your tracker.
