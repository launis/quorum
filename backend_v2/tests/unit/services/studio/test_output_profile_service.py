"""Tests for StudioOutputProfileService."""

from __future__ import annotations

from unittest.mock import AsyncMock, Mock

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.core_base import I18nText
from backend_v2.models.enums import TargetBlockType
from backend_v2.models.v2_core import MatrixSynthesisGroup, OutputProfile
from backend_v2.services.studio.output_profile_service import StudioOutputProfileService


@pytest.fixture
def mock_output_profile_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_workflow_service() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def service(mock_output_profile_repo: AsyncMock, mock_workflow_service: AsyncMock) -> StudioOutputProfileService:
    return StudioOutputProfileService(
        output_profile_repo=mock_output_profile_repo,
        workflow_service=mock_workflow_service,
    )


def _make_valid_profile(profile_id: str, slug: str, workflow_id: str, org_id: str, name: str = "Test") -> OutputProfile:
    return OutputProfile(
        id=profile_id,
        slug=slug,
        workflow_id=workflow_id,
        name=I18nText(translations={"en": name}),
        organization_id=org_id,
        target_block_order=[TargetBlockType.GLOBAL_SCORE_BLOCK],
    )


@pytest.mark.asyncio
async def test_save_output_profile_allows_target_block_types(
    service: StudioOutputProfileService, mock_workflow_service: AsyncMock
) -> None:
    """Test that virtual blocks from TargetBlockType are allowed without failing validation."""
    initiator = TokenData(id="test_user", role=UserRole.ADMIN, organization_id="root")

    workflow = AsyncMock()
    workflow.slug = "test_wf"
    workflow.steps = []
    workflow.get_allowed_layout_targets = Mock(return_value={TargetBlockType.GLOBAL_SCORE_BLOCK.value})

    mock_workflow_service.get_workflow.return_value = workflow
    mock_workflow_service.list_steps.return_value = []

    profile = _make_valid_profile("prf_1234567890abcdef", "opt_123", "wf_123", "root", "Test")
    service.output_profile_repo.get_output_profile_by_id.return_value = profile

    await service.save_output_profile(initiator, profile.id, profile)
    assert service.output_profile_repo.create_output_profile.called


@pytest.mark.asyncio
async def test_list_output_profiles_root_and_tenant(service: StudioOutputProfileService) -> None:
    """Test list_output_profiles filters correctly by role/tenant."""
    p1 = _make_valid_profile("prf_1111111111111111", "opt_1", "wf_1", "org_1", "P1")
    p2 = _make_valid_profile("prf_2222222222222222", "opt_2", "wf_1", "org_2", "P2")
    service.output_profile_repo.get_all_output_profiles.return_value = [p1, p2]

    root_user = TokenData(id="root_user", role=UserRole.ROOT, organization_id="root")
    res_root = await service.list_output_profiles(root_user)
    assert len(res_root) == 2

    tenant_user = TokenData(id="tenant_user", role=UserRole.ADMIN, organization_id="org_1")
    res_tenant = await service.list_output_profiles(tenant_user)
    assert len(res_tenant) == 1
    assert res_tenant[0].id == "prf_1111111111111111"


@pytest.mark.asyncio
async def test_get_output_profile_success_and_not_found(service: StudioOutputProfileService) -> None:
    """Test get_output_profile returns model or raises ResourceNotFoundError."""
    initiator = TokenData(id="test_user", role=UserRole.ADMIN, organization_id="org_1")
    p1 = _make_valid_profile("prf_1111111111111111", "opt_1", "wf_1", "org_1", "P1")
    service.output_profile_repo.get_output_profile_by_id.return_value = p1
    res = await service.get_output_profile(initiator, "prf_1111111111111111")
    assert res.id == "prf_1111111111111111"

    service.output_profile_repo.get_output_profile_by_id.return_value = None
    with pytest.raises(AppException) as exc_info:
        await service.get_output_profile(initiator, "prf_missing111111")
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_output_profile(service: StudioOutputProfileService) -> None:
    """Test delete_output_profile deletes existing resource."""
    initiator = TokenData(id="test_user", role=UserRole.ADMIN, organization_id="org_1")
    p1 = _make_valid_profile("prf_1111111111111111", "opt_1", "wf_1", "org_1", "P1")
    service.output_profile_repo.get_output_profile_by_id.return_value = p1
    await service.delete_output_profile(initiator, "prf_1111111111111111")
    assert service.output_profile_repo.delete_output_profile.called


@pytest.mark.asyncio
async def test_create_and_clone_output_profile(
    service: StudioOutputProfileService, mock_workflow_service: AsyncMock
) -> None:
    """Test draft creation and cloning of an output profile."""
    initiator = TokenData(id="test_user", role=UserRole.ADMIN, organization_id="org_1")

    workflow = AsyncMock()
    workflow.id = "wf_1234567890abcdef"
    workflow.steps = []
    workflow.get_allowed_layout_targets = Mock(return_value={TargetBlockType.GLOBAL_SCORE_BLOCK.value})
    mock_workflow_service.get_workflow.return_value = workflow
    mock_workflow_service.list_steps.return_value = []
    mock_workflow_service.list_workflows.return_value = [workflow]

    p1 = _make_valid_profile("prf_1111111111111111", "opt_1", "wf_1234567890abcdef", "org_1", "Original")

    async def mock_get_by_id(pid: str) -> OutputProfile | None:
        if pid == "prf_1111111111111111":
            return p1
        return _make_valid_profile(pid, pid, "wf_1234567890abcdef", "org_1", "Created")

    service.output_profile_repo.get_output_profile_by_id.side_effect = mock_get_by_id

    draft = await service.create_output_profile_draft(initiator)
    assert draft.id.startswith("prf_")
    assert draft.workflow_id == "wf_1234567890abcdef"

    cloned = await service.clone_output_profile(initiator, "prf_1111111111111111")
    assert cloned.id.startswith("prf_")


@pytest.mark.asyncio
async def test_output_profile_service_not_found_branches(service: StudioOutputProfileService) -> None:
    """Test ResourceNotFoundError triggers for missing resources on delete and clone."""
    initiator = TokenData(id="test_user", role=UserRole.ADMIN, organization_id="org_1")
    service.output_profile_repo.get_output_profile_by_id.return_value = None

    with pytest.raises(AppException) as exc_info:
        await service.delete_output_profile(initiator, "prf_missing111111")
    assert exc_info.value.status_code == 404

    with pytest.raises(AppException) as exc_info:
        await service.clone_output_profile(initiator, "prf_missing111111")
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_save_output_profile_invalid_target_component_raises_app_exception(
    service: StudioOutputProfileService, mock_workflow_service: AsyncMock
) -> None:
    """Test that target block not in allowed_blocks raises 400 VALIDATION_FAILED."""
    initiator = TokenData(id="test_user", role=UserRole.ADMIN, organization_id="org_1")

    workflow = AsyncMock()
    workflow.id = "wf_1234567890abcdef"
    workflow.steps = []
    workflow.get_allowed_layout_targets = Mock(return_value={"blk_allowed_001"})
    mock_workflow_service.get_workflow.return_value = workflow
    mock_workflow_service.list_steps.return_value = []

    group = MatrixSynthesisGroup(
        id="grp_1111111111111111",
        title=I18nText(translations={"en": "Invalid Group"}),
        target_blocks=["blk_not_allowed_999"],
    )
    profile = _make_valid_profile("prf_1111111111111111", "opt_1", "wf_1234567890abcdef", "org_1", "Test")
    profile = profile.model_copy(update={"matrix_synthesis_groups": [group]})

    with pytest.raises(AppException) as exc_info:
        await service.save_output_profile(initiator, profile.id, profile)

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED


@pytest.mark.asyncio
async def test_create_output_profile_draft_raises_when_no_workflows(
    service: StudioOutputProfileService, mock_workflow_service: AsyncMock
) -> None:
    """Test that when list_workflows returns empty, draft raises ResourceNotFoundError."""
    initiator = TokenData(id="test_user", role=UserRole.ADMIN, organization_id="org_1")
    mock_workflow_service.list_workflows.return_value = []

    with pytest.raises(ResourceNotFoundError) as exc_info:
        await service.create_output_profile_draft(initiator)
    assert exc_info.value.error_code == ErrorCodes.RESOURCE_NOT_FOUND.value
