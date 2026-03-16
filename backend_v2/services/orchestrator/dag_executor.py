import asyncio
import logging
from typing import Any

from backend_v2.core.hook_registry import hook_registry
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
        # Validate acyclic property (Already validated by Pydantic Model but we ensure it)
        # Note: Pydantic Workflow model handles it on instantiation.

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

        # MVP Blueprint Injection (Hardcoded for Milestone 1)
        if not exec_record.render_blueprint:
            exec_record.render_blueprint = {
                "version": "1.0",
                "components": [
                    {"type": "metadata_header"},
                    {"type": "header", "title": "report.title_main"},
                    {"type": "bibliography_footer"}
                ]
            }

        # V2 Strictness Engine Metadata Injection
        macro_strict = exec_record.strictness_level.value
        micro_strict = 100 if macro_strict == 5 else 50
        exec_record.metadata["macro_strictness_level"] = macro_strict
        exec_record.metadata["micro_strictness_level"] = micro_strict

        # Upsert cleanly
        await self.repository.update_execution(
            execution_id,
            {
                "status": exec_record.status.value,
                "metadata": exec_record.metadata,
                "render_blueprint": exec_record.render_blueprint,
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
        state_data["_sys_workflow_id"] = workflow.id  # Required by V2 input_processing hook
        state_data["_sys_execution_id"] = execution_id
        state_data["_sys_repository"] = self.repository
        state_data["_sys_metadata"] = exec_record.metadata

        # --- V2 Strict Execution Hydration Phase ---
        # With V2 Shallow Copy Concurrency isolation (Phase 9), pre_hooks mutating state_data
        # inside _execute_step are strictly isolated. Thus, we MUST run global hydrators
        # like `input_processing` synchronously BEFORE parallel DAG orchestration starts.

        try:
            logger.info(f"[DAGExecutor] Initiating Step 0 Base64 Pre-Hydration for Workflow {workflow.id}")
            processed = await hook_registry.execute("input_processing", state_data)
            if isinstance(processed, dict) and "inputs" in processed:
                 state_data["inputs"] = processed["inputs"]
        except Exception as e:
            msg = f"Pre-Hydration failed to parse raw inputs: {e}"
            logger.error(f"[DAGExecutor] {ErrorCodes.VALIDATION_FAILED.name}: {msg}", exc_info=True)
            raise AppException(
                message=msg,
                details={"error_code": ErrorCodes.VALIDATION_FAILED},
                status_code=400
            ) from e
        state_data["_sys_execution_id"] = execution_id
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

                    result = await self._execute_step(step_obj, state_data, frozen_ctx)
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
                            "render_blueprint": exec_record.render_blueprint,
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

            from backend_v2.exceptions import AppException
            if isinstance(overall_err, AppException):
                 raise overall_err

            raise AppException(
                message=msg,
                details={"error_code": ErrorCodes.WORKFLOW_EXECUTION_FAILED},
                status_code=500
            ) from overall_err

    async def _execute_step(self, step: StepRule, shared_state_data: dict[str, Any], frozen_ctx: FrozenContext) -> Any:
        """Executes a single step: hook, agent, or conditional logic."""
        # 1. Condition Evaluation (Currently unsupported in V2 StepRule schema)

        # Isolate state to prevent concurrency bleeding between async nodes in Phase 9
        state_data = dict(shared_state_data)

        # 2. Hook Execution (Deterministic or Async)
        hook_name: str | None = getattr(step, "hook", None)
        if hook_name:
            # Inject repository for hooks that need database or LLM access
            state_data["_sys_repository"] = self.repository

            logger.debug(f"Executing Hook via Registry: {hook_name}")
            return await hook_registry.execute(hook_name, state_data)

        # 3. Role LLM Execution (Non-Deterministic)
        blueprint_slug: str | None = getattr(step, "task_blueprint", None)
        if blueprint_slug:
            step_def = await self.repository.get_step_by_id(blueprint_slug)
            if not step_def:
                msg = f"Configuration error: Step '{blueprint_slug}' not found in database."
                logger.error(f"[DAGExecutor] {ErrorCodes.VALIDATION_FAILED.name}: {msg}", exc_info=True)
                raise AppException(
                    message=msg,
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED}
                )

            from backend_v2.models.v2_core import Step
            step_obj = Step.model_validate(step_def)

            logger.debug(f"Executing Step: {step_obj.id}")

            # 3.0 Pre-Hooks Execution
            state_data["_sys_repository"] = self.repository
            state_data["_sys_step_id"] = step.id

            for pre_hook in step_obj.pre_hooks:
                logger.debug(f"Executing Pre-Hook: {pre_hook}")
                # We assume pre-hooks modify state_data in-place or return updated dict.
                result = await hook_registry.execute(pre_hook, state_data)
                if isinstance(result, dict):
                     state_data.update(result)

            # 3.1 Resolving xml context
            system_prompt = "Complete the evaluation according to the provided schema."
            target_locale = state_data.get("_sys_metadata", {}).get("target_locale")
            if not target_locale:
                msg = "Execution metadata is missing the required 'target_locale', violating the Fail-Fast mandate."
                logger.error(f"[DAGExecutor] {ErrorCodes.VALIDATION_FAILED.name}: {msg}", exc_info=True)
                raise AppException(message=msg, details={"error_code": ErrorCodes.VALIDATION_FAILED}, status_code=400)

            xml_ctx = self.compiler.build_xml_context(
                input_mappings=step.input_mappings if hasattr(step, "input_mappings") else {},
                state_data=state_data,
                target_locale=target_locale # The LLM outputs in the user's localized language
            )

            # 3.2 Criteria Blocks Gathering (prompt_blocks)
            criteria_blocks = []
            all_prompt_blocks = await self.repository.get_all_prompt_blocks()
            block_map = {b["id"]: b for b in all_prompt_blocks if "id" in b}

            # --- V2 Strictness Level: Cognitive Payload Injection ---
            # Extract execution record to determine Strictness Level
            # Default to CAUSAL (V1 max) if not found
            strictness = 3
            execution_id = state_data.get("_sys_execution_id")
            if execution_id:
                exec_record_dict = await self.repository.get_execution(execution_id)
                if exec_record_dict and hasattr(exec_record_dict, 'strictness_level'):
                    strictness = exec_record_dict.strictness_level

            # Clone the block list so we don't mutate the db-loaded schema
            active_prompt_blocks = list(step_obj.prompt_blocks)

            # Apply Zero-Trust / Falsification dynamic mutations
            if strictness >= 4:
                # Remove default judge completely if present
                if "block_role_judge" in active_prompt_blocks:
                    active_prompt_blocks.remove("block_role_judge")

                # Falsification First applies to both 4 and 5
                if "block_rule_falsification_first" not in active_prompt_blocks:
                    active_prompt_blocks.append("block_rule_falsification_first")

                # Level 5 gets Saboteur, Level 4 gets Prosecutor
                if strictness == 5:
                    if "block_role_saboteur" not in active_prompt_blocks:
                        active_prompt_blocks.append("block_role_saboteur")
                else:
                    if "block_role_prosecutor" not in active_prompt_blocks:
                        active_prompt_blocks.append("block_role_prosecutor")

            if strictness == 5:
                # Inject absolute Zero-Trust mandates and humility check
                if "block_mandate_zerotrust" not in active_prompt_blocks:
                    active_prompt_blocks.append("block_mandate_zerotrust")
                if "block_rule_cognitiverequirement" not in active_prompt_blocks:
                    active_prompt_blocks.append("block_rule_cognitiverequirement")
                if "matrix_epistemic_humility" not in active_prompt_blocks:
                    active_prompt_blocks.append("matrix_epistemic_humility")

            for m_id in active_prompt_blocks:
                block_dict = block_map.get(m_id)
                if block_dict:
                    from backend_v2.models.v2_core import PromptBlock

                    # Apply absolute cognitive friction (Scale 100 fallback) for Level 5
                    if strictness == 5 and block_dict.get("type", "float") == "float":
                         block_dict["strictness_level"] = 100

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

            # 3.3 Dynamic Schema
            dynamic_schema = self.compiler.build_dynamic_schema(
                schema_name=f"Step_{step.id}_Response",
                criteria=criteria_blocks,
                require_justification=True
            )
            frozen_ctx.generated_schemas[step.id] = dynamic_schema.model_json_schema()

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": xml_ctx}
            ]

            # 3.4 LLM Strategy Resolution (V2 Strict Mode)
            strategy_name = step.model_strategy or "fast"
            from backend_v2.llm.client import LLMClient
            bound_client = await LLMClient.from_strategy(strategy_name, self.repository)

            # 3.5 LLM Call (Using Strategy-bound Client wrapper)
            result = await bound_client.run_structured_task(
                messages=messages,
                response_model=dynamic_schema,
            )

            final_dict = result.model_dump(mode="json")

            # 3.4 Post-Hooks Execution
            # V2 Isolation: Provide the isolated final_dict, but inject a lookup hook
            # for global context if the post-hook needs to aggregate across nodes.
            # SSOT Mandate (Phase 11): Strict IN -> Generic OUT. Enforce dictionary serialization boundary.
            safe_context = {
                k: v.model_dump(mode="json") if hasattr(v, "model_dump") else v
                for k, v in state_data.items()
            }
            final_dict["_sys_context_vars"] = safe_context

            for post_hook in step_obj.post_hooks:
                logger.debug(f"Executing Post-Hook: {post_hook}")
                # Pass the LLM output dict to the post hook for manipulation/normalization
                ph_result = await hook_registry.execute(post_hook, final_dict)
                if isinstance(ph_result, dict):
                    final_dict.update(ph_result)

            # Remove the injected global context immediately to prevent recursive JSON bloat
            if "_sys_context_vars" in final_dict:
                del final_dict["_sys_context_vars"]

            # 3.5 Merge Python Hook State into Final Result
            # Pre-hooks often return specific statistical metadata keys. By convention,
            # we look for known injected objects in the state_data and append them dynamically
            # to the Pydantic-validated output dictionary.
            for key in ["profiler_metrics", "step_metadata", "_audit_signature"]:
                if key in state_data:
                    final_dict[key] = state_data[key]

            # Inject PromptBlock micro strictness metadata into the step result
            micro_strictness_map = {
                block["id"]: block.get("strictness_level", 50)
                for block in criteria_blocks
            }
            if "_step_metadata" not in final_dict:
                final_dict["_step_metadata"] = {}
            final_dict["_step_metadata"]["micro_strictness_levels"] = micro_strictness_map

            return final_dict

        else:
            msg = f"Step {step.id} has no valid execution target (no hook or matrix_ids)."
            logger.error(f"[DAGExecutor] {ErrorCodes.VALIDATION_FAILED.name}: {msg}", exc_info=True)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED}
            )
