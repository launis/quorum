import json
import pytest
from typing import Any
from httpx import ASGITransport, AsyncClient

from backend_v2.api.dependencies import get_current_user_from_header, ExecutionServiceDep, get_execution_service, get_repo
from backend_v2.exceptions import ErrorCodes
from backend_v2.main import app
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.v2_core import ExecutionRecord, ExecutionStatus

async def mock_current_user() -> TokenData:
    return TokenData(id="usr_test123", email="test@test.com", role=UserRole.ADMIN, organization_id="org_test")

@pytest.fixture(autouse=True)
def mock_auth_verify(monkeypatch: pytest.MonkeyPatch) -> None:
    async def mock_verify_async(self: Any, token: str) -> dict[str, Any]:
        return {"uid": "usr_test123", "email": "test@test.com", "firebase": {"sign_in_provider": "password"}}
    monkeypatch.setattr("backend_v2.services.auth.AuthService.verify_token", mock_verify_async)

app.dependency_overrides[get_current_user_from_header] = mock_current_user

# Setup standard headers
MOCK_HEADERS = {
    "Authorization": "Bearer test-admin-token",
    "X-User-ID": "usr_test123",
    "X-Organization-ID": "org_test",
}

@pytest.fixture
def mock_trace_data():
    return {
        "blk_test1_scaled": 5.0,
        "blk_test1_normalized": 100.0,
        "blk_test1_true_atoms": 5,
        "blk_test1_total_atoms": 5,
        "blk_test1_false_atoms": 0,
        "blk_test1_justification": "Taso 1 vaikuttaa hyvältä.",
        "blk_test1_missing_context": "",
        "blk_test1_level_breakdown": {
            "1.0": {"hits": 5, "total": 5}
        },
        "blk_info99_scaled": 2.0,
        "blk_info99_normalized": None,
        "blk_info99_true_atoms": 1,
        "blk_info99_total_atoms": 5,
        "blk_info99_false_atoms": 4,
        "blk_info99_justification": "Tämä on vain infoa.",
        "blk_info99_missing_context": "Puutteita.",
        "blk_info99_level_breakdown": {
            "1.0": {"hits": 1, "total": 5}
        }
    }


@pytest.mark.asyncio
async def test_scorecard_api_parses_dina_breakdown(monkeypatch, mock_trace_data):
    """Positive test: Scorecard API correctly computes flat arrays including level_breakdown."""
    
    mock_exe_record = ExecutionRecord(
        id="exe_a1b2c3d4e5f60000",
        workflow_id="wf_a1b2c3d4e5f60000",
        status=ExecutionStatus.COMPLETED,
        execution_trace_storage_path="mock/path/file.json",
        organization_id="org_test"
    )
    
    class MockExecutionService:
        async def get_execution(self, *args, **kwargs):
            return mock_exe_record
            
    app.dependency_overrides[ExecutionServiceDep.__metadata__[0].dependency] = lambda: MockExecutionService()
    
    class MockStorage:
        async def read(self, path):
            return json.dumps(mock_trace_data).encode("utf-8")
            
    monkeypatch.setattr("backend_v2.services.storage.get_storage_driver", lambda: MockStorage())
    
    class MockRepo:
        async def get_workflow_by_id(self, *args, **kwargs):
            return {"id": "wf_a1b2c3d4e5f60000", "steps": [{"task_blueprint": "step_mock"}]}
        async def get_step_by_id(self, *args, **kwargs):
            return {"id": "step_mock", "prompt_blocks": ["blk_test1", "blk_info99"]}
        async def get_prompt_block_by_id(self, pb_id):
            if pb_id == "blk_test1":
                return {"id": "blk_test1", "category_id": "matrix", "is_evaluative": True, "label": {"translations": {"fi": "Testi Matriisi"}}, "scales": [{"score": 5.0}]}
            return {"id": "blk_info99", "category_id": "matrix", "is_evaluative": False, "label": {"translations": {"fi": "Info Matriisi"}}}
            
        async def get_user(self, id: str):
            from backend_v2.models.auth import UserRole
            import datetime
            return {
                "id": "usr_testadmin123",
                "email": "test@example.com",
                "role": UserRole.ADMIN,
                "organization_id": "org_test",
                "is_active": True,
                "language": "fi",
                "theme_mode": "system",
                "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            }

    from backend_v2.api.dependencies import get_repo
    app.dependency_overrides[get_repo] = lambda: MockRepo()
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v2/execution/scorecard/exe_a1b2c3d4e5f60000", headers=MOCK_HEADERS)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert data["execution_id"] == "exe_a1b2c3d4e5f60000"
        assert data["global_average"] == 100.0
        
        eval_matrices = data["evaluative_matrices"]
        assert len(eval_matrices) == 1
        assert eval_matrices[0]["block_id"] == "blk_test1"
        assert eval_matrices[0]["label_fi"] == "Testi Matriisi"
        assert eval_matrices[0]["scale_max"] == 5.0
        assert eval_matrices[0]["normalized_score"] == 100.0
        assert eval_matrices[0]["level_breakdown"] == {"1.0": {"hits": 5, "total": 5}}

        info_matrices = data["informational_matrices"]
        assert len(info_matrices) == 1
        assert info_matrices[0]["block_id"] == "blk_info99"
        assert info_matrices[0]["is_evaluative"] is False


@pytest.mark.asyncio
async def test_scorecard_api_fails_fast_on_missing_trace(monkeypatch, mock_trace_data):
    """Negative test: Scorecard API throws ErrorCodes.RESOURCE_NOT_FOUND (HTTP 404) if trace path is missing."""
    mock_exe_record = ExecutionRecord(
        id="exe_a1b2c3d4e5f60000",
        workflow_id="wf_a1b2c3d4e5f60000",
        status=ExecutionStatus.COMPLETED,
        execution_trace_storage_path=None,  # MISSING
        organization_id="org_test"
    )
    
    class MockExecutionServiceFailFast:
        async def get_execution(self, *args, **kwargs):
            return mock_exe_record
            
    app.dependency_overrides[get_execution_service] = lambda: MockExecutionServiceFailFast()
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v2/execution/scorecard/exe_a1b2c3d4e5f60000", headers=MOCK_HEADERS)
        
        assert response.status_code == 404
        data = response.json()
        assert data["extensions"]["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value
