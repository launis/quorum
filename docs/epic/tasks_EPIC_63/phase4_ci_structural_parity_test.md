# Phase 4: CI-Level Structural Parity Meta-Test

> **Source**: Epic 63 – Phase 4 (CI-tason Meta-yksikkötestin toteutus / Automated Parity Quality Gate)

---

## Objective

Implement the automated structural parity unit test that dynamically inspects `ExecutionCoreFields`, `WorkflowState`, and `ExecutionRecord` using Python's `__annotations__` introspection. This test MUST fail immediately (Fail-Fast) if any child class illegally redefines an inherited core field, guaranteeing zero schema drift between the domain and persistence models.

---

## Architectural Invariants (Injected from `.agents/rules/`)

| Rule ID | Rule | Enforcement |
|---|---|---|
| R2 (`strict_pydantic_v2_rust`) | Pydantic V2 `model_fields` for inheritance checking | Used alongside `__annotations__` |
| R55-59 (`pep257_google_style`) | Google-style docstrings on test functions | All new tests |
| `tdd_mandate` | Write failing test first, verify it catches regressions | Core design principle |
| `the_zero_compromise_pledge` | Zero tolerance for schema drift | This test enforces it at CI level |

---

## Scoping

### TARGET Files (Modify)
1. **[MODIFY]** `backend_v2/tests/unit/test_v2_core_models.py` — Add the structural parity meta-test

### CONTEXT Files (Read-Only)
- `backend_v2/models/execution_core.py` — `ExecutionCoreFields` SSOT
- `backend_v2/models/state.py` — `WorkflowState`
- `backend_v2/models/v2_core.py` — `ExecutionRecord`

---

## Milestones

### Milestone 4.1: Implement Structural Parity Meta-Test (Source: Epic Phase 4, Section 4 + Warning Block)

**File**: `backend_v2/tests/unit/test_v2_core_models.py` [MODIFY]

Add the following test function to the existing test file:

```python
def test_strict_schema_parity_for_core_execution_fields() -> None:
    """Meta-test: Enforce that child classes inherit and do NOT redefine core fields.

    Uses __annotations__ (not model_fields) because model_fields includes
    BOTH inherited AND own fields, making it impossible to detect redefinitions.
    __annotations__ contains ONLY the fields explicitly defined at that class level.

    The 'status' field is whitelisted as a legitimate override because
    ExecutionRecord uses LaxExecutionStatus (broader type) while
    ExecutionCoreFields uses Literal (strict domain type).
    """
    from backend_v2.models.execution_core import ExecutionCoreFields
    from backend_v2.models.state import WorkflowState
    from backend_v2.models.v2_core import ExecutionRecord

    core_field_names = set(ExecutionCoreFields.model_fields.keys())
    assert len(core_field_names) >= 5, "ExecutionCoreFields must define at least 5 shared fields"

    # Fields that child classes are explicitly allowed to override
    # (e.g., ExecutionRecord overrides 'status' with LaxExecutionStatus)
    allowed_overrides = {"status"}

    for child_cls in [WorkflowState, ExecutionRecord]:
        # 1. Verify inheritance
        assert issubclass(child_cls, ExecutionCoreFields), (
            f"{child_cls.__name__} must inherit from ExecutionCoreFields"
        )

        # 2. Verify NO redefinition of core fields using __annotations__
        own_annotations = child_cls.__annotations__  # Only THIS class level
        redefined = (core_field_names - allowed_overrides) & set(own_annotations.keys())
        assert not redefined, (
            f"{child_cls.__name__} illegally redefines inherited core fields: {redefined}. "
            f"These must be defined ONLY in ExecutionCoreFields."
        )

        # 3. Verify all core fields are accessible on the child
        child_all_fields = set(child_cls.model_fields.keys())
        missing = core_field_names - child_all_fields
        assert not missing, (
            f"{child_cls.__name__} is missing inherited core fields: {missing}"
        )
```

> [!IMPORTANT]
> **Key deviation from Epic's raw test code**: The `allowed_overrides = {"status"}` set is added because `ExecutionRecord` legitimately overrides the `status` field type from `Literal[...]` to `LaxExecutionStatus`. Without this whitelist, the test would always fail. This is explicitly documented in Phase 1's Milestone 1.1 Important note.

### Milestone 4.2: Verification — Prove the Meta-Test Catches Regressions (Source: Epic Phase 4, Varmistus)

The executing agent MUST verify the test works by:

1. Running the test and confirming it passes in the clean state:
   ```powershell
   uv run pytest backend_v2/tests/unit/test_v2_core_models.py::test_strict_schema_parity_for_core_execution_fields -v
   ```

2. Temporarily adding a redefined field to `WorkflowState` (e.g., `execution_trace: list[TraceEvent] = Field(...)`) and confirming the test **fails immediately** with a clear error message about illegal redefinition.

3. Reverting the temporary change.

---

## Documentation Update

Update `docs/architecture/02_domain_models.md` to document the CI-level structural parity test and its role in preventing schema drift.

---

## Testing & Quality Gate Plan

### Unit Tests
- The meta-test itself IS the quality gate. It must:
  - Pass when inheritance is correct and no core fields are redefined
  - Fail when a developer accidentally redefines a core field in a child class
  - Correctly handle the `status` override whitelist

### Quality Gates
```powershell
uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_v2_core_models.py --test
```

---

## Session Handover

```
To execute this plan, start a NEW chat session and run:
/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_63\phase4_ci_structural_parity_test.md]
```
