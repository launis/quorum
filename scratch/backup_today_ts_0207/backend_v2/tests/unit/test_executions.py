from typing import Any
from unittest.mock import AsyncMock

import pytest

from backend_v2.api.routers.execution.executions import (
    delete_execution,
    get_execution_status,
    list_executions,
    resume_execution,
    start_execution,
)
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.v2_core import ExecutionRecord


@pytest.fixture
def mock_current_user() -> Any:
    return TokenData(id="user_123", email="test@test.com", role=UserRole.MEMBER)


@pytest.fixture
def mock_execution_service() -> Any:
    return AsyncMock()


@pytest.fixture
def mock_doc_service() -> Any:
    return AsyncMock()


@pytest.fixture
def mock_arq_pool() -> Any:
    return AsyncMock()


@pytest.mark.asyncio
async def test_list_executions(mock_current_user: Any, mock_execution_service: AsyncMock) -> None:
    """Test retrieving list of executions."""
    mock_execution_service.list_executions.return_value = []
    result = await list_executions(current_user=mock_current_user, execution_service=mock_execution_service)
    assert result == []
    mock_execution_service.list_executions.assert_called_once_with(initiator=mock_current_user)


@pytest.mark.asyncio
async def test_get_execution_status(mock_current_user: Any, mock_execution_service: AsyncMock) -> None:
    """Test retrieving execution status by ID."""
    mock_record = ExecutionRecord(
        id="exe_1234567890abcdef1234567890abcdef",
        status=ExecutionStatus.COMPLETED,
        workflow_id="wf_1",
    )
    mock_execution_service.get_execution.return_value = mock_record

    result = await get_execution_status(
        execution_id="exe_1234567890abcdef1234567890abcdef",
        current_user=mock_current_user,
        execution_service=mock_execution_service,
    )
    assert result.id == "exe_1234567890abcdef1234567890abcdef"
    mock_execution_service.get_execution.assert_called_once_with(
        initiator=mock_current_user, execution_id="exe_1234567890abcdef1234567890abcdef"
    )  # noqa: E501


@pytest.mark.asyncio
async def test_start_execution(
    mock_current_user: Any, mock_execution_service: AsyncMock, mock_doc_service: AsyncMock, mock_arq_pool: AsyncMock
) -> None:  # noqa: E501
    """Test starting an execution router delegation."""
    from backend_v2.models.v2_core import ExecutionCreate

    payload = ExecutionCreate.model_validate(
        {
            "workflow_id": "wf_1",
            "target_locale": "fi",
            "raw_inputs": {"dynamic_inputs": {"file1": "test"}},
        }
    )

    mock_record = ExecutionRecord(
        id="exe_1234567890abcdef1234567890abcdef",
        status=ExecutionStatus.PENDING,
        workflow_id="wf_1",
    )
    mock_execution_service.start_execution.return_value = mock_record

    result = await start_execution(
        payload=payload,
        arq_pool=mock_arq_pool,
        current_user=mock_current_user,
        execution_service=mock_execution_service,
        doc_service=mock_doc_service,
    )

    assert result.id == "exe_1234567890abcdef1234567890abcdef"
    mock_execution_service.start_execution.assert_called_once_with(
        initiator=mock_current_user, payload=payload, arq_pool=mock_arq_pool, doc_service=mock_doc_service
    )


@pytest.mark.asyncio
async def test_delete_execution(mock_current_user: Any, mock_execution_service: AsyncMock) -> None:
    """Test deleting an execution."""
    await delete_execution(
        execution_id="exe_1234567890abcdef1234567890abcdef",
        current_user=mock_current_user,
        execution_service=mock_execution_service,
    )
    mock_execution_service.delete_execution.assert_called_once_with(
        initiator=mock_current_user, execution_id="exe_1234567890abcdef1234567890abcdef"
    )  # noqa: E501


@pytest.mark.asyncio
async def test_resume_execution(
    mock_current_user: Any, mock_execution_service: AsyncMock, mock_arq_pool: AsyncMock
) -> None:
    """Test resuming an execution."""
    mock_record = ExecutionRecord(
        id="exe_1234567890abcdef1234567890abcdef",
        status=ExecutionStatus.RUNNING,
        workflow_id="wf_1",
    )
    mock_execution_service.resume_execution.return_value = mock_record

    res = await resume_execution(
        execution_id="exe_1234567890abcdef1234567890abcdef",
        arq_pool=mock_arq_pool,
        current_user=mock_current_user,
        execution_service=mock_execution_service,
    )
    assert res.id == "exe_1234567890abcdef1234567890abcdef"
