
import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi.testclient import TestClient
from backend.main import app
from backend.dependencies import get_repository_dep, get_current_user_from_header
from backend.models.auth import TokenData, UserRole

client = TestClient(app)

# Mock User
async def mock_get_current_user():
    return TokenData(uid="test-root", role=UserRole.ROOT, organization_id="system")

# Mock Repository
mock_repo = MagicMock()

def override_dependencies():
    app.dependency_overrides[get_current_user_from_header] = mock_get_current_user
    app.dependency_overrides[get_repository_dep] = lambda: mock_repo

def clear_dependencies():
    app.dependency_overrides = {}

@pytest.fixture(autouse=True)
def setup_teardown():
    override_dependencies()
    yield
    clear_dependencies()

def test_create_workflow_missing_mapping():
    """Test that creating a workflow with missing model mapping returns 400."""
    # Setup
    mock_repo.create_workflow = AsyncMock()
    mock_repo.get_step_by_id = AsyncMock(return_value={"id": "step_1", "name": "Step 1"})

    payload = {
        "id": "wf_test",
        "name": "Test Workflow",
        "steps": ["step_1", "step_2"],
        "default_model_mapping": {
            "step_1": "fast"
            # Missing step_2
        }
    }

    response = client.post("/builder/workflows", json=payload)

    assert response.status_code == 400
    data = response.json()
    assert "Missing model mapping" in data["detail"]
    assert "step_2" in data["detail"]

def test_update_workflow_missing_mapping():
    """Test that updating a workflow with missing model mapping returns 400."""
    # Setup
    mock_repo.get_workflow_by_id = AsyncMock(return_value={
        "id": "wf_test",
        "organization_id": "system",
        "steps": ["step_1"],
        "default_model_mapping": {"step_1": "fast"}
    })
    mock_repo.update_workflow = AsyncMock()

    # Update adds step_2 but forgets mapping
    payload = {
        "steps": ["step_1", "step_2"],
        "default_model_mapping": {
            "step_1": "fast"
        }
    }

    response = client.put("/builder/workflows/wf_test", json=payload)

    assert response.status_code == 400
    data = response.json()
    assert "Missing model mapping" in data["detail"]
    assert "step_2" in data["detail"]
