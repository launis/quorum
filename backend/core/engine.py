import importlib
import inspect
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel

from backend.core.registry import TaskRegistry
from backend.exceptions import AppException, ErrorCodes, WorkflowExecutionError, status
from backend.models.domain.inputs import WorkflowInputs
from backend.models.state import ReasoningTrace, TraceEvent, WorkflowState
from backend.models.workflow import WorkflowDefinition
from backend.utils.pydantic_utils import inflate

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
    "calculate_control_ratio": ("backend.hooks.metrics", "calculate_text_metrics_hook"),
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
    # Integrity & Linking
    "verify_citation_integrity": ("backend.hooks.integrity", "verify_citation_integrity"),
    "enforce_hypothesis_linking": ("backend.hooks.integrity", "enforce_hypothesis_linking"),
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
            "context_variables": context_vars,
        }

        try:
            execution_state = WorkflowState(**state_payload)
        except Exception as e:
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
                if record and record.results:
                    # Handle results (model or dict)
                    if hasattr(record.results, "model_dump"):
                        persisted_dict = record.results.model_dump()
                    else:
                        persisted_dict = record.results

                    if persisted_dict:
                        logger.info(f"[GraphEngine] Resuming execution {execution_id} from persisted state.")

                        # Merge Strategy for Pydantic (copy + update)
                        current_dump = execution_state.model_dump()
                        current_dump.update(persisted_dict)
                        # Re-instantiate to validate
                        execution_state = WorkflowState(**current_dump)
            except Exception as e:
                logger.warning(f"[GraphEngine] Failed to hydrate state for {execution_id}: {e}")

        # Jan 2026 Mandate: Strict Input Inflation & Sanitization
        inputs_data = execution_state.context_variables.get("inputs")

        # 1. Inflate to Model (Fail Fast)
        if inputs_data:
            inputs_model = inflate(inputs_data, WorkflowInputs)
            if not inputs_model:
                # If raw data exists but fails validation -> CRITICAL INTEGRITY ERROR
                error_code = ErrorCodes.INVALID_JSON_PAYLOAD
                msg = f"Invalid WorkflowInputs data. Failed to inflate {type(inputs_data)}."
                logger.error(f"[GraphEngine] {error_code}: {msg}")
                raise AppException(message=msg, status_code=400, details={"error_code": error_code})

            # 2. Chat Parsing / Sanitization (on Model Fields)
            updates = {}
            for field in ["history_text", "product_text", "reflection_text"]:
                val = getattr(inputs_model, field, None)
                if val and isinstance(val, str) and ("chat" in field or "history" in field):
                    # Strict: No Fallback for invalid chat logs.
                    try:
                        original_len = len(val)
                        parsed_value = ChatLogParser.parse(val)

                        if parsed_value != val:
                            updates[field] = parsed_value
                            if len(parsed_value) != original_len:
                                logger.info(
                                    f"[GraphEngine] ChatLogParser optimized '{field}': "
                                    f"{original_len} -> {len(parsed_value)} chars"
                                )
                    except Exception as e:
                        # Fail Fast: Invalid Chat Log is a data integrity error.
                        logger.error(f"[GraphEngine] ChatLogParser failed for '{field}': {e}")
                        raise AppException(
                            message=f"Chat Log Parsing failed for field '{field}': {e}",
                            status_code=status.HTTP_400_BAD_REQUEST,
                            details={
                                "error_code": ErrorCodes.INVALID_JSON_PAYLOAD,
                                "field": field,
                                "original_error": str(e),
                            },
                        ) from e

            # 3. Apply Updates & Store Model
            if updates:
                inputs_model = inputs_model.model_copy(update=updates)

            execution_state.context_variables["inputs"] = inputs_model

        logger.info(f"Starting workflow '{definition.id}' with {len(definition.steps)} steps.")

        # Track executed steps to avoid duplicates in append-only log?
        # Actually Event Sourcing usually allows re-runs, but here we probably want to skip if already done.
        executed_step_names = {
            event.step_name
            for event in execution_state.execution_trace
            if event.event_type == "output"  # Only count successful outputs
        }

        for _, step_id in enumerate(definition.steps):
            if not isinstance(step_id, str):
                logger.error(
                    f"[GraphEngine] Invalid step type in workflow {definition.id}: Expected str, got {type(step_id)}"
                )
                continue

            # Idempotency Check
            if step_id in executed_step_names:
                logger.info(f"[GraphEngine] Skipping step '{step_id}' - event already exists in trace.")
                continue

            # Graceful Cancellation Check
            if repository and execution_id:
                exec_status = await repository.get_execution_status(execution_id)
                if exec_status in ("cancelling", "cancelled"):
                    logger.info(f"[GraphEngine] Execution {execution_id} cancelled by user.")
                    execution_state = execution_state.model_copy(update={"status": exec_status})
                    break

            try:
                # 0. HYDRATION (Hyper-Strict SSOT)
                canonical_step = None
                if repository:
                    try:
                        canonical_step = await repository.get_step_by_id(step_id)
                    except Exception as e:
                        logger.warning(f"[GraphEngine] Step fetch failed for '{step_id}': {e}")

                if not canonical_step:
                    logger.error(
                        f"[GraphEngine] Step '{step_id}' not found in Registry. Rejecting due to Zero-Fallback mandate."
                    )
                    raise WorkflowExecutionError(
                        step_id=step_id,
                        task_key="unknown",
                        original_error=ValueError(f"Step {step_id} completely missing from canonical registry"),
                        details={"message": "Strict Hydration failed: Missing Canonical Step"},
                    )

                # We copy canonical to avoid mutating cache/db result
                merged = canonical_step.copy()

                if "task_key" not in merged:
                    merged["task_key"] = merged.get("component", "unknown")
                if "id" not in merged:
                    merged["id"] = step_id

                from backend.models.workflow import WorkflowStep

                try:
                    step = WorkflowStep.model_validate(merged)
                except Exception as e:
                    logger.error(
                        f"[GraphEngine] Failed to properly validate step '{step_id}': {e}. Rejecting due to Zero-Fallback mandate."
                    )
                    raise WorkflowExecutionError(
                        step_id=step_id,
                        task_key=merged.get("task_key", "unknown"),
                        original_error=e,
                        details={"message": "Step validation failed against strict SSOT Schema (Zero-Fallback)"},
                    ) from e

                # --- 0.5 PRE-HOOKS ---
                if step.config and "pre_hooks" in step.config:
                    pre_hooks = step.config["pre_hooks"]
                    if pre_hooks:
                        logger.debug(f"[GraphEngine] Executing Pre-Hooks for {step.id}: {pre_hooks}")
                        for hook in pre_hooks:
                            execution_state = await self._execute_hook(hook, execution_state, repository)

                # 1. Get Task Handler First (to access schema)
                task_def = TaskRegistry.get(step.task_key)
                if not task_def:
                    raise AppException(
                        message=f"Task '{step.task_key}' not found in registry.",
                        status_code=status.HTTP_404_NOT_FOUND,
                        details={"error_code": ErrorCodes.TASK_NOT_FOUND, "task_key": step.task_key},
                    )

                # 2. Resolve Inputs (with Strict Schema Awareness)
                task_inputs = self._resolve_inputs(step.inputs, execution_state, input_schema=task_def.input_schema)

                # 3. Validate Inputs against Schema
                try:
                    # Logic to allow "Thinking Tokens" if model supports it?
                    # For now, just standard validation.
                    validated_input = task_def.input_schema.model_validate(task_inputs)
                except Exception as e:
                    raise AppException(
                        message=f"Input validation failed for key '{step.task_key}': {e}",
                        status_code=status.HTTP_400_BAD_REQUEST,
                        details={"error_code": ErrorCodes.AGENT_SCHEMA_VALIDATION_FAILED, "original_error": str(e)},
                    ) from e

                # 3.5 Inject Runtime Context (Identity & Governance)
                # Ensure agents have access to Organization ID even if not explicitly mapped in inputs.
                runtime_config = step.config.copy() if step.config else {}

                # 1. Try from explicit inputs
                current_inputs = execution_state.context_variables.get("inputs")
                if current_inputs:
                    if hasattr(current_inputs, "organization_id") and current_inputs.organization_id:
                        runtime_config["organization_id"] = current_inputs.organization_id
                    elif isinstance(current_inputs, dict) and "organization_id" in current_inputs:
                        runtime_config["organization_id"] = current_inputs["organization_id"]

                    if hasattr(current_inputs, "user_id") and current_inputs.user_id:
                        runtime_config["user_id"] = current_inputs.user_id
                    elif isinstance(current_inputs, dict) and "user_id" in current_inputs:
                        runtime_config["user_id"] = current_inputs["user_id"]

                # 2. Try from root workflow state (properties reading context_variables)
                if "organization_id" not in runtime_config and execution_state.organization_id:
                    runtime_config["organization_id"] = execution_state.organization_id
                
                if "user_id" not in runtime_config and execution_state.user_id:
                    runtime_config["user_id"] = execution_state.user_id

                runtime_config["workflow"] = execution_state.workflow_id
                runtime_config["execution_id"] = execution_id
                runtime_config["step_id"] = step.id

                # 4. Execute Task
                logger.debug(f"Executing step '{step.id}' ({step.task_key})...")

                sig = inspect.signature(task_def.handler)
                if "execution_config" in sig.parameters or any(
                    p.kind == p.VAR_KEYWORD for p in sig.parameters.values()
                ):
                    result = await task_def.handler(validated_input, execution_config=runtime_config)
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

                # Extract Usage via Pydantic Metadata (Domain models)
                step_usage = {}
                if hasattr(result, "metadata") and getattr(result, "metadata", None) is not None:
                    if hasattr(result.metadata, "token_usage") and result.metadata.token_usage:
                        step_usage = result.metadata.token_usage

                # Fallbacks for dictionary responses or legacy reasoning objects
                if not step_usage and "metadata" in result_dict and isinstance(result_dict["metadata"], dict):
                    step_usage = result_dict["metadata"].get("token_usage", {})
                if not step_usage:
                    step_usage = result_dict.pop("token_usage", {})

                if not isinstance(step_usage, dict):
                    step_usage = {}

                if reasoning_trace:
                    reasoning_trace = reasoning_trace.model_copy(update={"token_usage": step_usage})

                # Global Usage Accumulation
                global_usage = execution_state.context_variables.setdefault("usage", {})
                global_usage["total_tokens"] = global_usage.get("total_tokens", 0) + step_usage.get("total_tokens", 0)
                global_usage["prompt_tokens"] = global_usage.get("prompt_tokens", 0) + step_usage.get(
                    "prompt_tokens", 0
                )
                global_usage["completion_tokens"] = global_usage.get("completion_tokens", 0) + step_usage.get(
                    "completion_tokens", 0
                )

                if "cost_usd" in step_usage:
                    global_usage["cost_usd"] = global_usage.get("cost_usd", 0.0) + step_usage.get("cost_usd", 0.0)

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

                        step_updates: dict[str, Any] = {
                            "results": state_dict,
                            "current_step": step.id,
                            "execution_trace_count": len(execution_state.execution_trace),
                            "status": "running",
                        }

                        await repository.update_execution(execution_id, step_updates)
                    except Exception as e:
                        logger.warning(f"Failed to persist state for {execution_id}: {e}")

            except AppException as ae:
                # Specific Application Error (Fail Fast)
                safe_step_id = step.id if "step" in locals() else step_id
                logger.error(f"{ae.error_code}: Workflow failed at step '{safe_step_id}': {ae.message}", exc_info=True)

                # Create Error Event
                error_event = TraceEvent(
                    step_name=safe_step_id,
                    event_type="error",
                    content={"error": ae.message, "code": ae.error_code},
                    metadata={"timestamp": datetime.now(timezone.utc).isoformat()},
                )
                try:
                    execution_state = execution_state.add_event(error_event)
                except Exception:
                    pass  # Fallback if adding event fails

                # Check if we should re-raise or wrap?
                # If it's already an AppException, re-raising preserves the code.
                raise ae

            except Exception as e:
                string_code = "WORKFLOW_STEP_FAILED"
                safe_step_id = step.id if "step" in locals() else step_id
                logger.error(f"{string_code}: Workflow failed at step '{safe_step_id}': {e}", exc_info=True)

                # Create Error Event
                error_event = TraceEvent(
                    step_name=safe_step_id,
                    event_type="error",
                    content={"error": str(e), "code": string_code},
                    metadata={"timestamp": datetime.now(timezone.utc).isoformat()},
                )
                try:
                    execution_state = execution_state.add_event(error_event)
                except Exception:
                    pass

                failed_state_dump = execution_state.model_dump(mode="json")
                safe_task_key = step.task_key if "step" in locals() else "unknown"
                raise WorkflowExecutionError(
                    step_id=safe_step_id,
                    task_key=safe_task_key,
                    original_error=e,
                    details={"execution_state": failed_state_dump, "error_code": string_code},
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
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    details={"error_code": ErrorCodes.HOOK_EXECUTION_FAILED},
                )

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
                raise AppException(
                    message=f"Hook '{hook_name}' returned None. Must return WorkflowState.",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    details={"error_code": ErrorCodes.HOOK_EXECUTION_FAILED},
                )

            return result_state

        except Exception as e:
            logger.error(f"[GraphEngine] Hook '{hook_name}' failed: {e}", exc_info=True)
            if isinstance(e, AppException):
                raise e
            raise AppException(
                message=f"Hook execution failed: {e}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.HOOK_EXECUTION_FAILED, "original_error": str(e)},
            ) from e

    def _resolve_inputs(
        self, input_mapping: dict[str, str], state: WorkflowState, input_schema: type[BaseModel] | None = None
    ) -> dict[str, Any]:
        """Resolve inputs from WorkflowState object (using context_variables).

        Refactored Feb 2026: Supports 'Strict Typed Retrieval' via state.get_context(Model).
        If input_schema is provided, we attempt to inflate the context variable
        into the expected Pydantic model *before* returning it.
        """
        resolved: dict[str, Any] = {}

        # Helper to resolve type from schema
        def _get_field_type(field_name: str) -> type[BaseModel] | None:
            if not input_schema:
                return None
            field_info = input_schema.model_fields.get(field_name)
            if not field_info:
                return None

            # Inspect annotation
            annotation = field_info.annotation
            if not annotation:
                return None

            # Handle Optional[model], Union[model, None], etc.
            # Simple heuristic: if it's a subclass of BaseModel, use it.
            # Iterate args if generic.
            import inspect
            from typing import get_args, get_origin

            # Direct match
            if inspect.isclass(annotation) and issubclass(annotation, BaseModel):
                return annotation

            # Optional/Union match
            origin = get_origin(annotation)
            if origin:
                for arg in get_args(annotation):
                    if inspect.isclass(arg) and issubclass(arg, BaseModel):
                        return arg

            return None

        for target_field, source_path in input_mapping.items():
            if isinstance(source_path, str) and source_path.startswith("$"):
                # Remove '$' and split by dot
                path_parts = source_path[1:].split(".")

                head = path_parts[0]
                tail = path_parts[1:]

                # Determine expected type for this root object?
                # Usually we map root-to-root (e.g. step_analyst -> $analyst_step)
                # If we map root-to-prop (e.g. text -> $analyst.summary), we can't easily infer the type of $analyst
                # unless we know the schema of the SOURCE, which we don't here.
                # We only know the schema of the TARGET.

                # However, if target_field strictly expects a Model, we should try to get it as such.
                expected_model = _get_field_type(target_field) if not tail else None

                # Fetch from State (Typed if possible and no tail traversal needed)
                if expected_model and not tail:
                    # Strict Retrieval: logic to inflate Pydantic models from context dicts
                    value = state.get_context(head, model_class=expected_model)
                else:
                    # Generic Retrieval
                    value = state.get_context(head)

                # Fallback: Check if head is a property of state
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
                            # If it's a Pydantic model, use getattr
                            value = getattr(value, part)
                    resolved[target_field] = value
                except Exception as e:
                    raise AppException(
                        message=f"Resolution failed for path '{source_path}': {e}",
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        details={"error_code": ErrorCodes.INPUT_RESOLUTION_FAILED, "original_error": str(e)},
                    )
            else:
                # Static value
                resolved[target_field] = source_path
        return resolved
