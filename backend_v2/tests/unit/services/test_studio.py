from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend_v2.exceptions import PermissionDeniedError, ResourceNotFoundError
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.v2_core import PromptBlock, Step, Workflow
from backend_v2.services.studio import StudioService


@pytest.fixture
def mock_workflow_repo() -> Any:
    return AsyncMock()


@pytest.fixture
def mock_component_repo() -> Any:
    return AsyncMock()


@pytest.fixture
def mock_knowledge_repo() -> Any:
    return AsyncMock()


@pytest.fixture
def mock_system_repo() -> Any:
    return AsyncMock()


@pytest.fixture
def studio_service(
    mock_workflow_repo: Any, 
    mock_component_repo: Any, 
    mock_knowledge_repo: Any, 
    mock_system_repo: Any,
    mock_seed_prompt_block_repo: Any,
    mock_seed_output_profile_repo: Any
) -> Any:
    return StudioService(
        workflow_repo=mock_workflow_repo,
        component_repo=mock_component_repo,
        prompt_block_repo=mock_seed_prompt_block_repo,
        output_profile_repo=mock_seed_output_profile_repo,
        knowledge_repo=mock_knowledge_repo,
        system_repo=mock_system_repo,
    )


@pytest.fixture
def root_token() -> Any:
    return TokenData(id="root_user", role=UserRole.ROOT)


@pytest.fixture
def admin_token() -> Any:
    return TokenData(id="admin_user", role=UserRole.ADMIN, organization_id="org_123")


@pytest.fixture
def user_token() -> Any:
    return TokenData(id="user1", role=UserRole.MEMBER, organization_id="org_123")


async def test_enforce_tenant_isolation_success(studio_service: Any, user_token: Any) -> None:
    studio_service._enforce_tenant_isolation(user_token, "org_123", "workflow", "wf_1234567890abcdef12")


async def test_enforce_tenant_isolation_failure(studio_service: Any, user_token: Any) -> None:
    with pytest.raises(PermissionDeniedError):
        studio_service._enforce_tenant_isolation(user_token, "org_999", "workflow", "wf_1234567890abcdef12")


async def test_enforce_tenant_isolation_root(studio_service: Any, root_token: Any) -> None:
    studio_service._enforce_tenant_isolation(root_token, "org_999", "workflow", "wf_1234567890abcdef12")


async def test_enforce_modification_rights_success(studio_service: Any, admin_token: Any) -> None:
    studio_service._enforce_modification_rights(admin_token, "org_123")


async def test_enforce_modification_rights_failure_role(studio_service: Any, user_token: Any) -> None:
    with pytest.raises(PermissionDeniedError):
        studio_service._enforce_modification_rights(user_token, "org_123")


async def test_enforce_modification_rights_failure_tenant(studio_service: Any, admin_token: Any) -> None:
    with pytest.raises(PermissionDeniedError):
        studio_service._enforce_modification_rights(admin_token, "org_999")


async def test_list_workflows_empty(
    studio_service: Any, root_token: Any, mock_workflow_repo: Any, mock_component_repo: Any
) -> None:
    mock_workflow_repo.get_all_workflows.return_value = []
    mock_component_repo.get_all_output_profiles.return_value = []
    res = await studio_service.list_workflows(root_token)
    assert res == []


async def test_list_workflows_with_data(
    studio_service: Any, root_token: Any, mock_workflow_repo: Any, mock_component_repo: Any
) -> None:
    wf_data = {
        "id": "wf_1234567890abcdef12",
        "slug": "wf-1",
        "name": {"default_locale": "en", "translations": {"en": "Test Workflow"}},
        "description": {"default_locale": "en", "translations": {"en": "Test Desc"}},
        "status": "active",
        "version": 1,
        "organization_id": "org_123",
        "expected_inputs": [],
        "steps": [],
        "default_profile_id": "prof_1234567890abcdef12",
    }
    mock_workflow_repo.get_all_workflows.return_value = [wf_data]
    mock_component_repo.get_all_output_profiles.return_value = []
    res = await studio_service.list_workflows(root_token)
    assert len(res) == 1
    assert res[0].id == "wf_1234567890abcdef12"


async def test_get_workflow_not_found(studio_service: Any, root_token: Any, mock_workflow_repo: Any) -> None:
    mock_workflow_repo.get_workflow_by_id.return_value = None
    with pytest.raises(ResourceNotFoundError):
        await studio_service.get_workflow(root_token, "wf_missing")


async def test_delete_workflow(studio_service: Any, admin_token: Any, mock_workflow_repo: Any) -> None:
    wf_data = {
        "id": "wf_1234567890abcdef12",
        "slug": "wf-1",
        "name": {"default_locale": "en", "translations": {"en": "Test Workflow"}},
        "description": {"default_locale": "en", "translations": {"en": "Test Desc"}},
        "status": "active",
        "version": 1,
        "organization_id": "org_123",
        "expected_inputs": [],
        "steps": [],
        "default_profile_id": "prof_1234567890abcdef12",
    }
    mock_workflow_repo.get_workflow_by_id.return_value = wf_data
    await studio_service.delete_workflow(admin_token, "wf_1234567890abcdef12")
    mock_workflow_repo.delete_workflow.assert_called_once_with("wf_1234567890abcdef12")


async def test_create_workflow_draft(studio_service: Any, admin_token: Any, mock_workflow_repo: Any) -> None:
    mock_workflow_repo.get_workflow_by_id.return_value = {
        "id": "wf_1234567890abcdef12",
        "slug": "wf_test",
        "name": {"default_locale": "en", "translations": {"en": "Test"}},
        "description": {"default_locale": "en", "translations": {"en": "Desc"}},
        "status": "draft",
        "version": 1,
        "organization_id": "org_123",
        "expected_inputs": [],
        "steps": [],
        "default_profile_id": "prof_1234567890abcdef12",
    }
    res = await studio_service.create_workflow_draft(admin_token)
    assert res.status == "draft"


async def test_get_available_models_success(studio_service: Any, root_token: Any) -> None:
    mock_handler = MagicMock()
    mock_handler.fetch_all_available_models.return_value = {"openai": ["gpt-4o"]}
    res = studio_service.get_available_models(root_token, mock_handler)
    assert res == ["gpt-4o"]


async def test_get_available_models_permission_denied(studio_service: Any, user_token: Any) -> None:
    mock_handler = MagicMock()
    with pytest.raises(PermissionDeniedError):
        studio_service.get_available_models(user_token, mock_handler)


async def test_system_config_get(studio_service: Any, root_token: Any, mock_system_repo: Any) -> None:
    mock_system_repo.get_model_registry.return_value = {
        "id": "sys_1234567890abcdef12",
        "slug": "sys_1",
        "type": "model_registry",
        "models": {},
    }
    res = await studio_service.get_system_config(root_token, "sys_1234567890abcdef12")
    assert res.id == "sys_1234567890abcdef12"


async def test_system_config_permission_denied(studio_service: Any, admin_token: Any, mock_system_repo: Any) -> None:
    with pytest.raises(PermissionDeniedError):
        await studio_service.get_system_config(admin_token, "sys_1234567890abcdef12")


async def test_list_steps_empty(studio_service: Any, root_token: Any, mock_workflow_repo: Any) -> None:
    mock_workflow_repo.get_all_steps.return_value = []
    res = await studio_service.list_steps(root_token)
    assert res == []


async def test_get_step_not_found(studio_service: Any, root_token: Any, mock_workflow_repo: Any) -> None:
    mock_workflow_repo.get_step_by_id.return_value = None
    with pytest.raises(ResourceNotFoundError):
        await studio_service.get_step(root_token, "step_missing")


async def test_delete_step(studio_service: Any, admin_token: Any, mock_workflow_repo: Any) -> None:
    step_data = {
        "id": "step_1234567890abcdef12",
        "slug": "step_1",
        "name": {"default_locale": "en", "translations": {"en": "Test Step"}},
        "type": "llm",
        "organization_id": "org_123",
        "safety": "safe",
        "model_strategy": "fast",
        "criteria_block_ids": ["blk_1234567890abcdef12"],
        "extraction_protocol_block_id": "blk_1234567890abcdef12",
    }
    mock_workflow_repo.get_step_by_id.return_value = step_data
    await studio_service.delete_step(admin_token, "step_1234567890abcdef12")
    mock_workflow_repo.delete_step.assert_called_once()


async def test_list_prompt_blocks_empty(studio_service: Any, root_token: Any, mock_seed_prompt_block_repo: Any) -> None:
    mock_seed_prompt_block_repo.get_all_prompt_blocks.return_value = []
    res = await studio_service.list_prompt_blocks(root_token)
    assert res == []


async def test_get_prompt_block_not_found(studio_service: Any, root_token: Any, mock_seed_prompt_block_repo: Any) -> None:
    mock_seed_prompt_block_repo.get_prompt_block_by_id.return_value = None
    with pytest.raises(ResourceNotFoundError):
        await studio_service.get_prompt_block(root_token, "blk_missing")


async def test_delete_prompt_block(studio_service: Any, admin_token: Any, mock_seed_prompt_block_repo: Any) -> None:
    blk_data = {
        "id": "blk_1234567890abcdef12",
        "slug": "blk_1",
        "label": {"default_locale": "en", "translations": {"en": "Block"}},
        "description": {"default_locale": "en", "translations": {"en": "Desc"}},
        "category_id": "agent_role",
        "type": "string",
        "organization_id": "org_123",
    }
    mock_seed_prompt_block_repo.get_prompt_block_by_id.side_effect = None
    mock_seed_prompt_block_repo.get_prompt_block_by_id.return_value = blk_data
    await studio_service.delete_prompt_block(admin_token, "blk_1234567890abcdef12")
    mock_seed_prompt_block_repo.delete_prompt_block.assert_called_once()


async def test_list_output_profiles_empty(studio_service: Any, root_token: Any, mock_seed_output_profile_repo: Any) -> None:
    mock_seed_output_profile_repo.get_all_output_profiles.return_value = []
    res = await studio_service.list_output_profiles(root_token)
    assert res == []


async def test_get_output_profile_not_found(studio_service: Any, root_token: Any, mock_seed_output_profile_repo: Any) -> None:
    mock_seed_output_profile_repo.get_output_profile_by_id.return_value = None
    with pytest.raises(ResourceNotFoundError):
        await studio_service.get_output_profile(root_token, "prof_missing")


async def test_delete_output_profile(studio_service: Any, admin_token: Any, mock_seed_output_profile_repo: Any) -> None:
    prof_data = {
        "id": "prof_1234567890abcdef12",
        "slug": "prof_1",
        "name": {"default_locale": "en", "translations": {"en": "Prof"}},
        "category_id": "report",
        "layouts": [],
        "organization_id": "org_123",
        "workflow_id": "wf_1234567890abcdef12",
    }
    mock_seed_output_profile_repo.get_output_profile_by_id.side_effect = None
    mock_seed_output_profile_repo.get_output_profile_by_id.return_value = prof_data
    await studio_service.delete_output_profile(admin_token, "prof_1234567890abcdef12")
    mock_seed_output_profile_repo.delete_output_profile.assert_called_once()


async def test_list_mcp_gateways_empty(studio_service: Any, root_token: Any, mock_system_repo: Any) -> None:
    mock_system_repo.get_mcp_gateways.return_value = None
    res = await studio_service.list_mcp_gateways(root_token)
    assert res == []


async def test_save_workflow(studio_service: Any, admin_token: Any, mock_workflow_repo: Any) -> None:
    wf_data = {
        "id": "wf_1234567890abcdef12",
        "slug": "wf-1",
        "name": {"default_locale": "en", "translations": {"en": "Test Workflow"}},
        "description": {"default_locale": "en", "translations": {"en": "Test Desc"}},
        "status": "active",
        "version": 1,
        "organization_id": "org_123",
        "expected_inputs": [],
        "steps": [],
        "default_profile_id": "prof_1234567890abcdef12",
    }
    mock_workflow_repo.get_workflow_by_id.return_value = wf_data
    res = await studio_service.save_workflow(admin_token, "wf_1234567890abcdef12", Workflow.model_validate(wf_data))
    assert res.id == "wf_1234567890abcdef12"


async def test_save_step(studio_service: Any, admin_token: Any, mock_workflow_repo: Any) -> None:
    step_data = {
        "id": "step_1234567890abcdef12",
        "slug": "step_1",
        "name": {"default_locale": "en", "translations": {"en": "Test Step"}},
        "type": "llm",
        "organization_id": "org_123",
        "safety": "safe",
        "model_strategy": "fast",
        "criteria_block_ids": ["blk_1234567890abcdef12"],
        "extraction_protocol_block_id": "blk_1234567890abcdef12",
    }
    mock_workflow_repo.get_step_by_id.return_value = step_data
    res = await studio_service.save_step(admin_token, "step_1234567890abcdef12", Step.model_validate(step_data))
    assert res.id == "step_1234567890abcdef12"


async def test_save_prompt_block(studio_service: Any, admin_token: Any, mock_seed_prompt_block_repo: Any) -> None:
    blk_data = {
        "id": "blk_1234567890abcdef12",
        "slug": "blk_1",
        "label": {"default_locale": "en", "translations": {"en": "Block"}},
        "description": {"default_locale": "en", "translations": {"en": "Desc"}},
        "category_id": "agent_role",
        "type": "string",
        "organization_id": "org_123",
    }
    mock_seed_prompt_block_repo.get_prompt_block_by_id.side_effect = None
    mock_seed_prompt_block_repo.get_prompt_block_by_id.return_value = blk_data
    res = await studio_service.save_prompt_block(
        admin_token, "blk_1234567890abcdef12", PromptBlock.model_validate(blk_data)
    )
    assert res.id == "blk_1234567890abcdef12"


from unittest.mock import patch


@pytest.mark.asyncio
@patch("backend_v2.llm.client.LLMClient.from_strategy", new_callable=AsyncMock)
@patch("backend_v2.services.llm_task_executor.LLMTaskExecutor")
async def test_discover_new_performative_phrases_success(
    mock_executor_class: Any, mock_llm_client: Any, studio_service: Any
) -> None:
    mock_llm_client.return_value = AsyncMock()

    mock_executor_instance = mock_executor_class.return_value
    mock_executor_instance.execute_structured_task = AsyncMock(
        return_value=({"phrases": [{"word": "test", "translation_en": "test"}]}, {})
    )

    res = await studio_service.discover_new_performative_phrases("fi")
    assert res is not None


@pytest.mark.asyncio
@patch("backend_v2.llm.client.LLMClient.from_strategy", new_callable=AsyncMock)
@patch("backend_v2.services.llm_task_executor.LLMTaskExecutor")
async def test_translate_performative_phrases_success(
    mock_executor_class: Any, mock_llm_client: Any, studio_service: Any, mock_system_repo: Any
) -> None:
    mock_llm_client.return_value = AsyncMock()

    mock_executor_instance = mock_executor_class.return_value
    mock_executor_instance.execute_structured_task = AsyncMock(
        return_value=({"phrases": [{"word": "test", "translation_en": "test"}]}, {})
    )

    mock_system_repo.get_system_config.return_value = {
        "id": "sys_e0b2a3c4d5e6f7a8",
        "slug": "lexicons",
        "type": "performative_lexicons",
    }

    res = await studio_service.translate_performative_phrases("fi")
    assert res is not None
