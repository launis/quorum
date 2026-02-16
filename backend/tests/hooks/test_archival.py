
import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.hooks.archival import retrieve_precedent
from backend.models.state import WorkflowState
from backend.exceptions import AppException

@pytest.mark.asyncio
async def test_retrieve_precedent_no_repo():
    # Fix: Use correct fields for WorkflowState
    state = WorkflowState(workflow_id="test_workflow")
    
    with pytest.raises(AppException) as excinfo:
        await retrieve_precedent(state, repository=None)
    
    assert "ARCHIVAL_CONFIG_ERROR" in str(excinfo.value.details)
    assert excinfo.value.status_code == 500

@pytest.mark.asyncio
async def test_retrieve_precedent_success():
    state = WorkflowState(workflow_id="current_workflow")
    mock_repo = AsyncMock()
    
    # Mock executions
    mock_repo.get_all_executions.return_value = [
        {
            "execution_id": "exe-1",
            "status": "completed",
            "end_time": "2025-01-01T12:00:00",
            "trace": {
                "step_judge": {
                    "pisteet": {
                        "analyysi": {"arvosana": 80},
                        "arviointi": {"arvosana": 80},
                        "synteesi": {"arvosana": 80}
                    },
                    "kriittiset_havainnot_yhteenveto": "Verdict 1"
                }
            }
        },
        {
            "execution_id": "exe-2", # In progress, should be skipped
            "status": "running"
        }
    ]
    
    new_state = await retrieve_precedent(state, repository=mock_repo)
    
    assert "archivist_precedents" in new_state.context_variables
    summary = new_state.context_variables["archivist_precedents"]
    assert "Case exe-1" in summary
    assert "Verdict 1" in summary
    assert "Case exe-2" not in summary

@pytest.mark.asyncio
async def test_retrieve_precedent_empty():
    state = WorkflowState(workflow_id="current_workflow")
    mock_repo = AsyncMock()
    mock_repo.get_all_executions.return_value = []
    
    new_state = await retrieve_precedent(state, repository=mock_repo)
    
    summary = new_state.context_variables["archivist_precedents"]
    assert "Ei aiempi tapauksia tiedostossa" in summary

@pytest.mark.asyncio
async def test_retrieve_precedent_repo_error():
    state = WorkflowState(workflow_id="current_workflow")
    mock_repo = AsyncMock()
    mock_repo.get_all_executions.side_effect = Exception("DB Down")
    
    with pytest.raises(AppException) as excinfo:
        await retrieve_precedent(state, repository=mock_repo)
        
    assert "ARCHIVAL_RETRIEVAL_FAILED" in str(excinfo.value.details)
    assert "DB Down" in str(excinfo.value.message)
