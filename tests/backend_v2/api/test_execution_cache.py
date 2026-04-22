from typing import Any
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from backend_v2.api.dependencies import get_arq_pool, get_current_user_from_header, get_repo
from backend_v2.main import app
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.state import TraceEvent
from backend_v2.models.v2_core import (
    ExecutionRecord,
    ExecutionStatus,
    RenderedSynthesisCache,
)
from backend_v2.api.routers.execution import executions
from backend_v2.services import execution


def mock_get_current_user_admin() -> Any:
    return TokenData(
        email="admin@test.com",
        id="usr_1111222233334444",
        role=UserRole.ADMIN,
        organization_id="org_1111222233334444",
    )


@pytest.fixture
def mock_repo_with_cache() -> Any:
    repo = AsyncMock()
    
    # 4. Execution Record
    mock_execution = ExecutionRecord(
        id="exe_1010101010101010",
        workflow_id="wf_1234567812345678",
        created_by="usr_1111222233334444",
        status=ExecutionStatus.COMPLETED,
        execution_trace=[],
        profile_syntheses={
            "prf_2233445566778899": RenderedSynthesisCache(
                synthesized_markdown="Global Executive Synthesis from worker.",
                section_syntheses={},
            )
        },
        metadata={"target_locale": "en"},
    )
    repo.get_execution.return_value = mock_execution
    
    # Needs a workflow
    repo.get_workflow_by_id.return_value = {
        "id": "wf_1234567812345678",
        "slug": "test_wf",
        "version": 1,
        "status": "published",
        "description": "Test WF Desc",
        "default_profile_id": "prf_2233445566778899",
        "name": {"default_locale": "en", "translations": {"en": "Test WF"}},
        "output_profiles": {
            "prf_2233445566778899": {
                "name": {"default_locale": "en", "translations": {"en": "desc"}},
                "layouts": []
            }
        },
        "steps": [],
    }
    
    return repo


@pytest.fixture
def test_client(mock_repo_with_cache: Any) -> Any:
    app.dependency_overrides[get_current_user_from_header] = mock_get_current_user_admin
    app.dependency_overrides[get_repo] = lambda: mock_repo_with_cache
    app.dependency_overrides[get_arq_pool] = lambda: AsyncMock()

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


def test_delete_profile_synthesis_clears_cache_and_pdf(test_client: Any) -> None:
    """Test that the cache clear endpoint successfully removes a profile synthesis and forces On-Demand Rendering."""
    execution_id = "exe_1010101010101010"
    profile_id = "prf_2233445566778899"
    
    # 1. Invalidate cache
    response = test_client.delete(
        f"/api/v2/execution/executions/{execution_id}/profiles/{profile_id}",
    )
    
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    
    # 2. Render JSON, the execution_service uses repo.get_execution which is mocked.
    # The delete modifies the mocked object in memory if we check what it was called with.
    # Actually, the repo mock `update_execution` was called!
    repo = app.dependency_overrides[get_repo]()
    repo.update_execution.assert_called_once()
    
    # The payload should have `prf_2233445566778899` deleted
    call_args = repo.update_execution.call_args[0]
    # call_args[0] = exe_id, call_args[1] = data
    payload = call_args[1]
    assert "profile_syntheses" in payload
    assert profile_id not in payload["profile_syntheses"]
