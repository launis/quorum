import asyncio
import logging
from typing import Any

import backend_v2.hooks  # Ensures hooks are registered
from backend_v2.core.hook_registry import hook_registry
from backend_v2.database.repository import AbstractWorkflowRepository
from backend_v2.exceptions import AppException, ErrorCodes

# Note: Using V1 LLM Client and Hook Registry since V2 versions don't exist yet/weren't found,
# but we wrap them in Fail-Fast V2 principles here.
from backend_v2.llm.client import LLMClient
from backend_v2.models.v2_core import (
    ExecutionRecord,
    ExecutionStatus,
    FrozenContext,
    StepRule,
    Workflow,
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

        # Create new execution record
        exec_record = ExecutionRecord(
            id=execution_id,
            workflow_id=workflow.id,
            status=ExecutionStatus.RUNNING,
            raw_inputs=raw_inputs,
            frozen_context=FrozenContext(),
            results={},
        )
        await self.repository.create_execution(exec_record.model_dump())

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

        state_data = dict(raw_inputs)
        state_data["inputs"] = raw_inputs  # Legacy V1 hooks expect data["inputs"]
        state_data["_sys_workflow_id"] = workflow.id  # Required by V2 input_processing hook
        frozen_ctx = exec_record.frozen_context

        try:
            # Main execution loop
            async def run_step_wrapper(step_id: str) -> None:
                step_obj = steps_by_id[step_id]
                # Wait for dependencies
                for dep in step_obj.depends_on:
                    await step_events[dep].wait()

                try:
                    result = await self._execute_step(step_obj, state_data, frozen_ctx)
                    # State update is atomic per step constraint
                    state_data[step_obj.id] = result
                    exec_record.results[step_obj.id] = result
                    # Append results to DB (Optimistic Update)
                    await self.repository.update_execution(
                        execution_id,
                        {"results": exec_record.results, "frozen_context": frozen_ctx.model_dump()}
                    )
                    # Signal completion to unblock dependents ONLY ON SUCCESS
                    step_events[step_id].set()
                except asyncio.CancelledError:
                    # Task was cancelled, do not set event
                    raise
                except Exception as e:
                    logger.error(f"Step {step_id} failed: {e}")
                    raise e

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
            logger.error(f"Workflow execution {execution_id} failed: {overall_err}")
            exec_record.status = ExecutionStatus.FAILED
            exec_record.error = str(overall_err)
            await self.repository.update_execution(
                execution_id,
                {"status": exec_record.status.value, "error": exec_record.error}
            )
            # DO NOT re-raise. This runs in a FastAPI BackgroundTask. Re-raising here
            # crashes the Uvicorn ASGI server as the response has already been sent.
            return exec_record

    async def _execute_step(self, step: StepRule, state_data: dict[str, Any], frozen_ctx: FrozenContext) -> Any:
        """Executes a single step: hook, agent, or conditional logic."""
        # 1. Condition Evaluation (Currently unsupported in V2 StepRule schema)

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
                logger.error(f"Step '{blueprint_slug}' not found for step {step.id}")
                raise AppException(
                    message=f"Configuration error: Step '{blueprint_slug}' not found in database.",
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED}
                )

            from backend_v2.models.v2_core import Step
            step_obj = Step.model_validate(step_def)

            logger.debug(f"Executing Step: {step_obj.id}")

            # 3.0 Pre-Hooks Execution
            state_data["_sys_repository"] = self.repository
            for pre_hook in step_obj.pre_hooks:
                logger.debug(f"Executing Pre-Hook: {pre_hook}")
                # We assume pre-hooks modify state_data in-place or return updated dict.
                result = await hook_registry.execute(pre_hook, state_data)
                if isinstance(result, dict):
                     state_data.update(result)

            # 3.1 Resolving xml context
            system_prompt = "Complete the evaluation according to the provided schema."
            xml_ctx = self.compiler.build_xml_context(
                input_mappings=step.input_mappings if hasattr(step, "input_mappings") else {},
                state_data=state_data,
                target_locale="en"
            )

            # 3.2 Criteria Blocks Gathering (prompt_blocks)
            criteria_blocks = []
            all_prompt_blocks = await self.repository.get_all_prompt_blocks()
            block_map = {b["id"]: b for b in all_prompt_blocks if "id" in b}

            for m_id in step_obj.prompt_blocks:
                block_dict = block_map.get(m_id)
                if block_dict:
                    from backend_v2.models.v2_core import PromptBlock
                    PromptBlock.model_validate(block_dict) # Fail-Fast validation check
                    criteria_blocks.append(block_dict)
                else:
                    logger.warning(f"PromptBlock '{m_id}' not found. Referenced by Step '{step_obj.slug}'")

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
            return result.model_dump()

        else:
            raise AppException(
                message=f"Step {step.id} has no valid execution target (no hook or matrix_ids).",
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED}
            )
