"""Unit tests for StudioWorkflowService.

Comprehensive unit tests for StudioWorkflowService covering
all branches, system core protection, tenant isolation, cloning, and error states.
"""

from __future__ import annotations

import re

import pytest

from backend_v2.database.interfaces import get_active_uow
from backend_v2.exceptions import AppException, ErrorCodes, PermissionDeniedError, ResourceNotFoundError
from backend_v2.models.auth import SystemOrganizations, TokenData, UserRole
from backend_v2.models.core_base import OPAQUE_STRIPE_ID_REGEX, I18nText, generate_opaque_id
from backend_v2.models.domain.matrix import MatrixScale
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock, ProtocolPromptBlock
from backend_v2.models.domain.step import Step, StepRule
from backend_v2.models.domain.synthesis import MatrixSynthesisGroup
from backend_v2.models.domain.system_config import SystemConfigMCPGateways, SystemConfigModelRegistry
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.enums import (
    BlockDataType,
    CognitiveTier,
    EntityPrefix,
    HistoricalContextMode,
    PresetView,
    PromptBlockCategory,
    StepFilterScope,
    StepType,
    TargetBlockType,
    XaiExtensionType,
)
from backend_v2.services.studio.output_profile_service import StudioOutputProfileService
from backend_v2.services.studio.prompt_block_service import StudioPromptBlockService
from backend_v2.services.studio.system_config_service import StudioSystemConfigService
from backend_v2.services.studio.task_brief_service import StudioTaskBriefService
from backend_v2.services.studio.workflow_service import StudioWorkflowService
from backend_v2.tests.factories.model_factories import (
    OutputProfileFactory,
    SystemRulePromptBlockFactory,
    TaskBriefFactory,
    WorkflowFactory,
)
from backend_v2.tests.fakes.in_memory_repositories import (
    InMemoryOutputProfileRepository,
    InMemoryPromptBlockRepository,
    InMemorySystemRepository,
    InMemoryTaskBriefRepository,
    InMemoryWorkflowRepository,
)
from backend_v2.tests.fakes.in_memory_uow import InMemoryUnitOfWork

pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_workflow_repo() -> InMemoryWorkflowRepository:
    return InMemoryWorkflowRepository()


@pytest.fixture
def mock_output_profile_repo() -> InMemoryOutputProfileRepository:
    return InMemoryOutputProfileRepository()


@pytest.fixture
def mock_prompt_block_repo() -> InMemoryPromptBlockRepository:
    return InMemoryPromptBlockRepository()


@pytest.fixture
def mock_system_repo() -> InMemorySystemRepository:
    return InMemorySystemRepository()


@pytest.fixture
def workflow_service(
    mock_workflow_repo: InMemoryWorkflowRepository,
    mock_output_profile_repo: InMemoryOutputProfileRepository,
    mock_prompt_block_repo: InMemoryPromptBlockRepository,
    mock_system_repo: InMemorySystemRepository,
) -> StudioWorkflowService:
    return StudioWorkflowService(
        workflow_repo=mock_workflow_repo,
        output_profile_repo=mock_output_profile_repo,
        prompt_block_repo=mock_prompt_block_repo,
        system_repo=mock_system_repo,
    )


@pytest.fixture
def root_token() -> TokenData:
    return TokenData(id="usr_0195f3a00000700a83fd6b3d77c748f4", role=UserRole.ROOT)


@pytest.fixture
def admin_token() -> TokenData:
    return TokenData(
        id="usr_0195f3a0000070008000000000000001",
        role=UserRole.ADMIN,
        organization_id="org_0195f3a0000070008000000000000123",
    )


@pytest.fixture
def other_admin_token() -> TokenData:
    return TokenData(
        id="usr_0195f3a0000070008000000000000002",
        role=UserRole.ADMIN,
        organization_id="org_0195f3a0000070008000000000000999",
    )


@pytest.fixture
def member_token() -> TokenData:
    return TokenData(
        id="usr_0195f3a0000070008000000000000003",
        role=UserRole.MEMBER,
        organization_id="org_0195f3a0000070008000000000000123",
    )


def _valid_step(
    step_id: str = "stp_0195f3a00000700080000123456789ab",
    slug: str = "step_slug",
    is_system_core: bool = False,
    org_id: str = "org_0195f3a0000070008000000000000123",
) -> Step:
    return Step(
        id=step_id,
        slug=slug,
        name=I18nText(translations={"en": "Test Step"}),
        type=StepType.LLM,
        organization_id=org_id,
        safety="safe",
        mcp_tool_params={},
        cognitive_tier=CognitiveTier.FAST,
        criteria_block_ids=["blk_0195f3a00000700080000123456789ab"],
        extraction_protocol_block_id="blk_0195f3a00000700080000123456789ab",
        is_system_core=is_system_core,
    )


def _valid_workflow(
    wf_id: str = "wf_0195f3a00000700080000123456789ab",
    slug: str = "wf_slug",
    org_id: str = "org_0195f3a0000070008000000000000123",
    status: str = "active",
    model_registry_id: str = "mrg_0195f3a0000070008000e26807f3bfa3",
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
        default_profile_id="prf_0195f3a00000700080000123456789ab",
        historical_context_mode=HistoricalContextMode.DISABLED,
        model_registry_id=model_registry_id,
    )


def _valid_matrix_block(block_id: str = "blk_0195f3a00000700080000123456789ab") -> MatrixPromptBlock:
    return MatrixPromptBlock(
        id=block_id,
        slug=f"slug_{block_id}",
        label=I18nText(translations={"en": "Matrix Label"}),
        description=I18nText(translations={"en": "Description"}),
        ai_description="AI desc",
        category_id=PromptBlockCategory.MATRIX,
        type=BlockDataType.FLOAT,
        organization_id="org_0195f3a0000070008000000000000123",
        output_extensions=["detailed_gap_analysis", "executive_summary"],
        scales=[MatrixScale(score=1, ai_label="INITIAL", claims=[])],
    )


async def test_list_workflows_empty(
    workflow_service: StudioWorkflowService,
    root_token: TokenData,
    mock_workflow_repo: InMemoryWorkflowRepository,
    mock_output_profile_repo: InMemoryOutputProfileRepository,
) -> None:
    res = await workflow_service.list_workflows(root_token)
    assert res == []


async def test_list_workflows_tenant_filtering(
    workflow_service: StudioWorkflowService,
    admin_token: TokenData,
    mock_workflow_repo: InMemoryWorkflowRepository,
    mock_output_profile_repo: InMemoryOutputProfileRepository,
) -> None:
    wf1 = _valid_workflow("wf_0195f3a00000700080000123456789ab", org_id="org_0195f3a0000070008000000000000123")
    wf2 = _valid_workflow("wf_0195f3a00000700080000123456789fe", org_id="org_0195f3a0000070008000000000000999")
    await mock_workflow_repo.save_workflow(wf1)
    await mock_workflow_repo.save_workflow(wf2)
    res = await workflow_service.list_workflows(admin_token)
    assert len(res) == 1
    assert res[0].id == "wf_0195f3a00000700080000123456789ab"


async def test_list_workflows_public_and_system_allowed(
    workflow_service: StudioWorkflowService,
    admin_token: TokenData,
    mock_workflow_repo: InMemoryWorkflowRepository,
    mock_output_profile_repo: InMemoryOutputProfileRepository,
) -> None:
    wf_public = _valid_workflow("wf_0195f3a0000070008000000000000001", org_id="org_0195f3a0000070008000000000000999")
    wf_public = wf_public.model_copy(update={"is_public": True})
    wf_system = _valid_workflow(
        "wf_0195f3a0000070008000000000000002",
        org_id="org_0195f3a0000070008000000000000001",
    )
    wf_own = _valid_workflow(
        "wf_0195f3a0000070008000000000000003",
        org_id="org_0195f3a0000070008000000000000123",
    )
    await mock_workflow_repo.save_workflow(wf_public)
    await mock_workflow_repo.save_workflow(wf_system)
    await mock_workflow_repo.save_workflow(wf_own)
    res = await workflow_service.list_workflows(admin_token)
    assert len(res) == 3


async def test_get_workflow_not_found(
    workflow_service: StudioWorkflowService, root_token: TokenData, mock_workflow_repo: InMemoryWorkflowRepository
) -> None:
    with pytest.raises(ResourceNotFoundError):
        await workflow_service.get_workflow(root_token, "wor_missing111111")


async def test_get_workflow_tenant_isolation_fails(
    workflow_service: StudioWorkflowService,
    other_admin_token: TokenData,
    mock_workflow_repo: InMemoryWorkflowRepository,
) -> None:
    wf = _valid_workflow(org_id="org_0195f3a0000070008000000000000123")
    await mock_workflow_repo.save_workflow(wf)
    with pytest.raises(PermissionDeniedError):
        await workflow_service.get_workflow(other_admin_token, wf.id)


async def test_get_workflow_success(
    workflow_service: StudioWorkflowService,
    admin_token: TokenData,
    mock_workflow_repo: InMemoryWorkflowRepository,
    mock_output_profile_repo: InMemoryOutputProfileRepository,
) -> None:
    wf = _valid_workflow(org_id="org_0195f3a0000070008000000000000123")
    await mock_workflow_repo.save_workflow(wf)
    res = await workflow_service.get_workflow(admin_token, wf.id)
    assert res.id == wf.id


async def test_get_workflow_available_extensions(
    workflow_service: StudioWorkflowService,
    admin_token: TokenData,
    mock_workflow_repo: InMemoryWorkflowRepository,
    mock_prompt_block_repo: InMemoryPromptBlockRepository,
    mock_output_profile_repo: InMemoryOutputProfileRepository,
) -> None:
    wf = _valid_workflow(org_id="org_0195f3a0000070008000000000000123")
    step = _valid_step("stp_0195f3a00000700080000123456789ab", org_id="org_0195f3a0000070008000000000000123")
    wf_with_steps = wf.model_copy(
        update={
            "steps": [
                StepRule(
                    id="sr_0195f3a00000700080000123456789ab",
                    task_blueprint="stp_0195f3a00000700080000123456789ab",
                )
            ]
        }
    )
    await mock_workflow_repo.save_workflow(wf_with_steps)
    await mock_workflow_repo.save_step(step)
    await mock_prompt_block_repo.create_prompt_block(_valid_matrix_block("blk_0195f3a00000700080000123456789ab"))

    exts = await workflow_service.get_workflow_available_extensions(admin_token, wf.id)
    assert exts == ["detailed_gap_analysis", "executive_summary"]


async def test_save_workflow_missing_after_save_raises(
    workflow_service: StudioWorkflowService, admin_token: TokenData, mock_workflow_repo: InMemoryWorkflowRepository
) -> None:
    wf = _valid_workflow(org_id="org_0195f3a0000070008000000000000123")
    mock_workflow_repo.inject_fault(
        "get_workflow_by_id",
        ResourceNotFoundError(resource_type="workflow", resource_id=wf.id),
    )
    try:
        with pytest.raises(ResourceNotFoundError):
            await workflow_service.save_workflow(admin_token, wf.id, wf)
        with pytest.raises(ResourceNotFoundError):
            await workflow_service.create_workflow_draft(admin_token)
    finally:
        mock_workflow_repo.clear_faults()


async def test_save_workflow_success(
    workflow_service: StudioWorkflowService,
    admin_token: TokenData,
    mock_workflow_repo: InMemoryWorkflowRepository,
    mock_output_profile_repo: InMemoryOutputProfileRepository,
) -> None:
    wf = _valid_workflow(org_id="org_0195f3a0000070008000000000000123")
    await mock_workflow_repo.save_workflow(wf)
    res = await workflow_service.save_workflow(admin_token, wf.id, wf)
    assert res.id == wf.id
    persisted = await mock_workflow_repo.get_workflow_by_id(wf.id)
    assert persisted is not None
    assert persisted.id == wf.id


async def test_delete_workflow_not_found(
    workflow_service: StudioWorkflowService, admin_token: TokenData, mock_workflow_repo: InMemoryWorkflowRepository
) -> None:
    with pytest.raises(ResourceNotFoundError):
        await workflow_service.delete_workflow(admin_token, "wor_missing111111")


async def test_delete_workflow_success(
    workflow_service: StudioWorkflowService, admin_token: TokenData, mock_workflow_repo: InMemoryWorkflowRepository
) -> None:
    wf = _valid_workflow(org_id="org_0195f3a0000070008000000000000123")
    await mock_workflow_repo.save_workflow(wf)
    await workflow_service.delete_workflow(admin_token, wf.id)
    persisted = await mock_workflow_repo.get_workflow_by_id(wf.id)
    assert persisted is None


async def test_create_workflow_draft_root(root_token: TokenData) -> None:
    """Tests creating a workflow draft as root user using in-memory stateful persistence."""
    wf_repo = InMemoryWorkflowRepository()
    op_repo = InMemoryOutputProfileRepository()
    pb_repo = InMemoryPromptBlockRepository()
    sys_repo = InMemorySystemRepository()
    service = StudioWorkflowService(
        workflow_repo=wf_repo,
        output_profile_repo=op_repo,
        prompt_block_repo=pb_repo,
        system_repo=sys_repo,
    )
    res = await service.create_workflow_draft(root_token)
    assert res.status == "draft"
    first_reg = (await sys_repo.get_all_model_registries())[0]
    assert res.model_registry_id == first_reg.id
    first_gw = (await sys_repo.get_all_mcp_gateways())[0]
    assert res.mcp_gateway_id == first_gw.id
    assert res.default_profile_id is None
    assert res.organization_id == SystemOrganizations.ROOT_SYSTEM
    assert bool(re.match(OPAQUE_STRIPE_ID_REGEX, res.id))
    assert res.id.startswith(f"{EntityPrefix.WORKFLOW}_")
    assert isinstance(res.name, I18nText)
    assert res.name.translations["en"] == "New Workflow"

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
    sys_repo = InMemorySystemRepository()
    service = StudioWorkflowService(
        workflow_repo=wf_repo,
        output_profile_repo=op_repo,
        prompt_block_repo=pb_repo,
        system_repo=sys_repo,
    )
    res = await service.create_workflow_draft(admin_token)
    assert res.status == "draft"
    first_reg = (await sys_repo.get_all_model_registries())[0]
    assert res.model_registry_id == first_reg.id
    first_gw = (await sys_repo.get_all_mcp_gateways())[0]
    assert res.mcp_gateway_id == first_gw.id
    assert res.default_profile_id is None
    assert res.organization_id == "org_0195f3a0000070008000000000000123"
    assert bool(re.match(OPAQUE_STRIPE_ID_REGEX, res.id))
    assert res.id.startswith(f"{EntityPrefix.WORKFLOW}_")
    assert isinstance(res.name, I18nText)
    assert res.name.translations["en"] == "New Workflow"
    assert res.name.translations["fi"] == "Uusi työnkulku"

    persisted = await wf_repo.get_workflow_by_id(res.id)
    assert persisted is not None
    assert persisted.id == res.id
    assert persisted.status == "draft"
    assert persisted.organization_id == "org_0195f3a0000070008000000000000123"


async def test_clone_workflow_not_found(
    workflow_service: StudioWorkflowService, admin_token: TokenData, mock_workflow_repo: InMemoryWorkflowRepository
) -> None:
    with pytest.raises(ResourceNotFoundError):
        await workflow_service.clone_workflow(admin_token, "wor_missing111111")


async def test_clone_workflow_success(admin_token: TokenData) -> None:
    """Tests cloning a workflow with in-memory stateful persistence roundtrip."""
    wf_repo = InMemoryWorkflowRepository()
    op_repo = InMemoryOutputProfileRepository()
    pb_repo = InMemoryPromptBlockRepository()
    sys_repo = InMemorySystemRepository()
    service = StudioWorkflowService(
        workflow_repo=wf_repo,
        output_profile_repo=op_repo,
        prompt_block_repo=pb_repo,
        system_repo=sys_repo,
    )
    orig_wf = _valid_workflow(
        wf_id=generate_opaque_id(EntityPrefix.WORKFLOW), org_id="org_0195f3a0000070008000000000000123"
    )
    orig_profile = OutputProfile(
        id=generate_opaque_id(EntityPrefix.OUTPUT_PROFILE),
        slug="prof_standard",
        workflow_id=orig_wf.id,
        organization_id=orig_wf.organization_id,
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
    assert res.organization_id == "org_0195f3a0000070008000000000000123"
    assert isinstance(res.name, I18nText)
    assert res.name.translations["en"] == "Test Workflow (Copy)"

    # Profile clone assertions
    assert res.default_profile_id is not None
    assert res.default_profile_id != orig_profile.id
    assert res.default_profile_id.startswith(f"{EntityPrefix.OUTPUT_PROFILE}_")
    cloned_op = await op_repo.get_output_profile_by_id(res.default_profile_id)
    assert cloned_op is not None
    assert cloned_op.workflow_id == res.id
    assert cloned_op.organization_id == "org_0195f3a0000070008000000000000123"

    # Stateful roundtrip verification
    persisted = await wf_repo.get_workflow_by_id(res.id)
    assert persisted is not None
    assert persisted.id == res.id
    assert isinstance(persisted.name, I18nText)
    assert persisted.name.translations["en"] == "Test Workflow (Copy)"


async def test_list_steps_empty(
    workflow_service: StudioWorkflowService, root_token: TokenData, mock_workflow_repo: InMemoryWorkflowRepository
) -> None:
    res = await workflow_service.list_steps(root_token)
    assert res == []


async def test_list_steps_tenant_filtering(
    workflow_service: StudioWorkflowService, admin_token: TokenData, mock_workflow_repo: InMemoryWorkflowRepository
) -> None:
    s1 = _valid_step("stp_0195f3a00000700080000123456789ab", org_id="org_0195f3a0000070008000000000000123")
    s2 = _valid_step("stp_0195f3a00000700080000123456789fe", org_id="org_0195f3a0000070008000000000000999")
    await mock_workflow_repo.save_step(s1)
    await mock_workflow_repo.save_step(s2)
    res = await workflow_service.list_steps(admin_token)
    assert len(res) == 1
    assert res[0].id == "stp_0195f3a00000700080000123456789ab"


async def test_list_steps_scope_filtering(
    workflow_service: StudioWorkflowService, root_token: TokenData, mock_workflow_repo: InMemoryWorkflowRepository
) -> None:
    s_spec = _valid_step("stp_0195f3a00000700080000123456789ab", is_system_core=False)
    s_core = _valid_step("stp_0195f3a0000070008000c4a5a1d15c00", is_system_core=True)
    await mock_workflow_repo.save_step(s_spec)
    await mock_workflow_repo.save_step(s_core)

    res_default = await workflow_service.list_steps(root_token)
    assert len(res_default) == 1
    assert res_default[0].id == "stp_0195f3a00000700080000123456789ab"

    res_specialists = await workflow_service.list_steps(root_token, scope=StepFilterScope.SPECIALISTS)
    assert len(res_specialists) == 1
    assert res_specialists[0].id == "stp_0195f3a00000700080000123456789ab"

    res_core = await workflow_service.list_steps(root_token, scope=StepFilterScope.SYSTEM_CORE)
    assert len(res_core) == 1
    assert res_core[0].id == "stp_0195f3a0000070008000c4a5a1d15c00"

    res_all = await workflow_service.list_steps(root_token, scope=StepFilterScope.ALL)
    assert len(res_all) == 2


async def test_get_step_not_found(
    workflow_service: StudioWorkflowService, root_token: TokenData, mock_workflow_repo: InMemoryWorkflowRepository
) -> None:
    with pytest.raises(ResourceNotFoundError):
        await workflow_service.get_step(root_token, "sp_missing111111")


async def test_get_step_tenant_isolation_fails(
    workflow_service: StudioWorkflowService,
    other_admin_token: TokenData,
    mock_workflow_repo: InMemoryWorkflowRepository,
) -> None:
    s = _valid_step(org_id="org_0195f3a0000070008000000000000123")
    await mock_workflow_repo.save_step(s)
    with pytest.raises(PermissionDeniedError):
        await workflow_service.get_step(other_admin_token, s.id)


async def test_get_step_success(
    workflow_service: StudioWorkflowService, admin_token: TokenData, mock_workflow_repo: InMemoryWorkflowRepository
) -> None:
    s = _valid_step(org_id="org_0195f3a0000070008000000000000123")
    await mock_workflow_repo.save_step(s)
    res = await workflow_service.get_step(admin_token, s.id)
    assert res.id == s.id


async def test_save_step_missing_after_save_raises(
    workflow_service: StudioWorkflowService, admin_token: TokenData, mock_workflow_repo: InMemoryWorkflowRepository
) -> None:
    step = _valid_step(org_id="org_0195f3a0000070008000000000000123")
    mock_workflow_repo.inject_fault(
        "get_step_by_id",
        ResourceNotFoundError(resource_type="step", resource_id=step.id),
    )
    try:
        with pytest.raises(ResourceNotFoundError):
            await workflow_service.save_step(admin_token, step.id, step)
    finally:
        mock_workflow_repo.clear_faults()


async def test_save_step_success(
    workflow_service: StudioWorkflowService, admin_token: TokenData, mock_workflow_repo: InMemoryWorkflowRepository
) -> None:
    step = _valid_step(org_id="org_0195f3a0000070008000000000000123")
    await mock_workflow_repo.save_step(step)
    res = await workflow_service.save_step(admin_token, step.id, step)
    assert res.id == step.id
    persisted = await mock_workflow_repo.get_step_by_id(step.id)
    assert persisted is not None
    assert persisted.id == step.id


async def test_save_step_protected_system_core_slug_mutation_fails_fast(
    workflow_service: StudioWorkflowService, admin_token: TokenData, mock_workflow_repo: InMemoryWorkflowRepository
) -> None:
    existing = _valid_step(
        "stp_0195f3a00000700080000123456789ab",
        slug="orig_slug",
        is_system_core=True,
        org_id="org_0195f3a0000070008000000000000123",
    )
    await mock_workflow_repo.save_step(existing)

    modified = existing.model_copy(update={"slug": "mutated_slug"})
    with pytest.raises(AppException) as exc_info:
        await workflow_service.save_step(admin_token, existing.id, modified)

    assert exc_info.value.status_code == 403
    assert exc_info.value.details["error_code"] == ErrorCodes.SYSTEM_PROTECTED_RESOURCE.value


async def test_delete_step_not_found(
    workflow_service: StudioWorkflowService, admin_token: TokenData, mock_workflow_repo: InMemoryWorkflowRepository
) -> None:
    with pytest.raises(ResourceNotFoundError):
        await workflow_service.delete_step(admin_token, "sp_missing111111")


async def test_delete_step_protected_system_core_fails_fast(
    workflow_service: StudioWorkflowService, admin_token: TokenData, mock_workflow_repo: InMemoryWorkflowRepository
) -> None:
    step_data = _valid_step(
        "stp_0195f3a00000700080000123456789ab", is_system_core=True, org_id="org_0195f3a0000070008000000000000123"
    )
    await mock_workflow_repo.save_step(step_data)
    with pytest.raises(AppException) as exc_info:
        await workflow_service.delete_step(admin_token, step_data.id)

    assert exc_info.value.status_code == 403
    assert exc_info.value.details["error_code"] == ErrorCodes.SYSTEM_PROTECTED_RESOURCE.value
    persisted = await mock_workflow_repo.get_step_by_id(step_data.id)
    assert persisted is not None


async def test_delete_step_success(
    workflow_service: StudioWorkflowService, admin_token: TokenData, mock_workflow_repo: InMemoryWorkflowRepository
) -> None:
    step_data = _valid_step(
        "stp_0195f3a00000700080000123456789ab", is_system_core=False, org_id="org_0195f3a0000070008000000000000123"
    )
    await mock_workflow_repo.save_step(step_data)
    await workflow_service.delete_step(admin_token, step_data.id)
    persisted = await mock_workflow_repo.get_step_by_id(step_data.id)
    assert persisted is None


async def test_create_step_draft_no_protocol_block_raises(
    workflow_service: StudioWorkflowService,
    admin_token: TokenData,
    mock_prompt_block_repo: InMemoryPromptBlockRepository,
) -> None:
    with pytest.raises(AppException) as exc_info:
        await workflow_service.create_step_draft(admin_token)
    assert exc_info.value.details["error_code"] == ErrorCodes.STATE_INTEGRITY_ERROR
    with pytest.raises(AppException) as exc_info:
        await workflow_service.create_step_draft(admin_token)
    assert exc_info.value.details["error_code"] == ErrorCodes.STATE_INTEGRITY_ERROR


async def test_create_step_draft_success(admin_token: TokenData) -> None:
    """Tests creating a step draft using in-memory stateful persistence."""
    wf_repo = InMemoryWorkflowRepository()
    op_repo = InMemoryOutputProfileRepository()
    pb_repo = InMemoryPromptBlockRepository()
    sys_repo = InMemorySystemRepository()
    service = StudioWorkflowService(
        workflow_repo=wf_repo,
        output_profile_repo=op_repo,
        prompt_block_repo=pb_repo,
        system_repo=sys_repo,
    )
    proto_block = ProtocolPromptBlock(
        id="blk_0195f3a00000700080000123456789ab",
        slug="extraction_protocol_default",
        category_id=PromptBlockCategory.PROTOCOL,
        type=BlockDataType.INSTRUCTION,
        label=I18nText(translations={"en": "Default Protocol"}),
        description=I18nText(translations={"en": "Default Protocol Description"}),
        organization_id="org_0195f3a0000070008000000000000123",
        protocol_instructions="Default protocol instruction",
    )
    await pb_repo.create_prompt_block(proto_block)
    with pytest.raises(AppException) as missing_crit_exc:
        await service.create_step_draft(admin_token)
    assert missing_crit_exc.value.details["error_code"] == ErrorCodes.STATE_INTEGRITY_ERROR
    matrix_block = _valid_matrix_block("blk_0195f3a0000070008000440a5fef9331")
    await pb_repo.create_prompt_block(matrix_block)

    res = await service.create_step_draft(admin_token)
    assert res is not None
    assert bool(re.match(OPAQUE_STRIPE_ID_REGEX, res.id))
    assert res.id.startswith(f"{EntityPrefix.STEP}_")
    assert res.organization_id == "org_0195f3a0000070008000000000000123"
    assert res.extraction_protocol_block_id == proto_block.id
    assert res.criteria_block_ids == [matrix_block.id]

    persisted = await wf_repo.get_step_by_id(res.id)
    assert persisted is not None
    assert persisted.id == res.id


async def test_clone_step_not_found(
    workflow_service: StudioWorkflowService, admin_token: TokenData, mock_workflow_repo: InMemoryWorkflowRepository
) -> None:
    with pytest.raises(ResourceNotFoundError):
        await workflow_service.clone_step(admin_token, "sp_missing111111")


async def test_clone_step_success(admin_token: TokenData) -> None:
    """Tests cloning a step using in-memory stateful persistence."""
    wf_repo = InMemoryWorkflowRepository()
    op_repo = InMemoryOutputProfileRepository()
    pb_repo = InMemoryPromptBlockRepository()
    sys_repo = InMemorySystemRepository()
    service = StudioWorkflowService(
        workflow_repo=wf_repo,
        output_profile_repo=op_repo,
        prompt_block_repo=pb_repo,
        system_repo=sys_repo,
    )
    step_data = _valid_step(generate_opaque_id(EntityPrefix.STEP), org_id="org_0195f3a0000070008000000000000123")
    await wf_repo.save_step(step_data)

    res = await service.clone_step(admin_token, step_data.id)
    assert res is not None
    assert res.id != step_data.id
    assert bool(re.match(OPAQUE_STRIPE_ID_REGEX, res.id))
    assert res.id.startswith(f"{EntityPrefix.STEP}_")
    assert res.slug == step_data.slug
    assert res.name.translations["en"] == "Test Step (Copy)"
    assert res.organization_id == "org_0195f3a0000070008000000000000123"

    persisted = await wf_repo.get_step_by_id(res.id)
    assert persisted is not None
    assert persisted.id == res.id
    assert persisted.name.translations["en"] == "Test Step (Copy)"


async def test_save_workflow_aligns_mismatched_id(
    workflow_service: StudioWorkflowService,
    admin_token: TokenData,
    mock_workflow_repo: InMemoryWorkflowRepository,
    mock_output_profile_repo: InMemoryOutputProfileRepository,
) -> None:
    target_id = "wf_0195f3a00000700080000123456789ab"
    await mock_workflow_repo.save_workflow(
        _valid_workflow(wf_id=target_id, org_id="org_0195f3a0000070008000000000000123")
    )
    wf = _valid_workflow(wf_id="wf_0195f3a0000070008000aabbccddeeff", org_id="org_0195f3a0000070008000000000000123")

    res = await workflow_service.save_workflow(admin_token, target_id, wf)
    assert res.id == target_id
    persisted = await mock_workflow_repo.get_workflow_by_id(target_id)
    assert persisted is not None
    assert persisted.id == target_id


async def test_save_step_aligns_mismatched_id(
    workflow_service: StudioWorkflowService, admin_token: TokenData, mock_workflow_repo: InMemoryWorkflowRepository
) -> None:
    target_id = "stp_0195f3a00000700080000123456789ab"
    await mock_workflow_repo.save_step(_valid_step(step_id=target_id, org_id="org_0195f3a0000070008000000000000123"))
    step = _valid_step(step_id="stp_0195f3a0000070008000aabbccddeeff", org_id="org_0195f3a0000070008000000000000123")

    res = await workflow_service.save_step(admin_token, target_id, step)
    assert res.id == target_id
    persisted = await mock_workflow_repo.get_step_by_id(target_id)
    assert persisted is not None
    assert persisted.id == target_id


async def test_stitch_profiles_attaches_matching_workflow_profiles(
    workflow_service: StudioWorkflowService,
    admin_token: TokenData,
    mock_workflow_repo: InMemoryWorkflowRepository,
    mock_output_profile_repo: InMemoryOutputProfileRepository,
) -> None:
    wf = _valid_workflow(wf_id="wf_0195f3a00000700080000123456789ab", org_id="org_0195f3a0000070008000000000000123")
    await mock_workflow_repo.save_workflow(wf)
    matching_profile = OutputProfile(
        id="prf_0195f3a00000700080000123456789ab",
        workflow_id=wf.id,
        slug="default_profile",
        name=I18nText(translations={"en": "Default"}),
        organization_id="org_0195f3a0000070008000000000000123",
        description=I18nText(translations={"en": "Desc"}),
        target_block_order=[],
        matrix_synthesis_groups=[],
    )
    await mock_output_profile_repo.create_output_profile(matching_profile)

    res = await workflow_service.list_workflows(admin_token)
    assert len(res) == 1
    assert wf.id in res[0].id
    assert matching_profile.id in res[0].output_profiles
    assert matching_profile.id in res[0].output_profiles


async def test_clone_workflow_with_steps_and_profiles(admin_token: TokenData) -> None:
    """Tests cloning a complex workflow with steps, dependencies, input mappings, and output profiles."""
    wf_repo = InMemoryWorkflowRepository()
    op_repo = InMemoryOutputProfileRepository()
    pb_repo = InMemoryPromptBlockRepository()
    sys_repo = InMemorySystemRepository()
    service = StudioWorkflowService(
        workflow_repo=wf_repo,
        output_profile_repo=op_repo,
        prompt_block_repo=pb_repo,
        system_repo=sys_repo,
    )
    step_rule_1 = StepRule(
        id=generate_opaque_id(EntityPrefix.STEP_REFERENCE),
        task_blueprint="stp_0195f3a00000700080000123456789ab",
        depends_on=[],
        input_mappings={"static_key": "raw_val"},
    )
    step_rule_2 = StepRule(
        id=generate_opaque_id(EntityPrefix.STEP_REFERENCE),
        task_blueprint="stp_0195f3a00000700080000123456789ab",
        depends_on=[step_rule_1.id],
        input_mappings={"input_a": f"$steps.{step_rule_1.id}.output"},
    )
    wf_id = generate_opaque_id(EntityPrefix.WORKFLOW)
    matching_profile = OutputProfile(
        id=generate_opaque_id(EntityPrefix.OUTPUT_PROFILE),
        workflow_id=wf_id,
        slug="default_profile",
        name=I18nText(translations={"en": "Default"}),
        organization_id="org_0195f3a0000070008000000000000123",
        description=I18nText(translations={"en": "Desc"}),
        target_block_order=[],
        matrix_synthesis_groups=[],
    )
    wf = _valid_workflow(wf_id=wf_id, org_id="org_0195f3a0000070008000000000000123").model_copy(
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
    assert res.default_profile_id is not None
    assert res.default_profile_id != matching_profile.id
    assert res.default_profile_id.startswith(f"{EntityPrefix.OUTPUT_PROFILE}_")
    cloned_prof_id = res.default_profile_id
    persisted_prof = await op_repo.get_output_profile_by_id(cloned_prof_id)
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
    mock_workflow_repo: InMemoryWorkflowRepository,
    mock_prompt_block_repo: InMemoryPromptBlockRepository,
    mock_output_profile_repo: InMemoryOutputProfileRepository,
) -> None:
    step = _valid_step(step_id="stp_0195f3a00000700080000123456789ab", org_id="org_0195f3a0000070008000000000000123")
    step_rule = StepRule(
        id="sr_0195f3a0000070008000111111111111",
        task_blueprint=step.id,
        depends_on=[],
        input_mappings={},
    )
    wf = _valid_workflow(org_id="org_0195f3a0000070008000000000000123")
    wf = wf.model_copy(update={"steps": [step_rule]})

    await mock_workflow_repo.save_workflow(wf)
    await mock_workflow_repo.save_step(step)
    mock_prompt_block_repo.inject_fault(
        "get_prompt_block_by_id",
        AppException(message="Block corrupted", status_code=500),
    )
    try:
        with pytest.raises(AppException) as exc_info:
            await workflow_service.get_workflow_available_extensions(admin_token, wf.id)
        assert exc_info.value.status_code == 500
        assert exc_info.value.details["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value
    finally:
        mock_prompt_block_repo.clear_faults()


async def test_list_workflows_corrupted_record_raises_app_exception(
    workflow_service: StudioWorkflowService,
    admin_token: TokenData,
    mock_workflow_repo: InMemoryWorkflowRepository,
) -> None:
    mock_workflow_repo.inject_fault(
        "get_all_workflows",
        AppException(
            message="Database integrity error: Workflow corrupted failed strict validation.",
            status_code=500,
            details={"error_code": ErrorCodes.STATE_INTEGRITY_ERROR.value},
        ),
    )
    try:
        with pytest.raises(AppException) as exc_info:
            await workflow_service.list_workflows(admin_token)
        assert exc_info.value.status_code == 500
        assert exc_info.value.details["error_code"] == ErrorCodes.STATE_INTEGRITY_ERROR.value
    finally:
        mock_workflow_repo.clear_faults()


async def test_stitch_profiles_corrupted_profile_raises_app_exception(
    workflow_service: StudioWorkflowService,
    admin_token: TokenData,
    mock_workflow_repo: InMemoryWorkflowRepository,
    mock_output_profile_repo: InMemoryOutputProfileRepository,
) -> None:
    wf = _valid_workflow(org_id="org_0195f3a0000070008000000000000123")
    await mock_workflow_repo.save_workflow(wf)
    mock_output_profile_repo.inject_fault(
        "get_all_output_profiles",
        AppException(
            message="Database integrity error: OutputProfile corrupted failed strict validation.",
            status_code=500,
            details={"error_code": ErrorCodes.STATE_INTEGRITY_ERROR.value},
        ),
    )
    try:
        with pytest.raises(AppException) as exc_info:
            await workflow_service.list_workflows(admin_token)
        assert exc_info.value.status_code == 500
        assert exc_info.value.details["error_code"] == ErrorCodes.STATE_INTEGRITY_ERROR.value
    finally:
        mock_output_profile_repo.clear_faults()


async def test_in_memory_save_workflow_roundtrip(admin_token: TokenData) -> None:
    """Tests saving a workflow using stateful in-memory repository roundtrip."""
    wf_repo = InMemoryWorkflowRepository()
    op_repo = InMemoryOutputProfileRepository()
    pb_repo = InMemoryPromptBlockRepository()
    sys_repo = InMemorySystemRepository()
    service = StudioWorkflowService(
        workflow_repo=wf_repo,
        output_profile_repo=op_repo,
        prompt_block_repo=pb_repo,
        system_repo=sys_repo,
    )

    initial_wf = _valid_workflow(
        wf_id="wf_0195f3a0000070008000aabbccddeeff", org_id="org_0195f3a0000070008000000000000123"
    )
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
    sys_repo = InMemorySystemRepository()
    service = StudioWorkflowService(
        workflow_repo=wf_repo,
        output_profile_repo=op_repo,
        prompt_block_repo=pb_repo,
        system_repo=sys_repo,
    )

    initial_step = _valid_step("stp_0195f3a0000070008000aabbccddeeff", org_id="org_0195f3a0000070008000000000000123")
    await wf_repo.save_step(initial_step)

    updated_step = initial_step.model_copy(
        update={
            "cognitive_tier": CognitiveTier.FAST,
            "name": I18nText(translations={"en": "Updated Step", "fi": "Päivitetty askel"}),
        }
    )

    saved = await service.save_step(admin_token, initial_step.id, updated_step)
    assert saved.id == initial_step.id
    assert saved.cognitive_tier == CognitiveTier.FAST

    fetched = await wf_repo.get_step_by_id(initial_step.id)
    assert fetched is not None
    assert fetched.id == initial_step.id
    assert fetched.cognitive_tier == CognitiveTier.FAST


async def test_save_workflow_unauthorized_token_raises_permission_denied(
    workflow_service: StudioWorkflowService,
    mock_workflow_repo: InMemoryWorkflowRepository,
) -> None:
    """Tests that a non-admin token from another org cannot save a workflow."""
    unauthorized_token = TokenData(
        id="usr_0195f3a0000070008000000000000004",
        organization_id="org_0195f3a0000070008000000000000888",
        email="other@example.com",
        role=UserRole.MEMBER,
    )
    wf = _valid_workflow(wf_id="wf_0195f3a0000070008000aabbccddeeff", org_id="org_0195f3a0000070008000000000000123")
    await mock_workflow_repo.save_workflow(wf)
    with pytest.raises(PermissionDeniedError):
        await workflow_service.save_workflow(unauthorized_token, wf.id, wf)


async def test_save_step_unauthorized_token_raises_permission_denied(
    workflow_service: StudioWorkflowService,
    mock_workflow_repo: InMemoryWorkflowRepository,
) -> None:
    """Tests that a non-admin token from another org cannot save a step."""
    unauthorized_token = TokenData(
        id="usr_0195f3a0000070008000000000000004",
        organization_id="org_0195f3a0000070008000000000000888",
        email="other@example.com",
        role=UserRole.MEMBER,
    )
    step = _valid_step("stp_0195f3a0000070008000aabbccddeeff", org_id="org_0195f3a0000070008000000000000123")
    await mock_workflow_repo.save_step(step)
    with pytest.raises(PermissionDeniedError):
        await workflow_service.save_step(unauthorized_token, step.id, step)


async def test_save_workflow_malformed_dag_raises_validation_failed(
    workflow_service: StudioWorkflowService,
    admin_token: TokenData,
    mock_workflow_repo: InMemoryWorkflowRepository,
) -> None:
    """Tests that saving a workflow with a cyclic DAG dependency raises 422 AppException."""
    step1 = StepRule(
        id="sr_0195f3a0000070008000111122223333",
        task_blueprint="stp_0195f3a00000700080000123456789ab",
        depends_on=["sr_0195f3a0000070008000555566667777"],
        input_mappings={},
    )
    step2 = StepRule(
        id="sr_0195f3a0000070008000555566667777",
        task_blueprint="stp_0195f3a00000700080000123456789ab",
        depends_on=["sr_0195f3a0000070008000111122223333"],
        input_mappings={},
    )
    base_wf = _valid_workflow(
        wf_id="wf_0195f3a0000070008000aabbccddeeff", org_id="org_0195f3a0000070008000000000000123"
    )
    await mock_workflow_repo.save_workflow(base_wf)
    cyclic_wf = base_wf.model_copy(update={"steps": [step1, step2]})
    with pytest.raises(AppException) as exc_info:
        await workflow_service.save_workflow(admin_token, cyclic_wf.id, cyclic_wf)

    assert exc_info.value.status_code == 422
    assert exc_info.value.details["error_code"] == ErrorCodes.WORKFLOW_COMPILATION_ERROR.value


async def test_create_workflow_draft_no_registries_raises_not_found(
    workflow_service: StudioWorkflowService,
    mock_system_repo: InMemorySystemRepository,
    admin_token: TokenData,
) -> None:
    """Tests that creating a workflow draft when no model registries exist raises ResourceNotFoundError."""
    mock_system_repo._model_registries.clear()
    with pytest.raises(ResourceNotFoundError) as exc_info:
        await workflow_service.create_workflow_draft(admin_token)

    assert exc_info.value.status_code == 404
    assert exc_info.value.details["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value


async def test_clone_workflow_corrupted_profile_raises_validation_failed(
    workflow_service: StudioWorkflowService,
    mock_workflow_repo: InMemoryWorkflowRepository,
    mock_output_profile_repo: InMemoryOutputProfileRepository,
    admin_token: TokenData,
) -> None:
    """Tests that cloning a workflow with a corrupted output profile raises 500 AppException with VALIDATION_FAILED."""
    wf = _valid_workflow(wf_id="wf_0195f3a0000070008000aabbccddeeff", org_id="org_0195f3a0000070008000000000000123")
    await mock_workflow_repo.save_workflow(wf)

    mock_output_profile_repo.inject_fault(
        "get_all_output_profiles",
        AppException(
            message="Corrupted output profile encountered during workflow clone",
            status_code=500,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        ),
    )
    try:
        with pytest.raises(AppException) as exc_info:
            await workflow_service.clone_workflow(admin_token, wf.id)

        assert exc_info.value.status_code == 500
        assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    finally:
        mock_output_profile_repo.clear_faults()


async def test_clone_workflow_remaps_causal_source_step_id(
    workflow_service: StudioWorkflowService,
    mock_workflow_repo: InMemoryWorkflowRepository,
    mock_output_profile_repo: InMemoryOutputProfileRepository,
    admin_token: TokenData,
) -> None:
    """Tests that cloning a workflow remaps causal_source_step_id and preserves relational consistency."""
    causal_step = StepRule(
        id="sr_0195f3a0000070008000111122223333",
        task_blueprint="stp_0195f3a00000700080000123456789ab",
        depends_on=[],
        input_mappings={},
    )
    specialist_step = StepRule(
        id="sr_0195f3a0000070008000555566667777",
        task_blueprint="stp_0195f3a00000700080000123456789ab",
        depends_on=["sr_0195f3a0000070008000111122223333"],
        causal_source_step_id="sr_0195f3a0000070008000111122223333",
        input_mappings={},
    )
    wf = _valid_workflow(
        wf_id="wf_0195f3a0000070008000aabbccddeeff", org_id="org_0195f3a0000070008000000000000123"
    ).model_copy(update={"steps": [causal_step, specialist_step], "default_profile_id": None})
    await mock_workflow_repo.save_workflow(wf)

    cloned_wf = await workflow_service.clone_workflow(admin_token, wf.id)

    assert cloned_wf.id != wf.id
    assert len(cloned_wf.steps) == 2
    cloned_causal = cloned_wf.steps[0]
    cloned_specialist = cloned_wf.steps[1]

    assert cloned_causal.id != causal_step.id
    assert cloned_specialist.id != specialist_step.id
    assert cloned_specialist.depends_on == [cloned_causal.id]
    assert cloned_specialist.causal_source_step_id == cloned_causal.id


async def test_get_workflow_available_extensions_includes_system_core_steps(
    workflow_service: StudioWorkflowService,
    root_token: TokenData,
    mock_workflow_repo: InMemoryWorkflowRepository,
    mock_prompt_block_repo: InMemoryPromptBlockRepository,
) -> None:
    """Regression test: get_workflow_available_extensions must include extensions from is_system_core=True steps."""
    wf = _valid_workflow(org_id="org_0195f3a0000070008000000000000001")
    system_step = _valid_step(
        "stp_0195f3a00000700c84a5a1d15c00438a",
        slug="step_causal_discovery",
        is_system_core=True,
        org_id="org_0195f3a0000070008000000000000001",
    )
    wf_with_steps = wf.model_copy(
        update={
            "steps": [
                StepRule(
                    id="sr_0195f3a00000700a88f1d71000000002",
                    task_blueprint="stp_0195f3a00000700c84a5a1d15c00438a",
                )
            ]
        }
    )
    await mock_workflow_repo.save_workflow(wf_with_steps)
    await mock_workflow_repo.save_step(system_step)
    await mock_prompt_block_repo.create_prompt_block(_valid_matrix_block("blk_0195f3a00000700080000123456789ab"))

    exts = await workflow_service.get_workflow_available_extensions(root_token, wf.id)
    assert exts == ["detailed_gap_analysis", "executive_summary"]


async def test_delete_step_blocked_by_workflow_usage_raises(
    workflow_service: StudioWorkflowService, admin_token: TokenData, mock_workflow_repo: InMemoryWorkflowRepository
) -> None:
    """Tests that deleting a step referenced by a workflow raises 400 DELETE_BLOCKED_BY_USAGE."""
    step_data = _valid_step(
        "stp_0195f3a00000700080000123456789ab", is_system_core=False, org_id="org_0195f3a0000070008000000000000123"
    )
    await mock_workflow_repo.save_step(step_data)
    wf = _valid_workflow(org_id="org_0195f3a0000070008000000000000123").model_copy(
        update={
            "steps": [
                StepRule(
                    id="sr_0195f3a00000700080000123456789ab",
                    task_blueprint=step_data.id,
                )
            ]
        }
    )
    await mock_workflow_repo.save_workflow(wf)

    with pytest.raises(AppException) as exc_info:
        await workflow_service.delete_step(admin_token, step_data.id, force_delete=False)

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.DELETE_BLOCKED_BY_USAGE.value
    assert await mock_workflow_repo.get_step_by_id(step_data.id) is not None


async def test_delete_step_force_delete_bypasses_workflow_usage_check(
    workflow_service: StudioWorkflowService, admin_token: TokenData, mock_workflow_repo: InMemoryWorkflowRepository
) -> None:
    """Tests that ON DELETE RESTRICT blocks step deletion even when force_delete=True until referencing workflows are removed."""
    step_data = _valid_step(
        "stp_0195f3a00000700080000123456789ab", is_system_core=False, org_id="org_0195f3a0000070008000000000000123"
    )
    await mock_workflow_repo.save_step(step_data)
    wf = _valid_workflow(org_id="org_0195f3a0000070008000000000000123").model_copy(
        update={
            "steps": [
                StepRule(
                    id="sr_0195f3a00000700080000123456789ab",
                    task_blueprint=step_data.id,
                )
            ]
        }
    )
    await mock_workflow_repo.save_workflow(wf)

    with pytest.raises(AppException) as exc_info:
        await workflow_service.delete_step(admin_token, step_data.id, force_delete=True)
    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.DELETE_BLOCKED_BY_USAGE.value
    assert await mock_workflow_repo.get_step_by_id(step_data.id) is not None

    await mock_workflow_repo.delete_workflow(wf.id)
    await workflow_service.delete_step(admin_token, step_data.id, force_delete=True)
    persisted = await mock_workflow_repo.get_step_by_id(step_data.id)
    assert persisted is None


async def test_save_workflow_prunes_stale_target_blocks_and_coerces_view_type_on_linked_output_profiles(
    workflow_service: StudioWorkflowService,
    admin_token: TokenData,
    mock_workflow_repo: InMemoryWorkflowRepository,
    mock_output_profile_repo: InMemoryOutputProfileRepository,
) -> None:
    """Saving workflow prunes stale target_blocks, variance_target_block, and user_role_target_block and coerces view_type."""
    blk_1 = "blk_0195f3a0000070008000012345678901"
    blk_2 = "blk_0195f3a0000070008000012345678902"
    blk_3_deleted = "blk_0195f3a0000070008000012345678903"

    step_1 = _valid_step(
        "stp_0195f3a0000070008000012345678901", org_id="org_0195f3a0000070008000000000000123"
    ).model_copy(update={"criteria_block_ids": [blk_1], "extraction_protocol_block_id": blk_1})
    step_2 = _valid_step(
        "stp_0195f3a0000070008000012345678902", org_id="org_0195f3a0000070008000000000000123"
    ).model_copy(update={"criteria_block_ids": [blk_2], "extraction_protocol_block_id": blk_2})
    step_3 = _valid_step(
        "stp_0195f3a0000070008000012345678903", org_id="org_0195f3a0000070008000000000000123"
    ).model_copy(update={"criteria_block_ids": [blk_3_deleted], "extraction_protocol_block_id": blk_3_deleted})
    await mock_workflow_repo.save_step(step_1)
    await mock_workflow_repo.save_step(step_2)
    await mock_workflow_repo.save_step(step_3)

    wf_id = "wf_0195f3a00000700080000123456789ab"
    await mock_workflow_repo.save_workflow(_valid_workflow(wf_id=wf_id, org_id="org_0195f3a0000070008000000000000123"))
    prf_id = "prf_0195f3a00000700080000123456789ab"
    linked_profile = OutputProfile(
        id=prf_id,
        slug="prf_linked",
        workflow_id=wf_id,
        name=I18nText(translations={"en": "Linked Profile"}),
        organization_id="org_0195f3a0000070008000000000000123",
        target_block_order=[
            TargetBlockType.GLOBAL_SCORE_BLOCK,
            TargetBlockType.MATRIX_GRAPHS_BLOCK,
            TargetBlockType.VARIANCE_VALIDATION_BLOCK,
        ],
        visible_workflow_extensions=[XaiExtensionType.VARIANCE_VALIDATION],
        variance_target_block=blk_3_deleted,
        user_role_target_block=blk_3_deleted,
        matrix_synthesis_groups=[
            MatrixSynthesisGroup(
                id="grp_0195f3a0000070008000012345678901",
                title=I18nText(translations={"en": "3D Group"}),
                target_blocks=[blk_1, blk_2, blk_3_deleted],
                view_type=PresetView.MATRIX_3D,
            ),
            MatrixSynthesisGroup(
                id="grp_0195f3a0000070008000012345678902",
                title=I18nText(translations={"en": "2D Group"}),
                target_blocks=[blk_1, blk_3_deleted],
                view_type=PresetView.COMPARE_2D,
            ),
        ],
    )
    await mock_output_profile_repo.create_output_profile(linked_profile)

    wf_updated = _valid_workflow(wf_id=wf_id, org_id="org_0195f3a0000070008000000000000123").model_copy(
        update={
            "steps": [
                StepRule(id="sr_0195f3a0000070008000012345678901", task_blueprint=step_1.id),
                StepRule(id="sr_0195f3a0000070008000012345678902", task_blueprint=step_2.id),
            ]
        }
    )
    saved_dto = await workflow_service.save_workflow(admin_token, wf_id, wf_updated)

    persisted_profile = await mock_output_profile_repo.get_output_profile_by_id(prf_id)
    assert persisted_profile is not None
    assert len(persisted_profile.matrix_synthesis_groups) == 2
    assert persisted_profile.matrix_synthesis_groups[0].target_blocks == [blk_1, blk_2]
    assert persisted_profile.matrix_synthesis_groups[0].view_type == PresetView.COMPARE_2D
    assert persisted_profile.matrix_synthesis_groups[1].target_blocks == [blk_1]
    assert persisted_profile.matrix_synthesis_groups[1].view_type == PresetView.METRICS_1D
    assert persisted_profile.variance_target_block is None
    assert persisted_profile.user_role_target_block is None
    assert TargetBlockType.VARIANCE_VALIDATION_BLOCK not in persisted_profile.target_block_order
    assert XaiExtensionType.VARIANCE_VALIDATION not in persisted_profile.visible_workflow_extensions
    assert saved_dto.output_profiles[prf_id].variance_target_block is None
    assert saved_dto.output_profiles[prf_id].matrix_synthesis_groups[0].view_type == PresetView.COMPARE_2D


async def test_save_workflow_removes_empty_matrix_synthesis_group_and_matrix_graphs_block_when_all_targets_deleted(
    workflow_service: StudioWorkflowService,
    admin_token: TokenData,
    mock_workflow_repo: InMemoryWorkflowRepository,
    mock_output_profile_repo: InMemoryOutputProfileRepository,
) -> None:
    """Removing all matrix blocks removes empty groups and MATRIX_GRAPHS_BLOCK from target_block_order."""
    blk_deleted = "blk_0195f3a0000070008000012345678999"
    wf_id = "wf_0195f3a00000700080000123456789ab"
    prf_id = "prf_0195f3a00000700080000123456789ab"

    linked_profile = OutputProfile(
        id=prf_id,
        slug="prf_empty_groups",
        workflow_id=wf_id,
        name=I18nText(translations={"en": "Empty Groups Profile"}),
        organization_id="org_0195f3a0000070008000000000000123",
        target_block_order=[
            TargetBlockType.GLOBAL_SCORE_BLOCK,
            TargetBlockType.MATRIX_GRAPHS_BLOCK,
        ],
        matrix_synthesis_groups=[
            MatrixSynthesisGroup(
                id="grp_0195f3a0000070008000012345678901",
                title=I18nText(translations={"en": "Single Block Group"}),
                target_blocks=[blk_deleted],
                view_type=PresetView.METRICS_1D,
            )
        ],
    )
    await mock_output_profile_repo.create_output_profile(linked_profile)

    wf_empty = _valid_workflow(wf_id=wf_id, org_id="org_0195f3a0000070008000000000000123").model_copy(
        update={"steps": []}
    )
    await mock_workflow_repo.save_workflow(wf_empty)
    await workflow_service.save_workflow(admin_token, wf_id, wf_empty)

    persisted_profile = await mock_output_profile_repo.get_output_profile_by_id(prf_id)
    assert persisted_profile is not None
    assert persisted_profile.matrix_synthesis_groups == []
    assert TargetBlockType.MATRIX_GRAPHS_BLOCK not in persisted_profile.target_block_order
    assert TargetBlockType.GLOBAL_SCORE_BLOCK in persisted_profile.target_block_order


async def test_studio_save_workflow_cross_tenant_put_idor_raises_permission_denied() -> None:
    """Verify cross-tenant PUT IDOR on save_workflow and save_step is blocked and non-ROOT org_id is preserved."""
    org_a = generate_opaque_id(EntityPrefix.ORGANIZATION)
    org_b = generate_opaque_id(EntityPrefix.ORGANIZATION)
    initiator_a = TokenData(
        id=generate_opaque_id(EntityPrefix.USER),
        organization_id=org_a,
        email="admin-a@example.com",
        role=UserRole.ADMIN,
    )

    wf_repo = InMemoryWorkflowRepository()
    op_repo = InMemoryOutputProfileRepository()
    pb_repo = InMemoryPromptBlockRepository()
    sys_repo = InMemorySystemRepository()
    service = StudioWorkflowService(
        workflow_repo=wf_repo,
        output_profile_repo=op_repo,
        prompt_block_repo=pb_repo,
        system_repo=sys_repo,
    )

    wf_b = WorkflowFactory.build(
        organization_id=org_b,
        steps=[],
        default_profile_id=None,
    )
    await wf_repo.save_workflow(wf_b)

    forged_wf_payload = wf_b.model_copy(
        update={
            "organization_id": org_a,
            "name": I18nText(translations={"en": "Hijacked Workflow"}),
        }
    )
    with pytest.raises(PermissionDeniedError):
        await service.save_workflow(initiator_a, wf_b.id, forged_wf_payload)

    persisted_b = await wf_repo.get_workflow_by_id(wf_b.id)
    assert persisted_b is not None
    assert persisted_b.organization_id == org_b
    assert persisted_b.name == wf_b.name

    wf_a = WorkflowFactory.build(
        organization_id=org_a,
        steps=[],
        default_profile_id=None,
    )
    await wf_repo.save_workflow(wf_a)
    reassigned_wf = wf_a.model_copy(update={"organization_id": org_b})
    saved_wf_a = await service.save_workflow(initiator_a, wf_a.id, reassigned_wf)
    assert saved_wf_a.organization_id == org_a


async def test_studio_save_methods_reject_client_invented_id_when_missing_with_404(
    root_token: TokenData,
    admin_token: TokenData,
) -> None:
    """Verify all 7 Studio save_* methods reject non-existent client-invented UUIDv7 IDs with 404."""
    root_uow = InMemoryUnitOfWork()
    wf_repo = InMemoryWorkflowRepository()
    op_repo = InMemoryOutputProfileRepository()
    pb_repo = InMemoryPromptBlockRepository()
    tb_repo = InMemoryTaskBriefRepository()
    sys_repo = InMemorySystemRepository()

    wf_service = StudioWorkflowService(
        workflow_repo=wf_repo,
        output_profile_repo=op_repo,
        prompt_block_repo=pb_repo,
        system_repo=sys_repo,
        uow_factory=lambda: InMemoryUnitOfWork(root_uow.store),
    )
    op_service = StudioOutputProfileService(output_profile_repo=op_repo, workflow_service=wf_service)
    pb_service = StudioPromptBlockService(prompt_block_repo=pb_repo, system_repo=sys_repo)
    tb_service = StudioTaskBriefService(task_brief_repo=tb_repo)
    sys_service = StudioSystemConfigService(system_repo=sys_repo, workflow_repo=wf_repo)

    missing_block = SystemRulePromptBlockFactory.build(organization_id=admin_token.organization_id)
    with pytest.raises(ResourceNotFoundError):
        await pb_service.save_prompt_block(admin_token, missing_block.id, missing_block)
    assert await pb_repo.get_prompt_block_by_id(missing_block.id) is None

    missing_wf = WorkflowFactory.build(
        organization_id=admin_token.organization_id,
        steps=[],
        default_profile_id=None,
    )
    with pytest.raises(ResourceNotFoundError):
        await wf_service.save_workflow(admin_token, missing_wf.id, missing_wf)
    assert await wf_repo.get_workflow_by_id(missing_wf.id) is None

    missing_step = _valid_step(
        step_id=generate_opaque_id(EntityPrefix.STEP),
        org_id="org_0195f3a0000070008000000000000123",
    )
    with pytest.raises(ResourceNotFoundError):
        await wf_service.save_step(admin_token, missing_step.id, missing_step)
    assert await wf_repo.get_step_by_id(missing_step.id) is None

    missing_profile = OutputProfileFactory.build(
        workflow_id=missing_wf.id,
        organization_id=admin_token.organization_id,
        target_block_order=[TargetBlockType.GLOBAL_SCORE_BLOCK],
        matrix_synthesis_groups=[],
        variance_target_block=None,
        user_role_target_block=None,
    )
    with pytest.raises(ResourceNotFoundError):
        await op_service.save_output_profile(admin_token, missing_profile.id, missing_profile)
    assert await op_repo.get_output_profile_by_id(missing_profile.id) is None

    missing_brief = TaskBriefFactory.build(organization_id=admin_token.organization_id)
    with pytest.raises(ResourceNotFoundError):
        await tb_service.save_task_brief(admin_token, missing_brief.id, missing_brief)
    assert await tb_repo.get_task_brief_by_id(missing_brief.id) is None

    existing_reg = (await sys_repo.get_all_model_registries())[0]
    missing_reg_id = generate_opaque_id(EntityPrefix.MODEL_REGISTRY)
    missing_reg: SystemConfigModelRegistry = existing_reg.model_copy(update={"id": missing_reg_id})
    with pytest.raises(ResourceNotFoundError):
        await sys_service.save_system_config(root_token, missing_reg_id, missing_reg)

    missing_gw_id = generate_opaque_id(EntityPrefix.MCP_GATEWAY)
    missing_gw = SystemConfigMCPGateways(
        id=missing_gw_id,
        organization_id=admin_token.organization_id,
        name="Missing Gateway",
        slug="missing_gateway",
        tools=[],
    )
    with pytest.raises(ResourceNotFoundError):
        await sys_service.save_mcp_gateways(root_token, missing_gw_id, missing_gw)


async def test_clone_workflow_executes_parent_before_child_atomically_in_single_uow(
    admin_token: TokenData,
) -> None:
    """Verify clone_workflow executes parent-before-child writes inside a single active UoW transaction."""
    root_uow = InMemoryUnitOfWork()
    opened_uows: list[InMemoryUnitOfWork] = []

    def tracking_uow_factory() -> InMemoryUnitOfWork:
        created = InMemoryUnitOfWork(root_uow.store)
        opened_uows.append(created)
        return created

    wf_repo = InMemoryWorkflowRepository()
    op_repo = InMemoryOutputProfileRepository()
    pb_repo = InMemoryPromptBlockRepository()
    sys_repo = InMemorySystemRepository()
    service = StudioWorkflowService(
        workflow_repo=wf_repo,
        output_profile_repo=op_repo,
        prompt_block_repo=pb_repo,
        system_repo=sys_repo,
        uow_factory=tracking_uow_factory,
    )

    source_wf = WorkflowFactory.build(
        slug="strategic_board_audit",
        organization_id=admin_token.organization_id,
        steps=[],
        default_profile_id=None,
    )
    source_profile = OutputProfileFactory.build(
        slug="executive_summary_profile",
        workflow_id=source_wf.id,
        organization_id=admin_token.organization_id,
        target_block_order=[TargetBlockType.GLOBAL_SCORE_BLOCK],
        matrix_synthesis_groups=[],
        variance_target_block=None,
        user_role_target_block=None,
    )
    source_wf = source_wf.model_copy(update={"default_profile_id": source_profile.id})
    await wf_repo.save_workflow(source_wf)
    await op_repo.create_output_profile(source_profile)

    # 1. Verify parent Workflow (with pre-mapped default_profile_id under deferrable FK) is written BEFORE child OutputProfile and aborts UoW on fault
    op_repo.inject_fault("create_output_profile", AppException(message="Child insert aborted", status_code=500))
    try:
        with pytest.raises(AppException):
            await service.clone_workflow(admin_token, source_wf.id)
    finally:
        op_repo.clear_faults()

    assert len(opened_uows) == 1
    aborted_uow = opened_uows[0]
    assert aborted_uow._finalized is True
    assert root_uow.store.current_org_reset_count == 1
    all_wfs_at_child_step = await wf_repo.get_all_workflows(organization_id=admin_token.organization_id, role="ADMIN")
    aborted_clones = [w for w in all_wfs_at_child_step if w.id != source_wf.id]
    assert len(aborted_clones) == 1
    assert aborted_clones[0].default_profile_id is not None
    assert aborted_clones[0].default_profile_id != source_profile.id
    assert aborted_clones[0].version == 1
    await wf_repo.delete_workflow(aborted_clones[0].id)
    opened_uows.clear()

    # 2. Verify full parent -> child clone executes with a single save_workflow call and version == 1 in one committed UoW
    saves_before = wf_repo.get_call_count("save_workflow")
    creates_before = op_repo.get_call_count("create_output_profile")

    cloned = await service.clone_workflow(admin_token, source_wf.id)

    assert len(opened_uows) == 1
    single_uow = opened_uows[0]
    assert single_uow._finalized is True
    assert root_uow.store.current_org_reset_count == 2
    assert get_active_uow() is None
    assert wf_repo.get_call_count("save_workflow") - saves_before == 1
    assert op_repo.get_call_count("create_output_profile") - creates_before == 1
    assert cloned.slug == "strategic_board_audit"
    assert cloned.version == 1
    assert cloned.default_profile_id is not None
    assert cloned.default_profile_id != source_profile.id

    cloned_profile = await op_repo.get_output_profile_by_id(cloned.default_profile_id)
    assert cloned_profile is not None
    assert cloned_profile.slug == "executive_summary_profile"
    assert cloned_profile.workflow_id == cloned.id


async def test_save_workflow_enforces_sql_occ_version_increment_and_conflict(
    workflow_service: StudioWorkflowService,
    admin_token: TokenData,
    mock_workflow_repo: InMemoryWorkflowRepository,
) -> None:
    """Verify save_workflow increments Workflow.version and raises 409 CONFLICT on stale version."""
    wf_id = "wf_0195f3a00000700080000123456789ef"
    initial_wf = _valid_workflow(wf_id=wf_id, org_id="org_0195f3a0000070008000000000000123")
    assert initial_wf.version == 1
    await mock_workflow_repo.save_workflow(initial_wf)

    saved_v2 = await workflow_service.save_workflow(admin_token, wf_id, initial_wf)
    assert saved_v2.version == 2

    with pytest.raises(AppException) as stale_exc:
        await workflow_service.save_workflow(admin_token, wf_id, initial_wf)
    assert stale_exc.value.status_code == 409
    assert stale_exc.value.details["error_code"] == ErrorCodes.CONFLICT.value


async def test_clone_workflow_with_missing_default_profile_raises_validation_failed(
    workflow_service: StudioWorkflowService,
    admin_token: TokenData,
    mock_workflow_repo: InMemoryWorkflowRepository,
) -> None:
    """Verify clone_workflow fails fast when default_profile_id is absent from workflow output profiles."""
    orphan_wf = _valid_workflow(
        wf_id="wf_0195f3a00000700080000123456789aa",
        org_id="org_0195f3a0000070008000000000000123",
    )
    await mock_workflow_repo.save_workflow(orphan_wf)

    with pytest.raises(AppException) as exc_info:
        await workflow_service.clone_workflow(admin_token, orphan_wf.id)
    assert exc_info.value.status_code == 422
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
