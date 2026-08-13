# Phase 1: DAG Engine Strategy Inference Refactoring

## Objective
Remove the hardcoded `task_blueprint` check for synthesis in the DAG executor and replace it with a robust dynamic evaluation based on `model_strategy`.

## Scope
### [MODIFY] `backend_v2/services/orchestrator/dag_executor.py`
- Locate the hardcoded `if step_obj.task_blueprint == "sp_7a8b9c0d1e2f3a4b":` block.
- Replace the rigid check with a dynamic property inference: `if step_def.model_strategy == "synthesis":`.
- Ensure all logging and error boundaries accurately reflect dynamic strategy inference.
