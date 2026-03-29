from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.v2_core import ExecutionRecord, ExecutionStatus
from backend_v2.services.execution import ExecutionService


@pytest.mark.asyncio
async def test_resume_execution_fails_fast_on_invalid_state() -> None:
    repo_mock = AsyncMock()
    executor_mock = Mock()
    arq_pool = AsyncMock()

    # Setup mock to return an already running execution (invalid for resume)
    mock_record = Mock(spec=ExecutionRecord)
    mock_record.status = ExecutionStatus.RUNNING
    repo_mock.get_execution.return_value = mock_record

    service = ExecutionService(repo=repo_mock, executor=executor_mock)
    initiator = TokenData(id="u1", role=UserRole.ROOT)  # Bypasses auth checks

    with pytest.raises(AppException) as exc_info:
        await service.resume_execution(initiator=initiator, execution_id="exe_123", arq_pool=arq_pool)

    assert "Cannot resume execution in state" in exc_info.value.message
    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"
