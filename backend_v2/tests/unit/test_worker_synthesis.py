from unittest.mock import AsyncMock, patch

import pytest

from backend_v2.core.hook_registry import HookResult
from backend_v2.models.v2_core import ExecutionRecord, ExecutionStatus
from backend_v2.worker import generate_profile_synthesis_and_pdf_task


@pytest.mark.asyncio
@patch("backend_v2.worker.UnifiedWorkflowRepository")
@patch("backend_v2.worker.get_driver", new_callable=AsyncMock)
@patch("backend_v2.core.hook_registry.hook_registry.execute", new_callable=AsyncMock)
async def test_worker_invokes_synthesis_hook(
    mock_execute: AsyncMock, _mock_driver: AsyncMock, mock_repo_class: AsyncMock
) -> None:
    """Test that the worker background task invokes the text_consolidation_hook and updates the execution record."""
    mock_repo = AsyncMock()
    mock_repo_class.return_value = mock_repo

    mock_execution = ExecutionRecord(
        id="exec_1234567812345678",
        workflow_id="wf_1234567812345678",
        status=ExecutionStatus.COMPLETED,
    )
    mock_repo.get_execution.return_value = mock_execution
    mock_repo.get_workflow_by_id.return_value = {
        "id": "wf_1234567812345678",
        "slug": "test_workflow",
        "name": {"default_locale": "en", "translations": {"en": "Test"}},
        "description": {"default_locale": "en", "translations": {"en": "Desc"}},
        "status": "draft",
        "version": 1,
        "default_profile_id": "default",
        "expected_inputs": [],
        "steps": [],
    }
    mock_repo.get_output_profile_by_id.return_value = {
        "slug": "test_slug",
        "workflow_id": "wf_123",
        "name": {"default_locale": "en", "translations": {"en": "Test"}},
        "id": "default",
        "strictness_level": 50,
        "scoring_strategy": "AVERAGE",
        "layouts": [],
        "display_scale": "original",
    }

    mock_execute.return_value = HookResult(success=True, state_delta={"synthesized_markdown": "Test MD"})

    await generate_profile_synthesis_and_pdf_task(
        execution_id="exec_1234567812345678", accept_language="en", profile_id="default", redis=None
    )

    mock_execute.assert_called_once()
    assert mock_execute.call_args[0][0] == "text_consolidation_hook"

    found_payload = None
    for call in mock_repo.update_execution.call_args_list:
        args, kwargs = call
        if args[0] == "exec_1234567812345678" and "profile_syntheses" in args[1]:
            found_payload = args[1]
            break

    assert found_payload is not None, "Execution record was not updated with profile_syntheses"
    assert "default" in found_payload["profile_syntheses"]
    assert found_payload["profile_syntheses"]["default"]["synthesized_markdown"] == "Test MD"
