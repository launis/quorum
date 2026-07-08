# Phase 4: Simulation Service & God Code Deletion

## 1. Goal
Complete the Strangler Fig migration by extracting `StudioSimulationService` and physically deleting the original `backend_v2/services/studio.py` file. Update the dependency container to permanently sever the legacy God object.

## 2. Architectural Invariants
- **Strangler Fig Finalization**: The final cleanup phase guarantees no orphaned imports or unresolved `StudioService` references remain.
- **Architectural Documentation**: The IDE rules must be updated if this restructuring introduces major directory shifts.

## 3. Destructive Operation Inventory
Move from `StudioService`:
- `simulate_workflow` -> `StudioSimulationService`
- `simulate_prompt_block` -> `StudioSimulationService`
- `simulate_step` -> `StudioSimulationService`

**DELETE**: `backend_v2/services/studio.py` completely.

## 4. Proposed Changes

### [NEW] `backend_v2/services/studio/simulation_service.py`
- Create `StudioSimulationService`.
- Since simulation touches everything, it may need `IWorkflowRepository`, `IPromptBlockRepository`, etc.

### [MODIFY] `backend_v2/services/studio/__init__.py`
- Export `StudioSimulationService`.

### [MODIFY] `backend_v2/api/dependencies.py`
- Add `StudioSimulationServiceDep`.
- **DELETE** `get_studio_service` and `StudioServiceDep` completely from the system.

### [MODIFY] Routers (Final Pass)
- `backend_v2/api/routers/studio/workflows.py`: Replace legacy `StudioServiceDep` with `StudioSimulationServiceDep` for `simulate` endpoint.
- `backend_v2/api/routers/studio/steps.py`: Same.
- `backend_v2/api/routers/studio/prompt_blocks.py`: Same.

### [DELETE] `backend_v2/services/studio.py`
- Pre-Delete Audit: Execute a `grep_search` across `backend_v2` for `StudioService` to ensure zero usage.
- Physically delete the file.

### [MODIFY] `docs/architecture/` and `.agents/rules/04_directory_reference.md`
- Document the new `backend_v2/services/studio/` directory structure.

## 5. Testing Strategy & Quality Gate
1. Comprehensive audit of all studio routers and services.
2. Ensure 0% usage of old `StudioService` remains.

---
### Session Handover
```bash
/tier5-resume --target="docs/epic/studio_decomposition_tracker.md" --workflow="/tier2-execute" --achieved="Phase 4 Planned" --learned="Simulation service extracted and legacy file removed." --remaining="Execute Phase 4."
```
