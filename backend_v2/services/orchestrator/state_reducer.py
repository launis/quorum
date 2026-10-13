"""Pure state reduction utilities for orchestrator execution and dynamic inputs merging."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, cast

from pydantic import JsonValue

from backend_v2.models.domain.analyst import AnalystOutput
from backend_v2.models.domain.evaluation import EvaluationResult
from backend_v2.models.domain.interaction import InteractionAnalysisDTO
from backend_v2.models.domain.linguistics import LinguisticsResultDTO
from backend_v2.models.domain.metadata import (
    MetadataHookPayloadDTO,
    MetadataHookResultDTO,
    StepMetadataDTO,
)
from backend_v2.models.domain.metrics import ProfilerMetricsDTO
from backend_v2.models.domain.references import BibliographyResultDTO
from backend_v2.models.domain.validation import ValidationResultDTO
from backend_v2.models.dtos.global_context import GlobalContextVarsDTO
from backend_v2.models.dtos.hook_delta import (
    AnomalyRetryResultDTO,
    ArchivistPrecedentsResultDTO,
    ExternalEvidenceResultDTO,
    FlatteningHookOutput,
    HookDeltaDTO,
    InputControlRatioResultDTO,
    MatrixHookResultDTO,
    PassivityDetectionResultDTO,
)
from backend_v2.models.dtos.hook_state import ExecutionInputsDTO
from backend_v2.models.dtos.lightweight_matrix import ScoringResultDTO
from backend_v2.models.dtos.synthesis import SynthesisDistillationDTO
from backend_v2.models.dtos.trace import TraceEventMetadataDTO, TraceScoringPayloadDTO
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.llm import LLMProviderConfig
from backend_v2.models.state import StepOutputDTO, TraceEvent

if TYPE_CHECKING:
    from backend_v2.core.hook_registry import HookState

__all__ = [
    "merge_execution_inputs",
    "reduce_hook_delta",
]

logger = logging.getLogger(__name__)


def merge_execution_inputs(
    base: ExecutionInputsDTO | None,
    delta: ExecutionInputsDTO | None,
) -> ExecutionInputsDTO:
    """Pure immutable merging of ExecutionInputsDTO instances via pure constructor.

    Guarantees:
    1. Base and delta are never mutated in-place (pure function).
    2. raw_inputs and dynamic_inputs dictionaries are non-destructively merged.
    3. delta fields take precedence over base fields.
    4. Returns a newly instantiated, immutable ExecutionInputsDTO.

    Args:
        base: The original base inputs container, or None.
        delta: The inputs container containing updates, or None.

    Returns:
        A new ExecutionInputsDTO representing the merged state.
    """
    if base is None and delta is None:
        return ExecutionInputsDTO()
    if base is None:
        assert delta is not None
        return delta
    if delta is None:
        return base

    merged_raw = {**base.raw_inputs, **delta.raw_inputs}
    merged_dynamic = {**base.dynamic_inputs, **delta.dynamic_inputs}

    target_locale = base.target_locale
    if delta.target_locale is not None:
        target_locale = delta.target_locale

    user_role = base.user_role
    if delta.user_role is not None:
        user_role = delta.user_role

    return ExecutionInputsDTO(
        raw_inputs=merged_raw,
        dynamic_inputs=merged_dynamic,
        target_locale=target_locale,
        user_role=user_role,
    )


def reduce_hook_delta(
    current_state: HookState,
    delta_dto: HookDeltaDTO,
    step_id: str | None = None,
) -> tuple[HookState, list[TraceEvent]]:
    """Pure state reduction function integrating HookDeltaDTO into HookState.

    Guarantees:
    1. Zero in-place mutations — instantiates new HookState and ExecutionMetadata via pure constructors.
    2. Exhaustive DTO matching on delta payload without dict-parsing or duck-typing.
    3. Emits decision TraceEvents for context updates or external evidence audit traces.

    Args:
        current_state: Current immutable HookState.
        delta_dto: Strongly typed HookDeltaDTO returned by a hook.
        step_id: Current executing DAG step ID for trace anchoring.

    Returns:
        Tuple of (updated HookState, list of emitted TraceEvents).
    """
    from backend_v2.core.hook_registry import HookState

    emitted_events: list[TraceEvent] = []
    if step_id is not None:
        effective_step = step_id
    elif current_state.step_id is not None:
        effective_step = current_state.step_id
    else:
        effective_step = "unknown"

    # 1. Reduce Metadata Updates
    new_metadata = current_state.metadata
    if delta_dto.metadata_updates is not None:
        meta_delta = delta_dto.metadata_updates
        new_matrix_sampling = (
            meta_delta.matrix_sampling_strategy
            if meta_delta.matrix_sampling_strategy is not None
            else current_state.metadata.matrix_sampling_strategy
        )
        new_provider = (
            meta_delta.provider_override
            if meta_delta.provider_override is not None
            else current_state.metadata.provider_override
        )
        new_registry_id = (
            meta_delta.model_registry_id
            if meta_delta.model_registry_id is not None
            else current_state.metadata.model_registry_id
        )

        new_metadata = ExecutionMetadata(
            matrix_sampling_strategy=new_matrix_sampling,
            workflow_version=current_state.metadata.workflow_version,
            global_context_vars=current_state.metadata.global_context_vars,
            provider_override=new_provider,
            model_registry_id=new_registry_id,
        )

        if meta_delta.mcp_audit_traces:
            raw_traces = [t.model_dump(mode="json") for t in meta_delta.mcp_audit_traces]
            emitted_events.append(
                TraceEvent(
                    step_name=effective_step,
                    event_type="decision",
                    content={"mcp_audit_traces": cast(JsonValue, raw_traces)},
                    metadata=TraceEventMetadataDTO(mcp_audit_traces=meta_delta.mcp_audit_traces),
                    mcp_audit_traces=meta_delta.mcp_audit_traces,
                )
            )

        if meta_delta.estimated_token_count is not None:
            emitted_events.append(
                TraceEvent(
                    step_name=effective_step,
                    event_type="decision",
                    content={"estimated_token_count": meta_delta.estimated_token_count},
                    metadata=TraceEventMetadataDTO(estimated_token_count=meta_delta.estimated_token_count),
                )
            )

    # 2. Reduce Delta Payload into Inputs or Global Context Vars
    new_inputs = current_state.inputs
    new_global_vars = current_state.global_context_vars
    delta = delta_dto.delta

    if delta is not None:
        if isinstance(delta, ArchivistPrecedentsResultDTO):
            base_vars = new_global_vars or GlobalContextVarsDTO()
            new_global_vars = base_vars.model_copy(update={"archivist_precedents": delta.archivist_precedents})
        elif isinstance(delta, PassivityDetectionResultDTO):
            base_vars = new_global_vars or GlobalContextVarsDTO()
            new_global_vars = base_vars.model_copy(update={"passivity_detected": delta.passivity_detected})
            emitted_events.append(
                TraceEvent(
                    step_name=effective_step,
                    event_type="decision",
                    content={"passivity_detected": delta.passivity_detected},
                    metadata=TraceEventMetadataDTO(is_context_update=True),
                )
            )
        elif isinstance(delta, AnomalyRetryResultDTO):
            base_vars = new_global_vars or GlobalContextVarsDTO()
            new_global_vars = base_vars.model_copy(
                update={"llm_anomaly_retry_requested": delta.llm_anomaly_retry_requested}
            )
        elif isinstance(delta, InputControlRatioResultDTO):
            base_vars = new_global_vars or GlobalContextVarsDTO()
            new_global_vars = base_vars.model_copy(update={"input_control_ratio": delta.input_control_ratio})
        elif isinstance(delta, ProfilerMetricsDTO):
            base_vars = new_global_vars or GlobalContextVarsDTO()
            new_global_vars = base_vars.model_copy(update={"profiler_metrics": delta})
        elif isinstance(delta, ExternalEvidenceResultDTO):
            base_vars = new_global_vars or GlobalContextVarsDTO()
            new_global_vars = base_vars.model_copy(update={"external_evidence": delta.external_evidence})
        elif isinstance(delta, FlatteningHookOutput):
            base_vars = new_global_vars or GlobalContextVarsDTO()
            new_global_vars = base_vars.model_copy(update={"shuffled_atoms": delta.shuffled_atoms})
        elif isinstance(delta, MatrixHookResultDTO):
            base_vars = new_global_vars if new_global_vars is not None else GlobalContextVarsDTO()
            new_scores = {
                pb_id: float(out.normalized_score)
                for pb_id, out in delta.matrix_outputs.items()
                if out.normalized_score is not None
            }
            if base_vars.evaluative_matrices is not None:
                merged_eval = {**base_vars.evaluative_matrices, **new_scores}
            else:
                merged_eval = new_scores
            new_global_vars = base_vars.model_copy(update={"evaluative_matrices": merged_eval})
            matrix_inputs = ExecutionInputsDTO(
                dynamic_inputs={
                    **{pb_id: out for pb_id, out in delta.matrix_outputs.items()},
                    "_evaluative_matrices": merged_eval,
                    "evaluative_matrices": merged_eval,
                }
            )
            new_inputs = merge_execution_inputs(new_inputs, matrix_inputs)
            emitted_events.append(
                TraceEvent(
                    step_name=effective_step,
                    event_type="decision",
                    content={"evaluative_matrices": cast(JsonValue, merged_eval)},
                    metadata=TraceEventMetadataDTO(is_context_update=True),
                )
            )
        elif isinstance(delta, (AnalystOutput, EvaluationResult)):
            base_vars = new_global_vars or GlobalContextVarsDTO()
            new_global_vars = base_vars.model_copy(update={"integrity_verified_output": delta})
        elif isinstance(delta, SynthesisDistillationDTO):
            base_vars = new_global_vars or GlobalContextVarsDTO()
            new_global_vars = base_vars.model_copy(update={"distillation": delta})
        elif isinstance(delta, BibliographyResultDTO):
            base_vars = new_global_vars or GlobalContextVarsDTO()
            new_global_vars = base_vars.model_copy(update={"bibliography": delta})
        elif isinstance(delta, StepMetadataDTO):
            base_vars = new_global_vars or GlobalContextVarsDTO()
            new_global_vars = base_vars.model_copy(update={"step_metadata": delta})
        elif isinstance(delta, MetadataHookResultDTO):
            base_vars = new_global_vars or GlobalContextVarsDTO()
            new_global_vars = base_vars.model_copy(update={"step_metadata": delta.step_metadata})
        elif isinstance(delta, MetadataHookPayloadDTO):
            base_vars = new_global_vars or GlobalContextVarsDTO()
            new_global_vars = base_vars.model_copy(
                update={
                    "initiator_id": delta.sys_initiator_id,
                    "organization_id": delta.organization_id,
                    "language": delta.language,
                }
            )
        elif isinstance(delta, (ScoringResultDTO, TraceScoringPayloadDTO)):
            base_vars = new_global_vars or GlobalContextVarsDTO()
            new_global_vars = base_vars.model_copy(update={"scoring": delta})
        elif isinstance(delta, InteractionAnalysisDTO):
            base_vars = new_global_vars or GlobalContextVarsDTO()
            new_global_vars = base_vars.model_copy(update={"interaction_analysis": delta})
        elif isinstance(delta, LinguisticsResultDTO):
            base_vars = new_global_vars or GlobalContextVarsDTO()
            new_global_vars = base_vars.model_copy(update={"step_linguistics": delta})
            emitted_events.append(
                TraceEvent(
                    step_name=effective_step,
                    event_type="decision",
                    content={"step_linguistics": delta.model_dump(mode="json")},
                    metadata=TraceEventMetadataDTO(is_context_update=True),
                )
            )
        elif isinstance(delta, LLMProviderConfig):
            new_metadata = current_state.metadata.model_copy(update={"provider_override": delta.provider})
        elif isinstance(delta, ValidationResultDTO):
            pass
        elif isinstance(delta, StepOutputDTO):
            pass
        elif isinstance(delta, ExecutionInputsDTO):
            new_inputs = merge_execution_inputs(current_state.inputs, delta)
        elif isinstance(delta, GlobalContextVarsDTO):
            new_global_vars = delta
            emitted_events.append(
                TraceEvent(
                    step_name=effective_step,
                    event_type="decision",
                    content=delta.model_dump(mode="json"),
                    metadata=TraceEventMetadataDTO(is_context_update=True),
                )
            )

    new_hook_state = HookState(
        execution_id=current_state.execution_id,
        workflow_id=current_state.workflow_id,
        step_id=current_state.step_id,
        task_blueprint=current_state.task_blueprint,
        metadata=new_metadata,
        global_context_vars=new_global_vars,
        inputs=new_inputs,
    )
    return new_hook_state, emitted_events
