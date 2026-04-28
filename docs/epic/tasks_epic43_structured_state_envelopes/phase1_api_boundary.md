# Phase 1: API Boundary Sovereignty

## Objective
Implement a structured API boundary layer to guarantee Data Sovereignty. This phase eliminates the "API Boundary Leakage" trap where internal database fields (like `organization_id`) leak into public DTOs, causing `extra="forbid"` Pydantic crashes on the frontend and requiring localized `exclude=True` hacks in FastAPI routers.

## Architectural Invariants (Mandatory Rules)
- **Zero-Duck-Typing / Strict Pydantic V2 Rust:** Use `ConfigDict(extra='forbid', strict=True)`. Reject unstructured AI outputs instantly.
- **Data Leak Prevention Firewall:** Every single FastAPI router MUST explicitly define a `response_model` to strip hidden database variables out of the HTTP response string, preventing Cross-Tenant Trace Leaks.
- **The Zero Compromise Pledge:** Do NOT use `exclude=True` locally in routers. The DTO must handle its own domain serialization.

## Execution Steps

1. **Target (Modify): `backend_v2/models/dtos/base.py`**
   - Create a new class `BaseResponseDTO` inheriting from `V2CoreBase` (from `backend_v2.models.v2_core`).
   - Define `organization_id: str | None = Field(default=None, exclude=True)` inside `BaseResponseDTO`. This inherently drops the field from `.model_dump()` output, guaranteeing it won't leak to the API responses.

2. **Target (Modify): `backend_v2/models/dtos/output_profile.py`**
   - Refactor `OutputProfileResponseDTO` to inherit from `BaseResponseDTO`.
   - Remove the local `organization_id` field from `OutputProfileResponseDTO`, as it's now handled by the base class.
   - *Context (Read-Only):* `OutputProfileCreateDTO`, `OutputProfileUpdateDTO`.

3. **Target (Modify): Other relevant DTOs in `backend_v2/models/dtos/`**
   - Audit `inputs.py`, `report.py`, `synthesis.py`, `lightweight_matrix.py` etc., and switch any response-facing DTOs that currently implement `organization_id: str | None = Field(..., exclude=True)` to inherit from `BaseResponseDTO`.

4. **[x] Target (Modify): API Routers (`backend_v2/api/routers/`)**
   - Scan for any `response_model_exclude={"organization_id"}` in `@router.get` or `@router.post` decorators and remove them. The new `BaseResponseDTO` handles this globally.

## Verification & Quality Gate Plan
- **Script:** `uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/ backend_v2/api/routers/ --openapi`
- OpenAPI schema MUST generate successfully without namespace collisions.
- No Pydantic validation errors when returning OutputProfiles.
