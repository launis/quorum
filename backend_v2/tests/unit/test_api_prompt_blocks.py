from typing import Any
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from backend_v2.api.dependencies import (
    get_current_user_from_header,
    get_studio_output_profile_service,
    get_studio_prompt_block_service,
    get_studio_simulation_service,
    get_studio_workflow_service,
)
from backend_v2.main import app
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.domain.prompt_blocks import PromptBlock
from backend_v2.models.enums import PromptBlockCategory
from backend_v2.models.v2_core import BlockDataType, I18nText


# Mock Dependencies
async def override_get_current_user() -> Any:
    return TokenData(email="test@test.com", id="usr_12345678", role=UserRole.ROOT, organization_id="org_testorg123")


@pytest.fixture
def mock_studio_service() -> Any:
    service = AsyncMock()
    # Configure mock responses
    pb = PromptBlock(
        id="blk_ffff6666ffff6666",
        slug="mock_pb_1",
        label=I18nText(default_locale="en", translations={"en": "Test Label", "fi": "Test Label"}),
        description=I18nText(default_locale="en", translations={"en": "Test Desc", "fi": "Test Desc"}),
        category_id=PromptBlockCategory.SYSTEM_RULE,
        type=BlockDataType.STRING,
        output_extensions=[],
    )
    service.list_prompt_blocks.return_value = [pb]
    service.get_prompt_block.return_value = pb
    service.save_prompt_block.return_value = pb
    service.delete_prompt_block.return_value = None
    return service


@pytest.fixture
def client(mock_studio_service: Any) -> Any:
    app.dependency_overrides[get_current_user_from_header] = override_get_current_user
    app.dependency_overrides[get_studio_simulation_service] = lambda: mock_studio_service
    app.dependency_overrides[get_studio_workflow_service] = lambda: mock_studio_service
    app.dependency_overrides[get_studio_prompt_block_service] = lambda: mock_studio_service
    app.dependency_overrides[get_studio_output_profile_service] = lambda: mock_studio_service
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_get_prompt_blocks(client: Any, mock_studio_service: Any) -> None:
    response = client.get("/api/v2/studio/prompt-blocks")  # Default API prefix pattern
    if response.status_code == 404:
        response = client.get("/studio/prompt-blocks")  # Fallback pattern
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == "blk_ffff6666ffff6666"
    mock_studio_service.list_prompt_blocks.assert_called_once()


def test_delete_prompt_block(client: Any, mock_studio_service: Any) -> None:
    response = client.delete("/api/v2/studio/prompt-blocks/blk_ffff6666ffff6666")
    if response.status_code == 404:
        response = client.delete("/studio/prompt-blocks/blk_ffff6666ffff6666")
    assert response.status_code == 200
    assert response.json()["deleted_id"] == "blk_ffff6666ffff6666"
    mock_studio_service.delete_prompt_block.assert_called_once()
