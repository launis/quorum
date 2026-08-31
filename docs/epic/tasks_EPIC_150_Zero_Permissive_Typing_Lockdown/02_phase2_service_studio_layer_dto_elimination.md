# Phase 2: Service & Studio Layer DTO Elimination

> **STATUS: DEFERRED** — This is a placeholder. Run `/tier0-create-plan @[docs/epic/EPIC_150_Zero_Permissive_Typing_Lockdown.md] @[docs/epic/EPIC_150_tracker.md]` to generate the full implementation plan for this phase.

## Scope Summary

Eliminate all `dict[str, Any]` annotations from the service layer, progress tracking, studio services, and worker telemetry. Refine existing `ProgressState` model and create `TaskMetadataDTO`, `SimulationResultDTO`.

## Target Files (~20 files)

- `@[backend_v2/services/progress.py]`
- `@[backend_v2/core/registry.py]`
- `@[backend_v2/services/studio/simulation_service.py]`
- `@[backend_v2/services/studio/workflow_service.py]`
- `@[backend_v2/services/studio/system_config_service.py]`
- `@[backend_v2/services/studio/prompt_block_service.py]`
- `@[backend_v2/services/studio/output_profile_service.py]`
- `@[backend_v2/services/execution.py]`
- `@[backend_v2/services/llm_task_executor.py]`
- `@[backend_v2/services/flattener.py]`
- `@[backend_v2/services/blueprint.py]`
- `@[backend_v2/services/mcp/mcp_tool_loop.py]`
- `@[backend_v2/worker.py]`
- `@[backend_v2/utils/redis_patcher.py]`
- `@[backend_v2/utils/dict_utils.py]`
- `@[backend_v2/models/dtos/system.py]`
