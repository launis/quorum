import pytest
from unittest.mock import AsyncMock
from fastapi import Request

from backend_v2.api.routers.execution.executions import (
    list_executions, 
    start_execution, 
    get_execution_status,
    delete_execution,
    resume_execution
)
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.v2_core import ExecutionRecord

@pytest.fixture
def mock_current_user():
    return TokenData(id="user_123", email="test@test.com", role=UserRole.MEMBER)

@pytest.fixture
def mock_execution_service():
    return AsyncMock()

@pytest.fixture
def mock_doc_service():
    return AsyncMock()

@pytest.fixture
def mock_arq_pool():
    return AsyncMock()

@pytest.mark.asyncio
async def test_list_executions(mock_current_user, mock_execution_service) -> None:
    """Test retrieving list of executions."""
    mock_execution_service.list_executions.return_value = []
    result = await list_executions(current_user=mock_current_user, execution_service=mock_execution_service)
    assert result == []
    mock_execution_service.list_executions.assert_called_once_with(initiator=mock_current_user)

@pytest.mark.asyncio
async def test_get_execution_status(mock_current_user, mock_execution_service) -> None:
    """Test retrieving execution status by ID."""
    mock_record = ExecutionRecord(id="exe_1234567890abcdef1234567890abcdef", status="completed", workflow_id="wf_1")
    mock_execution_service.get_execution.return_value = mock_record
    
    result = await get_execution_status(
        execution_id="exe_1234567890abcdef1234567890abcdef",
        current_user=mock_current_user,
        execution_service=mock_execution_service
    )
    assert result.id == "exe_1234567890abcdef1234567890abcdef"
    mock_execution_service.get_execution.assert_called_once_with(initiator=mock_current_user, execution_id="exe_1234567890abcdef1234567890abcdef")

@pytest.mark.asyncio
async def test_start_execution(mock_current_user, mock_execution_service, mock_doc_service, mock_arq_pool) -> None:
    """Test starting an execution with eager document extraction."""
    mock_request = AsyncMock(spec=Request)
    mock_request.json.return_value = {
        "workflow_id": "wf_1",
        "target_locale": "fi",
        "raw_inputs": {"file1": "test"}
    }
    
    mock_record = ExecutionRecord(id="exe_1234567890abcdef1234567890abcdef", status="pending", workflow_id="wf_1")
    mock_execution_service.start_execution.return_value = mock_record
    
    result = await start_execution(
        request=mock_request,
        arq_pool=mock_arq_pool,
        current_user=mock_current_user,
        execution_service=mock_execution_service,
        doc_service=mock_doc_service
    )
    
    assert result.id == "exe_1234567890abcdef1234567890abcdef"
    mock_doc_service.process_raw_inputs.assert_called_once_with({"file1": "test"})
    mock_execution_service.start_execution.assert_called_once()

@pytest.mark.asyncio
async def test_delete_execution(mock_current_user, mock_execution_service) -> None:
    """Test deleting an execution."""
    await delete_execution(
        execution_id="exe_1234567890abcdef1234567890abcdef",
        current_user=mock_current_user,
        execution_service=mock_execution_service
    )
    mock_execution_service.delete_execution.assert_called_once_with(initiator=mock_current_user, execution_id="exe_1234567890abcdef1234567890abcdef")

@pytest.mark.asyncio
async def test_resume_execution(mock_current_user, mock_execution_service, mock_arq_pool) -> None:
    """Test resuming an execution."""
    mock_record = ExecutionRecord(id="exe_1234567890abcdef1234567890abcdef", status="running", workflow_id="wf_1")
    mock_execution_service.resume_execution.return_value = mock_record
    
    res = await resume_execution(
        execution_id="exe_1234567890abcdef1234567890abcdef",
        arq_pool=mock_arq_pool,
        current_user=mock_current_user,
        execution_service=mock_execution_service
    )
    assert res.id == "exe_1234567890abcdef1234567890abcdef"
