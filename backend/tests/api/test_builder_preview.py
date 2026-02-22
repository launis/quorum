from fastapi.testclient import TestClient
import backend.worker  # noqa: F401
from backend.dependencies import get_current_user_from_header
from backend.main import app
from backend.models.auth import TokenData, UserRole

client = TestClient(app)

import pytest


# Mock Auth
async def mock_get_current_user():
    return TokenData(uid="test-user", role=UserRole.ADMIN, organization_id="test-org")


@pytest.fixture(autouse=True)
def setup_dependencies():
    app.dependency_overrides[get_current_user_from_header] = mock_get_current_user
    yield
    app.dependency_overrides.pop(get_current_user_from_header, None)


def test_preview_step_flow():
    """Test creating a step and then previewing it."""
    # 1. Create a Step
    # We might need to use the repository directly or a route.
    # Current codebase might not have a public create-step route exposed for generic steps easily without auth?
    # Actually, let's use the create endpoint if available, otherwise direct repo injection is harder in functional tests without setup.
    # Looking at steps.py, there is `create_custom_step` and `clone_step`, but plain `create_step` might be missing or in another router?
    # Wait, `backend/api/routes/builder/steps.py` doesn't show a generic `create_step` endpoint!
    # It only has `list`, `get`, `update`, `clone`, `create_custom`.

    # So we should use `create_custom_step`.
    create_payload = {"component_type": "judge", "name_hint": "Preview Test Judge"}
    create_res = client.post("/builder/steps/create-custom", json=create_payload)
    assert create_res.status_code == 200, f"Setup Failed: {create_res.text}"
    step_data = create_res.json()
    step_id = step_data["id"]

    # 2. Preview Step
    preview_res = client.post(f"/builder/steps/{step_id}/preview", headers={"Accept-Language": "en-US"})
    assert preview_res.status_code == 200
    preview_data = preview_res.json()

    assert "system_instruction" in preview_data
    assert "user_prompt" in preview_data
    assert "Judge" in preview_data["agent_class"] or "Unknown" in preview_data["agent_class"]


def test_preview_chain_flow():
    """Test creating a workflow and previewing the chain."""
    # 1. Create Steps
    s1_res = client.post("/builder/steps/create-custom", json={"component_type": "judge", "name_hint": "S1"})
    s1_id = s1_res.json()["id"]

    s2_res = client.post("/builder/steps/create-custom", json={"component_type": "reporter", "name_hint": "S2"})
    s2_id = s2_res.json()["id"]

    # 2. Create Workflow
    wf_payload = {
        "name": "Chain Test",
        "description": "A workflow chain for testing.",
        "organization_id": "test-org",
        "steps": [s1_id, s2_id],
        "default_model_mapping": {s1_id: "test-model", s2_id: "test-model"},
    }
    wf_res = client.post("/builder/workflows", json=wf_payload)
    assert wf_res.status_code == 200, f"Workflow Setup Failed: {wf_res.text}"
    wf_id = wf_res.json()["id"]

    # 3. Preview Chain
    chain_res = client.get(f"/builder/workflows/{wf_id}/chain-preview")
    assert chain_res.status_code == 200
    chain_data = chain_res.json()

    assert "markdown_content" in chain_data
    content = chain_data["markdown_content"]

    # Verify Structural integrity
    assert f"ID: {wf_id}" in content
    assert "## Step 1:" in content
    assert "S1" in content
    assert "judge" in content.lower() or "unknown" in content.lower()
    assert "## Step 2:" in content
    assert "S2" in content
    assert "reporter" in content.lower() or "unknown" in content.lower()


def test_preview_not_found():
    res = client.post("/builder/steps/non_existent_step/preview")
    assert res.status_code == 404
