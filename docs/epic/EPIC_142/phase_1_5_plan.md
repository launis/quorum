<required_context_rules>
- @[.agents/rules/00-antigravity-core.md]
- @[.agents/rules/01-python-backend.md]
- @[docs/epic/EPIC_142_Matrix_Atom_Boolean_Evaluation_Fix.md]
</required_context_rules>

# Phase 1.5: Producer Contract Fix (scoring.py & execution.py)

## Objective
Fix upstream PRODUCERS that currently emit raw `True`/`False` booleans and `.value` strings. This must be completed before Phase 2 to prevent real executions from crashing at the Pydantic validation boundary enforced in Phase 1.

## Steps

### 1. Update scoring.py
**File:** `@[backend_v2/hooks/scoring.py]`
- In the logic evaluating matrix scores (around line 710):
  - Ensure `ExecutionStatus` is imported from `backend_v2.models.enums`.
  - Update the `evaluated_atoms_by_block` dictionary type annotation from `dict[str, dict[str, bool | str]]` to `dict[str, dict[str, ExecutionStatus]]`.
  - Replace boolean `True` assignment with `ExecutionStatus.PASSED` (around line 925).
  - Replace boolean `False` assignment with `ExecutionStatus.FAILED` (around line 929).
  - Replace string `"DLQ"` assignment with `ExecutionStatus.SYSTEM_ERROR` (around line 915).
  - Replace string `"CONTESTED"` assignment with `ExecutionStatus.PASSED` (around line 920).

### 2. Update execution.py
**File:** `@[backend_v2/services/execution.py]`
- In the `override_atom` function (around line 990):
  - Ensure `ExecutionStatus` is imported if needed.
  - Change the assignment of `payload.new_status.value` to the native Enum object `payload.new_status`.

## Verification Plan

### Automated Tests
- Run `uv run python scripts/backend_audit_loop.py backend_v2 --test`

### Negative Test Scenarios (Anti-Happy-Path Mandate)
- **Test 1**: Verify that passing raw boolean values (`True`/`False`) or raw strings (`"FAILED"`) to `evaluated_atoms` in downstream processing explicitly crashes Pydantic validation due to strict Enum enforcement, proving the DTO boundary is locked.
- **Test 2**: Verify that applying a human override via `override_atom` with an invalid `ExecutionStatus` strictly raises an `AppException` before modifying the state dictionary.
