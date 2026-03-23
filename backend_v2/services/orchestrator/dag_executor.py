"""Asynchronous Directed Acyclic Graph (DAG) Executor for V3 Workflows.

Strictly follows Event Sourcing, Fail-Fast principles (RFC 7807) and O(1) Concurrency.
God object refactored into: DAGOrchestrator, NodeExecutor, ExecutionCommitter.
"""

import asyncio
import logging
from typing import Any

from backend_v2.core.hook_registry import HookDependencies, HookState, hook_registry
from backend_v2.database.repository import AbstractWorkflowRepository
from backend_v2.exceptions import AppException, ErrorCodes, WorkflowExecutionError
from backend_v2.llm.client import LLMClient
from backend_v2.models.state import ErrorTraceEvent, StateProjector, TraceEvent
from backend_v2.models.v2_core import (
    ExecutionRecord,
    ExecutionStatus,
    ExecutionStepState,
    FrozenContext,
    StepRule,
    Workflow,
    WorkflowInputs,
)
from backend_v2.utils.dict_utils import deep_merge_dicts

logger = logging.getLogger(__name__)


class ExecutionCommitter:
    """Handles Checkpointing of the Event Sourced Trace."""

    def __init__(self, repository: AbstractWorkflowRepository, execution_id: str):
        self.repository = repository
        self.execution_id = execution_id

    async def commit_trace(
        self,
        trace: list[TraceEvent],
        status: ExecutionStatus,
        step_states: dict[str, ExecutionStepState],
        error: str | None = None
    ) -> None:
        """Flushes the event array to persistent DB safely."""
        try:
            payload: dict[str, Any] = {
                "status": status.value,
                "execution_trace": [e.model_dump(mode="json") for e in trace],
                "step_states": {k: v.model_dump(mode="json") for k, v in step_states.items()}
            }
            if error:
                payload["error"] = error

            # The repository natively handles 100KB+ offloading to Blob storage via _offload_payloads()
            await self.repository.update_execution(self.execution_id, payload)
        except Exception as e:
            msg = f"Failed to commit execution trace for {self.execution_id}"
            logger.error(f"[ExecutionCommitter] {ErrorCodes.PROGRESS_UPDATE_FAILED.name}: {msg}", exc_info=True)
            raise AppException(
                message=msg,
                details={"error_code": ErrorCodes.PROGRESS_UPDATE_FAILED},
                status_code=500
            ) from e


class NodeExecutor:
    """Executes a single step in pure isolation, emitting TraceEvents."""

    def __init__(self, repository: AbstractWorkflowRepository, prompt_compiler: Any):
        self.repository = repository
        self.compiler = prompt_compiler

    async def execute(
        self,
        step: StepRule,
        execution_id: str,
        workflow_id: str,
        metadata: dict[str, Any],
        projector: StateProjector,
        expected_inputs: list[Any] | None = None,
        frozen_ctx: FrozenContext | None = None,
        trace: list[TraceEvent] | None = None
    ) -> list[TraceEvent]:
        emitted_events: list[TraceEvent] = []
        try:
            # 1. State extraction (Immutable isolation point)
            current_state = dict(projector.snapshot)

            blueprint_slug = getattr(step, "task_blueprint", None)
            if not blueprint_slug:
                raise AppException(
                    message=f"Step {step.id} has no task_blueprint configured.",
                    status_code=500,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR}
                )

            step_def = await self.repository.get_step_by_id(blueprint_slug)
            if not step_def:
                raise AppException(
                    message=f"Configuration error: Step '{blueprint_slug}' not found.",
                    status_code=500,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR}
                )

            hook_deps = HookDependencies(repository=self.repository)

            # --- NATIVE LOGIC NODE EXECUTION ---
            if step_def.get("type", "llm") == "logic":
                logic_hook = step_def.get("hook", None)
                if not logic_hook:
                    raise AppException(
                        message=f"Logic step '{blueprint_slug}' has no native hook defined.",
                        status_code=500,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED}
                    )

                # Execute synchronous heavy hooks securely wrapped in to_thread!
                async def run_logic() -> dict[str, Any]:
                    state_data = dict(current_state)
                    hook_state = HookState(
                        execution_id=execution_id,
                        workflow_id=workflow_id,
                        step_id=step.id,
                        task_blueprint=blueprint_slug,
                        metadata=metadata,
                        inputs=state_data
                    )

                    # Pre-hooks
                    for pre_hook in step_def.get("pre_hooks", []):
                        res = await hook_registry.execute(pre_hook, hook_state, hook_deps)
                        if res.success and res.state_delta:
                            state_data = deep_merge_dicts(state_data, res.state_delta)
                            hook_state = hook_state.model_copy(update={"inputs": state_data})

                    # Main logic hook
                    is_async = asyncio.iscoroutinefunction(hook_registry.execute)
                    if not is_async:
                        main_res = await asyncio.to_thread(
                            asyncio.run, hook_registry.execute(logic_hook, hook_state, hook_deps)
                        )
                    else:
                        main_res = await hook_registry.execute(logic_hook, hook_state, hook_deps)

                    if main_res.success and main_res.state_delta:
                        state_data = deep_merge_dicts(state_data, main_res.state_delta)
                        hook_state = hook_state.model_copy(update={"inputs": state_data})

                    # Post-hooks
                    from backend_v2.models.v2_core import Step as V2Step
                    step_obj = V2Step.model_validate(step_def)
                    combined_post_hooks = list(dict.fromkeys(step_obj.post_hooks + step.post_hooks))
                    for post_hook in combined_post_hooks:
                        res = await hook_registry.execute(post_hook, hook_state, hook_deps)
                        if res.success and res.state_delta:
                            state_data = deep_merge_dicts(state_data, res.state_delta)
                            hook_state = hook_state.model_copy(update={"inputs": state_data})

                    return state_data

                final_outputs = await run_logic()
                emitted_events.append(TraceEvent(
                    step_name=step.id,
                    event_type="output",
                    content=final_outputs
                ))
                return emitted_events

            # --- LLM NODE EXECUTION ---
            else:
                from backend_v2.models.v2_core import Step as V2Step
                step_obj = V2Step.model_validate(step_def)
                state_data = dict(current_state)
                hook_state = HookState(
                    execution_id=execution_id,
                    workflow_id=workflow_id,
                    step_id=step.id,
                    task_blueprint=blueprint_slug,
                    metadata=metadata,
                    inputs=state_data
                )

                # Pre-Hooks
                combined_pre_hooks = list(dict.fromkeys(step_obj.pre_hooks + step.pre_hooks))
                for pre_hook in combined_pre_hooks:
                    res = await hook_registry.execute(pre_hook, hook_state, hook_deps)
                    if res.success and res.state_delta:
                        state_data = deep_merge_dicts(state_data, res.state_delta)
                        hook_state = hook_state.model_copy(update={"inputs": state_data})

                # Compile LLM Prompts & Schemas
                criteria_blocks = []
                all_prompt_blocks = await self.repository.get_all_prompt_blocks()
                block_map = {b["id"]: b for b in all_prompt_blocks if "id" in b}
                for m_id in step_obj.prompt_blocks:
                    b = block_map.get(m_id)
                    if b:
                        criteria_blocks.append(b)
                    else:
                        raise AppException(
                            message=f"PromptBlock '{m_id}' not found.",
                            status_code=500,
                            details={"error_code": ErrorCodes.VALIDATION_FAILED}
                        )

                target_locale = metadata.get("target_locale", "en")
                static_instructions = self.compiler.compile_static_instructions(criteria_blocks, target_locale)
                dynamic_instructions = self.compiler.compile_dynamic_instructions(criteria_blocks, target_locale)

                system_prompt = "Complete the evaluation according to the provided schema."
                if static_instructions:
                    system_prompt += f"\n\n{static_instructions}"

                # P4: Prevent Token Explosion with fold_trace pruning
                llm_context_data = state_data
                if trace:
                    from backend_v2.models.state import StateProjector
                    pruner = StateProjector()
                    pruned_history = pruner.fold_trace(trace, max_tokens=20000)
                    # Merge active hook deltas with pruned history
                    llm_context_data = {**pruned_history, **state_data}

                xml_ctx = self.compiler.build_xml_context(
                    input_mappings=step.input_mappings if hasattr(step, "input_mappings") else {},
                    state_data=llm_context_data,
                    target_locale=target_locale,
                    expected_inputs=expected_inputs
                )

                user_payload = xml_ctx
                if dynamic_instructions:
                    user_payload += f"\n\n--- RUNTIME AWARENESS ---\n{dynamic_instructions}"

                has_search = any("search_result" in v for v in state_data.values() if isinstance(v, dict))
                dynamic_schema = self.compiler.build_dynamic_schema(
                    schema_name=f"Step_{step.id}_Response",
                    criteria=criteria_blocks,
                    has_search_result=has_search,
                    target_locale=target_locale
                )

                if frozen_ctx:
                    frozen_ctx.generated_schemas[step.id] = dynamic_schema.model_json_schema()

                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_payload}
                ]

                # LLM Invocation
                strategy_name = step.model_strategy or "fast"
                bound_client = await LLMClient.from_strategy(strategy_name, self.repository)
                # Ensure no results dictionary is directly modified.
                result, usage_dict = await bound_client.run_structured_task(
                    messages=messages,
                    response_model=dynamic_schema,
                    mock_identity=step.id,
                )

                final_dict = result.model_dump(mode="json")

                # Post-Hooks
                safe_context = {
                    k: v.model_dump(mode="json") if hasattr(v, "model_dump") else v
                    for k, v in state_data.items()
                }
                post_hook_state = hook_state.model_copy(update={
                    "global_context_vars": safe_context,
                    "inputs": final_dict
                })
                combined_post_hooks = list(dict.fromkeys(step_obj.post_hooks + step.post_hooks))
                for post_hook in combined_post_hooks:
                    ph_res = await hook_registry.execute(post_hook, post_hook_state, hook_deps)
                    if ph_res.success and ph_res.state_delta:
                        final_dict = deep_merge_dicts(final_dict, ph_res.state_delta)
                        post_hook_state = post_hook_state.model_copy(update={"inputs": final_dict})

                for key in ["profiler_metrics", "step_metadata", "_audit_signature"]:
                    if key in state_data:
                        final_dict[key] = state_data[key]

                if usage_dict:
                    if "_step_metadata" not in final_dict:
                        final_dict["_step_metadata"] = {}
                    final_dict["_step_metadata"]["token_usage"] = usage_dict

                emitted_events.append(TraceEvent(
                    step_name=step.id,
                    event_type="output",
                    content=final_dict
                ))
                return emitted_events

        except Exception as e:
            logger.error(f"[NodeExecutor] Dual-Reporting Exception for step {step.id}: {str(e)}", exc_info=True)
            return [ErrorTraceEvent(
                step_name=step.id,
                error_code="STEP_FAILED",
                error_message=str(e),
                content={"traceback": str(e)}
            )]


class DAGExecutor:
    """The central DAGOrchestrator."""

    def __init__(self, repository: AbstractWorkflowRepository, prompt_compiler: Any):
        self.repository = repository
        self.compiler = prompt_compiler
        self.committer = ExecutionCommitter(repository, "")
        self.node_executor = NodeExecutor(repository, prompt_compiler)

    async def execute_workflow(
        self,
        execution_id: str,
        workflow: Workflow,
        raw_inputs: dict[str, Any]
    ) -> ExecutionRecord:
        """Main entrypoint for Workflow Execution."""
        # Fast Fail validation
        from backend_v2.services.orchestrator.dag_compiler import DAGCompilerService
        DAGCompilerService.validate_workflow(workflow)

        self.committer.execution_id = execution_id

        # 1. State Rehydration / Initialization
        existing_record_dict = await self.repository.get_execution(execution_id)

        step_states = {
            step.id: ExecutionStepState(id=step.id, label=step.id, status="pending")
            for step in workflow.steps
        }

        if existing_record_dict:
            exec_record = ExecutionRecord.model_validate(existing_record_dict)
            exec_record.status = ExecutionStatus.RUNNING
            if not getattr(exec_record, "step_states", None) or not exec_record.step_states:
                exec_record.step_states = step_states
        else:
            inputs_obj = raw_inputs if isinstance(raw_inputs, WorkflowInputs) else WorkflowInputs(**raw_inputs)
            exec_record = ExecutionRecord(
                id=execution_id,
                workflow_id=workflow.id,
                status=ExecutionStatus.RUNNING,
                raw_inputs=inputs_obj,
                execution_trace=[],
                step_states=step_states,
                frozen_context=FrozenContext(),
            )

        # 2. Project Initial State
        projector = StateProjector()
        for evt in exec_record.execution_trace:
            projector.apply_delta(evt)

        # Initial Hydration Phase (if new execution)
        if not exec_record.execution_trace:
            inputs_dict = exec_record.raw_inputs.model_dump(mode="json")
            input_event = TraceEvent(
                step_name="system_inputs",
                event_type="input",
                content=inputs_dict
            )
            exec_record.execution_trace.append(input_event)
            projector.apply_delta(input_event)

            try:
                global_hook_deps = HookDependencies(repository=self.repository)
                global_hook_state = HookState(
                    execution_id=execution_id,
                    workflow_id=workflow.id,
                    metadata=exec_record.metadata,
                    inputs=inputs_dict
                )
                processed_result = await hook_registry.execute("input_processing", global_hook_state, global_hook_deps)
                if processed_result.success and isinstance(processed_result.state_delta, dict):
                    proc_event = TraceEvent(
                        step_name="system_inputs_processed",
                        event_type="input",
                        content=processed_result.state_delta
                    )
                    exec_record.execution_trace.append(proc_event)
                    projector.apply_delta(proc_event)
            except Exception as e:
                msg = f"Pre-Hydration failed: {e}"
                logger.error(msg, exc_info=True)
                raise AppException(
                    message=msg,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED},
                    status_code=400
                ) from e

        # 3. Topology Setup
        steps_by_id = {step.id: step for step in workflow.steps}
        step_events: dict[str, asyncio.Event] = {step.id: asyncio.Event() for step in workflow.steps}

        failed_previous_steps = []
        for step_id, s_state in exec_record.step_states.items():
            if getattr(s_state, "status", None) == "completed":
                step_events[step_id].set()
            elif getattr(s_state, "status", None) == "failed":
                failed_previous_steps.append(step_id)
                exec_record.step_states[step_id].status = "pending"

        # Concurrency Limiter
        semaphore = asyncio.Semaphore(10)

        async def run_step_wrapper(step_id: str) -> None:
            step_obj = steps_by_id[step_id]

            # Skip if completed (Rehydration)
            if exec_record.step_states[step_id].status == "completed":
                return

            for dep in step_obj.depends_on:
                await step_events[dep].wait()

            async with semaphore:
                try:
                    exec_record.step_states[step_id].status = "running"

                    # Proactive status push
                    await self.committer.commit_trace(
                        trace=exec_record.execution_trace,
                        status=exec_record.status,
                        step_states=exec_record.step_states
                    )

                    events = await self.node_executor.execute(
                        step=step_obj,
                        execution_id=execution_id,
                        workflow_id=workflow.id,
                        metadata=exec_record.metadata,
                        projector=projector,
                        expected_inputs=workflow.expected_inputs,
                        frozen_ctx=exec_record.frozen_context,
                        trace=exec_record.execution_trace
                    )

                    for e in events:
                        exec_record.execution_trace.append(e)
                        projector.apply_delta(e)

                    # Error Catching Boundary
                    if any(isinstance(e, ErrorTraceEvent) for e in events):
                        exec_record.step_states[step_id].status = "failed"
                        # Extract the error message from the event
                        msg = [e.error_message for e in events if isinstance(e, ErrorTraceEvent)][0]
                        raise AppException(
                            message=f"Step {step_id} emitted ErrorTraceEvent: {msg}",
                            status_code=500,
                            details={"error_code": ErrorCodes.WORKFLOW_EXECUTION_FAILED}
                        )

                    exec_record.step_states[step_id].status = "completed"
                    await self.committer.commit_trace(
                        trace=exec_record.execution_trace,
                        status=exec_record.status,
                        step_states=exec_record.step_states
                    )
                    step_events[step_id].set()

                except Exception as e:
                    exec_record.step_states[step_id].status = "failed"
                    await self.committer.commit_trace(
                        trace=exec_record.execution_trace,
                        status=ExecutionStatus.FAILED,
                        step_states=exec_record.step_states,
                        error=str(e)
                    )
                    raise WorkflowExecutionError(
                        step_id=step_id,
                        task_key=step_obj.task_blueprint,
                        original_error=e
                    ) from e

        tasks = [asyncio.create_task(run_step_wrapper(step.id)) for step in workflow.steps]
        try:
            await asyncio.gather(*tasks)
            exec_record.status = ExecutionStatus.COMPLETED
            await self.committer.commit_trace(
                trace=exec_record.execution_trace,
                status=exec_record.status,
                step_states=exec_record.step_states
            )
            return exec_record
        except Exception as overall_err:
            for t in tasks:
                if not t.done():
                    t.cancel()
            exec_record.status = ExecutionStatus.FAILED
            exec_record.error = str(overall_err)

            # Safe synchronous fire-and-forget save in loop death
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(self.committer.commit_trace(
                    trace=exec_record.execution_trace,
                    status=exec_record.status,
                    step_states=exec_record.step_states,
                    error=exec_record.error
                ))
            except Exception:
                pass

            if isinstance(overall_err, AppException):
                 raise overall_err

            raise AppException(
                message=f"Workflow failed: {overall_err}",
                details={"error_code": ErrorCodes.WORKFLOW_EXECUTION_FAILED},
                status_code=500
            ) from overall_err
