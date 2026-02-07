import logging
import inspect
import importlib
from typing import Any

from backend.core.registry import TaskRegistry
from backend.exceptions import WorkflowExecutionError
from backend.models.workflow import WorkflowDefinition

logger = logging.getLogger(__name__)

# Centralized Hook Mapping (Single Source of Truth)
HOOK_MAPPING = {
    # Reporting & Output
    "generate_report": ("backend.hooks.reporting", "generate_report"),
    # Validation & Structure
    "verify_structure": ("backend.hooks.validation", "verify_structure"),
    # Search & External
    "execute_google_search": ("backend.hooks.search", "execute_google_search"),
    # Security & PII (use wrapper functions)
    "sanitize_text": ("backend.hooks.security", "sanitize_text_hook"),
    "check_banned_phrases": ("backend.hooks.security", "check_banned_phrases_hook"),
    # Metrics & Analysis (use wrapper functions)
    "calculate_text_metrics": ("backend.hooks.metrics", "calculate_text_metrics_hook"),
    "calculate_control_ratio": ("backend.hooks.metrics", "calculate_control_ratio_hook"),
    # Linguistics
    "detect_performative_patterns": ("backend.hooks.linguistics", "detect_performative_patterns"),
    # Scoring
    "apply_scoring_logic": ("backend.hooks.scoring", "apply_scoring_logic"),
    # Archival
    "retrieve_precedent": ("backend.hooks.archival", "retrieve_precedent"),
    # References (use wrapper function)
    "generate_bibliography": ("backend.hooks.references", "generate_bibliography_hook"),
}


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

        # Hydration (Strict Object Mode)
        from backend.models.state import WorkflowState
        from backend.services.chat_log_parser import ChatLogParser

        # 1. Initialize State Object
        # We start by attempting to build a valid WorkflowState from inputs.
        # 1. Initialize State Object
        # Construct the valid dictionary structure for WorkflowState
        # "Strict Mode" means we align data to the Schema, not just dump it.
        state_payload = {}
        
        # A) Handle Inputs
        if "inputs" in initial_input:
            state_payload["inputs"] = initial_input["inputs"]
            # Copy other top-level keys if they match State fields (e.g. metadata?)
            for k, v in initial_input.items():
                if k != "inputs":
                    state_payload[k] = v
        else:
            # Assume flat inputs -> Map to InputData
            # STRICT MODE: We rely on InputData schema to define defaults for optional fields.
            # If mandatory fields (history_text) are missing, this WILL and SHOULD fail.
            state_payload["inputs"] = initial_input

        # B) Handle Execution ID
        if execution_id:
            state_payload["execution_id"] = execution_id
        elif "execution_id" not in state_payload:
            # Fallback if not provided in args OR payload (shouldn't happen via API)
            # Generate temporary ID for isolated runs
            import uuid
            state_payload["execution_id"] = str(uuid.uuid4())

        # C) Hydrate Metadata from Definition
        if definition.id:
            state_payload["workflow_id"] = definition.id
        if definition.name:
            state_payload["workflow_name"] = definition.name

        try:
            execution_state = WorkflowState(**state_payload)
        except Exception as e:
            # Check for Pydantic ValidationError
            # (We import Pydantic dynamically or assume it's available via models)
            from pydantic import ValidationError
            from backend.exceptions import AppException, ErrorCodes, status

            if isinstance(e, ValidationError):
                # Check if specific fields failed due to being empty
                for err in e.errors():
                    loc = err.get("loc", [])
                    msg = err.get("msg", "")
                    if (
                        ("history_text" in loc or "product_text" in loc or "reflection_text" in loc)
                        and ("least 1 character" in msg or "min_length" in err.get("type", ""))
                    ):
                         logger.warning(f"[GraphEngine] Empty input detected: {err}")
                         raise AppException(
                             message="Input fields cannot be empty.",
                             status_code=status.HTTP_400_BAD_REQUEST,
                             details={"error_code": ErrorCodes.EMPTY_INPUT}
                         ) from e

            logger.error(f"[GraphEngine] Invalid initial state: {e}")
            raise AppException(
                message=f"Invalid initial state structure: {e}",
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.INVALID_JSON_PAYLOAD, "original_error": str(e)}
            ) from e

        if execution_id and repository:
            try:
                # Attempt to hydrate from persistence
                record = await repository.get_execution(execution_id)
                if record and record.get("results"):
                    persisted_dict = record["results"]
                    if persisted_dict:
                        logger.info(f"[GraphEngine] Resuming execution {execution_id} from persisted state.")
                        
                        # Merge Strategy for Pydantic (copy + update)
                        # We dump current, update with persisted, re-validate.
                        current_dump = execution_state.model_dump()
                        current_dump.update(persisted_dict)
                        execution_state = WorkflowState(**current_dump)

            except Exception as e:
                # Non-fatal warning? Or strict fail?
                # "ilman fallbackkeja" suggests fail logic, but hydration failure is usually IO.
                # Let's log error but allow proceed if we have valid initial state?
                # User said "virhetilanteet vain valuerroreina".
                logger.warning(f"[GraphEngine] Failed to hydrate state for {execution_id}: {e}")
                # We do NOT fail here because we have a valid 'execution_state' from initial_input.

        # Jan 2026 Mandate: Centralized Chat Parsing / Sanitization
        # Access properties on the Object
        if execution_state.inputs:
            for field in ["history_text", "product_text", "reflection_text"]:
                val = getattr(execution_state.inputs, field, None)
                if val and isinstance(val, str) and ("chat" in field or "history" in field):
                     try:
                        original_len = len(val)
                        parsed_value = ChatLogParser.parse(val)
                        # Set back to object
                        setattr(execution_state.inputs, field, parsed_value)
                        
                        if len(parsed_value) != original_len:
                             logger.info(
                                 f"[GraphEngine] ChatLogParser optimized '{field}': "
                                 f"{original_len} -> {len(parsed_value)} chars"
                             )
                     except Exception as e:
                        logger.warning(f"[GraphEngine] ChatLogParser failed for '{field}': {e}")

        logger.info(f"Starting workflow '{definition.id}' with {len(definition.steps)} steps.")

        total_steps = len(definition.steps)
        for i, step in enumerate(definition.steps):
            # Idempotency Check
            if step.id in execution_state.step_results:
                logger.info(f"[GraphEngine] Skipping step '{step.id}' - result already exists in state.")
                continue

            # Graceful Cancellation Check
            if repository and execution_id:
                exec_status = await repository.get_execution_status(execution_id)
                if exec_status in ("cancelling", "cancelled"):
                    logger.info(f"[GraphEngine] Execution {execution_id} cancelled by user.")
                    # We can't set "status" on WorkflowState if it's not a field?
                    # WorkflowState DOES NOT have a 'status' field in the definition I saw earlier.
                    # It has 'step_results', 'aux_data'.
                    # Persistence layer handles 'status'.
                    # We interrupt here.
                    break

            try:
                # 0. HYDRATION (SSOT Pattern)
                if repository:
                    try:
                        library_step_data = await repository.get_step_by_id(step.id)
                        if library_step_data:
                            logger.debug(f"[GraphEngine] Hydrating step '{step.id}' from Registry (SSOT).")
                            if "task_key" in library_step_data:
                                step.task_key = library_step_data["task_key"]
                            
                            lib_config = library_step_data.get("config", {})
                            if not step.config:
                                step.config = lib_config
                            else:
                                merged = lib_config.copy()
                                merged.update(step.config)
                                step.config = merged
                    except Exception as e:
                         # Log but continue (Config Hydration is optional enhancement)
                         logger.warning(f"[GraphEngine] Step hydration failed for '{step.id}': {e}")

                # --- 0.5 PRE-HOOKS ---
                if step.config and "pre_hooks" in step.config:
                    pre_hooks = step.config["pre_hooks"]
                    if pre_hooks:
                        logger.debug(f"[GraphEngine] Executing Pre-Hooks for {step.id}: {pre_hooks}")
                        for hook in pre_hooks:
                            # Pass OBJECT directly
                            execution_state = await self._execute_hook(hook, execution_state, repository)

                # 1. Resolve Inputs
                # Check mapping against OBJECT
                task_inputs = self._resolve_inputs(step.inputs, execution_state)

                # 2. Get Task Handler
                task_def = TaskRegistry.get(step.task_key)
                if not task_def:
                    raise ValueError(f"Task '{step.task_key}' not found in registry (Hydrated Key: {step.task_key}).")

                # 3. Validate Inputs against Schema
                try:
                    validated_input = task_def.input_schema.model_validate(task_inputs)
                except Exception as e:
                    raise ValueError(f"Input validation failed for key '{step.task_key}': {e}") from e

                # 4. Execute Task
                logger.debug(f"Executing step '{step.id}' ({step.task_key})...")
                
                sig = inspect.signature(task_def.handler)

                if "execution_config" in sig.parameters or any(
                    p.kind == p.VAR_KEYWORD for p in sig.parameters.values()
                ):
                    result = await task_def.handler(validated_input, execution_config=step.config)
                else:
                    result = await task_def.handler(validated_input)

                # 5. Store Result
                # Store normalized result in step_results dict (Object field)
                if hasattr(result, "model_dump"):
                    state_val = result.model_dump()
                else:
                    state_val = result

                execution_state.step_results[step.id] = state_val
                
                # Update current_step_name on the Object if it exists
                if hasattr(execution_state, "current_step_name"):
                    execution_state.current_step_name = step.id

                logger.debug(f"Step '{step.id}' completed.")

                # --- 5.5 POST-HOOKS ---
                if step.config and "post_hooks" in step.config:
                    post_hooks = step.config["post_hooks"]
                    if post_hooks:
                        logger.debug(f"[GraphEngine] Executing Post-Hooks for {step.id}: {post_hooks}")
                        for hook in post_hooks:
                            execution_state = await self._execute_hook(hook, execution_state, repository)

                # 6. PERSISTENCE
                if repository and execution_id:
                    try:
                        # Dump state to dict for storage
                        state_dict = execution_state.model_dump()
                        
                        updates = {
                            "results": state_dict,
                            "current_step": step.id,
                            "current_step_name": step.id,
                            "current_step_index": i + 1,
                            "total_steps": total_steps,
                            "status": "running",
                        }

                        # Dynamic Hoisting
                        if step.hoist_keys:
                            for field in step.hoist_keys:
                                # We check the Step Result we just got
                                if hasattr(result, field):
                                     val = getattr(result, field)
                                elif isinstance(result, dict) and field in result:
                                     val = result[field]
                                else:
                                     val = None
                                
                                if val is not None:
                                    updates[field] = val

                        await repository.update_execution(execution_id, updates)
                        logger.debug(f"Persisted state after step '{step.id}'.")
                    except Exception as e:
                        logger.warning(f"Failed to persist intermediate state for {execution_id}: {e}")

            except Exception as e:
                error_code = "WORKFLOW_STEP_FAILED"
                logger.error(f"{error_code}: Workflow failed at step '{step.id}': {e}", exc_info=True)
                
                # Capture current state definition at failure
                failed_state_dump = execution_state.model_dump()
                
                raise WorkflowExecutionError(
                    step_id=step.id,
                    task_key=step.task_key,
                    original_error=e,
                    details={"execution_state": failed_state_dump, "error_code": error_code},
                ) from e

        logger.info(f"Workflow '{definition.id}' execution completed.")
        
        # Return Dict to maintain signature compatibility if callers expect dict
        # OR return WorkflowState if we updated signature.
        # Signature says: -> dict[str, Any]
        return execution_state.model_dump()

    async def _execute_hook(self, hook_name: str, state, repository: Any):
        """Executes a hook by name using the centralized HOOK_MAPPING.
        
        Args:
            hook_name: Name of the hook.
            state: WorkflowState OBJECT.
            
        Returns:
            WorkflowState: Updated state object.
        """
        # Type Check (Strict Mode)
        # We can't easily import WorkflowState for isinstance check due to circular imports?
        # But we trust the flow now.
        
        if hook_name not in HOOK_MAPPING:
            logger.warning(f"[GraphEngine] Hook '{hook_name}' not found in HOOK_MAPPING.")
            return state

        module_path, func_name = HOOK_MAPPING[hook_name]

        try:
            module = importlib.import_module(module_path)
            if not hasattr(module, func_name):
                msg = f"Hook Function '{func_name}' not found in module '{module_path}'"
                logger.error(f"[GraphEngine] {msg}")
                raise ValueError(msg)

            hook_func = getattr(module, func_name)

            # Inspect signature
            sig = inspect.signature(hook_func)
            kwargs = {}
            if "repository" in sig.parameters:
                kwargs["repository"] = repository

            # Execute (Async/Sync) - PASS OBJECT DIRECTLY
            if inspect.iscoroutinefunction(hook_func):
                result_state = await hook_func(state, **kwargs)
            else:
                result_state = hook_func(state, **kwargs)

            # Strict Check: Hook MUST return something
            if result_state is None:
                 raise ValueError(f"Hook '{hook_name}' returned None. Must return WorkflowState.")

            return result_state

        except Exception as e:
            logger.error(f"[GraphEngine] Hook '{hook_name}' failed: {e}", exc_info=True)
            # "Ilman fallbackkeja" -> If a hook fails, do we crash the workflow?
            # User said "virhetilanteet vain valuerroreina".
            # Raising ValueError here will bubble up and stop workflow.
            if isinstance(e, ValueError):
                raise e
            raise ValueError(f"Hook execution failed: {e}") from e

    def _resolve_inputs(self, input_mapping: dict[str, str], state) -> dict[str, Any]:
        """Resolve inputs from WorkflowState object."""
        resolved = {}
        for target_field, source_path in input_mapping.items():
            if isinstance(source_path, str) and source_path.startswith("$"):
                # Remove '$' and split by dot
                path_parts = source_path[1:].split(".")
                
                head = path_parts[0]
                tail = path_parts[1:]
                
                # 1. Access Attribute on State Object
                value = getattr(state, head, None)
                
                # 2. Fallback: Check step_results dict if head not found on main object
                # 2. Fallback: Check step_results dict if head not found on main object
                if value is None and hasattr(state, "step_results") and head in state.step_results:
                     value = state.step_results[head]
                
                if value is None:
                    # Still null?
                    resolved[target_field] = None
                    continue

                # TRAVERSE TAIL
                try:
                    for part in tail:
                        if isinstance(value, dict):
                            value = value.get(part)
                        else:
                            value = getattr(value, part, None)

                        if value is None:
                            break
                    resolved[target_field] = value
                except Exception as e:
                     raise ValueError(f"Resolution failed for path '{source_path}': {e}")
            else:
                # Static value
                resolved[target_field] = source_path
        return resolved
