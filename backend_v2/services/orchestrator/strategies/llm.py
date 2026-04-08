import logging
from typing import Any

from backend_v2.core.hook_registry import HookDependencies, HookState
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.client import LLMClient
from backend_v2.models.state import StateProjector, TraceEvent
from backend_v2.models.v2_core import FrozenContext, StepRule
from backend_v2.models.v2_core import Step as V2Step
from backend_v2.services.orchestrator.strategies.base import NodeStrategy, StrategyContext

logger = logging.getLogger(__name__)


class LLMNodeStrategy(NodeStrategy):
    """Executes an AI/LLM Step.

    Manages dynamic schema compilation, instruction aggregation, tracing optimization
    for token context explosion, and routes through either a standard structured prediction
    task or an autonomous MCP Tool Loop depending on step configuration.
    """

    async def execute(
        self,
        step: StepRule,
        projector: StateProjector,
        context: StrategyContext,
        frozen_ctx: FrozenContext | None,
        trace: list[TraceEvent] | None,
    ) -> list[TraceEvent]:
        current_state = dict(projector.snapshot)

        blueprint_id = getattr(step, "task_blueprint", None)
        if not blueprint_id:
            logger.error(
                "Step has no task_blueprint configured.",
                extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name, "step_id": step.id},
            )
            raise AppException(
                message=f"Step {step.id} has no task_blueprint configured.",
                status_code=500,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR},
            )

        step_def = await self.repository.get_step_by_id(blueprint_id)
        if not step_def:
            logger.error(
                f"Configuration error: Step '{blueprint_id}' not found.",
                extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name, "step_id": step.id},
            )
            raise AppException(
                message=f"Configuration error: Step '{blueprint_id}' not found.",
                status_code=500,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR},
            )

        step_obj = V2Step.model_validate(step_def)
        hook_deps = HookDependencies(repository=self.repository)

        state_data = dict(current_state)
        hook_state = HookState(
            execution_id=context.execution_id,
            workflow_id=context.workflow_id,
            step_id=step.id,
            task_blueprint=blueprint_id,
            metadata=context.metadata,
            inputs=state_data,
        )

        # 1. Pre-Hooks
        hook_state = await self.run_pre_hooks(step_obj, step, hook_state, hook_deps, state_data)
        state_data = dict(hook_state.inputs)

        # 2. Compile LLM Prompts & Schemas
        criteria_blocks = []
        all_prompt_blocks = await self.repository.get_all_prompt_blocks()
        block_map = {b["id"]: b for b in all_prompt_blocks if "id" in b}
        # Enforce Architectual Parity: Fail-Fast if Pipeline Amnesia occurs
        target_profile = context.metadata.get("profile_id")
        if not target_profile:
            from backend_v2.exceptions import ConfigurationError
            msg = f"Execution metadata missing mandatory 'profile_id' for workflow {context.workflow_id}."
            raise ConfigurationError(msg, details={"error_code": ErrorCodes.CONFIGURATION_ERROR})

        for m_id in step_obj.prompt_blocks:
            b = block_map.get(m_id)
            if b:
                criteria_blocks.append(b)
            else:
                logger.error(
                    f"PromptBlock '{m_id}' not found.",
                    extra={"error_code": ErrorCodes.VALIDATION_FAILED.name, "step_id": step.id},
                )
                raise AppException(
                    message=f"PromptBlock '{m_id}' not found.",
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED},
                )

        target_locale = str(context.metadata.get("target_locale", "en"))
        static_instructions = self.compiler.compile_static_instructions(criteria_blocks, target_locale)
        dynamic_instructions = self.compiler.compile_dynamic_instructions(criteria_blocks, target_locale)

        # Epic 12: Generate Thick XML/Markdown rubrics for System Prompt
        xml_rubrics = self.compiler.compile_xml_rubrics(criteria_blocks, target_locale)

        # Epic 13 M2: Resolve tools and build dynamic instruction
        effective_mcp_tools = step_obj.allowed_mcp_tools
        mcp_instruction = self.compiler.generate_mcp_instruction(effective_mcp_tools)

        system_prompt = "Complete the evaluation according to the provided schema."
        if static_instructions:
            system_prompt += f"\n\n{static_instructions}"
        if xml_rubrics:
            system_prompt += f"\n\n{xml_rubrics}"
        if mcp_instruction:
            system_prompt += f"\n\n{mcp_instruction}"

        # 3. Prevent Token Explosion with fold_trace pruning
        llm_context_data = state_data
        if trace:
            pruner = StateProjector()
            pruned_history = pruner.fold_trace(trace, max_tokens=20000)
            llm_context_data = {**pruned_history, **state_data}

        xml_ctx = self.compiler.build_xml_context(
            input_mappings=step.input_mappings if hasattr(step, "input_mappings") else {},
            state_data=llm_context_data,
            target_locale=target_locale,
            expected_inputs=context.expected_inputs,
        )

        user_payload = xml_ctx
        if dynamic_instructions:
            user_payload += f"\n\n--- RUNTIME AWARENESS ---\n{dynamic_instructions}"

        has_search = any("search_result" in v for v in state_data.values() if isinstance(v, dict))
        dynamic_schema = self.compiler.build_dynamic_schema(
            schema_name=f"Step_{step.id}_Response",
            criteria=criteria_blocks,
            has_search_result=has_search,
            target_locale=target_locale,
        )

        if frozen_ctx:
            frozen_ctx.generated_schemas[step.id] = dynamic_schema.model_json_schema()

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_payload},
        ]

        # 4. Invoke LLM Model (Tool Loop vs Direct Output)
        strategy_name = context.model_strategy
        if not strategy_name:
            logger.error(
                "Step has no model_strategy defined. Zero fallbacks allowed.",
                extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name, "step_id": step.id},
            )
            raise AppException(
                message=f"Step {step.id} has no model_strategy defined (Fail-Fast: No fallbacks allowed).",
                status_code=500,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR},
            )
        bound_client = await LLMClient.from_strategy(strategy_name, self.repository)

        final_dict: dict[str, Any] = {}
        usage_dict: dict[str, Any] = {}

        if effective_mcp_tools:
            # Inline import for MCP to avoid module load overhead unless explicitly utilized.
            from backend_v2.services.mcp.mcp_tool_loop import execute_tool_loop

            try:
                loop_result = await execute_tool_loop(
                    llm_client=bound_client,
                    messages=messages,
                    response_model=dynamic_schema,
                    allowed_tools=effective_mcp_tools,
                    step_name=step.id,
                    mock_identity=step.id,
                    target_language=target_locale,
                    synthesis_instructions=state_data.get("synthesis_instructions"),
                )
                final_dict = dict(loop_result.result_data)
                usage_dict = dict(loop_result.usage) if loop_result.usage else {}

                if frozen_ctx and loop_result.audit_traces:
                    # Deduplicate at the orchestrator root to prevent DB bloat across DAG retries or LLM loop confusions
                    existing_hashes = {
                        f"{a.tool_id}::{a.query}" for a in frozen_ctx.mcp_tool_audit
                    }
                    for trace in loop_result.audit_traces:
                        thash = f"{trace.tool_id}::{trace.query}"
                        if thash not in existing_hashes:
                            frozen_ctx.mcp_tool_audit.append(trace)
                            existing_hashes.add(thash)
            except Exception as e:
                logger.error(
                    "Execution of MCP tool loop failed.",
                    extra={
                        "error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL.name,
                        "step_id": step.id,
                        "detail": str(e),
                    },
                    exc_info=True,
                )
                if isinstance(e, AppException):
                    raise
                raise AppException(
                    message=f"MCP Tool Loop Execution failed: {str(e)}",
                    status_code=500,
                    details={"error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL},
                ) from e
        else:
            try:
                result, usage = await bound_client.run_structured_task(
                    messages=messages,
                    response_model=dynamic_schema,
                    mock_identity=step.id,
                )
                final_dict = dict(result.model_dump(mode="json"))
                usage_dict = dict(usage) if usage else {}
            except Exception as e:
                logger.error(
                    "Execution of structured LLM task failed.",
                    extra={
                        "error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL.name,
                        "step_id": step.id,
                        "detail": str(e),
                    },
                    exc_info=True,
                )
                if isinstance(e, AppException):
                    raise
                raise AppException(
                    message=f"Structured LLM execution failed: {str(e)}",
                    status_code=500,
                    details={"error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL},
                ) from e

        # 5. Post-Hooks
        safe_context = {
            k: v.model_dump(mode="json") if hasattr(v, "model_dump") else v for k, v in dict(projector.snapshot).items()
        }

        final_dict = await self.run_post_hooks(
            step_obj=step_obj,
            step=step,
            hook_state=hook_state,
            hook_deps=hook_deps,
            final_dict=final_dict,
            global_context_vars=safe_context,
        )

        # 6. Metadata Merging
        for key in ["profiler_metrics", "step_metadata", "_audit_signature"]:
            if key in state_data:
                final_dict[key] = state_data[key]

        if usage_dict:
            if "_step_metadata" not in final_dict:
                final_dict["_step_metadata"] = {}
            final_dict["_step_metadata"]["token_usage"] = usage_dict

        return [
            TraceEvent(
                step_name=step.id,
                event_type="output",
                content=final_dict,
            )
        ]
