"""Stage 3 LLMClient binding, MCP tool retrieval, and bounded engine anomaly retry loop."""

from __future__ import annotations

import logging
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from pydantic import BaseModel

from backend_v2.core.hook_registry import ExecutionInputsDTO, HookDependencies, HookState
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.client import LLMClient
from backend_v2.models.domain.inputs import DomainInputValue
from backend_v2.models.domain.mcp import MCPRetrievalResultDTO
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock, PromptBlock
from backend_v2.models.domain.step import Step, StepRule
from backend_v2.models.domain.system_config import MCPAuditTrace, SystemConfigMCPGateways
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.dtos.causal_discovery import CausalGraphPayloadDTO
from backend_v2.models.dtos.engine import EngineExecutionRequest, EngineExecutionResult, MatrixEvaluationContext
from backend_v2.models.dtos.hook_delta import StepContextMetadataDTO
from backend_v2.models.dtos.trace import ExecutionUpdateDTO
from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.llm import LLMMessageDTO
from backend_v2.models.state import TraceEvent
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.mcp.dispatcher import ToolDispatcher
from backend_v2.services.mcp.mcp_tool_loop import execute_mcp_retrieval
from backend_v2.services.orchestrator.engines.synthesis_engine import SynthesisEngine
from backend_v2.services.orchestrator.strategies.base import StrategyContext, StrategyDependencies
from backend_v2.services.orchestrator.strategies.llm_strategy.blueprint_and_metadata_stage import (
    BlueprintStageResult,
    extract_step_context_metadata,
)
from backend_v2.services.orchestrator.strategies.llm_strategy.prompt_and_schema_stage import (
    PromptAndSchemaStageResult,
)
from backend_v2.settings import Settings, get_settings

if TYPE_CHECKING:
    from backend_v2.services.orchestrator.engines.base import ExecutionEngine

__all__ = ["EngineRetryStageResult", "execute_engine_retry_stage"]

logger = logging.getLogger(__name__)
_ZERO_USAGE = TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0)

type PostHooksRunner = Callable[..., Awaitable[tuple[HookState, list[TraceEvent]]]]
type MCPRetrievalRunner = Callable[..., Awaitable[MCPRetrievalResultDTO]]
type StepMetadataExtractor = Callable[[HookState, StrategyContext | None], StepContextMetadataDTO]


@dataclass(frozen=True)
class EngineRetryStageResult:
    """Immutable output container for Stage 3 engine retry loop and MCP retrieval.

    Attributes:
        hook_state: Resulting HookState after executing step post-hooks.
        final_dict: Normalized step output dictionary mapping keys to DomainInputValue.
        post_events: Ordered list of TraceEvents emitted by post-hooks.
        engine_result: Result container returned by the configured ExecutionEngine.
        mcp_audit_traces: List of MCP tool execution audit traces collected before engine invocation.
        bound_client: Bound LLMClient instance resolved from the step's cognitive tier.
        retrieval_usage: Aggregated TokenUsage consumed during pre-execution MCP retrieval.
        usage_agg: Combined TokenUsage across MCP retrieval and engine execution.
        latency_ms: Measured execution latency in milliseconds for the final engine attempt.
        context_char_length: Character length of the compiled user payload sent to the engine.
        dynamic_schema: Dynamically compiled Pydantic response schema when applicable.
        prompt_contexts: List of prompt context strings recorded for trace metadata.
    """

    hook_state: HookState
    final_dict: dict[str, DomainInputValue]
    post_events: list[TraceEvent]
    engine_result: EngineExecutionResult | None
    mcp_audit_traces: list[MCPAuditTrace]
    bound_client: LLMClient | None = None
    retrieval_usage: TokenUsage = field(default_factory=lambda: _ZERO_USAGE)
    usage_agg: TokenUsage = field(default_factory=lambda: _ZERO_USAGE)
    latency_ms: int = 0
    context_char_length: int = 0
    dynamic_schema: type[BaseModel] | None = None
    prompt_contexts: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class _MCPRetrievalEnrichment:
    """Immutable container for pre-execution MCP retrieval enrichment outputs.

    Attributes:
        user_payload: Enriched user payload string including MCP evidence when present.
        global_source_text: Enriched source text string including MCP evidence when present.
        retrieval_usage: TokenUsage consumed by MCP tool loop synthesis.
        mcp_audit_traces: Collected MCPAuditTrace records from tool invocations.
    """

    user_payload: str
    global_source_text: str
    retrieval_usage: TokenUsage
    mcp_audit_traces: list[MCPAuditTrace]


@dataclass(frozen=True)
class _PreparedEngineInvocation:
    """Immutable container holding the constructed EngineExecutionRequest and dynamic schema.

    Attributes:
        engine_request: Configured EngineExecutionRequest ready for engine execution.
        dynamic_schema: Compiled Pydantic response schema when synthesized dynamically, else None.
    """

    engine_request: EngineExecutionRequest
    dynamic_schema: type[BaseModel] | None


@dataclass(frozen=True)
class _PostHooksExecutionOutcome:
    """Immutable container holding the post-hook state, emitted events, and normalized output dict.

    Attributes:
        post_hook_state: Updated HookState returned by step post-hooks.
        post_events: TraceEvent list emitted during post-hook execution.
        final_dict: Normalized output mapping extracted from post_hook_state.
    """

    post_hook_state: HookState
    post_events: list[TraceEvent]
    final_dict: dict[str, DomainInputValue]


async def _run_optional_mcp_retrieval(
    *,
    step_obj: Step,
    step: StepRule,
    stage1: BlueprintStageResult,
    stage2: PromptAndSchemaStageResult,
    context: StrategyContext,
    deps: StrategyDependencies,
    bound_client: LLMClient,
    mcp_retrieval_fn: MCPRetrievalRunner,
) -> _MCPRetrievalEnrichment:
    """Execute optional MCP tool loop retrieval and enrich user_payload and global_source_text.

    Args:
        step_obj: Validated Step blueprint entity defining allowed_mcp_tools.
        step: Active workflow StepRule.
        stage1: Resolved Stage 1 blueprint and pre-hook output container.
        stage2: Resolved Stage 2 prompt compilation and schema output container.
        context: Strategy configuration parameters.
        deps: Strategy dependencies container holding system_repo and prompt_compiler.
        bound_client: Bound LLMClient instance for MCP argument synthesis.
        mcp_retrieval_fn: Injectable MCP retrieval coroutine.

    Returns:
        _MCPRetrievalEnrichment containing updated payloads, token usage, and audit traces.
    """
    user_payload = stage2.user_payload
    global_source_text = stage1.global_source_text
    if not step_obj.allowed_mcp_tools:
        return _MCPRetrievalEnrichment(
            user_payload=user_payload,
            global_source_text=global_source_text,
            retrieval_usage=_ZERO_USAGE,
            mcp_audit_traces=[],
        )

    raw_gateways = await deps.system_repo.get_all_mcp_gateways()
    active_gateways: list[SystemConfigMCPGateways] = []
    if isinstance(raw_gateways, list):
        active_gateways = [g for g in raw_gateways if isinstance(g, SystemConfigMCPGateways)]
    src_ctx = global_source_text if global_source_text else user_payload
    retrieval_result = await mcp_retrieval_fn(
        llm_client=bound_client,
        executor=LLMTaskExecutor(prompt_compiler=deps.prompt_compiler),
        messages=[LLMMessageDTO(role="user", content=src_ctx)],
        allowed_tools=step_obj.allowed_mcp_tools,
        step_name=step.id,
        target_language=stage1.target_locale,
        validation_context={"strictness_level": context.strictness_level},
        source_context=src_ctx,
        alias_engine=stage2.alias_engine,
        repository=deps.system_repo,
        dispatcher=ToolDispatcher(gateways=active_gateways),
        mcp_tool_params=step_obj.mcp_tool_params,
    )
    if not retrieval_result.audit_traces:
        return _MCPRetrievalEnrichment(
            user_payload=user_payload,
            global_source_text=global_source_text,
            retrieval_usage=_ZERO_USAGE,
            mcp_audit_traces=[],
        )

    enriched_user_payload = (
        f"{user_payload}\n\n{retrieval_result.evidence_payload}" if user_payload else retrieval_result.evidence_payload
    )
    enriched_source_text = (
        f"{global_source_text}\n\n{retrieval_result.evidence_payload}"
        if global_source_text
        else retrieval_result.evidence_payload
    )
    return _MCPRetrievalEnrichment(
        user_payload=enriched_user_payload,
        global_source_text=enriched_source_text,
        retrieval_usage=retrieval_result.usage,
        mcp_audit_traces=list(retrieval_result.audit_traces),
    )


def _prepare_engine_invocation(
    *,
    step: StepRule,
    context: StrategyContext,
    deps: StrategyDependencies,
    engine: ExecutionEngine,
    bound_client: LLMClient,
    criteria_blocks: list[PromptBlock],
    hook_state: HookState,
    user_payload: str,
    global_source_text: str,
    target_locale: str,
    stage2: PromptAndSchemaStageResult,
    progress_callback: Callable[[int, int], Awaitable[None]] | None,
    request_cls: Callable[..., EngineExecutionRequest],
    extract_metadata_fn: StepMetadataExtractor,
) -> _PreparedEngineInvocation:
    """Construct EngineExecutionRequest and compile dynamic schema for synthesis or non-matrix steps.

    Args:
        step: Rule defining the workflow execution block configuration.
        context: Strategy configuration parameters.
        deps: Strategy dependencies container holding prompt_compiler.
        engine: Configured ExecutionEngine instance.
        bound_client: Bound LLMClient instance.
        criteria_blocks: Resolved criteria PromptBlock models.
        hook_state: Active HookState before engine invocation.
        user_payload: Enriched user payload string.
        global_source_text: Enriched global source document text.
        target_locale: Resolved Stage 1 target locale code.
        stage2: Resolved Stage 2 prompt compilation and schema output container.
        progress_callback: Optional async callback reporting item progress.
        request_cls: Injectable EngineExecutionRequest constructor.
        extract_metadata_fn: Injectable step context metadata extractor callable.

    Returns:
        _PreparedEngineInvocation containing the EngineExecutionRequest and optional dynamic_schema.
    """
    matrix_block = next((b for b in criteria_blocks if isinstance(b, MatrixPromptBlock)), None)
    matrix_block_id: str | None = None
    matrix_context: MatrixEvaluationContext | None = None
    if matrix_block is not None:
        matrix_block_id = matrix_block.id
        matrix_context = MatrixEvaluationContext(
            theory_grounding=matrix_block.theory_grounding,
            matrix_objective=matrix_block.ai_description,
            allow_contextual_override=matrix_block.allow_contextual_override,
        )

    is_synthesis_step = isinstance(engine, SynthesisEngine)
    dynamic_schema: type[BaseModel] | None = None
    hydrated_messages: list[LLMMessageDTO] | None = None
    req_sys_prompt, req_locale = user_payload, target_locale

    if is_synthesis_step or matrix_block is None:
        req_locale = context.target_locale
        step_meta = extract_metadata_fn(hook_state, context)
        expected_sdui_type = "grid"
        if step.expected_sdui_type is not None and step.expected_sdui_type.strip():
            expected_sdui_type = step.expected_sdui_type
        dynamic_schema = deps.prompt_compiler.build_dynamic_schema(
            schema_name=f"Step_{step.id}_Response",
            criteria=criteria_blocks,
            has_shuffled_atoms=False,
            target_locale=req_locale,
            strictness_level=context.strictness_level,
            source_document_ids=step_meta.doc_aliases,
            expected_sdui_type=expected_sdui_type,
            dag_results=step_meta.dag_results,
        )
        static_instructions = deps.prompt_compiler.compile_static_instructions(criteria_blocks, req_locale)
        static_msg = LLMMessageDTO(role="system", content=static_instructions)
        if is_synthesis_step:
            hydrated_messages, req_sys_prompt = [static_msg], ""
        else:
            hydrated_messages = [static_msg, LLMMessageDTO(role="user", content=user_payload)]

    engine_request = request_cls(
        bound_client=bound_client,
        compiled_schema=dynamic_schema,
        hydrated_messages=hydrated_messages,
        system_prompt=req_sys_prompt,
        step=step,
        context=context,
        global_source_text=global_source_text,
        target_locale=req_locale,
        progress_callback=progress_callback,
        trace_callback=None,
        prompt_compiler=deps.prompt_compiler,
        shuffled_atoms=stage2.hydrated_shuffled_atoms,
        matrix_block_id=matrix_block_id,
        matrix_context=matrix_context,
    )
    return _PreparedEngineInvocation(engine_request=engine_request, dynamic_schema=dynamic_schema)


def _extract_engine_result_dict(engine_result: EngineExecutionResult) -> dict[str, DomainInputValue]:
    """Normalize EngineExecutionResult into a dictionary of DomainInputValue entries.

    Args:
        engine_result: Result container returned by ExecutionEngine.execute().

    Returns:
        Dictionary mapping output keys to DomainInputValue payloads.
    """
    if engine_result.synthesis_output is not None:
        if isinstance(engine_result.synthesis_output, BaseModel):
            if isinstance(engine_result.synthesis_output, CausalGraphPayloadDTO):
                return {"graph": engine_result.synthesis_output}
            return engine_result.synthesis_output.model_dump(exclude_none=True)
        if not isinstance(engine_result.synthesis_output, (str, int, float, bool, list)):
            return {k: v for k, v in engine_result.synthesis_output.items() if v is not None}
        return {"output": engine_result.synthesis_output}
    return {"results": engine_result.results, "hydrated_references": engine_result.hydrated_references}


async def _run_step_post_hooks(
    *,
    step_obj: Step,
    step: StepRule,
    hook_state: HookState,
    hook_deps: HookDependencies,
    initial_final_dict: dict[str, DomainInputValue],
    run_post_hooks_fn: PostHooksRunner,
) -> _PostHooksExecutionOutcome:
    """Execute step post-hooks and extract the updated final_dict mapping.

    Args:
        step_obj: Validated Step blueprint entity.
        step: Active workflow StepRule.
        hook_state: Pre-execution HookState to copy into post-hook inputs.
        hook_deps: HookDependencies container for post-hook execution.
        initial_final_dict: Normalized engine output dictionary before post-hooks.
        run_post_hooks_fn: Bound post-hook runner coroutine.

    Returns:
        _PostHooksExecutionOutcome containing post_hook_state, post_events, and final_dict.
    """
    post_target_locale: str | None = None
    post_user_role: str | None = None
    if isinstance(hook_state.inputs, ExecutionInputsDTO):
        post_target_locale, post_user_role = hook_state.inputs.target_locale, hook_state.inputs.user_role

    candidate_hook_state = hook_state.model_copy(
        update={
            "global_context_vars": hook_state.global_context_vars,
            "inputs": ExecutionInputsDTO(
                dynamic_inputs=initial_final_dict,
                raw_inputs=initial_final_dict,
                target_locale=post_target_locale,
                user_role=post_user_role,
            ),
        }
    )
    post_hook_state, post_events = await run_post_hooks_fn(
        step_obj=step_obj, step=step, hook_state=candidate_hook_state, hook_deps=hook_deps
    )
    final_dict: dict[str, DomainInputValue]
    if isinstance(post_hook_state.inputs, ExecutionInputsDTO):
        final_dict = dict(post_hook_state.inputs.dynamic_inputs)
    elif not isinstance(post_hook_state.inputs, (str, int, float, bool, list)) and post_hook_state.inputs is not None:
        final_dict = dict(post_hook_state.inputs)
    else:
        final_dict = {}
    if post_hook_state.global_context_vars and post_hook_state.global_context_vars.evaluative_matrices:
        final_dict["_evaluative_matrices"] = post_hook_state.global_context_vars.evaluative_matrices
        final_dict["evaluative_matrices"] = post_hook_state.global_context_vars.evaluative_matrices
    return _PostHooksExecutionOutcome(
        post_hook_state=post_hook_state,
        post_events=post_events,
        final_dict=final_dict,
    )


async def _persist_anomaly_retry_status(
    *,
    execution_id: str,
    step_id: str,
    deps: StrategyDependencies,
) -> None:
    """Persist RUNNING status and event_llm_anomaly_retry message_code on ExecutionRecord.

    Args:
        execution_id: Active execution identifier.
        step_id: Active StepRule identifier.
        deps: Strategy dependencies container holding exec_repo.
    """
    exec_record = await deps.exec_repo.get_execution(execution_id)
    if exec_record is not None and step_id in exec_record.step_states:
        new_state = exec_record.step_states[step_id].model_copy(
            update={"status": ExecutionStatus.RUNNING, "message_code": "event_llm_anomaly_retry"}
        )
        await deps.exec_repo.update_execution(
            execution_id,
            ExecutionUpdateDTO(step_states={**exec_record.step_states, step_id: new_state}),
        )


async def execute_engine_retry_stage(
    *,
    stage1: BlueprintStageResult,
    stage2: PromptAndSchemaStageResult,
    step: StepRule,
    context: StrategyContext,
    deps: StrategyDependencies,
    engine: ExecutionEngine | None,
    run_post_hooks_fn: PostHooksRunner,
    progress_callback: Callable[[int, int], Awaitable[None]] | None = None,
    request_cls: Callable[..., EngineExecutionRequest] = EngineExecutionRequest,
    mcp_retrieval_fn: MCPRetrievalRunner = execute_mcp_retrieval,
    extract_metadata_fn: StepMetadataExtractor = extract_step_context_metadata,
    settings_getter: Callable[[], Settings] = get_settings,
    step_logger: logging.Logger = logger,
) -> EngineRetryStageResult:
    """Execute Stage 3 LLMClient binding, MCP tool retrieval, and bounded engine retry loop.

    Args:
        stage1: Resolved Stage 1 blueprint and pre-hook output container.
        stage2: Resolved Stage 2 prompt compilation and schema output container.
        step: Rule defining the workflow execution block configuration.
        context: Strategy configuration parameters (model, metadata, strictness).
        deps: Strategy dependencies container holding repositories and compiler.
        engine: Configured ExecutionEngine instance.
        run_post_hooks_fn: Bound post-hook runner coroutine from the strategy instance.
        progress_callback: Optional async callback reporting processed and total item progress.
        request_cls: Injectable EngineExecutionRequest constructor for test spy compatibility.
        mcp_retrieval_fn: Injectable MCP retrieval coroutine for test spy compatibility.
        extract_metadata_fn: Injectable step context metadata extractor callable.
        settings_getter: Callable returning global Settings SSOT.
        step_logger: Logger instance used to preserve logger name parity in logs.

    Returns:
        EngineRetryStageResult containing final_dict, post_events, engine_result, and telemetry.

    Raises:
        AppException: With ErrorCodes.CONFIGURATION_ERROR when cognitive_tier or engine is missing,
            or propagated from MCP retrieval and engine execution.
    """
    # Validate mandatory cognitive_tier before binding LLMClient via Model Registry.
    if not context.cognitive_tier:
        step_logger.error(
            "Step has no cognitive_tier defined. Zero fallbacks allowed.",
            exc_info=True,
            extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name, "step_id": step.id},
        )
        raise AppException(
            message=f"Step {step.id} has no cognitive_tier defined (Fail-Fast: No fallbacks allowed).",
            status_code=500,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
        )
    bound_client = await LLMClient.from_tier(
        context.cognitive_tier,
        deps.system_repo,
        provider=context.metadata.provider_override,
        registry_id=context.model_registry_id,
        pipeline_name="chunk_worker",
    )
    enrichment = await _run_optional_mcp_retrieval(
        step_obj=stage1.step_obj,
        step=step,
        stage1=stage1,
        stage2=stage2,
        context=context,
        deps=deps,
        bound_client=bound_client,
        mcp_retrieval_fn=mcp_retrieval_fn,
    )
    user_payload = enrichment.user_payload
    global_source_text = enrichment.global_source_text
    retrieval_usage = enrichment.retrieval_usage
    mcp_audit_traces = enrichment.mcp_audit_traces

    max_retries = settings_getter().llm_max_retries
    retry_count, latency_ms, context_char_length = 0, 0, len(user_payload)
    final_dict: dict[str, DomainInputValue] = {}
    post_events: list[TraceEvent] = []
    engine_result: EngineExecutionResult | None = None
    dynamic_schema = stage2.dynamic_schema
    usage_agg, post_hook_state = retrieval_usage, stage2.hook_state

    while retry_count <= max_retries:
        telemetry_start_time = time.time()
        context_char_length = len(user_payload)
        step_logger.info(
            "Map-reduce execution telemetry for step '%s'. Context Bounds: %d chars, Chunk count: %d. (Attempt %d)",
            step.id,
            context_char_length,
            len(stage2.target_chunks),
            retry_count + 1,
        )
        if engine is None:
            msg = "LLMNodeStrategy has no ExecutionEngine configured."
            step_logger.error(
                "[LLMStrategy] %s: %s",
                ErrorCodes.CONFIGURATION_ERROR.name,
                msg,
                exc_info=True,
                extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name, "step_id": step.id},
            )
            raise AppException(
                message=msg, status_code=500, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value}
            )

        prepared = _prepare_engine_invocation(
            step=step,
            context=context,
            deps=deps,
            engine=engine,
            bound_client=bound_client,
            criteria_blocks=stage2.criteria_blocks,
            hook_state=stage2.hook_state,
            user_payload=user_payload,
            global_source_text=global_source_text,
            target_locale=stage1.target_locale,
            stage2=stage2,
            progress_callback=progress_callback,
            request_cls=request_cls,
            extract_metadata_fn=extract_metadata_fn,
        )
        dynamic_schema = prepared.dynamic_schema
        engine_result = await engine.execute(prepared.engine_request)
        initial_final_dict = _extract_engine_result_dict(engine_result)

        latency_ms = int((time.time() - telemetry_start_time) * 1000)
        engine_usage = engine_result.usage if engine_result.usage is not None else _ZERO_USAGE
        usage_agg = retrieval_usage + engine_usage

        post_outcome = await _run_step_post_hooks(
            step_obj=stage1.step_obj,
            step=step,
            hook_state=stage2.hook_state,
            hook_deps=stage1.hook_deps,
            initial_final_dict=initial_final_dict,
            run_post_hooks_fn=run_post_hooks_fn,
        )
        post_hook_state = post_outcome.post_hook_state
        post_events = post_outcome.post_events
        final_dict = post_outcome.final_dict

        if "llm_anomaly_retry_requested" in final_dict and final_dict["llm_anomaly_retry_requested"]:
            retry_count += 1
            if retry_count > max_retries:
                step_logger.warning(
                    "[LLMStrategy] Max retries (%d) exceeded for step '%s'. Swallowing anomaly.", max_retries, step.id
                )
                final_dict["anomaly_unresolved"] = True
                del final_dict["llm_anomaly_retry_requested"]
                break
            step_logger.info(
                "[LLMStrategy] LLM Anomaly Retry triggered for step '%s'. Attempt %d/%d.",
                step.id,
                retry_count,
                max_retries,
            )
            await _persist_anomaly_retry_status(
                execution_id=context.execution_id,
                step_id=step.id,
                deps=deps,
            )
            continue
        break

    return EngineRetryStageResult(
        hook_state=post_hook_state,
        final_dict=final_dict,
        post_events=post_events,
        engine_result=engine_result,
        mcp_audit_traces=mcp_audit_traces,
        bound_client=bound_client,
        retrieval_usage=retrieval_usage,
        usage_agg=usage_agg,
        latency_ms=latency_ms,
        context_char_length=context_char_length,
        dynamic_schema=dynamic_schema,
        prompt_contexts=[],
    )
