"""Unit Tests for StudioPromptBlockService with Stateful Roundtrip Parity."""

from __future__ import annotations

import pytest

from backend_v2.exceptions import AppException, ErrorCodes, PermissionDeniedError, ResourceNotFoundError
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.core_base import I18nText, generate_opaque_id
from backend_v2.models.domain.prompt_blocks import (
    MatrixPromptBlock,
    PersonaPromptBlock,
    ProtocolPromptBlock,
    SystemRulePromptBlock,
)
from backend_v2.models.enums import BlockDataType, EntityPrefix, PromptBlockCategory
from backend_v2.services.studio.prompt_block_service import StudioPromptBlockService
from backend_v2.tests.factories.model_factories import SystemRulePromptBlockFactory
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
        id="blk_0195f3a0000070018234567890abcdef",
        slug="blk_1",
        label=I18nText(translations={"en": "Block"}),
        description=I18nText(translations={"en": "Desc"}),
        category_id=PromptBlockCategory.EXECUTION_PERSONA,
        type=BlockDataType.INSTRUCTION,
        organization_id="org_123",
        role_enforcement="Strict enforcement.",
        output_extensions=[],
        tone_directives=[],
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
    assert res[0].id == "blk_0195f3a0000070018234567890abcdef"


async def test_list_prompt_blocks_tenant_filtering(
    prompt_block_service: StudioPromptBlockService,
    prompt_block_repo: InMemoryPromptBlockRepository,
    admin_token: TokenData,
    sample_block: PersonaPromptBlock,
) -> None:
    await prompt_block_repo.create_prompt_block(sample_block)
    blk_other = sample_block.model_copy(
        update={"id": "blk_0195f3a0000070058555666677778888", "organization_id": "org_other_999"}
    )
    await prompt_block_repo.create_prompt_block(blk_other)
    res = await prompt_block_service.list_prompt_blocks(admin_token)
    assert len(res) == 1
    assert res[0].id == "blk_0195f3a0000070018234567890abcdef"


async def test_get_prompt_block_success(
    prompt_block_service: StudioPromptBlockService,
    prompt_block_repo: InMemoryPromptBlockRepository,
    admin_token: TokenData,
    sample_block: PersonaPromptBlock,
) -> None:
    await prompt_block_repo.create_prompt_block(sample_block)
    block = await prompt_block_service.get_prompt_block(admin_token, "blk_0195f3a0000070018234567890abcdef")
    assert block.id == "blk_0195f3a0000070018234567890abcdef"


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
        await prompt_block_service.get_prompt_block(other_admin_token, "blk_0195f3a0000070018234567890abcdef")


async def test_save_prompt_block_success(
    prompt_block_service: StudioPromptBlockService,
    prompt_block_repo: InMemoryPromptBlockRepository,
    admin_token: TokenData,
    sample_block: PersonaPromptBlock,
) -> None:
    await prompt_block_repo.create_prompt_block(sample_block)
    updated_block = sample_block.model_copy(update={"role_enforcement": "Updated strict enforcement."})
    res = await prompt_block_service.save_prompt_block(
        admin_token, "blk_0195f3a0000070018234567890abcdef", updated_block
    )
    assert res.id == "blk_0195f3a0000070018234567890abcdef"
    assert isinstance(res, PersonaPromptBlock)
    assert res.role_enforcement == "Updated strict enforcement."

    # Stateful roundtrip verification via repository re-fetch
    persisted = await prompt_block_repo.get_prompt_block_by_id("blk_0195f3a0000070018234567890abcdef")
    assert persisted is not None
    assert isinstance(persisted, PersonaPromptBlock)
    assert persisted.role_enforcement == "Updated strict enforcement."
    assert persisted.id == "blk_0195f3a0000070018234567890abcdef"


async def test_save_prompt_block_missing_after_save_raises(
    prompt_block_service: StudioPromptBlockService,
    prompt_block_repo: InMemoryPromptBlockRepository,
    admin_token: TokenData,
    sample_block: PersonaPromptBlock,
) -> None:
    prompt_block_repo.inject_fault(
        "get_prompt_block_by_id",
        ResourceNotFoundError(resource_type="prompt_block", resource_id="blk_0195f3a0000070018234567890abcdef"),
    )
    try:
        with pytest.raises(ResourceNotFoundError):
            await prompt_block_service.save_prompt_block(
                admin_token, "blk_0195f3a0000070018234567890abcdef", sample_block
            )
        with pytest.raises(ResourceNotFoundError):
            await prompt_block_service.create_prompt_block_draft(admin_token)
    finally:
        prompt_block_repo.clear_faults()


async def test_save_prompt_block_atomization_failure_raises(
    prompt_block_service: StudioPromptBlockService,
    prompt_block_repo: InMemoryPromptBlockRepository,
    admin_token: TokenData,
    sample_block: PersonaPromptBlock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    await prompt_block_repo.create_prompt_block(sample_block)

    async def _fail_atomize(*_args: object, **_kwargs: object) -> PersonaPromptBlock:
        raise RuntimeError("Atomizer engine failure")

    monkeypatch.setattr(
        "backend_v2.services.studio.prompt_block_service.PromptAtomizer.atomize_prompt_block",
        _fail_atomize,
    )
    with pytest.raises(AppException) as exc_info:
        await prompt_block_service.save_prompt_block(admin_token, "blk_0195f3a0000070018234567890abcdef", sample_block)
    assert exc_info.value.status_code == 500
    assert exc_info.value.details == {"error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL}


async def test_save_prompt_block_id_mismatch_normalizes_id(
    prompt_block_service: StudioPromptBlockService,
    prompt_block_repo: InMemoryPromptBlockRepository,
    admin_token: TokenData,
    sample_block: PersonaPromptBlock,
) -> None:
    authoritative_id = "blk_0195f3a00000700a8bcdef1234567890"
    await prompt_block_repo.create_prompt_block(sample_block.model_copy(update={"id": authoritative_id}))
    res = await prompt_block_service.save_prompt_block(admin_token, authoritative_id, sample_block)
    assert res.id == authoritative_id
    persisted = await prompt_block_repo.get_prompt_block_by_id(authoritative_id)
    assert persisted is not None
    assert persisted.id == authoritative_id


async def test_delete_prompt_block_success(
    prompt_block_service: StudioPromptBlockService,
    prompt_block_repo: InMemoryPromptBlockRepository,
    admin_token: TokenData,
    sample_block: PersonaPromptBlock,
) -> None:
    await prompt_block_repo.create_prompt_block(sample_block)
    await prompt_block_service.delete_prompt_block(admin_token, "blk_0195f3a0000070018234567890abcdef")
    persisted = await prompt_block_repo.get_prompt_block_by_id("blk_0195f3a0000070018234567890abcdef")
    assert persisted is None


async def test_delete_prompt_block_not_found(
    prompt_block_service: StudioPromptBlockService,
    admin_token: TokenData,
) -> None:
    with pytest.raises(ResourceNotFoundError):
        await prompt_block_service.delete_prompt_block(admin_token, "blk_missing")


async def test_delete_protocol_prompt_block_without_force_raises(
    prompt_block_service: StudioPromptBlockService,
    prompt_block_repo: InMemoryPromptBlockRepository,
    admin_token: TokenData,
) -> None:
    protocol_block = ProtocolPromptBlock(
        id="blk_0195f3a0000070018234567890abcdef",
        slug="blk_protocol",
        label=I18nText(translations={"en": "Protocol Block"}),
        description=I18nText(translations={"en": "Protocol Desc"}),
        category_id=PromptBlockCategory.PROTOCOL,
        type=BlockDataType.INSTRUCTION,
        organization_id="org_123",
        output_extensions=[],
        protocol_instructions="Strict protocol enforcement.",
    )
    await prompt_block_repo.create_prompt_block(protocol_block)
    with pytest.raises(AppException) as exc_info:
        await prompt_block_service.delete_prompt_block(
            admin_token, "blk_0195f3a0000070018234567890abcdef", force_delete=False
        )
    assert exc_info.value.status_code == 403
    assert exc_info.value.details == {"error_code": ErrorCodes.SYSTEM_PROTECTED_RESOURCE}


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


async def test_create_matrix_prompt_block_draft(
    prompt_block_service: StudioPromptBlockService,
    prompt_block_repo: InMemoryPromptBlockRepository,
    admin_token: TokenData,
) -> None:
    draft = await prompt_block_service.create_prompt_block_draft(admin_token, category_id=PromptBlockCategory.MATRIX)
    assert isinstance(draft, MatrixPromptBlock)
    assert draft.category_id == PromptBlockCategory.MATRIX
    assert len(draft.scales) == 1

    persisted = await prompt_block_repo.get_prompt_block_by_id(draft.id)
    assert isinstance(persisted, MatrixPromptBlock)
    assert persisted.id == draft.id


async def test_clone_prompt_block_success(
    prompt_block_service: StudioPromptBlockService,
    prompt_block_repo: InMemoryPromptBlockRepository,
    admin_token: TokenData,
    sample_block: PersonaPromptBlock,
) -> None:
    await prompt_block_repo.create_prompt_block(sample_block)
    cloned = await prompt_block_service.clone_prompt_block(admin_token, "blk_0195f3a0000070018234567890abcdef")
    assert cloned.id.startswith("blk_")
    assert cloned.id != "blk_0195f3a0000070018234567890abcdef"
    assert cloned.slug == sample_block.slug
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


async def test_create_runtime_variables_and_system_rule_prompt_block_draft_and_clone(
    prompt_block_service: StudioPromptBlockService,
    prompt_block_repo: InMemoryPromptBlockRepository,
    admin_token: TokenData,
) -> None:
    draft = await prompt_block_service.create_prompt_block_draft(
        admin_token,
        category_id=PromptBlockCategory.SYSTEM_RULE,
    )
    assert isinstance(draft, SystemRulePromptBlock)
    assert draft.category_id == PromptBlockCategory.SYSTEM_RULE
    assert draft.organization_id == "org_123"

    runtime_draft = await prompt_block_service.create_prompt_block_draft(
        admin_token,
        category_id=PromptBlockCategory.RUNTIME_VARIABLES,
    )
    assert isinstance(runtime_draft, SystemRulePromptBlock)
    assert runtime_draft.category_id == PromptBlockCategory.RUNTIME_VARIABLES

    cloned = await prompt_block_service.clone_prompt_block(admin_token, runtime_draft.id)
    assert isinstance(cloned, SystemRulePromptBlock)
    assert cloned.category_id == PromptBlockCategory.RUNTIME_VARIABLES
    assert cloned.id != runtime_draft.id
    assert cloned.label.translations["en"].endswith("(Copy)")

    persisted_clone = await prompt_block_repo.get_prompt_block_by_id(cloned.id)
    assert isinstance(persisted_clone, SystemRulePromptBlock)
    assert persisted_clone.category_id == PromptBlockCategory.RUNTIME_VARIABLES


async def test_save_prompt_block_cross_tenant_idor_org_preservation_and_unknown_id_404(
    prompt_block_service: StudioPromptBlockService,
    prompt_block_repo: InMemoryPromptBlockRepository,
    admin_token: TokenData,
) -> None:
    """Verify cross-tenant PUT IDOR rejection, non-ROOT organization_id preservation, and missing ID 404."""
    missing_block = SystemRulePromptBlockFactory.build(organization_id="org_123")
    with pytest.raises(ResourceNotFoundError):
        await prompt_block_service.save_prompt_block(admin_token, missing_block.id, missing_block)
    assert await prompt_block_repo.get_prompt_block_by_id(missing_block.id) is None

    other_org_block = SystemRulePromptBlockFactory.build(organization_id="org_other")
    await prompt_block_repo.create_prompt_block(other_org_block)
    forged_payload = other_org_block.model_copy(update={"organization_id": "org_123"})
    with pytest.raises(PermissionDeniedError):
        await prompt_block_service.save_prompt_block(admin_token, other_org_block.id, forged_payload)
    unchanged = await prompt_block_repo.get_prompt_block_by_id(other_org_block.id)
    assert unchanged is not None
    assert unchanged.organization_id == "org_other"

    own_block = SystemRulePromptBlockFactory.build(organization_id="org_123")
    await prompt_block_repo.create_prompt_block(own_block)
    reassigned_payload = own_block.model_copy(
        update={
            "organization_id": generate_opaque_id(EntityPrefix.ORGANIZATION),
            "system_instructions": "Updated own instructions.",
        }
    )
    saved = await prompt_block_service.save_prompt_block(admin_token, own_block.id, reassigned_payload)
    assert saved.organization_id == "org_123"
    assert isinstance(saved, SystemRulePromptBlock)
    assert saved.system_instructions == "Updated own instructions."
