from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from backend_v2.api.dependencies import get_current_user_from_header, get_studio_service
from backend_v2.main import app
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.v2_core import (
    PromptBlock,
    Step,
    SystemConfigMCPGateways,
    SystemConfigModelRegistry,
    Workflow,
)
from backend_v2.services.studio import StudioService


def mock_get_current_user_admin():
    return TokenData(
        email="admin@test.com",
        id="usr_admin123",
        role=UserRole.ADMIN,
        organization_id="org_testorg123",
    )


def mock_get_current_user_root():
    return TokenData(
        email="root@test.com",
        id="usr_root999",
        role=UserRole.ROOT,
        organization_id="org_testorg123",
    )


@pytest.fixture
def mock_studio_service():
    service = AsyncMock(spec=StudioService)
    # Configure mock returns for cloning
    service.clone_workflow.return_value = Workflow(
        id="wf_clone12345678",
        slug="test_wf_clone",
        name={"default_locale": "en", "translations": {"en": "Workflow (Copy)"}},
        description="test",
    )
    service.clone_step.return_value = Step(
        id="step_clone12345678",
        slug="test_step_clone",
        name={"default_locale": "en", "translations": {"en": "Step (Copy)"}},
        type="llm",
        model_strategy="fast",
        prompt_blocks=["block1"],
    )
    service.clone_prompt_block.return_value = PromptBlock(
        id="blk_clone12345678",
        slug="test_block_clone",
        label={"default_locale": "en", "translations": {"en": "Block (Copy)"}},
        description={"default_locale": "en", "translations": {"en": "desc"}},
        category_id="test",
        type="string",
    )
    service.clone_system_config.return_value = SystemConfigModelRegistry(
        id="sys_clone12345678",
        slug="test_sys_clone",
        type="model_registry",
        models={},
    )
    service.clone_mcp_gateways.return_value = SystemConfigMCPGateways(
        id="mcp_clone12345678",
        slug="test_mcp_clone",
        type="mcp_gateways",
        tools=[],
    )
    service.clone_output_profile.return_value = OutputProfile(
        id="prof_clone12345678",
        slug="test_prof_clone",
        workflow_id="wf_clone12345678",
        name={"default_locale": "en", "translations": {"en": "Profile (Copy)"}},
        layouts=[],
    )
    return service


@pytest.fixture
def client_admin(mock_studio_service):
    app.dependency_overrides[get_current_user_from_header] = mock_get_current_user_admin
    app.dependency_overrides[get_studio_service] = lambda: mock_studio_service
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def client_root(mock_studio_service):
    app.dependency_overrides[get_current_user_from_header] = mock_get_current_user_root
    app.dependency_overrides[get_studio_service] = lambda: mock_studio_service
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# --- Tests ---


def test_clone_workflow_endpoint(client_admin, mock_studio_service):
    response = client_admin.post("/api/v2/studio/workflows/wf_12345/clone")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "wf_clone12345678"
    mock_studio_service.clone_workflow.assert_called_once()


def test_clone_step_endpoint(client_admin, mock_studio_service):
    response = client_admin.post("/api/v2/studio/steps/step_12345/clone")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "step_clone12345678"
    mock_studio_service.clone_step.assert_called_once()


def test_clone_prompt_block_endpoint(client_admin, mock_studio_service):
    response = client_admin.post("/api/v2/studio/prompt-blocks/blk_12345/clone")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "blk_clone12345678"
    mock_studio_service.clone_prompt_block.assert_called_once()


def test_clone_model_registry_endpoint(client_root, mock_studio_service):
    # System Configs require ROOT role
    response = client_root.post("/api/v2/studio/model-registry/sys_12345/clone")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "sys_clone12345678"
    mock_studio_service.clone_system_config.assert_called_once()


def test_clone_mcp_gateways_endpoint(client_root, mock_studio_service):
    # MCP Gateways require ROOT role
    response = client_root.post("/api/v2/studio/mcp-gateways/mcp_12345/clone")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "mcp_clone12345678"
    mock_studio_service.clone_mcp_gateways.assert_called_once()


def test_clone_output_profile_endpoint(client_admin, mock_studio_service):
    response = client_admin.post("/api/v2/output-profiles/prof_12345/clone")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "prof_clone12345678"
    mock_studio_service.clone_output_profile.assert_called_once()
