"""Unit tests for variance_synthesis.py covering metrics extraction, validation, and task building."""

from datetime import datetime, timezone
from typing import Any, Literal, cast
from unittest.mock import AsyncMock, patch

import pytest
from pydantic import ValidationError

from backend_v2.database.repository import UnifiedWorkflowRepository
from backend_v2.exceptions import AppException, ConfigurationError, ErrorCodes
from backend_v2.models.auth import SystemOrganizations
from backend_v2.models.core_base import I18nText, generate_uuid7
from backend_v2.models.domain.execution import ExecutionRecord, FrozenContext
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.domain.linguistics import LinguisticsResultDTO, PerformativePatternDTO
from backend_v2.models.domain.matrix import MatrixScale
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock
from backend_v2.models.dtos.atom_result import ExtensionMetricsDTO
from backend_v2.models.dtos.context_variables import ContextVariablesDTO, ContextVariableValue
from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput
from backend_v2.models.dtos.schema_manifest import GeneratedSchemaManifestDTO
from backend_v2.models.dtos.theory_manifest import InjectedTheoryManifestDTO
from backend_v2.models.dtos.trace import TraceEventMetadataDTO
from backend_v2.models.enums import ExecutionStatus, TargetBlockType, XaiExtensionType
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import TraceEvent
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository
from backend_v2.workers.variance_synthesis import (
    VarianceExplanationResult,
    build_variance_metrics_and_task,
)

TARGET_BLOCK_ID = "blk_0195f3a00000700283456789abcdef01"


def _make_matrix_prompt_block(
    block_id: str = TARGET_BLOCK_ID,
    computed_max: int = 3,
) -> MatrixPromptBlock:
    return MatrixPromptBlock(
        id=block_id,
        slug="test_matrix",
        label=I18nText(translations={"en": "Test Matrix"}),
        description=I18nText(translations={"en": "Test Description"}),
        output_extensions=[],
        scales=[
            MatrixScale(score=1, ai_label="POOR", claims=[]),
            MatrixScale(score=computed_max if computed_max > 0 else 1, ai_label="EXCELLENT", claims=[]),
        ],
        computed_min=1,
        computed_max=computed_max,
    )


async def _make_fake_repo(target_block: MatrixPromptBlock | None = None) -> UnifiedWorkflowRepository:
    fake_repo = InMemoryUnifiedWorkflowRepository()
    await fake_repo.create_prompt_block(target_block or _make_matrix_prompt_block())
    return cast(UnifiedWorkflowRepository, fake_repo)


def _make_trace_event(
    event_type: Literal[
        "input", "reasoning", "decision", "error", "output", "tombstone", "evidence_override", "progress"
    ],
    step_name: str,
    content: Any = None,
) -> TraceEvent:
    return TraceEvent(
        event_id=generate_uuid7(),
        v=1,
        timestamp=datetime.now(timezone.utc),
        event_type=event_type,
        step_name=step_name,
        content=content,
        metadata=TraceEventMetadataDTO(mcp_audit_traces=[]),
        mcp_audit_traces=[],
    )


def _make_execution(
    trace_events: list[TraceEvent] | None = None,
    context_vars: dict[str, ContextVariableValue] | None = None,
    organization_id: str | None = None,
    raw_inputs_org_id: str | None = None,
) -> ExecutionRecord:
    cv = ContextVariablesDTO(variables=context_vars or {})
    return ExecutionRecord(
        id="exe_0195f3a00000700283456789abcdef01",
        workflow_id="wor_0195f3a00000700283456789abcdef01",
        output_profile_id="pro_0195f3a00000700283456789abcdef01",
        organization_id=organization_id,
        status=ExecutionStatus.PASSED,
        target_locale="en",
        metadata=ExecutionMetadata(),
        execution_trace=trace_events or [],
        context_variables=cv,
        raw_inputs=WorkflowInputs(organization_id=raw_inputs_org_id, dynamic_inputs={}),
        frozen_context=FrozenContext(
            compiled_prompts={},
            injected_theory=InjectedTheoryManifestDTO(theories={}),
            generated_schemas=GeneratedSchemaManifestDTO(schemas={}),
            ui_hints_snapshot={},
            mcp_tool_audit=[],
        ),
        steps=[],
        step_states={},
        profile_syntheses={},
        source_identity_manifest={},
        models_used={},
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def _make_profile(
    has_ext: bool = True,
    target_block: str | None = TARGET_BLOCK_ID,
    directive: str | None = "Synthesize variance findings.",
    tone: str | None = None,
    length_constraint: int | None = None,
) -> OutputProfile:
    exts: list[XaiExtensionType] = [XaiExtensionType.VARIANCE_VALIDATION] if has_ext else []
    target_blk = target_block if has_ext else None
    return OutputProfile(
        id="pro_0195f3a00000700283456789abcdef01",
        slug="prof_test",
        workflow_id="wor_0195f3a00000700283456789abcdef01",
        name=I18nText(translations={"en": "Test Profile"}),
        visible_metadata=[],
        matrix_visible_columns=[],
        visible_block_extensions=[],
        visible_workflow_extensions=exts,
        matrix_synthesis_groups=[],
        content_blocks=[],
        variance_target_block=target_blk,
        variance_synthesis_directive=directive,
        tone_instruction=tone,
        variance_length_constraint=length_constraint,
        target_block_order=[TargetBlockType.EXECUTIVE_SUMMARY_BLOCK],
    )


def test_variance_explanation_result_schema() -> None:
    """Test VarianceExplanationResult strict and frozen schema."""
    res = VarianceExplanationResult(explanation="Clear explanation")
    assert res.explanation == "Clear explanation"
    assert VarianceExplanationResult.model_config["frozen"] is True
    with pytest.raises(ValidationError):
        VarianceExplanationResult.model_validate({"explanation": "x", "extra": "forbidden"})


@pytest.mark.asyncio
async def test_build_variance_metrics_none_profile() -> None:
    """Test build_variance_metrics_and_task returns (None, None) when profile is None."""
    rec = _make_execution()

    async def dummy_sem(coro: Any) -> Any:
        return await coro

    m, t = await build_variance_metrics_and_task(await _make_fake_repo(), rec, None, "en", None, dummy_sem)
    assert m is None
    assert t is None


@pytest.mark.asyncio
async def test_build_variance_metrics_no_variance_extension() -> None:
    """Test build_variance_metrics_and_task returns (None, None) when extension is absent."""
    rec = _make_execution()
    prof = _make_profile(has_ext=False)

    async def dummy_sem(coro: Any) -> Any:
        return await coro

    m, t = await build_variance_metrics_and_task(await _make_fake_repo(), rec, prof, "en", None, dummy_sem)
    assert m is None
    assert t is None


@pytest.mark.asyncio
async def test_build_variance_metrics_missing_target_block_raises() -> None:
    """Test build_variance_metrics_and_task raises AppException if variance_target_block missing."""
    rec = _make_execution()
    prof = OutputProfile.model_construct(
        id="pro_0195f3a00000700283456789abcdef01",
        slug="prof_test",
        workflow_id="wor_0195f3a00000700283456789abcdef01",
        name=I18nText(translations={"en": "Test Profile"}),
        visible_metadata=[],
        matrix_visible_columns=[],
        visible_block_extensions=[],
        visible_workflow_extensions=[XaiExtensionType.VARIANCE_VALIDATION],
        matrix_synthesis_groups=[],
        content_blocks=[],
        variance_target_block=None,
        target_block_order=[TargetBlockType.EXECUTIVE_SUMMARY_BLOCK],
    )

    async def dummy_sem(coro: Any) -> Any:
        return await coro

    with pytest.raises(AppException) as exc_info:
        await build_variance_metrics_and_task(await _make_fake_repo(), rec, prof, "en", None, dummy_sem)
    assert exc_info.value.status_code == 400
    assert exc_info.value.details == {"error_code": ErrorCodes.CONFIGURATION_ERROR.value}


@pytest.mark.asyncio
async def test_build_variance_metrics_missing_metrics_returns_none() -> None:
    """Test build_variance_metrics_and_task returns (None, None) when metrics cannot be extracted."""
    rec = _make_execution()
    prof = _make_profile(has_ext=True, target_block=TARGET_BLOCK_ID)

    async def dummy_sem(coro: Any) -> Any:
        return await coro

    m, t = await build_variance_metrics_and_task(await _make_fake_repo(), rec, prof, "en", None, dummy_sem)
    assert m is None
    assert t is None


@pytest.mark.asyncio
async def test_build_variance_metrics_corrupted_linguistics_raises() -> None:
    """Test build_variance_metrics_and_task raises AppException on corrupted step_linguistics in trace."""
    evt = _make_trace_event(
        event_type="decision",
        step_name="st",
        content={"step_linguistics": "not_a_valid_linguistics_payload"},
    )
    rec = _make_execution(trace_events=[evt])
    prof = _make_profile(has_ext=True, target_block=TARGET_BLOCK_ID)

    async def dummy_sem(coro: Any) -> Any:
        return await coro

    with pytest.raises(AppException) as exc_info:
        await build_variance_metrics_and_task(await _make_fake_repo(), rec, prof, "en", None, dummy_sem)
    assert exc_info.value.status_code == 500
    assert exc_info.value.details == {"error_code": ErrorCodes.VALIDATION_FAILED.value}


@pytest.mark.asyncio
async def test_build_variance_metrics_corrupted_matrix_output_raises() -> None:
    """Test build_variance_metrics_and_task raises AppException on corrupted matrix output in trace."""
    pat = PerformativePatternDTO(pattern_id="pat_1", detected_phrase="phrase", category="filler")
    ling = LinguisticsResultDTO(performative_patterns=[pat], total_word_count=100)
    evt_ling = _make_trace_event(
        event_type="decision",
        step_name="st",
        content={"step_linguistics": ling.model_dump(mode="json")},
    )
    evt_mat = _make_trace_event(
        event_type="output",
        step_name="st",
        content={TARGET_BLOCK_ID: "corrupted_matrix_value"},
    )
    rec = _make_execution(trace_events=[evt_ling, evt_mat])
    prof = _make_profile(has_ext=True, target_block=TARGET_BLOCK_ID)

    async def dummy_sem(coro: Any) -> Any:
        return await coro

    with pytest.raises(AppException) as exc_info:
        await build_variance_metrics_and_task(await _make_fake_repo(), rec, prof, "en", None, dummy_sem)
    assert exc_info.value.status_code == 500
    assert exc_info.value.details == {"error_code": ErrorCodes.VALIDATION_FAILED.value}


@pytest.mark.asyncio
async def test_build_variance_metrics_target_block_not_found_raises_configuration_error() -> None:
    """Negative: target prompt block not found in repository raises CONFIGURATION_ERROR."""
    pat = PerformativePatternDTO(pattern_id="pat_1", detected_phrase="phrase", category="filler")
    ling = LinguisticsResultDTO(performative_patterns=[pat], total_word_count=100)
    mat = LightweightMatrixOutput(raw_score=2.5, evaluated_atoms={}, extensions={})
    rec = _make_execution(
        context_vars={"step_linguistics": ling},
        trace_events=[
            _make_trace_event(
                event_type="output",
                step_name="st",
                content={TARGET_BLOCK_ID: mat.model_dump(mode="json")},
            )
        ],
    )
    prof = _make_profile(has_ext=True, target_block=TARGET_BLOCK_ID)
    fake_repo = cast(UnifiedWorkflowRepository, InMemoryUnifiedWorkflowRepository())

    async def dummy_sem(coro: Any) -> Any:
        return await coro

    with pytest.raises(AppException) as exc_info:
        await build_variance_metrics_and_task(fake_repo, rec, prof, "en", None, dummy_sem)
    assert exc_info.value.status_code == 500
    assert "not found in repository" in exc_info.value.message
    assert exc_info.value.details == {"error_code": ErrorCodes.CONFIGURATION_ERROR.value}


@pytest.mark.asyncio
async def test_build_variance_metrics_target_block_invalid_extrema_raises_configuration_error() -> None:
    """Negative: target prompt block with non-positive computed_max raises CONFIGURATION_ERROR."""
    pat = PerformativePatternDTO(pattern_id="pat_1", detected_phrase="phrase", category="filler")
    ling = LinguisticsResultDTO(performative_patterns=[pat], total_word_count=100)
    mat = LightweightMatrixOutput(raw_score=2.5, evaluated_atoms={}, extensions={})
    rec = _make_execution(
        context_vars={"step_linguistics": ling},
        trace_events=[
            _make_trace_event(
                event_type="output",
                step_name="st",
                content={TARGET_BLOCK_ID: mat.model_dump(mode="json")},
            )
        ],
    )
    prof = _make_profile(has_ext=True, target_block=TARGET_BLOCK_ID)
    invalid_block = _make_matrix_prompt_block(computed_max=0)
    fake_repo = InMemoryUnifiedWorkflowRepository()
    await fake_repo.create_prompt_block(invalid_block)

    async def dummy_sem(coro: Any) -> Any:
        return await coro

    with pytest.raises(AppException) as exc_info:
        await build_variance_metrics_and_task(
            cast(UnifiedWorkflowRepository, fake_repo), rec, prof, "en", None, dummy_sem
        )
    assert exc_info.value.status_code == 500
    assert "lacks valid scale extrema definitions" in exc_info.value.message
    assert exc_info.value.details == {"error_code": ErrorCodes.CONFIGURATION_ERROR.value}


@pytest.mark.asyncio
async def test_build_variance_metrics_missing_directive_returns_metrics_only() -> None:
    """Test build_variance_metrics_and_task returns (metrics, None) when directive is empty."""
    pat = PerformativePatternDTO(pattern_id="pat_1", detected_phrase="phrase", category="filler")
    ling = LinguisticsResultDTO(performative_patterns=[pat], total_word_count=100)
    mat = LightweightMatrixOutput(raw_score=2.5, evaluated_atoms={}, extensions={})
    rec = _make_execution(
        context_vars={"step_linguistics": ling},
        trace_events=[
            _make_trace_event(
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
        metrics, task = await build_variance_metrics_and_task(await _make_fake_repo(), rec, prof, "en", None, dummy_sem)
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
    mat = LightweightMatrixOutput(raw_score=2.8, evaluated_atoms={}, extensions={})
    rec = _make_execution(
        context_vars={"step_linguistics": ling},
        trace_events=[
            _make_trace_event(
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
            await _make_fake_repo(), rec, prof, "en", "reg_123", dummy_sem
        )
        assert isinstance(metrics, ExtensionMetricsDTO)
        assert metrics.authenticity_score == 2.8
        assert metrics.performative_phrases_count == 2.0
        assert metrics.total_word_count == 200
        assert isinstance(task, VarianceExplanationResult)
        assert task.explanation == "Evaluated variance."


@pytest.mark.asyncio
async def test_build_variance_metrics_trace_extraction_direct_models() -> None:
    """Test metrics extraction when linguistics and matrix models are directly in trace events."""
    pat = PerformativePatternDTO(pattern_id="p1", detected_phrase="phrase1", category="filler")
    ling = LinguisticsResultDTO(performative_patterns=[pat], total_word_count=50)
    mat = LightweightMatrixOutput(raw_score=2.2, evaluated_atoms={}, extensions={})

    evt_ling = _make_trace_event(
        event_type="decision",
        step_name="st_dec",
        content={"step_linguistics": ling.model_dump(mode="json")},
    )
    evt_mat = TraceEvent.model_construct(
        event_id=generate_uuid7(),
        v=1,
        timestamp=datetime.now(timezone.utc),
        event_type="output",
        step_name="st_out",
        content=mat,
        metadata=TraceEventMetadataDTO(mcp_audit_traces=[]),
        mcp_audit_traces=[],
    )
    evt_in = _make_trace_event(event_type="input", step_name="st_in", content=None)
    rec = _make_execution(trace_events=[evt_ling, evt_mat, evt_in])
    prof = _make_profile(
        has_ext=True,
        target_block=TARGET_BLOCK_ID,
        directive="Evaluate variance.",
    )
    mock_client = AsyncMock()
    mock_client.run_structured_task.return_value = VarianceExplanationResult(explanation="Done.")

    async def dummy_sem(coro: Any) -> Any:
        return await coro

    with patch("backend_v2.workers.variance_synthesis.LLMClient.from_tier", return_value=mock_client):
        metrics, task = await build_variance_metrics_and_task(await _make_fake_repo(), rec, prof, "en", None, dummy_sem)
        assert isinstance(metrics, ExtensionMetricsDTO)
        assert metrics.authenticity_score == 2.2
        assert metrics.performative_phrases_count == 1.0
        assert metrics.total_word_count == 50
        assert isinstance(task, VarianceExplanationResult)


@pytest.mark.asyncio
async def test_build_variance_metrics_propagates_tenant_organization_id_to_llm_client() -> None:
    """Phase 1, Step 3: Verify execution.organization_id and raw_inputs.organization_id are passed to LLMClient.from_tier."""
    pat = PerformativePatternDTO(pattern_id="p1", detected_phrase="phrase1", category="filler")
    ling = LinguisticsResultDTO(performative_patterns=[pat], total_word_count=100)
    mat = LightweightMatrixOutput(raw_score=2.5, evaluated_atoms={}, extensions={})
    evt_out = _make_trace_event(
        event_type="output",
        step_name="st",
        content={TARGET_BLOCK_ID: mat.model_dump(mode="json")},
    )
    tenant_org_id = "org_0195f3a0000070008000000000000777"
    raw_org_id = "org_0195f3a0000070008000000000000888"

    rec_direct = _make_execution(
        context_vars={"step_linguistics": ling},
        trace_events=[evt_out],
        organization_id=tenant_org_id,
    )
    rec_raw = _make_execution(
        context_vars={"step_linguistics": ling},
        trace_events=[evt_out],
        organization_id=None,
        raw_inputs_org_id=raw_org_id,
    )
    prof = _make_profile(has_ext=True, target_block=TARGET_BLOCK_ID, directive="Evaluate variance.")
    mock_client = AsyncMock()
    mock_client.run_structured_task.return_value = VarianceExplanationResult(explanation="Done.")

    async def dummy_sem(coro: Any) -> Any:
        return await coro

    repo = await _make_fake_repo()
    with patch(
        "backend_v2.workers.variance_synthesis.LLMClient.from_tier",
        new_callable=AsyncMock,
        return_value=mock_client,
    ) as mock_from_tier:
        await build_variance_metrics_and_task(
            repo, rec_direct, prof, "en", "sys_0195f3a0000070018111222233334444", dummy_sem
        )
        mock_from_tier.assert_awaited_once()
        assert mock_from_tier.await_args is not None
        assert mock_from_tier.await_args.kwargs["organization_id"] == tenant_org_id

        mock_from_tier.reset_mock()
        await build_variance_metrics_and_task(
            repo, rec_raw, prof, "en", "sys_0195f3a0000070018111222233334444", dummy_sem
        )
        mock_from_tier.assert_awaited_once()
        assert mock_from_tier.await_args is not None
        assert mock_from_tier.await_args.kwargs["organization_id"] == raw_org_id


@pytest.mark.asyncio
async def test_build_variance_metrics_defaults_organization_id_to_root_system() -> None:
    """Phase 1, Step 3: Verify missing organization_id defaults to SystemOrganizations.ROOT_SYSTEM."""
    pat = PerformativePatternDTO(pattern_id="p1", detected_phrase="phrase1", category="filler")
    ling = LinguisticsResultDTO(performative_patterns=[pat], total_word_count=100)
    mat = LightweightMatrixOutput(raw_score=2.5, evaluated_atoms={}, extensions={})
    evt_out = _make_trace_event(
        event_type="output",
        step_name="st",
        content={TARGET_BLOCK_ID: mat.model_dump(mode="json")},
    )
    rec_root = _make_execution(
        context_vars={"step_linguistics": ling},
        trace_events=[evt_out],
        organization_id=None,
        raw_inputs_org_id=None,
    )
    prof = _make_profile(has_ext=True, target_block=TARGET_BLOCK_ID, directive="Evaluate variance.")
    mock_client = AsyncMock()
    mock_client.run_structured_task.return_value = VarianceExplanationResult(explanation="Done.")

    async def dummy_sem(coro: Any) -> Any:
        return await coro

    repo = await _make_fake_repo()
    with patch(
        "backend_v2.workers.variance_synthesis.LLMClient.from_tier",
        new_callable=AsyncMock,
        return_value=mock_client,
    ) as mock_from_tier:
        await build_variance_metrics_and_task(repo, rec_root, prof, "en", None, dummy_sem)
        mock_from_tier.assert_awaited_once()
        assert mock_from_tier.await_args is not None
        assert mock_from_tier.await_args.kwargs["organization_id"] == SystemOrganizations.ROOT_SYSTEM.value


@pytest.mark.asyncio
async def test_build_variance_metrics_byok_secret_resolution_failure_fails_fast() -> None:
    """Phase 1, Step 3 (Negative): ConfigurationError from LLMClient.from_tier propagates fail-fast."""
    pat = PerformativePatternDTO(pattern_id="p1", detected_phrase="phrase1", category="filler")
    ling = LinguisticsResultDTO(performative_patterns=[pat], total_word_count=100)
    mat = LightweightMatrixOutput(raw_score=2.5, evaluated_atoms={}, extensions={})
    evt_out = _make_trace_event(
        event_type="output",
        step_name="st",
        content={TARGET_BLOCK_ID: mat.model_dump(mode="json")},
    )
    rec = _make_execution(
        context_vars={"step_linguistics": ling},
        trace_events=[evt_out],
        organization_id="org_0195f3a0000070008000000000000777",
    )
    prof = _make_profile(has_ext=True, target_block=TARGET_BLOCK_ID, directive="Evaluate variance.")

    async def dummy_sem(coro: Any) -> Any:
        return await coro

    repo = await _make_fake_repo()
    with (
        patch(
            "backend_v2.workers.variance_synthesis.LLMClient.from_tier",
            new_callable=AsyncMock,
            side_effect=ConfigurationError(
                message="Corrupted BYOK secret for tenant org_0195f3a0000070008000000000000777",
                details={"error_code": ErrorCodes.SECRET_RESOLUTION_FAILED.value},
            ),
        ),
        pytest.raises(ConfigurationError) as exc_info,
    ):
        await build_variance_metrics_and_task(repo, rec, prof, "en", None, dummy_sem)

    assert exc_info.value.details["error_code"] == ErrorCodes.SECRET_RESOLUTION_FAILED.value
