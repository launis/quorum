import pytest
from unittest.mock import AsyncMock, patch
from typing import Any

from backend_v2.services.studio import StudioService
from backend_v2.database.repository import AbstractWorkflowRepository
from backend_v2.models.auth import TokenData, UserRole, SystemOrganizations
from backend_v2.models.v2_core import Workflow, Step, PromptBlock
from backend_v2.exceptions import PermissionDeniedError, ResourceNotFoundError


@pytest.fixture
def mock_repo() -> AsyncMock:
    repo = AsyncMock(spec=AbstractWorkflowRepository)
    repo.get_all_output_profiles.return_value = []
    return repo


@pytest.fixture
def root_initiator() -> TokenData:
    return TokenData(id="root_user", role=UserRole.ROOT, organization_id=SystemOrganizations.ROOT_SYSTEM)


@pytest.fixture
def tenant_initiator() -> TokenData:
    return TokenData(id="tenant_user", role=UserRole.ADMIN, organization_id="org_123")


@pytest.fixture
def studio_service(mock_repo: AsyncMock) -> StudioService:
    return StudioService(repo=mock_repo)


@pytest.mark.asyncio
async def test_get_workflow_tenant_isolation(
    studio_service: StudioService, mock_repo: AsyncMock, root_initiator: TokenData, tenant_initiator: TokenData
) -> None:
    mock_workflow: dict[str, Any] = {
        "id": "wf_1234567890abcdef",
        "slug": "wf_123",
        "name": {"default_locale": "en", "translations": {"en": "Test WF"}},
        "description": {"default_locale": "en", "translations": {"en": "Test"}},
        "status": "draft",
        "version": 1,
        "is_public": False,
        "organization_id": "org_123",
        "expected_inputs": [],
        "steps": [],
        "default_profile_id": "prof_1234567890abcdef"
    }
    mock_repo.get.return_value = mock_workflow

    # ROOT can access
    wf_root = await studio_service.get_workflow(root_initiator, "wf_1234567890abcdef")
    assert wf_root.id == "wf_1234567890abcdef"

    # Tenant (org_123) can access
    wf_tenant = await studio_service.get_workflow(tenant_initiator, "wf_1234567890abcdef")
    assert wf_tenant.id == "wf_1234567890abcdef"

    # Other tenant cannot access
    other_tenant = TokenData(id="other", role=UserRole.ADMIN, organization_id="org_999")
    with pytest.raises(PermissionDeniedError):
        await studio_service.get_workflow(other_tenant, "wf_1234567890abcdef")


@pytest.mark.asyncio
async def test_save_prompt_block_atomization(
    studio_service: StudioService, mock_repo: AsyncMock, tenant_initiator: TokenData
) -> None:
    mock_block = PromptBlock(
        id="blk_1234567890abcdef",
        slug="blk_123",
        label={"default_locale": "en", "translations": {"en": "Block"}},
        description={"default_locale": "en", "translations": {"en": "Desc"}},
        category_id="general",
        is_evaluative=True,
        type="string",
        organization_id="org_123",
    )

    mock_repo.get.return_value = mock_block.model_dump(mode="json")

    with patch(
        "backend_v2.services.orchestrator.atomizer.PromptAtomizer.atomize_prompt_block", new_callable=AsyncMock
    ) as mock_atomize:
        mock_atomize.return_value = mock_block

        saved = await studio_service.save_prompt_block(tenant_initiator, "blk_1234567890abcdef", mock_block)

        assert saved.id == "blk_1234567890abcdef"
        mock_atomize.assert_called_once_with(mock_block, repository=mock_repo)
        mock_repo.create_raw.assert_called_once()


@pytest.mark.asyncio
async def test_create_step_draft(
    studio_service: StudioService, mock_repo: AsyncMock, tenant_initiator: TokenData
) -> None:
    mock_repo.create_raw.return_value = None

    async def mock_get(collection: str, id: str) -> dict[str, Any]:
        return {
            "id": id,
            "slug": id,
            "name": {"default_locale": "en", "translations": {"en": "New Askel", "fi": "Uusi askel"}},
            "description": {"default_locale": "en", "translations": {"en": "Draft step", "fi": "Luonnos"}},
            "type": "llm",
            "prompt_blocks": ["blk_440a5fef9331451b"],
            "pre_hooks": [],
            "post_hooks": [],
            "safety": "safe",
            "allowed_mcp_tools": [],
            "model_strategy": "fast",
            "organization_id": "org_123",
        }

    mock_repo.get.side_effect = mock_get

    draft = await studio_service.create_step_draft(tenant_initiator)
    assert draft.organization_id == "org_123"
    assert draft.type == "llm"
    assert draft.model_strategy == "fast"


@pytest.mark.asyncio
async def test_stitch_profiles_to_workflows(
    studio_service: StudioService, mock_repo: AsyncMock, root_initiator: TokenData
) -> None:
    mock_workflow: dict[str, Any] = {
        "id": "wf_1234567890abcdef",
        "slug": "wf_123",
        "name": {"default_locale": "en", "translations": {"en": "Test WF"}},
        "description": {"default_locale": "en", "translations": {"en": "Test"}},
        "status": "draft",
        "version": 1,
        "is_public": False,
        "organization_id": "org_123",
        "expected_inputs": [],
        "steps": [],
        "default_profile_id": "prof_1234567890abcdef"
    }

    mock_profile: dict[str, Any] = {
        "id": "prof_1234567890abcdef",
        "slug": "prof_123",
        "workflow_id": "wf_1234567890abcdef",
        "name": {"default_locale": "en", "translations": {"en": "Profile 1"}},
        "visible_metadata": ["date"],
        "display_scale": "original",
        "layouts": [],
    }

    mock_repo.get_all.return_value = [mock_workflow]
    mock_repo.get_all_output_profiles.return_value = [mock_profile]

    wfs = await studio_service.list_workflows(root_initiator)
    assert len(wfs) == 1
    assert wfs[0].output_profiles is not None
    assert "prof_1234567890abcdef" in wfs[0].output_profiles
    assert wfs[0].output_profiles["prof_1234567890abcdef"].name.translations["en"] == "Profile 1"


@pytest.mark.asyncio
async def test_resource_not_found(
    studio_service: StudioService, mock_repo: AsyncMock, root_initiator: TokenData
) -> None:
    mock_repo.get.return_value = None

    with pytest.raises(ResourceNotFoundError):
        await studio_service.get_workflow(root_initiator, "wf_missing")

    with pytest.raises(ResourceNotFoundError):
        await studio_service.delete_step(root_initiator, "step_missing")


@pytest.mark.asyncio
async def test_clone_workflow(
    studio_service: StudioService, mock_repo: AsyncMock, tenant_initiator: TokenData
) -> None:
    mock_workflow: dict[str, Any] = {
        "id": "wf_1234567890abcdef",
        "slug": "wf_123",
        "name": {"default_locale": "en", "translations": {"en": "Test WF"}},
        "description": {"default_locale": "en", "translations": {"en": "Test"}},
        "status": "draft",
        "version": 1,
        "is_public": False,
        "organization_id": "org_123",
        "expected_inputs": [],
        "steps": [],
        "default_profile_id": "prof_1234567890abcdef"
    }
    
    async def mock_get(collection: str, id: str) -> dict[str, Any]:
        data = mock_workflow.copy()
        data["id"] = id
        return data
        
    mock_repo.get.side_effect = mock_get
    
    with patch("backend_v2.services.orchestrator.dag_compiler.DAGCompilerService.validate_workflow"):
        cloned = await studio_service.clone_workflow(tenant_initiator, "wf_1234567890abcdef")
        assert cloned.id != "wf_1234567890abcdef"
        assert cloned.id.startswith("wf_")


@pytest.mark.asyncio
async def test_output_profile_methods(
    studio_service: StudioService, mock_repo: AsyncMock, tenant_initiator: TokenData
) -> None:
    mock_profile: dict[str, Any] = {
        "id": "prof_1234567890abcdef",
        "slug": "prof_123",
        "workflow_id": "wf_1234567890abcdef",
        "organization_id": "org_123",
        "name": {"default_locale": "en", "translations": {"en": "Profile 1"}},
        "visible_metadata": ["date"],
        "display_scale": "original",
        "layouts": [],
    }
    
    mock_repo.get_all_output_profiles.return_value = [mock_profile]
    
    async def mock_get_profile(id: str) -> dict[str, Any]:
        data = mock_profile.copy()
        data["id"] = id
        return data
        
    mock_repo.get_output_profile_by_id.side_effect = mock_get_profile
    
    # Mock workflow to pass validation in save_output_profile
    async def mock_get_workflow(collection: str, id: str) -> dict[str, Any]:
        return {
            "id": id,
            "slug": "wf_1",
            "name": {"default_locale": "en", "translations": {"en": "WF"}},
            "description": {"default_locale": "en", "translations": {"en": "WF"}},
            "status": "draft",
            "version": 1,
            "is_public": False,
            "organization_id": "org_123",
            "default_profile_id": "prof_1234567890abcdef",
            "expected_inputs": [],
            "steps": []
        }
    mock_repo.get.side_effect = mock_get_workflow
    
    # List
    profiles = await studio_service.list_output_profiles(tenant_initiator)
    assert len(profiles) == 1
    assert profiles[0].id == "prof_1234567890abcdef"
    
    # Get
    profile = await studio_service.get_output_profile(tenant_initiator, "prof_1234567890abcdef")
    assert profile.id == "prof_1234567890abcdef"
    
    # Clone
    cloned = await studio_service.clone_output_profile(tenant_initiator, "prof_1234567890abcdef")
    assert cloned.id != "prof_1234567890abcdef"
    assert cloned.id.startswith("prof_")
    
    # Delete
    await studio_service.delete_output_profile(tenant_initiator, "prof_1234567890abcdef")
    mock_repo.delete_output_profile.assert_called_once_with("prof_1234567890abcdef")


@pytest.mark.asyncio
async def test_step_methods(
    studio_service: StudioService, mock_repo: AsyncMock, tenant_initiator: TokenData
) -> None:
    mock_step: dict[str, Any] = {
        "id": "step_1234567890abcdef",
        "slug": "step_123",
        "name": {"default_locale": "en", "translations": {"en": "Test Step"}},
        "type": "llm",
        "prompt_blocks": ["blk_1234567890abcdef"],
        "model_strategy": "fast",
        "organization_id": "org_123"
    }
    
    mock_repo.get_all.return_value = [mock_step]
    
    async def mock_get(collection: str, id: str) -> dict[str, Any]:
        data = mock_step.copy()
        data["id"] = id
        return data
        
    mock_repo.get.side_effect = mock_get
    
    # List
    steps = await studio_service.list_steps(tenant_initiator)
    assert len(steps) == 1
    
    # Get
    step = await studio_service.get_step(tenant_initiator, "step_1234567890abcdef")
    assert step.id == "step_1234567890abcdef"
    
    # Clone
    cloned = await studio_service.clone_step(tenant_initiator, "step_1234567890abcdef")
    assert cloned.id != "step_1234567890abcdef"
    assert cloned.id.startswith("step_")
    
    # Delete
    await studio_service.delete_step(tenant_initiator, "step_1234567890abcdef")
    mock_repo.delete_step.assert_called_once_with("step_1234567890abcdef", force_delete=False)
