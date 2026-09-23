"""Unit tests for state_reducer.py following ISTQB Equivalence Partitions."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from backend_v2.core.hook_registry import HookState
from backend_v2.models.domain.analyst import AnalystOutput, Hypothesis
from backend_v2.models.domain.archival import ArchivalPrecedentDTO
from backend_v2.models.domain.evaluation import EvaluationResult
from backend_v2.models.domain.interaction import InteractionAnalysisDTO
from backend_v2.models.domain.judge import DimensionResultItem
from backend_v2.models.domain.linguistics import LinguisticsResultDTO
from backend_v2.models.domain.matrix import FlattenedAtom
from backend_v2.models.domain.metadata import (
    MetadataHookPayloadDTO,
    MetadataHookResultDTO,
    StepMetadataDTO,
)
from backend_v2.models.domain.metrics import ProfilerMetricsDTO
from backend_v2.models.domain.references import BibliographyResultDTO, ReferenceDTO
from backend_v2.models.domain.security import SanitizationResultDTO
from backend_v2.models.domain.system_config import MCPAuditTrace
from backend_v2.models.domain.validation import ValidationResultDTO
from backend_v2.models.dtos.global_context import GlobalContextVarsDTO
from backend_v2.models.dtos.hook_delta import (
    AnomalyRetryResultDTO,
    ArchivistPrecedentsResultDTO,
    ExecutionMetadataDeltaDTO,
    ExternalEvidenceResultDTO,
    FlatteningHookOutput,
    HookDeltaDTO,
    InputControlRatioResultDTO,
    MatrixHookResultDTO,
    PassivityDetectionResultDTO,
)
from backend_v2.models.dtos.hook_state import ExecutionInputsDTO
from backend_v2.models.dtos.lightweight_matrix import (
    LightweightMatrixOutput,
    ScoringResultDTO,
)
from backend_v2.models.dtos.step_output import StepOutputDTO
from backend_v2.models.dtos.synthesis import SynthesisDistillationDTO
from backend_v2.models.dtos.trace import TraceScoringPayloadDTO
from backend_v2.models.enums import InteractionStrategy, RoleClassification
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.llm import LLMProviderConfig
from backend_v2.services.orchestrator.state_reducer import merge_execution_inputs, reduce_hook_delta


def _build_test_hook_state() -> HookState:
    """Helper to build an initial HookState."""
    return HookState(
        execution_id="exe_test_001",
        workflow_id="wor_test_001",
        step_id="stp_step_1",
        metadata=ExecutionMetadata(matrix_sampling_strategy=10, workflow_version=1),
        global_context_vars=GlobalContextVarsDTO(language="en"),
        inputs=ExecutionInputsDTO(raw_inputs={"doc": "content"}),
    )


def test_merge_execution_inputs_with_none_inputs() -> None:
    """ISTQB Partition 1: None inputs handling."""
    assert merge_execution_inputs(None, None) == ExecutionInputsDTO()

    base = ExecutionInputsDTO(raw_inputs={"a": "1"})
    assert merge_execution_inputs(base, None) == base

    delta = ExecutionInputsDTO(raw_inputs={"b": "2"})
    assert merge_execution_inputs(None, delta) == delta


def test_merge_execution_inputs_pure_immutability() -> None:
    """ISTQB Partition 2: Verifies base and delta are never mutated in-place."""
    base = ExecutionInputsDTO(
        raw_inputs={"text": "orig", "count": 1},
        dynamic_inputs={"score": 10.0},
        target_locale="en",
    )
    delta = ExecutionInputsDTO(
        raw_inputs={"extra": "new"},
        dynamic_inputs={"score": 20.0, "step1": "done"},
        target_locale="fi",
    )

    merged = merge_execution_inputs(base, delta)

    # Merged has combined state
    assert merged.raw_inputs == {"text": "orig", "count": 1, "extra": "new"}
    assert merged.dynamic_inputs == {"score": 20.0, "step1": "done"}
    assert merged.target_locale == "fi"

    # Base is unchanged
    assert base.raw_inputs == {"text": "orig", "count": 1}
    assert base.dynamic_inputs == {"score": 10.0}
    assert base.target_locale == "en"

    # Delta is unchanged
    assert delta.raw_inputs == {"extra": "new"}
    assert delta.dynamic_inputs == {"score": 20.0, "step1": "done"}
    assert delta.target_locale == "fi"


def test_merge_execution_inputs_overwrites_and_locale() -> None:
    """ISTQB Partition 3: Delta takes precedence over base fields."""
    base = ExecutionInputsDTO(
        raw_inputs={"doc": "base_doc"},
        dynamic_inputs={"val": "base_val"},
        user_role="analyst",
        target_locale="en",
    )
    delta = ExecutionInputsDTO(
        raw_inputs={"doc": "delta_doc"},
        dynamic_inputs={"val": "delta_val"},
        user_role="admin",
        target_locale=None,
    )

    merged = merge_execution_inputs(base, delta)

    assert merged.raw_inputs["doc"] == "delta_doc"
    assert merged.dynamic_inputs["val"] == "delta_val"
    assert merged.user_role == "admin"
    assert merged.target_locale == "en"


def test_merge_execution_inputs_negative_and_boundary_cases() -> None:
    """ISTQB Partition 4 & 5: Negative schema rejection and boundary None handling."""
    with pytest.raises(ValidationError):
        ExecutionInputsDTO.model_validate({"raw_inputs": {}, "unexpected_extra": "fail"})

    with pytest.raises(ValidationError):
        ExecutionInputsDTO.model_validate({"target_locale": 12345})

    base = ExecutionInputsDTO(raw_inputs={"a": "1"}, user_role=None, target_locale=None)
    delta = ExecutionInputsDTO(raw_inputs={"b": "2"}, user_role=None, target_locale=None)
    merged = merge_execution_inputs(base, delta)
    assert merged.user_role is None
    assert merged.target_locale is None
    assert merged.raw_inputs == {"a": "1", "b": "2"}


def test_reduce_hook_delta_passivity_and_anomaly() -> None:
    """Verify reduction of PassivityDetectionResultDTO and AnomalyRetryResultDTO."""
    state = _build_test_hook_state()

    passivity_delta = HookDeltaDTO(delta=PassivityDetectionResultDTO(passivity_detected=True))
    new_state, events = reduce_hook_delta(state, passivity_delta, "stp_step_1")
    assert new_state.inputs.dynamic_inputs["passivity_detected"] is True
    assert len(events) == 0

    anomaly_delta = HookDeltaDTO(delta=AnomalyRetryResultDTO(llm_anomaly_retry_requested=True))
    new_state2, events2 = reduce_hook_delta(state, anomaly_delta, "stp_step_1")
    assert new_state2.inputs.dynamic_inputs["llm_anomaly_retry_requested"] is True
    assert len(events2) == 0


def test_reduce_hook_delta_metadata_updates_and_traces() -> None:
    """Verify reduction of ExecutionMetadataDeltaDTO with MCP audit traces."""
    state = _build_test_hook_state()

    trace = MCPAuditTrace(
        tool_id="mcp_search",
        step_name="stp_step_1",
        query="claim check",
        source_urls=["https://verified.org"],
    )
    meta_delta = HookDeltaDTO(
        metadata_updates=ExecutionMetadataDeltaDTO(
            matrix_sampling_strategy=5,
            estimated_token_count=500,
            mcp_audit_traces=[trace],
        )
    )

    new_state, events = reduce_hook_delta(state, meta_delta, "stp_step_1")
    assert new_state.metadata.matrix_sampling_strategy == 5
    assert len(events) == 2
    assert events[0].event_type == "decision"
    assert "mcp_audit_traces" in events[0].content
    assert events[0].mcp_audit_traces == [trace]
    assert events[1].event_type == "decision"
    assert "estimated_token_count" in events[1].content


def test_reduce_hook_delta_archivist_and_flattening() -> None:
    """Verify reduction of ArchivistPrecedentsResultDTO and FlatteningHookOutput."""
    state = _build_test_hook_state()

    precedent = ArchivalPrecedentDTO(id="exe_old", date="2026-09-20", scores="5.0", verdict="Approved")
    arch_delta = HookDeltaDTO(delta=ArchivistPrecedentsResultDTO(archivist_precedents=[precedent]))
    new_state, _ = reduce_hook_delta(state, arch_delta)
    assert len(new_state.inputs.dynamic_inputs["archivist_precedents"]) == 1

    atom = FlattenedAtom(atom_id="atm_01", question="Criteria A?")
    flat_delta = HookDeltaDTO(delta=FlatteningHookOutput(shuffled_atoms=[atom]))
    new_state2, _ = reduce_hook_delta(state, flat_delta)
    assert len(new_state2.inputs.dynamic_inputs["shuffled_atoms"]) == 1


def test_reduce_hook_delta_matrix_hook_result() -> None:
    """Verify reduction of MatrixHookResultDTO."""
    state = _build_test_hook_state()

    matrix_out = LightweightMatrixOutput(raw_score=4.0, normalized_score=80.0)
    matrix_delta = HookDeltaDTO(
        delta=MatrixHookResultDTO(
            matrix_outputs={"blk_test": matrix_out},
            missing_contexts={"blk_test": "Missing summary"},
            atom_quotes={"blk_test": []},
        )
    )

    new_state, _ = reduce_hook_delta(state, matrix_delta)
    assert "blk_test" in new_state.inputs.dynamic_inputs
    assert new_state.inputs.dynamic_inputs["blk_test"] == matrix_out
    assert new_state.inputs.dynamic_inputs["blk_test_missing_context"] == "Missing summary"


def test_reduce_hook_delta_input_control_and_profiler_and_evidence() -> None:
    """Verify reduction of InputControlRatioResultDTO, ProfilerMetricsDTO, and ExternalEvidenceResultDTO."""
    state = _build_test_hook_state()

    ctrl_delta = HookDeltaDTO(delta=InputControlRatioResultDTO(input_control_ratio=0.75))
    s1, _ = reduce_hook_delta(state, ctrl_delta)
    assert s1.inputs.dynamic_inputs["input_control_ratio"] == 0.75

    prof_delta = HookDeltaDTO(delta=ProfilerMetricsDTO(word_count=120))
    s2, _ = reduce_hook_delta(state, prof_delta)
    assert s2.inputs.dynamic_inputs["profiler_metrics"].word_count == 120

    ev_delta = HookDeltaDTO(delta=ExternalEvidenceResultDTO(external_evidence="rag data"))
    s3, _ = reduce_hook_delta(state, ev_delta)
    assert s3.inputs.dynamic_inputs["external_evidence"] == "rag data"


def test_reduce_hook_delta_analyst_and_evaluation_and_distillation() -> None:
    """Verify reduction of AnalystOutput, EvaluationResult, and SynthesisDistillationDTO."""
    state = _build_test_hook_state()

    analyst_delta = HookDeltaDTO(
        delta=AnalystOutput(
            hypotheses=[Hypothesis(id="hyp_01", claim_text="Claim", evidence_found=False, search_query="search")],
            thought_process="Thinking step",
            conclusion="Hypothesis confirmed",
            confidence_score=0.95,
        )
    )
    s1, _ = reduce_hook_delta(state, analyst_delta)
    assert "integrity_verified_output" in s1.inputs.dynamic_inputs

    eval_delta = HookDeltaDTO(
        delta=EvaluationResult(
            matrix_id="mat_test",
            timestamp=datetime.now(timezone.utc),
            total_score=4.5,
            final_verdict="PASSED",
            thought_process="Reasoning",
            conclusion="Verdict",
            confidence_score=0.9,
            dimensions=[DimensionResultItem(dimension_id="dim_01", score=4.5, reasoning="Detailed reasoning")],
            scale_min=1.0,
            scale_max=5.0,
        )
    )
    s2, _ = reduce_hook_delta(state, eval_delta)
    assert "integrity_verified_output" in s2.inputs.dynamic_inputs

    dist_delta = HookDeltaDTO(delta=SynthesisDistillationDTO(distilled_inputs="compressed inputs"))
    s3, _ = reduce_hook_delta(state, dist_delta)
    assert s3.inputs.dynamic_inputs["distillation"].distilled_inputs == "compressed inputs"


def test_reduce_hook_delta_security_and_references() -> None:
    """Verify reduction of SanitizationResultDTO and BibliographyResultDTO."""
    state = _build_test_hook_state()

    san_delta = HookDeltaDTO(
        delta=SanitizationResultDTO(
            sanitized_inputs={"user_text": "clean"}, security_status="CLEAN", threat_detected=False
        )
    )
    s1, _ = reduce_hook_delta(state, san_delta)
    assert s1.inputs.dynamic_inputs["sanitization"].security_status == "CLEAN"

    ref = ReferenceDTO(source_id="src_42", title="Architecture Spec", snippet="Section 3")
    bib_delta = HookDeltaDTO(delta=BibliographyResultDTO(references=[ref]))
    s2, _ = reduce_hook_delta(state, bib_delta)
    assert len(s2.inputs.dynamic_inputs["bibliography"].references) == 1


def test_reduce_hook_delta_metadata_variants() -> None:
    """Verify reduction of MetadataHookPayloadDTO, MetadataHookResultDTO, and StepMetadataDTO."""
    state = _build_test_hook_state()

    payload_delta = HookDeltaDTO(delta=MetadataHookPayloadDTO(_sys_initiator_id="usr_admin"))
    s1, _ = reduce_hook_delta(state, payload_delta)
    assert "metadata" in s1.inputs.dynamic_inputs

    step_meta = StepMetadataDTO(
        execution_id="exe_01",
        workflow_id="wor_01",
        step_id="stp_01",
        initiator_id="usr_01",
        timestamp_isot="2026-09-22T00:00:00Z",
        unix_time=1700000000,
    )
    meta_result_delta = HookDeltaDTO(delta=MetadataHookResultDTO(step_metadata=step_meta))
    s2, _ = reduce_hook_delta(state, meta_result_delta)
    assert s2.inputs.dynamic_inputs["_step_metadata"] == step_meta

    direct_step_meta_delta = HookDeltaDTO(delta=step_meta)
    s3, _ = reduce_hook_delta(state, direct_step_meta_delta)
    assert s3.inputs.dynamic_inputs["_step_metadata"] == step_meta


def test_reduce_hook_delta_scoring_interaction_linguistics_provider() -> None:
    """Verify reduction of hook deltas including LinguisticsResultDTO and scoring payloads."""
    from backend_v2.models.dtos.lightweight_matrix import XAILogDto

    state = _build_test_hook_state()

    score_delta = HookDeltaDTO(
        delta=ScoringResultDTO(score=88.5, xai_log=XAILogDto(pedagogical_key="PED_KEY"), breakdown={})
    )
    s1, _ = reduce_hook_delta(state, score_delta)
    assert s1.inputs.dynamic_inputs["scoring"].score == 88.5

    trace_score_delta = HookDeltaDTO(delta=TraceScoringPayloadDTO(total_score=75.0))
    s2, _ = reduce_hook_delta(state, trace_score_delta)
    assert s2.inputs.dynamic_inputs["scoring"].total_score == 75.0

    inter_delta = HookDeltaDTO(
        delta=InteractionAnalysisDTO(
            thought_process="Reasoning",
            conclusion="Verdict",
            confidence_score=0.9,
            role_classification=RoleClassification.PASSENGER,
            high_dependency=False,
            imperative_command_count=3,
            strategy=InteractionStrategy.ZERO_SHOT,
        )
    )
    s3, _ = reduce_hook_delta(state, inter_delta)
    assert s3.inputs.dynamic_inputs["interaction_analysis"].imperative_command_count == 3

    ling_delta = HookDeltaDTO(delta=LinguisticsResultDTO(total_word_count=45))
    s4, events_4 = reduce_hook_delta(state, ling_delta)
    assert s4.inputs.dynamic_inputs["linguistics"].total_word_count == 45
    assert s4.global_context_vars is not None
    assert s4.global_context_vars.step_linguistics is not None
    assert s4.global_context_vars.step_linguistics.total_word_count == 45
    assert len(events_4) == 1
    assert events_4[0].event_type == "decision"
    assert events_4[0].metadata == {"is_context_update": True}
    assert "step_linguistics" in events_4[0].content

    state_no_gvars = HookState(
        execution_id="exe_2",
        workflow_id="wor_2",
        step_id="stp_2",
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(),
    )
    s4_no_gvars, events_no_gvars = reduce_hook_delta(state_no_gvars, ling_delta)
    assert s4_no_gvars.global_context_vars.step_linguistics is not None
    assert s4_no_gvars.global_context_vars.step_linguistics.total_word_count == 45
    assert len(events_no_gvars) == 1
    assert events_no_gvars[0].event_type == "decision"
    assert events_no_gvars[0].metadata == {"is_context_update": True}
    assert "step_linguistics" in events_no_gvars[0].content

    llm_delta = HookDeltaDTO(
        delta=LLMProviderConfig(
            id="cfg_12345678",
            provider="openai",
            model_name="gpt-4",
            tpm_limit=1000,
            rpm_limit=100,
            temperature=0.7,
        )
    )
    s5, _ = reduce_hook_delta(state, llm_delta)
    assert s5.inputs.dynamic_inputs["llm_config"].temperature == 0.7


def test_reduce_hook_delta_validation_step_output_inputs_global_vars() -> None:
    """Verify reduction of ValidationResultDTO, StepOutputDTO, ExecutionInputsDTO, and GlobalContextVarsDTO."""
    state = _build_test_hook_state()

    val_delta = HookDeltaDTO(delta=ValidationResultDTO(is_valid=True, errors=[]))
    s1, _ = reduce_hook_delta(state, val_delta)
    assert s1.inputs.dynamic_inputs["validation"].is_valid is True

    step_out = StepOutputDTO(step_id="stp_prior", block_id="blk_prior", data_type="text", payload="Done text")
    s2, _ = reduce_hook_delta(state, HookDeltaDTO(delta=step_out))
    assert s2.inputs.dynamic_inputs["stp_prior"] == step_out

    inputs_delta = HookDeltaDTO(delta=ExecutionInputsDTO(dynamic_inputs={"merged_key": "merged_val"}))
    s3, _ = reduce_hook_delta(state, inputs_delta)
    assert s3.inputs.dynamic_inputs["merged_key"] == "merged_val"

    gvars_delta = HookDeltaDTO(delta=GlobalContextVarsDTO(language="fi"))
    s4, events = reduce_hook_delta(state, gvars_delta)
    assert s4.global_context_vars is not None
    assert s4.global_context_vars.language == "fi"
    assert len(events) == 1
    assert events[0].event_type == "decision"


def test_reduce_hook_delta_matrix_with_existing_evaluative_matrices() -> None:
    """Verify matrix hook evaluation map handles pre-existing and numeric matrix scores."""
    base_state = _build_test_hook_state()
    state = base_state.model_copy(
        update={"inputs": ExecutionInputsDTO(dynamic_inputs={"_evaluative_matrices": {"old_pb": 70.0, "int_pb": 60.0}})}
    )

    matrix_out = LightweightMatrixOutput(raw_score=4.0, normalized_score=85.0)
    matrix_delta = HookDeltaDTO(
        delta=MatrixHookResultDTO(
            matrix_outputs={"new_pb": matrix_out},
            missing_contexts={},
            atom_quotes={},
        )
    )

    new_state, _ = reduce_hook_delta(state, matrix_delta)
    eval_map = new_state.inputs.dynamic_inputs["_evaluative_matrices"]
    assert eval_map["old_pb"] == 70.0
    assert eval_map["int_pb"] == 60.0
    assert eval_map["new_pb"] == 85.0
