import asyncio
import copy
import logging
from typing import Any

from backend_v2.core.hook_registry import HookDependencies, HookState, hook_registry
from backend_v2.database.repository import AbstractWorkflowRepository
from backend_v2.exceptions import AppException, ErrorCodes

# Note: Using V1 LLM Client and Hook Registry since V2 versions don't exist yet/weren't found,
# but we wrap them in Fail-Fast V2 principles here.
from backend_v2.llm.client import LLMClient
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


class DAGExecutor:
    """Asynchronous Directed Acyclic Graph (DAG) Executor for V2 Workflows.

    Adheres strictly to RFC 7807 Fail-Fast principles. Executes steps concurrently
    where possible using asyncio.gather. Utilizes PromptCompiler for Schema-Driven AI.
    """

    def __init__(self, repository: AbstractWorkflowRepository, prompt_compiler: Any):
        """Args:
        repository: V2 dual-backend repository for persistence.
        prompt_compiler: Instance of backend_v2 PromptCompiler.
        """
        self.repository = repository
        self.compiler = prompt_compiler
        # Singleton LLM context
        self.llm_client = LLMClient()

    async def execute_workflow(
        self,
        execution_id: str,
        workflow: Workflow,
        raw_inputs: dict[str, Any]
    ) -> ExecutionRecord:
        """Main entrypoint. Inits execution context, parses graph, runs async tasks.

        Args:
            execution_id: The requested Execution UUID.
            workflow: The hydrated strictly-typed V2 Workflow object.
            raw_inputs: Unvalidated inputs dict (validated per step by models).
        """
        # Epic 2: Execution Firewall (Fast Fail Invalid Graphs)
        from backend_v2.services.orchestrator.dag_compiler import DAGCompilerService
        DAGCompilerService.validate_workflow(workflow)

        # Fetch existing execution record from DB (created by ExecutionService)
        existing_record_dict = await self.repository.get_execution(execution_id)

        step_states = {
            step.id: ExecutionStepState(id=step.id, label=step.id, status="pending")
            for step in workflow.steps
        }

        if existing_record_dict:
            exec_record = ExecutionRecord.model_validate(existing_record_dict)
            exec_record.status = ExecutionStatus.RUNNING
            # Update step states if they were not already populated
            if not exec_record.step_states:
                exec_record.step_states = step_states
        else:
            # Fallback if not initialized by service
            exec_record = ExecutionRecord(
                id=execution_id,
                workflow_id=workflow.id,
                status=ExecutionStatus.RUNNING,
                raw_inputs=raw_inputs if isinstance(raw_inputs, WorkflowInputs) else WorkflowInputs(**raw_inputs),
                frozen_context=FrozenContext(),
                results={},
                step_states=step_states,
            )



        # Upsert cleanly
        await self.repository.update_execution(
            execution_id,
            {
                "status": exec_record.status.value,
                "metadata": exec_record.metadata,
                "step_states": {k: v.model_dump() for k, v in exec_record.step_states.items()}
            }
        )

        # Resolve Steps
        steps_by_id = {step.id: step for step in workflow.steps}

        dependents: dict[str, list[str]] = {step.id: [] for step in workflow.steps}

        for step in workflow.steps:
            for dep in step.depends_on:
                if dep not in dependents:
                    dependents[dep] = []
                dependents[dep].append(step.id)

        # Execution State variables
        step_events: dict[str, asyncio.Event] = {step.id: asyncio.Event() for step in workflow.steps}

        # Convert to pure dicts for hook compatibility
        raw_inputs_dict = raw_inputs.model_dump(mode="json") if hasattr(raw_inputs, "model_dump") else dict(raw_inputs)
        state_data = dict(raw_inputs_dict)
        state_data["inputs"] = raw_inputs_dict  # Legacy V1 hooks expect data["inputs"]

        # --- V2 Strict Execution Hydration Phase ---
        # With V2 Shallow Copy Concurrency isolation (Phase 9), pre_hooks mutating state_data
        # inside _execute_step are strictly isolated. Thus, we MUST run global hydrators
        # like `input_processing` synchronously BEFORE parallel DAG orchestration starts.

        try:
            logger.info(f"[DAGExecutor] Initiating Step 0 Base64 Pre-Hydration for Workflow {workflow.id}")

            # Create strict dependencies and state for global hooks
            global_hook_deps = HookDependencies(repository=self.repository)
            global_hook_state = HookState(
                execution_id=execution_id,
                workflow_id=workflow.id,
                metadata=exec_record.metadata,
                inputs=state_data
            )

            processed_result = await hook_registry.execute("input_processing", global_hook_state, global_hook_deps)
            if processed_result.success and isinstance(processed_result.state_delta, dict):
                 state_data = deep_merge_dicts(state_data, processed_result.state_delta)
                 if "inputs" in processed_result.state_delta:
                     state_data["inputs"] = processed_result.state_delta["inputs"]
        except Exception as e:
            msg = f"Pre-Hydration failed to parse raw inputs: {e}"
            logger.error(f"[DAGExecutor] {ErrorCodes.VALIDATION_FAILED.name}: {msg}", exc_info=True)
            raise AppException(
                message=msg,
                details={"error_code": ErrorCodes.VALIDATION_FAILED},
                status_code=400
            ) from e

        frozen_ctx = exec_record.frozen_context

        try:
            # Main execution loop
            async def run_step_wrapper(step_id: str) -> None:
                step_obj = steps_by_id[step_id]
                # Wait for dependencies
                for dep in step_obj.depends_on:
                    await step_events[dep].wait()

                try:
                    # 1. Update status to running
                    exec_record.step_states[step_id].status = "running"
                    await self.repository.update_execution(
                        execution_id,
                        {"step_states": {k: v.model_dump() for k, v in exec_record.step_states.items()}}
                    )

                    result = await self._execute_step(
                        step=step_obj,
                        shared_state_data=state_data,
                        frozen_ctx=frozen_ctx,
                        execution_id=execution_id,
                        workflow_id=workflow.id,
                        metadata=exec_record.metadata,
                        expected_inputs=workflow.expected_inputs
                    )
                    # State update is atomic per step constraint
                    state_data[step_obj.id] = result
                    exec_record.results[step_obj.id] = result

                    # 2. Update status to completed
                    exec_record.step_states[step_id].status = "completed"

                    # Append results to DB (Optimistic Update)
                    await self.repository.update_execution(
                        execution_id,
                        {
                            "results": exec_record.results,
                            "frozen_context": frozen_ctx.model_dump(),
                            "step_states": {k: v.model_dump() for k, v in exec_record.step_states.items()}
                        }
                    )
                    # Signal completion to unblock dependents ONLY ON SUCCESS
                    step_events[step_id].set()
                except asyncio.CancelledError:
                    # Task was cancelled, do not set event
                    raise
                except Exception as e:
                    logger.error(
                        f"[DAGExecutor] {ErrorCodes.WORKFLOW_EXECUTION_FAILED.name}: "
                        f"Step {step_id} failed: {e}",
                        exc_info=True
                    )
                    # 3. Update status to failed
                    if step_id in exec_record.step_states:
                        exec_record.step_states[step_id].status = "failed"
                        await self.repository.update_execution(
                            execution_id,
                            {"step_states": {k: v.model_dump() for k, v in exec_record.step_states.items()}}
                        )
                    from backend_v2.exceptions import WorkflowExecutionError
                    raise WorkflowExecutionError(
                        step_id=step_id,
                        task_key=step_obj.task_blueprint,
                        original_error=e
                    ) from e

            # Schedule all steps immediately, they will block on .wait()
            tasks = [asyncio.create_task(run_step_wrapper(step.id)) for step in workflow.steps]

            try:
                # Await all
                await asyncio.gather(*tasks)
            except Exception as e:
                # Cancel all remaining tasks to ensure true Fail-Fast behavior
                for t in tasks:
                    if not t.done():
                        t.cancel()
                raise e

            exec_record.status = ExecutionStatus.COMPLETED
            await self.repository.update_execution(execution_id, {"status": exec_record.status.value})
            return exec_record

        except Exception as overall_err:
            msg = f"Workflow execution {execution_id} failed: {overall_err}"
            logger.error(
                f"[DAGExecutor] {ErrorCodes.WORKFLOW_EXECUTION_FAILED.name}: {msg}",
                exc_info=True
            )
            exec_record.status = ExecutionStatus.FAILED
            exec_record.error = str(overall_err)

            # Use safe fire-and-forget sync wrapper for DB update if we're crashing
            try:
                # Need a new event loop or run synchronously to ensure it saves before crash
                loop = asyncio.get_running_loop()
                loop.create_task(self.repository.update_execution(
                    execution_id,
                    {"status": exec_record.status.value, "error": exec_record.error}
                ))
            except Exception:
                pass

            # RFC 7807 Fail-Fast Mandate: We MUST raise here. BackgroundTasks in FastAPI
            # actually handle raising exceptions just fine by logging them to stderr.
            # Suppressing them violates the V2 Zero-Compromise Pledge.

            if isinstance(overall_err, AppException):
                 raise overall_err

            raise AppException(
                message=msg,
                details={"error_code": ErrorCodes.WORKFLOW_EXECUTION_FAILED},
                status_code=500
            ) from overall_err

    async def _execute_step(
        self,
        step: StepRule,
        shared_state_data: dict[str, Any],
        frozen_ctx: FrozenContext,
        execution_id: str,
        workflow_id: str,
        metadata: dict[str, Any],
        expected_inputs: list[Any] | None = None
    ) -> Any:
        """Executes a single step: hook, agent, or conditional logic."""
        # 1. Condition Evaluation (Currently unsupported in V2 StepRule schema)

        # Isolate state deeply to prevent concurrency bleeding between async nodes in Phase 9
        # Shallow copies (like `dict()`) fail if hooks mutate nested dicts or lists during asyncio.gather
        state_data = copy.deepcopy(shared_state_data)

        # 2. Hook Execution (Deterministic or Async)
        hook_name: str | None = getattr(step, "hook", None)
        if hook_name:
            # Create strict state and deps for the standalone hook
            hook_deps = HookDependencies(repository=self.repository)
            hook_state = HookState(
                execution_id=execution_id,
                workflow_id=workflow_id,
                step_id=step.id,
                task_blueprint=getattr(step, "task_blueprint", None),
                metadata=metadata,
                inputs=state_data
            )

            logger.debug(f"Executing Hook via Registry: {hook_name}")
            hook_result = await hook_registry.execute(hook_name, hook_state, hook_deps)
            return deep_merge_dicts(state_data, hook_result.state_delta or {})

        # 3. Role LLM Execution (Non-Deterministic)
        blueprint_slug: str | None = getattr(step, "task_blueprint", None)
        if blueprint_slug:
            step_def = await self.repository.get_step_by_id(blueprint_slug)
            if not step_def:
                msg = f"Configuration error: Step '{blueprint_slug}' not found in database."
                logger.error(f"[DAGExecutor] {ErrorCodes.CONFIGURATION_ERROR.name}: {msg}")
                raise AppException(
                    message=msg,
                    status_code=500,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR}
                )

            # Execution logic branches based on node type
            if step_def.get("type", "llm") == "logic":
                # Create typed context for the standalone logic node
                hook_deps = HookDependencies(repository=self.repository)
                hook_state = HookState(
                    execution_id=execution_id,
                    workflow_id=workflow_id,
                    step_id=step.id,
                    task_blueprint=getattr(step, "task_blueprint", None),
                    metadata=metadata,
                    inputs=state_data
                )

                # --- NATIVE LOGIC NODE EXECUTION (No LLM Cost) ---
                logic_hook: str | None = step_def.get("hook", None)
                if logic_hook:
                    # Execute Step-level pre-hooks manually before the designated logic
                    for pre_hook in step_def.get("pre_hooks", []):
                        hook_result = await hook_registry.execute(pre_hook, hook_state, hook_deps)
                        if hook_result.success and hook_result.state_delta:
                            state_data = deep_merge_dicts(state_data, hook_result.state_delta)
                            # Update hook_state with the merged state_data for subsequent hooks
                            hook_state = hook_state.model_copy(update={"inputs": state_data})

                    logger.debug(
                        f"Executing Native Logic Step '{step_def.get('slug', 'unknown')}' "
                        f"via hook: {logic_hook}"
                    )
                    result = await hook_registry.execute(logic_hook, hook_state, hook_deps)
                    if result.success and result.state_delta:
                        state_data = deep_merge_dicts(state_data, result.state_delta)
                        hook_state = hook_state.model_copy(update={"inputs": state_data})

                    # 4. Post-Hook Execution
                    # Hooks attached to the StepRule
                    for post_hook in getattr(step, "post_hooks", []):
                        hook_result = await hook_registry.execute(post_hook, hook_state, hook_deps)
                        if hook_result.success and hook_result.state_delta:
                            state_data = deep_merge_dicts(state_data, hook_result.state_delta)
                            hook_state = hook_state.model_copy(update={"inputs": state_data})

                    # Hooks attached to the logical Step template
                    for post_hook in step_def.get("post_hooks", []):
                        hook_result = await hook_registry.execute(post_hook, hook_state, hook_deps)
                        if hook_result.success and hook_result.state_delta:
                            state_data = deep_merge_dicts(state_data, hook_result.state_delta)
                            hook_state = hook_state.model_copy(update={"inputs": state_data})

                    return state_data
                else:
                    raise AppException(
                        message=f"Logic step '{step_def.get('slug', 'unknown')}' has no hook defined.",
                        status_code=500,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED}
                    )

            # --- LLM NODE EXECUTION ---
            # Step level Pre-Hooks
            from backend_v2.models.v2_core import Step
            step_obj = Step.model_validate(step_def)

            logger.debug(f"Executing Step: {step_obj.id}")

            # 3.0 Pre-Hooks Execution
            hook_deps = HookDependencies(repository=self.repository)
            hook_state = HookState(
                execution_id=execution_id,
                workflow_id=workflow_id,
                step_id=step.id,
                task_blueprint=step.task_blueprint,
                metadata=metadata,
                inputs=state_data
            )

            # Combine pre-hooks from both the underlying Step and the specific StepRule,
            # preserving order and ensuring uniqueness via dict.fromkeys
            combined_pre_hooks = list(dict.fromkeys(step_obj.pre_hooks + step.pre_hooks))

            for pre_hook in combined_pre_hooks:
                logger.debug(f"Executing Pre-Hook: {pre_hook}")
                # We assume pre-hooks modify state_data by returning state deltas.
                result = await hook_registry.execute(pre_hook, hook_state, hook_deps)
                if result.success and result.state_delta:
                     state_data = deep_merge_dicts(state_data, result.state_delta)
                     hook_state = hook_state.model_copy(update={"inputs": state_data})

            # 3.1 Criteria Blocks Gathering (prompt_blocks)
            criteria_blocks = []
            all_prompt_blocks = await self.repository.get_all_prompt_blocks()
            block_map = {b["id"]: b for b in all_prompt_blocks if "id" in b}

            # Clone the block list so we don't mutate the db-loaded schema
            active_prompt_blocks = list(step_obj.prompt_blocks)

            for m_id in active_prompt_blocks:
                block_dict = block_map.get(m_id)
                if block_dict:
                    from backend_v2.models.v2_core import PromptBlock
                    PromptBlock.model_validate(block_dict) # Fail-Fast validation check
                    criteria_blocks.append(block_dict)
                else:
                    msg = f"PromptBlock '{m_id}' not found. Referenced by Step '{step_obj.slug}'"
                    logger.error(f"[DAGExecutor] {ErrorCodes.VALIDATION_FAILED.name}: {msg}", exc_info=True)
                    raise AppException(
                        message=msg,
                        status_code=500,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED}
                    )

            # 3.2 Resolving xml context & Epic 5 Caching Extraction
            target_locale = metadata.get("target_locale")
            if not target_locale:
                msg = "Execution metadata is missing the required 'target_locale', violating the Fail-Fast mandate."
                logger.error(f"[DAGExecutor] {ErrorCodes.VALIDATION_FAILED.name}: {msg}", exc_info=True)
                raise AppException(message=msg, details={"error_code": ErrorCodes.VALIDATION_FAILED}, status_code=400)

            # Extract Static & Dynamic Prompts
            static_instructions = self.compiler.compile_static_instructions(criteria_blocks, target_locale)
            dynamic_instructions = self.compiler.compile_dynamic_instructions(criteria_blocks, target_locale)

            # The Head (System Prompt focuses entirely on static cacheable content)
            system_prompt = "Complete the evaluation according to the provided schema."
            if static_instructions:
                system_prompt += f"\n\n{static_instructions}"

            xml_ctx = self.compiler.build_xml_context(
                input_mappings=step.input_mappings if hasattr(step, "input_mappings") else {},
                state_data=state_data,
                target_locale=target_locale, # The LLM outputs in the user's localized language
                expected_inputs=expected_inputs
            )

            # The Tail (User Prompt terminates with dynamic variables to prevent cache invalidation)
            user_payload = xml_ctx
            if dynamic_instructions:
                user_payload += f"\n\n--- RUNTIME AWARENESS ---\n{dynamic_instructions}"

            # 3.3 Dynamic Schema
            has_search_result = any("search_result" in v for v in state_data.values() if isinstance(v, dict))
            dynamic_schema = self.compiler.build_dynamic_schema(
                schema_name=f"Step_{step.id}_Response",
                criteria=criteria_blocks,
                require_justification=True,
                has_search_result=has_search_result,
                target_locale=target_locale
            )
            frozen_ctx.generated_schemas[step.id] = dynamic_schema.model_json_schema()

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_payload}
            ]

            # 3.4 LLM Strategy Resolution (V2 Strict Mode)
            strategy_name = step.model_strategy or "fast"
            from backend_v2.llm.client import LLMClient
            bound_client = await LLMClient.from_strategy(strategy_name, self.repository)

            # 3.5 LLM Call (Using Strategy-bound Client wrapper)
            result, usage_dict = await bound_client.run_structured_task(
                messages=messages,
                response_model=dynamic_schema,
                mock_identity=step.id,
            )

            final_dict = result.model_dump(mode="json")

            # 3.4 Post-Hooks Execution
            # V2 Isolation: Provide the isolated final_dict, and pass global context in the explicit
            # HookState instead of polluting the result JSON directly via _sys_context_vars

            safe_context = {
                k: v.model_dump(mode="json") if hasattr(v, "model_dump") else v
                for k, v in state_data.items()
            }

            # Post hooks use the strict state, integrating global context securely
            post_hook_state = hook_state.model_copy(update={
                "global_context_vars": safe_context,
                "inputs": final_dict
            })

            # Combine post-hooks from both the underlying Step and the specific StepRule
            combined_post_hooks = list(dict.fromkeys(step_obj.post_hooks + step.post_hooks))

            for post_hook in combined_post_hooks:
                logger.debug(f"Executing Post-Hook: {post_hook}")
                # Pass the LLM output dict inside the post hook state
                ph_result = await hook_registry.execute(post_hook, post_hook_state, hook_deps)
                if ph_result.success and ph_result.state_delta:
                    final_dict = deep_merge_dicts(final_dict, ph_result.state_delta)
                    post_hook_state = post_hook_state.model_copy(update={"inputs": final_dict})

            # 3.5 Merge Python Hook State into Final Result
            # Pre-hooks often return specific statistical metadata keys. By convention,
            # we look for known injected objects in the state_data and append them dynamically
            # to the Pydantic-validated output dictionary.
            for key in ["profiler_metrics", "step_metadata", "_audit_signature"]:
                if key in state_data:
                    final_dict[key] = state_data[key]

            # Inject Usage Metadata into the result for worker.py extraction
            if usage_dict:
                if "_step_metadata" not in final_dict:
                    final_dict["_step_metadata"] = {}
                final_dict["_step_metadata"]["token_usage"] = {
                    "prompt_tokens": usage_dict.get("prompt_tokens", 0),
                    "completion_tokens": usage_dict.get("completion_tokens", 0),
                    "total_tokens": usage_dict.get("total_tokens", 0),
                    "cached_tokens": usage_dict.get("cached_tokens", 0),
                    "reasoning_tokens": usage_dict.get("reasoning_tokens", 0),
                    "cost_usd": usage_dict.get("cost_usd", 0.0)
                }

            return final_dict

        else:
            msg = f"Step {step.id} has no valid execution target (no hook or matrix_ids)."
            logger.error(f"[DAGExecutor] {ErrorCodes.VALIDATION_FAILED.name}: {msg}", exc_info=True)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED}
            )
