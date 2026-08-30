from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.dtos.synthesis import (
    ExecutiveSummarySectionResult,
    MatrixSectionSynthesesResult,
    SynthesisSectionDTO,
    XaiHighlightsResult,
)
from backend_v2.models.prompts import DEFAULT_SYNTHESIS_SYSTEM_PROMPT
from backend_v2.models.state import TraceEvent
from backend_v2.models.v2_core import ExecutionRecord, ExecutionStatus
from backend_v2.models.view.sdui import ParagraphBlock
from backend_v2.settings import get_settings
from backend_v2.worker import generate_profile_synthesis_and_pdf_task


@pytest.mark.asyncio
@patch("backend_v2.worker.UnifiedWorkflowRepository")
@patch("backend_v2.worker.get_driver", new_callable=AsyncMock)
async def test_worker_extracts_synthesis_from_trace(_mock_driver: AsyncMock, mock_repo_class: AsyncMock) -> None:
    """Test that the worker background task extracts synthesis payload from the DAG execution trace."""
    # Enforce global offline strict mode for unit test isolation
    get_settings().use_mock_llm = True

    mock_repo = AsyncMock()
    mock_repo_class.return_value = mock_repo

    mock_execution = ExecutionRecord(
        id="exec_1234567812345678",
        workflow_id="wf_1234567812345678",
        output_profile_id="prof_1111111111111111",
        status=ExecutionStatus.PASSED,
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
    mock_repo.get_execution.return_value = mock_execution
    mock_repo.get_workflow_by_id.return_value = {
        "id": "wf_1234567812345678",
        "slug": "test_workflow",
        "name": {"translations": {"en": "Test", "fi": "Test"}},
        "description": {"translations": {"en": "Desc", "fi": "Desc"}},
        "status": "draft",
        "allowed_exports": ["pdf"],
        "historical_context_mode": "DISABLED",
        "version": 1,
        "default_profile_id": "prof_1111111111111111",
        "expected_inputs": [],
        "steps": [{"id": "sr_1234567812345678", "task_blueprint": "sp_1234567812345678"}],
    }

    async def mock_get_step_by_id(b_id: str) -> dict[str, Any] | None:
        if b_id == "sp_1234567812345678":
            return {"id": "sp_1234567812345678", "model_strategy": "synthesis", "type": "logic"}
        return None

    mock_repo.get_step_by_id.side_effect = mock_get_step_by_id
    mock_repo.get_all_steps.return_value = [
        {
            "id": "sp_1234567812345678",
            "slug": "synthesis_step",
            "name": {"translations": {"en": "Synth"}},
            "model_strategy": "synthesis",
            "type": "logic",
            "hook": "text_consolidation_hook",
        }
    ]
    mock_repo.get_model_registry.return_value = {
        "id": "cfg_1111111111111111",
        "type": "model_registry",
        "slug": "model_registry",
        "models": {
            "synthesis": {
                "provider": "mock_llm_99",
                "model_name": "gemini-2.5-pro",
                "temperature": 0.0,
                "max_tokens": 1024,
                "is_active": True,
                "tpm_limit": 100000,
                "rpm_limit": 1000,
            }
        },
    }

    mock_repo.get_all_prompt_blocks.return_value = [
        {
            "id": "pb_1111111111111111",
            "slug": "system_prompt",
            "type": "instruction",
            "label": {"translations": {"en": "System"}},
            "description": {"translations": {"en": "System prompt"}},
            "category_id": "system_rule",
        }
    ]

    mock_repo.get_prompt_block.return_value = {
        "id": "pb_2222222222222222",
        "slug": "synthesis_prompt",
        "type": "instruction",
        "label": {"translations": {"en": "Synth System"}},
        "description": {"translations": {"en": "System prompt for synthesis"}},
        "ai_description": "You are an AI.",
        "category_id": "system_rule",
    }

    mock_repo.get_output_profile_by_id.return_value = {
        "slug": "test_slug",
        "workflow_id": "wf_123",
        "name": {"translations": {"en": "Test", "fi": "Test"}},
        "id": "prof_1111111111111111",
        "strictness_level": 85,
        "scoring_strategy": "AVERAGE",
        "max_extension_items": 3,
        "synthesis_length_constraint": 1000,
        "tone_instruction": {"translations": {"en": "Professional"}},
        "matrix_synthesis_groups": [
            {
                "id": "grp_1111111111111111",
                "title": {"translations": {"en": "Group 1", "fi": "Ryhmä 1"}},
                "target_blocks": ["blk_1"],
            }
        ],
        "target_block_order": ["matrix_graphs_block"],
        "display_scale": "original",
    }

    await generate_profile_synthesis_and_pdf_task(
        execution_id="exec_1234567812345678", accept_language="en", profile_id="prof_1111111111111111", redis=None
    )

    found_payload = None
    for call in mock_repo.update_execution.call_args_list:
        args, kwargs = call
        if args[0] == "exec_1234567812345678" and "profile_syntheses" in args[1]:
            found_payload = args[1]
            break

    assert found_payload is not None, "Execution record was not updated with profile_syntheses"
    assert isinstance(found_payload["profile_syntheses"]["prof_1111111111111111"]["section_syntheses"], dict)


def _setup_mock_repo_for_metrics(
    mock_repo: AsyncMock, trace_content_ling: dict[str, Any] | None, trace_content_det: dict[str, Any] | None
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
        execution_trace=trace_events,
        context_variables={},
    )
    mock_repo.get_execution.return_value = mock_execution
    mock_repo.get_workflow_by_id.return_value = {
        "id": "wf_1234567812345678",
        "slug": "test_workflow",
        "name": {"translations": {"en": "Test", "fi": "Test"}},
        "description": {"translations": {"en": "Desc", "fi": "Desc"}},
        "status": "draft",
        "allowed_exports": ["pdf"],
        "historical_context_mode": "DISABLED",
        "version": 1,
        "default_profile_id": "prof_1111111111111111",
        "expected_inputs": [],
        "steps": [],
    }
    mock_repo.get_all_steps.return_value = []
    mock_repo.get_model_registry.return_value = {
        "id": "cfg_1111111111111111",
        "type": "model_registry",
        "slug": "model_registry",
        "models": {
            "synthesis": {
                "provider": "mock_llm_99",
                "model_name": "gemini-2.5-pro",
                "temperature": 0.0,
                "max_tokens": 1024,
                "is_active": True,
                "tpm_limit": 100000,
                "rpm_limit": 1000,
            },
            "strict": {
                "provider": "mock_llm_99",
                "model_name": "gemini-2.5-pro",
                "temperature": 0.0,
                "max_tokens": 1024,
                "is_active": True,
                "tpm_limit": 100000,
                "rpm_limit": 1000,
            },
        },
    }
    mock_repo.get_all_prompt_blocks.return_value = []

    async def _mock_get_prompt_block(block_id: str) -> dict[str, Any]:
        return {
            "id": block_id,
            "slug": "synthesis_prompt",
            "type": "instruction",
            "label": {"translations": {"en": "Synth System"}},
            "description": {"translations": {"en": "System prompt for synthesis"}},
            "ai_description": "You are an AI.",
            "category_id": "system_rule",
        }

    mock_repo.get_prompt_block.side_effect = _mock_get_prompt_block
    mock_repo.get_all_prompt_blocks.return_value = []
    mock_repo.get_output_profile_by_id.return_value = {
        "id": "prof_1111111111111111",
        "slug": "prof",
        "name": {"translations": {"en": "test"}},
        "workflow_id": "wf_1234567812345678",
        "strictness_level": 85,
        "scoring_strategy": "AVERAGE",
        "display_scale": "original",
        "visible_workflow_extensions": ["variance_validation"],
        "performativity_detector_step_id": "sp_det_step",
        "matrix_synthesis_groups": [],
        "target_block_order": [],
    }


@pytest.mark.asyncio
@patch("backend_v2.worker.UnifiedWorkflowRepository")
@patch("backend_v2.worker.get_driver", new_callable=AsyncMock)
async def test_worker_synthesis_extracts_metrics_from_trace(
    _mock_driver: AsyncMock, mock_repo_class: AsyncMock
) -> None:
    mock_repo = AsyncMock()
    mock_repo_class.return_value = mock_repo

    _setup_mock_repo_for_metrics(
        mock_repo,
        trace_content_ling={
            "performative_patterns": [
                {"pattern_id": "1", "detected_phrase": "phrase", "category": "cat"},
                {"pattern_id": "2", "detected_phrase": "phrase2", "category": "cat2"},
            ]
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
                "task_blueprint": "sp_det_step",
            },
        },
    )

    await generate_profile_synthesis_and_pdf_task(
        execution_id="exec_1234567812345678", accept_language="en", profile_id="prof_1111111111111111", redis=None
    )

    found_payload = None
    for call in mock_repo.update_execution.call_args_list:
        args, kwargs = call
        if args[0] == "exec_1234567812345678" and "profile_syntheses" in args[1]:
            found_payload = args[1]
            break

    assert found_payload is not None
    metrics = found_payload["profile_syntheses"]["prof_1111111111111111"].get("extension_metrics")
    assert metrics is not None
    assert metrics["authenticity_score"] == 2.5
    assert metrics["performative_phrases_count"] == 2.0


@pytest.mark.asyncio
@patch("backend_v2.worker.UnifiedWorkflowRepository")
@patch("backend_v2.worker.get_driver", new_callable=AsyncMock)
async def test_worker_synthesis_missing_metrics_remains_none(
    _mock_driver: AsyncMock, mock_repo_class: AsyncMock
) -> None:
    mock_repo = AsyncMock()
    mock_repo_class.return_value = mock_repo

    _setup_mock_repo_for_metrics(mock_repo, trace_content_ling=None, trace_content_det=None)

    await generate_profile_synthesis_and_pdf_task(
        execution_id="exec_1234567812345678", accept_language="en", profile_id="prof_1111111111111111", redis=None
    )

    found_payload = None
    for call in mock_repo.update_execution.call_args_list:
        args, kwargs = call
        if args[0] == "exec_1234567812345678" and "profile_syntheses" in args[1]:
            found_payload = args[1]
            break

    assert found_payload is not None
    metrics = found_payload["profile_syntheses"]["prof_1111111111111111"].get("extension_metrics")
    assert metrics is None


@pytest.mark.asyncio
@patch("backend_v2.worker.UnifiedWorkflowRepository")
@patch("backend_v2.worker.get_driver", new_callable=AsyncMock)
async def test_worker_synthesis_malformed_metrics_remains_none(
    _mock_driver: AsyncMock, mock_repo_class: AsyncMock
) -> None:
    mock_repo = AsyncMock()
    mock_repo_class.return_value = mock_repo

    _setup_mock_repo_for_metrics(
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

    await generate_profile_synthesis_and_pdf_task(
        execution_id="exec_1234567812345678", accept_language="en", profile_id="prof_1111111111111111", redis=None
    )

    found_payload = None
    for call in mock_repo.update_execution.call_args_list:
        args, kwargs = call
        if args[0] == "exec_1234567812345678" and "profile_syntheses" in args[1]:
            found_payload = args[1]
            break

    assert found_payload is not None
    metrics = found_payload["profile_syntheses"]["prof_1111111111111111"].get("extension_metrics")
    assert metrics is None


@pytest.mark.asyncio
@patch("backend_v2.worker.UnifiedWorkflowRepository")
@patch("backend_v2.worker.get_driver", new_callable=AsyncMock)
async def test_worker_synthesis_metrics_no_step_metadata(_mock_driver: AsyncMock, mock_repo_class: AsyncMock) -> None:
    mock_repo = AsyncMock()
    mock_repo_class.return_value = mock_repo

    _setup_mock_repo_for_metrics(
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

    await generate_profile_synthesis_and_pdf_task(
        execution_id="exec_1234567812345678", accept_language="en", profile_id="prof_1111111111111111", redis=None
    )

    found_payload = None
    for call in mock_repo.update_execution.call_args_list:
        args, kwargs = call
        if args[0] == "exec_1234567812345678" and "profile_syntheses" in args[1]:
            found_payload = args[1]
            break

    assert found_payload is not None
    metrics = found_payload["profile_syntheses"]["prof_1111111111111111"].get("extension_metrics")
    assert metrics is None


@pytest.mark.asyncio
@patch("backend_v2.worker.UnifiedWorkflowRepository")
@patch("backend_v2.worker.get_driver", new_callable=AsyncMock)
async def test_worker_synthesis_metrics_no_task_blueprint_in_metadata(
    _mock_driver: AsyncMock, mock_repo_class: AsyncMock
) -> None:
    mock_repo = AsyncMock()
    mock_repo_class.return_value = mock_repo

    _setup_mock_repo_for_metrics(
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

    await generate_profile_synthesis_and_pdf_task(
        execution_id="exec_1234567812345678", accept_language="en", profile_id="prof_1111111111111111", redis=None
    )

    found_payload = None
    for call in mock_repo.update_execution.call_args_list:
        args, kwargs = call
        if args[0] == "exec_1234567812345678" and "profile_syntheses" in args[1]:
            found_payload = args[1]
            break

    assert found_payload is not None
    metrics = found_payload["profile_syntheses"]["prof_1111111111111111"].get("extension_metrics")
    assert metrics is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("synthesis_directive", "expected_snippet"),
    [
        (None, "2D COMPARISON SYNTHESIS MANDATE:"),
        ("CUSTOM 1D MANDATE:", "CUSTOM 1D MANDATE:"),
        ("CUSTOM 3D MANDATE:", "CUSTOM 3D MANDATE:"),
    ],
)
@patch("backend_v2.worker.UnifiedWorkflowRepository")
@patch("backend_v2.worker.get_driver", new_callable=AsyncMock)
@patch("backend_v2.worker.LLMClient.from_strategy")
async def test_worker_synthesis_matrix_layout_directives(
    mock_from_strategy: AsyncMock,
    _mock_driver: AsyncMock,
    mock_repo_class: AsyncMock,
    synthesis_directive: str | None,
    expected_snippet: str,
) -> None:
    """Test that matrix synthesis groups deterministically receive their respective synthesis directives."""
    get_settings().use_mock_llm = True

    mock_repo = AsyncMock()
    mock_repo_class.return_value = mock_repo
    _setup_mock_repo_for_metrics(mock_repo, trace_content_ling=None, trace_content_det=None)

    mock_repo.get_output_profile_by_id.return_value = {
        "id": "prof_1111111111111111",
        "slug": "prof_test",
        "name": {"translations": {"en": "Test Profile"}},
        "workflow_id": "wf_1234567812345678",
        "strictness_level": 85,
        "scoring_strategy": "AVERAGE",
        "display_scale": "original",
        "synthesis_length_constraint": 1000,
        "tone_instruction": {"translations": {"en": "Professional", "fi": "Ammattimainen"}},
        "matrix_synthesis_groups": [
            {
                "id": "grp_1234567890123456",
                "title": {"translations": {"fi": "Matriisinäkymä", "en": "Matrix View"}},
                "target_blocks": ["blk_1"],
                "synthesis_directive": synthesis_directive,
                "view_type": "2d_compare",
            }
        ],
        "target_block_order": ["matrix_graphs_block"],
    }

    mock_client = AsyncMock()

    async def _mock_run_structured_task(*args: Any, **kwargs: Any) -> tuple[Any, TokenUsage]:
        resp_model = kwargs.get("response_model")
        usage = TokenUsage(prompt_tokens=50, completion_tokens=50, total_tokens=100, cost_usd=0.001)
        if resp_model is ExecutiveSummarySectionResult:
            return (
                ExecutiveSummarySectionResult(
                    user_role="Executive",
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
    mock_from_strategy.return_value = mock_client

    await generate_profile_synthesis_and_pdf_task(
        execution_id="exec_1234567812345678", accept_language="fi", profile_id="prof_1111111111111111", redis=None
    )

    assert mock_client.run_structured_task.called
    assert any(
        DEFAULT_SYNTHESIS_SYSTEM_PROMPT in m.get("content", "")
        for call in mock_client.run_structured_task.call_args_list
        for m in call.kwargs.get("messages", [])
        if isinstance(m, dict) and m.get("role") == "system"
    )
    all_user_content = ""
    for call in mock_client.run_structured_task.call_args_list:
        messages = call.kwargs.get("messages", [])
        all_user_content += " ".join(m.get("content", "") for m in messages if isinstance(m, dict))
    assert expected_snippet in all_user_content


@pytest.mark.asyncio
@patch("backend_v2.worker.UnifiedWorkflowRepository")
@patch("backend_v2.worker.get_driver", new_callable=AsyncMock)
@patch("backend_v2.worker.LLMClient.from_strategy")
async def test_worker_synthesis_disabled_layout_omits_section_instruction(
    mock_from_strategy: AsyncMock,
    _mock_driver: AsyncMock,
    mock_repo_class: AsyncMock,
) -> None:
    """Test that when matrix_synthesis_groups is empty, no group section instruction is generated."""
    get_settings().use_mock_llm = True

    mock_repo = AsyncMock()
    mock_repo_class.return_value = mock_repo
    _setup_mock_repo_for_metrics(mock_repo, trace_content_ling=None, trace_content_det=None)

    mock_repo.get_output_profile_by_id.return_value = {
        "id": "prof_1111111111111111",
        "slug": "prof_disabled",
        "name": {"translations": {"en": "Disabled Profile"}},
        "workflow_id": "wf_1234567812345678",
        "strictness_level": 85,
        "scoring_strategy": "AVERAGE",
        "display_scale": "original",
        "synthesis_length_constraint": 1000,
        "tone_instruction": {"translations": {"en": "Professional", "fi": "Ammattimainen"}},
        "matrix_synthesis_groups": [],
        "target_block_order": ["executive_summary_block"],
    }

    mock_client = AsyncMock()

    async def _mock_run_structured_task_disabled(*args: Any, **kwargs: Any) -> tuple[Any, TokenUsage]:
        resp_model = kwargs.get("response_model")
        usage = TokenUsage(prompt_tokens=50, completion_tokens=50, total_tokens=100, cost_usd=0.001)
        if resp_model is ExecutiveSummarySectionResult:
            return (
                ExecutiveSummarySectionResult(
                    user_role="Executive",
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
        return (None, usage)

    mock_client.run_structured_task.side_effect = _mock_run_structured_task_disabled
    mock_from_strategy.return_value = mock_client

    await generate_profile_synthesis_and_pdf_task(
        execution_id="exec_1234567812345678", accept_language="fi", profile_id="prof_1111111111111111", redis=None
    )

    assert mock_client.run_structured_task.called
    all_user_content = ""
    for call in mock_client.run_structured_task.call_args_list:
        messages = call.kwargs.get("messages", [])
        all_user_content += " ".join(m.get("content", "") for m in messages if isinstance(m, dict))
    assert "2D COMPARISON SYNTHESIS MANDATE:" not in all_user_content


@pytest.mark.asyncio
@patch("backend_v2.worker.UnifiedWorkflowRepository")
@patch("backend_v2.worker.get_driver", new_callable=AsyncMock)
@patch("backend_v2.worker.LLMClient.from_strategy")
async def test_worker_synthesis_executive_summary_instruction_and_cache(
    mock_from_strategy: AsyncMock,
    _mock_driver: AsyncMock,
    mock_repo_class: AsyncMock,
) -> None:
    """Test that executive summary instruction is generated and results are cached properly."""
    get_settings().use_mock_llm = True

    mock_repo = AsyncMock()
    mock_repo_class.return_value = mock_repo
    _setup_mock_repo_for_metrics(mock_repo, trace_content_ling=None, trace_content_det=None)

    mock_repo.get_output_profile_by_id.return_value = {
        "id": "prof_1111111111111111",
        "slug": "prof_exec_summary",
        "name": {"translations": {"en": "Exec Profile"}},
        "workflow_id": "wf_1234567812345678",
        "strictness_level": 85,
        "scoring_strategy": "AVERAGE",
        "display_scale": "original",
        "synthesis_length_constraint": 1000,
        "tone_instruction": {"translations": {"en": "Professional", "fi": "Ammattimainen"}},
        "matrix_synthesis_groups": [],
        "target_block_order": ["executive_summary_block"],
    }

    mock_client = AsyncMock()

    async def _mock_run_structured_task_exec(*args: Any, **kwargs: Any) -> tuple[Any, TokenUsage]:
        resp_model = kwargs.get("response_model")
        usage = TokenUsage(prompt_tokens=50, completion_tokens=50, total_tokens=100, cost_usd=0.001)
        if resp_model is ExecutiveSummarySectionResult:
            return (
                ExecutiveSummarySectionResult(
                    user_role="ROLE_ARCHITECT",
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
    mock_from_strategy.return_value = mock_client

    await generate_profile_synthesis_and_pdf_task(
        execution_id="exec_1234567812345678", accept_language="fi", profile_id="prof_1111111111111111", redis=None
    )

    assert mock_client.run_structured_task.called
    all_user_content = ""
    for call in mock_client.run_structured_task.call_args_list:
        messages = call.kwargs.get("messages", [])
        all_user_content += " ".join(m.get("content", "") for m in messages if isinstance(m, dict))
    assert '<section_instruction id="executive_summary_block" title="Executive Summary">' in all_user_content
    assert "EXECUTIVE SUMMARY SYNTHESIS MANDATE:" in all_user_content

    found_payload = None
    for call in mock_repo.update_execution.call_args_list:
        args, kwargs = call
        if args[0] == "exec_1234567812345678" and "profile_syntheses" in args[1]:
            found_payload = args[1]
            break

    assert found_payload is not None
    sec_synth = found_payload["profile_syntheses"]["prof_1111111111111111"]["section_syntheses"]
    assert "executive_summary_block" in sec_synth
    assert len(sec_synth["executive_summary_block"]) == 1
    assert sec_synth["executive_summary_block"][0]["text"] == "Executive summary narrative paragraph 1."


@pytest.mark.asyncio
@patch("backend_v2.worker.UnifiedWorkflowRepository")
@patch("backend_v2.worker.get_driver", new_callable=AsyncMock)
@patch("backend_v2.worker.LLMClient.from_strategy")
async def test_worker_synthesis_multi_section_aggregation(
    mock_from_strategy: AsyncMock,
    _mock_driver: AsyncMock,
    mock_repo_class: AsyncMock,
) -> None:
    """Test that multiple SynthesisSectionDTO items for a matrix group are aggregated into sec_dict[group_id]."""
    get_settings().use_mock_llm = True

    mock_repo = AsyncMock()
    mock_repo_class.return_value = mock_repo
    _setup_mock_repo_for_metrics(mock_repo, trace_content_ling=None, trace_content_det=None)

    mock_repo.get_output_profile_by_id.return_value = {
        "id": "prof_1111111111111111",
        "slug": "prof_multi_sec",
        "name": {"translations": {"en": "Multi Section Profile"}},
        "workflow_id": "wf_1234567812345678",
        "strictness_level": 85,
        "scoring_strategy": "AVERAGE",
        "display_scale": "original",
        "synthesis_length_constraint": 1000,
        "tone_instruction": {"translations": {"en": "Professional", "fi": "Ammattimainen"}},
        "matrix_synthesis_groups": [
            {
                "id": "grp_c5804a9143c34cb1",
                "title": {"translations": {"fi": "Kausaalisuus", "en": "Causality"}},
                "target_blocks": ["blk_1"],
            }
        ],
        "target_block_order": ["matrix_graphs_block"],
    }

    mock_client = AsyncMock()

    async def _mock_run_structured_task_multi(*args: Any, **kwargs: Any) -> tuple[Any, TokenUsage]:
        resp_model = kwargs.get("response_model")
        usage = TokenUsage(prompt_tokens=50, completion_tokens=50, total_tokens=100, cost_usd=0.001)
        if resp_model is ExecutiveSummarySectionResult:
            return (
                ExecutiveSummarySectionResult(
                    user_role="Executive",
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
    mock_from_strategy.return_value = mock_client

    await generate_profile_synthesis_and_pdf_task(
        execution_id="exec_1234567812345678", accept_language="fi", profile_id="prof_1111111111111111", redis=None
    )

    found_payload = None
    for call in mock_repo.update_execution.call_args_list:
        args, kwargs = call
        if args[0] == "exec_1234567812345678" and "profile_syntheses" in args[1]:
            found_payload = args[1]
            break

    assert found_payload is not None
    sec_synth = found_payload["profile_syntheses"]["prof_1111111111111111"]["section_syntheses"]
    assert "grp_c5804a9143c34cb1" in sec_synth
    assert len(sec_synth["grp_c5804a9143c34cb1"]) == 2
    assert sec_synth["grp_c5804a9143c34cb1"][0]["text"] == "Paragraph 1 text"
    assert sec_synth["grp_c5804a9143c34cb1"][1]["text"] == "Paragraph 2 text"


@pytest.mark.asyncio
@patch("backend_v2.worker.UnifiedWorkflowRepository")
@patch("backend_v2.worker.get_driver", new_callable=AsyncMock)
@patch("backend_v2.worker.LLMClient.from_strategy")
async def test_worker_synthesis_empty_sections_not_set_in_cache(
    mock_from_strategy: AsyncMock,
    _mock_driver: AsyncMock,
    mock_repo_class: AsyncMock,
) -> None:
    """Negative Test: Verify that when matrix sections or content_blocks are empty, no key is set in sec_dict."""
    get_settings().use_mock_llm = True

    mock_repo = AsyncMock()
    mock_repo_class.return_value = mock_repo
    _setup_mock_repo_for_metrics(mock_repo, trace_content_ling=None, trace_content_det=None)

    mock_repo.get_output_profile_by_id.return_value = {
        "id": "prof_1111111111111111",
        "slug": "prof_empty_sec",
        "name": {"translations": {"en": "Empty Section Profile"}},
        "workflow_id": "wf_1234567812345678",
        "strictness_level": 85,
        "scoring_strategy": "AVERAGE",
        "display_scale": "original",
        "synthesis_length_constraint": 1000,
        "tone_instruction": {"translations": {"en": "Professional", "fi": "Ammattimainen"}},
        "matrix_synthesis_groups": [
            {
                "id": "grp_0000000000000000",
                "title": {"translations": {"fi": "Kausaalisuus", "en": "Causality"}},
                "target_blocks": ["blk_1"],
            }
        ],
        "target_block_order": ["matrix_graphs_block"],
    }

    mock_client = AsyncMock()

    async def _mock_run_structured_task_empty(*args: Any, **kwargs: Any) -> tuple[Any, TokenUsage]:
        resp_model = kwargs.get("response_model")
        usage = TokenUsage(prompt_tokens=50, completion_tokens=50, total_tokens=100, cost_usd=0.001)
        if resp_model is ExecutiveSummarySectionResult:
            return (
                ExecutiveSummarySectionResult(
                    user_role="Executive",
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
    mock_from_strategy.return_value = mock_client

    await generate_profile_synthesis_and_pdf_task(
        execution_id="exec_1234567812345678", accept_language="fi", profile_id="prof_1111111111111111", redis=None
    )

    found_payload = None
    for call in mock_repo.update_execution.call_args_list:
        args, kwargs = call
        if args[0] == "exec_1234567812345678" and "profile_syntheses" in args[1]:
            found_payload = args[1]
            break

    assert found_payload is not None
    sec_synth = found_payload["profile_syntheses"]["prof_1111111111111111"]["section_syntheses"]
    assert "grp_0000000000000000" not in sec_synth
