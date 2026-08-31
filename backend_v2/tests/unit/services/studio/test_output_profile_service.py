"""Tests for StudioOutputProfileService."""

from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.enums import TargetBlockType
from backend_v2.models.v2_core import I18nText, MatrixSynthesisGroup, OutputProfile
from backend_v2.services.studio.output_profile_service import StudioOutputProfileService


@pytest.fixture
def mock_output_profile_repo() -> Any:
    return AsyncMock()


@pytest.fixture
def mock_workflow_service() -> Any:
    return AsyncMock()


@pytest.fixture
def service(mock_output_profile_repo: Any, mock_workflow_service: Any) -> Any:
    return StudioOutputProfileService(
        output_profile_repo=mock_output_profile_repo,
        workflow_service=mock_workflow_service,
    )


@pytest.mark.asyncio
async def test_save_output_profile_allows_target_block_types(service: Any, mock_workflow_service: Any) -> None:
    """Test that virtual blocks from TargetBlockType are allowed without failing validation."""
    initiator = TokenData(id="test_user", role=UserRole.ADMIN, organization_id="root")

    # Mock Workflow
    workflow = AsyncMock()
    workflow.slug = "test_wf"
    workflow.steps = []

    workflow.get_allowed_layout_targets = Mock(return_value={TargetBlockType.GLOBAL_SCORE_BLOCK.value})

    mock_workflow_service.get_workflow.return_value = workflow
    mock_workflow_service.list_steps.return_value = []

    # Mock return from repo
    service.output_profile_repo.get_output_profile_by_id.return_value = {
        "id": "opt_1234567890abcdef",
        "slug": "opt_123",
        "workflow_id": "wf_123",
        "name": {"translations": {"en": "Test"}},
        "organization_id": "root",
        "matrix_synthesis_groups": [
            {
                "id": "grp_1234567890123456",
                "title": {"translations": {"en": "Test"}},
                "target_blocks": ["*"],
            }
        ],
    }

    # Create an OutputProfile that includes "global_score_block"
    profile = OutputProfile(
        id="opt_1234567890abcdef",
        slug="opt_123",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "Test"}),
        organization_id="root",
        target_block_order=[TargetBlockType.GLOBAL_SCORE_BLOCK],
        matrix_synthesis_groups=[
            MatrixSynthesisGroup(
                id="grp_1234567890123456",
                title=I18nText(translations={"en": "Test Group"}),
                target_blocks=[TargetBlockType.GLOBAL_SCORE_BLOCK],
            )
        ],
    )

    # This should NOT raise AppException
    await service.save_output_profile(initiator, profile.id, profile)

    # If it raised AppException, the test would fail. We also verify it called create
    assert service.output_profile_repo.create_output_profile.called


@pytest.mark.asyncio
async def test_save_output_profile_fails_wrong_workflow_block(service: Any, mock_workflow_service: Any) -> None:
    """Negative Test 1: Validation throws AppException if using a block ID belonging to another workflow."""
    initiator = TokenData(id="test_user", role=UserRole.ADMIN, organization_id="root")

    workflow = AsyncMock()
    workflow.id = "wf_123"
    workflow.steps = []

    workflow.get_allowed_layout_targets = Mock(return_value={"blk_allowed"})

    mock_workflow_service.get_workflow.return_value = workflow
    mock_workflow_service.list_steps.return_value = []

    profile_dict = {
        "id": "opt_1234567890abcdef",
        "slug": "opt_123",
        "workflow_id": "wf_123",
        "name": {"translations": {"en": "Test"}},
        "organization_id": "root",
        "matrix_synthesis_groups": [
            {
                "id": "grp_2222222222222222",
                "title": {"translations": {"en": "Wrong"}},
                "target_blocks": ["blk_wrong_workflow"],
            }
        ],
    }
    profile = OutputProfile.model_validate(profile_dict, strict=False)

    with pytest.raises(AppException) as exc_info:
        await service.save_output_profile(initiator, profile.id, profile)

    assert exc_info.value.status_code == 400
    assert "Target Component 'blk_wrong_workflow' does not exist in the context of Workflow 'wf_123'" in str(
        exc_info.value.message
    )


@pytest.mark.asyncio
async def test_save_output_profile_fails_invalid_block(service: Any, mock_workflow_service: Any) -> None:
    """Negative Test 2: Validation throws AppException if using a fabricated block ID."""
    initiator = TokenData(id="test_user", role=UserRole.ADMIN, organization_id="root")

    workflow = AsyncMock()
    workflow.id = "wf_123"
    workflow.steps = []

    workflow.get_allowed_layout_targets = Mock(return_value={"blk_allowed"})

    mock_workflow_service.get_workflow.return_value = workflow
    mock_workflow_service.list_steps.return_value = []

    profile_dict = {
        "id": "opt_1234567890abcdef",
        "slug": "opt_123",
        "workflow_id": "wf_123",
        "name": {"translations": {"en": "Test"}},
        "organization_id": "root",
        "matrix_synthesis_groups": [
            {
                "id": "grp_3333333333333333",
                "title": {"translations": {"en": "Invalid"}},
                "target_blocks": ["invalid_block_123"],
            }
        ],
    }
    profile = OutputProfile.model_validate(profile_dict, strict=False)

    with pytest.raises(AppException) as exc_info:
        await service.save_output_profile(initiator, profile.id, profile)

    assert exc_info.value.status_code == 400


def _make_valid_profile(
    profile_id: str, slug: str, workflow_id: str, org_id: str, name: str = "Test"
) -> OutputProfile:
    return OutputProfile(
        id=profile_id,
        slug=slug,
        workflow_id=workflow_id,
        name=I18nText(translations={"en": name}),
        organization_id=org_id,
        target_block_order=[TargetBlockType.GLOBAL_SCORE_BLOCK],
        matrix_synthesis_groups=[
            MatrixSynthesisGroup(
                id="grp_1234567890123456",
                title=I18nText(translations={"en": "Group"}),
                target_blocks=[TargetBlockType.GLOBAL_SCORE_BLOCK],
            )
        ],
    )


@pytest.mark.asyncio
async def test_list_output_profiles_root_and_tenant(service: Any) -> None:
    """Test list_output_profiles filters correctly by role/tenant."""
    p1 = _make_valid_profile("opt_1111111111111111", "opt_1", "wf_1", "org_1", "P1")
    p2 = _make_valid_profile("opt_2222222222222222", "opt_2", "wf_1", "org_2", "P2")
    service.output_profile_repo.get_all_output_profiles.return_value = [p1, p2]

    root_user = TokenData(id="root_user", role=UserRole.ROOT, organization_id="root")
    res_root = await service.list_output_profiles(root_user)
    assert len(res_root) == 2

    tenant_user = TokenData(id="tenant_user", role=UserRole.ADMIN, organization_id="org_1")
    res_tenant = await service.list_output_profiles(tenant_user)
    assert len(res_tenant) == 1
    assert res_tenant[0].id == "opt_1111111111111111"


@pytest.mark.asyncio
async def test_get_output_profile_success_and_not_found(service: Any) -> None:
    """Test get_output_profile returns model or raises ResourceNotFoundError."""
    initiator = TokenData(id="test_user", role=UserRole.ADMIN, organization_id="org_1")
    p1 = _make_valid_profile("opt_1111111111111111", "opt_1", "wf_1", "org_1", "P1")
    service.output_profile_repo.get_output_profile_by_id.return_value = p1
    res = await service.get_output_profile(initiator, "opt_1111111111111111")
    assert res.id == "opt_1111111111111111"

    service.output_profile_repo.get_output_profile_by_id.return_value = None
    with pytest.raises(AppException) as exc_info:
        await service.get_output_profile(initiator, "opt_missing")
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_output_profile(service: Any) -> None:
    """Test delete_output_profile deletes existing resource."""
    initiator = TokenData(id="test_user", role=UserRole.ADMIN, organization_id="org_1")
    p1 = _make_valid_profile("opt_1111111111111111", "opt_1", "wf_1", "org_1", "P1")
    service.output_profile_repo.get_output_profile_by_id.return_value = p1
    await service.delete_output_profile(initiator, "opt_1111111111111111")
    assert service.output_profile_repo.delete_output_profile.called


@pytest.mark.asyncio
async def test_create_and_clone_output_profile(service: Any, mock_workflow_service: Any) -> None:
    """Test draft creation and cloning of an output profile."""
    initiator = TokenData(id="test_user", role=UserRole.ADMIN, organization_id="org_1")

    workflow = AsyncMock()
    workflow.id = "*"
    workflow.steps = []
    workflow.get_allowed_layout_targets = Mock(return_value={"*", TargetBlockType.GLOBAL_SCORE_BLOCK.value})
    mock_workflow_service.get_workflow.return_value = workflow
    mock_workflow_service.list_steps.return_value = []

    p1 = _make_valid_profile("opt_1111111111111111", "opt_1", "*", "org_1", "Original")

    async def mock_get_by_id(pid: str) -> OutputProfile | None:
        if pid == "opt_1111111111111111":
            return p1
        return _make_valid_profile(pid, pid, "*", "org_1", "Created")

    service.output_profile_repo.get_output_profile_by_id.side_effect = mock_get_by_id

    draft = await service.create_output_profile_draft(initiator)
    assert draft.id.startswith("prf_")

    cloned = await service.clone_output_profile(initiator, "opt_1111111111111111")
    assert cloned.id.startswith("prf_")


@pytest.mark.asyncio
async def test_output_profile_service_not_found_branches(service: Any) -> None:
    """Test ResourceNotFoundError triggers for missing resources on delete and clone."""
    initiator = TokenData(id="test_user", role=UserRole.ADMIN, organization_id="org_1")
    service.output_profile_repo.get_output_profile_by_id.return_value = None

    with pytest.raises(AppException) as exc_info:
        await service.delete_output_profile(initiator, "missing_prof")
    assert exc_info.value.status_code == 404

    with pytest.raises(AppException) as exc_info:
        await service.clone_output_profile(initiator, "missing_prof")
    assert exc_info.value.status_code == 404
