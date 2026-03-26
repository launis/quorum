from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from backend_v2.api.dependencies import get_current_user_from_header, get_studio_service
from backend_v2.main import app
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.services.studio import StudioService


def mock_get_current_user_admin():
    return TokenData(email="admin@test.com", id="usr_admin123", role=UserRole.ADMIN, organization_id="org_testorg123")

@pytest.fixture
def mock_studio_service_admin():
    service = AsyncMock(spec=StudioService)
    # The actual business logic doesn't matter, we want to test FastAPI request parsing boundaries
    # Return the first argument (which is the validated dictionary or workflow) so response_model succeeds safely.
    service.save_workflow.side_effect = lambda user, id, payload: payload
    service.save_prompt_block.side_effect = lambda user, id, payload: payload
    service.save_step.side_effect = lambda user, id, payload: payload
    return service

@pytest.fixture
def client_admin(mock_studio_service_admin):
    app.dependency_overrides[get_current_user_from_header] = mock_get_current_user_admin
    app.dependency_overrides[get_studio_service] = lambda: mock_studio_service_admin
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_workflow_api_fails_fast_on_invalid_model_strategy(client_admin):
    """Test that putting an invalid model strategy to the workflow root fails at the API boundary."""
    payload = {
        "id": "wf_valid1234567",
        "name": {"default_locale": "en", "translations": {"en": "Test WF"}},
        "description": {"default_locale": "en", "translations": {"en": "Desc"}},
        "slug": "valid_wf",
        "model_strategy": "super_mega_brain_5000", # INVALID ENUM!
        "steps": []
    }
    response = client_admin.put("/api/v2/studio/workflows/wf_valid1234567", json=payload)
    if response.status_code == 404:
         response = client_admin.put("/studio/workflows/wf_valid1234567", json=payload)

    # Should be 422 Unprocessable Entity by FastAPI due to Pydantic Enum validation
    assert response.status_code == 422
    assert "model_strategy" in response.text


def test_workflow_api_fails_fast_on_invalid_step_id(client_admin):
    """Test that providing an invalid Step ID pattern fails fast."""
    payload = {
        "id": "wf_valid1234567",
        "name": {"default_locale": "en", "translations": {"en": "Test WF"}},
        "description": {"default_locale": "en", "translations": {"en": "Desc"}},
        "slug": "valid_wf",
        "steps": [
            {
                "id": "BAD_ID_FORMAT", # INVALID FORMAT, violates regex
                "task_blueprint": "step_abc123456"
            }
        ]
    }
    response = client_admin.put("/api/v2/studio/workflows/wf_valid1234567", json=payload)
    if response.status_code == 404:
         response = client_admin.put("/studio/workflows/wf_valid1234567", json=payload)

    assert response.status_code == 422
    assert "steps" in response.text


def test_workflow_api_strips_illegal_step_attributes(client_admin, mock_studio_service_admin):
    """Test what the API lets through. We intentionally send pre_hooks and model_strategy
    inside the StepRule. Because of Epic 12 SSOT, Pydantic should strictly drop them 
    if extra='ignore' (default) or reject them if extra='forbid'. 
    Let's see if they survive into the validated payload.
    """
    payload = {
        "id": "wf_valid1234567",
        "name": {"default_locale": "en", "translations": {"en": "Test WF"}},
        "description": {"default_locale": "en", "translations": {"en": "Desc"}},
        "slug": "valid_wf",
        "steps": [
            {
                "id": "step_valid123456",
                "task_blueprint": "bp_test123",
                "depends_on": [],
                "input_mappings": {"doc": "123"},
                "pre_hooks": ["malicious_hook_that_should_be_dropped"], # ILLEGAL IN STEP RULE!
                "model_strategy": "sneaky_strategy"   # ILLEGAL IN STEP RULE!
            }
        ]
    }

    response = client_admin.put("/api/v2/studio/workflows/wf_valid1234567", json=payload)
    if response.status_code == 404:
        response = client_admin.put("/studio/workflows/wf_valid1234567", json=payload)

    assert response.status_code == 422, f"API unexpectedly accepted ILLEGAL properties or failed differently: {response.text}"

    # Assert that the reason was exactly because of extra_forbidden (Fail-Fast doctrine!)
    data = response.json()
    assert "extra_forbidden" in str(data), "Expected 'extra_forbidden' for pre_hooks and model_strategy."
    assert "pre_hooks" in str(data)
    assert "model_strategy" in str(data)

    # Ensure service was never executed (API effectively blocked it!)
    assert mock_studio_service_admin.save_workflow.called == False


def test_prompt_block_api_fails_fast_on_invalid_type(client_admin):
    """Test that PromptBlock API rejects invalid types (enums)."""
    payload = {
        "id": "blk_test123",
        "slug": "test_block",
        "name": {"default_locale": "en", "translations": {"en": "Test Block"}},
        "type": "illegal_type_enum", # ILLEGAL ENUM (e.g., BlockDataType)
        "content_template": {"default_locale": "en", "translations": {"en": "Content"}}
    }
    response = client_admin.put("/api/v2/studio/prompt-blocks/blk_test123", json=payload)
    if response.status_code == 404:
         response = client_admin.put("/studio/prompt-blocks/blk_test123", json=payload)

    assert response.status_code == 422
    assert "type" in response.text


def test_step_api_fails_fast_on_invalid_extra_attributes(client_admin):
    """Test that Blueprint (Step) API forbids random extra fields leaking into storage."""
    payload = {
        "id": "step_valid_blueprint",
        "slug": "valid_bp",
        "name": {"default_locale": "en", "translations": {"en": "Test BP"}},
        "type": "llm",
        "execution_logic": "Execute this.",
        "prompt_blocks": ["blk_123"],
        "unexpected_garbage_property": "This should kill the request" # ILLEGAL EXTRA
    }
    response = client_admin.put("/api/v2/studio/steps/step_valid_blueprint", json=payload)
    if response.status_code == 404:
         response = client_admin.put("/studio/steps/step_valid_blueprint", json=payload)

    assert response.status_code == 422
    assert "extra_forbidden" in response.text
    assert "unexpected_garbage_property" in response.text


def test_workflow_api_fails_fast_on_orphan_dependency(client_admin):
    """Test that a Workflow with a dependency pointing to a missing step is outright rejected."""
    payload = {
        "id": "wf_valid1234567",
        "name": {"default_locale": "en", "translations": {"en": "Test WF"}},
        "description": {"default_locale": "en", "translations": {"en": "Desc"}},
        "slug": "valid_wf",
        "steps": [
            {
                "id": "blk_step1234",
                "task_blueprint": "step_valid",
                "depends_on": ["blk_missing1"] # ORPHAN REFERENCE!
            }
        ]
    }
    response = client_admin.put("/api/v2/studio/workflows/wf_valid1234567", json=payload)
    if response.status_code == 404:
         response = client_admin.put("/studio/workflows/wf_valid1234567", json=payload)

    assert response.status_code == 422
    assert "does not exist in this workflow" in response.text


def test_workflow_api_fails_fast_on_cyclic_dependency(client_admin):
    """Test that a Workflow with A -> B -> A cyclical dependencies is outright rejected."""
    payload = {
        "id": "wf_valid1234567",
        "name": {"default_locale": "en", "translations": {"en": "Test WF"}},
        "description": {"default_locale": "en", "translations": {"en": "Desc"}},
        "slug": "valid_wf",
        "steps": [
            {
                "id": "blk_aaaaaaaa",
                "task_blueprint": "step_a_valid1",
                "depends_on": ["blk_bbbbbbbb"] # A depends on B
            },
            {
                "id": "blk_bbbbbbbb",
                "task_blueprint": "step_b_valid2",
                "depends_on": ["blk_aaaaaaaa"] # B depends on A (CYCLE!)
            }
        ]
    }
    response = client_admin.put("/api/v2/studio/workflows/wf_valid1234567", json=payload)
    if response.status_code == 404:
         response = client_admin.put("/studio/workflows/wf_valid1234567", json=payload)

    assert response.status_code == 422
    assert "Circular dependency" in response.text


def test_workflow_api_succeeds_with_valid_data(client_admin, mock_studio_service_admin):
    """Test the happy path: a valid Workflow DAG saves successfully passing all strict Pydantic locks."""
    payload = {
        "id": "wf_valid1234567",
        "name": {"default_locale": "en", "translations": {"en": "Happy Path WF"}},
        "description": {"default_locale": "en", "translations": {"en": "Desc"}},
        "slug": "happy_path_wf",
        "model_strategy": "fast", # VALID strategy
        "steps": [
            {
                "id": "blk_aaaa1111",
                "task_blueprint": "step_valid_a",
                "depends_on": [] # Root Node
            },
            {
                "id": "blk_bbbb2222",
                "task_blueprint": "step_valid_b",
                "depends_on": ["blk_aaaa1111"] # B depends on A
            },
            {
                "id": "blk_cccc3333",
                "task_blueprint": "step_valid_c",
                "depends_on": ["blk_aaaa1111", "blk_bbbb2222"] # C depends on A and B (Valid DAG)
            }
        ]
    }

    response = client_admin.put("/api/v2/studio/workflows/wf_valid1234567", json=payload)
    if response.status_code == 404:
         response = client_admin.put("/studio/workflows/wf_valid1234567", json=payload)

    assert response.status_code == 200, f"API unexpectedly rejected valid configuration: {response.text}"

    # Assert that the mocked save_workflow was actually executed
    assert mock_studio_service_admin.save_workflow.called == True

