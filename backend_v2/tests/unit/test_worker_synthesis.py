"""Unit tests for worker background synthesis tasks and trace extraction."""

from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from pydantic import JsonValue

from backend_v2.exceptions import AppException
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.synthesis import RenderedSynthesisCache
from backend_v2.models.domain.system_config import ChatMessageDTO, SystemConfigModelRegistry
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.synthesis import (
    ExecutiveSummarySectionResult,
    MatrixExplanationsResult,
    MatrixSectionSynthesesResult,
    SynthesisSectionDTO,
    XaiHighlightsResult,
)
from backend_v2.models.enums import ExecutionStatus, RoleClassification
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.llm import LLMMessageDTO
from backend_v2.models.state import TraceEvent
from backend_v2.models.view.sdui import ParagraphBlock
from backend_v2.settings import get_settings
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository
from backend_v2.workers import VarianceExplanationResult, generate_profile_synthesis_and_pdf_task


async def _get_profile_syntheses(
    repo: InMemoryUnifiedWorkflowRepository, exec_id: str = "exec_1234567812345678"
) -> dict[str, RenderedSynthesisCache] | None:
    rec = await repo.get_execution(exec_id)
    if rec and rec.profile_syntheses:
        return rec.profile_syntheses
    return None


def _get_base_model_registry() -> SystemConfigModelRegistry:
    profile = {
        "provider": "mock_llm_99",
        "model_name": "gemini-2.5-pro",
        "temperature": 0.0,
        "max_tokens": 1024,
        "is_active": True,
        "tpm_limit": 100000,
        "rpm_limit": 1000,
    }
    return SystemConfigModelRegistry.model_validate(
        {
            "id": "sys_1111222233334444",
            "name": "Default Test Registry",
            "type": "model_registry",
            "slug": "model_registry",
            "default_provider": "vertex_ai",
            "tier_definitions": {
                "fast": profile,
                "balanced": profile,
                "deep": profile,
                "reasoning": profile,
            },
        }
    )


@pytest.mark.asyncio
@patch("backend_v2.workers.synthesis_worker.get_driver", new_callable=AsyncMock)
async def test_worker_extracts_synthesis_from_trace(_mock_driver: AsyncMock) -> None:
    """Test that the worker background task extracts synthesis payload from the DAG execution trace."""
    get_settings().use_mock_llm = True

    mock_repo = InMemoryUnifiedWorkflowRepository()

    mock_execution = ExecutionRecord(
        id="exec_1234567812345678",
        workflow_id="wf_1234567812345678",
        output_profile_id="prof_1111111111111111",
        status=ExecutionStatus.PASSED,
        target_locale="fi",
        metadata=ExecutionMetadata(),
        progress=None,
        status_message=None,
        execution_trace=[
            TraceEvent(
                v=1,
                timestamp=datetime.now(timezone.utc),
                event_type="output",
                step_name="sr_1234567812345678",
                content={"blk_synth12345678": {"synthesized_markdown": "Test MD"}},
            )
        ],
    )
    await mock_repo.save_execution(mock_execution)

    wf_dict = {
        "id": "wf_1234567812345678",
        "slug": "test_workflow",
        "name": {"translations": {"en": "Test", "fi": "Test"}},
        "description": {"translations": {"en": "Desc", "fi": "Desc"}},
        "status": "draft",
        "historical_context_mode": "DISABLED",
        "version": 1,
        "default_profile_id": "prof_1111111111111111",
        "model_registry_id": "sys_1111222233334444",
        "expected_inputs": [],
        "steps": [{"id": "sr_1234567812345678", "task_blueprint": "sp_1234567812345678"}],
    }
    await mock_repo.save_workflow(Workflow.model_validate(wf_dict, strict=False))

    mock_repo.seed_raw_step(
        "sp_1234567812345678",
        {
            "id": "sp_1234567812345678",
            "slug": "synthesis_step",
            "name": {"translations": {"en": "Synth"}},
            "cognitive_tier": "fast",
            "type": "logic",
            "hook": "text_consolidation_hook",
        },
    )

    mock_repo.set_model_registry(_get_base_model_registry(), "sys_1111222233334444")

    pb_1 = {
        "id": "pb_1111111111111111",
        "slug": "system_prompt",
        "type": "instruction",
        "label": {"translations": {"en": "System"}},
        "description": {"translations": {"en": "System prompt"}},
        "category_id": "system_rule",
    }
    pb_2 = {
        "id": "pb_2222222222222222",
        "slug": "synthesis_prompt",
        "type": "instruction",
        "label": {"translations": {"en": "Synth System"}},
        "description": {"translations": {"en": "System prompt for synthesis"}},
        "instruction_text": "You are an AI.",
        "category_id": "system_rule",
    }
    mock_repo.set_prompt_blocks([pb_1, pb_2])

    output_prof = {
        "slug": "test_slug",
        "workflow_id": "wf_1234567812345678",
        "name": {"translations": {"en": "Test", "fi": "Test"}},
        "id": "prof_1111111111111111",
        "max_extension_items": 3,
        "synthesis_length_constraint": 1000,
        "tone_instruction": "Professional",
        "matrix_1d_synthesis_directive": "1D DIRECTIVE",
        "matrix_synthesis_groups": [
            {
                "id": "grp_1111111111111111",
                "title": {"translations": {"en": "Group 1", "fi": "Ryhmä 1"}},
                "target_blocks": ["blk_1"],
                "view_type": "1d_metrics",
            }
        ],
        "target_block_order": ["matrix_graphs_block"],
        "display_scale": "original",
    }
    mock_repo.set_output_profiles([output_prof])

    with patch("backend_v2.workers.synthesis_worker.UnifiedWorkflowRepository", return_value=mock_repo):
        await generate_profile_synthesis_and_pdf_task(
            execution_id="exec_1234567812345678", accept_language="en", profile_id="prof_1111111111111111", redis=None
        )

    prof_synth = await _get_profile_syntheses(mock_repo)
    assert prof_synth is not None, "Execution record was not updated with profile_syntheses"
    assert type(prof_synth["prof_1111111111111111"].section_syntheses) is dict


async def _setup_mock_repo_for_metrics(
    mock_repo: InMemoryUnifiedWorkflowRepository,
    trace_content_ling: Mapping[str, JsonValue] | None,
    trace_content_det: Mapping[str, JsonValue] | None,
) -> None:
    trace_events = []
    if trace_content_ling is not None:
        trace_events.append(
            TraceEvent(
                v=1,
                timestamp=datetime.now(timezone.utc),
                event_type="decision",
                step_name="ling",
                content={"step_linguistics": trace_content_ling},
            )
        )
    if trace_content_det is not None:
        trace_events.append(
            TraceEvent(
                v=1,
                timestamp=datetime.now(timezone.utc),
                event_type="output",
                step_name="sr_det_step12345678",
                content=trace_content_det,
            )
        )

    mock_execution = ExecutionRecord(
        id="exec_1234567812345678",
        workflow_id="wf_1234567812345678",
        output_profile_id="prof_1111111111111111",
        status=ExecutionStatus.PASSED,
        target_locale="fi",
        metadata=ExecutionMetadata(),
        progress=None,
        status_message=None,
        execution_trace=trace_events,
        context_variables={},
    )
    await mock_repo.save_execution(mock_execution)

    wf_dict = {
        "id": "wf_1234567812345678",
        "slug": "test_workflow",
        "name": {"translations": {"en": "Test", "fi": "Test"}},
        "description": {"translations": {"en": "Desc", "fi": "Desc"}},
        "status": "draft",
        "historical_context_mode": "DISABLED",
        "version": 1,
        "default_profile_id": "prof_1111111111111111",
        "model_registry_id": "sys_1111222233334444",
        "expected_inputs": [],
        "steps": [],
    }
    await mock_repo.save_workflow(Workflow.model_validate(wf_dict, strict=False))

    mock_repo.set_model_registry(_get_base_model_registry(), "sys_1111222233334444")

    pb_synth = {
        "id": "pb_2222222222222222",
        "slug": "synthesis_prompt",
        "type": "instruction",
        "label": {"translations": {"en": "Synth System"}},
        "description": {"translations": {"en": "System prompt for synthesis"}},
        "instruction_text": "You are an AI.",
        "category_id": "system_rule",
    }
    mock_repo.set_prompt_blocks([pb_synth])

    default_prof = {
        "id": "prof_1111111111111111",
        "slug": "prof",
        "name": {"translations": {"en": "test"}},
        "workflow_id": "wf_1234567812345678",
        "display_scale": "original",
        "tone_instruction": "Professional",
        "xai_synthesis_directive": "XAI DIRECTIVE",
        "variance_synthesis_directive": "VARIANCE DIRECTIVE",
        "max_extension_items": 3,
        "visible_workflow_extensions": ["variance_validation"],
        "variance_target_block": "blk_53f32679aa514fcb",
        "matrix_synthesis_groups": [],
        "target_block_order": [],
    }
    mock_repo.set_output_profiles([default_prof])


@pytest.mark.asyncio
@patch("backend_v2.workers.synthesis_worker.get_driver", new_callable=AsyncMock)
async def test_worker_synthesis_extracts_metrics_from_trace(
    _mock_driver: AsyncMock,
) -> None:
    """Test extracting extension metrics from execution trace during synthesis."""
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
            "blk_53f32679aa514fcb": {
                "raw_score": 2.5,
                "justification": "Authenticity evaluation",
                "level_breakdown": {"1.0": {"hits": 1, "total": 3}, "2.0": {"hits": 2, "total": 3}},
            },
            "_step_metadata": {
                "execution_id": "exec_1234567812345678",
                "workflow_id": "wf_1234567812345678",
                "step_id": "sr_det_step12345678",
                "initiator_id": "system",
                "timestamp_isot": "2026-08-06T00:00:00Z",
                "unix_time": 1700000000,
                "v2_engine": True,
                "task_blueprint": "sp_det_step",
            },
        },
    )

    with patch("backend_v2.workers.synthesis_worker.UnifiedWorkflowRepository", return_value=mock_repo):
        await generate_profile_synthesis_and_pdf_task(
            execution_id="exec_1234567812345678", accept_language="en", profile_id="prof_1111111111111111", redis=None
        )

    prof_synth = await _get_profile_syntheses(mock_repo)
    assert prof_synth is not None
    cache = prof_synth["prof_1111111111111111"]
    assert cache.extension_metrics is not None
    metrics = cache.extension_metrics
    assert metrics.authenticity_score == 2.5
    assert metrics.performative_phrases_count == 2.0
    assert metrics.total_word_count == 100
    assert metrics.jargon_density == 2.0


@pytest.mark.asyncio
@patch("backend_v2.workers.synthesis_worker.get_driver", new_callable=AsyncMock)
async def test_worker_synthesis_extracts_metrics_for_coach_goodhart_step(
    _mock_driver: AsyncMock,
) -> None:
    """Test extracting extension metrics from modernized Coach/Goodhart step."""
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
            "blk_53f32679aa514fcb": {
                "raw_score": 1.5,
                "justification": "Coach Goodhart evaluation",
                "level_breakdown": {"1.0": {"hits": 1, "total": 3}, "2.0": {"hits": 2, "total": 3}},
            },
            "_step_metadata": {
                "execution_id": "exec_1234567812345678",
                "workflow_id": "wf_9d68c573802341db",
                "step_id": "sr_0228db320e8f41bb",
                "initiator_id": "system",
                "timestamp_isot": "2026-08-06T00:00:00Z",
                "unix_time": 1700000000,
                "v2_engine": True,
                "task_blueprint": "sp_25664f44773a4354",
            },
        },
    )

    with patch("backend_v2.workers.synthesis_worker.UnifiedWorkflowRepository", return_value=mock_repo):
        await generate_profile_synthesis_and_pdf_task(
            execution_id="exec_1234567812345678", accept_language="en", profile_id="prof_1111111111111111", redis=None
        )

    prof_synth = await _get_profile_syntheses(mock_repo)
    assert prof_synth is not None
    cache = prof_synth["prof_1111111111111111"]
    assert cache.extension_metrics is not None
    metrics = cache.extension_metrics
    assert metrics.authenticity_score == 1.5
    assert metrics.performative_phrases_count == 1.0
    assert metrics.total_word_count == 200


@pytest.mark.asyncio
@patch("backend_v2.workers.synthesis_worker.get_driver", new_callable=AsyncMock)
async def test_worker_synthesis_missing_metrics_remains_none(
    _mock_driver: AsyncMock,
) -> None:
    """Test synthesis when extension metrics are missing from trace."""
    get_settings().use_mock_llm = True
    mock_repo = InMemoryUnifiedWorkflowRepository()

    await _setup_mock_repo_for_metrics(mock_repo, trace_content_ling=None, trace_content_det=None)

    with patch("backend_v2.workers.synthesis_worker.UnifiedWorkflowRepository", return_value=mock_repo):
        await generate_profile_synthesis_and_pdf_task(
            execution_id="exec_1234567812345678", accept_language="en", profile_id="prof_1111111111111111", redis=None
        )

    prof_synth = await _get_profile_syntheses(mock_repo)
    assert prof_synth is not None
    assert prof_synth["prof_1111111111111111"].extension_metrics is None


@pytest.mark.asyncio
@patch("backend_v2.workers.synthesis_worker.get_driver", new_callable=AsyncMock)
async def test_worker_synthesis_malformed_metrics_remains_none(
    _mock_driver: AsyncMock,
) -> None:
    """Test synthesis when extension metrics contain malformed score."""
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
                "execution_id": "exec_1234567812345678",
                "workflow_id": "wf_1234567812345678",
                "step_id": "sr_det_step12345678",
                "initiator_id": "system",
                "timestamp_isot": "2026-08-06T00:00:00Z",
                "unix_time": 1700000000,
                "v2_engine": True,
                "task_blueprint": "sp_det_step",
            },
        },
    )

    with patch("backend_v2.workers.synthesis_worker.UnifiedWorkflowRepository", return_value=mock_repo):
        await generate_profile_synthesis_and_pdf_task(
            execution_id="exec_1234567812345678", accept_language="en", profile_id="prof_1111111111111111", redis=None
        )

    prof_synth = await _get_profile_syntheses(mock_repo)
    assert prof_synth is not None
    assert prof_synth["prof_1111111111111111"].extension_metrics is None


@pytest.mark.asyncio
@patch("backend_v2.workers.synthesis_worker.get_driver", new_callable=AsyncMock)
async def test_worker_synthesis_metrics_no_step_metadata(_mock_driver: AsyncMock) -> None:
    """Test synthesis when step metadata is missing from detector output."""
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

    with patch("backend_v2.workers.synthesis_worker.UnifiedWorkflowRepository", return_value=mock_repo):
        await generate_profile_synthesis_and_pdf_task(
            execution_id="exec_1234567812345678", accept_language="en", profile_id="prof_1111111111111111", redis=None
        )

    prof_synth = await _get_profile_syntheses(mock_repo)
    assert prof_synth is not None
    assert prof_synth["prof_1111111111111111"].extension_metrics is None


@pytest.mark.asyncio
@patch("backend_v2.workers.synthesis_worker.get_driver", new_callable=AsyncMock)
async def test_worker_synthesis_metrics_no_task_blueprint_in_metadata(
    _mock_driver: AsyncMock,
) -> None:
    """Test synthesis when task_blueprint is missing from step metadata."""
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
                "execution_id": "exec_1234567812345678",
                "workflow_id": "wf_1234567812345678",
                "step_id": "sr_det_step12345678",
                "initiator_id": "system",
                "timestamp_isot": "2026-08-06T00:00:00Z",
                "unix_time": 1700000000,
                "v2_engine": True,
            },
        },
    )

    with patch("backend_v2.workers.synthesis_worker.UnifiedWorkflowRepository", return_value=mock_repo):
        await generate_profile_synthesis_and_pdf_task(
            execution_id="exec_1234567812345678", accept_language="en", profile_id="prof_1111111111111111", redis=None
        )

    prof_synth = await _get_profile_syntheses(mock_repo)
    assert prof_synth is not None
    assert prof_synth["prof_1111111111111111"].extension_metrics is None


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
@patch("backend_v2.workers.synthesis_worker.get_driver", new_callable=AsyncMock)
@patch("backend_v2.workers.synthesis_worker.LLMClient.from_tier")
async def test_worker_synthesis_matrix_layout_directives(
    mock_from_tier: AsyncMock,
    _mock_driver: AsyncMock,
    view_type: str,
    directive_field: str,
    directive_value: str | None,
    expected_snippet: str | None,
    should_execute_group: bool,
) -> None:
    """Test that matrix synthesis groups strictly execute based on profile-level directives matching view_type."""
    get_settings().use_mock_llm = True

    mock_repo = InMemoryUnifiedWorkflowRepository()
    await _setup_mock_repo_for_metrics(mock_repo, trace_content_ling=None, trace_content_det=None)

    target_blocks_map = {
        "1d_metrics": ["blk_1"],
        "2d_compare": ["blk_1", "blk_2"],
        "3d_matrix": ["blk_1", "blk_2", "blk_3"],
        "text_only": ["blk_1"],
    }
    prof_dict: dict[str, JsonValue] = {
        "id": "prof_1111111111111111",
        "slug": "prof_test",
        "name": {"translations": {"en": "Test Profile"}},
        "workflow_id": "wf_1234567812345678",
        "display_scale": "original",
        "synthesis_length_constraint": 1000,
        "tone_instruction": "Professional",
        "matrix_synthesis_groups": [
            {
                "id": "grp_1234567890123456",
                "title": {"translations": {"fi": "Matriisinäkymä", "en": "Matrix View"}},
                "target_blocks": target_blocks_map[view_type] if view_type in target_blocks_map else ["blk_1"],
                "view_type": view_type,
            }
        ],
        "target_block_order": ["matrix_graphs_block"],
    }
    if directive_value is not None:
        prof_dict[directive_field] = directive_value

    mock_repo.set_output_profiles([prof_dict])

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
                            layout_id="grp_1234567890123456",
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

    with patch("backend_v2.workers.synthesis_worker.UnifiedWorkflowRepository", return_value=mock_repo):
        if not should_execute_group:
            await generate_profile_synthesis_and_pdf_task(
                execution_id="exec_1234567812345678",
                accept_language="fi",
                profile_id="prof_1111111111111111",
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
            execution_id="exec_1234567812345678", accept_language="fi", profile_id="prof_1111111111111111", redis=None
        )

    all_user_content = ""
    for call in mock_client.run_structured_task.call_args_list:
        if "messages" in call.kwargs:
            messages = call.kwargs["messages"]
            all_user_content += " ".join(
                m.content
                if isinstance(m, (ChatMessageDTO, LLMMessageDTO))
                else (m["content"] if type(m) is dict and "content" in m else "")
                for m in messages
            )

    if expected_snippet is not None:
        assert expected_snippet in all_user_content


@pytest.mark.asyncio
@patch("backend_v2.workers.synthesis_worker.get_driver", new_callable=AsyncMock)
@patch("backend_v2.workers.synthesis_worker.LLMClient.from_tier")
async def test_worker_synthesis_disabled_layout_omits_section_instruction(
    mock_from_tier: AsyncMock,
    _mock_driver: AsyncMock,
) -> None:
    """Test that when matrix_synthesis_groups is empty, no group section instruction is generated."""
    get_settings().use_mock_llm = True

    mock_repo = InMemoryUnifiedWorkflowRepository()
    await _setup_mock_repo_for_metrics(mock_repo, trace_content_ling=None, trace_content_det=None)

    mock_repo.set_output_profiles(
        [
            {
                "id": "prof_1111111111111111",
                "slug": "prof_disabled",
                "name": {"translations": {"en": "Disabled Profile"}},
                "workflow_id": "wf_1234567812345678",
                "display_scale": "original",
                "synthesis_length_constraint": 1000,
                "tone_instruction": "Professional",
                "executive_summary_directive": "EXECUTIVE SUMMARY DIRECTIVE",
                "matrix_synthesis_groups": [],
                "target_block_order": ["executive_summary_block"],
            }
        ]
    )

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

    with patch("backend_v2.workers.synthesis_worker.UnifiedWorkflowRepository", return_value=mock_repo):
        await generate_profile_synthesis_and_pdf_task(
            execution_id="exec_1234567812345678", accept_language="fi", profile_id="prof_1111111111111111", redis=None
        )

    assert mock_client.run_structured_task.called
    all_user_content = ""
    for call in mock_client.run_structured_task.call_args_list:
        if "messages" in call.kwargs:
            messages = call.kwargs["messages"]
            all_user_content += " ".join(
                m.content
                if isinstance(m, (ChatMessageDTO, LLMMessageDTO))
                else (m["content"] if type(m) is dict and "content" in m else "")
                for m in messages
            )
    assert "2D COMPARISON SYNTHESIS MANDATE:" not in all_user_content


@pytest.mark.asyncio
@patch("backend_v2.workers.synthesis_worker.get_driver", new_callable=AsyncMock)
@patch("backend_v2.workers.synthesis_worker.LLMClient.from_tier")
async def test_worker_synthesis_executive_summary_instruction_and_cache(
    mock_from_tier: AsyncMock,
    _mock_driver: AsyncMock,
) -> None:
    """Test that executive summary instruction is generated and results are cached properly."""
    get_settings().use_mock_llm = True

    mock_repo = InMemoryUnifiedWorkflowRepository()
    await _setup_mock_repo_for_metrics(mock_repo, trace_content_ling=None, trace_content_det=None)

    mock_repo.set_output_profiles(
        [
            {
                "id": "prof_1111111111111111",
                "slug": "prof_exec_summary",
                "name": {"translations": {"en": "Exec Profile"}},
                "workflow_id": "wf_1234567812345678",
                "display_scale": "original",
                "synthesis_length_constraint": 1000,
                "tone_instruction": "Professional",
                "executive_summary_directive": "EXECUTIVE SUMMARY SYNTHESIS MANDATE:",
                "matrix_synthesis_groups": [],
                "target_block_order": ["executive_summary_block"],
            }
        ]
    )

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

    with patch("backend_v2.workers.synthesis_worker.UnifiedWorkflowRepository", return_value=mock_repo):
        await generate_profile_synthesis_and_pdf_task(
            execution_id="exec_1234567812345678", accept_language="fi", profile_id="prof_1111111111111111", redis=None
        )

    assert mock_client.run_structured_task.called
    all_user_content = ""
    for call in mock_client.run_structured_task.call_args_list:
        if "messages" in call.kwargs:
            messages = call.kwargs["messages"]
            all_user_content += " ".join(
                m.content
                if isinstance(m, (ChatMessageDTO, LLMMessageDTO))
                else (m["content"] if type(m) is dict and "content" in m else "")
                for m in messages
            )
    assert '<section_instruction id="executive_summary_block" title="Executive Summary">' in all_user_content
    assert "EXECUTIVE SUMMARY SYNTHESIS MANDATE:" in all_user_content

    prof_synth = await _get_profile_syntheses(mock_repo)
    assert prof_synth is not None
    sec_synth = prof_synth["prof_1111111111111111"].section_syntheses
    assert "executive_summary_block" in sec_synth
    assert len(sec_synth["executive_summary_block"]) == 1
    block = sec_synth["executive_summary_block"][0]
    assert isinstance(block, ParagraphBlock)
    assert block.text == "Executive summary narrative paragraph 1."


@pytest.mark.asyncio
@patch("backend_v2.workers.synthesis_worker.get_driver", new_callable=AsyncMock)
@patch("backend_v2.workers.synthesis_worker.LLMClient.from_tier")
async def test_worker_synthesis_multi_section_aggregation(
    mock_from_tier: AsyncMock,
    _mock_driver: AsyncMock,
) -> None:
    """Test that multiple SynthesisSectionDTO items for a matrix group are aggregated into sec_dict[group_id]."""
    get_settings().use_mock_llm = True

    mock_repo = InMemoryUnifiedWorkflowRepository()
    await _setup_mock_repo_for_metrics(mock_repo, trace_content_ling=None, trace_content_det=None)

    mock_repo.set_output_profiles(
        [
            {
                "id": "prof_1111111111111111",
                "slug": "prof_multi_sec",
                "name": {"translations": {"en": "Multi Section Profile"}},
                "workflow_id": "wf_1234567812345678",
                "display_scale": "original",
                "synthesis_length_constraint": 1000,
                "tone_instruction": "Professional",
                "matrix_1d_synthesis_directive": "CUSTOM CAUSALITY DIRECTIVE",
                "matrix_synthesis_groups": [
                    {
                        "id": "grp_c5804a9143c34cb1",
                        "title": {"translations": {"fi": "Kausaalisuus", "en": "Causality"}},
                        "target_blocks": ["blk_1"],
                        "view_type": "1d_metrics",
                    }
                ],
                "target_block_order": ["matrix_graphs_block"],
            }
        ]
    )

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

    with patch("backend_v2.workers.synthesis_worker.UnifiedWorkflowRepository", return_value=mock_repo):
        await generate_profile_synthesis_and_pdf_task(
            execution_id="exec_1234567812345678", accept_language="fi", profile_id="prof_1111111111111111", redis=None
        )

    prof_synth = await _get_profile_syntheses(mock_repo)
    assert prof_synth is not None
    sec_synth = prof_synth["prof_1111111111111111"].section_syntheses
    assert "grp_c5804a9143c34cb1" in sec_synth
    assert len(sec_synth["grp_c5804a9143c34cb1"]) == 2
    b1 = sec_synth["grp_c5804a9143c34cb1"][0]
    b2 = sec_synth["grp_c5804a9143c34cb1"][1]
    assert isinstance(b1, ParagraphBlock)
    assert isinstance(b2, ParagraphBlock)
    assert b1.text == "Paragraph 1 text"
    assert b2.text == "Paragraph 2 text"


@pytest.mark.asyncio
@patch("backend_v2.workers.synthesis_worker.get_driver", new_callable=AsyncMock)
@patch("backend_v2.workers.synthesis_worker.LLMClient.from_tier")
async def test_worker_synthesis_empty_sections_not_set_in_cache(
    mock_from_tier: AsyncMock,
    _mock_driver: AsyncMock,
) -> None:
    """Negative Test: Verify that when matrix sections or content_blocks are empty, no key is set in sec_dict."""
    get_settings().use_mock_llm = True

    mock_repo = InMemoryUnifiedWorkflowRepository()
    await _setup_mock_repo_for_metrics(mock_repo, trace_content_ling=None, trace_content_det=None)

    mock_repo.set_output_profiles(
        [
            {
                "id": "prof_1111111111111111",
                "slug": "prof_empty_sec",
                "name": {"translations": {"en": "Empty Section Profile"}},
                "workflow_id": "wf_1234567812345678",
                "display_scale": "original",
                "synthesis_length_constraint": 1000,
                "tone_instruction": "Professional",
                "matrix_1d_synthesis_directive": "1D DIRECTIVE",
                "matrix_synthesis_groups": [
                    {
                        "id": "grp_0000000000000000",
                        "title": {"translations": {"fi": "Kausaalisuus", "en": "Causality"}},
                        "target_blocks": ["blk_1"],
                    }
                ],
                "target_block_order": ["matrix_graphs_block"],
            }
        ]
    )

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

    with patch("backend_v2.workers.synthesis_worker.UnifiedWorkflowRepository", return_value=mock_repo):
        await generate_profile_synthesis_and_pdf_task(
            execution_id="exec_1234567812345678", accept_language="fi", profile_id="prof_1111111111111111", redis=None
        )

    prof_synth = await _get_profile_syntheses(mock_repo)
    assert prof_synth is not None
    sec_synth = prof_synth["prof_1111111111111111"].section_syntheses
    assert "grp_0000000000000000" not in sec_synth


@pytest.mark.asyncio
@patch("backend_v2.workers.synthesis_worker.get_driver", new_callable=AsyncMock)
@patch("backend_v2.workers.synthesis_worker.LLMClient.from_tier")
async def test_worker_synthesis_custom_directives_resolution(
    mock_from_tier: AsyncMock,
    _mock_driver: AsyncMock,
) -> None:
    """Test custom row, XAI, and variance directives configured in profile.

    Verifies they are dynamically compiled and injected into prompts.
    """
    get_settings().use_mock_llm = True

    mock_repo = InMemoryUnifiedWorkflowRepository()
    await _setup_mock_repo_for_metrics(
        mock_repo,
        trace_content_ling={
            "performative_patterns": [{"pattern_id": "1", "detected_phrase": "test phrase", "category": "cat"}]
        },
        trace_content_det={
            "blk_53f32679aa514fcb": {
                "raw_score": 3.0,
                "justification": "Authenticity evaluation",
                "level_breakdown": {},
            },
            "_step_metadata": {
                "execution_id": "exec_1234567812345678",
                "workflow_id": "wf_1234567812345678",
                "step_id": "sr_det_step12345678",
                "initiator_id": "system",
                "timestamp_isot": "2026-08-06T00:00:00Z",
                "unix_time": 1700000000,
                "v2_engine": True,
                "task_blueprint": "sp_det_step",
            },
        },
    )

    mock_repo.set_output_profiles(
        [
            {
                "id": "prof_1111111111111111",
                "slug": "prof_custom_directives",
                "name": {"translations": {"en": "Custom Directives Profile"}},
                "workflow_id": "wf_1234567812345678",
                "display_scale": "original",
                "synthesis_length_constraint": 1000,
                "tone_instruction": "Professional",
                "row_explanation_directive": "CUSTOM ROW EXPLANATION DIRECTIVE",
                "xai_synthesis_directive": "CUSTOM XAI SYNTHESIS DIRECTIVE",
                "variance_synthesis_directive": "CUSTOM VARIANCE DIRECTIVE",
                "visible_workflow_extensions": ["variance_validation"],
                "variance_target_block": "blk_53f32679aa514fcb",
                "matrix_visible_columns": ["label", "row_explanation"],
                "matrix_synthesis_groups": [],
                "target_block_order": ["variance_validation_block", "matrix_summary_table_block"],
            }
        ]
    )

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

    with patch("backend_v2.workers.synthesis_worker.UnifiedWorkflowRepository", return_value=mock_repo):
        await generate_profile_synthesis_and_pdf_task(
            execution_id="exec_1234567812345678", accept_language="fi", profile_id="prof_1111111111111111", redis=None
        )

    all_user_content = ""
    for call in mock_client.run_structured_task.call_args_list:
        if "messages" in call.kwargs:
            messages = call.kwargs["messages"]
            all_user_content += " ".join(
                m.content
                if isinstance(m, (ChatMessageDTO, LLMMessageDTO))
                else (m["content"] if type(m) is dict and "content" in m else "")
                for m in messages
            )

    assert "CUSTOM XAI SYNTHESIS DIRECTIVE" in all_user_content
    assert "CUSTOM VARIANCE DIRECTIVE" in all_user_content


@pytest.mark.asyncio
@patch("backend_v2.workers.synthesis_worker.get_driver", new_callable=AsyncMock)
async def test_worker_synthesis_missing_variance_target_block_raises_configuration_error(
    _mock_driver: AsyncMock,
) -> None:
    """Test that missing variance_target_block when variance is active raises fail-fast AppException."""
    get_settings().use_mock_llm = True
    mock_repo = InMemoryUnifiedWorkflowRepository()

    await _setup_mock_repo_for_metrics(
        mock_repo,
        trace_content_ling={"performative_patterns": [], "total_word_count": 100},
        trace_content_det={"blk_53f32679aa514fcb": {"raw_score": 2.5, "justification": "test"}},
    )

    # Override profile without variance_target_block
    mock_repo.set_output_profiles(
        [
            OutputProfile.model_construct(
                id="prof_1111111111111111",
                slug="prof_missing_target",
                name={"translations": {"en": "Missing Target"}},
                workflow_id="wf_1234567812345678",
                display_scale="original",
                visible_workflow_extensions=["variance_validation"],
                variance_target_block=None,
                target_block_order=["variance_validation_block"],
                matrix_synthesis_groups=[],
            )
        ]
    )

    with patch("backend_v2.workers.synthesis_worker.UnifiedWorkflowRepository", return_value=mock_repo):
        with pytest.raises(AppException) as exc_info:
            await generate_profile_synthesis_and_pdf_task(
                execution_id="exec_1234567812345678",
                accept_language="en",
                profile_id="prof_1111111111111111",
                redis=None,
            )

    assert exc_info.value.status_code in (400, 500)
    assert "variance_target_block" in str(exc_info.value)


@pytest.mark.asyncio
@patch("backend_v2.workers.synthesis_worker.get_driver", new_callable=AsyncMock)
async def test_worker_synthesis_unevaluated_target_block_handled_gracefully(
    _mock_driver: AsyncMock,
) -> None:
    """Test unevaluated target block in trace.

    If target block was never evaluated in the trace, synthesis succeeds without variance metrics.
    """
    get_settings().use_mock_llm = True
    mock_repo = InMemoryUnifiedWorkflowRepository()

    await _setup_mock_repo_for_metrics(
        mock_repo,
        trace_content_ling={"performative_patterns": [], "total_word_count": 100},
        trace_content_det={
            # Target block is blk_53f32679aa514fcb, but trace only has blk_unrelated99999999
            "blk_unrelated99999999": {
                "raw_score": 1.0,
                "justification": "Other block",
            }
        },
    )

    with patch("backend_v2.workers.synthesis_worker.UnifiedWorkflowRepository", return_value=mock_repo):
        await generate_profile_synthesis_and_pdf_task(
            execution_id="exec_1234567812345678",
            accept_language="en",
            profile_id="prof_1111111111111111",
            redis=None,
        )

    prof_synth = await _get_profile_syntheses(mock_repo)
    assert prof_synth is not None
    # Since blk_53f32679aa514fcb was never evaluated, extension_metrics should be None
    assert prof_synth["prof_1111111111111111"].extension_metrics is None


@pytest.mark.asyncio
@patch("backend_v2.workers.synthesis_worker.get_driver", new_callable=AsyncMock)
async def test_worker_synthesis_extracts_user_role_from_target_block_deterministically(
    _mock_driver: AsyncMock,
) -> None:
    """Test that when user_role_target_block is set, user_role is extracted deterministically from trace."""
    get_settings().use_mock_llm = True
    mock_repo = InMemoryUnifiedWorkflowRepository()

    await _setup_mock_repo_for_metrics(
        mock_repo,
        trace_content_ling={"performative_patterns": [], "total_word_count": 100},
        trace_content_det={
            "blk_53f32679aa514fcb": {
                "raw_score": 4.0,
                "justification": "Evaluated Goodhart Driver Score",
            }
        },
    )

    mock_repo.set_output_profiles(
        [
            {
                "id": "prof_1111111111111111",
                "slug": "prof_role_target",
                "name": {"translations": {"en": "Role Target Profile"}},
                "workflow_id": "wf_1234567812345678",
                "display_scale": "original",
                "visible_workflow_extensions": ["variance_validation"],
                "variance_target_block": "blk_53f32679aa514fcb",
                "user_role_target_block": "blk_53f32679aa514fcb",
                "target_block_order": ["variance_validation_block"],
                "matrix_synthesis_groups": [],
            }
        ]
    )

    with patch("backend_v2.workers.synthesis_worker.UnifiedWorkflowRepository", return_value=mock_repo):
        await generate_profile_synthesis_and_pdf_task(
            execution_id="exec_1234567812345678",
            accept_language="en",
            profile_id="prof_1111111111111111",
            redis=None,
        )

    prof_synth = await _get_profile_syntheses(mock_repo)
    assert prof_synth is not None
    cache_item = prof_synth["prof_1111111111111111"]
    assert cache_item.user_role == RoleClassification.DRIVER.value
    assert "blk_53f32679aa514fcb" in str(cache_item.user_role_justification)
    assert "score 4.0" in str(cache_item.user_role_justification)
