import importlib
import inspect
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from backend.core.registry import TaskRegistry
from backend.exceptions import WorkflowExecutionError
from backend.models.state import ReasoningTrace, TraceEvent, WorkflowState
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
    # Passiveness Cutter (Strict Penalty)
    "enforce_passivity_penalty": ("backend.hooks.scoring", "enforce_passivity_penalty"),
}


class GraphEngine:
    """Metadata-driven workflow engine (Event Sourcing Edition).
    Executes workflows defined by WorkflowDefinition using the TaskRegistry.
    Uses append-only TraceEvent log for state management.
    """

    def __init__(self):
        """Initialize the GraphEngine."""
        from backend.core.registry import TaskRegistry
        self.registry = TaskRegistry

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
            The final execution state model dump.
        """
        from backend.services.chat_log_parser import ChatLogParser

        # 1. Initialize State Object
        # "Strict Mode" means we align data to the Schema, not just dump it.

        # Context Variables Initialization
        context_vars = {}
        if "inputs" in initial_input:
            context_vars["inputs"] = initial_input["inputs"]
            for k, v in initial_input.items():
                if k != "inputs":
                    context_vars[k] = v
        else:
            context_vars["inputs"] = initial_input

        # Cast for mypy strictness
        state_payload: dict[str, Any] = {
            "execution_id": uuid.UUID(execution_id) if execution_id else uuid.uuid4(),
            "workflow_id": definition.id if definition.id else "unknown_workflow",
            "status": "running",
            "execution_trace": [],
            "context_variables": context_vars
        }

        try:
            execution_state = WorkflowState(**state_payload)
        except Exception as e:
            from backend.exceptions import AppException, ErrorCodes, status

            logger.error(f"[GraphEngine] Invalid initial state: {e}")
            raise AppException(
                message=f"Invalid initial state structure: {e}",
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.INVALID_JSON_PAYLOAD, "original_error": str(e)},
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
                        current_dump = execution_state.model_dump()
                        current_dump.update(persisted_dict)
                        # Re-instantiate to validate
                        execution_state = WorkflowState(**current_dump)
            except Exception as e:
                logger.warning(f"[GraphEngine] Failed to hydrate state for {execution_id}: {e}")

        # Jan 2026 Mandate: Chat Parsing / Sanitization (on context_variables)
        inputs = execution_state.context_variables.get("inputs")
        if inputs and isinstance(inputs, dict):  # Check if inputs is a dict
            for field in ["history_text", "product_text", "reflection_text"]:
                val = inputs.get(field)
                if val and isinstance(val, str) and ("chat" in field or "history" in field):
                    try:
                        original_len = len(val)
                        parsed_value = ChatLogParser.parse(val)
                        # Set back to dict
                        inputs[field] = parsed_value

                        if len(parsed_value) != original_len:
                            logger.info(
                                f"[GraphEngine] ChatLogParser optimized '{field}': "
                                f"{original_len} -> {len(parsed_value)} chars"
                            )
                    except Exception as e:
                        logger.warning(f"[GraphEngine] ChatLogParser failed for '{field}': {e}")
            execution_state.context_variables["inputs"] = inputs  # Update back

        logger.info(f"Starting workflow '{definition.id}' with {len(definition.steps)} steps.")

        # Track executed steps to avoid duplicates in append-only log?
        # Actually Event Sourcing usually allows re-runs, but here we probably want to skip if already done.
        executed_step_names = {
            event.step_name
            for event in execution_state.execution_trace
            if event.event_type == "output"  # Only count successful outputs
        }

        for _, step in enumerate(definition.steps):
            # Idempotency Check
            if step.id in executed_step_names:
                logger.info(f"[GraphEngine] Skipping step '{step.id}' - event already exists in trace.")
                continue

            # Graceful Cancellation Check
            if repository and execution_id:
                exec_status = await repository.get_execution_status(execution_id)
                if exec_status in ("cancelling", "cancelled"):
                    logger.info(f"[GraphEngine] Execution {execution_id} cancelled by user.")
                    break

            try:
                # 0. HYDRATION (SSOT Pattern)
                if repository:
                    try:
                        library_step_data = await repository.get_step_by_id(step.id)
                        if library_step_data:
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
                        logger.warning(f"[GraphEngine] Step hydration failed for '{step.id}': {e}")

                # --- 0.5 PRE-HOOKS ---
                if step.config and "pre_hooks" in step.config:
                    pre_hooks = step.config["pre_hooks"]
                    if pre_hooks:
                        logger.debug(f"[GraphEngine] Executing Pre-Hooks for {step.id}: {pre_hooks}")
                        for hook in pre_hooks:
                            execution_state = await self._execute_hook(hook, execution_state, repository)

                # 1. Resolve Inputs
                task_inputs = self._resolve_inputs(step.inputs, execution_state)

                # 2. Get Task Handler
                task_def = TaskRegistry.get(step.task_key)
                if not task_def:
                    raise ValueError(f"Task '{step.task_key}' not found in registry.")

                # 3. Validate Inputs against Schema
                try:
                    # Logic to allow "Thinking Tokens" if model supports it?
                    # For now, just standard validation.
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

                # 5. Extract Reasoning & Content (Event Sourcing Magic)
                # Check for "thinking" or "reasoning" fields in result (dict or object)
                reasoning_trace = None
                content_payload = {}

                # Convert result to dict for inspection
                if hasattr(result, "model_dump"):
                    result_dict = result.model_dump()
                elif isinstance(result, dict):
                    result_dict = result
                else:
                    result_dict = {"raw_output": str(result)}

                # Extraction Logic
                # We prioritize specific keys for reasoning
                reasoning_keys = ["thinking", "reasoning", "chain_of_thought", "reasoning_trace"]

                found_reasoning = {}
                for key in reasoning_keys:
                    if key in result_dict and result_dict[key]:
                        val = result_dict.pop(key)  # Remove from content
                        found_reasoning[key] = val

                if found_reasoning:
                    # Construct ReasoningTrace
                    # If we found multiple, join them or pick best?
                    # Let's assume the first non-empty one is the main thought process
                    primary_thought = next(iter(found_reasoning.values()))
                    # If it's a string, use it. If dict, dump it.
                    thought_str = str(primary_thought) if not isinstance(primary_thought, str) else primary_thought

                    reasoning_trace = ReasoningTrace(
                        thought_process=thought_str,
                        conclusion="See content",  # Implicit
                        confidence_score=1.0,  # Default
                        model_name=step.config.get("model", "unknown") if step.config else None,
                    )

                content_payload = result_dict

                # 6. Create TraceEvent
                new_event = TraceEvent(
                    step_name=step.id,
                    event_type="output",
                    content=content_payload,
                    reasoning=reasoning_trace,
                    metadata={"task_key": step.task_key, "timestamp": datetime.now(timezone.utc).isoformat()},
                )

                # 7. Append Event to State (Functional Update)
                execution_state = execution_state.add_event(new_event)

                # 8. Update Context Variables (Snapshot for next steps)
                # We merge the content_payload into context_variables[step.id]
                execution_state.context_variables[step.id] = content_payload

                logger.debug(f"Step '{step.id}' event added to trace.")

                # --- 8.1 CONDITIONAL STOP / EARLY EXIT ---
                # Check for explicit stop signals in the payload
                stop_signal = False
                stop_reason = ""

                # 1. Generic Flag
                if content_payload.get("stop_execution") is True:
                    stop_signal = True
                    stop_reason = f"Generic Stop Signal from '{step.id}'"

                # 2. GuardAgent Specific
                # Structure: content_payload = { "security_check": { "threat_detected": bool, ... }, ... }
                sec_check = content_payload.get("security_check")
                if isinstance(sec_check, dict) and sec_check.get("threat_detected") is True:
                    stop_signal = True
                    stop_reason = f"Security Threat Detected by '{step.id}'"
                
                if stop_signal:
                    logger.warning(f"[GraphEngine] 🛑 HALTING EXECUTION: {stop_reason}")
                    execution_state = execution_state.model_copy(update={"status": "stopped"})
                    # Stop the loop
                    break

                # --- 8.5 POST-HOOKS ---
                if step.config and "post_hooks" in step.config:
                    post_hooks = step.config["post_hooks"]
                    if post_hooks:
                        logger.debug(f"[GraphEngine] Executing Post-Hooks for {step.id}: {post_hooks}")
                        for hook in post_hooks:
                            execution_state = await self._execute_hook(hook, execution_state, repository)

                # 9. PERSISTENCE
                if repository and execution_id:
                    try:
                        # Dump state to dict for storage
                        state_dict = execution_state.model_dump()

                        updates = {
                            "results": state_dict,
                            "current_step": step.id,
                            "execution_trace_count": len(execution_state.execution_trace),
                            "status": "running",
                        }

                        # Dynamic Hoisting (Legacy Support?)
                        if step.hoist_keys:
                            for field in step.hoist_keys:
                                if field in content_payload:
                                    updates[field] = content_payload[field]

                        await repository.update_execution(execution_id, updates)
                    except Exception as e:
                        logger.warning(f"Failed to persist state for {execution_id}: {e}")

            except Exception as e:
                error_code = "WORKFLOW_STEP_FAILED"
                logger.error(f"{error_code}: Workflow failed at step '{step.id}': {e}", exc_info=True)

                # Create Error Event
                error_event = TraceEvent(
                    step_name=step.id,
                    event_type="error",
                    content={"error": str(e), "code": error_code},
                    metadata={"timestamp": datetime.now(timezone.utc).isoformat()},
                )
                execution_state = execution_state.add_event(error_event)

                failed_state_dump = execution_state.model_dump(mode='json')
                raise WorkflowExecutionError(
                    step_id=step.id,
                    task_key=step.task_key,
                    original_error=e,
                    details={"execution_state": failed_state_dump, "error_code": error_code},
                ) from e

        # Final Status Update
        if execution_state.status == "running":
            execution_state = execution_state.model_copy(update={"status": "completed"})

        logger.info(f"Workflow '{definition.id}' execution completed. Final Status: {execution_state.status}")
        return execution_state.model_dump()

    async def _execute_hook(self, hook_name: str, state: WorkflowState, repository: Any) -> WorkflowState:
        """Executes a hook by name using the centralized HOOK_MAPPING.

        Args:
            hook_name: Name of the hook.
            state: WorkflowState OBJECT.

        Returns:
            WorkflowState: Updated state object.
        """
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
            sig = inspect.signature(hook_func)
            kwargs = {}
            if "repository" in sig.parameters:
                kwargs["repository"] = repository

            if inspect.iscoroutinefunction(hook_func):
                result_state = await hook_func(state, **kwargs)
            else:
                result_state = hook_func(state, **kwargs)

            if result_state is None:
                raise ValueError(f"Hook '{hook_name}' returned None. Must return WorkflowState.")

            return result_state

        except Exception as e:
            logger.error(f"[GraphEngine] Hook '{hook_name}' failed: {e}", exc_info=True)
            if isinstance(e, ValueError):
                raise e
            raise ValueError(f"Hook execution failed: {e}") from e

    def _resolve_inputs(self, input_mapping: dict[str, str], state: WorkflowState) -> dict[str, Any]:
        """Resolve inputs from WorkflowState object (using context_variables)."""
        resolved: dict[str, Any] = {}
        for target_field, source_path in input_mapping.items():
            if isinstance(source_path, str) and source_path.startswith("$"):
                # Remove '$' and split by dot
                path_parts = source_path[1:].split(".")

                head = path_parts[0]
                tail = path_parts[1:]

                # Check context_variables first (The Snapshot)
                value = state.context_variables.get(head)

                # Fallback: inputs is often in context_variables["inputs"]
                if value is None and head == "inputs":
                    value = state.context_variables.get("inputs")

                # Fallback: Check if head is a property of state (e.g. execution_id)
                if value is None and hasattr(state, head):
                    value = getattr(state, head)

                if value is None:
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
