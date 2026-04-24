# [x] COMPLETE: Epic 31 - Phase 1: Eradicating `_extract_numeric_score` and Naked Dict Access

## 1. Goal
Remove the legacy `_extract_numeric_score` static method from `BlueprintTransformer` (`backend_v2/services/blueprint.py`). This method currently uses defensive `isinstance(val, dict)` checks and attempts to guess the location of a score (`step_4_final_score` or `score`), violating the Zero-Compromise and Fail-Fast mandates. The pipeline must expect and enforce strictly typed models (like `EvaluationResult`) instead of using `.get()` and duck typing on naked dictionaries.

## 2. Context & Constraints
- **TARGET (Modify):**
  - `backend_v2/services/blueprint.py`
  - `backend_v2/tests/unit/test_blueprint_transformer.py`
  - `backend_v2/tests/unit/test_blueprint_microcot.py`
  - `backend_v2/tests/unit/test_blueprint_sdui.py` (as needed for failing tests)
- **CONTEXT (Read-Only):**
  - `backend_v2/models/v2_core.py`
  - `backend_v2/models/state.py`
  - `backend_v2/models/domain/evaluation.py`
- **Architectural Rules (00-antigravity-core):**
  - Zero-Compromise Pledge: Eradicate fallback chains.
  - Fail-Fast Protocol: Raise `AppException(ErrorCodes.VALIDATION_FAILED)` if the score cannot be extracted natively from a typed property.
- **UI/UX Scoping (Desktop-First):** Desktop views require high-density valid data. Empty badges due to swallowed errors are unacceptable.

## 3. Execution Sequence
1. Delete the `_extract_numeric_score` static method entirely from `BlueprintTransformer`.
2. Refactor the numeric extraction inside the main `build_report_dto` loop:
   - Identify where `BlueprintTransformer._extract_numeric_score(target_val)` is called.
   - Replace it with strict, model-driven extraction. If `step_data` contains a score, it must be accessed via proper object properties or typed models. If the dictionary lacks the expected strict schema, throw `AppException(message="Invalid numeric score", details={"error_code": ErrorCodes.VALIDATION_FAILED}, status_code=400)`.
3. Update all unit tests that rely on `_extract_numeric_score` or test the graceful fallback behavior. Convert them to "Negative Tests" that assert the system crashes with a 400 Validation Error.

## 4. Verification & Quality Gate Plan
- **Fail-Fast Safety Tests:** Write negative tests in `test_blueprint_transformer.py` proving that passing an untyped dictionary without a clear `score` or `total_score` crashes the transformer rather than returning a fallback `0.0` or `None`.
- **Quality Loop Execution:**
  ```powershell
  uv run python scripts/backend_audit_loop.py backend_v2/services/blueprint.py backend_v2/tests/unit/test_blueprint_transformer.py --test
  ```
- **OpenAPI Schema Check:**
  ```powershell
  uv run python scripts/backend_audit_loop.py backend_v2/services/blueprint.py --openapi
  ```
