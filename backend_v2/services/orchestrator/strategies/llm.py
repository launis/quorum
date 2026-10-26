"""LLM Node Strategy for DAG-based workflow execution.

Orchestrates AI/LLM step execution including dynamic schema compilation,
chunked map-reduce evaluation, DLQ graceful degradation, and anomaly retry logic.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any, override

from pydantic import BaseModel

from backend_v2.settings import get_settings

if TYPE_CHECKING:
    from backend_v2.services.orchestrator.engines.base import ExecutionEngine

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    HookState,
)
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.client import LLMClient
from backend_v2.models.domain.execution import FrozenContext
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock
from backend_v2.models.domain.step import StepRule
from backend_v2.models.domain.system_config import MCPAuditTrace, SystemConfigMCPGateways
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.dtos.causal_discovery import CausalGraphPayloadDTO
from backend_v2.models.dtos.engine import EngineExecutionRequest, MatrixEvaluationContext
from backend_v2.models.dtos.hook_delta import StepContextMetadataDTO
from backend_v2.models.dtos.trace import ExecutionUpdateDTO, StepTraceMetadataDTO, TraceEventMetadataDTO
from backend_v2.models.enums import (
    CognitiveTier,
    ExecutionStatus,
    VirtualSystemStepID,
)
from backend_v2.models.llm import LLMMessageDTO
from backend_v2.models.state import StateProjector, TraceEvent
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.mcp.dispatcher import ToolDispatcher
from backend_v2.services.mcp.mcp_tool_loop import execute_mcp_retrieval
from backend_v2.services.orchestrator.engines.synthesis_engine import SynthesisEngine
from backend_v2.services.orchestrator.strategies.base import NodeStrategy, StrategyContext, StrategyDependencies
from backend_v2.services.orchestrator.strategies.llm_execution.context_builder import (
    ContextBuilder as ContextBuilder,
)
from backend_v2.services.orchestrator.strategies.llm_execution.prompt_factory import (
    PromptFactory as PromptFactory,
)
from backend_v2.services.orchestrator.strategies.llm_strategy.blueprint_and_metadata_stage import (
    _SCHEMA_BLOCK_EXTENSION as _SCHEMA_BLOCK_EXTENSION,
)
from backend_v2.services.orchestrator.strategies.llm_strategy.blueprint_and_metadata_stage import (
    _SCHEMA_BLOCK_MATRIX as _SCHEMA_BLOCK_MATRIX,
)
from backend_v2.services.orchestrator.strategies.llm_strategy.blueprint_and_metadata_stage import (
    _SCHEMA_BLOCK_SYSTEM as _SCHEMA_BLOCK_SYSTEM,
)
from backend_v2.services.orchestrator.strategies.llm_strategy.blueprint_and_metadata_stage import (
    _SCHEMA_BLOCK_TEXT as _SCHEMA_BLOCK_TEXT,
)
from backend_v2.services.orchestrator.strategies.llm_strategy.blueprint_and_metadata_stage import (
    BlueprintStageResult as BlueprintStageResult,
)
from backend_v2.services.orchestrator.strategies.llm_strategy.blueprint_and_metadata_stage import (
    NodeStatePayload as NodeStatePayload,
)
from backend_v2.services.orchestrator.strategies.llm_strategy.blueprint_and_metadata_stage import (
    dlq_handle_debug_log_error as dlq_handle_debug_log_error,
)
from backend_v2.services.orchestrator.strategies.llm_strategy.blueprint_and_metadata_stage import (
    execute_blueprint_and_pre_hooks_stage as execute_blueprint_and_pre_hooks_stage,
)
from backend_v2.services.orchestrator.strategies.llm_strategy.blueprint_and_metadata_stage import (
    extract_step_context_metadata as extract_step_context_metadata,
)
from backend_v2.services.orchestrator.strategies.llm_strategy.prompt_and_schema_stage import (
    PromptAndSchemaStageResult as PromptAndSchemaStageResult,
)
from backend_v2.services.orchestrator.strategies.llm_strategy.prompt_and_schema_stage import (
    execute_prompt_and_schema_stage as execute_prompt_and_schema_stage,
)

__all__ = [
    "BlueprintStageResult",
    "ContextBuilder",
    "LLMNodeStrategy",
    "NodeStatePayload",
    "PromptAndSchemaStageResult",
    "PromptFactory",
    "_SCHEMA_BLOCK_EXTENSION",
    "_SCHEMA_BLOCK_MATRIX",
    "_SCHEMA_BLOCK_SYSTEM",
    "_SCHEMA_BLOCK_TEXT",
    "dlq_handle_debug_log_error",
    "execute_blueprint_and_pre_hooks_stage",
    "execute_prompt_and_schema_stage",
    "extract_step_context_metadata",
]

logger = logging.getLogger(__name__)


class LLMNodeStrategy(NodeStrategy):
    """Executes an AI/LLM Step.

    Manages dynamic schema compilation, instruction aggregation, tracing optimization
    for token context explosion, and routes through either a standard structured prediction
    task or an autonomous MCP Tool Loop depending on step configuration.
    """

    def __init__(
        self,
        deps: StrategyDependencies,
        engine: ExecutionEngine | None = None,
    ) -> None:
        """Initialize the LLM strategy with StrategyDependencies and optional engine.

        Args:
            deps: Immutable container holding repositories, compiler, and pools.
            engine: Optional execution engine instance.
        """
        super().__init__(deps=deps)
        self._engine = engine

    @staticmethod
    def _dlq_handle_debug_log_error(exc: Exception) -> None:
        """Handle debug prompt logging failures in development gracefully.

        Args:
            exc: Exception encountered during debug prompt logging.
        """
        # Phase 1, Step 2: Delegate debug log error handler to blueprint_and_metadata_stage
        dlq_handle_debug_log_error(exc, step_logger=logger)

    def _extract_step_context_metadata(
        self,
        hook_state: HookState,
        context: StrategyContext | None = None,
    ) -> StepContextMetadataDTO:
        """Extract global vars, document aliases, and DAG input results from HookState.

        Args:
            hook_state: Ingress hook state holding inputs and context variables.
            context: Strategy configuration parameters holding context_variables.

        Returns:
            StepContextMetadataDTO containing gvars, doc_aliases, and dag_results.
        """
        # Phase 1, Step 2: Delegate step context metadata extraction to blueprint_and_metadata_stage
        return extract_step_context_metadata(hook_state, context)

    @override
    async def execute(
        self,
        step: StepRule,
        projector: StateProjector,
        context: StrategyContext,
        frozen_ctx: FrozenContext | None = None,
        trace: list[TraceEvent] | None = None,
        progress_callback: Callable[[int, int], Awaitable[None]] | None = None,
    ) -> list[TraceEvent]:
        """Executes the node's workflow sequence matching system rules.

        Args:
            step: Rule defining the workflow execution block configuration.
            projector: Database representation of current structured historical trace.
            context: Strategy configuration parameters (model, metadata, strictness).
            frozen_ctx: Accumulator state matching prompt caches and MCP traces.
            trace: List of chronological events.
            progress_callback: Optional async callback reporting processed and total item progress.

        Returns:
            List containing the computed outputs packed into structured TraceEvents.

        Raises:
            AppException: With ErrorCodes.CONFIGURATION_ERROR, ErrorCodes.VALIDATION_FAILED,
                or ErrorCodes.RESOURCE_NOT_FOUND upon missing configuration, invalid models, or missing records.
            ConfigurationError: With ErrorCodes.CONFIGURATION_ERROR upon missing mandatory step/profile blocks.
        """
        # Phase 1, Step 2: Delegate Stage 1 blueprint resolution and pre-hooks to blueprint_and_metadata_stage
        stage1 = await execute_blueprint_and_pre_hooks_stage(
            step=step,
            projector=projector,
            context=context,
            deps=self.deps,
            run_pre_hooks_fn=self.run_pre_hooks,
            step_logger=logger,
        )
        step_obj = stage1.step_obj
        hook_state = stage1.hook_state
        hook_deps = stage1.hook_deps
        pre_events = stage1.pre_events
        post_events: list[TraceEvent] = []
        target_locale = stage1.target_locale
        global_source_text = stage1.global_source_text
        state_data = stage1.state_data
        blueprint_id = step.task_blueprint
        effective_mcp_tools = step_obj.allowed_mcp_tools
        effective_mcp_tool_params = step_obj.mcp_tool_params

        # Phase 2, Step 2: Delegate Stage 2 context building, prompt compilation, and dynamic schema resolution
        stage2 = await execute_prompt_and_schema_stage(
            stage1=stage1,
            step=step,
            context=context,
            deps=self.deps,
            frozen_ctx=frozen_ctx,
            engine=self._engine,
            settings_getter=get_settings,
            step_logger=logger,
        )
        criteria_blocks = stage2.criteria_blocks
        hydrated_shuffled_atoms = stage2.hydrated_shuffled_atoms
        alias_engine = stage2.alias_engine
        user_payload = stage2.user_payload
        chunks_list = stage2.target_chunks
        dynamic_schema = stage2.dynamic_schema

        cognitive_tier = context.cognitive_tier
        if not cognitive_tier:
            logger.error(
                "Step has no cognitive_tier defined. Zero fallbacks allowed.",
                extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name, "step_id": step.id},
            )
            raise AppException(
                message=f"Step {step.id} has no cognitive_tier defined (Fail-Fast: No fallbacks allowed).",
                status_code=500,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )
        bound_client = await LLMClient.from_tier(
            cognitive_tier,
            self.system_repo,
            provider=context.metadata.provider_override,
            registry_id=context.model_registry_id,
            pipeline_name="chunk_worker",
        )

        mcp_audit_traces: list[MCPAuditTrace] = []
        retrieval_usage = TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0)

        if effective_mcp_tools:
            raw_gateways = await self.system_repo.get_all_mcp_gateways()
            active_gateways: list[SystemConfigMCPGateways] = []
            if isinstance(raw_gateways, list):
                active_gateways = [g for g in raw_gateways if isinstance(g, SystemConfigMCPGateways)]
            dispatcher = ToolDispatcher(gateways=active_gateways)
            task_executor = LLMTaskExecutor(prompt_compiler=self.compiler)
            retrieval_result = await execute_mcp_retrieval(
                llm_client=bound_client,
                executor=task_executor,
                messages=[LLMMessageDTO(role="user", content=global_source_text or user_payload)],
                allowed_tools=effective_mcp_tools,
                step_name=step.id,
                target_language=target_locale,
                validation_context={"strictness_level": context.strictness_level},
                source_context=global_source_text or user_payload,
                alias_engine=alias_engine,
                repository=self.system_repo,
                dispatcher=dispatcher,
                mcp_tool_params=effective_mcp_tool_params,
            )
            if retrieval_result.audit_traces:
                if user_payload:
                    user_payload = f"{user_payload}\n\n{retrieval_result.evidence_payload}"
                else:
                    user_payload = retrieval_result.evidence_payload

                if global_source_text:
                    global_source_text = f"{global_source_text}\n\n{retrieval_result.evidence_payload}"
                else:
                    global_source_text = retrieval_result.evidence_payload

                retrieval_usage = retrieval_result.usage
                mcp_audit_traces = list(retrieval_result.audit_traces)

        MAX_RETRIES = get_settings().llm_max_retries
        retry_count = 0
        final_dict = {}
        usage_agg = retrieval_usage
        latency_ms = 0

        while retry_count <= MAX_RETRIES:
            telemetry_start_time = time.time()
            context_char_length = len(user_payload)
            logger.info(
                "Map-reduce execution telemetry for step '%s'. Context Bounds: %d chars, Chunk count: %d. (Attempt %d)",
                step.id,
                context_char_length,
                len(chunks_list),
                retry_count + 1,
            )

            if self._engine is None:
                msg = "LLMNodeStrategy has no ExecutionEngine configured."
                logger.error(
                    "[LLMStrategy] %s: %s",
                    ErrorCodes.CONFIGURATION_ERROR.name,
                    msg,
                    extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name, "step_id": step.id},
                )
                raise AppException(
                    message=msg,
                    status_code=500,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                )

            matrix_block = next((b for b in criteria_blocks if isinstance(b, MatrixPromptBlock)), None)
            matrix_block_id: str | None = None
            if matrix_block is not None:
                matrix_block_id = matrix_block.id

            matrix_context = None
            if matrix_block:
                matrix_context = MatrixEvaluationContext(
                    theory_grounding=matrix_block.theory_grounding,
                    matrix_objective=matrix_block.ai_description,
                    allow_contextual_override=matrix_block.allow_contextual_override,
                )

            is_synthesis_step = isinstance(self._engine, SynthesisEngine)
            dynamic_schema = None

            if is_synthesis_step:
                target_locale = context.target_locale
                step_meta = self._extract_step_context_metadata(hook_state, context)
                doc_aliases = step_meta.doc_aliases
                dag_results = step_meta.dag_results
                expected_sdui_type = "grid"
                if step.expected_sdui_type is not None and step.expected_sdui_type.strip():
                    expected_sdui_type = step.expected_sdui_type

                dynamic_schema = self.compiler.build_dynamic_schema(
                    schema_name=f"Step_{step.id}_Response",
                    criteria=criteria_blocks,
                    has_shuffled_atoms=False,
                    target_locale=target_locale,
                    strictness_level=context.strictness_level,
                    source_document_ids=doc_aliases,
                    expected_sdui_type=expected_sdui_type,
                    dag_results=dag_results,
                )

                static_instructions = self.compiler.compile_static_instructions(criteria_blocks, target_locale)
                static_msg = LLMMessageDTO(role="system", content=static_instructions)

                engine_request = EngineExecutionRequest(
                    bound_client=bound_client,
                    compiled_schema=dynamic_schema,
                    hydrated_messages=[static_msg],
                    system_prompt="",
                    step=step,
                    context=context,
                    global_source_text=global_source_text,
                    target_locale=target_locale,
                    progress_callback=progress_callback,
                    trace_callback=None,
                    prompt_compiler=self.compiler,
                    shuffled_atoms=hydrated_shuffled_atoms,
                    matrix_block_id=matrix_block_id,
                    matrix_context=matrix_context,
                )
            elif matrix_block is None:
                target_locale = context.target_locale
                step_meta = self._extract_step_context_metadata(hook_state, context)
                doc_aliases = step_meta.doc_aliases
                dag_results = step_meta.dag_results
                expected_sdui_type = "grid"
                if step.expected_sdui_type is not None and step.expected_sdui_type.strip():
                    expected_sdui_type = step.expected_sdui_type

                dynamic_schema = self.compiler.build_dynamic_schema(
                    schema_name=f"Step_{step.id}_Response",
                    criteria=criteria_blocks,
                    has_shuffled_atoms=False,
                    target_locale=target_locale,
                    strictness_level=context.strictness_level,
                    source_document_ids=doc_aliases,
                    expected_sdui_type=expected_sdui_type,
                    dag_results=dag_results,
                )

                static_instructions = self.compiler.compile_static_instructions(criteria_blocks, target_locale)
                hydrated_messages = [
                    LLMMessageDTO(role="system", content=static_instructions),
                    LLMMessageDTO(role="user", content=user_payload),
                ]

                engine_request = EngineExecutionRequest(
                    bound_client=bound_client,
                    compiled_schema=dynamic_schema,
                    hydrated_messages=hydrated_messages,
                    system_prompt=user_payload,
                    step=step,
                    context=context,
                    global_source_text=global_source_text,
                    target_locale=target_locale,
                    progress_callback=progress_callback,
                    trace_callback=None,
                    prompt_compiler=self.compiler,
                    shuffled_atoms=hydrated_shuffled_atoms,
                    matrix_block_id=matrix_block_id,
                    matrix_context=matrix_context,
                )
            else:
                engine_request = EngineExecutionRequest(
                    bound_client=bound_client,
                    compiled_schema=None,
                    hydrated_messages=None,
                    system_prompt=user_payload,
                    step=step,
                    context=context,
                    global_source_text=global_source_text,
                    target_locale=target_locale,
                    progress_callback=progress_callback,
                    trace_callback=None,
                    prompt_compiler=self.compiler,
                    shuffled_atoms=hydrated_shuffled_atoms,
                    matrix_block_id=matrix_block_id,
                    matrix_context=matrix_context,
                )

            engine_result = await self._engine.execute(engine_request)

            if engine_result.synthesis_output is not None:
                if isinstance(engine_result.synthesis_output, BaseModel):
                    final_dict = engine_result.synthesis_output.model_dump(exclude_none=True)
                    if isinstance(engine_result.synthesis_output, CausalGraphPayloadDTO):
                        final_dict = {"graph": engine_result.synthesis_output}
                elif not isinstance(engine_result.synthesis_output, (str, int, float, bool, list)):
                    final_dict = {k: v for k, v in engine_result.synthesis_output.items() if v is not None}
                else:
                    final_dict = {"output": engine_result.synthesis_output}
            else:
                final_dict = {
                    "results": engine_result.results,
                    "hydrated_references": engine_result.hydrated_references,
                }

            latency_ms = int((time.time() - telemetry_start_time) * 1000)
            engine_usage = (
                engine_result.usage
                if engine_result.usage is not None
                else TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0)
            )
            usage_agg = retrieval_usage + engine_usage
            all_prompt_contexts: list[str] = []
            post_target_locale: str | None = None
            post_user_role: Any | None = None
            if isinstance(hook_state.inputs, ExecutionInputsDTO):
                post_target_locale = hook_state.inputs.target_locale
                post_user_role = hook_state.inputs.user_role

            post_hook_state = hook_state.model_copy(
                update={
                    "global_context_vars": hook_state.global_context_vars,
                    "inputs": ExecutionInputsDTO(
                        dynamic_inputs=final_dict,
                        raw_inputs=final_dict,
                        target_locale=post_target_locale,
                        user_role=post_user_role,
                    ),
                }
            )

            post_hook_state, post_events = await self.run_post_hooks(
                step_obj=step_obj,
                step=step,
                hook_state=post_hook_state,
                hook_deps=hook_deps,
            )
            if isinstance(post_hook_state.inputs, ExecutionInputsDTO):
                final_dict = dict(post_hook_state.inputs.dynamic_inputs)
            elif (
                not isinstance(post_hook_state.inputs, (str, int, float, bool, list))
                and post_hook_state.inputs is not None
            ):
                final_dict = dict(post_hook_state.inputs)
            else:
                final_dict = {}
            if post_hook_state.global_context_vars and post_hook_state.global_context_vars.evaluative_matrices:
                final_dict["_evaluative_matrices"] = post_hook_state.global_context_vars.evaluative_matrices
                final_dict["evaluative_matrices"] = post_hook_state.global_context_vars.evaluative_matrices

            if "llm_anomaly_retry_requested" in final_dict and final_dict["llm_anomaly_retry_requested"]:
                retry_count += 1
                if retry_count > MAX_RETRIES:
                    logger.warning(
                        "[LLMStrategy] Max retries (%d) exceeded for step '%s'. Swallowing anomaly.",
                        MAX_RETRIES,
                        step.id,
                    )
                    final_dict["anomaly_unresolved"] = True
                    if "llm_anomaly_retry_requested" in final_dict:
                        del final_dict["llm_anomaly_retry_requested"]
                    break
                else:
                    logger.info(
                        "[LLMStrategy] LLM Anomaly Retry triggered for step '%s'. Attempt %d/%d.",
                        step.id,
                        retry_count,
                        MAX_RETRIES,
                    )

                    exec_record = await self.exec_repo.get_execution(context.execution_id)
                    if exec_record is not None and step.id in exec_record.step_states:
                        new_state = exec_record.step_states[step.id].model_copy(
                            update={"status": ExecutionStatus.RUNNING, "message_code": "event_llm_anomaly_retry"}
                        )
                        new_states = {**exec_record.step_states, step.id: new_state}
                        await self.exec_repo.update_execution(
                            context.execution_id, ExecutionUpdateDTO(step_states=new_states)
                        )
                    continue

            break

        for key in ["profiler_metrics", VirtualSystemStepID.STEP_METADATA.value, "_audit_signature"]:
            if key in state_data:
                final_dict[key] = state_data[key]

        if "_step_metadata" in final_dict:
            meta_dto = StepTraceMetadataDTO.model_validate(final_dict["_step_metadata"])
        else:
            meta_dto = StepTraceMetadataDTO()

        model_strategy = "unknown"
        if self._engine is not None:
            raw_label = self._engine.telemetry_strategy_label
            if isinstance(raw_label, str):
                model_strategy = raw_label
            else:
                model_strategy = "prompt"

        cognitive_tier_val: str | None = None
        if isinstance(step_obj.cognitive_tier, CognitiveTier):
            cognitive_tier_val = step_obj.cognitive_tier.value
        elif isinstance(step_obj.cognitive_tier, str):
            cognitive_tier_val = step_obj.cognitive_tier

        physical_model_val: str | None = None
        if bound_client and isinstance(bound_client.model_name, str):
            physical_model_val = bound_client.model_name

        effective_token_usage = meta_dto.token_usage
        if effective_token_usage is None:
            if usage_agg.total_tokens > 0 or usage_agg.cost_usd > 0.0:
                effective_token_usage = usage_agg
        elif retrieval_usage.total_tokens > 0 or retrieval_usage.cost_usd > 0.0:
            effective_token_usage = effective_token_usage + retrieval_usage

        meta_dto = StepTraceMetadataDTO(
            task_blueprint=blueprint_id,
            model_strategy=model_strategy,
            cognitive_tier=cognitive_tier_val,
            physical_model=physical_model_val,
            token_usage=effective_token_usage,
            chunk_size=meta_dto.chunk_size,
            execution_id=meta_dto.execution_id,
            workflow_id=meta_dto.workflow_id,
            step_id=meta_dto.step_id,
            initiator_id=meta_dto.initiator_id,
            timestamp_isot=meta_dto.timestamp_isot,
            unix_time=meta_dto.unix_time,
            v2_engine=meta_dto.v2_engine,
            system_fingerprint=meta_dto.system_fingerprint,
        )
        serialized_meta = meta_dto.model_dump(exclude_none=True)
        final_dict["_step_metadata"] = serialized_meta
        final_dict["step_metadata"] = serialized_meta

        generated_schema = None
        if dynamic_schema is not None:
            generated_schema = dynamic_schema.model_json_schema()

        trace_metadata = TraceEventMetadataDTO(
            latency_ms=latency_ms,
            chunk_size=len(chunks_list),
            context_char_length=context_char_length,
            prompt_contexts=all_prompt_contexts,
            generated_schema=generated_schema,
        )
        return (
            pre_events
            + post_events
            + [
                TraceEvent(
                    step_name=step.id,
                    event_type="output",
                    content=final_dict,
                    metadata=trace_metadata,
                    mcp_audit_traces=mcp_audit_traces,
                )
            ]
        )
