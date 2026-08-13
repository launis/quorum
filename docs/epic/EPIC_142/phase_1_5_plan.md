# Phase 1.5: Producer Contract Fix (scoring.py & execution.py)

## Objective
Fix upstream PRODUCERS that currently emit raw `True`/`False` booleans and `.value` strings. This must be completed before Phase 2 to prevent real executions from crashing at the Pydantic validation boundary enforced in Phase 1.

## Steps

### 1. Update scoring.py
**File:** `backend_v2/hooks/scoring.py`
- In `_calculate_matrix_scores_from_evaluations` (note: actual function might be named slightly differently, ensure to target the hook logic that populates evaluations):
  - Ensure `ExecutionStatus` is imported.
  - Update the `evaluated_atoms_by_block` dictionary type annotation (if explicitly declared) to use `ExecutionStatus`.
  - Replace boolean `True` assignment with `ExecutionStatus.PASSED`.
  - Replace boolean `False` assignment with `ExecutionStatus.FAILED`.
  - Replace string `"DLQ"` assignment with `ExecutionStatus.SYSTEM_ERROR`.
  - Replace string `"CONTESTED"` assignment with `ExecutionStatus.PASSED`.

### 2. Update execution.py
**File:** `backend_v2/services/execution.py`
- In `apply_human_override`:
  - Ensure `ExecutionStatus` is imported.
  - Change the assignment of `payload.new_status.value` to the native Enum object `payload.new_status`.

### 3. Verification
- Run `uv run python scripts/backend_audit_loop.py backend_v2 --test`
