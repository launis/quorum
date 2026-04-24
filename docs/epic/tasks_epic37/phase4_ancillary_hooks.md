# Epic 37: Phase 4 - Ancillary Hooks Hardening

## 1. Goal Description
Conduct a blanket audit and Zero-Compromise hardening on the remaining ancillary hooks (`metrics.py`, `archival.py`, `hydration.py`, `linguistics.py`, `integrity.py`). Eradicate all `isinstance` checks, `dict.get()` usages, fix any inline imports, and upgrade typings to modern Python 3.14 standards (`PEP 695`, `| None`).

## 2. Scope
**TARGET (Modify):**
- [x] `c:\src\quorum\backend_v2\hooks\metrics.py`
- [x] `c:\src\quorum\backend_v2\hooks\archival.py`
- [x] `c:\src\quorum\backend_v2\hooks\hydration.py`
- [x] `c:\src\quorum\backend_v2\hooks\linguistics.py`
- [x] `c:\src\quorum\backend_v2\hooks\integrity.py`

**CONTEXT (Read-Only):**
- `c:\src\quorum\docs\epic\epic37_hook_directory_zero_compromise.md`
- `c:\src\quorum\.agents\rules\01-python-backend.md`

## 3. Sequence & Implementation Steps
1. **Pydantic Models:** 
   - Define strict input DTOs for each hook boundary where missing (e.g., `MetricsPayloadDTO`, `HydrationPayloadDTO`).
2. **API/Hook Implementation:**
   - Move all inline imports to the top of the respective files (PEP 8).
   - Replace legacy `typing.Optional` and `typing.Union` with modern Python 3.14 `| None` syntax.
   - Strip out `isinstance(data, dict)` checks and `.get()` defaults across all five files.
3. **Fail-Fast Enforcement:**
   - The hooks must unconditionally trust the Pydantic-validated models or crash `AppException(400)`.

## 4. Verification & Quality Gate Plan
- **Tools to execute:**
  - `uv run python scripts/backend_audit_loop.py backend_v2/hooks/metrics.py backend_v2/hooks/archival.py backend_v2/hooks/hydration.py backend_v2/hooks/linguistics.py backend_v2/hooks/integrity.py`
  - Ensure 0 Ruff/MyPy errors.
- **Unit Tests:**
  - Verify full coverage in corresponding `tests/backend_v2/hooks/test_*.py` files, confirming type safety and fail-fast triggers.
