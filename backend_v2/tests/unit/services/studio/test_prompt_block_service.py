"""Unit Tests for StudioPromptBlockService."""

from typing import Any
from unittest.mock import AsyncMock

import pytest

from backend_v2.exceptions import AppException, ErrorCodes, PermissionDeniedError, ResourceNotFoundError
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.domain.prompt_blocks import PromptBlockAdapter
from backend_v2.services.studio.prompt_block_service import StudioPromptBlockService

pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_system_repo() -> Any:
    return AsyncMock()


@pytest.fixture
def prompt_block_service(mock_seed_prompt_block_repo: Any, mock_system_repo: Any) -> Any:
    return StudioPromptBlockService(prompt_block_repo=mock_seed_prompt_block_repo, system_repo=mock_system_repo)


@pytest.fixture
def root_token() -> Any:
    return TokenData(id="root_user", role=UserRole.ROOT)


@pytest.fixture
def admin_token() -> Any:
    return TokenData(id="admin_user", role=UserRole.ADMIN, organization_id="org_123")


@pytest.fixture
def other_admin_token() -> Any:
    return TokenData(id="other_admin", role=UserRole.ADMIN, organization_id="org_other_999")


async def test_list_prompt_blocks_empty(
    prompt_block_service: Any, root_token: Any, mock_seed_prompt_block_repo: Any
) -> None:
    mock_seed_prompt_block_repo.get_all_prompt_blocks.return_value = []
    res = await prompt_block_service.list_prompt_blocks(root_token)
    assert res == []


async def test_list_prompt_blocks_success(
    prompt_block_service: Any, root_token: Any, mock_seed_prompt_block_repo: Any
) -> None:
    blk_data = {
        "id": "blk_1234567890abcdef12",
        "slug": "blk_1",
        "label": {"default_locale": "en", "translations": {"en": "Block"}},
        "description": {"default_locale": "en", "translations": {"en": "Desc"}},
        "category_id": "agent_role",
        "type": "string",
        "organization_id": "org_123",
    }
    mock_seed_prompt_block_repo.get_all_prompt_blocks.return_value = [blk_data]
    res = await prompt_block_service.list_prompt_blocks(root_token)
    assert len(res) == 1
    assert res[0].id == "blk_1234567890abcdef12"


async def test_list_prompt_blocks_corrupt_data_raises_app_exception(
    prompt_block_service: Any, root_token: Any, mock_seed_prompt_block_repo: Any
) -> None:
    corrupt_data = {
        "id": "blk_1234567890abcdef12",
        "slug": "blk_1",
        "label": {"default_locale": "en", "translations": {"en": "Block"}},
    }
    mock_seed_prompt_block_repo.get_all_prompt_blocks.return_value = [corrupt_data]
    with pytest.raises(AppException) as exc_info:
        await prompt_block_service.list_prompt_blocks(root_token)
    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.STATE_INTEGRITY_ERROR


async def test_list_prompt_blocks_tenant_filtering(
    prompt_block_service: Any, admin_token: Any, mock_seed_prompt_block_repo: Any
) -> None:
    blk_org = {
        "id": "blk_1111222233334444",
        "slug": "blk_org",
        "label": {"default_locale": "en", "translations": {"en": "Org Block"}},
        "description": {"default_locale": "en", "translations": {"en": "Desc"}},
        "category_id": "agent_role",
        "type": "string",
        "organization_id": "org_123",
    }
    blk_other_org = {
        "id": "blk_5555666677778888",
        "slug": "blk_other",
        "label": {"default_locale": "en", "translations": {"en": "Other Org Block"}},
        "description": {"default_locale": "en", "translations": {"en": "Desc"}},
        "category_id": "agent_role",
        "type": "string",
        "organization_id": "org_other_999",
    }
    mock_seed_prompt_block_repo.get_all_prompt_blocks.return_value = [blk_org, blk_other_org]
    res = await prompt_block_service.list_prompt_blocks(admin_token)
    assert len(res) == 1
    assert res[0].id == "blk_1111222233334444"


async def test_get_prompt_block_success(
    prompt_block_service: Any, admin_token: Any, mock_seed_prompt_block_repo: Any
) -> None:
    blk_data = {
        "id": "blk_1234567890abcdef12",
        "slug": "blk_1",
        "label": {"default_locale": "en", "translations": {"en": "Block"}},
        "description": {"default_locale": "en", "translations": {"en": "Desc"}},
        "category_id": "agent_role",
        "type": "string",
        "organization_id": "org_123",
    }
    mock_seed_prompt_block_repo.get_prompt_block_by_id.side_effect = None
    mock_seed_prompt_block_repo.get_prompt_block_by_id.return_value = blk_data
    block = await prompt_block_service.get_prompt_block(admin_token, "blk_1234567890abcdef12")
    assert block.id == "blk_1234567890abcdef12"


async def test_get_prompt_block_not_found(
    prompt_block_service: Any, root_token: Any, mock_seed_prompt_block_repo: Any, caplog: Any
) -> None:
    mock_seed_prompt_block_repo.get_prompt_block_by_id.side_effect = None
    mock_seed_prompt_block_repo.get_prompt_block_by_id.return_value = None
    with pytest.raises(ResourceNotFoundError):
        await prompt_block_service.get_prompt_block(root_token, "blk_missing")
    assert root_token.id in caplog.text


async def test_get_prompt_block_tenant_isolation_fails(
    prompt_block_service: Any, other_admin_token: Any, mock_seed_prompt_block_repo: Any
) -> None:
    blk_data = {
        "id": "blk_1234567890abcdef12",
        "slug": "blk_1",
        "label": {"default_locale": "en", "translations": {"en": "Block"}},
        "description": {"default_locale": "en", "translations": {"en": "Desc"}},
        "category_id": "agent_role",
        "type": "string",
        "organization_id": "org_123",
    }
    mock_seed_prompt_block_repo.get_prompt_block_by_id.side_effect = None
    mock_seed_prompt_block_repo.get_prompt_block_by_id.return_value = blk_data
    with pytest.raises(PermissionDeniedError):
        await prompt_block_service.get_prompt_block(other_admin_token, "blk_1234567890abcdef12")


async def test_save_prompt_block_success(
    prompt_block_service: Any, admin_token: Any, mock_seed_prompt_block_repo: Any
) -> None:
    blk_data = {
        "id": "blk_1234567890abcdef12",
        "slug": "blk_1",
        "label": {"default_locale": "en", "translations": {"en": "Block"}},
        "description": {"default_locale": "en", "translations": {"en": "Desc"}},
        "category_id": "agent_role",
        "type": "string",
        "organization_id": "org_123",
    }
    mock_seed_prompt_block_repo.get_prompt_block_by_id.side_effect = None
    mock_seed_prompt_block_repo.get_prompt_block_by_id.return_value = blk_data
    res = await prompt_block_service.save_prompt_block(
        admin_token, "blk_1234567890abcdef12", PromptBlockAdapter.validate_python(blk_data)
    )
    assert res.id == "blk_1234567890abcdef12"


async def test_save_prompt_block_missing_after_save_raises(
    prompt_block_service: Any, admin_token: Any, mock_seed_prompt_block_repo: Any
) -> None:
    blk_data = {
        "id": "blk_1234567890abcdef12",
        "slug": "blk_1",
        "label": {"default_locale": "en", "translations": {"en": "Block"}},
        "description": {"default_locale": "en", "translations": {"en": "Desc"}},
        "category_id": "agent_role",
        "type": "string",
        "organization_id": "org_123",
    }
    mock_seed_prompt_block_repo.get_prompt_block_by_id.side_effect = None
    mock_seed_prompt_block_repo.get_prompt_block_by_id.return_value = None
    with pytest.raises(ResourceNotFoundError):
        await prompt_block_service.save_prompt_block(
            admin_token, "blk_1234567890abcdef12", PromptBlockAdapter.validate_python(blk_data)
        )


async def test_delete_prompt_block_success(
    prompt_block_service: Any, admin_token: Any, mock_seed_prompt_block_repo: Any
) -> None:
    blk_data = {
        "id": "blk_1234567890abcdef12",
        "slug": "blk_1",
        "label": {"default_locale": "en", "translations": {"en": "Block"}},
        "description": {"default_locale": "en", "translations": {"en": "Desc"}},
        "category_id": "agent_role",
        "type": "string",
        "organization_id": "org_123",
    }
    mock_seed_prompt_block_repo.get_prompt_block_by_id.side_effect = None
    mock_seed_prompt_block_repo.get_prompt_block_by_id.return_value = blk_data
    await prompt_block_service.delete_prompt_block(admin_token, "blk_1234567890abcdef12")
    mock_seed_prompt_block_repo.delete_prompt_block.assert_called_once()


async def test_delete_prompt_block_not_found(
    prompt_block_service: Any, admin_token: Any, mock_seed_prompt_block_repo: Any
) -> None:
    mock_seed_prompt_block_repo.get_prompt_block_by_id.side_effect = None
    mock_seed_prompt_block_repo.get_prompt_block_by_id.return_value = None
    with pytest.raises(ResourceNotFoundError):
        await prompt_block_service.delete_prompt_block(admin_token, "blk_missing")


async def test_create_prompt_block_draft(
    prompt_block_service: Any, admin_token: Any, mock_seed_prompt_block_repo: Any
) -> None:
    stored: dict[str, Any] = {}

    async def fake_create(data: dict[str, Any]) -> str:
        stored[data["id"]] = data
        return data["id"]

    async def fake_get(block_id: str) -> dict[str, Any] | None:
        return stored.get(block_id)

    mock_seed_prompt_block_repo.create_prompt_block.side_effect = fake_create
    mock_seed_prompt_block_repo.get_prompt_block_by_id.side_effect = fake_get

    draft = await prompt_block_service.create_prompt_block_draft(admin_token)
    assert draft.id.startswith("blk_")
    assert draft.organization_id == "org_123"


async def test_clone_prompt_block_success(
    prompt_block_service: Any, admin_token: Any, mock_seed_prompt_block_repo: Any
) -> None:
    stored: dict[str, Any] = {
        "blk_1234567890abcdef12": {
            "id": "blk_1234567890abcdef12",
            "slug": "blk_1",
            "label": {"default_locale": "en", "translations": {"en": "Block"}},
            "description": {"default_locale": "en", "translations": {"en": "Desc"}},
            "category_id": "agent_role",
            "type": "string",
            "organization_id": "org_123",
        }
    }

    async def fake_create(data: dict[str, Any]) -> str:
        stored[data["id"]] = data
        return data["id"]

    async def fake_get(block_id: str) -> dict[str, Any] | None:
        return stored.get(block_id)

    mock_seed_prompt_block_repo.create_prompt_block.side_effect = fake_create
    mock_seed_prompt_block_repo.get_prompt_block_by_id.side_effect = fake_get

    cloned = await prompt_block_service.clone_prompt_block(admin_token, "blk_1234567890abcdef12")
    assert cloned.id.startswith("blk_")
    assert cloned.id != "blk_1234567890abcdef12"
    assert cloned.label.translations["en"] == "Block (Copy)"


async def test_clone_prompt_block_not_found(
    prompt_block_service: Any, admin_token: Any, mock_seed_prompt_block_repo: Any
) -> None:
    mock_seed_prompt_block_repo.get_prompt_block_by_id.return_value = None
    with pytest.raises(ResourceNotFoundError):
        await prompt_block_service.clone_prompt_block(admin_token, "blk_missing")
