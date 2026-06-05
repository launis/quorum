# Phase 2: Workflow API & Context Router Cleanup

Source: Epic 68 Phase 1.3 & Phase 2.1

## Architectural Laws (from .agents/rules & hardening.xml)
- **Rule 18 (RFC 7807):** Ensure any new errors throw `AppException` with proper error codes.
- **Rule 32 (Anemic Routers):** API routers strictly encapsulate HTTP context. The computation logic for available extensions MUST go in `WorkflowService`, NOT the router.
- **Rule 47 (Zero DB Hardcoding Mandate):** Remove `if ext == "variance_validation"` from `context_router.py`. When refactoring, you must preserve functional behavior by translating it into a dynamic check.

## Target Files (Modify)
- `backend_v2/api/routers/system/workflow.py`
- `backend_v2/services/orchestrator/context_router.py`
- `docs/architecture/01_backend_api_and_core.md`

## Context Files (Read-Only)
- `backend_v2/models/enums.py`

## Tasks

1. **`backend_v2/api/routers/system/workflow.py`**:
   - Create a backend computation logic in `WorkflowService` (or locally if small) to calculate the union of all `output_extensions` defined across all Target Matrices within a specific DAG.
   - Expose this via a new endpoint `/api/v2/workflows/{id}/available-extensions` or append it to the existing Workflow DTO. Provide strict Pydantic V2 schemas.

2. **`backend_v2/services/orchestrator/context_router.py`**:
   - Remove the `variance_validation` bypass at L95-99.
   - Refactor `route_and_prune()` to read `output_profile.visible_block_extensions` instead of `output_profile.visible_extensions`.
   - Ensure the router becomes scope-blind (it just iterates over whatever list it receives).

3. **Documentation Update**:
   - Update `c:\src\quorum\docs\architecture\01_backend_api_and_core.md` to explain the new `/api/v2/workflows/{id}/available-extensions` logic and how `ContextRouter` became scope-blind.

## Testing & Quality Gate Plan
- **Quality Gate:** Execute `uv run python scripts/backend_audit_loop.py backend_v2/api/routers/system/workflow.py backend_v2/services/orchestrator/context_router.py --openapi`

## Session Handover
To execute this phase, start a NEW chat session and run:
`/tier2-execute --target="c:\src\quorum\docs\epic\tasks_EPIC_68_Extension_Scope_Separation\phase2_api_and_routing.md"`
