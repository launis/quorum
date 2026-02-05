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
        from backend.services.chat_log_parser import ChatLogParser

        # Hydration / Initialization
        execution_state = initial_input.copy()

        if execution_id and repository:
            try:
                # Attempt to hydrate from persistence
                record = await repository.get_execution(execution_id)
                if record and record.get("results"):
                    persisted_state = record["results"]
                    # "Merge initial_input into this restored state... give precedence to the persisted state."
                    # Strategy: Start with initial (default), then update with persisted (overwrite matching keys).
                    if persisted_state:
                        logger.info(f"[GraphEngine] Resuming execution {execution_id} from persisted state.")
                        execution_state.update(persisted_state)
            except Exception as e:
                # Non-fatal warning, start fresh if hydration fails
                logger.warning(f"[GraphEngine] Failed to hydrate state for {execution_id}: {e}")

        # Jan 2026 Mandate: Centralized Chat Parsing / Sanitization
        # Enforce "User:" prefix on all chat inputs regardless of entry point (API, CLI, Test)
        for key, value in execution_state.items():
            if (key == "history_text" or "chat" in key or "history" in key) and isinstance(value, str):
                try:
                    original_len = len(value)
                    parsed_value = ChatLogParser.parse(value)
                    execution_state[key] = parsed_value
                    if len(parsed_value) != original_len:
                         logger.info(
                             f"[GraphEngine] ChatLogParser optimized '{key}': "
                             f"{original_len} -> {len(parsed_value)} chars"
                         )
                except Exception as e:
                    # Fail open or closed? Mandate says "Enforce", but we shouldn't crash workflow start if possible?
                    # "Strict Mode" suggests crashing.
                    logger.warning(f"[GraphEngine] ChatLogParser failed for '{key}': {e}")
                    # Keep raw value if parsing fails, but log warning.

        logger.info(f"Starting workflow '{definition.id}' with {len(definition.steps)} steps.")

        # Ensure step_results exists for idempotency checks
        if "step_results" not in execution_state:
            execution_state["step_results"] = {}

        total_steps = len(definition.steps)
        for i, step in enumerate(definition.steps):
            # Idempotency Check (Jan 2026)
            if "step_results" in execution_state and step.id in execution_state["step_results"]:
                logger.info(f"[GraphEngine] Skipping step '{step.id}' - result already exists in state.")
                continue

            # Graceful Cancellation Check (Jan 2026)
            if repository and execution_id:
                # We check the centralized status source of truth
                exec_status = await repository.get_execution_status(execution_id)
                if exec_status in ("cancelling", "cancelled"):
                    logger.info(f"[GraphEngine] Execution {execution_id} cancelled by user.")
                    execution_state["status"] = "cancelled"
                    # Break the loop to stop processing further steps
                    break


            try:
                # 0. HYDRATION (SSOT Pattern)
                # Ensure we are using the 'Library' definition of the step if available.
                # This enables central management of step logic (prompts, config) while allowing
                # workflows to override specific bindings (inputs).
                if repository:
                    try:
                        # Fetch the authoritative definition from the Registry
                        library_step_data = await repository.get_step_by_id(step.id)

                        if library_step_data:
                            logger.debug(f"[GraphEngine] Hydrating step '{step.id}' from Registry (SSOT).")
                            
                            # Merge Logic: Library is BASE, Workflow is OVERRIDE.
                            # We want to use the Library's config/task_key, but keep the Workflow's inputs/mapping.
                            
                            # 1. Update Task Key/Handler (if changed in lib)
                            if "task_key" in library_step_data:
                                step.task_key = library_step_data["task_key"]

                            # 2. Update Configuration (Deep Merge or Replacement?)
                            # Strategy: Library config is usually the Truth. Workflow might have empty config.
                            # If Workflow config is provided, does it override or augment?
                            # Standard Pattern: Workflow Overrides.
                            # But if Workflow config is 'stale snapshot', we typically want the Library version.
                            # Compromise: If Workflow config is empty, use Library.
                            lib_config = library_step_data.get("config", {})
                            if not step.config:
                                step.config = lib_config
                            else:
                                # Merge: Lib Config updated by Step Config
                                merged = lib_config.copy()
                                merged.update(step.config)
                                step.config = merged

                            # 3. Inputs usually stay with the Workflow (binding), preventing hydration refactor.
                        else:
                            logger.debug(f"[GraphEngine] Step '{step.id}' not found in Registry. Using local snapshot.")

                    except Exception as e:
                        logger.warning(f"[GraphEngine] Step hydration failed for '{step.id}': {e}. Continuing with snapshot.")

                # 1. Resolve Inputs
                task_inputs = self._resolve_inputs(step.inputs, execution_state)

                # 2. Get Task Handler
                task_def = TaskRegistry.get(step.task_key)
                if not task_def:
                    raise ValueError(f"Task '{step.task_key}' not found in registry (Hydrated Key: {step.task_key}).")

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
                            "current_step_index": i + 1,
                            "total_steps": total_steps,
                            "status": "running",
                            # "updated_at": ... (handled by repo or db trigger usually)
                        }


                        # Dynamic Hoisting (Jan 2026)
                        # Use the step definition's hoist_keys to determine what to promote.
                        if step.hoist_keys:
                            for field in step.hoist_keys:
                                # Check dict result
                                if isinstance(state_val, dict) and field in state_val:
                                    updates[field] = state_val[field]
                                # Check Pydantic model result
                                elif hasattr(state_val, field):
                                    val = getattr(state_val, field)
                                    if val is not None:
                                        updates[field] = val

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
