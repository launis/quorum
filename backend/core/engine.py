import logging
from typing import Any

from backend.core.registry import TaskRegistry
from backend.exceptions import WorkflowExecutionError
from backend.models.workflow import WorkflowDefinition

logger = logging.getLogger(__name__)


class GraphEngine:
    """Metadata-driven workflow engine.
    Executes workflows defined by WorkflowDefinition using the TaskRegistry.
    """

    async def execute_workflow(
        self,
        definition: WorkflowDefinition,
        initial_input: dict[str, Any],
        repository: Any = None,  # AbstractWorkflowRepository
        execution_id: str | None = None,
    ) -> dict[str, Any]:
        """Execute a workflow definition sequentially.

        Args:
            definition: The workflow schema definition.
            initial_input: The initial input variables.
            repository: Optional repository to persist intermediate state.
            execution_id: Optional ID to link updates to.

        Returns:
            The final execution state.
        """
        execution_state = initial_input.copy()
        logger.info(f"Starting workflow '{definition.id}' with {len(definition.steps)} steps.")

        for step in definition.steps:
            try:
                # 1. Resolve Inputs
                task_inputs = self._resolve_inputs(step.inputs, execution_state)

                # 2. Get Task Handler
                task_def = TaskRegistry.get(step.task_key)
                if not task_def:
                    raise ValueError(f"Task '{step.task_key}' not found in registry.")

                # 3. Validate Inputs against Schema
                # This ensures the data matches what the handler expects
                validated_input = task_def.input_schema.model_validate(task_inputs)

                # 4. Execute Task
                logger.debug(f"Executing step '{step.id}' ({step.task_key})...")

                # INSPECT HANDLER SIGNATURE
                # Standard agents accept execution_config.
                # Functional tasks (register_task) might not.
                import inspect

                sig = inspect.signature(task_def.handler)

                if "execution_config" in sig.parameters or any(
                    p.kind == p.VAR_KEYWORD for p in sig.parameters.values()
                ):
                    result = await task_def.handler(validated_input, execution_config=step.config)
                else:
                    # Backward compatibility for functional tasks
                    result = await task_def.handler(validated_input)

                # 5. Store Result
                # We store the raw Pydantic model or dict in the state
                # If result is a Pydantic model, dump it to dict for state consistency?
                # For now, let's keep it flexible or dump it.
                # specification says: Store the result in execution_state.step_results[step.id]

                # If the handler returns a Pydantic model, we generally want to store it as a dict
                # to make it easily accessible for future steps JSON pathing
                if hasattr(result, "model_dump"):
                    state_val = result.model_dump()
                else:
                    state_val = result

                # Refactor: Store in step_results
                if "step_results" not in execution_state:
                    execution_state["step_results"] = {}
                
                execution_state["step_results"][step.id] = state_val
                
                logger.debug(f"Step '{step.id}' completed.")

                # 6. PERSISTENCE (Step-by-Step)
                if repository and execution_id:
                    try:
                        # Sanitize state before saving (similar to router logic)
                        # We do a basic hygiene check or rely on repository adapter
                        # But importantly: Update 'results', 'current_step', 'status'
                        updates = {
                            "results": execution_state,
                            "current_step": step.id,  # Keep for legacy/internal
                            "current_step_name": step.id,  # Frontend Contract
                            "status": "running",
                            # "updated_at": ... (handled by repo or db trigger usually)
                        }

                        # HOISTING LOGIC FIX (Jan 2026)
                        # Ensure xai_report_formatted is promoted to top-level for Frontend visibility

                        # Protocol: Hoist XAI Reporting fields to top-level state
                        # This ensures the Frontend can access summary cards (Verdict, Score, etc.)
                        # directly from the Execution object.

                        hoist_fields = [
                            "xai_report_formatted",
                            "final_verdict",
                            "confidence_score",
                            "executive_summary",
                            "analysis_strengths",
                            "analysis_weaknesses",
                            "analysis_opportunities",
                            "analysis_recommendations",
                        ]

                        for field in hoist_fields:
                            # Check dict
                            if isinstance(state_val, dict) and state_val.get(field):
                                updates[field] = state_val[field]
                            # Check Pydantic
                            elif hasattr(state_val, field) and getattr(state_val, field):
                                updates[field] = getattr(state_val, field)

                        await repository.update_execution(execution_id, updates)
                        logger.debug(f"Persisted state after step '{step.id}'.")
                    except Exception as e:
                        # Non-blocking failure for persistence?
                        logger.warning(f"Failed to persist intermediate state for {execution_id}: {e}")

            except Exception as e:
                error_code = "WORKFLOW_STEP_FAILED"
                logger.error(f"{error_code}: Workflow failed at step '{step.id}': {e}", exc_info=True)
                raise WorkflowExecutionError(
                    step_id=step.id,
                    task_key=step.task_key,
                    original_error=e,
                    details={"execution_state": execution_state, "error_code": error_code},
                ) from e

        logger.info(f"Workflow '{definition.id}' execution completed.")
        return execution_state

    def _resolve_inputs(self, input_mapping: dict[str, str], state: dict[str, Any]) -> dict[str, Any]:
        """Resolve input values from the execution state based on mapping definition.

        Args:
            input_mapping: Dict mapping target field mapping string (e.g. "$step1.result")
            state: Current execution state dictionary.

        Returns:
            Dict representing the actual inputs for the task.
        """
        resolved = {}
        for target_field, source_path in input_mapping.items():
            if isinstance(source_path, str) and source_path.startswith("$"):
                # Remove '$' and split by dot
                path_parts = source_path[1:].split(".")
                value = state
                try:
                    for part in path_parts:
                        if isinstance(value, dict):
                            value = value.get(part)
                        else:
                            # Try attribute access if it's an object/model
                            value = getattr(value, part)

                        if value is None:
                            break
                    resolved[target_field] = value
                except Exception as e:
                    # If path resolution fails, we might want to pass None or raise error
                    # For now, explicit None if path doesn't exist
                    logger.debug(f"Input resolution failed for path '{source_path}': {e}")
                    resolved[target_field] = None
            else:
                # Static value
                resolved[target_field] = source_path
        return resolved
