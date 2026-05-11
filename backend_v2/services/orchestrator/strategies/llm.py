import asyncio
import json
import logging
import time
from typing import Any

from backend_v2.core.hook_registry import HookDependencies, HookState
from backend_v2.exceptions import AppException, ConfigurationError, ErrorCodes
from backend_v2.llm.client import LLMClient
from backend_v2.models.chunking import ChunkingRequest
from backend_v2.models.domain.usage import TokenUsage
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
        # Epic 43 Phase 2 Fail-Fast Parity: Re-inject 'inputs' and 'raw_inputs' DTO payloads into the root state
        # so legacy dot-notation mappings resolve properly without Naked Dict violations.
        inputs_payload = {d.block_id: d.payload for d in projector.snapshot if d.step_id == "inputs"}

        raw_inputs_payload = {d.block_id: d.payload for d in projector.snapshot if d.step_id == "raw_inputs"}

        current_state: dict[str, Any] = {
            "steps": projector.snapshot,
            "inputs": inputs_payload,
            "raw_inputs": raw_inputs_payload,
        }

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

        step_def = await self.workflow_repo.get_step_by_id(blueprint_id)
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
        hook_deps = HookDependencies(
            exec_repo=self.exec_repo,
            workflow_repo=self.workflow_repo,
            comp_repo=self.comp_repo,
            identity_repo=self.identity_repo,
            audit_repo=self.audit_repo,
            system_repo=self.system_repo,
        )

        # Extract input keys from context — ExpectedInput.input_key is a required typed field.
        input_keys = set()
        if context.expected_inputs:
            for ei in context.expected_inputs:
                input_keys.add(ei.input_key)

        state_data = current_state

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
        all_prompt_blocks_raw = await self.comp_repo.get_all_prompt_blocks()
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

        if "profile_id" not in context.metadata or not context.metadata["profile_id"]:
            msg = f"Execution metadata missing mandatory 'profile_id' for workflow {context.workflow_id}."
            raise ConfigurationError(msg, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value})
        target_profile = context.metadata["profile_id"]

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

        if "target_locale" not in context.metadata or not context.metadata["target_locale"]:
            msg = f"Execution metadata missing mandatory 'target_locale' for workflow {context.workflow_id}."
            raise ConfigurationError(msg, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value})
        target_locale = str(context.metadata["target_locale"])
        effective_mcp_tools = step_obj.allowed_mcp_tools

        # StepRule.input_mappings has default_factory=dict — always present, no guard needed.
        input_mappings = dict(step.input_mappings)

        workflow_def = await self.workflow_repo.get_workflow(context.workflow_id)
        output_profile = None
        schema_map = {}
        if workflow_def:
            workflow_obj = Workflow.model_validate(workflow_def)
            if target_profile in workflow_obj.output_profiles:
                output_profile = workflow_obj.output_profiles[target_profile]

            for s in workflow_obj.steps:
                is_matrix = False
                blueprint_def = await self.workflow_repo.get_step(s.task_blueprint)
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
            schema_map["inputs"] = _SCHEMA_BLOCK_TEXT
            schema_map["raw_inputs"] = _SCHEMA_BLOCK_TEXT

        criteria_blocks = criteria_blocks_models

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
        bound_client = await LLMClient.from_strategy(strategy_name, self.system_repo)

        sem = asyncio.Semaphore(SystemConcurrency.MAX_CONCURRENT_LLM_STEPS.value)

        # Step 4 & 5 - Map-Reduce and Accumulation with Anomaly Circuit Breaker
        MAX_RETRIES = 2
        retry_count = 0
        final_dict = {}
        usage_agg = TokenUsage()
        latency_ms = 0

        while retry_count <= MAX_RETRIES:
            telemetry_start_time = time.time()
            context_char_length = len(user_payload)
            logger.info(
                "Epic 27 Telemetry: Compiling map-reduce for step '%s'. "
                "Context Bounds: %d chars, Chunk count: %d. (Attempt %d)",
                step.id,
                context_char_length,
                len(chunks_list),
                retry_count + 1,
            )

            syn_instr = state_data["synthesis_instructions"] if "synthesis_instructions" in state_data else None

            # Map Phase: Distribute to Arq Workers
            redis = self.arq_pool
            hkey = f"exec:{context.execution_id}:step:{step.id}"

            # Reset Redis accumulator state just in case of retry
            if redis:
                await redis.delete(hkey)

            if redis:
                for i, c in enumerate(chunks_list):
                    # In real production, file_path would be passed instead of reading the whole text
                    # Here we pass user_payload as the payload due to mock limitations
                    await redis.enqueue_job(
                        "evaluate_chunk_job",
                        context.execution_id,
                        step.id,
                        i,
                        len(chunks_list),
                        None,  # file_path
                        c.items,
                        [b.model_dump() for b in criteria_blocks],
                        base_system_prompt,
                        has_search,
                        has_shuffled_atoms,
                        atom_to_block_ids,
                        effective_mcp_tools,
                        target_locale,
                        syn_instr,
                        context.strictness_level,
                    )

                # Wait Phase: Poll Redis for Completion (Synchronous Block)
                while True:
                    completed = await redis.hget(hkey, "completed")
                    if int(completed or 0) == len(chunks_list):
                        break
                    await asyncio.sleep(1)
            else:
                # Fallback to TaskGroup if Redis is not configured (e.g. tests)
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
                                    synthesis_instructions=syn_instr,
                                    output_profile=None,
                                    strictness_level=context.strictness_level,
                                )
                            )
                        )

            latency_ms = int((time.time() - telemetry_start_time) * 1000)

            # Step 5 - Accumulation & Hooks
            accumulator = ChunkAccumulator()
            usage_agg = TokenUsage()

            # Reduce Phase: Pull chunks from Redis or Tasks
            from backend_v2.models.state import TraceEvent
            from backend_v2.models.v2_core import MCPAuditTrace

            if redis:
                all_chunks = await redis.hgetall(hkey)
                for i in range(len(chunks_list)):
                    chunk_data_str = all_chunks.get(f"chunk_{i}".encode(), b"{}")
                    chunk_data = json.loads(chunk_data_str)

                    c_final = chunk_data.get("final", {})
                    c_usage_dict = chunk_data.get("usage")
                    c_traces_dict = chunk_data.get("traces", [])

                    accumulator.add(c_final)

                    if c_usage_dict:
                        usage_agg = usage_agg + TokenUsage.model_validate(c_usage_dict)

                    if frozen_ctx and c_traces_dict:
                        existing_hashes = {f"{a.tool_id}::{a.query}" for a in frozen_ctx.mcp_tool_audit}
                        for tr_dict in c_traces_dict:
                            t_trace = MCPAuditTrace.model_validate(tr_dict)
                            thash = f"{t_trace.tool_id}::{t_trace.query}"
                            if thash not in existing_hashes:
                                frozen_ctx.mcp_tool_audit.append(t_trace)
                                existing_hashes.add(thash)
            else:
                for t in tasks:
                    c_final, c_usage, c_traces = t.result()

                    accumulator.add(c_final)

                    if c_usage is not None:
                        usage_agg = usage_agg + c_usage

                    if frozen_ctx and c_traces:
                        existing_hashes = {f"{a.tool_id}::{a.query}" for a in frozen_ctx.mcp_tool_audit}
                        for t_trace in c_traces:
                            thash = f"{t_trace.tool_id}::{t_trace.query}"
                            if thash not in existing_hashes:
                                frozen_ctx.mcp_tool_audit.append(t_trace)
                                existing_hashes.add(thash)

            final_dict = accumulator.get_final_result()

            safe_context: dict[str, Any] = {"steps": projector.snapshot}

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

            if final_dict.get("llm_anomaly_retry_requested"):
                retry_count += 1
                if retry_count > MAX_RETRIES:
                    logger.warning(
                        "[LLMStrategy] Max retries (%d) exceeded for step '%s'. Swallowing anomaly.",
                        MAX_RETRIES,
                        step.id,
                    )
                    final_dict["anomaly_unresolved"] = True
                    final_dict.pop("llm_anomaly_retry_requested", None)
                    break
                else:
                    logger.info(
                        "[LLMStrategy] LLM Anomaly Retry triggered for step '%s'. Attempt %d/%d.",
                        step.id,
                        retry_count,
                        MAX_RETRIES,
                    )

                    # Dispatch SSE to client: {"status": "processing", "message_code": "event_llm_anomaly_retry"}
                    # Accomplished by updating the step_states in the database directly.
                    exec_record = await self.exec_repo.get_execution(context.execution_id)
                    if exec_record and step.id in exec_record.step_states:
                        new_state = exec_record.step_states[step.id].model_copy(
                            update={"status": "processing", "message_code": "event_llm_anomaly_retry"}
                        )
                        new_states = {**exec_record.step_states, step.id: new_state}
                        new_states_raw = {k: v.model_dump(mode="json") for k, v in new_states.items()}
                        await self.exec_repo.update_execution(context.execution_id, {"step_states": new_states_raw})
                    continue

            break

        for key in ["profiler_metrics", "step_metadata", "_audit_signature"]:
            if key in state_data:
                final_dict[key] = state_data[key]

        if usage_agg.total_tokens > 0 or usage_agg.cost_usd > 0.0:
            if "_step_metadata" not in final_dict:
                final_dict["_step_metadata"] = {}
            final_dict["_step_metadata"]["token_usage"] = usage_agg.model_dump()

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
