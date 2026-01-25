
from fastapi.testclient import TestClient

from backend.dependencies import get_current_user_from_header
from backend.main import app
from backend.models.auth import TokenData, UserRole

client = TestClient(app)

# Mock Auth Dependency
async def mock_get_current_user():
    return TokenData(uid="test-user", role=UserRole.ADMIN, organization_id="test-org")

app.dependency_overrides[get_current_user_from_header] = mock_get_current_user

def test_get_workflow_schema():
    """Verify that the WorkflowDefinition schema is returned with SDUI hints (Default English)."""
    response = client.get("/builder/schema/workflow")
    assert response.status_code == 200
    schema = response.json()

    properties = schema.get("properties", {})

    # Verify Default English Labels
    assert properties["name"]["x-ui-label"] == "Workflow Name"
    assert properties["description"]["x-ui-label"] == "Description"
    assert properties["steps"]["x-ui-group"] == "Steps"

def test_get_workflow_schema_fi():
    """Verify that the WorkflowDefinition schema respects Accept-Language: fi."""
    headers = {"Accept-Language": "fi-FI"}
    response = client.get("/builder/schema/workflow", headers=headers)
    assert response.status_code == 200
    schema = response.json()

    properties = schema.get("properties", {})

    # Verify Finnish Labels
    assert properties["name"]["x-ui-label"] == "Työnkulun Nimi"
    assert properties["description"]["x-ui-label"] == "Kuvaus"
    assert properties["steps"]["x-ui-group"] == "Vaiheet"

def test_invalid_component_schema():
    """Verify 404 for unknown components."""
    response = client.get("/builder/schema/invalid_component_xyz")
    assert response.status_code == 404

    error_data = response.json()
    assert error_data["status"] == 404
    assert "component-schema-not-found" in error_data["type"]
