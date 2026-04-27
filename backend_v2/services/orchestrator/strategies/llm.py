import asyncio
import logging
import time
from typing import Any

from backend_v2.core.hook_registry import HookDependencies, HookState
from backend_v2.exceptions import AppException, ConfigurationError, ErrorCodes
from backend_v2.llm.client import LLMClient
from backend_v2.models.chunking import ChunkingRequest
from backend_v2.models.enums import SystemConcurrency
from backend_v2.models.state import StateProjector, TraceEvent
from backend_v2.models.v2_core import FrozenContext, PromptBlock, StepRule, Workflow
from backend_v2.models.v2_core import Step as V2Step
from backend_v2.services.orchestrator.chunk_accumulator import ChunkAccumulator
from backend_v2.services.orchestrator.chunking_service import ChunkingService
from backend_v2.services.orchestrator.strategies.base import NodeStrategy, StrategyContext
from backend_v2.services.orchestrator.strategies.llm_execution.chunk_worker import ChunkWorker
from backend_v2.services.orchestrator.strategies.llm_execution.context_builder import ContextBuilder
from backend_v2.services.orchestrator.strategies.llm_execution.prompt_factory import PromptFactory

logger = logging.getLogger(__name__)

# Internal schema routing tokens — used to classify DAG step outputs without duck-typing.
# These values are consumed by ContextBuilder; do NOT rename without updating that module.
_SCHEMA_BLOCK_MATRIX = "MATRIX"
_SCHEMA_BLOCK_TEXT = "TEXT"
_SCHEMA_BLOCK_EXTENSION = "EXTENSION"
_SCHEMA_BLOCK_SYSTEM = "SYSTEM"


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

        blueprint_id = step.task_blueprint
        if not blueprint_id:
            logger.error(
                "Step has no task_blueprint configured.",
                extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name, "step_id": step.id},
            )
            raise AppException(
                message=f"Step {step.id} has no task_blueprint configured.",
                status_code=500,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
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
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )

        step_obj = V2Step.model_validate(step_def)
        hook_deps = HookDependencies(repository=self.repository)

        # Extract input keys from context — ExpectedInput.input_key is a required typed field.
        input_keys = set()
        if context.expected_inputs:
            for ei in context.expected_inputs:
                input_keys.add(ei.input_key)

        # Exclude inputs from the $steps container to prevent matrix parsing crashes and context pollution
        step_outputs = {}
        for k, v in current_state.items():
            if k not in input_keys and k not in ["inputs", "raw_inputs"]:
                step_outputs[k] = v

        # Restore V1 namespace structure for state_data so ContextBuilder can resolve `$steps` and `$inputs`
        state_data = {"steps": step_outputs}
        for key in ["inputs", "raw_inputs"]:
            if key in current_state:
                state_data[key] = current_state[key]

        # Provide all keys at root level for global input mapping
        # (InputProcessingHook writes to root)
        for k, v in current_state.items():
            if k not in state_data:
                state_data[k] = v

        hook_state = HookState(
            execution_id=context.execution_id,
            workflow_id=context.workflow_id,
            step_id=step.id,
            task_blueprint=blueprint_id,
            metadata=context.metadata,
            global_context_vars={},
            inputs=state_data,
        )

        # 1. Pre-Hooks
        hook_state = await self.run_pre_hooks(step_obj, step, hook_state, hook_deps)
        state_data = dict(hook_state.inputs)

        # 2. Extract configuration criteria
        all_prompt_blocks_raw = await self.repository.get_all_prompt_blocks()
        all_prompt_blocks = []
        for raw in all_prompt_blocks_raw:
            try:
                all_prompt_blocks.append(PromptBlock.model_validate(raw))
            except Exception as e:
                logger.error(
                    "[LLMStrategy] Malformed PromptBlock in DB — Fail-Fast.",
                    extra={"error_code": ErrorCodes.VALIDATION_FAILED.name},
                    exc_info=e,
                )
                raise

        block_map = {b.id: b for b in all_prompt_blocks if b.id}

        target_profile = context.metadata.get("profile_id")
        if not target_profile:
            msg = f"Execution metadata missing mandatory 'profile_id' for workflow {context.workflow_id}."
            raise ConfigurationError(msg, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value})

        criteria_blocks_models = []
        for m_id in step_obj.prompt_blocks:
            b = block_map.get(m_id)
            if b:
                criteria_blocks_models.append(b)
            else:
                logger.error(
                    f"PromptBlock '{m_id}' not found.",
                    extra={"error_code": ErrorCodes.VALIDATION_FAILED.name, "step_id": step.id},
                )
                raise AppException(
                    message=f"PromptBlock '{m_id}' not found.",
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )

        target_locale = context.metadata.get("target_locale")
        if not target_locale:
            msg = f"Execution metadata missing mandatory 'target_locale' for workflow {context.workflow_id}."
            raise ConfigurationError(msg, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value})
        target_locale = str(target_locale)
        effective_mcp_tools = step_obj.allowed_mcp_tools

        # StepRule.input_mappings has default_factory=dict — always present, no guard needed.
        input_mappings = dict(step.input_mappings)

        workflow_def = await self.repository.get_workflow(context.workflow_id)
        output_profile = None
        schema_map = {}
        if workflow_def:
            workflow_obj = Workflow.model_validate(workflow_def)
            output_profile = workflow_obj.output_profiles.get(target_profile)

            for s in workflow_obj.steps:
                is_matrix = False
                blueprint_def = await self.repository.get_step(s.task_blueprint)
                if blueprint_def:
                    blueprint_obj = V2Step.model_validate(blueprint_def)
                    for m_id in blueprint_obj.prompt_blocks:
                        b = block_map.get(m_id)
                        if b:
                            if b.category_id == "matrix":
                                is_matrix = True
                                schema_map[m_id] = _SCHEMA_BLOCK_MATRIX
                            else:
                                schema_map[m_id] = _SCHEMA_BLOCK_TEXT

                            if b.output_extensions:
                                for ext in b.output_extensions:
                                    schema_map[ext] = _SCHEMA_BLOCK_EXTENSION

                schema_map[s.id] = _SCHEMA_BLOCK_MATRIX if is_matrix else _SCHEMA_BLOCK_TEXT

            schema_map["_step_metadata"] = _SCHEMA_BLOCK_SYSTEM
            schema_map["_audit_signature"] = _SCHEMA_BLOCK_SYSTEM

        # Export back to dict for legacy consumers that haven't been hardened yet
        criteria_blocks = [b.model_dump(mode="json") for b in criteria_blocks_models]

        # Step 1 - Context Building
        llm_context_data, new_input_mappings = ContextBuilder.build(
            input_mappings=input_mappings,
            state_data=state_data,
            output_profile=output_profile,
            schema_map=schema_map,
        )
        input_mappings = new_input_mappings

        # Step 2 - Prompt Construction
        prompt_payload = PromptFactory.build(
            compiler=self.compiler,
            criteria_blocks=criteria_blocks,
            target_locale=target_locale,
            effective_mcp_tools=effective_mcp_tools,
            input_mappings=input_mappings,
            llm_context_data=llm_context_data,
            expected_inputs=context.expected_inputs,
        )

        user_payload = prompt_payload.user_payload
        base_system_prompt = prompt_payload.base_system_prompt
        atom_to_block_ids = prompt_payload.atom_to_block_ids

        # Step 3 - Chunk execution setup
        has_shuffled_atoms = False
        chunks_list: list[Any] = []

        # Epic 32: Prevent state leakage. Only chunk if the current step actually contains matrix blocks.
        is_matrix_step = any(b.category_id == "matrix" for b in criteria_blocks_models)

        if is_matrix_step and "shuffled_atoms" in state_data:
            has_shuffled_atoms = True
            shuffled_atoms = state_data["shuffled_atoms"]

            if not isinstance(shuffled_atoms, list) or len(shuffled_atoms) == 0:
                msg = f"Strict Fail-Fast Enforced: 'shuffled_atoms' is empty or not a list for step '{step.id}'."
                logger.error("[LLMStrategy] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                raise AppException(
                    message=msg,
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )

            req = ChunkingRequest[dict[str, Any]](
                parent_id=context.workflow_id,
                items=shuffled_atoms,
                max_chunk_size=SystemConcurrency.LLM_MAX_CHUNK_SIZE.value,
            )
            chunks_list = ChunkingService.chunk_payload(req)
        else:
            chunks_list = [None]  # Dummy to execute single non-chunk payload

        has_search = any("search_result" in v for v in state_data.values() if isinstance(v, dict))

        if frozen_ctx:
            global_schema = self.compiler.build_dynamic_schema(
                schema_name=f"Step_{step.id}_Response",
                criteria=criteria_blocks,
                has_search_result=has_search,
                has_shuffled_atoms=has_shuffled_atoms,
                target_locale=target_locale,
            )
            frozen_ctx.generated_schemas[step.id] = global_schema.model_json_schema()

        strategy_name = context.model_strategy
        if not strategy_name:
            logger.error(
                "Step has no model_strategy defined. Zero fallbacks allowed.",
                extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name, "step_id": step.id},
            )
            raise AppException(
                message=f"Step {step.id} has no model_strategy defined (Fail-Fast: No fallbacks allowed).",
                status_code=500,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )
        bound_client = await LLMClient.from_strategy(strategy_name, self.repository)

        sem = asyncio.Semaphore(SystemConcurrency.MAX_CONCURRENT_LLM_STEPS.value)

        telemetry_start_time = time.time()
        context_char_length = len(user_payload)
        logger.info(
            "Epic 27 Telemetry: Compiling map-reduce for step '%s'. Context Bounds: %d chars, Chunk count: %d.",
            step.id,
            context_char_length,
            len(chunks_list),
        )

        # Step 4 - Map-Reduce (ChunkWorker)
        tasks = []
        async with asyncio.TaskGroup() as tg:
            for c in chunks_list:
                tasks.append(
                    tg.create_task(
                        ChunkWorker.process_chunk(
                            chunk=c,
                            sem=sem,
                            compiler=self.compiler,
                            criteria_blocks=criteria_blocks,
                            user_payload=user_payload,
                            base_system_prompt=base_system_prompt,
                            has_search=has_search,
                            has_shuffled_atoms=has_shuffled_atoms,
                            atom_to_block_ids=atom_to_block_ids,
                            effective_mcp_tools=effective_mcp_tools,
                            bound_client=bound_client,
                            step_id=step.id,
                            target_locale=target_locale,
                            synthesis_instructions=state_data.get("synthesis_instructions"),
                            output_profile=None,
                        )
                    )
                )

        latency_ms = int((time.time() - telemetry_start_time) * 1000)

        # Step 5 - Accumulation & Hooks
        accumulator = ChunkAccumulator()
        usage_dict: dict[str, Any] = {}

        for t in tasks:
            c_final, c_usage, c_traces = t.result()

            accumulator.add(c_final)

            if c_usage is not None:
                for k, v in c_usage.items():
                    usage_dict[k] = usage_dict.get(k, 0) + v

            if frozen_ctx and c_traces:
                existing_hashes = {f"{a.tool_id}::{a.query}" for a in frozen_ctx.mcp_tool_audit}
                for t_trace in c_traces:
                    thash = f"{t_trace.tool_id}::{t_trace.query}"
                    if thash not in existing_hashes:
                        frozen_ctx.mcp_tool_audit.append(t_trace)
                        existing_hashes.add(thash)

        final_dict = accumulator.get_final_result()

        safe_context = {
            k: v.model_dump(mode="json") if hasattr(v, "model_dump") else v for k, v in dict(projector.snapshot).items()
        }

        post_hook_state = hook_state.model_copy(
            update={
                "global_context_vars": safe_context,
                "inputs": final_dict,
            }
        )

        post_hook_state = await self.run_post_hooks(
            step_obj=step_obj,
            step=step,
            hook_state=post_hook_state,
            hook_deps=hook_deps,
        )
        final_dict = dict(post_hook_state.inputs)

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
                metadata={
                    "latency_ms": latency_ms,
                    "chunk_size": len(chunks_list),
                    "context_char_length": context_char_length,
                },
            )
        ]
