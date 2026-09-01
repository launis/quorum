"""Unit Tests for StudioPromptBlockService."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from backend_v2.exceptions import PermissionDeniedError, ResourceNotFoundError
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.prompt_blocks import PersonaPromptBlock, PromptBlock
from backend_v2.models.enums import BlockDataType, PromptBlockCategory
from backend_v2.services.studio.prompt_block_service import StudioPromptBlockService

pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_system_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_prompt_block_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def prompt_block_service(mock_prompt_block_repo: AsyncMock, mock_system_repo: AsyncMock) -> StudioPromptBlockService:
    return StudioPromptBlockService(prompt_block_repo=mock_prompt_block_repo, system_repo=mock_system_repo)


@pytest.fixture
def root_token() -> TokenData:
    return TokenData(id="root_user", role=UserRole.ROOT)


@pytest.fixture
def admin_token() -> TokenData:
    return TokenData(id="admin_user", role=UserRole.ADMIN, organization_id="org_123")


@pytest.fixture
def other_admin_token() -> TokenData:
    return TokenData(id="other_admin", role=UserRole.ADMIN, organization_id="org_other_999")


@pytest.fixture
def sample_block() -> PersonaPromptBlock:
    return PersonaPromptBlock(
        id="blk_1234567890abcdef",
        slug="blk_1",
        label=I18nText(translations={"en": "Block"}),
        description=I18nText(translations={"en": "Desc"}),
        category_id=PromptBlockCategory.EXECUTION_PERSONA,
        type=BlockDataType.INSTRUCTION,
        organization_id="org_123",
        role_enforcement="Strict enforcement.",
    )


async def test_list_prompt_blocks_empty(
    prompt_block_service: StudioPromptBlockService, root_token: TokenData, mock_prompt_block_repo: AsyncMock
) -> None:
    mock_prompt_block_repo.get_all_prompt_blocks.return_value = []
    res = await prompt_block_service.list_prompt_blocks(root_token)
    assert res == []


async def test_list_prompt_blocks_success(
    prompt_block_service: StudioPromptBlockService,
    root_token: TokenData,
    mock_prompt_block_repo: AsyncMock,
    sample_block: PersonaPromptBlock,
) -> None:
    mock_prompt_block_repo.get_all_prompt_blocks.return_value = [sample_block]
    res = await prompt_block_service.list_prompt_blocks(root_token)
    assert len(res) == 1
    assert res[0].id == "blk_1234567890abcdef"


async def test_list_prompt_blocks_tenant_filtering(
    prompt_block_service: StudioPromptBlockService,
    admin_token: TokenData,
    mock_prompt_block_repo: AsyncMock,
    sample_block: PersonaPromptBlock,
) -> None:
    blk_other = sample_block.model_copy(update={"id": "blk_5555666677778888", "organization_id": "org_other_999"})
    mock_prompt_block_repo.get_all_prompt_blocks.return_value = [sample_block, blk_other]
    res = await prompt_block_service.list_prompt_blocks(admin_token)
    assert len(res) == 1
    assert res[0].id == "blk_1234567890abcdef"


async def test_get_prompt_block_success(
    prompt_block_service: StudioPromptBlockService,
    admin_token: TokenData,
    mock_prompt_block_repo: AsyncMock,
    sample_block: PersonaPromptBlock,
) -> None:
    mock_prompt_block_repo.get_prompt_block_by_id.return_value = sample_block
    block = await prompt_block_service.get_prompt_block(admin_token, "blk_1234567890abcdef")
    assert block.id == "blk_1234567890abcdef"


async def test_get_prompt_block_not_found(
    prompt_block_service: StudioPromptBlockService,
    root_token: TokenData,
    mock_prompt_block_repo: AsyncMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    mock_prompt_block_repo.get_prompt_block_by_id.return_value = None
    with pytest.raises(ResourceNotFoundError):
        await prompt_block_service.get_prompt_block(root_token, "blk_missing")
    assert root_token.id in caplog.text


async def test_get_prompt_block_tenant_isolation_fails(
    prompt_block_service: StudioPromptBlockService,
    other_admin_token: TokenData,
    mock_prompt_block_repo: AsyncMock,
    sample_block: PersonaPromptBlock,
) -> None:
    mock_prompt_block_repo.get_prompt_block_by_id.return_value = sample_block
    with pytest.raises(PermissionDeniedError):
        await prompt_block_service.get_prompt_block(other_admin_token, "blk_1234567890abcdef")


async def test_save_prompt_block_success(
    prompt_block_service: StudioPromptBlockService,
    admin_token: TokenData,
    mock_prompt_block_repo: AsyncMock,
    sample_block: PersonaPromptBlock,
) -> None:
    mock_prompt_block_repo.get_prompt_block_by_id.return_value = sample_block
    res = await prompt_block_service.save_prompt_block(admin_token, "blk_1234567890abcdef", sample_block)
    assert res.id == "blk_1234567890abcdef"


async def test_save_prompt_block_missing_after_save_raises(
    prompt_block_service: StudioPromptBlockService,
    admin_token: TokenData,
    mock_prompt_block_repo: AsyncMock,
    sample_block: PersonaPromptBlock,
) -> None:
    mock_prompt_block_repo.get_prompt_block_by_id.return_value = None
    with pytest.raises(ResourceNotFoundError):
        await prompt_block_service.save_prompt_block(admin_token, "blk_1234567890abcdef", sample_block)


async def test_delete_prompt_block_success(
    prompt_block_service: StudioPromptBlockService,
    admin_token: TokenData,
    mock_prompt_block_repo: AsyncMock,
    sample_block: PersonaPromptBlock,
) -> None:
    mock_prompt_block_repo.get_prompt_block_by_id.return_value = sample_block
    await prompt_block_service.delete_prompt_block(admin_token, "blk_1234567890abcdef")
    mock_prompt_block_repo.delete_prompt_block.assert_called_once()


async def test_delete_prompt_block_not_found(
    prompt_block_service: StudioPromptBlockService, admin_token: TokenData, mock_prompt_block_repo: AsyncMock
) -> None:
    mock_prompt_block_repo.get_prompt_block_by_id.return_value = None
    with pytest.raises(ResourceNotFoundError):
        await prompt_block_service.delete_prompt_block(admin_token, "blk_missing")


async def test_create_prompt_block_draft(
    prompt_block_service: StudioPromptBlockService, admin_token: TokenData, mock_prompt_block_repo: AsyncMock
) -> None:
    stored: dict[str, PromptBlock] = {}

    async def fake_create(data: PromptBlock) -> str:
        stored[data.id] = data
        return data.id

    async def fake_get(block_id: str) -> PromptBlock | None:
        return stored.get(block_id)

    mock_prompt_block_repo.create_prompt_block.side_effect = fake_create
    mock_prompt_block_repo.get_prompt_block_by_id.side_effect = fake_get

    draft = await prompt_block_service.create_prompt_block_draft(admin_token)
    assert draft.id.startswith("blk_")
    assert draft.organization_id == "org_123"


async def test_clone_prompt_block_success(
    prompt_block_service: StudioPromptBlockService,
    admin_token: TokenData,
    mock_prompt_block_repo: AsyncMock,
    sample_block: PersonaPromptBlock,
) -> None:
    stored: dict[str, PromptBlock] = {
        "blk_1234567890abcdef": sample_block,
    }

    async def fake_create(data: PromptBlock) -> str:
        stored[data.id] = data
        return data.id

    async def fake_get(block_id: str) -> PromptBlock | None:
        return stored.get(block_id)

    mock_prompt_block_repo.create_prompt_block.side_effect = fake_create
    mock_prompt_block_repo.get_prompt_block_by_id.side_effect = fake_get

    cloned = await prompt_block_service.clone_prompt_block(admin_token, "blk_1234567890abcdef")
    assert cloned.id.startswith("blk_")
    assert cloned.id != "blk_1234567890abcdef"
    assert cloned.label.translations["en"] == "Block (Copy)"


async def test_clone_prompt_block_not_found(
    prompt_block_service: StudioPromptBlockService, admin_token: TokenData, mock_prompt_block_repo: AsyncMock
) -> None:
    mock_prompt_block_repo.get_prompt_block_by_id.return_value = None
    with pytest.raises(ResourceNotFoundError):
        await prompt_block_service.clone_prompt_block(admin_token, "blk_missing")
