"""Unit tests for StudioWorkflowService.

Comprehensive unit tests for StudioWorkflowService covering
all branches, system core protection, tenant isolation, cloning, and error states.
"""

from typing import Any
from unittest.mock import AsyncMock

import pytest

from backend_v2.exceptions import AppException, ErrorCodes, PermissionDeniedError, ResourceNotFoundError
from backend_v2.models.auth import SystemOrganizations, TokenData, UserRole
from backend_v2.models.v2_core import Step, Workflow
from backend_v2.services.studio.workflow_service import StudioWorkflowService

pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_workflow_repo() -> Any:
    return AsyncMock()


@pytest.fixture
def mock_output_profile_repo() -> Any:
    return AsyncMock()


@pytest.fixture
def mock_prompt_block_repo() -> Any:
    return AsyncMock()


@pytest.fixture
def workflow_service(
    mock_workflow_repo: Any, mock_output_profile_repo: Any, mock_prompt_block_repo: Any
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


def _valid_step_dict(
    step_id: str = "sp_0123456789abcdef01",
    slug: str = "step_slug",
    is_system_core: bool = False,
    org_id: str = "org_123",
) -> dict[str, Any]:
    return {
        "id": step_id,
        "slug": slug,
        "name": {"translations": {"en": "Test Step"}},
        "type": "llm",
        "organization_id": org_id,
        "safety": "safe",
        "model_strategy": "fast",
        "criteria_block_ids": ["blk_0123456789abcdef01"],
        "extraction_protocol_block_id": "blk_0123456789abcdef01",
        "is_system_core": is_system_core,
    }


def _valid_workflow_dict(
    wf_id: str = "wor_0123456789abcdef01",
    slug: str = "wf_slug",
    org_id: str = "org_123",
    status: str = "active",
) -> dict[str, Any]:
    return {
        "id": wf_id,
        "slug": slug,
        "name": {"translations": {"en": "Test Workflow"}},
        "description": {"translations": {"en": "Test Desc"}},
        "status": status,
        "version": 1,
        "organization_id": org_id,
        "expected_inputs": [],
        "steps": [],
        "default_profile_id": "pro_0123456789abcdef01",
        "allowed_exports": ["pdf"],
        "historical_context_mode": "DISABLED",
    }


def _valid_matrix_block_dict(block_id: str = "blk_0123456789abcdef01") -> dict[str, Any]:
    return {
        "id": block_id,
        "slug": f"slug_{block_id}",
        "label": {"translations": {"en": "Matrix Label"}},
        "description": {"translations": {"en": "Description"}},
        "ai_description": "AI desc",
        "category_id": "matrix",
        "type": "float",
        "output_extensions": ["detailed_gap_analysis", "executive_summary"],
        "scales": [
            {
                "score": 1,
                "ai_label": "INITIAL",
                "claims": [
                    {
                        "label": {"translations": {"en": "Default Claim"}},
                        "tda_assertions": [
                            {
                                "tda_id": "tda_00000000000000000000000000000001",
                                "inverse_evidence": False,
                                "aggregation_mode": "ALL_MUST_COMPLY",
                                "concept_description": "Concept Description Valid",
                            }
                        ],
                    }
                ],
            }
        ],
    }


async def test_list_workflows_empty(
    workflow_service: StudioWorkflowService,
    root_token: TokenData,
    mock_workflow_repo: Any,
    mock_output_profile_repo: Any,
) -> None:
    mock_workflow_repo.get_all_workflows.return_value = []
    mock_output_profile_repo.get_all_output_profiles.return_value = []
    res = await workflow_service.list_workflows(root_token)
    assert res == []


async def test_list_workflows_tenant_filtering(
    workflow_service: StudioWorkflowService,
    admin_token: TokenData,
    mock_workflow_repo: Any,
    mock_output_profile_repo: Any,
) -> None:
    wf1 = _valid_workflow_dict("wor_0123456789abcdef01", org_id="org_123")
    wf2 = _valid_workflow_dict("wor_0123456789abcdef02", org_id="org_999")
    mock_workflow_repo.get_all_workflows.return_value = [wf1, wf2]
    mock_output_profile_repo.get_all_output_profiles.return_value = []
    res = await workflow_service.list_workflows(admin_token)
    assert len(res) == 1
    assert res[0].id == "wor_0123456789abcdef01"


async def test_list_workflows_corrupt_data_raises_integrity_error(
    workflow_service: StudioWorkflowService, root_token: TokenData, mock_workflow_repo: Any
) -> None:
    mock_workflow_repo.get_all_workflows.return_value = [{"id": "invalid"}]
    with pytest.raises(AppException) as exc_info:
        await workflow_service.list_workflows(root_token)
    assert exc_info.value.details["error_code"] == ErrorCodes.STATE_INTEGRITY_ERROR


async def test_get_workflow_not_found(
    workflow_service: StudioWorkflowService, root_token: TokenData, mock_workflow_repo: Any
) -> None:
    mock_workflow_repo.get_workflow_by_id.return_value = None
    with pytest.raises(ResourceNotFoundError):
        await workflow_service.get_workflow(root_token, "wor_missing")


async def test_get_workflow_tenant_isolation_fails(
    workflow_service: StudioWorkflowService, other_admin_token: TokenData, mock_workflow_repo: Any
) -> None:
    wf = _valid_workflow_dict(org_id="org_123")
    mock_workflow_repo.get_workflow_by_id.return_value = wf
    with pytest.raises(PermissionDeniedError):
        await workflow_service.get_workflow(other_admin_token, wf["id"])


async def test_get_workflow_success(
    workflow_service: StudioWorkflowService,
    admin_token: TokenData,
    mock_workflow_repo: Any,
    mock_output_profile_repo: Any,
) -> None:
    wf = _valid_workflow_dict(org_id="org_123")
    mock_workflow_repo.get_workflow_by_id.return_value = wf
    mock_output_profile_repo.get_all_output_profiles.return_value = []
    res = await workflow_service.get_workflow(admin_token, wf["id"])
    assert res.id == wf["id"]


async def test_get_workflow_available_extensions(
    workflow_service: StudioWorkflowService,
    admin_token: TokenData,
    mock_workflow_repo: Any,
    mock_prompt_block_repo: Any,
    mock_output_profile_repo: Any,
) -> None:
    wf_dict = _valid_workflow_dict(org_id="org_123")
    wf_dict["steps"] = [{"id": "sr_0123456789abcdef01", "task_blueprint": "sp_0123456789abcdef01"}]
    mock_workflow_repo.get_workflow_by_id.return_value = wf_dict
    mock_output_profile_repo.get_all_output_profiles.return_value = []

    step_dict = _valid_step_dict("sp_0123456789abcdef01", org_id="org_123")
    mock_workflow_repo.get_all_steps.return_value = [step_dict]

    mock_prompt_block_repo.get_prompt_block_by_id.return_value = _valid_matrix_block_dict("blk_0123456789abcdef01")

    exts = await workflow_service.get_workflow_available_extensions(admin_token, wf_dict["id"])
    assert exts == ["detailed_gap_analysis", "executive_summary"]


async def test_save_workflow_missing_after_save_raises(
    workflow_service: StudioWorkflowService, admin_token: TokenData, mock_workflow_repo: Any
) -> None:
    wf = Workflow.model_validate(_valid_workflow_dict(org_id="org_123"))
    mock_workflow_repo.get_workflow_by_id.return_value = None
    with pytest.raises(ResourceNotFoundError):
        await workflow_service.save_workflow(admin_token, wf.id, wf)


async def test_save_workflow_success(
    workflow_service: StudioWorkflowService,
    admin_token: TokenData,
    mock_workflow_repo: Any,
    mock_output_profile_repo: Any,
) -> None:
    wf = Workflow.model_validate(_valid_workflow_dict(org_id="org_123"))
    mock_workflow_repo.get_workflow_by_id.return_value = wf.model_dump(mode="json")
    mock_output_profile_repo.get_all_output_profiles.return_value = []
    res = await workflow_service.save_workflow(admin_token, wf.id, wf)
    assert res.id == wf.id


async def test_delete_workflow_not_found(
    workflow_service: StudioWorkflowService, admin_token: TokenData, mock_workflow_repo: Any
) -> None:
    mock_workflow_repo.get_workflow_by_id.return_value = None
    with pytest.raises(ResourceNotFoundError):
        await workflow_service.delete_workflow(admin_token, "wor_missing")


async def test_delete_workflow_success(
    workflow_service: StudioWorkflowService, admin_token: TokenData, mock_workflow_repo: Any
) -> None:
    wf = _valid_workflow_dict(org_id="org_123")
    mock_workflow_repo.get_workflow_by_id.return_value = wf
    await workflow_service.delete_workflow(admin_token, wf["id"])
    mock_workflow_repo.delete_workflow.assert_called_once_with(wf["id"])


async def test_create_workflow_draft_root(
    workflow_service: StudioWorkflowService,
    root_token: TokenData,
    mock_workflow_repo: Any,
    mock_output_profile_repo: Any,
) -> None:
    mock_workflow_repo.get_workflow_by_id.side_effect = lambda id_: {
        **_valid_workflow_dict(id_, org_id=SystemOrganizations.ROOT_SYSTEM, status="draft")
    }
    mock_output_profile_repo.get_all_output_profiles.return_value = []
    res = await workflow_service.create_workflow_draft(root_token)
    assert res.status == "draft"


async def test_clone_workflow_not_found(
    workflow_service: StudioWorkflowService, admin_token: TokenData, mock_workflow_repo: Any
) -> None:
    mock_workflow_repo.get_workflow_by_id.return_value = None
    with pytest.raises(ResourceNotFoundError):
        await workflow_service.clone_workflow(admin_token, "wor_missing")


async def test_clone_workflow_success(
    workflow_service: StudioWorkflowService,
    admin_token: TokenData,
    mock_workflow_repo: Any,
    mock_output_profile_repo: Any,
) -> None:
    wf = _valid_workflow_dict(org_id="org_123")
    wf["steps"] = [
        {
            "id": "sr_000000000000000000000001",
            "task_blueprint": "sp_0123456789abcdef01",
            "depends_on": [],
            "input_mappings": {},
        },
        {
            "id": "sr_000000000000000000000002",
            "task_blueprint": "sp_0123456789abcdef01",
            "depends_on": ["sr_000000000000000000000001"],
            "input_mappings": {"doc": "$steps.sr_000000000000000000000001.output"},
        },
    ]
    mock_workflow_repo.get_workflow_by_id.side_effect = [
        wf,
        {**wf, "id": "wor_0123456789abcdef0123456789abcdef"},
    ]
    mock_output_profile_repo.get_all_output_profiles.return_value = [
        {
            "id": "pro_0123456789abcdef01",
            "slug": "prof_standard",
            "workflow_id": wf["id"],
            "name": {"translations": {"en": "Standard"}},
            "layouts": [{"preset_view": "default", "steps": ["sr_000000000000000000000001"]}],
            "max_extension_items": 5,
        }
    ]

    res = await workflow_service.clone_workflow(admin_token, wf["id"])
    assert res is not None
    mock_output_profile_repo.create_output_profile.assert_called_once()


async def test_list_steps_empty(
    workflow_service: StudioWorkflowService, root_token: TokenData, mock_workflow_repo: Any
) -> None:
    mock_workflow_repo.get_all_steps.return_value = []
    res = await workflow_service.list_steps(root_token)
    assert res == []


async def test_list_steps_tenant_filtering(
    workflow_service: StudioWorkflowService, admin_token: TokenData, mock_workflow_repo: Any
) -> None:
    s1 = _valid_step_dict("sp_0123456789abcdef01", org_id="org_123")
    s2 = _valid_step_dict("sp_0123456789abcdef02", org_id="org_999")
    mock_workflow_repo.get_all_steps.return_value = [s1, s2]
    res = await workflow_service.list_steps(admin_token)
    assert len(res) == 1
    assert res[0].id == "sp_0123456789abcdef01"


async def test_list_steps_corrupt_data_raises(
    workflow_service: StudioWorkflowService, root_token: TokenData, mock_workflow_repo: Any
) -> None:
    mock_workflow_repo.get_all_steps.return_value = [{"id": "invalid"}]
    with pytest.raises(AppException) as exc_info:
        await workflow_service.list_steps(root_token)
    assert exc_info.value.details["error_code"] == ErrorCodes.STATE_INTEGRITY_ERROR


async def test_get_step_not_found(
    workflow_service: StudioWorkflowService, root_token: TokenData, mock_workflow_repo: Any
) -> None:
    mock_workflow_repo.get_step_by_id.return_value = None
    with pytest.raises(ResourceNotFoundError):
        await workflow_service.get_step(root_token, "sp_missing")


async def test_get_step_tenant_isolation_fails(
    workflow_service: StudioWorkflowService, other_admin_token: TokenData, mock_workflow_repo: Any
) -> None:
    s = _valid_step_dict(org_id="org_123")
    mock_workflow_repo.get_step_by_id.return_value = s
    with pytest.raises(PermissionDeniedError):
        await workflow_service.get_step(other_admin_token, s["id"])


async def test_get_step_success(
    workflow_service: StudioWorkflowService, admin_token: TokenData, mock_workflow_repo: Any
) -> None:
    s = _valid_step_dict(org_id="org_123")
    mock_workflow_repo.get_step_by_id.return_value = s
    res = await workflow_service.get_step(admin_token, s["id"])
    assert res.id == s["id"]


async def test_save_step_missing_after_save_raises(
    workflow_service: StudioWorkflowService, admin_token: TokenData, mock_workflow_repo: Any
) -> None:
    step = Step.model_validate(_valid_step_dict(org_id="org_123"))
    mock_workflow_repo.get_step_by_id.return_value = None
    with pytest.raises(ResourceNotFoundError):
        await workflow_service.save_step(admin_token, step.id, step)


async def test_save_step_success(
    workflow_service: StudioWorkflowService, admin_token: TokenData, mock_workflow_repo: Any
) -> None:
    step = Step.model_validate(_valid_step_dict(org_id="org_123"))
    mock_workflow_repo.get_step_by_id.side_effect = [None, step.model_dump(mode="json")]
    res = await workflow_service.save_step(admin_token, step.id, step)
    assert res.id == step.id


async def test_save_step_protected_system_core_slug_mutation_fails_fast(
    workflow_service: StudioWorkflowService, admin_token: TokenData, mock_workflow_repo: Any
) -> None:
    """PROMISE: Mutating slug/core of a system core step raises AppException(SYSTEM_PROTECTED_RESOURCE)."""
    existing = _valid_step_dict("sp_0123456789abcdef01", slug="orig_slug", is_system_core=True, org_id="org_123")
    mock_workflow_repo.get_step_by_id.return_value = existing

    modified = Step.model_validate({**existing, "slug": "mutated_slug"})
    with pytest.raises(AppException) as exc_info:
        await workflow_service.save_step(admin_token, existing["id"], modified)

    assert exc_info.value.status_code == 403
    assert exc_info.value.details["error_code"] == ErrorCodes.SYSTEM_PROTECTED_RESOURCE.value


async def test_delete_step_not_found(
    workflow_service: StudioWorkflowService, admin_token: TokenData, mock_workflow_repo: Any
) -> None:
    mock_workflow_repo.get_step_by_id.return_value = None
    with pytest.raises(ResourceNotFoundError):
        await workflow_service.delete_step(admin_token, "sp_missing")


async def test_delete_step_protected_system_core_fails_fast(
    workflow_service: StudioWorkflowService, admin_token: TokenData, mock_workflow_repo: Any
) -> None:
    """PROMISE: Deleting a protected system core step raises AppException(SYSTEM_PROTECTED_RESOURCE)."""
    step_data = _valid_step_dict("sp_0123456789abcdef01", is_system_core=True, org_id="org_123")
    mock_workflow_repo.get_step_by_id.return_value = step_data
    with pytest.raises(AppException) as exc_info:
        await workflow_service.delete_step(admin_token, step_data["id"])

    assert exc_info.value.status_code == 403
    assert exc_info.value.details["error_code"] == ErrorCodes.SYSTEM_PROTECTED_RESOURCE.value
    mock_workflow_repo.delete_step.assert_not_called()


async def test_delete_step_success(
    workflow_service: StudioWorkflowService, admin_token: TokenData, mock_workflow_repo: Any
) -> None:
    step_data = _valid_step_dict("sp_0123456789abcdef01", is_system_core=False, org_id="org_123")
    mock_workflow_repo.get_step_by_id.return_value = step_data
    await workflow_service.delete_step(admin_token, step_data["id"])
    mock_workflow_repo.delete_step.assert_called_once_with(step_data["id"], force_delete=False)


async def test_create_step_draft_no_protocol_block_raises(
    workflow_service: StudioWorkflowService, admin_token: TokenData, mock_prompt_block_repo: Any
) -> None:
    mock_prompt_block_repo.get_all_prompt_blocks.return_value = []
    with pytest.raises(AppException) as exc_info:
        await workflow_service.create_step_draft(admin_token)
    assert exc_info.value.details["error_code"] == ErrorCodes.STATE_INTEGRITY_ERROR


async def test_create_step_draft_success(
    workflow_service: StudioWorkflowService,
    admin_token: TokenData,
    mock_prompt_block_repo: Any,
    mock_workflow_repo: Any,
) -> None:
    mock_prompt_block_repo.get_all_prompt_blocks.return_value = [
        {"id": "blk_0123456789abcdef01", "category_id": "protocol"}
    ]
    mock_workflow_repo.get_step_by_id.side_effect = lambda id_: _valid_step_dict(id_, org_id="org_123")
    res = await workflow_service.create_step_draft(admin_token)
    assert res is not None


async def test_clone_step_not_found(
    workflow_service: StudioWorkflowService, admin_token: TokenData, mock_workflow_repo: Any
) -> None:
    mock_workflow_repo.get_step_by_id.return_value = None
    with pytest.raises(ResourceNotFoundError):
        await workflow_service.clone_step(admin_token, "sp_missing")


async def test_clone_step_success(
    workflow_service: StudioWorkflowService, admin_token: TokenData, mock_workflow_repo: Any
) -> None:
    step_data = _valid_step_dict("sp_0123456789abcdef01", org_id="org_123")
    mock_workflow_repo.get_step_by_id.side_effect = [
        step_data,
        None,
        {**step_data, "id": "sp_0123456789abcdef02"},
    ]
    res = await workflow_service.clone_step(admin_token, step_data["id"])
    assert res is not None
