"""Unit Tests for StudioTaskBriefService with Stateful Roundtrip Parity."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from backend_v2.database.repositories.components.task_brief import TaskBriefRepositoryImpl
from backend_v2.exceptions import (
    AppException,
    ErrorCodes,
    PermissionDeniedError,
    ResourceNotFoundError,
)
from backend_v2.models.auth import Organization, SystemOrganizations, TokenData, UserRole
from backend_v2.models.core_base import I18nText, generate_opaque_id
from backend_v2.models.domain.execution import ExecutionAssignment
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.domain.task_brief import TaskAssignmentBriefDTO, TaskBrief
from backend_v2.models.enums import AssignmentStatus, EntityPrefix
from backend_v2.services.studio.task_brief_service import StudioTaskBriefService
from backend_v2.tests.factories.model_factories import (
    OutputProfileFactory,
    StepFactory,
    SystemRulePromptBlockFactory,
    TaskBriefFactory,
    WorkflowFactory,
)
from backend_v2.tests.fakes.in_memory_uow import InMemoryUnitOfWork

pytestmark = pytest.mark.asyncio

ORG_ALPHA_ID = "org_0195f3a0000070008000000000000111"
ORG_BETA_ID = "org_0195f3a0000070008000000000000222"


@pytest.fixture
def uow() -> InMemoryUnitOfWork:
    """Provide an in-memory Unit of Work fixture."""
    return InMemoryUnitOfWork()


@pytest.fixture
def task_brief_repo(uow: InMemoryUnitOfWork) -> TaskBriefRepositoryImpl:
    """Provide a TaskBriefRepositoryImpl backed by the shared in-memory PostgreSQL store."""
    return TaskBriefRepositoryImpl(uow_factory=lambda: InMemoryUnitOfWork(uow.store))


@pytest.fixture
def task_brief_service(
    task_brief_repo: TaskBriefRepositoryImpl,
) -> StudioTaskBriefService:
    """Provide a StudioTaskBriefService wired to TaskBriefRepositoryImpl."""
    return StudioTaskBriefService(
        task_brief_repo=task_brief_repo,
    )


@pytest.fixture
def root_token() -> TokenData:
    """Provide a ROOT user token fixture."""
    return TokenData(
        id=generate_opaque_id(EntityPrefix.USER),
        role=UserRole.ROOT,
        organization_id=SystemOrganizations.ROOT_SYSTEM.value,
    )


@pytest.fixture
def admin_token() -> TokenData:
    """Provide an ADMIN user token fixture for ORG_ALPHA_ID."""
    return TokenData(
        id=generate_opaque_id(EntityPrefix.USER),
        role=UserRole.ADMIN,
        organization_id=ORG_ALPHA_ID,
    )


@pytest.fixture
def other_admin_token() -> TokenData:
    """Provide an ADMIN user token fixture for ORG_BETA_ID."""
    return TokenData(
        id=generate_opaque_id(EntityPrefix.USER),
        role=UserRole.ADMIN,
        organization_id=ORG_BETA_ID,
    )


@pytest.fixture
def member_token() -> TokenData:
    """Provide a MEMBER user token fixture for ORG_ALPHA_ID."""
    return TokenData(
        id=generate_opaque_id(EntityPrefix.USER),
        role=UserRole.MEMBER,
        organization_id=ORG_ALPHA_ID,
    )


@pytest.fixture
def sample_brief() -> TaskBrief:
    """Provide a tenant-scoped TaskBrief fixture."""
    return TaskBriefFactory.build(
        id="tbr_0195f3a00000700d8a1b2c3d4e5f6001",
        slug="alpha_case_study",
        organization_id=ORG_ALPHA_ID,
        label=I18nText(translations={"en": "Alpha Brief", "fi": "Alpha-ohje"}),
        description=I18nText(translations={"en": "Brief description", "fi": "Kuvaus"}),
        instruction_text="Analyze the financial risks in section 3.",
        source_url="https://docs.qrum.ai/cases/alpha",
    )


async def test_list_task_briefs_empty_and_tenant_filtering(
    task_brief_service: StudioTaskBriefService,
    task_brief_repo: TaskBriefRepositoryImpl,
    root_token: TokenData,
    admin_token: TokenData,
    sample_brief: TaskBrief,
) -> None:
    """Verify list_task_briefs returns all for ROOT and filters cross-tenant briefs for ADMIN."""
    assert await task_brief_service.list_task_briefs(root_token) == []

    sys_brief = sample_brief.model_copy(
        update={
            "id": generate_opaque_id(EntityPrefix.TASK_BRIEF),
            "organization_id": SystemOrganizations.ROOT_SYSTEM.value,
        }
    )
    beta_brief = sample_brief.model_copy(
        update={
            "id": generate_opaque_id(EntityPrefix.TASK_BRIEF),
            "organization_id": ORG_BETA_ID,
        }
    )
    await task_brief_repo.create_task_brief(sample_brief)
    await task_brief_repo.create_task_brief(sys_brief)
    await task_brief_repo.create_task_brief(beta_brief)

    root_list = await task_brief_service.list_task_briefs(root_token)
    assert len(root_list) == 3

    alpha_list = await task_brief_service.list_task_briefs(admin_token)
    assert {b.id for b in alpha_list} == {sample_brief.id, sys_brief.id}


async def test_create_draft_save_get_and_clone_task_brief_lifecycle(
    task_brief_service: StudioTaskBriefService,
    task_brief_repo: TaskBriefRepositoryImpl,
    root_token: TokenData,
    admin_token: TokenData,
) -> None:
    """Verify full stateful CRUD + Draft + Clone lifecycle for TaskBrief."""
    draft = await task_brief_service.create_task_brief_draft(admin_token)
    assert draft.id.startswith("tbr_")
    assert draft.organization_id == ORG_ALPHA_ID
    assert draft.label.translations["en"] == "New Task Brief"

    root_draft = await task_brief_service.create_task_brief_draft(root_token)
    assert root_draft.organization_id == SystemOrganizations.ROOT_SYSTEM.value

    updated_payload = draft.model_copy(
        update={
            "label": I18nText(translations={"en": "Updated Brief", "fi": "Päivitetty ohje"}),
            "instruction_text": "Updated candidate instructions.",
            "source_url": "https://docs.qrum.ai/cases/updated",
        }
    )
    saved = await task_brief_service.save_task_brief(admin_token, draft.id, updated_payload)
    assert saved.id == draft.id
    assert saved.instruction_text == "Updated candidate instructions."

    fetched = await task_brief_service.get_task_brief(admin_token, draft.id)
    assert fetched.label.translations["en"] == "Updated Brief"
    assert fetched.source_url == "https://docs.qrum.ai/cases/updated"

    cloned = await task_brief_service.clone_task_brief(admin_token, draft.id)
    assert cloned.id != draft.id
    assert cloned.id.startswith("tbr_")
    assert cloned.slug == draft.slug
    assert cloned.organization_id == ORG_ALPHA_ID
    assert cloned.label.translations["en"] == "Updated Brief (Copy)"

    persisted_clone = await task_brief_repo.get_task_brief_by_id(cloned.id)
    assert persisted_clone is not None
    assert persisted_clone.id == cloned.id

    await task_brief_service.delete_task_brief(admin_token, cloned.id)
    assert await task_brief_repo.get_task_brief_by_id(cloned.id) is None


async def test_get_and_clone_task_brief_not_found_error(
    task_brief_service: StudioTaskBriefService,
    admin_token: TokenData,
) -> None:
    """Verify get_task_brief, delete_task_brief, and clone_task_brief raise ResourceNotFoundError on missing ID."""
    missing_id = generate_opaque_id(EntityPrefix.TASK_BRIEF)
    with pytest.raises(ResourceNotFoundError) as get_exc:
        await task_brief_service.get_task_brief(admin_token, missing_id)
    assert get_exc.value.details["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value

    with pytest.raises(ResourceNotFoundError) as del_exc:
        await task_brief_service.delete_task_brief(admin_token, missing_id)
    assert del_exc.value.details["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value

    with pytest.raises(ResourceNotFoundError) as clone_exc:
        await task_brief_service.clone_task_brief(admin_token, missing_id)
    assert clone_exc.value.details["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value


async def test_task_brief_rbac_and_tenant_isolation_failure(
    task_brief_service: StudioTaskBriefService,
    task_brief_repo: TaskBriefRepositoryImpl,
    admin_token: TokenData,
    other_admin_token: TokenData,
    member_token: TokenData,
    sample_brief: TaskBrief,
) -> None:
    """Verify cross-tenant access, member modification, and non-root system modification raise PermissionDeniedError."""
    await task_brief_repo.create_task_brief(sample_brief)

    # Cross-tenant read blocked
    with pytest.raises(PermissionDeniedError):
        await task_brief_service.get_task_brief(other_admin_token, sample_brief.id)

    # Cross-tenant save blocked even when payload organization_id is forged to caller's tenant
    forged_cross_tenant = TaskBriefFactory.build(
        id=sample_brief.id,
        organization_id=ORG_BETA_ID,
        instruction_text="Forged cross-tenant overwrite",
    )
    with pytest.raises(PermissionDeniedError):
        await task_brief_service.save_task_brief(other_admin_token, sample_brief.id, forged_cross_tenant)
    persisted_alpha = await task_brief_repo.get_task_brief_by_id(sample_brief.id)
    assert persisted_alpha is not None
    assert persisted_alpha.organization_id == ORG_ALPHA_ID
    assert persisted_alpha.instruction_text == sample_brief.instruction_text

    # Non-ROOT caller saving own task brief preserves existing.organization_id
    forged_org_attempt = sample_brief.model_copy(
        update={"organization_id": ORG_BETA_ID, "instruction_text": "Authorized tenant update"}
    )
    saved_own = await task_brief_service.save_task_brief(admin_token, sample_brief.id, forged_org_attempt)
    assert saved_own.organization_id == ORG_ALPHA_ID
    assert saved_own.instruction_text == "Authorized tenant update"

    # Unknown client-invented ID raises 404 ResourceNotFoundError without inserting
    missing_brief = TaskBriefFactory.build(organization_id=ORG_ALPHA_ID)
    with pytest.raises(ResourceNotFoundError):
        await task_brief_service.save_task_brief(admin_token, missing_brief.id, missing_brief)
    assert await task_brief_repo.get_task_brief_by_id(missing_brief.id) is None

    # Member cannot create draft
    with pytest.raises(PermissionDeniedError):
        await task_brief_service.create_task_brief_draft(member_token)

    # Non-root without organization_id cannot create or clone
    orphan_admin = TokenData(id=generate_opaque_id(EntityPrefix.USER), role=UserRole.ADMIN, organization_id=None)
    with pytest.raises(PermissionDeniedError):
        await task_brief_service.create_task_brief_draft(orphan_admin)
    with pytest.raises(PermissionDeniedError):
        await task_brief_service.clone_task_brief(orphan_admin, sample_brief.id)

    # Non-root cannot modify or delete a system task brief
    sys_brief = sample_brief.model_copy(
        update={
            "id": generate_opaque_id(EntityPrefix.TASK_BRIEF),
            "organization_id": SystemOrganizations.ROOT_SYSTEM.value,
        }
    )
    await task_brief_repo.create_task_brief(sys_brief)
    with pytest.raises(PermissionDeniedError):
        await task_brief_service.save_task_brief(admin_token, sys_brief.id, sys_brief)
    with pytest.raises(PermissionDeniedError):
        await task_brief_service.delete_task_brief(admin_token, sys_brief.id)


async def test_delete_task_brief_referenced_by_assignment_raises_delete_blocked_by_usage(
    task_brief_service: StudioTaskBriefService,
    task_brief_repo: TaskBriefRepositoryImpl,
    uow: InMemoryUnitOfWork,
    admin_token: TokenData,
    sample_brief: TaskBrief,
) -> None:
    """Verify kernel ON DELETE RESTRICT blocks deleting a TaskBrief referenced by an ExecutionAssignment."""
    await task_brief_repo.create_task_brief(sample_brief)

    active_assignment = ExecutionAssignment(
        id=generate_opaque_id(EntityPrefix.ASSIGNMENT),
        organization_id=ORG_ALPHA_ID,
        created_by=admin_token.id,
        assigned_email="candidate@alpha.fi",
        workflow_id=generate_opaque_id(EntityPrefix.WORKFLOW),
        task_brief_id=sample_brief.id,
        task_brief_snapshot=TaskAssignmentBriefDTO(
            id=sample_brief.id,
            label=sample_brief.label,
            instruction_text=sample_brief.instruction_text,
            source_url=sample_brief.source_url,
        ),
        locked_inputs=WorkflowInputs(dynamic_inputs={}),
        assignee_input_keys=[],
        draft_inputs=WorkflowInputs(dynamic_inputs={}),
        token_hash="a" * 64,
        status=AssignmentStatus.PENDING,
        hard_deadline_at=datetime.now(UTC) + timedelta(hours=4),
        created_at=datetime.now(UTC),
    )
    await uow.entities.upsert_execution_assignment(active_assignment)

    with pytest.raises(AppException) as blocked_exc:
        await task_brief_service.delete_task_brief(admin_token, sample_brief.id)
    assert blocked_exc.value.status_code == 400
    assert blocked_exc.value.details["error_code"] == ErrorCodes.DELETE_BLOCKED_BY_USAGE.value

    # Once assignment no longer references sample_brief.id, deletion succeeds
    unlinked_assignment = active_assignment.model_copy(update={"task_brief_id": None, "task_brief_snapshot": None})
    await uow.entities.upsert_execution_assignment(unlinked_assignment)

    await task_brief_service.delete_task_brief(admin_token, sample_brief.id)
    assert await task_brief_repo.get_task_brief_by_id(sample_brief.id) is None


async def test_delete_tenant_organization_cascades_studio_entities_with_zero_null_promotion(
    uow: InMemoryUnitOfWork,
    sample_brief: TaskBrief,
) -> None:
    """Verify deleting a tenant Organization cascade-deletes its Studio entities without touching ROOT_SYSTEM."""
    now = datetime.now(UTC)
    alpha_org = Organization(
        id=ORG_ALPHA_ID,
        name="Alpha Tenant",
        slug="alpha-tenant",
        created_at=now,
        is_active=True,
        tier="enterprise",
        subscription_status="active",
        quota_limit=1000.0,
        tpm_limit=100000,
        rpm_limit=100,
    )
    system_org = Organization(
        id=SystemOrganizations.ROOT_SYSTEM.value,
        name="System Administration",
        slug="system",
        created_at=now,
        is_active=True,
        tier="system",
        subscription_status="active",
        quota_limit=100000.0,
        tpm_limit=1000000,
        rpm_limit=1000,
    )
    await uow.entities.upsert_organization(alpha_org)
    await uow.entities.upsert_organization(system_org)

    alpha_block = SystemRulePromptBlockFactory.build(organization_id=ORG_ALPHA_ID)
    system_block = SystemRulePromptBlockFactory.build(organization_id=SystemOrganizations.ROOT_SYSTEM.value)
    alpha_step = StepFactory.build(organization_id=ORG_ALPHA_ID)
    alpha_wf = WorkflowFactory.build(organization_id=ORG_ALPHA_ID)
    alpha_prf = OutputProfileFactory.build(workflow_id=alpha_wf.id, organization_id=ORG_ALPHA_ID, content_blocks=[])
    system_brief = sample_brief.model_copy(
        update={
            "id": generate_opaque_id(EntityPrefix.TASK_BRIEF),
            "organization_id": SystemOrganizations.ROOT_SYSTEM.value,
        }
    )

    await uow.entities.upsert_prompt_block(alpha_block)
    await uow.entities.upsert_prompt_block(system_block)
    await uow.entities.upsert_task_brief(sample_brief)
    await uow.entities.upsert_task_brief(system_brief)
    await uow.entities.upsert_step(alpha_step)
    await uow.entities.upsert_workflow(alpha_wf)
    await uow.entities.upsert_output_profile(alpha_prf)

    assert await uow.entities.delete_organization(ORG_ALPHA_ID) is True

    assert await uow.entities.get_prompt_block(alpha_block.id) is None
    assert await uow.entities.get_task_brief(sample_brief.id) is None
    assert await uow.entities.get_step(alpha_step.id) is None
    assert await uow.entities.get_workflow(alpha_wf.id) is None
    assert await uow.entities.get_output_profile(alpha_prf.id) is None

    remaining_block = await uow.entities.get_prompt_block(system_block.id)
    remaining_brief = await uow.entities.get_task_brief(system_brief.id)
    assert remaining_block is not None
    assert remaining_block.organization_id == SystemOrganizations.ROOT_SYSTEM.value
    assert remaining_brief is not None
    assert remaining_brief.organization_id == SystemOrganizations.ROOT_SYSTEM.value
