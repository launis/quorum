import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

from backend_v2.main import app
from backend_v2.api.dependencies import get_current_user_from_header, get_studio_service
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.v2_core import PromptBlock, I18nText, BlockDataType
from backend_v2.services.studio import StudioService

# Mock Dependencies
async def override_get_current_user():
    return TokenData(email="test@test.com", id="user123", role=UserRole.ROOT, organization_id="test_org")

@pytest.fixture
def mock_studio_service():
    service = AsyncMock(spec=StudioService)
    # Configure mock responses
    pb = PromptBlock(
        id="mock_pb_1",
        label=I18nText(default_locale="en", translations={"en": "Test Label"}),
        description=I18nText(default_locale="en", translations={"en": "Test Desc"}),
        category_id="test_cat",
        type=BlockDataType.STRING,
        strictness_level=50,
        require_justification=False
    )
    service.list_prompt_blocks.return_value = [pb]
    service.get_prompt_block.return_value = pb
    service.save_prompt_block.return_value = pb
    service.delete_prompt_block.return_value = None
    return service

@pytest.fixture
def client(mock_studio_service):
    app.dependency_overrides[get_current_user_from_header] = override_get_current_user
    app.dependency_overrides[get_studio_service] = lambda: mock_studio_service
    yield TestClient(app)
    app.dependency_overrides.clear()

def test_get_prompt_blocks(client, mock_studio_service):
    response = client.get("/api/v2/studio/prompt-blocks") # Default API prefix pattern
    if response.status_code == 404:
         response = client.get("/studio/prompt-blocks") # Fallback pattern
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == "mock_pb_1"
    mock_studio_service.list_prompt_blocks.assert_called_once()

def test_delete_prompt_block(client, mock_studio_service):
    response = client.delete("/api/v2/studio/prompt-blocks/mock_pb_1")
    if response.status_code == 404:
         response = client.delete("/studio/prompt-blocks/mock_pb_1")
    assert response.status_code == 200
    assert response.json()["deleted_id"] == "mock_pb_1"
    mock_studio_service.delete_prompt_block.assert_called_once()
