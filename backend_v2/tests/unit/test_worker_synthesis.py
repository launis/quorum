from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from backend_v2.models.state import TraceEvent
from backend_v2.models.v2_core import ExecutionRecord, ExecutionStatus
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
        output_profile_id="default",
        status=ExecutionStatus.PASSED,
        execution_trace=[
            TraceEvent(
                v=1,
                timestamp=datetime.now(timezone.utc),
                event_type="output",
                step_name="sr_1234567812345678",
                content={"synthesized_markdown": "Test MD"},
            )
        ],
    )
    mock_repo.get_execution.return_value = mock_execution
    mock_repo.get_workflow_by_id.return_value = {
        "id": "wf_1234567812345678",
        "slug": "test_workflow",
        "name": {"default_locale": "en", "translations": {"en": "Test", "fi": "Test"}},
        "description": {"default_locale": "en", "translations": {"en": "Desc", "fi": "Desc"}},
        "status": "draft",
        "allowed_exports": ["pdf"],
        "historical_context_mode": "DISABLED",
        "version": 1,
        "default_profile_id": "default",
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
            "name": {"default_locale": "en", "translations": {"en": "Synth"}},
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
            "label": {"default_locale": "en", "translations": {"en": "System"}},
            "description": {"default_locale": "en", "translations": {"en": "System prompt"}},
            "category_id": "system_rule",
        }
    ]

    mock_repo.get_prompt_block.return_value = {
        "id": "pb_2222222222222222",
        "slug": "synthesis_prompt",
        "type": "instruction",
        "label": {"default_locale": "en", "translations": {"en": "Synth System"}},
        "description": {"default_locale": "en", "translations": {"en": "System prompt for synthesis"}},
        "ai_description": "You are an AI.",
        "category_id": "system_rule",
    }

    mock_repo.get_output_profile_by_id.return_value = {
        "slug": "test_slug",
        "workflow_id": "wf_123",
        "name": {"default_locale": "en", "translations": {"en": "Test", "fi": "Test"}},
        "id": "default",
        "strictness_level": 85,
        "scoring_strategy": "AVERAGE",
        "max_extension_items": 3,
        "layouts": [
            {
                "preset_view": "3d_matrix",
                "title": {"default_locale": "en", "translations": {"en": "T"}},
                "synthesis": {
                    "synthesis_block_id": "pb_2222222222222222",
                    "model_strategy": "synthesis",
                    "length_constraint": 1000,
                    "tone_instruction": {"default_locale": "en", "translations": {"en": "Professional"}},
                    "omit_empty_sections": True,
                },
            }
        ],
        "display_scale": "original",
    }

    await generate_profile_synthesis_and_pdf_task(
        execution_id="exec_1234567812345678", accept_language="en", profile_id="default", redis=None
    )

    found_payload = None
    for call in mock_repo.update_execution.call_args_list:
        args, kwargs = call
        if args[0] == "exec_1234567812345678" and "profile_syntheses" in args[1]:
            found_payload = args[1]
            break

    assert found_payload is not None, "Execution record was not updated with profile_syntheses"
    assert "default" in found_payload["profile_syntheses"]
    assert isinstance(found_payload["profile_syntheses"]["default"]["content_blocks"], list)
    assert isinstance(found_payload["profile_syntheses"]["default"]["xai_highlights"], list)
