from unittest.mock import AsyncMock, patch

import pytest

from backend_v2.core.hook_registry import HookResult
from backend_v2.models.v2_core import ExecutionRecord, ExecutionStatus
from backend_v2.worker import generate_profile_synthesis_and_pdf_task


@pytest.mark.asyncio
async def test_worker_invokes_synthesis_hook() -> None:
    """Test that the worker background task invokes the text_consolidation_hook and updates the execution record."""
    with patch("backend_v2.worker.get_driver", new_callable=AsyncMock) as mock_driver:
        with patch("backend_v2.worker.UnifiedWorkflowRepository") as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo_class.return_value = mock_repo

        mock_execution = ExecutionRecord(
            id="exec_1234567812345678", workflow_id="wf_1234567812345678", status=ExecutionStatus.COMPLETED
        )
        mock_repo.get_execution.return_value = mock_execution

        with patch("backend_v2.core.hook_registry.hook_registry.execute") as mock_execute:
            mock_execute.return_value = HookResult(success=True, state_delta={"synthesized_markdown": "Test MD"})

            await generate_profile_synthesis_and_pdf_task(
                execution_id="exec_1234567812345678", accept_language="en", profile_id="default", redis=None
            )

            mock_execute.assert_called_once()
            assert mock_execute.call_args[0][0] == "text_consolidation_hook"

            args, kwargs = mock_repo.update_execution.call_args
            assert args[0] == "exec_1234567812345678"
            payload = args[1]
            assert "profile_syntheses" in payload
            assert "default" in payload["profile_syntheses"]
            assert payload["profile_syntheses"]["default"]["synthesized_markdown"] == "Test MD"
