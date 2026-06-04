# Phase 3: Factory Pattern Adapter & API Boundary Hardening

> **Source**: Epic 63 – Phase 3 (Adapterin ja Rajapintojen Hardening / API Boundaries)

---

## Objective

Implement the `create_execution_record` type-safe factory function and replace all direct `ExecutionRecord(...)` instantiation sites with this centralized factory. This eliminates field drift risk between the two known instantiation locations.

---

## Architectural Invariants (Injected from `.agents/rules/`)

| Rule ID | Rule | Enforcement |
|---|---|---|
| R2 (`strict_pydantic_v2_rust`) | Strict Pydantic instantiation, not dict splat | Factory uses explicit Pydantic constructor |
| R18 (`rfc7807_dual_reporting_strict`) | Errors → `AppException(error_code=ErrorCodes.XYZ)`, not `ValueError` | Factory wraps `ValidationError` with `AppException` |
| R24 (`python_314_modern_syntax`) | `X \| None`, PEP 695 generics | All annotations |
| R55-59 (`pep257_google_style`) | Google-style docstrings with Args/Returns/Raises | Factory function docstring |
| R73 (`no_inline_imports`) | All imports global | Strict enforcement |
| R80 (`pydantic_validation_bypass_ban`) | Explicit Pydantic instantiation | No `dict(model)` patterns |

---

## Scoping

### TARGET Files (Modify)
1. **[MODIFY]** `backend_v2/services/execution.py` — Add `create_execution_record()` factory; replace direct `ExecutionRecord(...)` instantiation at line 319
2. **[MODIFY]** `backend_v2/services/orchestrator/dag_executor.py` — Replace direct `ExecutionRecord(...)` instantiation at line 348

### CONTEXT Files (Read-Only)
- `backend_v2/models/v2_core.py` — `ExecutionRecord`, `FrozenContext`, `WorkflowInputs`, `ExecutionStepState` definitions
- `backend_v2/models/execution_core.py` — `ExecutionCoreFields` SSOT
- `backend_v2/models/enums.py` — `ExecutionStatus`, `ErrorCodes`
- `backend_v2/exceptions.py` — `AppException`

---

## Milestones

### Milestone 3.1: Implement `create_execution_record` Factory (Source: Epic Phase 3, Section 3.3)

**File**: `backend_v2/services/execution.py` [MODIFY]

Add the following factory function at module level (before the `ExecutionService` class definition, around line 46):

```python
def create_execution_record(
    execution_id: str,
    workflow_id: str,
    raw_inputs: WorkflowInputs,
    frozen_context: FrozenContext,
    **extra_persistence_fields: Any,
) -> ExecutionRecord:
    """Type-safe factory for ExecutionRecord creation.

    Centralizes initialization logic to prevent field drift between
    dag_executor.py and execution.py instantiation sites.

    Args:
        execution_id: Opaque Stripe ID for the execution.
        workflow_id: ID of the workflow definition.
        raw_inputs: Validated user inputs by role.
        frozen_context: Immutable snapshot of context at execution start.
        **extra_persistence_fields: Additional presentation-layer fields.

    Returns:
        A strictly validated ExecutionRecord instance.

    Raises:
        AppException: If Pydantic validation fails (VALIDATION_FAILED).
    """
    try:
        return ExecutionRecord(
            id=execution_id,
            workflow_id=workflow_id,
            status=ExecutionStatus.PENDING,
            raw_inputs=raw_inputs,
            frozen_context=frozen_context,
            **extra_persistence_fields,
        )
    except ValidationError as e:
        logger.error(
            "[ExecutionService] Fail-Fast: ExecutionRecord creation failed: %s",
            e,
            exc_info=True,
        )
        raise AppException(
            message=f"ExecutionRecord creation failed: {e}",
            status_code=500,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        ) from e
```

**Required additional import** at top of `execution.py`:
```python
from pydantic import ValidationError
```

### Milestone 3.2: Replace Instantiation in `execution.py` (Source: Epic Phase 3, Korvattavat instansioinnit #2)

**File**: `backend_v2/services/execution.py` [MODIFY]

Replace the direct `ExecutionRecord(...)` instantiation in `start_execution()` method (currently at lines 319-335):

**BEFORE** (current code):
```python
        initial_record = ExecutionRecord(
            id=execution_id,
            workflow_id=workflow.id,
            status=ExecutionStatus.PENDING,
            raw_inputs=payload.raw_inputs,
            output_profile_id=resolved_profile_id,
            frozen_context=FrozenContext(ui_hints_snapshot=ui_hints),
            step_states=step_states,
            metadata={
                "target_locale": target_locale,
                "profile_id": resolved_profile_id,
                "matrix_sampling_strategy": payload.matrix_sampling_strategy,
                "workflow_version": workflow.version,
            },
            created_by=initiator.id,
            organization_id=getattr(initiator, "organization_id", None),
        )
```

**AFTER** (refactored):
```python
        initial_record = create_execution_record(
            execution_id=execution_id,
            workflow_id=workflow.id,
            raw_inputs=payload.raw_inputs,
            frozen_context=FrozenContext(ui_hints_snapshot=ui_hints),
            output_profile_id=resolved_profile_id,
            step_states=step_states,
            metadata={
                "target_locale": target_locale,
                "profile_id": resolved_profile_id,
                "matrix_sampling_strategy": payload.matrix_sampling_strategy,
                "workflow_version": workflow.version,
            },
            created_by=initiator.id,
            organization_id=getattr(initiator, "organization_id", None),
        )
```

### Milestone 3.3: Replace Instantiation in `dag_executor.py` (Source: Epic Phase 3, Korvattavat instansioinnit #1)

**File**: `backend_v2/services/orchestrator/dag_executor.py` [MODIFY]

1. **Add import** at top of file:
   ```python
   from backend_v2.services.execution import create_execution_record
   ```

2. **Replace** the direct `ExecutionRecord(...)` instantiation in `execute_workflow()` method (currently at lines 348-356):

**BEFORE** (current code):
```python
            exec_record = ExecutionRecord(
                id=execution_id,
                workflow_id=workflow.id,
                status=ExecutionStatus.RUNNING,
                raw_inputs=raw_inputs,
                execution_trace=[],
                step_states=step_states,
                frozen_context=FrozenContext(),
            )
```

**AFTER** (refactored):
```python
            exec_record = create_execution_record(
                execution_id=execution_id,
                workflow_id=workflow.id,
                raw_inputs=raw_inputs,
                frozen_context=FrozenContext(),
                status=ExecutionStatus.RUNNING,
                step_states=step_states,
            )
```

> [!NOTE]
> The `dag_executor.py` instantiation passes `status=ExecutionStatus.RUNNING` (not PENDING), which overrides the factory's default. This is valid because `**extra_persistence_fields` accepts any additional keyword arguments passed through to `ExecutionRecord(...)`.

---

## Documentation Update

Update `docs/architecture/02_domain_models.md` to document the `create_execution_record` factory pattern and its role in preventing field drift.

---

## Testing & Quality Gate Plan

### Unit Tests
- **File**: `backend_v2/tests/unit/services/test_execution.py` [MODIFY]
- Add `test_create_execution_record_factory_success()`:
  - Verify factory returns a valid `ExecutionRecord` with correct `status=PENDING`
  - Verify all core fields from `ExecutionCoreFields` are populated
- Add `test_create_execution_record_factory_fail_fast()`:
  - Verify factory raises `AppException` (not raw `ValidationError`) when passed invalid data
  - Verify the `error_code` is `VALIDATION_FAILED`

### Integration Tests
- Existing tests in `test_executions.py`, `test_worker.py`, `test_pdf_generator.py`, `test_flattener.py`, and `test_worker_synthesis.py` that construct `ExecutionRecord(...)` directly MUST still pass. These tests are NOT refactored in this phase (they test their own concerns).

### Quality Gates
```powershell
uv run python scripts/backend_audit_loop.py backend_v2/services/execution.py backend_v2/services/orchestrator/dag_executor.py --test
```

---

## Session Handover

```
To execute this plan, start a NEW chat session and run:
/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_63\phase3_factory_adapter_api_hardening.md]
```
