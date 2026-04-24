# Epic 37: Phase 3 - Security & Validation Strictness

## 1. Goal Description
Enforce the "Zero-Compromise" Fail-Fast architecture in the security and validation hooks (`backend_v2/hooks/security.py`, `backend_v2/hooks/validation.py`). Eliminate defensive programming constructs like `if not inputs or not isinstance(inputs, dict):` and `.get("_system_warnings", [])`. Enforce strict Pydantic parsing utilizing models like `SecurityPayloadDTO`.

## 2. Scope
**TARGET (Modify):**
- `c:\src\quorum\backend_v2\hooks\security.py`
- `c:\src\quorum\backend_v2\hooks\validation.py`
- `c:\src\quorum\backend_v2\models\domain\security.py` (or equivalent models file)

**CONTEXT (Read-Only):**
- `c:\src\quorum\docs\epic\epic37_hook_directory_zero_compromise.md`
- `c:\src\quorum\.agents\rules\01-python-backend.md`

## 3. Sequence & Implementation Steps
1. **Pydantic Models:** 
   - Define strict models for hook inputs (e.g., `SecurityPayloadDTO`, `ValidationHookPayloadDTO`).
   - Define structure for system warnings so it can be parsed natively rather than extracted dynamically.
2. **API/Hook Implementation (`security.py`, `validation.py`):**
   - Replace manual `isinstance` and `.get()` extractions with `.model_validate(inputs)`.
   - Ensure the hook only interacts with properly typed attributes (e.g., `payload.system_warnings`).
3. **Fail-Fast Enforcement:**
   - Instead of checking `if not inputs: return ...`, enforce that if the payload does not match the DTO, it crashes with `AppException(ErrorCodes.VALIDATION_FAILED)`.

## 4. Verification & Quality Gate Plan
- **Tools to execute:**
  - `uv run python scripts/backend_audit_loop.py backend_v2/hooks/security.py backend_v2/hooks/validation.py`
  - Ensure 0 Ruff/MyPy errors.
- **Unit Tests:**
  - Update `tests/backend_v2/hooks/test_security.py` and `tests/backend_v2/hooks/test_validation.py` to ensure legacy dictionary payloads fail instantly, while valid schemas process successfully.
