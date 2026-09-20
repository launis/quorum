"""Unit tests for variance_synthesis.py covering metrics extraction, validation, and task building."""

from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.linguistics import LinguisticsResultDTO, PerformativePatternDTO
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.dtos.atom_result import ExtensionMetricsDTO
from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput
from backend_v2.models.enums import ExecutionStatus, TargetBlockType, XaiExtensionType
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import TraceEvent
from backend_v2.workers.variance_synthesis import (
    VarianceExplanationResult,
    build_variance_metrics_and_task,
)

TARGET_BLOCK_ID = "blk_0123456789abcdef01"


def _make_execution(
    trace_events: list[TraceEvent] | None = None,
    context_vars: dict[str, Any] | None = None,
) -> ExecutionRecord:
    return ExecutionRecord(
        id="exe_0123456789abcdef01",
        workflow_id="wor_0123456789abcdef01",
        output_profile_id="pro_0123456789abcdef01",
        status=ExecutionStatus.PASSED,
        target_locale="en",
        metadata=ExecutionMetadata(),
        execution_trace=trace_events or [],
        context_variables=context_vars or {},
    )


def _make_profile(
    has_ext: bool = True,
    target_block: str | None = TARGET_BLOCK_ID,
    directive: str | None = "Synthesize variance findings.",
    tone: str | None = None,
    length_constraint: int | None = None,
) -> OutputProfile:
    exts = [XaiExtensionType.VARIANCE_VALIDATION] if has_ext else []
    target_blk = target_block if has_ext else None
    return OutputProfile(
        id="pro_0123456789abcdef01",
        slug="prof_test",
        workflow_id="wor_0123456789abcdef01",
        name=I18nText(translations={"en": "Test Profile"}),
        visible_workflow_extensions=exts,
        variance_target_block=target_blk,
        variance_synthesis_directive=directive,
        tone_instruction=tone,
        variance_length_constraint=length_constraint,
        target_block_order=[TargetBlockType.EXECUTIVE_SUMMARY_BLOCK],
    )


def test_variance_explanation_result_schema() -> None:
    """Test VarianceExplanationResult strict schema."""
    res = VarianceExplanationResult(explanation="Clear explanation")
    assert res.explanation == "Clear explanation"
    with pytest.raises(ValidationError):
        VarianceExplanationResult.model_validate({"explanation": "x", "extra": "forbidden"})


@pytest.mark.asyncio
async def test_build_variance_metrics_none_profile() -> None:
    """Test build_variance_metrics_and_task returns (None, None) when profile is None."""
    rec = _make_execution()

    async def dummy_sem(coro: Any) -> Any:
        return await coro

    m, t = await build_variance_metrics_and_task(AsyncMock(), rec, None, "en", None, dummy_sem)
    assert m is None
    assert t is None


@pytest.mark.asyncio
async def test_build_variance_metrics_no_variance_extension() -> None:
    """Test build_variance_metrics_and_task returns (None, None) when extension is absent."""
    rec = _make_execution()
    prof = _make_profile(has_ext=False)

    async def dummy_sem(coro: Any) -> Any:
        return await coro

    m, t = await build_variance_metrics_and_task(AsyncMock(), rec, prof, "en", None, dummy_sem)
    assert m is None
    assert t is None


@pytest.mark.asyncio
async def test_build_variance_metrics_missing_target_block_raises() -> None:
    """Test build_variance_metrics_and_task raises AppException if variance_target_block missing."""
    rec = _make_execution()
    prof = OutputProfile.model_construct(
        id="pro_0123456789abcdef01",
        slug="prof_test",
        workflow_id="wor_0123456789abcdef01",
        name=I18nText(translations={"en": "Test Profile"}),
        visible_workflow_extensions=[XaiExtensionType.VARIANCE_VALIDATION],
        variance_target_block=None,
        target_block_order=[TargetBlockType.EXECUTIVE_SUMMARY_BLOCK],
    )

    async def dummy_sem(coro: Any) -> Any:
        return await coro

    with pytest.raises(AppException) as exc_info:
        await build_variance_metrics_and_task(AsyncMock(), rec, prof, "en", None, dummy_sem)
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_build_variance_metrics_missing_metrics_returns_none() -> None:
    """Test build_variance_metrics_and_task returns (None, None) when metrics cannot be extracted."""
    rec = _make_execution()
    prof = _make_profile(has_ext=True, target_block=TARGET_BLOCK_ID)

    async def dummy_sem(coro: Any) -> Any:
        return await coro

    m, t = await build_variance_metrics_and_task(AsyncMock(), rec, prof, "en", None, dummy_sem)
    assert m is None
    assert t is None


@pytest.mark.asyncio
async def test_build_variance_metrics_corrupted_linguistics_raises() -> None:
    """Test build_variance_metrics_and_task raises AppException on corrupted step_linguistics in trace."""
    evt = TraceEvent(
        v=1,
        timestamp=datetime.now(timezone.utc),
        event_type="decision",
        step_name="st",
        content={"step_linguistics": "not_a_valid_linguistics_payload"},
    )
    rec = _make_execution(trace_events=[evt])
    prof = _make_profile(has_ext=True, target_block=TARGET_BLOCK_ID)

    async def dummy_sem(coro: Any) -> Any:
        return await coro

    with pytest.raises(AppException) as exc_info:
        await build_variance_metrics_and_task(AsyncMock(), rec, prof, "en", None, dummy_sem)
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_build_variance_metrics_corrupted_matrix_output_raises() -> None:
    """Test build_variance_metrics_and_task raises AppException on corrupted matrix output in trace."""
    pat = PerformativePatternDTO(pattern_id="pat_1", detected_phrase="phrase", category="filler")
    ling = LinguisticsResultDTO(performative_patterns=[pat], total_word_count=100)
    evt_ling = TraceEvent(
        v=1,
        timestamp=datetime.now(timezone.utc),
        event_type="decision",
        step_name="st",
        content={"step_linguistics": ling.model_dump(mode="json")},
    )
    evt_mat = TraceEvent(
        v=1,
        timestamp=datetime.now(timezone.utc),
        event_type="output",
        step_name="st",
        content={TARGET_BLOCK_ID: "corrupted_matrix_value"},
    )
    rec = _make_execution(trace_events=[evt_ling, evt_mat])
    prof = _make_profile(has_ext=True, target_block=TARGET_BLOCK_ID)

    async def dummy_sem(coro: Any) -> Any:
        return await coro

    with pytest.raises(AppException) as exc_info:
        await build_variance_metrics_and_task(AsyncMock(), rec, prof, "en", None, dummy_sem)
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_build_variance_metrics_missing_directive_returns_metrics_only() -> None:
    """Test build_variance_metrics_and_task returns (metrics, None) when directive is empty."""
    pat = PerformativePatternDTO(pattern_id="pat_1", detected_phrase="phrase", category="filler")
    ling = LinguisticsResultDTO(performative_patterns=[pat], total_word_count=100)
    mat = LightweightMatrixOutput(raw_score=2.5)
    rec = _make_execution(
        context_vars={"step_linguistics": ling.model_dump(mode="json")},
        trace_events=[
            TraceEvent(
                v=1,
                timestamp=datetime.now(timezone.utc),
                event_type="output",
                step_name="st",
                content={TARGET_BLOCK_ID: mat.model_dump(mode="json")},
            )
        ],
    )
    prof = _make_profile(has_ext=True, target_block=TARGET_BLOCK_ID, directive="")

    async def dummy_sem(coro: Any) -> Any:
        return await coro

    with patch("backend_v2.workers.variance_synthesis.LLMClient.from_tier", return_value=AsyncMock()):
        metrics, task = await build_variance_metrics_and_task(AsyncMock(), rec, prof, "en", None, dummy_sem)
    assert isinstance(metrics, ExtensionMetricsDTO)
    assert metrics.authenticity_score == 2.5
    assert metrics.performative_phrases_count == 1.0
    assert metrics.total_word_count == 100
    assert task is None


@pytest.mark.asyncio
async def test_build_variance_metrics_full_success_with_tone_and_budget() -> None:
    """Test build_variance_metrics_and_task builds task with tone and length constraints."""
    pat1 = PerformativePatternDTO(pattern_id="p1", detected_phrase="phrase1", category="filler")
    pat2 = PerformativePatternDTO(pattern_id="p2", detected_phrase="phrase2", category="filler")
    ling = LinguisticsResultDTO(performative_patterns=[pat1, pat2], total_word_count=200)
    mat = LightweightMatrixOutput(raw_score=2.8)
    rec = _make_execution(
        context_vars={"step_linguistics": ling.model_dump(mode="json")},
        trace_events=[
            TraceEvent(
                v=1,
                timestamp=datetime.now(timezone.utc),
                event_type="output",
                step_name="st",
                content={TARGET_BLOCK_ID: mat.model_dump(mode="json")},
            )
        ],
    )
    prof = _make_profile(
        has_ext=True,
        target_block=TARGET_BLOCK_ID,
        directive="Evaluate variance.",
        tone="Analytical and objective",
        length_constraint=150,
    )
    mock_client = AsyncMock()
    mock_client.run_structured_task.return_value = VarianceExplanationResult(explanation="Evaluated variance.")

    async def dummy_sem(coro: Any) -> Any:
        return await coro

    with patch("backend_v2.workers.variance_synthesis.LLMClient.from_tier", return_value=mock_client):
        metrics, task = await build_variance_metrics_and_task(
            AsyncMock(), rec, prof, "en", "reg_123", dummy_sem
        )
        assert isinstance(metrics, ExtensionMetricsDTO)
        assert metrics.authenticity_score == 2.8
        assert metrics.performative_phrases_count == 2.0
        assert metrics.total_word_count == 200
        assert isinstance(task, VarianceExplanationResult)
        assert task.explanation == "Evaluated variance."
