"""Unit tests for StudioWorkflowService.

Comprehensive unit tests for StudioWorkflowService covering
all branches, system core protection, tenant isolation, cloning, and error states.
"""

from __future__ import annotations

import re
from unittest.mock import AsyncMock

import pytest

from backend_v2.exceptions import AppException, ErrorCodes, PermissionDeniedError, ResourceNotFoundError
from backend_v2.models.auth import SystemOrganizations, TokenData, UserRole
from backend_v2.models.core_base import OPAQUE_STRIPE_ID_REGEX, I18nText, generate_opaque_id
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock, ProtocolPromptBlock
from backend_v2.models.enums import (
    BlockDataType,
    EntityPrefix,
    HistoricalContextMode,
    PromptBlockCategory,
    StepType,
    TargetBlockType,
)
from backend_v2.models.v2_core import MatrixScale, OutputProfile, Step, StepRule, Workflow
from backend_v2.services.studio.workflow_service import StudioWorkflowService
from backend_v2.tests.fakes.in_memory_repositories import (
    InMemoryOutputProfileRepository,
    InMemoryPromptBlockRepository,
    InMemoryWorkflowRepository,
)

pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_workflow_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_output_profile_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_prompt_block_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def workflow_service(
    mock_workflow_repo: AsyncMock, mock_output_profile_repo: AsyncMock, mock_prompt_block_repo: AsyncMock
) -> StudioWorkflowService:
    return StudioWorkflowService(
        workflow_repo=mock_workflow_repo,
        output_profile_repo=mock_output_profile_repo,
        prompt_block_repo=mock_prompt_block_repo,
    )


@pytest.fixture
def root_token() -> TokenData:
    return TokenData(id="root_user", role=UserRole.ROOT)


@pytest.fixture
def admin_token() -> TokenData:
    return TokenData(id="admin_user", role=UserRole.ADMIN, organization_id="org_123")


@pytest.fixture
def other_admin_token() -> TokenData:
    return TokenData(id="admin_other", role=UserRole.ADMIN, organization_id="org_999")


@pytest.fixture
def member_token() -> TokenData:
    return TokenData(id="user1", role=UserRole.MEMBER, organization_id="org_123")


def _valid_step(
    step_id: str = "sp_0123456789abcdef",
    slug: str = "step_slug",
    is_system_core: bool = False,
    org_id: str = "org_123",
) -> Step:
    return Step(
        id=step_id,
        slug=slug,
        name=I18nText(translations={"en": "Test Step"}),
        type=StepType.LLM,
        organization_id=org_id,
        safety="safe",
        model_strategy="fast",
        criteria_block_ids=["blk_0123456789abcdef"],
        extraction_protocol_block_id="blk_0123456789abcdef",
        is_system_core=is_system_core,
    )


def _valid_workflow(
    wf_id: str = "wor_0123456789abcdef",
    slug: str = "wf_slug",
    org_id: str = "org_123",
    status: str = "active",
) -> Workflow:
    return Workflow(
        id=wf_id,
        slug=slug,
        name=I18nText(translations={"en": "Test Workflow"}),
        description=I18nText(translations={"en": "Test Desc"}),
        status=status,
        version=1,
        organization_id=org_id,
        expected_inputs=[],
        steps=[],
        default_profile_id="prf_0123456789abcdef",
        allowed_exports=["pdf"],
        historical_context_mode=HistoricalContextMode.DISABLED,
    )


def _valid_matrix_block(block_id: str = "blk_0123456789abcdef") -> MatrixPromptBlock:
    return MatrixPromptBlock(
        id=block_id,
        slug=f"slug_{block_id}",
        label=I18nText(translations={"en": "Matrix Label"}),
        description=I18nText(translations={"en": "Description"}),
        ai_description="AI desc",
        category_id=PromptBlockCategory.MATRIX,
        type=BlockDataType.FLOAT,
        organization_id="org_123",
        output_extensions=["detailed_gap_analysis", "executive_summary"],
        scales=[MatrixScale(score=1, ai_label="INITIAL", claims=[])],
    )


async def test_list_workflows_empty(
    workflow_service: StudioWorkflowService,
    root_token: TokenData,
    mock_workflow_repo: AsyncMock,
    mock_output_profile_repo: AsyncMock,
) -> None:
    mock_workflow_repo.get_all_workflows.return_value = []
    mock_output_profile_repo.get_all_output_profiles.return_value = []
    res = await workflow_service.list_workflows(root_token)
    assert res == []


async def test_list_workflows_tenant_filtering(
    workflow_service: StudioWorkflowService,
    admin_token: TokenData,
    mock_workflow_repo: AsyncMock,
    mock_output_profile_repo: AsyncMock,
) -> None:
    wf1 = _valid_workflow("wor_0123456789abcdef", org_id="org_123")
    wf2 = _valid_workflow("wor_0123456789fedcba", org_id="org_999")
    mock_workflow_repo.get_all_workflows.return_value = [wf1, wf2]
    mock_output_profile_repo.get_all_output_profiles.return_value = []
    res = await workflow_service.list_workflows(admin_token)
    assert len(res) == 1
    assert res[0].id == "wor_0123456789abcdef"


async def test_get_workflow_not_found(
    workflow_service: StudioWorkflowService, root_token: TokenData, mock_workflow_repo: AsyncMock
) -> None:
    mock_workflow_repo.get_workflow_by_id.return_value = None
    with pytest.raises(ResourceNotFoundError):
        await workflow_service.get_workflow(root_token, "wor_missing111111")


async def test_get_workflow_tenant_isolation_fails(
    workflow_service: StudioWorkflowService, other_admin_token: TokenData, mock_workflow_repo: AsyncMock
) -> None:
    wf = _valid_workflow(org_id="org_123")
    mock_workflow_repo.get_workflow_by_id.return_value = wf
    with pytest.raises(PermissionDeniedError):
        await workflow_service.get_workflow(other_admin_token, wf.id)


async def test_get_workflow_success(
    workflow_service: StudioWorkflowService,
    admin_token: TokenData,
    mock_workflow_repo: AsyncMock,
    mock_output_profile_repo: AsyncMock,
) -> None:
    wf = _valid_workflow(org_id="org_123")
    mock_workflow_repo.get_workflow_by_id.return_value = wf
    mock_output_profile_repo.get_all_output_profiles.return_value = []
    res = await workflow_service.get_workflow(admin_token, wf.id)
    assert res.id == wf.id


async def test_get_workflow_available_extensions(
    workflow_service: StudioWorkflowService,
    admin_token: TokenData,
    mock_workflow_repo: AsyncMock,
    mock_prompt_block_repo: AsyncMock,
    mock_output_profile_repo: AsyncMock,
) -> None:
    wf = _valid_workflow(org_id="org_123")
    step = _valid_step("sp_0123456789abcdef", org_id="org_123")
    wf_with_steps = wf.model_copy(
        update={
            "steps": [
                StepRule(
                    id="sr_0123456789abcdef",
                    task_blueprint="sp_0123456789abcdef",
                )
            ]
        }
    )
    mock_workflow_repo.get_workflow_by_id.return_value = wf_with_steps
    mock_output_profile_repo.get_all_output_profiles.return_value = []
    mock_workflow_repo.get_all_steps.return_value = [step]
    mock_prompt_block_repo.get_prompt_block_by_id.return_value = _valid_matrix_block("blk_0123456789abcdef")

    exts = await workflow_service.get_workflow_available_extensions(admin_token, wf.id)
    assert exts == ["detailed_gap_analysis", "executive_summary"]


async def test_save_workflow_missing_after_save_raises(
    workflow_service: StudioWorkflowService, admin_token: TokenData, mock_workflow_repo: AsyncMock
) -> None:
    wf = _valid_workflow(org_id="org_123")
    mock_workflow_repo.get_workflow_by_id.return_value = None
    with pytest.raises(ResourceNotFoundError):
        await workflow_service.save_workflow(admin_token, wf.id, wf)


async def test_save_workflow_success(
    workflow_service: StudioWorkflowService,
    admin_token: TokenData,
    mock_workflow_repo: AsyncMock,
    mock_output_profile_repo: AsyncMock,
) -> None:
    wf = _valid_workflow(org_id="org_123")
    mock_workflow_repo.get_workflow_by_id.return_value = wf
    mock_output_profile_repo.get_all_output_profiles.return_value = []
    res = await workflow_service.save_workflow(admin_token, wf.id, wf)
    assert res.id == wf.id
    mock_workflow_repo.save_workflow.assert_called_once_with(wf)


async def test_delete_workflow_not_found(
    workflow_service: StudioWorkflowService, admin_token: TokenData, mock_workflow_repo: AsyncMock
) -> None:
    mock_workflow_repo.get_workflow_by_id.return_value = None
    with pytest.raises(ResourceNotFoundError):
        await workflow_service.delete_workflow(admin_token, "wor_missing111111")


async def test_delete_workflow_success(
    workflow_service: StudioWorkflowService, admin_token: TokenData, mock_workflow_repo: AsyncMock
) -> None:
    wf = _valid_workflow(org_id="org_123")
    mock_workflow_repo.get_workflow_by_id.return_value = wf
    await workflow_service.delete_workflow(admin_token, wf.id)
    mock_workflow_repo.delete_workflow.assert_called_once_with(wf.id)


async def test_create_workflow_draft_root(root_token: TokenData) -> None:
    """Tests creating a workflow draft as root user using in-memory stateful persistence."""
    wf_repo = InMemoryWorkflowRepository()
    op_repo = InMemoryOutputProfileRepository()
    pb_repo = InMemoryPromptBlockRepository()
    service = StudioWorkflowService(
        workflow_repo=wf_repo,
        output_profile_repo=op_repo,
        prompt_block_repo=pb_repo,
    )
    res = await service.create_workflow_draft(root_token)
    assert res.status == "draft"
    assert res.organization_id == SystemOrganizations.ROOT_SYSTEM
    assert bool(re.match(OPAQUE_STRIPE_ID_REGEX, res.id))
    assert res.id.startswith(f"{EntityPrefix.WORKFLOW}_")
    assert isinstance(res.name, I18nText)
    assert res.name.translations["en"] == "New Työnkulku"

    persisted = await wf_repo.get_workflow_by_id(res.id)
    assert persisted is not None
    assert persisted.id == res.id
    assert persisted.status == "draft"
    assert persisted.organization_id == SystemOrganizations.ROOT_SYSTEM


async def test_create_workflow_draft_admin(admin_token: TokenData) -> None:
    """Tests creating a workflow draft as admin user with tenant isolation."""
    wf_repo = InMemoryWorkflowRepository()
    op_repo = InMemoryOutputProfileRepository()
    pb_repo = InMemoryPromptBlockRepository()
    service = StudioWorkflowService(
        workflow_repo=wf_repo,
        output_profile_repo=op_repo,
        prompt_block_repo=pb_repo,
    )
    res = await service.create_workflow_draft(admin_token)
    assert res.status == "draft"
    assert res.organization_id == "org_123"
    assert bool(re.match(OPAQUE_STRIPE_ID_REGEX, res.id))
    assert res.id.startswith(f"{EntityPrefix.WORKFLOW}_")
    assert isinstance(res.name, I18nText)
    assert res.name.translations["en"] == "New Työnkulku"
    assert res.name.translations["fi"] == "Uusi työnkulku"

    persisted = await wf_repo.get_workflow_by_id(res.id)
    assert persisted is not None
    assert persisted.id == res.id
    assert persisted.status == "draft"
    assert persisted.organization_id == "org_123"


async def test_clone_workflow_not_found(
    workflow_service: StudioWorkflowService, admin_token: TokenData, mock_workflow_repo: AsyncMock
) -> None:
    mock_workflow_repo.get_workflow_by_id.return_value = None
    with pytest.raises(ResourceNotFoundError):
        await workflow_service.clone_workflow(admin_token, "wor_missing111111")


async def test_clone_workflow_success(admin_token: TokenData) -> None:
    """Tests cloning a workflow with in-memory stateful persistence roundtrip."""
    wf_repo = InMemoryWorkflowRepository()
    op_repo = InMemoryOutputProfileRepository()
    pb_repo = InMemoryPromptBlockRepository()
    service = StudioWorkflowService(
        workflow_repo=wf_repo,
        output_profile_repo=op_repo,
        prompt_block_repo=pb_repo,
    )
    orig_wf = _valid_workflow(wf_id=generate_opaque_id(EntityPrefix.WORKFLOW), org_id="org_123")
    orig_profile = OutputProfile(
        id=generate_opaque_id(EntityPrefix.OUTPUT_PROFILE),
        slug="prof_standard",
        workflow_id=orig_wf.id,
        name=I18nText(translations={"en": "Standard"}),
        target_block_order=[
            TargetBlockType.METADATA_BLOCK,
            TargetBlockType.EXECUTIVE_SUMMARY_BLOCK,
            TargetBlockType.SYNTHESIS_TEXT_BLOCK,
        ],
    )
    orig_wf = orig_wf.model_copy(update={"default_profile_id": orig_profile.id})
    await wf_repo.save_workflow(orig_wf)
    await op_repo.create_output_profile(orig_profile)

    res = await service.clone_workflow(admin_token, orig_wf.id)
    assert res is not None
    assert res.id != orig_wf.id
    assert bool(re.match(OPAQUE_STRIPE_ID_REGEX, res.id))
    assert res.id.startswith(f"{EntityPrefix.WORKFLOW}_")
    assert res.organization_id == "org_123"
    assert isinstance(res.name, I18nText)
    assert res.name.translations["en"] == "Test Workflow (Copy)"

    # Profile clone assertions
    assert res.default_profile_id != orig_profile.id
    assert res.default_profile_id.startswith(f"{EntityPrefix.OUTPUT_PROFILE}_")
    cloned_op = await op_repo.get_output_profile_by_id(res.default_profile_id)
    assert cloned_op is not None
    assert cloned_op.workflow_id == res.id
    assert cloned_op.organization_id == "org_123"

    # Stateful roundtrip verification
    persisted = await wf_repo.get_workflow_by_id(res.id)
    assert persisted is not None
    assert persisted.id == res.id
    assert isinstance(persisted.name, I18nText)
    assert persisted.name.translations["en"] == "Test Workflow (Copy)"


async def test_list_steps_empty(
    workflow_service: StudioWorkflowService, root_token: TokenData, mock_workflow_repo: AsyncMock
) -> None:
    mock_workflow_repo.get_all_steps.return_value = []
    res = await workflow_service.list_steps(root_token)
    assert res == []


async def test_list_steps_tenant_filtering(
    workflow_service: StudioWorkflowService, admin_token: TokenData, mock_workflow_repo: AsyncMock
) -> None:
    s1 = _valid_step("sp_0123456789abcdef", org_id="org_123")
    s2 = _valid_step("sp_0123456789fedcba", org_id="org_999")
    mock_workflow_repo.get_all_steps.return_value = [s1, s2]
    res = await workflow_service.list_steps(admin_token)
    assert len(res) == 1
    assert res[0].id == "sp_0123456789abcdef"


async def test_get_step_not_found(
    workflow_service: StudioWorkflowService, root_token: TokenData, mock_workflow_repo: AsyncMock
) -> None:
    mock_workflow_repo.get_step_by_id.return_value = None
    with pytest.raises(ResourceNotFoundError):
        await workflow_service.get_step(root_token, "sp_missing111111")


async def test_get_step_tenant_isolation_fails(
    workflow_service: StudioWorkflowService, other_admin_token: TokenData, mock_workflow_repo: AsyncMock
) -> None:
    s = _valid_step(org_id="org_123")
    mock_workflow_repo.get_step_by_id.return_value = s
    with pytest.raises(PermissionDeniedError):
        await workflow_service.get_step(other_admin_token, s.id)


async def test_get_step_success(
    workflow_service: StudioWorkflowService, admin_token: TokenData, mock_workflow_repo: AsyncMock
) -> None:
    s = _valid_step(org_id="org_123")
    mock_workflow_repo.get_step_by_id.return_value = s
    res = await workflow_service.get_step(admin_token, s.id)
    assert res.id == s.id


async def test_save_step_missing_after_save_raises(
    workflow_service: StudioWorkflowService, admin_token: TokenData, mock_workflow_repo: AsyncMock
) -> None:
    step = _valid_step(org_id="org_123")
    mock_workflow_repo.get_step_by_id.return_value = None
    with pytest.raises(ResourceNotFoundError):
        await workflow_service.save_step(admin_token, step.id, step)


async def test_save_step_success(
    workflow_service: StudioWorkflowService, admin_token: TokenData, mock_workflow_repo: AsyncMock
) -> None:
    step = _valid_step(org_id="org_123")
    mock_workflow_repo.get_step_by_id.side_effect = [None, step]
    res = await workflow_service.save_step(admin_token, step.id, step)
    assert res.id == step.id
    mock_workflow_repo.save_step.assert_called_once_with(step)


async def test_save_step_protected_system_core_slug_mutation_fails_fast(
    workflow_service: StudioWorkflowService, admin_token: TokenData, mock_workflow_repo: AsyncMock
) -> None:
    existing = _valid_step("sp_0123456789abcdef", slug="orig_slug", is_system_core=True, org_id="org_123")
    mock_workflow_repo.get_step_by_id.return_value = existing

    modified = existing.model_copy(update={"slug": "mutated_slug"})
    with pytest.raises(AppException) as exc_info:
        await workflow_service.save_step(admin_token, existing.id, modified)

    assert exc_info.value.status_code == 403
    assert exc_info.value.details["error_code"] == ErrorCodes.SYSTEM_PROTECTED_RESOURCE.value


async def test_delete_step_not_found(
    workflow_service: StudioWorkflowService, admin_token: TokenData, mock_workflow_repo: AsyncMock
) -> None:
    mock_workflow_repo.get_step_by_id.return_value = None
    with pytest.raises(ResourceNotFoundError):
        await workflow_service.delete_step(admin_token, "sp_missing111111")


async def test_delete_step_protected_system_core_fails_fast(
    workflow_service: StudioWorkflowService, admin_token: TokenData, mock_workflow_repo: AsyncMock
) -> None:
    step_data = _valid_step("sp_0123456789abcdef", is_system_core=True, org_id="org_123")
    mock_workflow_repo.get_step_by_id.return_value = step_data
    with pytest.raises(AppException) as exc_info:
        await workflow_service.delete_step(admin_token, step_data.id)

    assert exc_info.value.status_code == 403
    assert exc_info.value.details["error_code"] == ErrorCodes.SYSTEM_PROTECTED_RESOURCE.value
    mock_workflow_repo.delete_step.assert_not_called()


async def test_delete_step_success(
    workflow_service: StudioWorkflowService, admin_token: TokenData, mock_workflow_repo: AsyncMock
) -> None:
    step_data = _valid_step("sp_0123456789abcdef", is_system_core=False, org_id="org_123")
    mock_workflow_repo.get_step_by_id.return_value = step_data
    await workflow_service.delete_step(admin_token, step_data.id)
    mock_workflow_repo.delete_step.assert_called_once_with(step_data.id, force_delete=False)


async def test_create_step_draft_no_protocol_block_raises(
    workflow_service: StudioWorkflowService, admin_token: TokenData, mock_prompt_block_repo: AsyncMock
) -> None:
    mock_prompt_block_repo.get_all_prompt_blocks.return_value = []
    with pytest.raises(AppException) as exc_info:
        await workflow_service.create_step_draft(admin_token)
    assert exc_info.value.details["error_code"] == ErrorCodes.STATE_INTEGRITY_ERROR


async def test_create_step_draft_success(admin_token: TokenData) -> None:
    """Tests creating a step draft using in-memory stateful persistence."""
    wf_repo = InMemoryWorkflowRepository()
    op_repo = InMemoryOutputProfileRepository()
    pb_repo = InMemoryPromptBlockRepository()
    service = StudioWorkflowService(
        workflow_repo=wf_repo,
        output_profile_repo=op_repo,
        prompt_block_repo=pb_repo,
    )
    proto_block = ProtocolPromptBlock(
        id="blk_0123456789abcdef",
        slug="extraction_protocol_default",
        category_id=PromptBlockCategory.PROTOCOL,
        type=BlockDataType.INSTRUCTION,
        label=I18nText(translations={"en": "Default Protocol"}),
        description=I18nText(translations={"en": "Default Protocol Description"}),
        organization_id="org_123",
        protocol_instructions="Default protocol instruction",
    )
    await pb_repo.create_prompt_block(proto_block)

    res = await service.create_step_draft(admin_token)
    assert res is not None
    assert bool(re.match(OPAQUE_STRIPE_ID_REGEX, res.id))
    assert res.id.startswith(f"{EntityPrefix.STEP}_")
    assert res.organization_id == "org_123"
    assert res.extraction_protocol_block_id == proto_block.id

    persisted = await wf_repo.get_step_by_id(res.id)
    assert persisted is not None
    assert persisted.id == res.id


async def test_clone_step_not_found(
    workflow_service: StudioWorkflowService, admin_token: TokenData, mock_workflow_repo: AsyncMock
) -> None:
    mock_workflow_repo.get_step_by_id.return_value = None
    with pytest.raises(ResourceNotFoundError):
        await workflow_service.clone_step(admin_token, "sp_missing111111")


async def test_clone_step_success(admin_token: TokenData) -> None:
    """Tests cloning a step using in-memory stateful persistence."""
    wf_repo = InMemoryWorkflowRepository()
    op_repo = InMemoryOutputProfileRepository()
    pb_repo = InMemoryPromptBlockRepository()
    service = StudioWorkflowService(
        workflow_repo=wf_repo,
        output_profile_repo=op_repo,
        prompt_block_repo=pb_repo,
    )
    step_data = _valid_step(generate_opaque_id(EntityPrefix.STEP), org_id="org_123")
    await wf_repo.save_step(step_data)

    res = await service.clone_step(admin_token, step_data.id)
    assert res is not None
    assert res.id != step_data.id
    assert bool(re.match(OPAQUE_STRIPE_ID_REGEX, res.id))
    assert res.id.startswith(f"{EntityPrefix.STEP}_")
    assert res.name.translations["en"] == "Test Step (Copy)"
    assert res.organization_id == "org_123"

    persisted = await wf_repo.get_step_by_id(res.id)
    assert persisted is not None
    assert persisted.id == res.id
    assert persisted.name.translations["en"] == "Test Step (Copy)"


async def test_save_workflow_aligns_mismatched_id(
    workflow_service: StudioWorkflowService,
    admin_token: TokenData,
    mock_workflow_repo: AsyncMock,
    mock_output_profile_repo: AsyncMock,
) -> None:
    target_id = "wor_0123456789abcdef"
    wf = _valid_workflow(wf_id="wor_aabbccddeeff0011", org_id="org_123")
    aligned_wf = wf.model_copy(update={"id": target_id})
    mock_workflow_repo.get_workflow_by_id.return_value = aligned_wf
    mock_output_profile_repo.get_all_output_profiles.return_value = []

    res = await workflow_service.save_workflow(admin_token, target_id, wf)
    assert res.id == target_id
    mock_workflow_repo.save_workflow.assert_called_once()
    saved_arg = mock_workflow_repo.save_workflow.call_args[0][0]
    assert saved_arg.id == target_id


async def test_save_step_aligns_mismatched_id(
    workflow_service: StudioWorkflowService, admin_token: TokenData, mock_workflow_repo: AsyncMock
) -> None:
    target_id = "sp_0123456789abcdef"
    step = _valid_step(step_id="sp_aabbccddeeff0011", org_id="org_123")
    aligned_step = step.model_copy(update={"id": target_id})
    mock_workflow_repo.get_step_by_id.side_effect = [None, aligned_step]

    res = await workflow_service.save_step(admin_token, target_id, step)
    assert res.id == target_id
    mock_workflow_repo.save_step.assert_called_once()
    saved_arg = mock_workflow_repo.save_step.call_args[0][0]
    assert saved_arg.id == target_id


async def test_stitch_profiles_attaches_matching_workflow_profiles(
    workflow_service: StudioWorkflowService,
    admin_token: TokenData,
    mock_workflow_repo: AsyncMock,
    mock_output_profile_repo: AsyncMock,
) -> None:
    wf = _valid_workflow(wf_id="wor_0123456789abcdef", org_id="org_123")
    mock_workflow_repo.get_all_workflows.return_value = [wf]
    matching_profile = OutputProfile(
        id="prf_0123456789abcdef",
        workflow_id=wf.id,
        slug="default_profile",
        name=I18nText(translations={"en": "Default"}),
        organization_id="org_123",
        description=I18nText(translations={"en": "Desc"}),
        target_block_order=[],
        matrix_synthesis_groups=[],
    )
    mock_output_profile_repo.get_all_output_profiles.return_value = [matching_profile]

    res = await workflow_service.list_workflows(admin_token)
    assert len(res) == 1
    assert wf.id in res[0].id
    assert matching_profile.id in res[0].output_profiles


async def test_clone_workflow_with_steps_and_profiles(admin_token: TokenData) -> None:
    """Tests cloning a complex workflow with steps, dependencies, input mappings, and output profiles."""
    wf_repo = InMemoryWorkflowRepository()
    op_repo = InMemoryOutputProfileRepository()
    pb_repo = InMemoryPromptBlockRepository()
    service = StudioWorkflowService(
        workflow_repo=wf_repo,
        output_profile_repo=op_repo,
        prompt_block_repo=pb_repo,
    )
    step_rule_1 = StepRule(
        id=generate_opaque_id(EntityPrefix.STEP_REFERENCE),
        task_blueprint="sp_0123456789abcdef",
        depends_on=[],
        input_mappings={"static_key": "raw_val"},
    )
    step_rule_2 = StepRule(
        id=generate_opaque_id(EntityPrefix.STEP_REFERENCE),
        task_blueprint="sp_0123456789abcdef",
        depends_on=[step_rule_1.id],
        input_mappings={"input_a": f"$steps.{step_rule_1.id}.output"},
    )
    wf_id = generate_opaque_id(EntityPrefix.WORKFLOW)
    matching_profile = OutputProfile(
        id=generate_opaque_id(EntityPrefix.OUTPUT_PROFILE),
        workflow_id=wf_id,
        slug="default_profile",
        name=I18nText(translations={"en": "Default"}),
        organization_id="org_123",
        description=I18nText(translations={"en": "Desc"}),
        target_block_order=[],
        matrix_synthesis_groups=[],
    )
    wf = _valid_workflow(wf_id=wf_id, org_id="org_123").model_copy(
        update={
            "name": I18nText(translations={"en": "Complex Pipeline", "fi": "Monimutkainen putki"}),
            "steps": [step_rule_1, step_rule_2],
            "default_profile_id": matching_profile.id,
        }
    )
    await wf_repo.save_workflow(wf)
    await op_repo.create_output_profile(matching_profile)

    res = await service.clone_workflow(admin_token, wf.id)
    assert res is not None
    assert res.id != wf.id
    assert bool(re.match(OPAQUE_STRIPE_ID_REGEX, res.id))
    assert res.id.startswith(f"{EntityPrefix.WORKFLOW}_")
    assert isinstance(res.name, I18nText)
    assert res.name.translations["en"] == "Complex Pipeline (Copy)"
    assert res.name.translations["fi"] == "Monimutkainen putki (Copy)"

    # Step remapping assertions
    assert len(res.steps) == 2
    cloned_s1 = res.steps[0]
    cloned_s2 = res.steps[1]
    assert cloned_s1.id != step_rule_1.id
    assert cloned_s1.id.startswith(f"{EntityPrefix.STEP_REFERENCE}_")
    assert cloned_s2.id != step_rule_2.id
    assert cloned_s2.id.startswith(f"{EntityPrefix.STEP_REFERENCE}_")
    assert cloned_s2.depends_on == [cloned_s1.id]
    assert cloned_s2.input_mappings["input_a"] == f"$steps.{cloned_s1.id}.output"
    assert cloned_s1.input_mappings["static_key"] == "raw_val"

    # Profile clone assertions
    assert res.default_profile_id != matching_profile.id
    assert res.default_profile_id.startswith(f"{EntityPrefix.OUTPUT_PROFILE}_")
    persisted_prof = await op_repo.get_output_profile_by_id(res.default_profile_id)
    assert persisted_prof is not None
    assert persisted_prof.workflow_id == res.id

    # Stateful workflow persistence
    persisted_wf = await wf_repo.get_workflow_by_id(res.id)
    assert persisted_wf is not None
    assert persisted_wf.id == res.id
    assert len(persisted_wf.steps) == 2
    assert persisted_wf.steps[1].depends_on == [persisted_wf.steps[0].id]


async def test_get_workflow_available_extensions_handles_exception(
    workflow_service: StudioWorkflowService,
    admin_token: TokenData,
    mock_workflow_repo: AsyncMock,
    mock_prompt_block_repo: AsyncMock,
    mock_output_profile_repo: AsyncMock,
) -> None:
    step = _valid_step(step_id="sp_0123456789abcdef", org_id="org_123")
    step_rule = StepRule(
        id="sr_1111111111111111",
        task_blueprint=step.id,
        depends_on=[],
        input_mappings={},
    )
    wf = _valid_workflow(org_id="org_123")
    wf = wf.model_copy(update={"steps": [step_rule]})

    mock_workflow_repo.get_workflow_by_id.return_value = wf
    mock_output_profile_repo.get_all_output_profiles.return_value = []
    mock_workflow_repo.get_all_steps.return_value = [step]
    mock_prompt_block_repo.get_prompt_block_by_id.side_effect = AppException(message="Block corrupted", status_code=500)

    exts = await workflow_service.get_workflow_available_extensions(admin_token, wf.id)
    assert exts == []


async def test_list_workflows_corrupted_record_raises_app_exception(
    workflow_service: StudioWorkflowService,
    admin_token: TokenData,
    mock_workflow_repo: AsyncMock,
) -> None:
    mock_workflow_repo.get_all_workflows.return_value = [{"invalid": "data"}]
    with pytest.raises(AppException) as exc_info:
        await workflow_service.list_workflows(admin_token)
    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.STATE_INTEGRITY_ERROR.value


async def test_stitch_profiles_corrupted_profile_raises_app_exception(
    workflow_service: StudioWorkflowService,
    admin_token: TokenData,
    mock_workflow_repo: AsyncMock,
    mock_output_profile_repo: AsyncMock,
) -> None:
    wf = _valid_workflow(org_id="org_123")
    mock_workflow_repo.get_all_workflows.return_value = [wf]
    mock_output_profile_repo.get_all_output_profiles.return_value = [{"invalid": "profile"}]
    with pytest.raises(AppException) as exc_info:
        await workflow_service.list_workflows(admin_token)
    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.STATE_INTEGRITY_ERROR.value


async def test_in_memory_save_workflow_roundtrip(admin_token: TokenData) -> None:
    """Tests saving a workflow using stateful in-memory repository roundtrip."""
    wf_repo = InMemoryWorkflowRepository()
    op_repo = InMemoryOutputProfileRepository()
    pb_repo = InMemoryPromptBlockRepository()
    service = StudioWorkflowService(
        workflow_repo=wf_repo,
        output_profile_repo=op_repo,
        prompt_block_repo=pb_repo,
    )

    initial_wf = _valid_workflow(wf_id="wor_aabbccddeeff0011", org_id="org_123")
    await wf_repo.save_workflow(initial_wf)

    updated_wf = initial_wf.model_copy(
        update={
            "name": I18nText(translations={"en": "Updated Workflow", "fi": "Päivitetty työnkulku"}),
            "description": I18nText(translations={"en": "Updated desc", "fi": "Päivitetty kuvaus"}),
        }
    )

    saved_dto = await service.save_workflow(admin_token, initial_wf.id, updated_wf)
    assert saved_dto.id == initial_wf.id
    assert isinstance(saved_dto.name, I18nText)
    assert saved_dto.name.translations["en"] == "Updated Workflow"

    fetched = await wf_repo.get_workflow_by_id(initial_wf.id)
    assert fetched is not None
    assert fetched.id == initial_wf.id
    assert isinstance(fetched.name, I18nText)
    assert fetched.name.translations["en"] == "Updated Workflow"


async def test_in_memory_save_step_roundtrip(admin_token: TokenData) -> None:
    """Tests saving a step using stateful in-memory repository roundtrip."""
    wf_repo = InMemoryWorkflowRepository()
    op_repo = InMemoryOutputProfileRepository()
    pb_repo = InMemoryPromptBlockRepository()
    service = StudioWorkflowService(
        workflow_repo=wf_repo,
        output_profile_repo=op_repo,
        prompt_block_repo=pb_repo,
    )

    initial_step = _valid_step("sp_aabbccddeeff0011", org_id="org_123")
    await wf_repo.save_step(initial_step)

    updated_step = initial_step.model_copy(
        update={
            "model_strategy": "pro_fast_2026",
            "name": I18nText(translations={"en": "Updated Step", "fi": "Päivitetty askel"}),
        }
    )

    saved = await service.save_step(admin_token, initial_step.id, updated_step)
    assert saved.id == initial_step.id
    assert saved.model_strategy == "pro_fast_2026"

    fetched = await wf_repo.get_step_by_id(initial_step.id)
    assert fetched is not None
    assert fetched.id == initial_step.id
    assert fetched.model_strategy == "pro_fast_2026"


async def test_save_workflow_unauthorized_token_raises_permission_denied(
    workflow_service: StudioWorkflowService,
) -> None:
    """Tests that a non-admin token from another org cannot save a workflow."""
    unauthorized_token = TokenData(
        id="usr_other111111111",
        organization_id="org_other",
        email="other@example.com",
        role=UserRole.MEMBER,
    )
    wf = _valid_workflow(wf_id="wor_aabbccddeeff0011", org_id="org_123")
    with pytest.raises(PermissionDeniedError):
        await workflow_service.save_workflow(unauthorized_token, wf.id, wf)


async def test_save_step_unauthorized_token_raises_permission_denied(
    workflow_service: StudioWorkflowService,
) -> None:
    """Tests that a non-admin token from another org cannot save a step."""
    unauthorized_token = TokenData(
        id="usr_other111111111",
        organization_id="org_other",
        email="other@example.com",
        role=UserRole.MEMBER,
    )
    step = _valid_step("sp_aabbccddeeff0011", org_id="org_123")
    with pytest.raises(PermissionDeniedError):
        await workflow_service.save_step(unauthorized_token, step.id, step)


async def test_save_workflow_malformed_dag_raises_validation_failed(
    workflow_service: StudioWorkflowService, admin_token: TokenData
) -> None:
    """Tests that saving a workflow with a cyclic DAG dependency raises 422 AppException."""
    step1 = StepRule(
        id="rul_1111222233334444",
        task_blueprint="sp_0123456789abcdef",
        depends_on=["rul_5555666677778888"],
        input_mappings={},
    )
    step2 = StepRule(
        id="rul_5555666677778888",
        task_blueprint="sp_0123456789abcdef",
        depends_on=["rul_1111222233334444"],
        input_mappings={},
    )
    cyclic_wf = _valid_workflow(wf_id="wor_aabbccddeeff0011", org_id="org_123").model_copy(
        update={"steps": [step1, step2]}
    )
    with pytest.raises(AppException) as exc_info:
        await workflow_service.save_workflow(admin_token, cyclic_wf.id, cyclic_wf)

    assert exc_info.value.status_code == 422
    assert exc_info.value.details["error_code"] == ErrorCodes.WORKFLOW_COMPILATION_ERROR.value
