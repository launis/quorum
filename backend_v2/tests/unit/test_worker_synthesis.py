"""Unit tests for worker background synthesis tasks and trace extraction."""

from __future__ import annotations

from collections.abc import Generator, Mapping
from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from polyfactory.factories.pydantic_factory import ModelFactory

import backend_v2.workers.synthesis_worker as synthesis_worker_mod
from backend_v2.exceptions import AppException
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.matrix import MatrixScale
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.step import StepRule
from backend_v2.models.domain.synthesis import MatrixSynthesisGroup, RenderedSynthesisCache
from backend_v2.models.domain.system_config import (
    ChatMessageDTO,
    ModelProfile,
    SystemConfigModelRegistry,
)
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.dtos.context_variables import ContextVariablesDTO
from backend_v2.models.dtos.schema_manifest import JsonSchemaNode
from backend_v2.models.dtos.synthesis import (
    ExecutiveSummarySectionResult,
    MatrixExplanationsResult,
    MatrixSectionSynthesesResult,
    SynthesisSectionDTO,
    XaiHighlightsResult,
)
from backend_v2.models.enums import (
    BlockDataType,
    CognitiveTier,
    DisplayScale,
    ExecutionStatus,
    HistoricalContextMode,
    LLMProvider,
    PromptBlockCategory,
    RoleClassification,
    TargetBlockType,
    XaiExtensionType,
)
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.llm import LLMMessageDTO
from backend_v2.models.state import TraceEvent
from backend_v2.models.view.sdui import ParagraphBlock
from backend_v2.settings import get_settings
from backend_v2.tests.factories.model_factories import (
    ExecutionRecordFactory,
    MatrixPromptBlockFactory,
    OutputProfileFactory,
    SystemRulePromptBlockFactory,
    WorkflowFactory,
)
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository
from backend_v2.workers import VarianceExplanationResult, generate_profile_synthesis_and_pdf_task


class _ModelProfileFactory(ModelFactory[ModelProfile]):
    """Polyfactory model factory for deterministic ModelProfile configurations."""

    __model__ = ModelProfile
    __use_defaults__ = True


class _ModelRegistryFactory(ModelFactory[SystemConfigModelRegistry]):
    """Polyfactory model factory for deterministic SystemConfigModelRegistry instances."""

    __model__ = SystemConfigModelRegistry
    __use_defaults__ = True


class _TraceEventFactory(ModelFactory[TraceEvent]):
    """Polyfactory model factory for deterministic TraceEvent instances."""

    __model__ = TraceEvent
    __use_defaults__ = True


class _MatrixSynthesisGroupFactory(ModelFactory[MatrixSynthesisGroup]):
    """Polyfactory model factory for deterministic MatrixSynthesisGroup instances."""

    __model__ = MatrixSynthesisGroup
    __use_defaults__ = True


class _DeterministicExecutionRecordFactory(ExecutionRecordFactory):
    """ExecutionRecord factory preserving Pydantic defaults on unset optional fields."""

    __use_defaults__ = True


class _DeterministicWorkflowFactory(WorkflowFactory):
    """Workflow factory preserving Pydantic defaults on unset optional fields."""

    __use_defaults__ = True


class _DeterministicOutputProfileFactory(OutputProfileFactory):
    """OutputProfile factory preserving Pydantic defaults on unset optional fields."""

    __use_defaults__ = True


@pytest.fixture(autouse=True)
def mock_worker_report_service() -> Generator[MagicMock]:
    """Mock ReportService for background worker synthesis tasks.

    Yields:
        Mocked ReportService instance.
    """
    mock_artifact = MagicMock()
    mock_artifact.id = "rep_0195f3a0000070018234567890123456"
    mock_svc = MagicMock()
    mock_svc.get_or_create_default_artifact = AsyncMock(return_value=mock_artifact)
    mock_svc.compile_and_persist_artifact = AsyncMock()
    with (
        patch("backend_v2.workers.synthesis_worker.ReportService", return_value=mock_svc),
        patch("backend_v2.workers.synthesis_reducers.ReportService", return_value=mock_svc),
    ):
        yield mock_svc


async def _get_profile_syntheses(
    repo: InMemoryUnifiedWorkflowRepository,
    exec_id: str = "exec_0195f3a0000070018234567812345678",
) -> dict[str, RenderedSynthesisCache] | None:
    """Fetch profile_syntheses from the persisted ExecutionRecord when available.

    Args:
        repo: Seeded InMemoryUnifiedWorkflowRepository instance.
        exec_id: Target execution identifier.

    Returns:
        Dictionary of profile synthesis caches or None if unset.
    """
    rec = await repo.get_execution(exec_id)
    if rec and rec.profile_syntheses:
        return rec.profile_syntheses
    return None


def _get_base_model_registry() -> SystemConfigModelRegistry:
    """Build the default test SystemConfigModelRegistry routed to mock_llm_99.

    Returns:
        Configured SystemConfigModelRegistry instance.
    """
    profile = _ModelProfileFactory.build(
        provider="mock_llm_99",
        model_name="gemini-2.5-pro",
        temperature=0.0,
        max_tokens=1024,
        is_active=True,
        tpm_limit=100000,
        rpm_limit=1000,
    )
    return _ModelRegistryFactory.build(
        id="sys_0195f3a0000070018111222233334444",
        name="Default Test Registry",
        type="model_registry",
        slug="model_registry",
        default_provider=LLMProvider.VERTEX_AI,
        tier_definitions={
            CognitiveTier.FAST: profile,
            CognitiveTier.BALANCED: profile,
            CognitiveTier.DEEP: profile,
            CognitiveTier.REASONING: profile,
        },
    )


def _extract_captured_messages(calls: list[Any]) -> str:
    """Concatenate string message contents captured from mocked LLM task invocations.

    Args:
        calls: Recorded mock call list from run_structured_task.

    Returns:
        Concatenated prompt content string across all recorded calls.
    """
    collected: list[str] = []
    for call in calls:
        if "messages" in call.kwargs:
            for msg in call.kwargs["messages"]:
                if isinstance(msg, (ChatMessageDTO, LLMMessageDTO)) and isinstance(msg.content, str):
                    collected.append(msg.content)
    return " ".join(collected)


@pytest.mark.asyncio
async def test_worker_extracts_synthesis_from_trace() -> None:
    """Verify the worker background task extracts synthesis payload from the DAG execution trace."""
    get_settings().use_mock_llm = True

    mock_repo = InMemoryUnifiedWorkflowRepository()

    trace_event = _TraceEventFactory.build(
        v=1,
        timestamp=datetime.now(UTC),
        event_type="output",
        step_name="sr_0195f3a0000070018234567812345678",
        content={"blk_synth12345678": {"synthesized_markdown": "Test MD"}},
    )
    mock_execution = _DeterministicExecutionRecordFactory.build(
        id="exec_0195f3a0000070018234567812345678",
        workflow_id="wf_0195f3a0000070018234567812345678",
        output_profile_id="prof_0195f3a0000070018111111111111111",
        status=ExecutionStatus.PASSED,
        target_locale="fi",
        metadata=ExecutionMetadata(),
        progress=None,
        status_message=None,
        execution_trace=[trace_event],
    )
    await mock_repo.save_execution(mock_execution)

    workflow = _DeterministicWorkflowFactory.build(
        id="wf_0195f3a0000070018234567812345678",
        slug="test_workflow",
        name=I18nText(translations={"en": "Test", "fi": "Test"}),
        description=I18nText(translations={"en": "Desc", "fi": "Desc"}),
        status="draft",
        historical_context_mode=HistoricalContextMode.DISABLED,
        version=1,
        default_profile_id="prof_0195f3a0000070018111111111111111",
        model_registry_id="sys_0195f3a0000070018111222233334444",
        expected_inputs=[],
        steps=[
            StepRule(
                id="sr_0195f3a0000070018234567812345678",
                task_blueprint="sp_0195f3a0000070018234567812345678",
                depends_on=[],
                input_mappings={},
            )
        ],
    )
    await mock_repo.save_workflow(workflow)

    mock_repo.seed_raw_step(
        "sp_0195f3a0000070018234567812345678",
        {
            "id": "sp_0195f3a0000070018234567812345678",
            "slug": "synthesis_step",
            "name": {"translations": {"en": "Synth"}},
            "cognitive_tier": "fast",
            "type": "logic",
            "hook": "text_consolidation_hook",
        },
    )

    mock_repo.set_model_registry(_get_base_model_registry(), "sys_0195f3a0000070018111222233334444")

    pb_1 = SystemRulePromptBlockFactory.build(
        id="pb_0195f3a0000070018111111111111111",
        slug="system_prompt",
        type=BlockDataType.INSTRUCTION,
        label=I18nText(translations={"en": "System"}),
        description=I18nText(translations={"en": "System prompt"}),
        category_id=PromptBlockCategory.SYSTEM_RULE,
    )
    pb_2 = SystemRulePromptBlockFactory.build(
        id="pb_0195f3a0000070028222222222222222",
        slug="synthesis_prompt",
        type=BlockDataType.INSTRUCTION,
        label=I18nText(translations={"en": "Synth System"}),
        description=I18nText(translations={"en": "System prompt for synthesis"}),
        instruction_text="You are an AI.",
        category_id=PromptBlockCategory.SYSTEM_RULE,
    )
    mock_repo.set_prompt_blocks([pb_1, pb_2])

    output_prof = _DeterministicOutputProfileFactory.build(
        id="prof_0195f3a0000070018111111111111111",
        slug="test_slug",
        workflow_id="wf_0195f3a0000070018234567812345678",
        name=I18nText(translations={"en": "Test", "fi": "Test"}),
        max_extension_items=3,
        synthesis_length_constraint=1000,
        tone_instruction="Professional",
        matrix_1d_synthesis_directive="1D DIRECTIVE",
        matrix_synthesis_groups=[
            _MatrixSynthesisGroupFactory.build(
                id="grp_0195f3a0000070018111111111111111",
                title=I18nText(translations={"en": "Group 1", "fi": "Ryhmä 1"}),
                target_blocks=["blk_1"],
                view_type="1d_metrics",
            )
        ],
        target_block_order=[TargetBlockType.MATRIX_GRAPHS_BLOCK],
        display_scale=DisplayScale.ORIGINAL,
    )
    mock_repo.set_output_profiles([output_prof])

    with patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo):
        await generate_profile_synthesis_and_pdf_task(
            execution_id="exec_0195f3a0000070018234567812345678",
            accept_language="en",
            profile_id="prof_0195f3a0000070018111111111111111",
            redis=None,
        )

    prof_synth = await _get_profile_syntheses(mock_repo)
    assert prof_synth is not None, "Execution record was not updated with profile_syntheses"
    assert type(prof_synth["prof_0195f3a0000070018111111111111111"].section_syntheses) is dict


async def _setup_mock_repo_for_metrics(
    mock_repo: InMemoryUnifiedWorkflowRepository,
    trace_content_ling: Mapping[str, JsonSchemaNode] | None,
    trace_content_det: Mapping[str, JsonSchemaNode] | None,
) -> None:
    """Seed workflow, execution trace, prompt blocks, and default profile for metric extraction tests.

    Args:
        mock_repo: Target InMemoryUnifiedWorkflowRepository instance.
        trace_content_ling: Optional linguistics decision trace content mapping.
        trace_content_det: Optional detector output trace content mapping.
    """
    trace_events: list[TraceEvent] = []
    if trace_content_ling is not None:
        trace_events.append(
            _TraceEventFactory.build(
                v=1,
                timestamp=datetime.now(UTC),
                event_type="decision",
                step_name="ling",
                content={"step_linguistics": dict(trace_content_ling)},
            )
        )
    if trace_content_det is not None:
        trace_events.append(
            _TraceEventFactory.build(
                v=1,
                timestamp=datetime.now(UTC),
                event_type="output",
                step_name="sr_det_step12345678",
                content=dict(trace_content_det),
            )
        )

    mock_execution = _DeterministicExecutionRecordFactory.build(
        id="exec_0195f3a0000070018234567812345678",
        workflow_id="wf_0195f3a0000070018234567812345678",
        output_profile_id="prof_0195f3a0000070018111111111111111",
        status=ExecutionStatus.PASSED,
        target_locale="fi",
        metadata=ExecutionMetadata(),
        progress=None,
        status_message=None,
        execution_trace=trace_events,
        context_variables=ContextVariablesDTO(variables={}),
    )
    await mock_repo.save_execution(mock_execution)

    workflow = _DeterministicWorkflowFactory.build(
        id="wf_0195f3a0000070018234567812345678",
        slug="test_workflow",
        name=I18nText(translations={"en": "Test", "fi": "Test"}),
        description=I18nText(translations={"en": "Desc", "fi": "Desc"}),
        status="draft",
        historical_context_mode=HistoricalContextMode.DISABLED,
        version=1,
        default_profile_id="prof_0195f3a0000070018111111111111111",
        model_registry_id="sys_0195f3a0000070018111222233334444",
        expected_inputs=[],
        steps=[],
    )
    await mock_repo.save_workflow(workflow)

    mock_repo.set_model_registry(_get_base_model_registry(), "sys_0195f3a0000070018111222233334444")

    pb_synth = SystemRulePromptBlockFactory.build(
        id="pb_0195f3a0000070028222222222222222",
        slug="synthesis_prompt",
        type=BlockDataType.INSTRUCTION,
        label=I18nText(translations={"en": "Synth System"}),
        description=I18nText(translations={"en": "System prompt for synthesis"}),
        instruction_text="You are an AI.",
        category_id=PromptBlockCategory.SYSTEM_RULE,
    )
    pb_target = MatrixPromptBlockFactory.build(
        id="blk_0195f3a00000700583f32679aa514fcb",
        slug="matrix_goodhart",
        type=BlockDataType.FLOAT,
        label=I18nText(translations={"en": "Target Matrix"}),
        description=I18nText(translations={"en": "Desc"}),
        category_id=PromptBlockCategory.MATRIX,
        scales=[
            MatrixScale(score=1, ai_label="L1", claims=[]),
            MatrixScale(score=5, ai_label="L5", claims=[]),
        ],
    )
    mock_repo.set_prompt_blocks([pb_synth, pb_target])

    default_prof = _DeterministicOutputProfileFactory.build(
        id="prof_0195f3a0000070018111111111111111",
        slug="prof",
        name=I18nText(translations={"en": "test"}),
        workflow_id="wf_0195f3a0000070018234567812345678",
        display_scale=DisplayScale.ORIGINAL,
        tone_instruction="Professional",
        xai_synthesis_directive="XAI DIRECTIVE",
        variance_synthesis_directive="VARIANCE DIRECTIVE",
        max_extension_items=3,
        visible_workflow_extensions=[XaiExtensionType.VARIANCE_VALIDATION],
        variance_target_block="blk_0195f3a00000700583f32679aa514fcb",
        matrix_synthesis_groups=[],
        target_block_order=[],
    )
    mock_repo.set_output_profiles([default_prof])


@pytest.mark.asyncio
async def test_worker_synthesis_extracts_metrics_from_trace() -> None:
    """Verify extracting extension metrics from execution trace during synthesis."""
    get_settings().use_mock_llm = True
    mock_repo = InMemoryUnifiedWorkflowRepository()

    await _setup_mock_repo_for_metrics(
        mock_repo,
        trace_content_ling={
            "performative_patterns": [
                {"pattern_id": "1", "detected_phrase": "phrase", "category": "cat"},
                {"pattern_id": "2", "detected_phrase": "phrase2", "category": "cat2"},
            ],
            "total_word_count": 100,
        },
        trace_content_det={
            "blk_0195f3a00000700583f32679aa514fcb": {
                "raw_score": 2.5,
                "justification": "Authenticity evaluation",
                "level_breakdown": {"1.0": {"hits": 1, "total": 3}, "2.0": {"hits": 2, "total": 3}},
            },
            "_step_metadata": {
                "execution_id": "exec_0195f3a0000070018234567812345678",
                "workflow_id": "wf_0195f3a0000070018234567812345678",
                "step_id": "sr_det_step12345678",
                "initiator_id": "system",
                "timestamp_isot": "2026-08-06T00:00:00Z",
                "unix_time": 1700000000,
                "v2_engine": True,
                "task_blueprint": "sp_det_step",
            },
        },
    )

    with patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo):
        await generate_profile_synthesis_and_pdf_task(
            execution_id="exec_0195f3a0000070018234567812345678",
            accept_language="en",
            profile_id="prof_0195f3a0000070018111111111111111",
            redis=None,
        )

    prof_synth = await _get_profile_syntheses(mock_repo)
    assert prof_synth is not None
    cache = prof_synth["prof_0195f3a0000070018111111111111111"]
    assert cache.extension_metrics is not None
    metrics = cache.extension_metrics
    assert metrics.authenticity_score == 2.5
    assert metrics.performative_phrases_count == 2.0
    assert metrics.total_word_count == 100
    assert metrics.jargon_density == 2.0


@pytest.mark.asyncio
async def test_worker_synthesis_extracts_metrics_for_coach_goodhart_step() -> None:
    """Verify extracting extension metrics from Coach/Goodhart evaluation step."""
    get_settings().use_mock_llm = True
    mock_repo = InMemoryUnifiedWorkflowRepository()

    await _setup_mock_repo_for_metrics(
        mock_repo,
        trace_content_ling={
            "performative_patterns": [
                {"pattern_id": "1", "detected_phrase": "phrase", "category": "cat"},
            ],
            "total_word_count": 200,
        },
        trace_content_det={
            "blk_0195f3a00000700583f32679aa514fcb": {
                "raw_score": 1.5,
                "justification": "Coach Goodhart evaluation",
                "level_breakdown": {"1.0": {"hits": 1, "total": 3}, "2.0": {"hits": 2, "total": 3}},
            },
            "_step_metadata": {
                "execution_id": "exec_0195f3a0000070018234567812345678",
                "workflow_id": "wf_0195f3a0000070098d68c573802341db",
                "step_id": "sr_0195f3a0000070008228db320e8f41bb",
                "initiator_id": "system",
                "timestamp_isot": "2026-08-06T00:00:00Z",
                "unix_time": 1700000000,
                "v2_engine": True,
                "task_blueprint": "sp_0195f3a00000700285664f44773a4354",
            },
        },
    )

    with patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo):
        await generate_profile_synthesis_and_pdf_task(
            execution_id="exec_0195f3a0000070018234567812345678",
            accept_language="en",
            profile_id="prof_0195f3a0000070018111111111111111",
            redis=None,
        )

    prof_synth = await _get_profile_syntheses(mock_repo)
    assert prof_synth is not None
    cache = prof_synth["prof_0195f3a0000070018111111111111111"]
    assert cache.extension_metrics is not None
    metrics = cache.extension_metrics
    assert metrics.authenticity_score == 1.5
    assert metrics.performative_phrases_count == 1.0
    assert metrics.total_word_count == 200


@pytest.mark.asyncio
async def test_worker_synthesis_missing_metrics_remains_none() -> None:
    """Verify synthesis leaves extension_metrics as None when metrics are absent from trace."""
    get_settings().use_mock_llm = True
    mock_repo = InMemoryUnifiedWorkflowRepository()

    await _setup_mock_repo_for_metrics(mock_repo, trace_content_ling=None, trace_content_det=None)

    with patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo):
        await generate_profile_synthesis_and_pdf_task(
            execution_id="exec_0195f3a0000070018234567812345678",
            accept_language="en",
            profile_id="prof_0195f3a0000070018111111111111111",
            redis=None,
        )

    prof_synth = await _get_profile_syntheses(mock_repo)
    assert prof_synth is not None
    assert prof_synth["prof_0195f3a0000070018111111111111111"].extension_metrics is None


@pytest.mark.asyncio
async def test_worker_synthesis_malformed_metrics_remains_none() -> None:
    """Verify synthesis leaves extension_metrics as None when detector score is None."""
    mock_repo = InMemoryUnifiedWorkflowRepository()

    await _setup_mock_repo_for_metrics(
        mock_repo,
        trace_content_ling={
            "performative_patterns": [{"pattern_id": "1", "detected_phrase": "one", "category": "cat"}]
        },
        trace_content_det={
            "blk_det12345678det1": {
                "raw_score": None,
                "justification": "Authenticity evaluation",
                "level_breakdown": {"1.0": {"hits": 1, "total": 3}, "2.0": {"hits": 2, "total": 3}},
            },
            "_step_metadata": {
                "execution_id": "exec_0195f3a0000070018234567812345678",
                "workflow_id": "wf_0195f3a0000070018234567812345678",
                "step_id": "sr_det_step12345678",
                "initiator_id": "system",
                "timestamp_isot": "2026-08-06T00:00:00Z",
                "unix_time": 1700000000,
                "v2_engine": True,
                "task_blueprint": "sp_det_step",
            },
        },
    )

    with patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo):
        await generate_profile_synthesis_and_pdf_task(
            execution_id="exec_0195f3a0000070018234567812345678",
            accept_language="en",
            profile_id="prof_0195f3a0000070018111111111111111",
            redis=None,
        )

    prof_synth = await _get_profile_syntheses(mock_repo)
    assert prof_synth is not None
    assert prof_synth["prof_0195f3a0000070018111111111111111"].extension_metrics is None


@pytest.mark.asyncio
async def test_worker_synthesis_metrics_no_step_metadata() -> None:
    """Verify synthesis leaves extension_metrics as None when step metadata is missing."""
    mock_repo = InMemoryUnifiedWorkflowRepository()

    await _setup_mock_repo_for_metrics(
        mock_repo,
        trace_content_ling={
            "performative_patterns": [{"pattern_id": "1", "detected_phrase": "one", "category": "cat"}]
        },
        trace_content_det={
            "blk_det12345678det1": {
                "raw_score": 2.5,
                "justification": "Authenticity evaluation",
                "level_breakdown": {"1.0": {"hits": 1, "total": 3}, "2.0": {"hits": 2, "total": 3}},
            },
        },
    )

    with patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo):
        await generate_profile_synthesis_and_pdf_task(
            execution_id="exec_0195f3a0000070018234567812345678",
            accept_language="en",
            profile_id="prof_0195f3a0000070018111111111111111",
            redis=None,
        )

    prof_synth = await _get_profile_syntheses(mock_repo)
    assert prof_synth is not None
    assert prof_synth["prof_0195f3a0000070018111111111111111"].extension_metrics is None


@pytest.mark.asyncio
async def test_worker_synthesis_metrics_no_task_blueprint_in_metadata() -> None:
    """Verify synthesis leaves extension_metrics as None when task_blueprint is absent."""
    mock_repo = InMemoryUnifiedWorkflowRepository()

    await _setup_mock_repo_for_metrics(
        mock_repo,
        trace_content_ling={
            "performative_patterns": [{"pattern_id": "1", "detected_phrase": "one", "category": "cat"}]
        },
        trace_content_det={
            "blk_det12345678det1": {
                "raw_score": 2.5,
                "justification": "Authenticity evaluation",
                "level_breakdown": {"1.0": {"hits": 1, "total": 3}, "2.0": {"hits": 2, "total": 3}},
            },
            "_step_metadata": {
                "execution_id": "exec_0195f3a0000070018234567812345678",
                "workflow_id": "wf_0195f3a0000070018234567812345678",
                "step_id": "sr_det_step12345678",
                "initiator_id": "system",
                "timestamp_isot": "2026-08-06T00:00:00Z",
                "unix_time": 1700000000,
                "v2_engine": True,
            },
        },
    )

    with patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo):
        await generate_profile_synthesis_and_pdf_task(
            execution_id="exec_0195f3a0000070018234567812345678",
            accept_language="en",
            profile_id="prof_0195f3a0000070018111111111111111",
            redis=None,
        )

    prof_synth = await _get_profile_syntheses(mock_repo)
    assert prof_synth is not None
    assert prof_synth["prof_0195f3a0000070018111111111111111"].extension_metrics is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("view_type", "directive_field", "directive_value", "expected_snippet", "should_execute_group"),
    [
        ("2d_compare", "matrix_2d_synthesis_directive", None, None, False),
        (
            "2d_compare",
            "matrix_2d_synthesis_directive",
            "CUSTOM 2D MANDATE:",
            "CUSTOM 2D MANDATE:",
            True,
        ),
        (
            "3d_matrix",
            "matrix_3d_synthesis_directive",
            "CUSTOM 3D MANDATE:",
            "CUSTOM 3D MANDATE:",
            True,
        ),
        (
            "1d_metrics",
            "matrix_1d_synthesis_directive",
            "CUSTOM 1D MANDATE:",
            "CUSTOM 1D MANDATE:",
            True,
        ),
        (
            "text_only",
            "matrix_text_synthesis_directive",
            "CUSTOM TEXT MANDATE:",
            "CUSTOM TEXT MANDATE:",
            True,
        ),
        (
            "2d_compare",
            "matrix_1d_synthesis_directive",
            "1D ONLY",
            None,
            False,
        ),
    ],
)
@patch("backend_v2.workers.synthesis_worker.LLMClient.from_tier")
async def test_worker_synthesis_matrix_layout_directives(
    mock_from_tier: AsyncMock,
    view_type: str,
    directive_field: str,
    directive_value: str | None,
    expected_snippet: str | None,
    should_execute_group: bool,
) -> None:
    """Verify matrix synthesis groups execute strictly based on profile directives matching view_type."""
    get_settings().use_mock_llm = True

    mock_repo = InMemoryUnifiedWorkflowRepository()
    await _setup_mock_repo_for_metrics(mock_repo, trace_content_ling=None, trace_content_det=None)

    target_blocks_map = {
        "1d_metrics": ["blk_1"],
        "2d_compare": ["blk_1", "blk_2"],
        "3d_matrix": ["blk_1", "blk_2", "blk_3"],
        "text_only": ["blk_1"],
    }
    prof_obj: OutputProfile = _DeterministicOutputProfileFactory.build(
        id="prof_0195f3a0000070018111111111111111",
        slug="prof_test",
        name=I18nText(translations={"en": "Test Profile"}),
        workflow_id="wf_0195f3a0000070018234567812345678",
        display_scale=DisplayScale.ORIGINAL,
        synthesis_length_constraint=1000,
        tone_instruction="Professional",
        matrix_synthesis_groups=[
            _MatrixSynthesisGroupFactory.build(
                id="grp_0195f3a0000070018234567890123456",
                title=I18nText(translations={"fi": "Matriisinäkymä", "en": "Matrix View"}),
                target_blocks=target_blocks_map[view_type] if view_type in target_blocks_map else ["blk_1"],
                view_type=view_type,
            )
        ],
        target_block_order=[TargetBlockType.MATRIX_GRAPHS_BLOCK],
    )
    if directive_value is not None:
        prof_obj = prof_obj.model_copy(update={directive_field: directive_value})

    mock_repo.set_output_profiles([prof_obj])

    mock_client = AsyncMock()

    async def _mock_run_structured_task(*args: Any, **kwargs: Any) -> tuple[Any, TokenUsage]:
        resp_model = kwargs["response_model"] if "response_model" in kwargs else None
        usage = TokenUsage(prompt_tokens=50, completion_tokens=50, total_tokens=100, cost_usd=0.001)
        if resp_model is ExecutiveSummarySectionResult:
            return (
                ExecutiveSummarySectionResult(
                    user_role=RoleClassification.ARCHITECT,
                    user_role_justification="Target executive persona",
                    cited_sources=[],
                    executive_summary=[ParagraphBlock(text="Executive Summary", exact_quotes=[], citations=[])],
                ),
                usage,
            )
        if resp_model is MatrixSectionSynthesesResult:
            return (
                MatrixSectionSynthesesResult(
                    sections=[
                        SynthesisSectionDTO(
                            layout_id="grp_0195f3a0000070018234567890123456",
                            content_blocks=[ParagraphBlock(text="Section Content", exact_quotes=[], citations=[])],
                        )
                    ]
                ),
                usage,
            )
        if resp_model is XaiHighlightsResult:
            return (
                XaiHighlightsResult(
                    xai_highlights=[],
                ),
                usage,
            )
        return (None, usage)

    mock_client.run_structured_task.side_effect = _mock_run_structured_task
    mock_from_tier.return_value = mock_client

    with patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo):
        if not should_execute_group:
            await generate_profile_synthesis_and_pdf_task(
                execution_id="exec_0195f3a0000070018234567812345678",
                accept_language="fi",
                profile_id="prof_0195f3a0000070018111111111111111",
                redis=None,
            )
            group_calls = [
                call
                for call in mock_client.run_structured_task.call_args_list
                if "response_model" in call.kwargs and call.kwargs["response_model"] is MatrixSectionSynthesesResult
            ]
            assert len(group_calls) == 0
            return

        await generate_profile_synthesis_and_pdf_task(
            execution_id="exec_0195f3a0000070018234567812345678",
            accept_language="fi",
            profile_id="prof_0195f3a0000070018111111111111111",
            redis=None,
        )

    all_user_content = _extract_captured_messages(mock_client.run_structured_task.call_args_list)

    if expected_snippet is not None:
        assert expected_snippet in all_user_content


@pytest.mark.asyncio
@patch("backend_v2.workers.synthesis_worker.LLMClient.from_tier")
async def test_worker_synthesis_disabled_layout_omits_section_instruction(
    mock_from_tier: AsyncMock,
) -> None:
    """Verify empty matrix_synthesis_groups omits group section synthesis instructions."""
    get_settings().use_mock_llm = True

    mock_repo = InMemoryUnifiedWorkflowRepository()
    await _setup_mock_repo_for_metrics(mock_repo, trace_content_ling=None, trace_content_det=None)

    disabled_prof = _DeterministicOutputProfileFactory.build(
        id="prof_0195f3a0000070018111111111111111",
        slug="prof_disabled",
        name=I18nText(translations={"en": "Disabled Profile"}),
        workflow_id="wf_0195f3a0000070018234567812345678",
        display_scale=DisplayScale.ORIGINAL,
        synthesis_length_constraint=1000,
        tone_instruction="Professional",
        executive_summary_directive="EXECUTIVE SUMMARY DIRECTIVE",
        matrix_synthesis_groups=[],
        target_block_order=[TargetBlockType.EXECUTIVE_SUMMARY_BLOCK],
    )
    mock_repo.set_output_profiles([disabled_prof])

    mock_client = AsyncMock()

    async def _mock_run_structured_task_disabled(*args: Any, **kwargs: Any) -> tuple[Any, TokenUsage]:
        resp_model = kwargs["response_model"] if "response_model" in kwargs else None
        usage = TokenUsage(prompt_tokens=50, completion_tokens=50, total_tokens=100, cost_usd=0.001)
        if resp_model is ExecutiveSummarySectionResult:
            return (
                ExecutiveSummarySectionResult(
                    user_role=RoleClassification.ARCHITECT,
                    user_role_justification="Target executive persona",
                    cited_sources=[],
                    executive_summary=[ParagraphBlock(text="Executive Summary", exact_quotes=[], citations=[])],
                ),
                usage,
            )
        if resp_model is MatrixSectionSynthesesResult:
            return (MatrixSectionSynthesesResult(sections=[]), usage)
        if resp_model is XaiHighlightsResult:
            return (XaiHighlightsResult(xai_highlights=[]), usage)
        return (None, usage)

    mock_client.run_structured_task.side_effect = _mock_run_structured_task_disabled
    mock_from_tier.return_value = mock_client

    with patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo):
        await generate_profile_synthesis_and_pdf_task(
            execution_id="exec_0195f3a0000070018234567812345678",
            accept_language="fi",
            profile_id="prof_0195f3a0000070018111111111111111",
            redis=None,
        )

    assert mock_client.run_structured_task.called
    all_user_content = _extract_captured_messages(mock_client.run_structured_task.call_args_list)
    assert "2D COMPARISON SYNTHESIS MANDATE:" not in all_user_content
    assert "NO IN-TEXT CITATIONS MANDATE:" in all_user_content
    assert "HARVARD CITATION STANDARD MANDATE:" not in all_user_content


@pytest.mark.asyncio
@patch("backend_v2.workers.synthesis_worker.LLMClient.from_tier")
async def test_worker_synthesis_executive_summary_instruction_and_cache(
    mock_from_tier: AsyncMock,
) -> None:
    """Verify executive summary instruction is generated and synthesized blocks are cached."""
    get_settings().use_mock_llm = True

    mock_repo = InMemoryUnifiedWorkflowRepository()
    await _setup_mock_repo_for_metrics(mock_repo, trace_content_ling=None, trace_content_det=None)

    exec_prof = _DeterministicOutputProfileFactory.build(
        id="prof_0195f3a0000070018111111111111111",
        slug="prof_exec_summary",
        name=I18nText(translations={"en": "Exec Profile"}),
        workflow_id="wf_0195f3a0000070018234567812345678",
        display_scale=DisplayScale.ORIGINAL,
        synthesis_length_constraint=1000,
        tone_instruction="Professional",
        executive_summary_directive="EXECUTIVE SUMMARY SYNTHESIS MANDATE:",
        matrix_synthesis_groups=[],
        target_block_order=[
            TargetBlockType.EXECUTIVE_SUMMARY_BLOCK,
            TargetBlockType.PRINTABLE_SOURCES_BLOCK,
        ],
    )
    mock_repo.set_output_profiles([exec_prof])

    mock_client = AsyncMock()

    async def _mock_run_structured_task_exec(*args: Any, **kwargs: Any) -> tuple[Any, TokenUsage]:
        resp_model = kwargs["response_model"] if "response_model" in kwargs else None
        usage = TokenUsage(prompt_tokens=50, completion_tokens=50, total_tokens=100, cost_usd=0.001)
        if resp_model is ExecutiveSummarySectionResult:
            return (
                ExecutiveSummarySectionResult(
                    user_role=RoleClassification.ARCHITECT,
                    user_role_justification="Demonstrates high strategic maturity",
                    cited_sources=[],
                    executive_summary=[
                        ParagraphBlock(text="Executive summary narrative paragraph 1.", exact_quotes=[], citations=[])
                    ],
                ),
                usage,
            )
        if resp_model is MatrixSectionSynthesesResult:
            return (MatrixSectionSynthesesResult(sections=[]), usage)
        if resp_model is XaiHighlightsResult:
            return (XaiHighlightsResult(xai_highlights=[]), usage)
        return (None, usage)

    mock_client.run_structured_task.side_effect = _mock_run_structured_task_exec
    mock_from_tier.return_value = mock_client

    with patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo):
        await generate_profile_synthesis_and_pdf_task(
            execution_id="exec_0195f3a0000070018234567812345678",
            accept_language="fi",
            profile_id="prof_0195f3a0000070018111111111111111",
            redis=None,
        )

    assert mock_client.run_structured_task.called
    all_user_content = _extract_captured_messages(mock_client.run_structured_task.call_args_list)
    assert '<section_instruction id="executive_summary_block" title="Executive Summary">' in all_user_content
    assert "EXECUTIVE SUMMARY SYNTHESIS MANDATE:" in all_user_content
    assert "HARVARD CITATION STANDARD MANDATE:" in all_user_content
    assert "NO IN-TEXT CITATIONS MANDATE:" not in all_user_content

    prof_synth = await _get_profile_syntheses(mock_repo)
    assert prof_synth is not None
    sec_synth = prof_synth["prof_0195f3a0000070018111111111111111"].section_syntheses
    assert "executive_summary_block" in sec_synth
    assert len(sec_synth["executive_summary_block"]) == 1
    block = sec_synth["executive_summary_block"][0]
    assert isinstance(block, ParagraphBlock)
    assert block.text == "Executive summary narrative paragraph 1."


@pytest.mark.asyncio
@patch("backend_v2.workers.synthesis_worker.LLMClient.from_tier")
async def test_worker_synthesis_multi_section_aggregation(
    mock_from_tier: AsyncMock,
) -> None:
    """Verify multiple SynthesisSectionDTO items for a matrix group aggregate into section_syntheses."""
    get_settings().use_mock_llm = True

    mock_repo = InMemoryUnifiedWorkflowRepository()
    await _setup_mock_repo_for_metrics(mock_repo, trace_content_ling=None, trace_content_det=None)

    multi_prof = _DeterministicOutputProfileFactory.build(
        id="prof_0195f3a0000070018111111111111111",
        slug="prof_multi_sec",
        name=I18nText(translations={"en": "Multi Section Profile"}),
        workflow_id="wf_0195f3a0000070018234567812345678",
        display_scale=DisplayScale.ORIGINAL,
        synthesis_length_constraint=1000,
        tone_instruction="Professional",
        matrix_1d_synthesis_directive="CUSTOM CAUSALITY DIRECTIVE",
        matrix_synthesis_groups=[
            _MatrixSynthesisGroupFactory.build(
                id="grp_0195f3a00000700c85804a9143c34cb1",
                title=I18nText(translations={"fi": "Kausaalisuus", "en": "Causality"}),
                target_blocks=["blk_1"],
                view_type="1d_metrics",
            )
        ],
        target_block_order=[TargetBlockType.MATRIX_GRAPHS_BLOCK],
    )
    mock_repo.set_output_profiles([multi_prof])

    mock_client = AsyncMock()

    async def _mock_run_structured_task_multi(*args: Any, **kwargs: Any) -> tuple[Any, TokenUsage]:
        resp_model = kwargs["response_model"] if "response_model" in kwargs else None
        usage = TokenUsage(prompt_tokens=50, completion_tokens=50, total_tokens=100, cost_usd=0.001)
        if resp_model is ExecutiveSummarySectionResult:
            return (
                ExecutiveSummarySectionResult(
                    user_role=RoleClassification.ARCHITECT,
                    user_role_justification="Target executive persona",
                    cited_sources=[],
                    executive_summary=[ParagraphBlock(text="Executive Summary", exact_quotes=[], citations=[])],
                ),
                usage,
            )
        if resp_model is MatrixSectionSynthesesResult:
            return (
                MatrixSectionSynthesesResult(
                    sections=[
                        SynthesisSectionDTO(
                            layout_id="sub_paragraph_1",
                            content_blocks=[ParagraphBlock(text="Paragraph 1 text", exact_quotes=[], citations=[])],
                        ),
                        SynthesisSectionDTO(
                            layout_id="sub_paragraph_2",
                            content_blocks=[ParagraphBlock(text="Paragraph 2 text", exact_quotes=[], citations=[])],
                        ),
                    ]
                ),
                usage,
            )
        if resp_model is XaiHighlightsResult:
            return (XaiHighlightsResult(xai_highlights=[]), usage)
        return (None, usage)

    mock_client.run_structured_task.side_effect = _mock_run_structured_task_multi
    mock_from_tier.return_value = mock_client

    with patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo):
        await generate_profile_synthesis_and_pdf_task(
            execution_id="exec_0195f3a0000070018234567812345678",
            accept_language="fi",
            profile_id="prof_0195f3a0000070018111111111111111",
            redis=None,
        )

    prof_synth = await _get_profile_syntheses(mock_repo)
    assert prof_synth is not None
    sec_synth = prof_synth["prof_0195f3a0000070018111111111111111"].section_syntheses
    assert "grp_0195f3a00000700c85804a9143c34cb1" in sec_synth
    assert len(sec_synth["grp_0195f3a00000700c85804a9143c34cb1"]) == 2
    b1 = sec_synth["grp_0195f3a00000700c85804a9143c34cb1"][0]
    b2 = sec_synth["grp_0195f3a00000700c85804a9143c34cb1"][1]
    assert isinstance(b1, ParagraphBlock)
    assert isinstance(b2, ParagraphBlock)
    assert b1.text == "Paragraph 1 text"
    assert b2.text == "Paragraph 2 text"


@pytest.mark.asyncio
@patch("backend_v2.workers.synthesis_worker.LLMClient.from_tier")
async def test_worker_synthesis_empty_sections_not_set_in_cache(
    mock_from_tier: AsyncMock,
) -> None:
    """Verify empty matrix sections omit setting an empty group key in section_syntheses."""
    get_settings().use_mock_llm = True

    mock_repo = InMemoryUnifiedWorkflowRepository()
    await _setup_mock_repo_for_metrics(mock_repo, trace_content_ling=None, trace_content_det=None)

    empty_sec_prof = _DeterministicOutputProfileFactory.build(
        id="prof_0195f3a0000070018111111111111111",
        slug="prof_empty_sec",
        name=I18nText(translations={"en": "Empty Section Profile"}),
        workflow_id="wf_0195f3a0000070018234567812345678",
        display_scale=DisplayScale.ORIGINAL,
        synthesis_length_constraint=1000,
        tone_instruction="Professional",
        matrix_1d_synthesis_directive="1D DIRECTIVE",
        matrix_synthesis_groups=[
            MatrixSynthesisGroup(
                id="grp_0195f3a0000070008000000000000000",
                title=I18nText(translations={"fi": "Kausaalisuus", "en": "Causality"}),
                target_blocks=["blk_1"],
            )
        ],
        target_block_order=[TargetBlockType.MATRIX_GRAPHS_BLOCK],
    )
    mock_repo.set_output_profiles([empty_sec_prof])

    mock_client = AsyncMock()

    async def _mock_run_structured_task_empty(*args: Any, **kwargs: Any) -> tuple[Any, TokenUsage]:
        resp_model = kwargs["response_model"] if "response_model" in kwargs else None
        usage = TokenUsage(prompt_tokens=50, completion_tokens=50, total_tokens=100, cost_usd=0.001)
        if resp_model is ExecutiveSummarySectionResult:
            return (
                ExecutiveSummarySectionResult(
                    user_role=RoleClassification.ARCHITECT,
                    user_role_justification="Target executive persona",
                    cited_sources=[],
                    executive_summary=[],
                ),
                usage,
            )
        if resp_model is MatrixSectionSynthesesResult:
            return (
                MatrixSectionSynthesesResult(sections=[]),
                usage,
            )
        if resp_model is XaiHighlightsResult:
            return (XaiHighlightsResult(xai_highlights=[]), usage)
        return (None, usage)

    mock_client.run_structured_task.side_effect = _mock_run_structured_task_empty
    mock_from_tier.return_value = mock_client

    with patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo):
        await generate_profile_synthesis_and_pdf_task(
            execution_id="exec_0195f3a0000070018234567812345678",
            accept_language="fi",
            profile_id="prof_0195f3a0000070018111111111111111",
            redis=None,
        )

    prof_synth = await _get_profile_syntheses(mock_repo)
    assert prof_synth is not None
    sec_synth = prof_synth["prof_0195f3a0000070018111111111111111"].section_syntheses
    assert "grp_0195f3a0000070008000000000000000" not in sec_synth


@pytest.mark.asyncio
@patch("backend_v2.workers.synthesis_worker.LLMClient.from_tier")
async def test_worker_synthesis_custom_directives_resolution(
    mock_from_tier: AsyncMock,
) -> None:
    """Verify custom row, XAI, and variance directives configured on OutputProfile are injected into prompts."""
    get_settings().use_mock_llm = True

    mock_repo = InMemoryUnifiedWorkflowRepository()
    await _setup_mock_repo_for_metrics(
        mock_repo,
        trace_content_ling={
            "performative_patterns": [{"pattern_id": "1", "detected_phrase": "test phrase", "category": "cat"}]
        },
        trace_content_det={
            "blk_0195f3a00000700583f32679aa514fcb": {
                "raw_score": 3.0,
                "justification": "Authenticity evaluation",
                "level_breakdown": {},
            },
            "_step_metadata": {
                "execution_id": "exec_0195f3a0000070018234567812345678",
                "workflow_id": "wf_0195f3a0000070018234567812345678",
                "step_id": "sr_det_step12345678",
                "initiator_id": "system",
                "timestamp_isot": "2026-08-06T00:00:00Z",
                "unix_time": 1700000000,
                "v2_engine": True,
                "task_blueprint": "sp_det_step",
            },
        },
    )

    custom_prof = _DeterministicOutputProfileFactory.build(
        id="prof_0195f3a0000070018111111111111111",
        slug="prof_custom_directives",
        name=I18nText(translations={"en": "Custom Directives Profile"}),
        workflow_id="wf_0195f3a0000070018234567812345678",
        display_scale=DisplayScale.ORIGINAL,
        synthesis_length_constraint=1000,
        tone_instruction="Professional",
        row_explanation_directive="CUSTOM ROW EXPLANATION DIRECTIVE",
        xai_synthesis_directive="CUSTOM XAI SYNTHESIS DIRECTIVE",
        variance_synthesis_directive="CUSTOM VARIANCE DIRECTIVE",
        visible_workflow_extensions=[XaiExtensionType.VARIANCE_VALIDATION],
        variance_target_block="blk_0195f3a00000700583f32679aa514fcb",
        matrix_visible_columns=["label", "row_explanation"],
        matrix_synthesis_groups=[],
        target_block_order=[
            TargetBlockType.VARIANCE_VALIDATION_BLOCK,
            TargetBlockType.MATRIX_SUMMARY_TABLE_BLOCK,
        ],
    )
    mock_repo.set_output_profiles([custom_prof])

    mock_client = AsyncMock()

    async def _mock_run_structured_task_custom(*args: Any, **kwargs: Any) -> tuple[Any, TokenUsage]:
        resp_model = kwargs["response_model"] if "response_model" in kwargs else None
        usage = TokenUsage(prompt_tokens=50, completion_tokens=50, total_tokens=100, cost_usd=0.001)
        if resp_model is ExecutiveSummarySectionResult:
            return (
                ExecutiveSummarySectionResult(
                    user_role=RoleClassification.ARCHITECT,
                    user_role_justification="Target executive persona",
                    cited_sources=[],
                    executive_summary=[],
                ),
                usage,
            )
        if resp_model is MatrixSectionSynthesesResult:
            return (MatrixSectionSynthesesResult(sections=[]), usage)
        if resp_model is XaiHighlightsResult:
            return (XaiHighlightsResult(xai_highlights=[]), usage)
        if resp_model is VarianceExplanationResult:
            return (VarianceExplanationResult(explanation="Variance explanation result"), usage)
        if resp_model is MatrixExplanationsResult:
            return (MatrixExplanationsResult(explanations=[]), usage)
        return (None, usage)

    mock_client.run_structured_task.side_effect = _mock_run_structured_task_custom
    mock_from_tier.return_value = mock_client

    with patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo):
        await generate_profile_synthesis_and_pdf_task(
            execution_id="exec_0195f3a0000070018234567812345678",
            accept_language="fi",
            profile_id="prof_0195f3a0000070018111111111111111",
            redis=None,
        )

    all_user_content = _extract_captured_messages(mock_client.run_structured_task.call_args_list)

    assert "CUSTOM XAI SYNTHESIS DIRECTIVE" in all_user_content
    assert "CUSTOM VARIANCE DIRECTIVE" in all_user_content


@pytest.mark.asyncio
async def test_worker_synthesis_missing_variance_target_block_raises_configuration_error() -> None:
    """Verify missing variance_target_block when variance is active raises Fail-Fast AppException."""
    get_settings().use_mock_llm = True
    mock_repo = InMemoryUnifiedWorkflowRepository()

    await _setup_mock_repo_for_metrics(
        mock_repo,
        trace_content_ling={"performative_patterns": [], "total_word_count": 100},
        trace_content_det={"blk_0195f3a00000700583f32679aa514fcb": {"raw_score": 2.5, "justification": "test"}},
    )

    prof_missing = _DeterministicOutputProfileFactory.build(
        id="prof_0195f3a0000070018111111111111111",
        slug="prof_missing_target",
        name=I18nText(translations={"en": "Missing Target"}),
        workflow_id="wf_0195f3a0000070018234567812345678",
        display_scale=DisplayScale.ORIGINAL,
        target_block_order=[TargetBlockType.VARIANCE_VALIDATION_BLOCK],
        variance_target_block="blk_0195f3a00000700583f32679aa514fcb",
        matrix_synthesis_groups=[],
    ).model_copy(
        update={
            "visible_workflow_extensions": [XaiExtensionType.VARIANCE_VALIDATION],
            "variance_target_block": None,
        }
    )
    mock_repo.set_output_profiles([prof_missing])

    with patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo):
        with pytest.raises(AppException) as exc_info:
            await generate_profile_synthesis_and_pdf_task(
                execution_id="exec_0195f3a0000070018234567812345678",
                accept_language="en",
                profile_id="prof_0195f3a0000070018111111111111111",
                redis=None,
            )

    assert exc_info.value.status_code in (400, 500)
    assert "variance_target_block" in str(exc_info.value)


@pytest.mark.asyncio
async def test_worker_synthesis_unevaluated_target_block_handled_gracefully() -> None:
    """Verify synthesis completes cleanly without variance metrics if target block was not evaluated."""
    get_settings().use_mock_llm = True
    mock_repo = InMemoryUnifiedWorkflowRepository()

    await _setup_mock_repo_for_metrics(
        mock_repo,
        trace_content_ling={"performative_patterns": [], "total_word_count": 100},
        trace_content_det={
            "blk_unrelated99999999": {
                "raw_score": 1.0,
                "justification": "Other block",
            }
        },
    )

    with patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo):
        await generate_profile_synthesis_and_pdf_task(
            execution_id="exec_0195f3a0000070018234567812345678",
            accept_language="en",
            profile_id="prof_0195f3a0000070018111111111111111",
            redis=None,
        )

    prof_synth = await _get_profile_syntheses(mock_repo)
    assert prof_synth is not None
    assert prof_synth["prof_0195f3a0000070018111111111111111"].extension_metrics is None


@pytest.mark.asyncio
async def test_worker_synthesis_extracts_user_role_from_target_block_deterministically() -> None:
    """Verify user_role is extracted deterministically from trace when user_role_target_block is configured."""
    get_settings().use_mock_llm = True
    mock_repo = InMemoryUnifiedWorkflowRepository()

    await _setup_mock_repo_for_metrics(
        mock_repo,
        trace_content_ling={"performative_patterns": [], "total_word_count": 100},
        trace_content_det={
            "blk_0195f3a00000700583f32679aa514fcb": {
                "raw_score": 4.0,
                "justification": "Evaluated Goodhart Driver Score",
            }
        },
    )

    role_prof = _DeterministicOutputProfileFactory.build(
        id="prof_0195f3a0000070018111111111111111",
        slug="prof_role_target",
        name=I18nText(translations={"en": "Role Target Profile"}),
        workflow_id="wf_0195f3a0000070018234567812345678",
        display_scale=DisplayScale.ORIGINAL,
        visible_workflow_extensions=[XaiExtensionType.VARIANCE_VALIDATION],
        variance_target_block="blk_0195f3a00000700583f32679aa514fcb",
        user_role_target_block="blk_0195f3a00000700583f32679aa514fcb",
        target_block_order=[TargetBlockType.VARIANCE_VALIDATION_BLOCK],
        matrix_synthesis_groups=[],
    )
    mock_repo.set_output_profiles([role_prof])

    with patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo):
        await generate_profile_synthesis_and_pdf_task(
            execution_id="exec_0195f3a0000070018234567812345678",
            accept_language="en",
            profile_id="prof_0195f3a0000070018111111111111111",
            redis=None,
        )

    prof_synth = await _get_profile_syntheses(mock_repo)
    assert prof_synth is not None
    cache_item = prof_synth["prof_0195f3a0000070018111111111111111"]
    assert cache_item.user_role == RoleClassification.DRIVER.value
    assert "blk_0195f3a00000700583f32679aa514fcb" in str(cache_item.user_role_justification)
    assert "score 4.0" in str(cache_item.user_role_justification)
