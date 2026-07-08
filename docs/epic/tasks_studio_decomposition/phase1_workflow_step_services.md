# Phase 1: Workflow & Step Services Extraction

## 1. Goal
Extract the `StudioWorkflowService` and core authorization logic from `StudioService`. Integrate them into the FastAPI dependency graph and update the `workflows.py` and `steps.py` routers.

## 2. Architectural Invariants
- **Fail-Fast Hydration (01-python-backend.md)**: No naked dicts in state. 
- **Strangler Fig Pattern (tier3-god-code-decomposition.md)**: We are extracting one bounded context. The original `StudioService` will remain in `studio.py` for un-migrated components until Phase 4.

## 3. Destructive Operation Inventory
The following methods will be moved from `StudioService`:
- `_enforce_tenant_isolation` -> `backend_v2/services/studio/auth_validator.py`
- `_enforce_modification_rights` -> `backend_v2/services/studio/auth_validator.py`
- `_stitch_profiles_to_workflows` -> `StudioWorkflowService`
- `list_workflows` -> `StudioWorkflowService`
- `get_workflow` -> `StudioWorkflowService`
- `get_workflow_available_extensions` -> `StudioWorkflowService`
- `save_workflow` -> `StudioWorkflowService`
- `delete_workflow` -> `StudioWorkflowService`
- `create_workflow_draft` -> `StudioWorkflowService`
- `clone_workflow` -> `StudioWorkflowService`
- `list_steps` -> `StudioWorkflowService`
- `get_step` -> `StudioWorkflowService`
- `save_step` -> `StudioWorkflowService`
- `delete_step` -> `StudioWorkflowService`
- `create_step_draft` -> `StudioWorkflowService`
- `clone_step` -> `StudioWorkflowService`

## 4. Proposed Changes

### [NEW] `backend_v2/services/studio/__init__.py`
- Initialize the barrel export for the studio domain.

### [NEW] `backend_v2/services/studio/auth_validator.py`
- Expose pure functions `enforce_tenant_isolation` and `enforce_modification_rights`.

### [NEW] `backend_v2/services/studio/workflow_service.py`
- Create `StudioWorkflowService` with the extracted methods.
- Refactor the methods to use the pure `auth_validator` functions.

### [MODIFY] `backend_v2/api/dependencies.py`
- Add `get_studio_workflow_service` and `StudioWorkflowServiceDep`.

### [MODIFY] `backend_v2/api/routers/studio/workflows.py`
- Inject `StudioWorkflowServiceDep` for all CRUD operations.
- **Strangler Fig**: Keep injecting `StudioServiceDep` ONLY for `simulate_workflow` (which will be migrated in Phase 4).

### [MODIFY] `backend_v2/api/routers/studio/steps.py`
- Inject `StudioWorkflowServiceDep` for all CRUD operations.
- **Strangler Fig**: Keep injecting `StudioServiceDep` ONLY for `simulate_step` (which will be migrated in Phase 4).

## 5. Testing Strategy & Quality Gate
1. Run backend audit loop: `uv run python scripts/backend_audit_loop.py backend_v2/services/studio/ --test`
2. Run router audit loop: `uv run python scripts/backend_audit_loop.py backend_v2/api/routers/studio/ --test`

---
### Session Handover
```bash
/tier5-resume --target="docs/epic/studio_decomposition_tracker.md" --workflow="/tier2-execute" --achieved="Phase 1 Planned" --learned="Strangler fig pattern is active for simulations." --remaining="Execute Phase 1."
```
