"""Unit tests for the Event Sourcing State components and StepOutputDTO."""

from datetime import datetime, timezone

import pytest
from pydantic import BaseModel, ValidationError

import backend_v2.models.state as state_module
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.coach import BibliographyItem, CoachingPlan
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.domain.judge import DimensionResultItem, JudgeOutput, JudgeScoreCard
from backend_v2.models.domain.security import InputProcessingOutputDTO
from backend_v2.models.dtos.atom_evaluation import LightweightMatrixDTO
from backend_v2.models.dtos.atom_result import AtomResultDTO
from backend_v2.models.dtos.causal_discovery import (
    AntiFluffAuditDTO,
    CausalGraphPayloadDTO,
    CausalNodeDTO,
    CausalTdaFusionResultDTO,
    FairScoringBreakdownDTO,
)
from backend_v2.models.dtos.hook_state import ExecutionInputsDTO
from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput
from backend_v2.models.dtos.node_execution import StepOutputContentDTO
from backend_v2.models.dtos.trace import TraceScoringPayloadDTO
from backend_v2.models.enums import ExecutionStatus, VirtualSystemStepID
from backend_v2.models.execution_core import ExecutionCoreFields
from backend_v2.models.state import (
    ErrorTraceEvent,
    EvidenceOverrideDTO,
    ExecutionState,
    ReasoningTrace,
    StateProjector,
    StepExecutionEnvelope,
    TombstoneEvent,
    TraceEvent,
    WorkflowState,
)


def test_state_module_exports() -> None:
    """Verify that state.py exports all expected public symbols via __all__."""
    expected = {
        "ErrorTraceEvent",
        "EvidenceOverrideDTO",
        "ExecutionState",
        "ReasoningTrace",
        "StateProjector",
        "StepExecutionEnvelope",
        "StepOutputDTO",
        "TombstoneEvent",
        "TraceEvent",
        "WorkflowState",
    }
    assert set(state_module.__all__) == expected
    state_module_members = dir(state_module)
    for name in state_module.__all__:
        assert name in state_module_members


def test_reasoning_trace_validation_success() -> None:
    """Test valid ReasoningTrace construction with default token usage."""
    rt = ReasoningTrace(
        thought_process="Detailed reasoning in English",
        conclusion="Sound conclusion in English",
        confidence_score=0.95,
        model_name="gemini-2.5-pro",
    )
    assert rt.thought_process == "Detailed reasoning in English"
    assert rt.conclusion == "Sound conclusion in English"
    assert rt.confidence_score == 0.95
    assert rt.model_name == "gemini-2.5-pro"
    assert rt.token_usage.total_tokens == 0


def test_reasoning_trace_confidence_score_out_of_bounds_high() -> None:
    """Negative Test: Confidence score > 1.0 must raise AppException(VALIDATION_FAILED)."""
    with pytest.raises(AppException) as exc_info:
        ReasoningTrace(
            thought_process="Reasoning",
            conclusion="Conclusion",
            confidence_score=1.5,
        )
    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


def test_reasoning_trace_confidence_score_out_of_bounds_low() -> None:
    """Negative Test: Confidence score < 0.0 must raise AppException(VALIDATION_FAILED)."""
    with pytest.raises(AppException) as exc_info:
        ReasoningTrace(
            thought_process="Reasoning",
            conclusion="Conclusion",
            confidence_score=-0.1,
        )
    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


def test_evidence_override_dto_success_and_strictness() -> None:
    """Test EvidenceOverrideDTO construction and extra='forbid' constraint."""
    now = datetime.now(timezone.utc)
    dto = EvidenceOverrideDTO(
        evq_id="evq_12345",
        user_rejected=True,
        rejection_reason="Invalid claim citation",
        rejected_by="usr_tester",
        rejected_at=now,
    )
    assert dto.evq_id == "evq_12345"
    assert dto.user_rejected is True
    assert dto.rejected_at == now

    with pytest.raises(ValidationError):
        EvidenceOverrideDTO.model_validate(
            {
                "evq_id": "evq_12345",
                "user_rejected": True,
                "rejection_reason": "Reason",
                "rejected_by": "usr_tester",
                "rejected_at": now.isoformat(),
                "extra_forbidden": True,
            }
        )


def test_execution_state_success_and_strictness() -> None:
    """Test ExecutionState construction and extra='forbid' constraint."""
    es = ExecutionState(
        executive_summary="Summary of execution",
        evidence_quotes=[],
        urgency_level=2,
    )
    assert es.executive_summary == "Summary of execution"
    assert es.urgency_level == 2

    with pytest.raises(ValidationError):
        ExecutionState.model_validate(
            {
                "executive_summary": "Summary",
                "evidence_quotes": [],
                "urgency_level": 1,
                "unexpected": "error",
            }
        )


def test_state_projector_fold_trace_happy_path() -> None:
    """Test that valid trace events are folded correctly into StepOutputDTOs."""
    event1 = TraceEvent(
        step_name="stp_123",
        event_type="output",
        content={"blk_a": "Some text payload", "blk_b": {"nested": "matrix data"}},
    )

    projector = StateProjector()
    results = projector.fold_trace([event1])

    assert len(results) == 2
    dto_a = next(dto for dto in results if dto.block_id == "blk_a")
    assert dto_a.step_id == "stp_123"
    assert dto_a.data_type == "unknown"
    assert dto_a.payload == "Some text payload"

    dto_b = next(dto for dto in results if dto.block_id == "blk_b")
    assert dto_b.step_id == "stp_123"
    assert dto_b.data_type == "unknown"
    assert dto_b.payload == {"nested": "matrix data"}


def test_state_projector_snapshot_property() -> None:
    """Test that the snapshot property builds the strictly typed list."""
    event1 = TraceEvent(
        step_name="stp_999",
        event_type="output",
        content={"blk_x": 42},
    )

    projector = StateProjector([event1])
    results = projector.snapshot

    assert len(results) == 1
    assert results[0].step_id == "stp_999"
    assert results[0].block_id == "blk_x"
    assert results[0].data_type == "unknown"
    assert results[0].payload == 42


def test_state_projector_schema_version() -> None:
    """Test that schema_version reflects highest applied version."""
    projector = StateProjector()
    assert projector.schema_version == 0

    event1 = TraceEvent(step_name="stp_1", event_type="input", v=2, content={"k": "v"})
    projector.apply_delta(event1)
    assert projector.schema_version == 2


def test_state_projector_fold_trace_max_tokens() -> None:
    """Test that fold_trace respects max_tokens by dropping older events."""
    event_old = TraceEvent(
        step_name="stp_old",
        event_type="output",
        content={"blk_old": "very long text that consumes tokens " * 20},
        timestamp=datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
    )
    event_new = TraceEvent(
        step_name="stp_new",
        event_type="output",
        content={"blk_new": "short text"},
        timestamp=datetime(2026, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
    )

    projector = StateProjector()
    results = projector.fold_trace([event_old, event_new], max_tokens=10)
    assert len(results) == 1
    assert results[0].step_id == "stp_new"


def test_state_projector_tombstone_event() -> None:
    """Test that tombstone events replace content correctly."""
    event_output = TraceEvent(step_name="stp_del", event_type="output", content={"blk_1": "sensitive"})
    event_tombstone = TombstoneEvent(step_name="stp_del", redacted_hash="hash_123")

    projector = StateProjector()
    projector.apply_delta(event_output)
    projector.apply_delta(event_tombstone)

    results = projector.snapshot
    assert len(results) == 2

    redacted = next(dto for dto in results if dto.block_id == "_redacted")
    assert redacted.payload is True

    hash_dto = next(dto for dto in results if dto.block_id == "hash")
    assert hash_dto.payload == "hash_123"


def test_state_projector_fail_fast_on_legacy_data() -> None:
    """Test that the Zero-Compromise Pledge enforces strict dictionary structures."""
    projector = StateProjector()
    projector._snapshot["stp_legacy"] = "I am a raw string output from V1"

    with pytest.raises(AppException) as excinfo:
        _ = projector.snapshot

    assert excinfo.value.status_code == 500
    assert excinfo.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "Legacy flat trace detected" in excinfo.value.message


def test_step_execution_envelope_strictness() -> None:
    """Test that StepExecutionEnvelope enforces V2CoreBase strictness."""
    dto = StepExecutionEnvelope(execution_id="exec_123", v2_engine=True)
    assert dto.execution_id == "exec_123"
    assert dto.v2_engine is True

    with pytest.raises(ValidationError):
        StepExecutionEnvelope.model_validate({"execution_id": "exec_1", "extra_field": "fail"})


def test_workflow_state_inherits_execution_core_fields() -> None:
    """Phase 2: Verify WorkflowState correctly inherits ExecutionCoreFields SSOT."""
    assert issubclass(WorkflowState, ExecutionCoreFields), "WorkflowState must inherit from ExecutionCoreFields"

    core_field_names = {
        "status",
        "execution_trace",
        "execution_trace_storage_path",
        "context_variables",
        "context_variables_storage_path",
    }
    ws_fields = set(WorkflowState.model_fields.keys())
    missing = core_field_names - ws_fields
    assert not missing, f"WorkflowState missing inherited core fields: {missing}"

    error_event = ErrorTraceEvent(step_name="test_step", error_code="ERR_TEST", error_message="test error")
    ws = WorkflowState(workflow_id="wf_testtest1234", target_locale="fi")
    ws_with_error = ws.add_event(error_event)
    assert len(ws_with_error.execution_trace) == 1
    event = ws_with_error.execution_trace[0]
    assert isinstance(event, ErrorTraceEvent)
    assert event.error_code == "ERR_TEST"


class SampleDTO(BaseModel):
    name: str


def test_workflow_state_accessors_and_properties() -> None:
    """Test all typed context accessors and lazy properties in WorkflowState."""
    input_proc_dto = InputProcessingOutputDTO(
        thought_process="Valid thought",
        conclusion="Valid conclusion",
        confidence_score=0.95,
        is_safe=True,
    )
    judge_card = JudgeScoreCard(
        agent_name="Standard Judge",
        scale_min=1.0,
        scale_max=5.0,
        total_score=3.0,
        max_score=5,
        verdict="Pass",
        dimensions=[
            DimensionResultItem(
                dimension_id="dim_1",
                dimension_label="D1",
                score=3.0,
                reasoning="Good",
            )
        ],
    )
    judge_out = JudgeOutput(
        thought_process="Valid thought",
        conclusion="Valid conclusion",
        confidence_score=0.95,
        matrix_id="blk_matrix123",
        scale_min=1.0,
        scale_max=5.0,
        score_card=judge_card,
    )
    coach_out = CoachingPlan(
        thought_process="Valid thought",
        conclusion="Valid conclusion",
        confidence_score=0.95,
        actionable_steps=["Action step 1"],
        focus_areas=["Focus area 1"],
        bibliography=[
            BibliographyItem(
                source_id="src_123",
                title="Reference Book",
                url="https://example.com",
                snippet="Useful resource",
            )
        ],
    )

    ws = WorkflowState(
        workflow_id="wf_testtest1234",
        target_locale="fi",
        context_variables={
            "variables": {
                "organization_id": "org_12345",
                "user_id": "usr_67890",
                "audit_results": "passed",
                "raw_key": "raw_value",
                "count_key": 42,
                "step_input_processing": input_proc_dto.model_dump(),
                "step_judge": judge_out.model_dump(),
                "step_coach": coach_out.model_dump(),
            }
        },
    )

    assert ws.start_time == ws.created_at
    assert ws.organization_id == "org_12345"
    assert ws.user_id == "usr_67890"
    assert ws.audit_results == "passed"

    # Typed accessor tests
    assert ws.get_context("non_existent") is None
    assert ws.get_context("raw_key") == "raw_value"
    assert ws.get_context("count_key") == 42
    assert ws.step_input_processing is not None
    assert ws.step_judge is not None
    assert ws.step_coach is not None

    # Step properties without data (None branch)
    empty_ws = WorkflowState(workflow_id="wf_empty000000000", target_locale="fi")
    assert empty_ws.step_input_processing is None
    assert empty_ws.step_judge is None
    assert empty_ws.step_coach is None
    assert empty_ws.step_interaction is None
    assert empty_ws.step_analyst is None
    assert empty_ws.step_xai is None
    assert empty_ws.step_logician is None
    assert empty_ws.step_falsifier is None
    assert empty_ws.step_profiler is None
    assert empty_ws.step_archivist is None
    assert empty_ws.step_overseer is None
    assert empty_ws.step_causal is None
    assert empty_ws.step_detector is None
    assert empty_ws.step_judge_cognitive is None
    assert empty_ws.organization_id is None
    assert empty_ws.user_id is None
    assert empty_ws.audit_results is None


def test_workflow_state_none_branches() -> None:
    """Test organization_id and user_id when values in context_variables are None."""
    ws = WorkflowState(
        workflow_id="wf_none00000000",
        target_locale="fi",
        context_variables={"variables": {"organization_id": None, "user_id": None}},
    )
    assert ws.organization_id is None
    assert ws.user_id is None
    assert ws.audit_results is None


def test_state_projector_fold_trace_string_content() -> None:
    """Test fold_trace token calculation when event content is a string and fails fast."""
    event = TraceEvent.model_construct(
        step_name="stp_str",
        event_type="output",
        content="string payload",
    )
    projector = StateProjector()
    with pytest.raises(AppException, match="Legacy flat trace detected"):
        projector.fold_trace([event], max_tokens=100)


def test_state_projector_invalid_payload_raises_validation_failed() -> None:
    """ISTQB Negative Boundary Partition 1: Feeding malformed step output raises AppException(VALIDATION_FAILED)."""
    projector = StateProjector()
    invalid_content = StepOutputContentDTO.model_construct(data={"blk_invalid": object()})
    projector._snapshot["stp_broken"] = invalid_content

    with pytest.raises(AppException) as excinfo:
        _ = projector.snapshot

    assert excinfo.value.status_code == 500
    assert excinfo.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "Invalid step output payload" in excinfo.value.message


def test_trace_event_untyped_arbitrary_object_raises_validation_error() -> None:
    """ISTQB Negative Boundary Partition 2: Passing untyped arbitrary object to TraceEvent.content raises ValidationError."""

    class ArbitraryUnregisteredObject:
        pass

    with pytest.raises(ValidationError):
        TraceEvent.model_validate(
            {
                "step_name": "stp_invalid",
                "event_type": "output",
                "content": ArbitraryUnregisteredObject(),
            }
        )


def test_workflow_state_get_context_val_none() -> None:
    """Test get_context when key is present but value is None (line 371)."""
    ws = WorkflowState(
        workflow_id="wf_none00000000",
        target_locale="fi",
        context_variables={"variables": {"null_key": None}},
    )
    assert ws.get_context("null_key") is None


def test_state_projector_apply_delta_execution_inputs_dto() -> None:
    """Test apply_delta with ExecutionInputsDTO."""
    inputs = ExecutionInputsDTO(
        raw_inputs={"raw_text": "input document"},
        dynamic_inputs={"param_1": 42},
    )
    event = TraceEvent(step_name="inputs", event_type="input", content=inputs)
    projector = StateProjector()
    projector.apply_delta(event)

    results = projector.snapshot
    assert len(results) == 2
    by_block = {dto.block_id: dto.payload for dto in results}
    assert by_block["raw_text"] == "input document"
    assert by_block["param_1"] == 42


def test_state_projector_apply_delta_workflow_inputs() -> None:
    """Test apply_delta with WorkflowInputs."""
    inputs = WorkflowInputs(dynamic_inputs={"workflow_var": "val_1"})
    event = TraceEvent(step_name="inputs", event_type="input", content=inputs)
    projector = StateProjector()
    projector.apply_delta(event)

    results = projector.snapshot
    assert len(results) == 1
    assert results[0].block_id == "workflow_var"
    assert results[0].payload == "val_1"


def test_state_projector_apply_delta_lightweight_matrix_dto() -> None:
    """Test apply_delta with LightweightMatrixDTO."""
    dto = LightweightMatrixDTO(execution_id="exe_test", reduced_atoms=[], global_metrics={})
    event = TraceEvent(step_name="stp_matrix", event_type="output", content=dto)
    projector = StateProjector()
    projector.apply_delta(event)

    results = projector.snapshot
    assert len(results) == 1
    assert results[0].block_id == "reduced_atoms"
    assert results[0].payload == []


def test_state_projector_apply_delta_lightweight_matrix_output() -> None:
    """Test apply_delta with LightweightMatrixOutput."""
    dto = LightweightMatrixOutput(
        raw_score=4.0,
        normalized_score=80.0,
        evaluated_atoms={},
        extensions={},
    )
    event = TraceEvent(step_name="stp_output", event_type="output", content=dto)
    projector = StateProjector()
    projector.apply_delta(event)

    results = projector.snapshot
    assert len(results) == 1
    assert results[0].block_id == "stp_output"


def test_state_projector_apply_delta_causal_graph_and_fusion() -> None:
    """Test apply_delta with CausalGraphPayloadDTO and CausalTdaFusionResultDTO."""
    node = CausalNodeDTO(
        node_id="nod_1",
        claim="Claim 1",
        status=ExecutionStatus.PASSED,
        blame_parent_ids=[],
        dependent_child_ids=[],
    )
    graph = CausalGraphPayloadDTO(nodes=[node], edges=[])
    audit = AntiFluffAuditDTO(
        isolated_concept_count=0,
        cycle_detected=False,
        unsupported_claims_count=0,
        logical_cohesion_score=0.9,
        detected_hollow_terms=[],
    )
    fair = FairScoringBreakdownDTO(
        independent_error_count=0,
        cascading_fault_count=0,
        raw_penalty_points=0.0,
        deduplicated_penalty_points=0.0,
        dampened_savings_points=0.0,
    )
    fusion = CausalTdaFusionResultDTO(
        graph=graph,
        anti_fluff_audit=audit,
        fair_scoring=fair,
    )

    projector = StateProjector()
    # 1. Apply graph
    projector.apply_delta(TraceEvent(step_name="stp_causal", event_type="output", content=graph))
    # 2. Apply fusion on same step
    projector.apply_delta(TraceEvent(step_name="stp_causal", event_type="output", content=fusion))

    results = projector.snapshot
    assert len(results) == 2
    by_block = {dto.block_id for dto in results}
    assert "graph" in by_block
    assert "fusion" in by_block

    # 3. Apply fusion on fresh step
    projector.apply_delta(TraceEvent(step_name="stp_fresh", event_type="output", content=fusion))
    assert any(dto.step_id == "stp_fresh" for dto in projector.snapshot)


def test_state_projector_apply_delta_trace_scoring_payload_dto() -> None:
    """Test apply_delta with TraceScoringPayloadDTO."""
    dto = TraceScoringPayloadDTO(
        total_score=85.0,
        final_score=85.0,
        aggregation_status="passed",
    )
    event = TraceEvent(step_name="stp_score", event_type="output", content=dto)
    projector = StateProjector()
    projector.apply_delta(event)

    results = projector.snapshot
    assert len(results) == 1
    assert results[0].block_id == VirtualSystemStepID.SCORING_RESULT.value


def test_state_projector_apply_delta_atom_results() -> None:
    """Test apply_delta with AtomResultDTO and list of AtomResultDTO."""
    atom_1 = AtomResultDTO(
        tda_id="tda_1",
        matrix_id="blk_cohesion",
        status=ExecutionStatus.PASSED,
        contextual_override=True,
        is_inverse_evidence=False,
        evaluation_reasoning="Reasoning 1",
        extensions={},
        depends_on_tda_ids=[],
        short_circuit_reason_tda_ids=[],
    )
    atom_2 = AtomResultDTO(
        tda_id="tda_2",
        matrix_id="blk_cohesion",
        status=ExecutionStatus.PASSED,
        contextual_override=True,
        is_inverse_evidence=False,
        evaluation_reasoning="Reasoning 2",
        extensions={},
        depends_on_tda_ids=[],
        short_circuit_reason_tda_ids=[],
    )

    projector = StateProjector()
    projector.apply_delta(TraceEvent(step_name="stp_atoms", event_type="output", content=atom_1))
    projector.apply_delta(TraceEvent(step_name="stp_atoms", event_type="output", content=[atom_2]))

    results = projector.snapshot
    assert len(results) == 1
    assert results[0].block_id == "results"
    assert isinstance(results[0].payload, list)
    assert len(results[0].payload) == 2


def test_state_projector_apply_delta_base_model() -> None:
    """Test apply_delta with generic BaseModel."""
    sample = SampleDTO(name="generic_model")
    event = TraceEvent(step_name="stp_model", event_type="output", content=sample)
    projector = StateProjector()
    projector.apply_delta(event)

    results = projector.snapshot
    assert len(results) == 1
    assert results[0].block_id == "stp_model"
    assert results[0].payload == {"name": "generic_model"}


def test_state_projector_apply_delta_scoring_dict() -> None:
    """Test apply_delta with total_score dict."""
    payload = {
        "total_score": 90.0,
        "final_score": 88.0,
        "aggregation_status": "passed",
        "custom_meta": "extra",
    }
    event = TraceEvent(step_name="stp_dict_score", event_type="output", content=payload)
    projector = StateProjector()
    projector.apply_delta(event)

    results = projector.snapshot
    by_block = {dto.block_id for dto in results}
    assert VirtualSystemStepID.SCORING_RESULT.value in by_block
    assert "custom_meta" in by_block
