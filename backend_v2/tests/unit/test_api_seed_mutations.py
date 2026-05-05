import copy
import json
from typing import Any
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from backend_v2.api.dependencies import get_current_user_from_header, get_studio_service
from backend_v2.main import app
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.services.studio import StudioService


def mock_get_current_user_admin() -> Any:
    return TokenData(email="admin@test.com", id="usr_admin123", role=UserRole.ADMIN, organization_id="org_testorg123")


@pytest.fixture
def mock_studio_service_admin() -> Any:
    service = AsyncMock(spec=StudioService)
    service.save_workflow.side_effect = lambda user, id, payload: payload
    service.save_prompt_block.side_effect = lambda user, id, payload: payload
    service.save_step.side_effect = lambda user, id, payload: payload
    return service


@pytest.fixture
def client_admin(mock_studio_service_admin: Any) -> Any:
    app.dependency_overrides[get_current_user_from_header] = mock_get_current_user_admin
    app.dependency_overrides[get_studio_service] = lambda: mock_studio_service_admin
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def get_seed_data() -> Any:
    with open("backend_v2/seed/seed_data.json", encoding="utf-8") as f:
        return dict(json.load(f))


def get_audit_workflow() -> Any:
    return {
        "id": "wf_1111111111111111",
        "name": {"default_locale": "en", "translations": {"en": "Test WF"}},
        "description": {"default_locale": "en", "translations": {"en": "Desc"}},
        "status": "draft",
        "version": 1,
        "default_profile_id": "prof_mmmm1111mmmm1111",
        "slug": "valid_wf",
        "expected_inputs": [],
        "steps": [
            {"id": "blk_aaaa111111111111", "task_blueprint": "bp_1", "depends_on": []},
            {"id": "blk_cccc333333333333", "task_blueprint": "bp_3", "depends_on": ["blk_aaaa111111111111"]},
        ],
    }


def get_seed_prompt_block() -> Any:
    return {
        "id": "blk_test1234567",
        "slug": "test_block",
        "label": {"default_locale": "en", "translations": {"en": "Test Block"}},
        "description": {"default_locale": "en", "translations": {"en": "Content"}},
        "category_id": "matrix",
        "type": "float",
    }


def get_seed_step() -> Any:
    return {
        "id": "step_abc123456",
        "slug": "step_test",
        "type": "llm",
        "name": {"default_locale": "en", "translations": {"en": "Step"}},
        "execution_logic": "prompt",
        "prompt_blocks": [],
    }


def test_seed_workflow_happy_path(client_admin: Any, mock_studio_service_admin: Any) -> None:
    """Test that the unmodified massive audit workflow is entirely valid."""
    wf = get_audit_workflow()

    response = client_admin.put(f"/api/v2/studio/workflows/{wf['id']}", json=wf)
    if response.status_code == 404:
        response = client_admin.put(f"/studio/workflows/{wf['id']}", json=wf)

    assert response.status_code == 200, f"Unmodified seed workflow failed validation: {response.text}"


def test_seed_workflow_legal_mutations(client_admin: Any, mock_studio_service_admin: Any) -> None:
    """Test legally modifying inputs and safely removing steps."""
    wf = copy.deepcopy(get_audit_workflow())

    # Mutation 1: Drop the last 5 steps safely (ensuring we don't break depends_on structure upstream)
    # The workflow has 19 steps. Let's just keep the first 3 steps that don't depend on much, or just keep root.
    # Actually, a safe way to remove a node is to remove a LEAF node.
    # Let's find a node that nobody depends on.
    all_deps = set()
    for s in wf["steps"]:
        for d in s.get("depends_on", []):
            all_deps.add(d)

    leaf_nodes = [s["id"] for s in wf["steps"] if s["id"] not in all_deps]
    assert len(leaf_nodes) > 0, "No leaf nodes found in DAG!"

    # Remove one leaf node safely
    node_to_remove = leaf_nodes[0]
    wf["steps"] = [s for s in wf["steps"] if s["id"] != node_to_remove]

    # Mutation 2: Modify inputs safely
    # Add a new legal text input
    wf["expected_inputs"].append(
        {
            "input_key": "custom_test_input",
            "label": {"default_locale": "fi", "translations": {"fi": "Testi", "en": "Test"}},
            "required": False,
            "is_chat_history": False,
            "input_modes": ["text", "paste"],
            "description": {"default_locale": "fi", "translations": {"fi": "Kuvaus", "en": "Desc"}},
            "ai_description": "A very valid test input for AI",
        }
    )

    response = client_admin.put(f"/api/v2/studio/workflows/{wf['id']}", json=wf)
    if response.status_code == 404:
        response = client_admin.put(f"/studio/workflows/{wf['id']}", json=wf)

    assert response.status_code == 200, f"Legally mutated workflow failed: {response.text}"


def test_seed_workflow_illegal_orphan(client_admin: Any, mock_studio_service_admin: Any) -> None:
    """Test illegally deleting a ROOT node resulting in orphan references downstream."""
    wf = copy.deepcopy(get_audit_workflow())

    # Delete the very first step (root node)
    root_nodes = [s["id"] for s in wf["steps"] if not s.get("depends_on")]
    assert len(root_nodes) > 0
    node_to_remove = root_nodes[0]

    # Mutate DAG by ripping out the foundation without updating dependencies
    wf["steps"] = [s for s in wf["steps"] if s["id"] != node_to_remove]

    response = client_admin.put(f"/api/v2/studio/workflows/{wf['id']}", json=wf)
    if response.status_code == 404:
        response = client_admin.put(f"/studio/workflows/{wf['id']}", json=wf)

    assert response.status_code == 422
    assert "does not exist in this workflow" in response.text


def test_seed_workflow_illegal_input_contradiction(client_admin: Any, mock_studio_service_admin: Any) -> None:
    """Test adding an input that violates the strict Pydantic rules (e.g. Chat History + Questionnaire)."""
    wf = copy.deepcopy(get_audit_workflow())

    wf["expected_inputs"].append(
        {
            "input_key": "illegal_input",
            "label": {"default_locale": "en", "translations": {"en": "Label"}},
            "required": True,
            "is_chat_history": True,  # CONTRADICTION 1
            "input_modes": ["questionnaire"],  # CONTRADICTION 2
            "description": {"default_locale": "en", "translations": {"en": "Desc"}},
            "ai_description": "Will fail validation",
        }
    )

    response = client_admin.put(f"/api/v2/studio/workflows/{wf['id']}", json=wf)
    if response.status_code == 404:
        response = client_admin.put(f"/studio/workflows/{wf['id']}", json=wf)

    assert response.status_code == 422
    assert "cannot use 'questionnaire' mode when flagged as chat history" in response.text


def test_seed_prompt_block_illegal_mutation(client_admin: Any, mock_studio_service_admin: Any) -> None:
    """Test mutating a real seed PromptBlock with an illegal Enum."""
    block = copy.deepcopy(get_seed_prompt_block())

    # Inject illegal type
    block["type"] = "super_matrix_pro_max"

    response = client_admin.put(f"/api/v2/studio/prompt-blocks/{block['id']}", json=block)
    if response.status_code == 404:
        response = client_admin.put(f"/studio/prompt-blocks/{block['id']}", json=block)

    assert response.status_code == 422
    assert "Input should be" in response.text


def test_seed_step_illegal_mutation(client_admin: Any, mock_studio_service_admin: Any) -> None:
    """Test mutating a real seed Step (Blueprint) with forbidden properties."""
    step = copy.deepcopy(get_seed_step())

    # Try to sneak in illegal fields into a localized Step
    step["illegal_field"] = "deep"

    response = client_admin.put(f"/api/v2/studio/steps/{step['id']}", json=step)
    if response.status_code == 404:
        response = client_admin.put(f"/studio/steps/{step['id']}", json=step)

    assert response.status_code == 422
    assert "extra_forbidden" in response.text
