# Phase 2: Prompt Block & Output Profile Extraction

## 1. Goal
Extract `StudioPromptBlockService` and `StudioOutputProfileService` from the monolithic `StudioService`. Integrate them into the DI container and update corresponding routers.

## 2. Architectural Invariants
- **Strangler Fig Pattern**: Incrementally reduce the footprint of `StudioService`.
- **Single Responsibility Principle**: Separate logic for evaluating raw data (Prompt Blocks) from UI formatting logic (Output Profiles).

## 3. Destructive Operation Inventory
Move from `StudioService`:
- `list_prompt_blocks` -> `StudioPromptBlockService`
- `get_prompt_block` -> `StudioPromptBlockService`
- `save_prompt_block` -> `StudioPromptBlockService`
- `delete_prompt_block` -> `StudioPromptBlockService`
- `create_prompt_block_draft` -> `StudioPromptBlockService`
- `clone_prompt_block` -> `StudioPromptBlockService`
- `list_output_profiles` -> `StudioOutputProfileService`
- `get_output_profile` -> `StudioOutputProfileService`
- `save_output_profile` -> `StudioOutputProfileService`
- `delete_output_profile` -> `StudioOutputProfileService`
- `create_output_profile_draft` -> `StudioOutputProfileService`
- `clone_output_profile` -> `StudioOutputProfileService`

## 4. Proposed Changes

### [NEW] `backend_v2/services/studio/prompt_block_service.py`
- Create `StudioPromptBlockService`.

### [NEW] `backend_v2/services/studio/output_profile_service.py`
- Create `StudioOutputProfileService`.
- Inject `StudioWorkflowService` to validate `save_output_profile` against workflow steps.

### [MODIFY] `backend_v2/services/studio/__init__.py`
- Add exports for `StudioPromptBlockService` and `StudioOutputProfileService`.

### [MODIFY] `backend_v2/api/dependencies.py`
- Add `StudioPromptBlockServiceDep` and `StudioOutputProfileServiceDep`.

### [MODIFY] `backend_v2/api/routers/studio/prompt_blocks.py`
- Inject `StudioPromptBlockServiceDep`.
- Retain `StudioServiceDep` for `simulate_prompt_block` until Phase 4.

### [MODIFY] `backend_v2/api/routers/studio/output_profiles.py`
- Inject `StudioOutputProfileServiceDep` for all routes.

### [MODIFY] `backend_v2/api/routers/output_profiles.py` (root level router)
- Inject `StudioOutputProfileServiceDep` to replace the monolithic dependency.

## 5. Testing Strategy & Quality Gate
1. Run backend audit loop: `uv run python scripts/backend_audit_loop.py backend_v2/services/studio/ --test`
2. Run router audit loops.

---
### Session Handover
```bash
/tier5-resume --target="docs/epic/studio_decomposition_tracker.md" --workflow="/tier2-execute" --achieved="Phase 1 Executed. StudioWorkflowService extracted and passed MyPy. Phase 2 planned." --learned="MyPy internal errors can occur if dependencies are missing during DI instantiation. Solved via correct Repo injection. OutputProfile validation depends on Workflow extraction details, requiring StudioWorkflowService injection." --remaining="Execute phase 2: prompt profile services extraction."
```
