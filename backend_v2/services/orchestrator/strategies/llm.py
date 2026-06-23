"""LLM Node Strategy for DAG-based workflow execution.

Orchestrates AI/LLM step execution including dynamic schema compilation,
chunked map-reduce evaluation, DLQ graceful degradation, and anomaly retry logic.
"""

import asyncio
import json
import logging
import time
from typing import Any, cast

from backend_v2.core.hook_registry import HookDependencies, HookState
from backend_v2.exceptions import AppException, ConfigurationError, ErrorCodes
from backend_v2.llm.client import LLMClient
from backend_v2.models.chunking import ChunkingRequest
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.enums import SystemConcurrency
from backend_v2.models.state import StateProjector, TraceEvent
from backend_v2.models.v2_core import FrozenContext, MCPAuditTrace, PromptBlock, StepRule, Workflow
from backend_v2.models.v2_core import Step as V2Step
from backend_v2.services.orchestrator.chunk_accumulator import ChunkAccumulator
from backend_v2.services.orchestrator.chunking_service import ChunkingService
from backend_v2.services.orchestrator.strategies.base import NodeStrategy, StrategyContext
from backend_v2.services.orchestrator.strategies.llm_execution.chunk_worker import ChunkWorker
from backend_v2.services.orchestrator.strategies.llm_execution.context_builder import ContextBuilder
from backend_v2.services.orchestrator.strategies.llm_execution.prompt_factory import PromptFactory

logger = logging.getLogger(__name__)

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
        semaphore: asyncio.Semaphore,
        running_event: asyncio.Event | None = None,
    ) -> list[TraceEvent]:
        """Executes the node's workflow sequence matching system rules.

        Args:
            step: Rule defining the workflow execution block configuration.
            projector: Database representation of current structured historical trace.
            context: Strategy configuration parameters (model, metadata, strictness).
            frozen_ctx: Accumulator state matching prompt caches and MCP traces.
            trace: List of chronological events.
            semaphore: Concurrency limiter for model executions.
            running_event: Cancellation trigger for async processes.

        Returns:
            List containing the computed outputs packed into structured TraceEvents.

        Raises:
            AppException: Triggered upon infrastructure failure, database corruption, or model invalidity.
            ConfigurationError: Triggered upon incorrect configuration schemas.
        """
        inputs_payload = {d.block_id: d.payload for d in projector.snapshot if d.step_id == "inputs"}
        raw_inputs_payload = {d.block_id: d.payload for d in projector.snapshot if d.step_id == "raw_inputs"}

        texts: list[str] = []
        inputs_dict = inputs_payload.get("inputs", {})
        if isinstance(inputs_dict, dict):
            for v in inputs_dict.values():
                if isinstance(v, str):
                    texts.append(v)
        elif isinstance(inputs_dict, str):
            texts.append(inputs_dict)

        global_source_text = "\n\n".join(texts)
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

        step_def_raw = await self.workflow_repo.get_step_by_id(blueprint_id)
        step_def = cast(dict[str, Any], step_def_raw)
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

        input_keys: set[str] = set()
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
            global_context_vars=context.global_context_vars,
            inputs=state_data,
        )

        hook_state = await self.run_pre_hooks(step_obj, step, hook_state, hook_deps)
        state_data = hook_state.inputs.copy()

        all_prompt_blocks_raw = await self.comp_repo.get_all_prompt_blocks()
        all_prompt_blocks: list[PromptBlock] = []
        for raw in all_prompt_blocks_raw:
            try:
                all_prompt_blocks.append(PromptBlock.model_validate(raw))
            except Exception as e:
                logger.error(
                    "[LLMStrategy] Malformed PromptBlock in DB — Fail-Fast.",
                    exc_info=True,
                    extra={"error_code": ErrorCodes.VALIDATION_FAILED.name},
                )
                raise AppException(
                    message="Malformed PromptBlock in DB",
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                ) from e

        block_map = {b.id: b for b in all_prompt_blocks if b.id}

        if "profile_id" not in context.metadata or not context.metadata["profile_id"]:
            msg = f"Execution metadata missing mandatory 'profile_id' for workflow {context.workflow_id}."
            raise ConfigurationError(msg, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value})
        target_profile = context.metadata["profile_id"]

        role_block = None
        if step_obj.role_block_id:
            role_block = block_map[step_obj.role_block_id] if step_obj.role_block_id in block_map else None
            if not role_block:
                raise ConfigurationError(
                    f"Role Block '{step_obj.role_block_id}' not found.",
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                )

        protocol_block = None
        if step_obj.extraction_protocol_block_id:
            protocol_block = (
                block_map[step_obj.extraction_protocol_block_id]
                if step_obj.extraction_protocol_block_id in block_map
                else None
            )
            if not protocol_block:
                raise ConfigurationError(
                    f"Extraction Protocol Block '{step_obj.extraction_protocol_block_id}' not found.",
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                )

        execution_persona_block = None
        if step_obj.execution_persona_block_id:
            execution_persona_block = (
                block_map[step_obj.execution_persona_block_id]
                if step_obj.execution_persona_block_id in block_map
                else None
            )
            if not execution_persona_block:
                raise ConfigurationError(
                    f"Execution Persona Block '{step_obj.execution_persona_block_id}' not found.",
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                )

        criteria_blocks_models: list[PromptBlock] = []
        for m_id in step_obj.criteria_block_ids:
            b = block_map[m_id] if m_id in block_map else None
            if b:
                criteria_blocks_models.append(b)
            else:
                logger.error(
                    f"Criteria PromptBlock '{m_id}' not found.",
                    extra={"error_code": ErrorCodes.VALIDATION_FAILED.name, "step_id": step.id},
                )
                raise AppException(
                    message=f"Criteria PromptBlock '{m_id}' not found.",
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )

        # Phase 4 Step 3: Wire Best-of-Three ensemble flag
        is_lightweight = any(block.is_lightweight_protocol for block in criteria_blocks_models)
        if is_lightweight:
            if hook_state.metadata is None:
                hook_state.metadata = {}
            hook_state.metadata["is_lightweight_extraction"] = True

        if "target_locale" not in context.metadata or not context.metadata["target_locale"]:
            msg = f"Execution metadata missing mandatory 'target_locale' for workflow {context.workflow_id}."
            raise ConfigurationError(msg, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value})
        target_locale = str(context.metadata["target_locale"])
        effective_mcp_tools = step_obj.allowed_mcp_tools

        input_mappings = dict(step.input_mappings)

        workflow_def_raw = await self.workflow_repo.get_workflow(context.workflow_id)
        workflow_def = cast(dict[str, Any], workflow_def_raw)
        output_profile = None
        schema_map: dict[str, str] = {}
        if workflow_def:
            workflow_obj = Workflow.model_validate(workflow_def)
            if target_profile in workflow_obj.output_profiles:
                output_profile = workflow_obj.output_profiles[target_profile]

            for s in workflow_obj.steps:
                is_matrix = False
                blueprint_def_raw = await self.workflow_repo.get_step(s.task_blueprint)
                blueprint_def = cast(dict[str, Any], blueprint_def_raw)
                if blueprint_def:
                    blueprint_obj = V2Step.model_validate(blueprint_def)
                    all_bp_blocks: list[str] = []
                    if blueprint_obj.role_block_id:
                        all_bp_blocks.append(blueprint_obj.role_block_id)
                    if blueprint_obj.extraction_protocol_block_id:
                        all_bp_blocks.append(blueprint_obj.extraction_protocol_block_id)
                    if blueprint_obj.execution_persona_block_id:
                        all_bp_blocks.append(blueprint_obj.execution_persona_block_id)
                    all_bp_blocks.extend(blueprint_obj.criteria_block_ids)

                    for m_id in all_bp_blocks:
                        b = block_map[m_id] if m_id in block_map else None
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

        criteria_blocks = sorted(criteria_blocks_models, key=lambda x: str(x.id or ""))

        llm_context_data, new_input_mappings = ContextBuilder.build(
            input_mappings=input_mappings,
            state_data=state_data,
            output_profile=output_profile,
            schema_map=schema_map,
            criteria_blocks=criteria_blocks,
        )
        input_mappings = new_input_mappings

        has_shuffled_atoms = False
        is_matrix_step = any(b.category_id == "matrix" for b in criteria_blocks_models)
        if is_matrix_step and "shuffled_atoms" in state_data:
            shuffled_atoms = state_data["shuffled_atoms"]
            if isinstance(shuffled_atoms, list) and len(shuffled_atoms) > 0:
                has_shuffled_atoms = True

        prompt_payload = PromptFactory.build(
            compiler=self.compiler,
            role_block=role_block,
            protocol_block=protocol_block,
            execution_persona_block=execution_persona_block,
            criteria_blocks=criteria_blocks,
            target_locale=target_locale,
            effective_mcp_tools=effective_mcp_tools,
            input_mappings=input_mappings,
            llm_context_data=llm_context_data,
            expected_inputs=context.expected_inputs,
            has_shuffled_atoms=has_shuffled_atoms,
            execution_id=context.execution_id,
        )

        user_payload = prompt_payload.user_payload
        base_system_prompt = prompt_payload.base_system_prompt
        atom_to_block_ids = prompt_payload.atom_to_block_ids

        chunks_list: list[Any] = []

        if is_matrix_step and "shuffled_atoms" in state_data:
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
            chunks_list = [None]

        has_search = any("search_result" in v for v in state_data.values() if type(v) is dict)

        if frozen_ctx:
            global_schema = self.compiler.build_dynamic_schema(
                schema_name=f"Step_{step.id}_Response",
                criteria=criteria_blocks,
                has_search_result=has_search,
                has_shuffled_atoms=has_shuffled_atoms,
                target_locale=target_locale,
                strictness_level=context.strictness_level,
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

        sem = semaphore

        MAX_RETRIES = SystemConcurrency.LLM_MAX_RETRIES
        retry_count = 0
        final_dict: dict[str, Any] = {}
        usage_agg = TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0)
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

            if "synthesis_instructions" in state_data:
                syn_instr = state_data["synthesis_instructions"]
            else:
                syn_instr = None

            redis = None
            hkey = f"exec:{context.execution_id}:step:{step.id}"

            if redis:
                await redis.delete(hkey)

            if redis:
                for i, c in enumerate(chunks_list):
                    await redis.enqueue_job(
                        "evaluate_chunk_job",
                        context.execution_id,
                        step.id,
                        i,
                        len(chunks_list),
                        None,
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
                        hook_state.metadata,
                    )

                while True:
                    completed = await redis.hget(hkey, "completed")
                    if int(completed or 0) == len(chunks_list):
                        break
                    await asyncio.sleep(1)
            else:
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
                                    global_source_text=global_source_text,
                                    base_system_prompt=base_system_prompt,
                                    has_search=has_search,
                                    has_shuffled_atoms=has_shuffled_atoms,
                                    atom_to_block_ids=atom_to_block_ids,
                                    effective_mcp_tools=effective_mcp_tools,
                                    bound_client=bound_client,
                                    step_id=step.id,
                                    target_locale=target_locale,
                                    synthesis_instructions=syn_instr,
                                    output_profile=output_profile,
                                    strictness_level=context.strictness_level,
                                    running_event=running_event,
                                    step_metadata=hook_state.metadata,
                                )
                            )
                        )

                # Task results parsed after TaskGroup completes clean context boundaries.
                task_results = [t.result() for t in tasks]

            latency_ms = int((time.time() - telemetry_start_time) * 1000)

            accumulator = ChunkAccumulator()
            usage_agg = TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0)
            all_prompt_contexts: list[dict[str, Any]] = []

            if redis:
                all_chunks = await redis.hgetall(hkey)
                for i in range(len(chunks_list)):
                    chunk_key = f"chunk_{i}".encode()
                    chunk_data_str = all_chunks[chunk_key] if chunk_key in all_chunks else b"{}"
                    chunk_data = json.loads(chunk_data_str)

                    c_final = chunk_data["final"] if "final" in chunk_data else {}
                    c_usage_dict = chunk_data["usage"] if "usage" in chunk_data else None
                    c_traces_dict = chunk_data["traces"] if "traces" in chunk_data else []
                    c_prompt_context_dict = chunk_data.get("prompt_context")

                    if isinstance(c_final, dict):
                        if c_final.get("_dlq_status") == "FAILED/DLQ":
                            reason = c_final["reason"] if "reason" in c_final else "Unknown DLQ Failure"
                            logger.warning(
                                f"[Orchestrator] Step execution failed in chunk {i} and routed to DLQ. "
                                f"Continuing orchestrator run with degraded data. Reason: {reason}",
                                extra={"error_code": ErrorCodes.WORKFLOW_EXECUTION_FAILED.name},
                            )
                            # Phase 4, Step 2: Allow accumulator to proceed instead of raising AppException
                        elif c_final.get("_dlq_retry_count", 0) > 0:
                            logger.info(
                                "[Orchestrator] Chunk recovered after %d transient retries.",
                                c_final["_dlq_retry_count"],
                            )
                    accumulator.add(c_final)

                    if c_usage_dict:
                        c_usage = TokenUsage.model_validate(c_usage_dict)
                        usage_agg = usage_agg + c_usage
                        retries = c_final.get("_dlq_retry_count", 0) if isinstance(c_final, dict) else 0
                        logger.info(
                            f"[Chunk Success] Step {step.id} | Prompt tokens: {c_usage.prompt_tokens} | Completion tokens: {c_usage.completion_tokens} | Cached: {c_usage.cached_tokens} | Cost: ${c_usage.cost_usd:.4f} | Retries: {retries}",
                            extra={"error_code": "CHUNK_SUCCESS"},
                        )

                    if c_prompt_context_dict:
                        all_prompt_contexts.append(c_prompt_context_dict)

                    if frozen_ctx and c_traces_dict:
                        existing_hashes = {f"{a.tool_id}::{a.query}" for a in frozen_ctx.mcp_tool_audit}
                        for tr_dict in c_traces_dict:
                            t_trace = MCPAuditTrace.model_validate(tr_dict)
                            thash = f"{t_trace.tool_id}::{t_trace.query}"
                            if thash not in existing_hashes:
                                frozen_ctx.mcp_tool_audit.append(t_trace)
                                existing_hashes.add(thash)
            else:
                for c_final, c_usage, c_traces, c_prompt_context in task_results:
                    if isinstance(c_final, dict):
                        if c_final.get("_dlq_status") == "FAILED/DLQ":
                            reason = c_final["reason"] if "reason" in c_final else "Unknown DLQ Failure"
                            logger.warning(
                                "[Orchestrator] Step execution failed in task chunk and routed to DLQ. "
                                f"Continuing orchestrator run with degraded data. Reason: {reason}",
                                extra={"error_code": ErrorCodes.WORKFLOW_EXECUTION_FAILED.name},
                            )
                            # Phase 4, Step 2: Allow accumulator to proceed instead of raising AppException
                        elif c_final.get("_dlq_retry_count", 0) > 0:
                            logger.info(
                                "[Orchestrator] Chunk recovered after %d transient retries.",
                                c_final["_dlq_retry_count"],
                            )
                    accumulator.add(c_final)

                    if c_usage is not None:
                        usage_agg = usage_agg + c_usage
                        retries = c_final.get("_dlq_retry_count", 0) if isinstance(c_final, dict) else 0
                        logger.info(
                            f"[Chunk Success] Step {step.id} | Prompt tokens: {c_usage.prompt_tokens} | Completion tokens: {c_usage.completion_tokens} | Cached: {c_usage.cached_tokens} | Cost: ${c_usage.cost_usd:.4f} | Retries: {retries}",
                            extra={"error_code": "CHUNK_SUCCESS"},
                        )

                    if c_prompt_context:
                        all_prompt_contexts.append(c_prompt_context.model_dump())

                    if frozen_ctx and c_traces:
                        existing_hashes = {f"{a.tool_id}::{a.query}" for a in frozen_ctx.mcp_tool_audit}
                        for t_trace in c_traces:
                            thash = f"{t_trace.tool_id}::{t_trace.query}"
                            if thash not in existing_hashes:
                                frozen_ctx.mcp_tool_audit.append(t_trace)
                                existing_hashes.add(thash)

            final_dict = accumulator.get_final_result()
            safe_context: dict[str, Any] = {**hook_state.global_context_vars, "steps": projector.snapshot}

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
            final_dict = post_hook_state.inputs.copy()

            if "llm_anomaly_retry_requested" in final_dict and final_dict["llm_anomaly_retry_requested"]:
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

                    exec_record_raw = await self.exec_repo.get_execution(context.execution_id)
                    exec_record = cast(Any, exec_record_raw)
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
            meta = final_dict.setdefault("_step_metadata", {})
            meta["token_usage"] = usage_agg.model_dump()
            # Phase 1, Step 1.1: Ensure model_strategy is persisted in trace event metadata for execution fingerprinting
            meta["model_strategy"] = strategy_name

        return [
            TraceEvent(
                step_name=step.id,
                event_type="output",
                content=final_dict,
                metadata={
                    "latency_ms": latency_ms,
                    "chunk_size": len(chunks_list),
                    "context_char_length": context_char_length,
                    "prompt_contexts": all_prompt_contexts,
                },
            )
        ]
