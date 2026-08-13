<required_context_rules>
- @[.agents\rules\00-antigravity-core.md]
- @[c:\Users\risto\.gemini\antigravity-ide\knowledge\tripartite_pipeline_architecture\artifacts\ki_tripartite_pipeline_architecture.md]
- @[c:\Users\risto\.gemini\antigravity-ide\knowledge\god_code_prevention\artifacts\ki_god_code_prevention.md]
- @[c:\Users\risto\.gemini\antigravity-ide\knowledge\dag_engine_dto_projection_rules\artifacts\ki_dag_engine_dto_projection_rules.md]
</required_context_rules>

# Phase 1: DAG Engine Strategy Inference Refactoring

## Objective
Remove the hardcoded `task_blueprint` check for synthesis in the DAG executor and replace it with a robust dynamic evaluation based on `model_strategy`.

## Scope
### [MODIFY] @[backend_v2/services/orchestrator/dag_executor.py#L558-L750]
- Locate the hardcoded `if step_obj.task_blueprint == "sp_7a8b9c0d1e2f3a4b":` block around line 584.
- Fetch the `Step` definition from the `step_definitions` dictionary: `step_def = step_definitions.get(step_obj.task_blueprint) if step_obj.task_blueprint else None`.
- Replace the rigid string check with a dynamic property inference: `if step_def and step_def.model_strategy == "synthesis":`.
- Keep the existing logging intact. Do not change `logger.info("[DAGExecutor] Successfully applied MatrixReducer pre-synthesis.")`.

### [CONTEXT_ONLY]
- @[backend_v2/models/v2_core.py#L706-L795] (Contains the `Step` domain model)
- @[backend_v2/seed/seed_data.json#L9053-L9056] (Shows the `sp_7a8b9c0d1e2f3a4b` blueprint has `model_strategy: "synthesis"`)

<anti_targets>
- Do NOT change any other part of `dag_executor.py`.
- Do NOT guess what `step_def` is without pulling it from `step_definitions`.
- Do NOT alter existing log messages.
</anti_targets>

<dod_checklist>
- [ ] `task_blueprint` hardcoded ID check is removed.
- [ ] `model_strategy == "synthesis"` check is implemented safely checking for `step_def` existence.
- [ ] Code successfully passes typing and formatting.
</dod_checklist>

<validation_gate>
Run global audit: `uv run python scripts/backend_audit_loop.py backend_v2 --test`
</validation_gate>
