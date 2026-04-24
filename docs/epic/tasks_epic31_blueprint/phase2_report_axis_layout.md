# Epic 31 - Phase 2: Removing Duck Typing from the ReportAxis Layout Loop

## 1. Goal
Purge the `isinstance(v, dict)` branching and legacy duck typing from the ReportAxis Layout generation loop inside `BlueprintTransformer.build_report_dto`. This includes removing legacy fallback logic like guessing `f"{k}_justification"` if `step_3_logical_friction` is missing. The `ReportAxisDTO` instantiation must rely on strict Pydantic models with no silent fallbacks.

## 2. Context & Constraints
- **TARGET (Modify):**
  - `backend_v2/services/blueprint.py`
  - `backend_v2/tests/unit/test_blueprint_transformer.py`
- **CONTEXT (Read-Only):**
  - `backend_v2/models/v2_core.py`
  - `backend_v2/models/state.py`
- **Architectural Rules (00-antigravity-core & 01-python-backend):**
  - No Naked Dicts in State: Ensure the fold trace output respects schema logic.
  - The Duct Tape Ban: Stop defaulting to `None` or empty strings when keys go missing. The code should crash on invalid schemas.

## 3. Execution Sequence
1. Locate the deep `for step_res in results.values():` and `for k, v in step_data.items():` loops in `blueprint.py`.
2. Delete the legacy `isinstance(v, dict)` checks.
3. Remove suffix checks for legacy V1 keys (`_justification`, `_scaled`, `_normalized`, etc.) if they rely on duck-typed fallbacks.
4. Enforce that `v` maps to a known Pydantic model (e.g., pulling data from typed properties like `v.coaching`, `v.justification`). If `v` is an untyped dict, convert it or raise `AppException`.
5. Remove all `v.get(...)` calls that mask missing data and replace them with strict attribute access or strict validation.

## 4. Verification & Quality Gate Plan
- **Negative Tests:** Add specific unit tests to `test_blueprint_transformer.py` that inject malformed layout properties. Verify that `AppException(ErrorCodes.VALIDATION_FAILED)` is thrown instead of the loop continuing silently.
- **Coverage Check:** Ensure coverage remains above 90% and no existing happy paths break.
- **Quality Loop Execution:**
  ```powershell
  uv run python scripts/backend_audit_loop.py backend_v2/services/blueprint.py backend_v2/tests/unit/test_blueprint_transformer.py --test
  ```
