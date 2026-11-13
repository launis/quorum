"""Unit tests for synthesis_reducers.py covering user role extraction, starvation handling, result processing, and telemetry recovery."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import backend_v2.workers.synthesis_reducers as synthesis_reducers_mod
from backend_v2.exceptions import AppException
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.execution import ExecutionRecord, ExecutionStep, FrozenContext
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.synthesis import RenderedSynthesisCache
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput
from backend_v2.models.dtos.schema_manifest import JsonSchemaNode
from backend_v2.models.dtos.synthesis import (
    ExecutiveSummarySectionResult,
    MatrixExplanationContextDTO,
    MatrixExplanationsResult,
    MatrixSectionSynthesesResult,
    SynthesisRowExplanationDTO,
    SynthesisSectionDTO,
    XaiHighlightItem,
    XaiHighlightsResult,
)
from backend_v2.models.dtos.trace import StepTraceMetadataDTO, TraceEventMetadataEnvelope
from backend_v2.models.enums import (
    ExecutionStatus,
    RoleClassification,
    TargetBlockType,
    XaiExtensionType,
)
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import TraceEvent
from backend_v2.models.view.sdui import ParagraphBlock
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository
from backend_v2.workers.synthesis_reducers import (
    extract_user_role_from_trace,
    handle_starvation_if_detected,
    handle_synthesis_failure_state,
    process_executive_summary_result,
    process_matrix_sections_result,
    process_row_explanations_result,
    process_xai_highlights_result,
    recover_trace_telemetry,
)


def _make_execution(trace_events: list[TraceEvent] | None = None) -> ExecutionRecord:
    """Create a validated ExecutionRecord fixture with optional trace events."""
    return ExecutionRecord(
        id="exe_0195f3a00000700283456789abcdef01",
        workflow_id="wor_0195f3a00000700283456789abcdef01",
        output_profile_id="pro_0195f3a00000700283456789abcdef01",
        status=ExecutionStatus.PASSED,
        target_locale="en",
        raw_inputs=WorkflowInputs(),
        frozen_context=FrozenContext(),
        metadata=ExecutionMetadata(),
        execution_trace=trace_events if trace_events is not None else [],
    )


def test_extract_user_role_from_trace_lightweight_output() -> None:
    """Test extract_user_role_from_trace with LightweightMatrixOutput content."""
    matrix_out = LightweightMatrixOutput(raw_score=4.2, evaluated_atoms={}, extensions={})
    evt = TraceEvent(
        v=1,
        step_name="step_test",
        timestamp=datetime.now(UTC),
        event_type="output",
        content={"blk_role": matrix_out.model_dump(mode="json", exclude_none=True)},
    )
    exec_rec = _make_execution([evt])
    role, just = extract_user_role_from_trace(exec_rec, "blk_role")
    assert role == RoleClassification.DRIVER.value
    assert "4.2" in (just if just is not None else "")


def test_extract_user_role_from_trace_dict_with_matrix_output() -> None:
    """Test extract_user_role_from_trace with dict containing role_target_block_id."""
    matrix_out = LightweightMatrixOutput(raw_score=5.0, evaluated_atoms={}, extensions={})
    evt = TraceEvent(
        v=1,
        step_name="step_test",
        timestamp=datetime.now(UTC),
        event_type="output",
        content={"blk_role": matrix_out.model_dump(mode="json", exclude_none=True)},
    )
    exec_rec = _make_execution([evt])
    role, _ = extract_user_role_from_trace(exec_rec, "blk_role")
    assert role == RoleClassification.ARCHITECT.value


def test_extract_user_role_from_trace_raw_dict_hydration() -> None:
    """Test extract_user_role_from_trace hydrating raw dict into LightweightMatrixOutput."""
    raw_payload: dict[str, JsonSchemaNode] = {"raw_score": 1.0, "evaluated_atoms": {}}
    evt = TraceEvent(
        v=1,
        step_name="step_test",
        timestamp=datetime.now(UTC),
        event_type="output",
        content={"blk_role": raw_payload},
    )
    exec_rec = _make_execution([evt])
    role, _ = extract_user_role_from_trace(exec_rec, "blk_role")
    assert role == RoleClassification.PASSENGER.value


def test_extract_user_role_from_trace_corrupted_dict_raises() -> None:
    """Test extract_user_role_from_trace fails fast on malformed dictionary."""
    corrupted_payload: dict[str, JsonSchemaNode] = {"raw_score": "not-a-number", "evaluated_atoms": 123}
    evt = TraceEvent(
        v=1,
        step_name="step_test",
        timestamp=datetime.now(UTC),
        event_type="output",
        content={"blk_role": corrupted_payload},
    )
    exec_rec = _make_execution([evt])
    with pytest.raises(AppException) as exc_info:
        extract_user_role_from_trace(exec_rec, "blk_role")
    assert exc_info.value.status_code == 500


def test_extract_user_role_from_trace_missing_returns_none() -> None:
    """Test extract_user_role_from_trace returns (None, None) when block is missing."""
    exec_rec = _make_execution([])
    role, just = extract_user_role_from_trace(exec_rec, "blk_role")
    assert role is None
    assert just is None


def test_process_executive_summary_result_empty() -> None:
    """Test process_executive_summary_result returns empty when input is None."""
    res = process_executive_summary_result(None, None)
    assert res.exec_dto is None
    assert res.blocks == []
    assert res.cost_usd == 0.0
    assert res.total_tokens == 0


def test_process_executive_summary_result_with_budget() -> None:
    """Test process_executive_summary_result applies synthesis_length_constraint."""
    long_text = "This is a long synthesized sentence designed to test truncation budget behavior. " * 3
    p_block = ParagraphBlock(text=long_text, exact_quotes=[], citations=[])
    exec_res = ExecutiveSummarySectionResult(
        executive_summary=[p_block],
        user_role=None,
        user_role_justification=None,
        cited_sources=[],
    )
    usage = TokenUsage(total_tokens=30, prompt_tokens=10, completion_tokens=20, cost_usd=0.005)
    prof = OutputProfile(
        organization_id="org_0195f3a0000070008000000000000001",
        id="pro_0195f3a00000700283456789abcdef01",
        slug="prof_test",
        workflow_id="wor_0195f3a00000700283456789abcdef01",
        name=I18nText(translations={"en": "Test Profile"}),
        synthesis_length_constraint=100,
        target_block_order=[TargetBlockType.EXECUTIVE_SUMMARY_BLOCK],
    )
    res = process_executive_summary_result((exec_res, usage), prof)
    assert res.exec_dto is not None
    assert len(res.blocks) == 1
    assert isinstance(res.blocks[0], ParagraphBlock)
    assert len(res.blocks[0].text) <= 100 or "..." in res.blocks[0].text
    assert res.cost_usd == 0.005
    assert res.total_tokens == 30


def test_process_matrix_sections_result() -> None:
    """Test process_matrix_sections_result aggregates blocks and tokens."""
    sec = SynthesisSectionDTO(
        layout_id="sec_1",
        content_blocks=[ParagraphBlock(text="Block 1", exact_quotes=[], citations=[])],
    )
    mat_res = MatrixSectionSynthesesResult(sections=[sec])
    usage = TokenUsage(total_tokens=20, prompt_tokens=5, completion_tokens=15, cost_usd=0.002)

    res = process_matrix_sections_result([("layer_1", (mat_res, usage)), ("layer_empty", None)])
    assert "layer_1" in res.sec_dict
    assert len(res.sec_dict["layer_1"]) == 1
    assert res.cost_usd == 0.002
    assert res.total_tokens == 20


def test_process_xai_highlights_result() -> None:
    """Test process_xai_highlights_result enforces xai_length_constraint."""
    long_content = "Highlight explanation describing performance and metrics across systems in detail."
    highlight = XaiHighlightItem(
        extension_type=XaiExtensionType.VARIANCE_VALIDATION,
        content=long_content,
    )
    xai_res = XaiHighlightsResult(xai_highlights=[highlight])
    usage = TokenUsage(total_tokens=20, prompt_tokens=10, completion_tokens=10, cost_usd=0.001)
    prof = OutputProfile(
        organization_id="org_0195f3a0000070008000000000000001",
        id="pro_0195f3a00000700283456789abcdef01",
        slug="prof_test",
        workflow_id="wor_0195f3a00000700283456789abcdef01",
        name=I18nText(translations={"en": "Test Profile"}),
        xai_length_constraint=50,
        target_block_order=[TargetBlockType.GROUPED_EXTENSIONS_BLOCK],
    )
    res = process_xai_highlights_result((xai_res, usage), prof)
    assert len(res.highlights) == 1
    assert res.cost_usd == 0.001
    assert res.total_tokens == 20

    # None branch
    h_none = process_xai_highlights_result(None, None)
    assert h_none.highlights == []


def test_process_row_explanations_result() -> None:
    """Test process_row_explanations_result maps real and alias IDs with length constraint."""
    item = SynthesisRowExplanationDTO(
        matrix_id="alias_mat",
        row_explanation="Detailed causal explanation for why this row was scored this way in the workflow.",
        curated_quotes=[],
    )
    mat_res = MatrixExplanationsResult(explanations=[item])
    usage = TokenUsage(total_tokens=20, prompt_tokens=8, completion_tokens=12, cost_usd=0.003)
    ctx_dto = MatrixExplanationContextDTO(
        matrix_id="alias_mat",
        real_matrix_id="real_mat_123",
        matrix_label="Matrix Label",
        score=0.8,
        justification="Justification",
    )
    prof = OutputProfile(
        organization_id="org_0195f3a0000070008000000000000001",
        id="pro_0195f3a00000700283456789abcdef01",
        slug="prof_test",
        workflow_id="wor_0195f3a00000700283456789abcdef01",
        name=I18nText(translations={"en": "Test Profile"}),
        row_explanation_length_constraint=50,
        target_block_order=[TargetBlockType.MATRIX_SUMMARY_TABLE_BLOCK],
    )
    res = process_row_explanations_result((mat_res, usage), [ctx_dto], prof)
    assert "real_mat_123" in res.cache_explanations
    assert res.cost_usd == 0.003
    assert res.total_tokens == 20

    # None branch
    empty_res = process_row_explanations_result(None, [], None)
    assert empty_res.cache_explanations == {}


@pytest.mark.asyncio
async def test_handle_starvation_if_detected_true() -> None:
    """Test handle_starvation_if_detected detects DataStarvationEvent and short-circuits."""
    evt = TraceEvent(
        v=1,
        step_name="step_test",
        timestamp=datetime.now(UTC),
        event_type="output",
        content={"event_type": "starvation", "total_atoms": 0, "reason": "insufficient"},
    )
    exec_rec = _make_execution([evt])
    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_execution(exec_rec)
    mock_redis = AsyncMock()
    mock_render_fn = AsyncMock()
    mock_artifact = MagicMock()
    mock_artifact.id = "rep_0195f3a00000700283456789abcdef01"

    with patch("backend_v2.workers.synthesis_reducers.ReportService") as mock_report_service_cls:
        mock_svc = mock_report_service_cls.return_value
        mock_svc.get_or_create_default_artifact = AsyncMock(return_value=mock_artifact)
        mock_svc.compile_and_persist_artifact = AsyncMock()
        detected = await handle_starvation_if_detected(
            exec_rec,
            "pro_0195f3a00000700283456789abcdef01",
            "en",
            mock_repo,
            mock_redis,
            mock_render_fn,
        )
        assert detected is True
        saved_rec = await mock_repo.get_execution(exec_rec.id)
        assert saved_rec is not None
        assert saved_rec.profile_syntheses is not None
        assert "pro_0195f3a00000700283456789abcdef01" in saved_rec.profile_syntheses
        mock_render_fn.assert_called_once()
        mock_svc.get_or_create_default_artifact.assert_awaited_once_with(
            execution_id=exec_rec.id,
            profile_id="pro_0195f3a00000700283456789abcdef01",
            locale="en",
        )
        mock_svc.compile_and_persist_artifact.assert_awaited_once_with(
            "rep_0195f3a00000700283456789abcdef01",
            mock_redis,
        )


@pytest.mark.asyncio
async def test_handle_starvation_if_detected_dict_event() -> None:
    """Test handle_starvation_if_detected validates dict starvation payload."""
    evt = TraceEvent(
        v=1,
        step_name="step_test",
        timestamp=datetime.now(UTC),
        event_type="output",
        content={"event_type": "starvation", "total_atoms": 0, "reason": "none"},
    )
    exec_rec = _make_execution([evt])
    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_execution(exec_rec)
    mock_redis = AsyncMock()
    mock_render_fn = AsyncMock()
    mock_artifact = MagicMock()
    mock_artifact.id = "rep_0195f3a00000700283456789abcdef01"

    with patch("backend_v2.workers.synthesis_reducers.ReportService") as mock_report_service_cls:
        mock_svc = mock_report_service_cls.return_value
        mock_svc.get_or_create_default_artifact = AsyncMock(return_value=mock_artifact)
        mock_svc.compile_and_persist_artifact = AsyncMock()
        detected = await handle_starvation_if_detected(
            exec_rec,
            "pro_0195f3a00000700283456789abcdef01",
            "en",
            mock_repo,
            mock_redis,
            mock_render_fn,
        )
        assert detected is True
        saved_rec = await mock_repo.get_execution(exec_rec.id)
        assert saved_rec is not None
        assert saved_rec.profile_syntheses is not None
        assert "pro_0195f3a00000700283456789abcdef01" in saved_rec.profile_syntheses
        mock_svc.get_or_create_default_artifact.assert_awaited_once_with(
            execution_id=exec_rec.id,
            profile_id="pro_0195f3a00000700283456789abcdef01",
            locale="en",
        )
        mock_svc.compile_and_persist_artifact.assert_awaited_once_with(
            "rep_0195f3a00000700283456789abcdef01",
            mock_redis,
        )


@pytest.mark.asyncio
async def test_handle_starvation_if_detected_corrupted_dict_raises() -> None:
    """Test handle_starvation_if_detected fails fast on corrupted starvation event."""
    evt = TraceEvent(
        v=1,
        step_name="step_test",
        timestamp=datetime.now(UTC),
        event_type="output",
        content={"event_type": "starvation", "total_atoms": "invalid-int"},
    )
    exec_rec = _make_execution([evt])
    with pytest.raises(AppException) as exc_info:
        await handle_starvation_if_detected(
            exec_rec,
            "pro_0195f3a00000700283456789abcdef01",
            "en",
            AsyncMock(),
            None,
            AsyncMock(),
        )
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_handle_starvation_if_detected_false() -> None:
    """Test handle_starvation_if_detected returns False when no starvation event exists."""
    exec_rec = _make_execution([])
    detected = await handle_starvation_if_detected(
        exec_rec,
        "pro_0195f3a00000700283456789abcdef01",
        "en",
        AsyncMock(),
        None,
        AsyncMock(),
    )
    assert detected is False


@pytest.mark.asyncio
async def test_recover_trace_telemetry_from_blob() -> None:
    """Test recover_trace_telemetry parses stored trace blob when final_cost is 0.0."""
    env = TraceEventMetadataEnvelope(
        step_metadata=StepTraceMetadataDTO(
            token_usage=TokenUsage(
                total_tokens=90,
                prompt_tokens=50,
                completion_tokens=25,
                cached_tokens=10,
                reasoning_tokens=5,
                cost_usd=0.015,
            )
        )
    )
    trace_item = TraceEvent(
        v=1,
        step_name="step_test",
        timestamp=datetime.now(UTC),
        event_type="output",
        content=env.model_dump(mode="json", exclude_none=True),
    )

    exec_rec = _make_execution([trace_item])

    telemetry = await recover_trace_telemetry(exec_rec, 0.0)
    assert telemetry.final_cost == 0.015
    assert telemetry.prompt_tokens == 50
    assert telemetry.completion_tokens == 25
    assert telemetry.cached_tokens == 10
    assert telemetry.reasoning_tokens == 5


@pytest.mark.asyncio
async def test_recover_trace_telemetry_typed_envelope_recovers_usage() -> None:
    """Test recover_trace_telemetry recovers usage from typed TraceEventMetadataEnvelope instance."""
    env = TraceEventMetadataEnvelope(
        step_metadata=StepTraceMetadataDTO(
            token_usage=TokenUsage(
                prompt_tokens=30,
                completion_tokens=15,
                total_tokens=45,
                cached_tokens=5,
                reasoning_tokens=2,
                cost_usd=0.01,
            )
        )
    )
    trace_item = TraceEvent(
        v=1,
        step_name="step_typed",
        timestamp=datetime.now(UTC),
        event_type="output",
        content=env,
    )
    exec_rec = _make_execution([trace_item])
    telemetry = await recover_trace_telemetry(exec_rec, 0.0)
    assert telemetry.final_cost == 0.01
    assert telemetry.prompt_tokens == 30
    assert telemetry.completion_tokens == 15
    assert telemetry.cached_tokens == 5
    assert telemetry.reasoning_tokens == 2


@pytest.mark.asyncio
async def test_handle_synthesis_failure_state() -> None:
    """Test handle_synthesis_failure_state updates virtual step state."""
    mock_repo = InMemoryUnifiedWorkflowRepository()
    mock_record = _make_execution()
    await mock_repo.save_execution(mock_record)
    with patch.object(synthesis_reducers_mod, "UnifiedWorkflowRepository", return_value=mock_repo):
        await handle_synthesis_failure_state(
            "exe_0195f3a00000700283456789abcdef01",
            "pro_0195f3a00000700283456789abcdef01",
            ValueError("Synthesis error"),
        )
        saved_rec = await mock_repo.get_execution("exe_0195f3a00000700283456789abcdef01")
        assert saved_rec is not None


def test_extract_user_role_from_trace_invalid_entry_continues() -> None:
    """Test extract_user_role_from_trace skips invalid non-dict non-LightweightMatrixOutput entries."""
    evt = TraceEvent(
        v=1,
        timestamp=datetime.now(UTC),
        event_type="output",
        step_name="st",
        content={"blk_role": 123},
    )
    rec = _make_execution([evt])
    role, just = extract_user_role_from_trace(rec, "blk_role")
    assert role is None
    assert just is None


def test_process_row_explanations_result_real_id_fallback() -> None:
    """Test process_row_explanations_result falls back to real_matrix_id lookup."""
    item = SynthesisRowExplanationDTO(
        matrix_id="real_mat_123",
        row_explanation="Explanation for real matrix.",
        curated_quotes=[],
    )
    mat_res = MatrixExplanationsResult(explanations=[item])
    ctx_dto = MatrixExplanationContextDTO(
        matrix_id="alias_mat",
        real_matrix_id="real_mat_123",
        matrix_label="Matrix Label",
        score=0.8,
        justification="Justification",
    )
    res = process_row_explanations_result((mat_res, None), [ctx_dto], None)
    assert res.cache_explanations["real_mat_123"] == "Explanation for real matrix."


def test_process_row_explanations_result_empty_real_id_continues() -> None:
    """Test process_row_explanations_result skips items with empty real_matrix_id."""
    item = SynthesisRowExplanationDTO(
        matrix_id="alias_mat",
        row_explanation="Explanation for real matrix.",
        curated_quotes=[],
    )
    mat_res = MatrixExplanationsResult(explanations=[item])
    ctx_dto = MatrixExplanationContextDTO(
        matrix_id="alias_mat",
        real_matrix_id="",
        matrix_label="Matrix Label",
        score=0.8,
        justification="Justification",
    )
    res = process_row_explanations_result((mat_res, None), [ctx_dto], None)
    assert res.cache_explanations == {}


@pytest.mark.asyncio
async def test_recover_trace_telemetry_corrupted_envelope_raises() -> None:
    """Test recover_trace_telemetry raises AppException on corrupted envelope dict."""
    trace_item = TraceEvent(
        v=1,
        step_name="step_test",
        timestamp=datetime.now(UTC),
        event_type="output",
        content={"step_metadata": "corrupted_non_dict"},
    )
    exec_rec = _make_execution([trace_item])
    with pytest.raises(AppException) as exc_info:
        await recover_trace_telemetry(exec_rec, 0.0)
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_handle_synthesis_failure_state_none_profile() -> None:
    """Test handle_synthesis_failure_state returns immediately when profile_id is None."""
    await handle_synthesis_failure_state("exe_0195f3a00000700283456789abcdef01", None, ValueError("error"))


@pytest.mark.asyncio
async def test_handle_synthesis_failure_state_quarantines_on_current_step_without_mutating_steps() -> None:
    """Test handle_synthesis_failure_state records failure message in current_step without mutating canonical steps."""
    prof_id = "pro_0195f3a00000700283456789abcdef01"
    dag_step = ExecutionStep(id="stp_0195f3a00000700283456789abcdef01", label="DAG Step", status=ExecutionStatus.PASSED)
    mock_repo = InMemoryUnifiedWorkflowRepository()
    mock_record = _make_execution().model_copy(
        update={
            "steps": [dag_step],
        }
    )
    await mock_repo.save_execution(mock_record)
    with patch.object(synthesis_reducers_mod, "UnifiedWorkflowRepository", return_value=mock_repo):
        await handle_synthesis_failure_state(
            "exe_0195f3a00000700283456789abcdef01",
            prof_id,
            ValueError("Synthesis error"),
        )
        saved_rec = await mock_repo.get_execution("exe_0195f3a00000700283456789abcdef01")
        assert saved_rec is not None
        assert saved_rec.status_message == f"Synthesis failed for profile {prof_id}: Synthesis error"
        assert saved_rec.steps == [dag_step]


@pytest.mark.asyncio
async def test_handle_synthesis_failure_state_db_error_raises() -> None:
    """Test handle_synthesis_failure_state raises AppException on repository exception."""
    mock_repo = InMemoryUnifiedWorkflowRepository()
    mock_repo.inject_fault("get_execution", OSError("DB unavailable"), trigger_count=1)
    try:
        with patch.object(synthesis_reducers_mod, "UnifiedWorkflowRepository", return_value=mock_repo):
            with pytest.raises(AppException) as exc_info:
                await handle_synthesis_failure_state(
                    "exe_0195f3a00000700283456789abcdef01",
                    "pro_0195f3a00000700283456789abcdef01",
                    ValueError("Synthesis error"),
                )
            assert exc_info.value.status_code == 500
    finally:
        mock_repo.clear_faults()


def test_execution_record_with_updated_step_state_returns_new_frozen_instance() -> None:
    """Verify with_updated_step_state returns a new ExecutionRecord with updated canonical steps."""
    step_id = "stp_0195f3a00000700283456789abcdef01"
    initial_step = ExecutionStep(id=step_id, label="Initial Step", status=ExecutionStatus.PENDING, progress=0)
    record = _make_execution().model_copy(
        update={
            "steps": [initial_step],
        }
    )

    updated_step = initial_step.model_copy(update={"status": ExecutionStatus.PASSED, "progress": 100})
    new_record = record.with_updated_step_state(step_id, updated_step)

    assert new_record is not record
    assert new_record.steps == [updated_step]
    assert record.steps == [initial_step]

    # Also verify appending a step not yet present in steps list
    second_step_id = "stp_0195f3a00000700283456789abcdef02"
    second_step = ExecutionStep(id=second_step_id, label="Second Step", status=ExecutionStatus.RUNNING, progress=50)
    new_record_with_append = new_record.with_updated_step_state(second_step_id, second_step)
    assert len(new_record_with_append.steps) == 2
    assert new_record_with_append.steps[1] == second_step


def test_execution_record_with_updated_profile_synthesis_preserves_existing_profiles() -> None:
    """Verify with_updated_profile_synthesis preserves existing profile caches and adds the new profile cache."""
    existing_pid = "pro_0195f3a00000700283456789abcdef01"
    new_pid = "pro_0195f3a00000700283456789abcdef02"
    existing_cache = RenderedSynthesisCache(cited_sources=["doc_existing"])
    new_cache = RenderedSynthesisCache(cited_sources=["doc_new"])

    record = _make_execution().model_copy(update={"profile_syntheses": {existing_pid: existing_cache}})
    updated_record = record.with_updated_profile_synthesis(new_pid, new_cache)

    assert updated_record is not record
    assert updated_record.profile_syntheses[existing_pid] == existing_cache
    assert updated_record.profile_syntheses[new_pid] == new_cache
    assert new_pid not in record.profile_syntheses


def test_execution_record_with_cleared_profile_syntheses_empties_cache() -> None:
    """Verify with_cleared_profile_syntheses returns a new ExecutionRecord with empty profile_syntheses."""
    existing_pid = "pro_0195f3a00000700283456789abcdef01"
    existing_cache = RenderedSynthesisCache(cited_sources=["doc_existing"])
    record = _make_execution().model_copy(update={"profile_syntheses": {existing_pid: existing_cache}})

    cleared_record = record.with_cleared_profile_syntheses()

    assert cleared_record is not record
    assert cleared_record.profile_syntheses == {}
    assert record.profile_syntheses == {existing_pid: existing_cache}


@pytest.mark.asyncio
async def test_synthesis_reducers_atomic_persistence_roundtrip() -> None:
    """Verify profile synthesis updates persist roundtrip in InMemoryUnifiedWorkflowRepository."""
    repo = InMemoryUnifiedWorkflowRepository()
    exec_id = "exe_0195f3a00000700283456789abcdef01"
    prof_1 = "pro_0195f3a00000700283456789abcdef01"
    prof_2 = "pro_0195f3a00000700283456789abcdef02"

    dag_step = ExecutionStep(
        id="stp_0195f3a00000700283456789abcdef01",
        label="DAG Step",
        status=ExecutionStatus.PASSED,
        progress=100,
    )
    starvation_evt = TraceEvent(
        v=1,
        step_name="step_test",
        timestamp=datetime.now(UTC),
        event_type="output",
        content={"event_type": "starvation", "total_atoms": 0, "reason": "insufficient"},
    )
    initial_rec = _make_execution([starvation_evt]).model_copy(
        update={
            "steps": [dag_step],
        }
    )
    await repo.save_execution(initial_rec)

    mock_artifact = MagicMock()
    mock_artifact.id = "rep_0195f3a00000700283456789abcdef01"
    with patch("backend_v2.workers.synthesis_reducers.ReportService") as mock_report_service_cls:
        mock_svc = mock_report_service_cls.return_value
        mock_svc.get_or_create_default_artifact = AsyncMock(return_value=mock_artifact)
        mock_svc.compile_and_persist_artifact = AsyncMock()

        # Persist profile 1 synthesis
        current_1 = await repo.get_execution(exec_id)
        assert current_1 is not None
        await handle_starvation_if_detected(
            current_1,
            prof_1,
            "en",
            repo,
            None,
            AsyncMock(),
        )
        # Persist profile 2 synthesis on refreshed record
        current_2 = await repo.get_execution(exec_id)
        assert current_2 is not None
        await handle_starvation_if_detected(
            current_2,
            prof_2,
            "en",
            repo,
            None,
            AsyncMock(),
        )

    with patch.object(synthesis_reducers_mod, "UnifiedWorkflowRepository", return_value=repo):
        await handle_synthesis_failure_state(exec_id, prof_2, ValueError("Render warning"))

    reconstituted = await repo.get_execution(exec_id)
    assert reconstituted is not None
    validated = ExecutionRecord.model_validate_json(reconstituted.model_dump_json())
    assert prof_1 in validated.profile_syntheses
    assert prof_2 in validated.profile_syntheses
    assert validated.status_message == f"Synthesis failed for profile {prof_2}: Render warning"
    assert validated.steps == [dag_step]
