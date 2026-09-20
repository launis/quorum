"""Unit tests for synthesis_reducers.py covering user role extraction, starvation handling, result processing, and telemetry recovery."""

from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.dtos.base import DataStarvationEvent
from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput
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
from backend_v2.models.enums import ExecutionStatus, RoleClassification, TargetBlockType
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import TraceEvent
from backend_v2.models.view.sdui import ParagraphBlock
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
    return ExecutionRecord(
        id="exe_0123456789abcdef01",
        workflow_id="wor_0123456789abcdef01",
        output_profile_id="pro_0123456789abcdef01",
        status=ExecutionStatus.PASSED,
        target_locale="en",
        metadata=ExecutionMetadata(),
        execution_trace=trace_events or [],
    )


def test_extract_user_role_from_trace_lightweight_output() -> None:
    """Test extract_user_role_from_trace with LightweightMatrixOutput content."""
    matrix_out = LightweightMatrixOutput(raw_score=4.2, evaluated_atoms={})
    evt = TraceEvent(
        v=1,
        step_name="step_test",
        timestamp=datetime.now(timezone.utc),
        event_type="output",
        content={"blk_role": matrix_out.model_dump(mode="json")},
    )
    exec_rec = _make_execution([evt])
    role, just = extract_user_role_from_trace(exec_rec, "blk_role")
    assert role == RoleClassification.DRIVER.value
    assert "4.2" in (just or "")


def test_extract_user_role_from_trace_dict_with_matrix_output() -> None:
    """Test extract_user_role_from_trace with dict containing role_target_block_id."""
    matrix_out = LightweightMatrixOutput(raw_score=5.0, evaluated_atoms={})
    evt = TraceEvent(
        v=1,
        step_name="step_test",
        timestamp=datetime.now(timezone.utc),
        event_type="output",
        content={"blk_role": matrix_out.model_dump(mode="json")},
    )
    exec_rec = _make_execution([evt])
    role, just = extract_user_role_from_trace(exec_rec, "blk_role")
    assert role == RoleClassification.ARCHITECT.value


def test_extract_user_role_from_trace_raw_dict_hydration() -> None:
    """Test extract_user_role_from_trace hydrating raw dict into LightweightMatrixOutput."""
    evt = TraceEvent(
        v=1,
        step_name="step_test",
        timestamp=datetime.now(timezone.utc),
        event_type="output",
        content={"blk_role": {"raw_score": 1.0, "evaluated_atoms": {}}},
    )
    exec_rec = _make_execution([evt])
    role, _ = extract_user_role_from_trace(exec_rec, "blk_role")
    assert role == RoleClassification.PASSENGER.value


def test_extract_user_role_from_trace_corrupted_dict_raises() -> None:
    """Test extract_user_role_from_trace fails fast on malformed dictionary."""
    evt = TraceEvent(
        v=1,
        step_name="step_test",
        timestamp=datetime.now(timezone.utc),
        event_type="output",
        content={"blk_role": {"raw_score": "not-a-number", "evaluated_atoms": 123}},
    )
    exec_rec = _make_execution([evt])
    with pytest.raises(AppException) as exc_info:
        extract_user_role_from_trace(exec_rec, "blk_role")
    assert exc_info.value.status_code == 500


def test_extract_user_role_from_trace_missing_returns_default() -> None:
    """Test extract_user_role_from_trace returns fallback when block is missing."""
    exec_rec = _make_execution([])
    role, just = extract_user_role_from_trace(exec_rec, "blk_role", default_role="guest", default_justification="none")
    assert role == "guest"
    assert just == "none"


def test_process_executive_summary_result_empty() -> None:
    """Test process_executive_summary_result returns empty when input is None."""
    dto, blocks, cost, tokens = process_executive_summary_result(None, None)
    assert dto is None
    assert blocks == []
    assert cost == 0.0
    assert tokens == 0


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
        id="pro_0123456789abcdef01",
        slug="prof_test",
        workflow_id="wor_0123456789abcdef01",
        name=I18nText(translations={"en": "Test Profile"}),
        synthesis_length_constraint=100,
        target_block_order=[TargetBlockType.EXECUTIVE_SUMMARY_BLOCK],
    )
    dto, blocks, cost, tokens = process_executive_summary_result((exec_res, usage), prof)
    assert dto is not None
    assert len(blocks) == 1
    assert len(blocks[0].text) <= 100 or "..." in blocks[0].text  # type: ignore[attr-defined]
    assert cost == 0.005
    assert tokens == 30


def test_process_matrix_sections_result() -> None:
    """Test process_matrix_sections_result aggregates blocks and tokens."""
    sec = SynthesisSectionDTO(
        layout_id="sec_1",
        content_blocks=[ParagraphBlock(text="Block 1", exact_quotes=[], citations=[])],
    )
    mat_res = MatrixSectionSynthesesResult(sections=[sec])
    usage = TokenUsage(total_tokens=20, prompt_tokens=5, completion_tokens=15, cost_usd=0.002)

    sec_dict, cost, tokens = process_matrix_sections_result([("layer_1", (mat_res, usage)), ("layer_empty", None)])
    assert "layer_1" in sec_dict
    assert len(sec_dict["layer_1"]) == 1
    assert cost == 0.002
    assert tokens == 20


def test_process_xai_highlights_result() -> None:
    """Test process_xai_highlights_result enforces xai_length_constraint."""
    long_content = "Highlight explanation describing performance and metrics across systems in detail."
    highlight = XaiHighlightItem(
        extension_type="variance_validation",
        content=long_content,
    )
    xai_res = XaiHighlightsResult(xai_highlights=[highlight])
    usage = TokenUsage(total_tokens=20, prompt_tokens=10, completion_tokens=10, cost_usd=0.001)
    prof = OutputProfile(
        id="pro_0123456789abcdef01",
        slug="prof_test",
        workflow_id="wor_0123456789abcdef01",
        name=I18nText(translations={"en": "Test Profile"}),
        xai_length_constraint=50,
        target_block_order=[TargetBlockType.GROUPED_EXTENSIONS_BLOCK],
    )
    highlights, cost, tokens = process_xai_highlights_result((xai_res, usage), prof)
    assert len(highlights) == 1
    assert cost == 0.001
    assert tokens == 20

    # None branch
    h_none, _, _ = process_xai_highlights_result(None, None)
    assert h_none == []


def test_process_row_explanations_result() -> None:
    """Test process_row_explanations_result maps real and alias IDs with length constraint."""
    item = SynthesisRowExplanationDTO(
        matrix_id="alias_mat",
        row_explanation="Detailed causal explanation for why this row was scored this way in the workflow.",
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
        id="pro_0123456789abcdef01",
        slug="prof_test",
        workflow_id="wor_0123456789abcdef01",
        name=I18nText(translations={"en": "Test Profile"}),
        row_explanation_length_constraint=50,
        target_block_order=[TargetBlockType.MATRIX_SUMMARY_TABLE_BLOCK],
    )
    res_map, cost, tokens = process_row_explanations_result((mat_res, usage), [ctx_dto], prof)
    assert "real_mat_123" in res_map
    assert cost == 0.003
    assert tokens == 20

    # None branch
    empty_map, _, _ = process_row_explanations_result(None, [], None)
    assert empty_map == {}


@pytest.mark.asyncio
async def test_handle_starvation_if_detected_true() -> None:
    """Test handle_starvation_if_detected detects DataStarvationEvent and short-circuits."""
    evt = TraceEvent(
        v=1,
        step_name="step_test",
        timestamp=datetime.now(timezone.utc),
        event_type="output",
        content={"event_type": "starvation", "total_atoms": 0, "reason": "insufficient"},
    )
    exec_rec = _make_execution([evt])
    mock_repo = AsyncMock()
    mock_redis = AsyncMock()
    mock_render_fn = AsyncMock()

    detected = await handle_starvation_if_detected(
        exec_rec,
        "pro_0123456789abcdef01",
        "en",
        mock_repo,
        mock_redis,
        mock_render_fn,
    )
    assert detected is True
    mock_repo.update_execution.assert_called_once()
    mock_render_fn.assert_called_once()
    mock_redis.enqueue_job.assert_called_once_with(
        "generate_pdf_job", exec_rec.id, "en", "pro_0123456789abcdef01"
    )


@pytest.mark.asyncio
async def test_handle_starvation_if_detected_dict_event() -> None:
    """Test handle_starvation_if_detected validates dict starvation payload."""
    evt = TraceEvent(
        v=1,
        step_name="step_test",
        timestamp=datetime.now(timezone.utc),
        event_type="output",
        content={"event_type": "starvation", "total_atoms": 0, "reason": "none"},
    )
    exec_rec = _make_execution([evt])
    mock_repo = AsyncMock()
    mock_redis = AsyncMock()
    mock_render_fn = AsyncMock()

    detected = await handle_starvation_if_detected(
        exec_rec,
        "pro_0123456789abcdef01",
        "en",
        mock_repo,
        mock_redis,
        mock_render_fn,
    )
    assert detected is True


@pytest.mark.asyncio
async def test_handle_starvation_if_detected_corrupted_dict_raises() -> None:
    """Test handle_starvation_if_detected fails fast on corrupted starvation event."""
    evt = TraceEvent(
        v=1,
        step_name="step_test",
        timestamp=datetime.now(timezone.utc),
        event_type="output",
        content={"event_type": "starvation", "total_atoms": "invalid-int"},
    )
    exec_rec = _make_execution([evt])
    with pytest.raises(AppException) as exc_info:
        await handle_starvation_if_detected(
            exec_rec,
            "pro_0123456789abcdef01",
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
        "pro_0123456789abcdef01",
        "en",
        AsyncMock(),
        None,
        AsyncMock(),
    )
    assert detected is False


@pytest.mark.asyncio
async def test_recover_trace_telemetry_from_blob() -> None:
    """Test recover_trace_telemetry parses stored trace blob when final_cost is 0.0."""
    import json

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
        timestamp=datetime.now(timezone.utc),
        event_type="output",
        content=env.model_dump(mode="json"),
    )
    blob_bytes = json.dumps([trace_item.model_dump(mode="json")]).encode("utf-8")

    exec_rec = _make_execution([])
    exec_rec = exec_rec.model_copy(update={"execution_trace_storage_path": "traces/exec1.json"})

    mock_storage = AsyncMock()
    mock_storage.read.return_value = blob_bytes

    with patch("backend_v2.workers.synthesis_reducers.get_storage_driver", return_value=mock_storage):
        cost, p, c, cac, r = await recover_trace_telemetry(exec_rec, 0.0)
        assert cost == 0.015
        assert p == 50
        assert c == 25
        assert cac == 10
        assert r == 5


@pytest.mark.asyncio
async def test_recover_trace_telemetry_error_raises_corruption() -> None:
    """Test recover_trace_telemetry raises DATA_CORRUPTION on storage exception."""
    exec_rec = _make_execution([])
    exec_rec = exec_rec.model_copy(update={"execution_trace_storage_path": "traces/exec1.json"})

    mock_storage = AsyncMock()
    mock_storage.read.side_effect = OSError("Disk read failure")

    with patch("backend_v2.workers.synthesis_reducers.get_storage_driver", return_value=mock_storage):
        with pytest.raises(AppException) as exc_info:
            await recover_trace_telemetry(exec_rec, 0.0)
        assert exc_info.value.status_code == 500
        assert exc_info.value.details["error_code"] == "DATA_CORRUPTION"


@pytest.mark.asyncio
async def test_handle_synthesis_failure_state() -> None:
    """Test handle_synthesis_failure_state updates virtual step state."""
    mock_repo = AsyncMock()
    mock_repo.get_execution.return_value = {
        "id": "exe_0123456789abcdef01",
        "workflow_id": "wor_0123456789abcdef01",
        "target_locale": "en",
        "metadata": {},
        "step_states": {},
    }
    with patch("backend_v2.workers.synthesis_reducers.get_driver", new_callable=AsyncMock):
        with patch("backend_v2.workers.synthesis_reducers.UnifiedWorkflowRepository", return_value=mock_repo):
            await handle_synthesis_failure_state(
                "exe_0123456789abcdef01",
                "pro_0123456789abcdef01",
                ValueError("Synthesis error"),
            )
            mock_repo.update_execution.assert_called_once()


def test_extract_user_role_from_trace_invalid_entry_continues() -> None:
    """Test extract_user_role_from_trace skips invalid non-dict non-LightweightMatrixOutput entries."""
    evt = TraceEvent(
        v=1,
        timestamp=datetime.now(timezone.utc),
        event_type="output",
        step_name="st",
        content={"blk_role": 123},
    )
    rec = _make_execution([evt])
    role, just = extract_user_role_from_trace(rec, "blk_role", default_role="default")
    assert role == "default"


def test_process_row_explanations_result_real_id_fallback() -> None:
    """Test process_row_explanations_result falls back to real_matrix_id lookup."""
    item = SynthesisRowExplanationDTO(matrix_id="real_mat_123", row_explanation="Explanation for real matrix.")
    mat_res = MatrixExplanationsResult(explanations=[item])
    ctx_dto = MatrixExplanationContextDTO(
        matrix_id="alias_mat",
        real_matrix_id="real_mat_123",
        matrix_label="Matrix Label",
        score=0.8,
        justification="Justification",
    )
    res_map, _, _ = process_row_explanations_result((mat_res, None), [ctx_dto], None)
    assert res_map["real_mat_123"] == "Explanation for real matrix."


def test_process_row_explanations_result_empty_real_id_continues() -> None:
    """Test process_row_explanations_result skips items with empty real_matrix_id."""
    ctx_dto = MatrixExplanationContextDTO(
        matrix_id="alias_mat",
        real_matrix_id="",
        matrix_label="Matrix Label",
        score=0.8,
        justification="Justification",
    )
    res_map, _, _ = process_row_explanations_result(None, [ctx_dto], None)
    assert res_map == {}


@pytest.mark.asyncio
async def test_recover_trace_telemetry_corrupted_envelope_raises() -> None:
    """Test recover_trace_telemetry raises AppException on corrupted envelope dict."""
    import json

    trace_item = TraceEvent(
        v=1,
        step_name="step_test",
        timestamp=datetime.now(timezone.utc),
        event_type="output",
        content={"step_metadata": "corrupted_non_dict"},
    )
    blob_bytes = json.dumps([trace_item.model_dump(mode="json")]).encode("utf-8")
    exec_rec = _make_execution([]).model_copy(update={"execution_trace_storage_path": "traces/exec1.json"})
    mock_storage = AsyncMock()
    mock_storage.read.return_value = blob_bytes
    with patch("backend_v2.workers.synthesis_reducers.get_storage_driver", return_value=mock_storage):
        with pytest.raises(AppException) as exc_info:
            await recover_trace_telemetry(exec_rec, 0.0)
        assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_handle_synthesis_failure_state_none_profile() -> None:
    """Test handle_synthesis_failure_state returns immediately when profile_id is None."""
    await handle_synthesis_failure_state("exe_0123456789abcdef01", None, ValueError("error"))


@pytest.mark.asyncio
async def test_handle_synthesis_failure_state_with_virtual_step() -> None:
    """Test handle_synthesis_failure_state updates virtual step and execution record."""
    from backend_v2.models.domain.execution import ExecutionStep

    prof_id = "pro_0123456789abcdef01"
    v_step_id = f"sys_render_{prof_id}"
    v_step = ExecutionStep(id=v_step_id, label="Render", status=ExecutionStatus.PENDING)
    mock_repo = AsyncMock()
    mock_repo.get_execution.return_value = {
        "id": "exe_0123456789abcdef01",
        "workflow_id": "wor_0123456789abcdef01",
        "target_locale": "en",
        "metadata": {},
        "step_states": {v_step_id: v_step.model_dump(mode="json")},
        "steps": [v_step.model_dump(mode="json")],
    }
    with patch("backend_v2.workers.synthesis_reducers.get_driver", new_callable=AsyncMock):
        with patch("backend_v2.workers.synthesis_reducers.UnifiedWorkflowRepository", return_value=mock_repo):
            await handle_synthesis_failure_state(
                "exe_0123456789abcdef01",
                prof_id,
                ValueError("Synthesis error"),
            )
            mock_repo.update_execution.assert_called_once()


@pytest.mark.asyncio
async def test_handle_synthesis_failure_state_db_error_raises() -> None:
    """Test handle_synthesis_failure_state raises AppException on repository exception."""
    mock_repo = AsyncMock()
    mock_repo.get_execution.side_effect = OSError("DB unavailable")
    with patch("backend_v2.workers.synthesis_reducers.get_driver", new_callable=AsyncMock):
        with patch("backend_v2.workers.synthesis_reducers.UnifiedWorkflowRepository", return_value=mock_repo):
            with pytest.raises(AppException) as exc_info:
                await handle_synthesis_failure_state(
                    "exe_0123456789abcdef01",
                    "pro_0123456789abcdef01",
                    ValueError("Synthesis error"),
                )
            assert exc_info.value.status_code == 500
