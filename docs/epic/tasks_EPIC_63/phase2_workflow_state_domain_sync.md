# Phase 2: WorkflowState Domain Model Refactor

> **Source**: Epic 63 – Phase 2 (Domain-mallin `WorkflowState` päivitys / Domain Sync)

---

## Objective

Refactor `WorkflowState` in `backend_v2/models/state.py` to inherit from `ExecutionCoreFields` (from the new leaf module created in Phase 1), removing all duplicated core fields while preserving the pure domain methods and type-safe accessors.

---

## Architectural Invariants (Injected from `.agents/rules/`)

| Rule ID | Rule | Enforcement |
|---|---|---|
| R2 (`strict_pydantic_v2_rust`) | `ConfigDict(frozen=True, strict=True, extra="forbid")` via V2CoreBase chain | Inherited through `ExecutionCoreFields` → `V2CoreBase` |
| R24 (`python_314_modern_syntax`) | `X \| None`, not `Optional[X]` | All type annotations |
| R55-59 (`pep257_google_style`) | Google-style docstrings | All classes and methods |
| R73 (`no_inline_imports`) | All imports global at top of file | Strict enforcement |
| R92 (`pydantic_mutation_optimization`) | `.model_copy(update={...})`, not dump-then-reconstruct | Preserved in `add_event()` |

> [!CAUTION]
> **CIRCULAR IMPORT ANALYSIS**: This phase creates a circular import path: `execution_core.py` imports `TraceEvent` from `state.py`, and `state.py` will import `ExecutionCoreFields` from `execution_core.py`. This is safe because Python resolves imports at module load time, and `TraceEvent` is defined BEFORE `WorkflowState` in `state.py`. When `state.py` is first loaded, it defines `TraceEvent`, `ErrorTraceEvent`, `TombstoneEvent` etc. When `execution_core.py` imports from `state.py`, those classes are already defined. When `state.py` then imports `ExecutionCoreFields` from `execution_core.py`, that module has already been fully loaded. The `from __future__ import annotations` in `execution_core.py` ensures type annotations are lazy-evaluated.

---

## Scoping

### TARGET Files (Modify)
1. **[MODIFY]** `backend_v2/models/state.py` — Refactor `WorkflowState` to inherit `ExecutionCoreFields`

### CONTEXT Files (Read-Only)
- `backend_v2/models/execution_core.py` — `ExecutionCoreFields` (created in Phase 1)
- `backend_v2/models/core_base.py` — `V2CoreBase` definition

---

## Milestones

### Milestone 2.1: Update `WorkflowState` Imports (Source: Epic Phase 2, Import-tarkistus)

**File**: `backend_v2/models/state.py` [MODIFY]

Add the following import at the module top (after existing imports, around line 16):

```python
from backend_v2.models.execution_core import ExecutionCoreFields
```

### Milestone 2.2: Refactor `WorkflowState` Inheritance (Source: Epic Phase 2, Toimenpide)

**File**: `backend_v2/models/state.py` [MODIFY]

1. **Change class inheritance** (line 117): Replace `class WorkflowState(V2CoreBase):` with:
   ```python
   class WorkflowState(ExecutionCoreFields):
   ```

2. **Remove duplicated fields** from `WorkflowState`'s class body. The following fields MUST be removed because they now come from `ExecutionCoreFields`:
   - `status` (lines 129-133) — REMOVE entirely. The core's `Literal["pending", "running", "completed", "failed"]` type is identical to what `WorkflowState` currently defines.
   - `execution_trace` (line 135) — REMOVE. Note the type change: `WorkflowState` currently has `list[TraceEvent]` but the core defines `list[ErrorTraceEvent | TombstoneEvent | TraceEvent]`. This is an **intentional parity upgrade** per the Epic (Phase 2, Tyyppikorjaukset section).
   - `execution_trace_storage_path` (lines 136-138) — REMOVE
   - `context_variables` (lines 140-142) — REMOVE
   - `context_variables_storage_path` (lines 143-145) — REMOVE

3. **Preserve all domain-specific fields and methods**:
   - `execution_id` (line 120) — KEEP
   - `workflow_id` (lines 121-126) — KEEP
   - `trace_version` (line 127) — KEEP
   - `workflow_name` (line 147) — KEEP
   - `created_at` (line 148) — KEEP
   - `start_time` property (lines 150-152) — KEEP
   - `add_event()` method (lines 154-157) — KEEP
   - `get_context()` method (lines 159-179) — KEEP
   - All type-safe accessor properties (lines 186-260) — KEEP
   - `StateProjector` class (lines 263-352) — KEEP (unmodified)

> [!IMPORTANT]
> **Type Upgrade Impact**: `WorkflowState.execution_trace` changes from `list[TraceEvent]` to `list[ErrorTraceEvent | TombstoneEvent | TraceEvent]`. The `add_event()` method signature currently accepts `event: TraceEvent`. This is still correct because `ErrorTraceEvent` and `TombstoneEvent` are subclasses of `TraceEvent`, so any instance of those types satisfies the `TraceEvent` parameter type. No signature change is needed.

---

## Documentation Update

Update `docs/architecture/02_domain_models.md` with the `WorkflowState` inheritance change and the type parity upgrade for `execution_trace`.

---

## Testing & Quality Gate Plan

### Unit Tests
- **File**: `backend_v2/tests/unit/test_v2_core_models.py` [MODIFY]
- Add `test_workflow_state_inherits_execution_core_fields()`:
  - Verify `issubclass(WorkflowState, ExecutionCoreFields)` is True
  - Verify `WorkflowState` instances have all 5 core fields accessible
  - Verify `WorkflowState.execution_trace` accepts `ErrorTraceEvent` and `TombstoneEvent` instances

### Quality Gates
```powershell
uv run python scripts/backend_audit_loop.py backend_v2/models/state.py --test
```

---

## Session Handover

```
To execute this plan, start a NEW chat session and run:
/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_63\phase2_workflow_state_domain_sync.md]
```
