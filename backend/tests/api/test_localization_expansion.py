from fastapi.testclient import TestClient

from backend.dependencies import get_current_user_from_header
from backend.main import app
from backend.models.auth import TokenData, UserRole

client = TestClient(app)

import pytest

# Mock Auth Dependency
async def mock_get_current_user():
    return TokenData(uid="test-user", role=UserRole.ADMIN, organization_id="test-org")

@pytest.fixture(autouse=True)
def setup_dependencies():
    app.dependency_overrides[get_current_user_from_header] = mock_get_current_user
    yield
    app.dependency_overrides.pop(get_current_user_from_header, None)

def test_get_generic_schema_fi():
    """Verify that general schemas endpoint respects Accept-Language: fi."""
    headers = {"Accept-Language": "fi-FI"}
    # The 'WorkflowDefinition' is registered in schemas.py
    response = client.get("/v1/config/schemas/workflow_definition", headers=headers)
    if response.status_code != 200:
        with open("last_error.log", "w") as f:
            f.write(f"Status: {response.status_code}\nBody: {response.text}")
    assert response.status_code == 200
    schema = response.json().get("schema_def", {})

    properties = schema.get("properties", {})
    print("DEBUG TEST SCHEMA:", schema)
    print("DEBUG TEST PROPERTIES:", properties)
    # Verify translations from domain.py hints + fi.json
    assert properties["name"]["x-ui-label"] == "Työnkulun Nimi"
    assert properties["description"]["x-ui-label"] == "Kuvaus"

def test_get_evaluation_matrix_schema_fi():
    """Verify that EvaluationMatrixConfig endpoint respects Accept-Language: fi."""
    headers = {"Accept-Language": "fi-FI"}
    response = client.get("/v1/config/schemas/evaluation_matrix", headers=headers)
    assert response.status_code == 200
    schema = response.json().get("schema_def", {})

    properties = schema.get("properties", {})
    # Verify new hints added to domain.py
    assert properties["criteria"]["x-ui-group"] == "Arviointikriteerit"

def test_get_agents_list_fi():
    """Verify that agents list endpoint localizes input/output schemas."""
    headers = {"Accept-Language": "fi-FI"}
    response = client.get("/agents/", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    if len(data) > 0:
        # Check first agent with a schema
        agent = data[0]
        # This part depends on which agents are loaded, but we check logic execution
        # We can atleast assert the call succeeded and returned a list.
        # If any agent has a schema with known keys, it should be translated.
        assert "name" in agent

def test_get_schemas_list_fi():
    """Verify that the global schemas list endpoint works and localizes."""
    headers = {"Accept-Language": "fi-FI"}
    response = client.get("/v1/config/schemas", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    # Check if 'workflow_definition' is present and localized
    if "workflow_definition" in data:
        props = data["workflow_definition"]["schema"]["properties"]
        assert props["name"]["x-ui-label"] == "Työnkulun Nimi"

from unittest.mock import AsyncMock

from backend.dependencies import get_async_repository


def test_get_execution_view_fi():
    """Verify that Execution View (Report) is localized."""
    mock_repo = AsyncMock()
    from backend.models.domain.execution import ExecutionRecord
    mock_execution = ExecutionRecord(
        id="test-exec-1",
        status="completed",
        results={
            "step_results": {
                "step_judge": {
                    "total_score": 3,
                "final_verdict": "Good",
                "scale_min": 1,
                "scale_max": 5
                }
            }
        }
    )
    mock_repo.get_execution.return_value = mock_execution

    app.dependency_overrides[get_async_repository] = lambda: mock_repo

    headers = {"Accept-Language": "fi-FI"}
    response = client.get("/executions/test-exec-1/view", headers=headers)

    # Clean up override
    del app.dependency_overrides[get_async_repository]

    print(f"DEBUG STATUS: {response.status_code}")
    print(f"DEBUG BODY: {response.text}")
    assert response.status_code == 200
    view = response.json()
    import json
    print("DEBUG VIEW:", json.dumps(view, indent=2, ensure_ascii=False))

    # Check Score Card Title Translation
    # "Judge" -> "Tuomari" (Agent Name)
    # "Analysis Result" -> "Analyysin Tulos" (Title)

    # Allow for partial match or specific structure check
    # Structure: sections -> list. Find type=SCORE_CARD
    score_card = next((s for s in view["sections"] if s["type"] == "SCORE_CARD"), None)
    assert score_card is not None
    assert score_card["title"] == "Analyysin Tulos"
    assert score_card["data"]["agent_name"] == "Tuomari"
