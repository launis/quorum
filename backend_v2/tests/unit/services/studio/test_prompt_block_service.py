"""Unit Tests for StudioPromptBlockService with Stateful Roundtrip Parity."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from backend_v2.exceptions import PermissionDeniedError, ResourceNotFoundError
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.prompt_blocks import PersonaPromptBlock
from backend_v2.models.enums import BlockDataType, PromptBlockCategory
from backend_v2.services.studio.prompt_block_service import StudioPromptBlockService
from backend_v2.tests.fakes.in_memory_repositories import (
    InMemoryPromptBlockRepository,
    InMemorySystemRepository,
)

pytestmark = pytest.mark.asyncio


@pytest.fixture
def system_repo() -> InMemorySystemRepository:
    return InMemorySystemRepository()


@pytest.fixture
def prompt_block_repo() -> InMemoryPromptBlockRepository:
    return InMemoryPromptBlockRepository()


@pytest.fixture
def prompt_block_service(
    prompt_block_repo: InMemoryPromptBlockRepository,
    system_repo: InMemorySystemRepository,
) -> StudioPromptBlockService:
    return StudioPromptBlockService(prompt_block_repo=prompt_block_repo, system_repo=system_repo)


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
    prompt_block_service: StudioPromptBlockService,
    root_token: TokenData,
) -> None:
    res = await prompt_block_service.list_prompt_blocks(root_token)
    assert res == []


async def test_list_prompt_blocks_success(
    prompt_block_service: StudioPromptBlockService,
    prompt_block_repo: InMemoryPromptBlockRepository,
    root_token: TokenData,
    sample_block: PersonaPromptBlock,
) -> None:
    await prompt_block_repo.create_prompt_block(sample_block)
    res = await prompt_block_service.list_prompt_blocks(root_token)
    assert len(res) == 1
    assert res[0].id == "blk_1234567890abcdef"


async def test_list_prompt_blocks_tenant_filtering(
    prompt_block_service: StudioPromptBlockService,
    prompt_block_repo: InMemoryPromptBlockRepository,
    admin_token: TokenData,
    sample_block: PersonaPromptBlock,
) -> None:
    await prompt_block_repo.create_prompt_block(sample_block)
    blk_other = sample_block.model_copy(update={"id": "blk_5555666677778888", "organization_id": "org_other_999"})
    await prompt_block_repo.create_prompt_block(blk_other)
    res = await prompt_block_service.list_prompt_blocks(admin_token)
    assert len(res) == 1
    assert res[0].id == "blk_1234567890abcdef"


async def test_get_prompt_block_success(
    prompt_block_service: StudioPromptBlockService,
    prompt_block_repo: InMemoryPromptBlockRepository,
    admin_token: TokenData,
    sample_block: PersonaPromptBlock,
) -> None:
    await prompt_block_repo.create_prompt_block(sample_block)
    block = await prompt_block_service.get_prompt_block(admin_token, "blk_1234567890abcdef")
    assert block.id == "blk_1234567890abcdef"


async def test_get_prompt_block_not_found(
    prompt_block_service: StudioPromptBlockService,
    root_token: TokenData,
    caplog: pytest.LogCaptureFixture,
) -> None:
    with pytest.raises(ResourceNotFoundError):
        await prompt_block_service.get_prompt_block(root_token, "blk_missing")
    assert root_token.id in caplog.text


async def test_get_prompt_block_tenant_isolation_fails(
    prompt_block_service: StudioPromptBlockService,
    prompt_block_repo: InMemoryPromptBlockRepository,
    other_admin_token: TokenData,
    sample_block: PersonaPromptBlock,
) -> None:
    await prompt_block_repo.create_prompt_block(sample_block)
    with pytest.raises(PermissionDeniedError):
        await prompt_block_service.get_prompt_block(other_admin_token, "blk_1234567890abcdef")


async def test_save_prompt_block_success(
    prompt_block_service: StudioPromptBlockService,
    prompt_block_repo: InMemoryPromptBlockRepository,
    admin_token: TokenData,
    sample_block: PersonaPromptBlock,
) -> None:
    await prompt_block_repo.create_prompt_block(sample_block)
    updated_block = sample_block.model_copy(update={"role_enforcement": "Updated strict enforcement."})
    res = await prompt_block_service.save_prompt_block(admin_token, "blk_1234567890abcdef", updated_block)
    assert res.id == "blk_1234567890abcdef"
    assert isinstance(res, PersonaPromptBlock)
    assert res.role_enforcement == "Updated strict enforcement."

    # Stateful roundtrip verification via repository re-fetch
    persisted = await prompt_block_repo.get_prompt_block_by_id("blk_1234567890abcdef")
    assert persisted is not None
    assert isinstance(persisted, PersonaPromptBlock)
    assert persisted.role_enforcement == "Updated strict enforcement."
    assert persisted.id == "blk_1234567890abcdef"


async def test_save_prompt_block_missing_after_save_raises(
    prompt_block_service: StudioPromptBlockService,
    prompt_block_repo: InMemoryPromptBlockRepository,
    admin_token: TokenData,
    sample_block: PersonaPromptBlock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(prompt_block_repo, "get_prompt_block_by_id", AsyncMock(return_value=None))
    with pytest.raises(ResourceNotFoundError):
        await prompt_block_service.save_prompt_block(admin_token, "blk_1234567890abcdef", sample_block)


async def test_delete_prompt_block_success(
    prompt_block_service: StudioPromptBlockService,
    prompt_block_repo: InMemoryPromptBlockRepository,
    admin_token: TokenData,
    sample_block: PersonaPromptBlock,
) -> None:
    await prompt_block_repo.create_prompt_block(sample_block)
    await prompt_block_service.delete_prompt_block(admin_token, "blk_1234567890abcdef")
    persisted = await prompt_block_repo.get_prompt_block_by_id("blk_1234567890abcdef")
    assert persisted is None


async def test_delete_prompt_block_not_found(
    prompt_block_service: StudioPromptBlockService,
    admin_token: TokenData,
) -> None:
    with pytest.raises(ResourceNotFoundError):
        await prompt_block_service.delete_prompt_block(admin_token, "blk_missing")


async def test_create_prompt_block_draft(
    prompt_block_service: StudioPromptBlockService,
    prompt_block_repo: InMemoryPromptBlockRepository,
    admin_token: TokenData,
) -> None:
    draft = await prompt_block_service.create_prompt_block_draft(admin_token)
    assert draft.id.startswith("blk_")
    assert draft.organization_id == "org_123"

    persisted = await prompt_block_repo.get_prompt_block_by_id(draft.id)
    assert persisted is not None
    assert persisted.id == draft.id
    assert persisted.organization_id == "org_123"


async def test_clone_prompt_block_success(
    prompt_block_service: StudioPromptBlockService,
    prompt_block_repo: InMemoryPromptBlockRepository,
    admin_token: TokenData,
    sample_block: PersonaPromptBlock,
) -> None:
    await prompt_block_repo.create_prompt_block(sample_block)
    cloned = await prompt_block_service.clone_prompt_block(admin_token, "blk_1234567890abcdef")
    assert cloned.id.startswith("blk_")
    assert cloned.id != "blk_1234567890abcdef"
    assert cloned.label.translations["en"] == "Block (Copy)"

    persisted = await prompt_block_repo.get_prompt_block_by_id(cloned.id)
    assert persisted is not None
    assert persisted.id == cloned.id
    assert persisted.label.translations["en"] == "Block (Copy)"


async def test_clone_prompt_block_not_found(
    prompt_block_service: StudioPromptBlockService,
    admin_token: TokenData,
) -> None:
    with pytest.raises(ResourceNotFoundError):
        await prompt_block_service.clone_prompt_block(admin_token, "blk_missing")
