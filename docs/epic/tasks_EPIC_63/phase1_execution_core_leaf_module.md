# Phase 1: ExecutionCoreFields Leaf Module & ExecutionRecord Refactor

> **Source**: Epic 63 – Phase 1 (Lehtimoduulin `execution_core.py` luonti ja `ExecutionRecord`-päivitys)

---

## Objective

Create the new SSOT leaf module `backend_v2/models/execution_core.py` containing the shared `ExecutionCoreFields` base class, then refactor `ExecutionRecord` in `v2_core.py` to inherit from it and remove all duplicated core fields.

---

## Architectural Invariants (Injected from `.agents/rules/`)

| Rule ID | Rule | Enforcement |
|---|---|---|
| R2 (`strict_pydantic_v2_rust`) | `ConfigDict(frozen=True, strict=True, extra="forbid")` inherited from V2CoreBase | `ExecutionCoreFields` inherits `V2CoreBase` |
| R24 (`python_314_modern_syntax`) | `X \| None`, not `Optional[X]`. PEP 695 generics | All new type annotations |
| R55-59 (`pep257_google_style`) | Google-style docstrings with Summary + Attributes/Args/Returns/Raises | All new classes and functions |
| R73 (`no_inline_imports`) | All imports global at top of file, except ML SDKs | Strict enforcement |
| R80 (`pydantic_validation_bypass_ban`) | `.model_validate()`, not `dict(model)` | No legacy patterns |

> [!CAUTION]
> **CIRCULAR IMPORT PREVENTION**: `execution_core.py` is a LEAF MODULE. It imports `TraceEvent`, `ErrorTraceEvent`, `TombstoneEvent` from `state.py` and `V2CoreBase` from `core_base.py`. It MUST NOT import from `v2_core.py`. Both `v2_core.py` and `state.py` import FROM this leaf module, never the reverse.

---

## Scoping

### TARGET Files (Modify/Create)
1. **[NEW]** `backend_v2/models/execution_core.py` — New leaf module containing `ExecutionCoreFields`
2. **[MODIFY]** `backend_v2/models/v2_core.py` — Refactor `ExecutionRecord` to inherit `ExecutionCoreFields`, remove duplicated fields, update imports

### CONTEXT Files (Read-Only)
- `backend_v2/models/core_base.py` — `V2CoreBase` definition (inherits `ConfigDict(frozen=True, strict=True, extra="forbid")`)
- `backend_v2/models/state.py` — `TraceEvent`, `ErrorTraceEvent`, `TombstoneEvent` definitions
- `backend_v2/models/enums.py` — `ExecutionStatus`, `LaxExecutionStatus` enum definitions

---

## Milestones

### Milestone 1.1: Create `execution_core.py` Leaf Module (Source: Epic Phase 1, New File)

**File**: `backend_v2/models/execution_core.py` [NEW]

Create the shared SSOT base class with the following exact schema:

```python
# backend_v2/models/execution_core.py  [NEW FILE]
"""Shared SSOT structural core for workflow executions.

This module is an intentional LEAF MODULE in the import graph.
It imports TraceEvent types from state.py and V2CoreBase from core_base.py,
but NOTHING imports this module's siblings (v2_core.py) to prevent circular imports.
"""
from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.state import ErrorTraceEvent, TombstoneEvent, TraceEvent


class ExecutionCoreFields(V2CoreBase):
    """The Single Source of Truth (SSOT) structural core for workflow executions.

    Inherited by both the active domain state (WorkflowState) and the
    historical persistent database record (ExecutionRecord).

    Attributes:
        status: Current lifecycle status of the execution.
        execution_trace: Append-only log of all trace events.
        execution_trace_storage_path: Cloud Storage offload path for large traces.
        context_variables: Dynamic blackboard for cross-step data sharing.
        context_variables_storage_path: Cloud Storage offload path for large context.
    """

    status: Literal["pending", "running", "completed", "failed"] = Field(
        default="pending",
        description="Current status of the workflow execution.",
    )
    execution_trace: list[ErrorTraceEvent | TombstoneEvent | TraceEvent] = Field(
        default_factory=list,
        description="Immutable log of all events.",
    )
    execution_trace_storage_path: str | None = Field(
        default=None,
        description="Path to offloaded trace JSON in Cloud Storage.",
    )
    context_variables: dict[str, Any] = Field(
        default_factory=dict,
        description="Current snapshots of context variables (the dynamic blackboard).",
    )
    context_variables_storage_path: str | None = Field(
        default=None,
        description="Path to offloaded context variables JSON in Cloud Storage.",
    )
```

**Key decisions**:
- The `status` field uses `Literal["pending", "running", "completed", "failed"]` directly (not the `LaxExecutionStatus` enum) because this is the structural core shared by both models. `ExecutionRecord` in `v2_core.py` currently uses `Annotated[LaxExecutionStatus, ...]` — it will override the `status` type at its own class level to preserve its Lax parsing behavior.
- `execution_trace` uses the full union type `list[ErrorTraceEvent | TombstoneEvent | TraceEvent]` — this is the correct parity type matching `ExecutionRecord`'s current definition on line 1164 of `v2_core.py`.

> [!IMPORTANT]
> **Agent Decision Required**: The Epic specifies `status` as a `Literal["pending", "running", "completed", "failed"]` on `ExecutionCoreFields`. However, `ExecutionRecord` currently uses `Annotated[LaxExecutionStatus, ...]` which accepts additional values like `"queued"`, `"processing"`. The executing agent MUST keep `ExecutionCoreFields.status` as the `Literal` type (covering the domain-standard values), and `ExecutionRecord` MUST override `status` at its own class level with the `LaxExecutionStatus` type. This means `status` will appear in BOTH `ExecutionCoreFields.__annotations__` AND `ExecutionRecord.__annotations__` — the meta-test in Phase 4 must account for this by whitelisting `status` as a legitimate override.

### Milestone 1.2: Refactor `ExecutionRecord` in `v2_core.py` (Source: Epic Phase 1, v2_core.py Update)

**File**: `backend_v2/models/v2_core.py` [MODIFY]

1. **Update import** (line 35): Replace `from backend_v2.models.state import ErrorTraceEvent, TombstoneEvent, TraceEvent` with `from backend_v2.models.execution_core import ExecutionCoreFields`. If `TraceEvent` types are still needed elsewhere in `v2_core.py` (they are NOT — only `ExecutionRecord` used them), remove the import entirely.

2. **Refactor `ExecutionRecord` class** (line 1150): Change inheritance from `V2CoreBase` to `ExecutionCoreFields`:
   ```python
   class ExecutionRecord(ExecutionCoreFields):
   ```

3. **Remove duplicated fields from `ExecutionRecord`**. The following fields MUST be removed from `ExecutionRecord`'s class body because they now come from `ExecutionCoreFields` via inheritance:
   - `execution_trace` (line 1164-1166) — REMOVE
   - `execution_trace_storage_path` (line 1167-1169) — REMOVE
   - `context_variables` (line 1174-1176) — REMOVE
   - `context_variables_storage_path` (line 1177-1179) — REMOVE

4. **KEEP `status` as an override** on `ExecutionRecord` (line 1155): `ExecutionRecord` uses `Annotated[LaxExecutionStatus, ...]` which is a broader type than the core's `Literal[...]`. This is a legitimate specialization.

5. **Update `__all__`** export list (line 40-68): Add `"ExecutionCoreFields"` to the `__all__` list so downstream consumers can import it from `v2_core.py` if needed.

---

## Documentation Update

Update `docs/architecture/02_domain_models.md` to document the new `ExecutionCoreFields` SSOT pattern and the inheritance hierarchy (`V2CoreBase` → `ExecutionCoreFields` → `WorkflowState` / `ExecutionRecord`).

---

## Testing & Quality Gate Plan

### Unit Tests
- **File**: `backend_v2/tests/unit/test_v2_core_models.py` [MODIFY]
- Add `test_execution_core_fields_inheritance_on_execution_record()`:
  - Verify `issubclass(ExecutionRecord, ExecutionCoreFields)` is True
  - Verify `ExecutionRecord` instances have all 5 core fields accessible
  - Verify `ExecutionCoreFields` has `model_config` with `frozen=True`, `strict=True`, `extra="forbid"`
- Existing tests for `ExecutionRecord` MUST continue to pass without modification

### Quality Gates
```powershell
uv run python scripts/backend_audit_loop.py backend_v2/models/execution_core.py backend_v2/models/v2_core.py --test
```

---

## Session Handover

```
To execute this plan, start a NEW chat session and run:
/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_63\phase1_execution_core_leaf_module.md]
```
