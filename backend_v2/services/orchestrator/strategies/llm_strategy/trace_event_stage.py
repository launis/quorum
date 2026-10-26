"""Stage 4 telemetry metric merging, StepTraceMetadataDTO hydration, and TraceEvent emission."""

from __future__ import annotations

from typing import TYPE_CHECKING

from backend_v2.models.domain.step import StepRule
from backend_v2.models.dtos.trace import StepTraceMetadataDTO, TraceEventMetadataDTO
from backend_v2.models.enums import CognitiveTier, VirtualSystemStepID
from backend_v2.models.state import TraceEvent
from backend_v2.services.orchestrator.strategies.llm_strategy.blueprint_and_metadata_stage import (
    BlueprintStageResult,
)
from backend_v2.services.orchestrator.strategies.llm_strategy.engine_retry_stage import (
    EngineRetryStageResult,
)
from backend_v2.services.orchestrator.strategies.llm_strategy.prompt_and_schema_stage import (
    PromptAndSchemaStageResult,
)

if TYPE_CHECKING:
    from backend_v2.services.orchestrator.engines.base import ExecutionEngine

__all__ = ["build_llm_step_trace_events"]


def build_llm_step_trace_events(
    *,
    stage1: BlueprintStageResult,
    stage2: PromptAndSchemaStageResult,
    stage3: EngineRetryStageResult,
    step: StepRule,
    engine: ExecutionEngine | None = None,
) -> list[TraceEvent]:
    """Assemble final step TraceEvent list from Stage 1, Stage 2, and Stage 3 results.

    Args:
        stage1: Resolved Stage 1 blueprint and pre-hook output container.
        stage2: Resolved Stage 2 prompt compilation and chunking output container.
        stage3: Resolved Stage 3 engine retry loop and MCP retrieval output container.
        step: Rule defining the workflow execution block configuration.
        engine: Optional configured ExecutionEngine instance for telemetry_strategy_label resolution.

    Returns:
        Ordered list of pre-hook, post-hook, and step output TraceEvents.
    """
    # Phase 3, Step 1: Merge state_data keys, hydrate StepTraceMetadataDTO, and emit TraceEvents
    state_data = stage1.state_data
    step_obj = stage1.step_obj
    retrieval_usage = stage3.retrieval_usage
    usage_agg = stage3.usage_agg

    if (
        usage_agg.total_tokens == 0
        and usage_agg.cost_usd == 0.0
        and stage3.engine_result is not None
        and stage3.engine_result.usage is not None
    ):
        usage_agg = retrieval_usage + stage3.engine_result.usage

    if VirtualSystemStepID.STEP_METADATA.value in state_data:
        meta_dto = StepTraceMetadataDTO.model_validate(state_data[VirtualSystemStepID.STEP_METADATA.value])
    elif "_step_metadata" in stage3.final_dict:
        meta_dto = StepTraceMetadataDTO.model_validate(stage3.final_dict["_step_metadata"])
    else:
        meta_dto = StepTraceMetadataDTO()

    model_strategy = "unknown"
    if engine is not None:
        raw_label = engine.telemetry_strategy_label
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
    if stage3.bound_client and isinstance(stage3.bound_client.model_name, str):
        physical_model_val = stage3.bound_client.model_name

    effective_token_usage = meta_dto.token_usage
    if effective_token_usage is None:
        if usage_agg.total_tokens > 0 or usage_agg.cost_usd > 0.0:
            effective_token_usage = usage_agg
    elif retrieval_usage.total_tokens > 0 or retrieval_usage.cost_usd > 0.0:
        effective_token_usage = effective_token_usage + retrieval_usage

    meta_dto = StepTraceMetadataDTO(
        task_blueprint=step.task_blueprint,
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
    final_dict = serialized_meta.copy()
    final_dict.clear()
    final_dict.update(stage3.final_dict)
    for key in ["profiler_metrics", VirtualSystemStepID.STEP_METADATA.value, "_audit_signature"]:
        if key in state_data:
            final_dict[key] = state_data[key]
    final_dict["_step_metadata"] = serialized_meta
    final_dict["step_metadata"] = serialized_meta

    generated_schema = None
    if stage3.dynamic_schema is not None:
        generated_schema = stage3.dynamic_schema.model_json_schema()

    trace_metadata = TraceEventMetadataDTO(
        latency_ms=stage3.latency_ms,
        chunk_size=len(stage2.target_chunks),
        context_char_length=stage3.context_char_length,
        prompt_contexts=stage3.prompt_contexts,
        generated_schema=generated_schema,
    )
    output_event = TraceEvent(
        step_name=step.id,
        event_type="output",
        content=final_dict,
        metadata=trace_metadata,
        mcp_audit_traces=stage3.mcp_audit_traces,
    )
    return [*stage1.pre_events, *stage3.post_events, output_event]
