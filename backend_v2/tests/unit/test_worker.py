import pytest
from unittest.mock import AsyncMock, patch

from backend_v2.worker import health_check, startup, execute_workflow_job
from backend_v2.exceptions import WorkflowNotFoundError

@pytest.mark.asyncio
async def test_health_check():
    res = await health_check({})
    assert res == "OK"

@pytest.mark.asyncio
async def test_startup():
    with patch("backend_v2.worker.get_repository", new_callable=AsyncMock) as mock_repo:
        with patch("backend_v2.worker.LLMClient"):
            with patch("backend_v2.worker.PromptCompiler"):
                with patch("backend_v2.worker.DAGExecutor"):
                    mock_repo.return_value = AsyncMock()
                    ctx = {}
                    await startup(ctx)
                    assert "engine" in ctx
                    assert "repository" in ctx
                    assert "llm_client" in ctx

@pytest.mark.asyncio
async def test_execute_workflow_job_not_found():
    mock_repo = AsyncMock()
    mock_repo.get_workflow.return_value = None
    
    mock_engine = AsyncMock()
    
    ctx = {
        "repository": mock_repo,
        "engine": mock_engine
    }
    
    with pytest.raises(WorkflowNotFoundError):
        await execute_workflow_job(ctx, "nonexistent", {})

@pytest.mark.asyncio
async def test_execute_workflow_job_success():
    mock_repo = AsyncMock()
    mock_repo.get_workflow.return_value = {
        "id": "wf_1234567890123456",
        "name": "Test WF",
        "slug": "test-wf",
        "description": "desc",
        "status": "draft",
        "version": 1,
        "steps": [],
        "default_profile_id": "prof_1"
    }
    
    mock_engine = AsyncMock()
    
    ctx = {
        "repository": mock_repo,
        "engine": mock_engine,
        "redis": AsyncMock()
    }
    
    inputs = {}
    res = await execute_workflow_job(
        ctx, 
        workflow_id="wf_1234567890123456", 
        inputs=inputs, 
        execution_id="exe_123",
        organization_id="org_1",
        user_id="usr_1"
    )
    
    assert res["status"] == "COMPLETED"
    assert res["execution_id"] == "exe_123"
    assert inputs["organization_id"] == "org_1"
    assert inputs["user_id"] == "usr_1"
    mock_engine.execute_workflow.assert_called_once()
    mock_repo.update_execution.assert_called_once()
    ctx["redis"].enqueue_job.assert_called_once_with("render_profile_job", "exe_123", profile_id="prof_1")
