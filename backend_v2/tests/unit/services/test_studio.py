from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend_v2.exceptions import AppException, ErrorCodes, PermissionDeniedError, ResourceNotFoundError
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.domain.prompt_blocks import PromptBlock
from backend_v2.models.v2_core import Step, Workflow
from backend_v2.services.studio import (
    StudioLexiconService,
    StudioOutputProfileService,
    StudioPromptBlockService,
    StudioSimulationService,
    StudioSystemConfigService,
    StudioWorkflowService,
)
from backend_v2.services.studio.auth_validator import enforce_modification_rights, enforce_tenant_isolation

pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_workflow_repo() -> Any:
    return AsyncMock()


@pytest.fixture
def mock_component_repo() -> Any:
    return AsyncMock()


@pytest.fixture
def mock_system_repo() -> Any:
    return AsyncMock()


@pytest.fixture
def system_config_service(mock_system_repo: Any) -> Any:
    return StudioSystemConfigService(system_repo=mock_system_repo)


@pytest.fixture
def lexicon_service(mock_system_repo: Any) -> Any:
    return StudioLexiconService(system_repo=mock_system_repo)


@pytest.fixture
def workflow_service(
    mock_workflow_repo: Any, mock_seed_output_profile_repo: Any, mock_seed_prompt_block_repo: Any
) -> Any:
    return StudioWorkflowService(
        workflow_repo=mock_workflow_repo,
        output_profile_repo=mock_seed_output_profile_repo,
        prompt_block_repo=mock_seed_prompt_block_repo,
    )


@pytest.fixture
def prompt_block_service(mock_seed_prompt_block_repo: Any, mock_system_repo: Any) -> Any:
    return StudioPromptBlockService(prompt_block_repo=mock_seed_prompt_block_repo, system_repo=mock_system_repo)


@pytest.fixture
def output_profile_service(mock_seed_output_profile_repo: Any, workflow_service: Any) -> Any:
    return StudioOutputProfileService(
        output_profile_repo=mock_seed_output_profile_repo, workflow_service=workflow_service
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


async def test_enforce_tenant_isolation_success(user_token: Any) -> None:
    enforce_tenant_isolation(user_token, "org_123", "workflow", "wf_1234567890abcdef12")


async def test_enforce_tenant_isolation_failure(user_token: Any) -> None:
    with pytest.raises(PermissionDeniedError):
        enforce_tenant_isolation(user_token, "org_999", "workflow", "wf_1234567890abcdef12")


async def test_enforce_tenant_isolation_root(root_token: Any) -> None:
    enforce_tenant_isolation(root_token, "org_999", "workflow", "wf_1234567890abcdef12")


async def test_enforce_modification_rights_success(admin_token: Any) -> None:
    enforce_modification_rights(admin_token, "org_123")


async def test_enforce_modification_rights_failure_role(user_token: Any, caplog: Any) -> None:
    with pytest.raises(PermissionDeniedError):
        enforce_modification_rights(user_token, "org_123")
    assert user_token.id in caplog.text


async def test_enforce_modification_rights_failure_tenant(admin_token: Any, caplog: Any) -> None:
    with pytest.raises(PermissionDeniedError):
        enforce_modification_rights(admin_token, "org_999")
    assert admin_token.id in caplog.text


async def test_list_workflows_empty(
    workflow_service: Any, root_token: Any, mock_workflow_repo: Any, mock_component_repo: Any
) -> None:
    mock_workflow_repo.get_all_workflows.return_value = []
    mock_component_repo.get_all_output_profiles.return_value = []
    res = await workflow_service.list_workflows(root_token)
    assert res == []


async def test_list_workflows_with_data(
    workflow_service: Any, root_token: Any, mock_workflow_repo: Any, mock_component_repo: Any
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
        "allowed_exports": ["pdf"],
        "historical_context_mode": "DISABLED",
    }
    mock_workflow_repo.get_all_workflows.return_value = [wf_data]
    mock_component_repo.get_all_output_profiles.return_value = []
    res = await workflow_service.list_workflows(root_token)
    assert len(res) == 1
    assert res[0].id == "wf_1234567890abcdef12"


async def test_get_workflow_not_found(
    root_token: Any, workflow_service: Any, mock_workflow_repo: Any, caplog: Any
) -> None:
    mock_workflow_repo.get_workflow_by_id.return_value = None
    with pytest.raises(ResourceNotFoundError):
        await workflow_service.get_workflow(root_token, "wf_invalid")
    assert root_token.id in caplog.text


async def test_delete_workflow(workflow_service: Any, admin_token: Any, mock_workflow_repo: Any) -> None:
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
        "allowed_exports": ["pdf"],
        "historical_context_mode": "DISABLED",
    }
    mock_workflow_repo.get_workflow_by_id.return_value = wf_data
    await workflow_service.delete_workflow(admin_token, "wf_1234567890abcdef12")
    mock_workflow_repo.delete_workflow.assert_called_once_with("wf_1234567890abcdef12")


async def test_create_workflow_draft(workflow_service: Any, admin_token: Any, mock_workflow_repo: Any) -> None:
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
        "allowed_exports": ["pdf"],
        "historical_context_mode": "DISABLED",
    }
    res = await workflow_service.create_workflow_draft(admin_token)
    assert res.status == "draft"


async def test_get_available_models_success(system_config_service: Any, root_token: Any) -> None:
    mock_handler = MagicMock()
    mock_handler.fetch_all_available_models.return_value = {"openai": ["gpt-4o"]}
    res = system_config_service.get_available_models(root_token, mock_handler)
    assert res == ["gpt-4o"]


async def test_get_available_models_permission_denied(system_config_service: Any, user_token: Any) -> None:
    mock_handler = MagicMock()
    with pytest.raises(PermissionDeniedError):
        system_config_service.get_available_models(user_token, mock_handler)


async def test_system_config_get(system_config_service: Any, root_token: Any, mock_system_repo: Any) -> None:
    mock_system_repo.get_model_registry.return_value = {
        "id": "sys_1234567890abcdef12",
        "slug": "sys_1",
        "type": "model_registry",
        "models": {},
    }
    res = await system_config_service.get_system_config(root_token, "sys_1234567890abcdef12")
    assert res.id == "sys_1234567890abcdef12"


async def test_system_config_permission_denied(system_config_service: Any, user_token: Any, caplog: Any) -> None:
    # Attempting to fetch system config with normal user role should fail
    with pytest.raises(PermissionDeniedError):
        await system_config_service.get_system_config(user_token, "sys_model_registry")
    assert user_token.id in caplog.text


async def test_list_steps_empty(workflow_service: Any, root_token: Any, mock_workflow_repo: Any) -> None:
    mock_workflow_repo.get_all_steps.return_value = []
    res = await workflow_service.list_steps(root_token)
    assert res == []


async def test_get_step_not_found(workflow_service: Any, root_token: Any, mock_workflow_repo: Any) -> None:
    mock_workflow_repo.get_step_by_id.return_value = None
    with pytest.raises(ResourceNotFoundError):
        await workflow_service.get_step(root_token, "step_missing")


async def test_delete_step(workflow_service: Any, admin_token: Any, mock_workflow_repo: Any) -> None:
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
    await workflow_service.delete_step(admin_token, "step_1234567890abcdef12")
    mock_workflow_repo.delete_step.assert_called_once()


async def test_delete_step_protected_system_core_fails_fast(
    workflow_service: Any, admin_token: Any, mock_workflow_repo: Any
) -> None:
    """PROMISE: Deleting a protected system core step raises AppException(SYSTEM_PROTECTED_RESOURCE)."""
    step_data = {
        "id": "sp_db849f9790984585",
        "slug": "input_processing",
        "name": {"default_locale": "en", "translations": {"en": "Input Processing"}},
        "type": "logic",
        "hook": "input_processing_hook",
        "organization_id": "org_123",
        "is_system_core": True,
    }
    mock_workflow_repo.get_step_by_id.return_value = step_data
    with pytest.raises(AppException) as exc_info:
        await workflow_service.delete_step(admin_token, "sp_db849f9790984585")

    assert exc_info.value.status_code == 403
    assert exc_info.value.details["error_code"] == ErrorCodes.SYSTEM_PROTECTED_RESOURCE.value
    mock_workflow_repo.delete_step.assert_not_called()


async def test_save_step_protected_system_core_slug_mutation_fails_fast(
    workflow_service: Any, admin_token: Any, mock_workflow_repo: Any
) -> None:
    """PROMISE: Mutating the slug or is_system_core of a system core step raises AppException(SYSTEM_PROTECTED_RESOURCE)."""
    existing_step_data = {
        "id": "sp_db849f9790984585",
        "slug": "input_processing",
        "name": {"default_locale": "en", "translations": {"en": "Input Processing"}},
        "type": "logic",
        "hook": "input_processing_hook",
        "organization_id": "org_123",
        "is_system_core": True,
    }
    mock_workflow_repo.get_step_by_id.return_value = existing_step_data

    modified_step = Step(
        id="sp_db849f9790984585",
        slug="mutated_slug",
        name={"default_locale": "en", "translations": {"en": "Input Processing"}},
        type="logic",
        hook="input_processing_hook",
        organization_id="org_123",
        is_system_core=True,
    )

    with pytest.raises(AppException) as exc_info:
        await workflow_service.save_step(admin_token, "sp_db849f9790984585", modified_step)

    assert exc_info.value.status_code == 403
    assert exc_info.value.details["error_code"] == ErrorCodes.SYSTEM_PROTECTED_RESOURCE.value


async def test_list_prompt_blocks_empty(
    prompt_block_service: Any, root_token: Any, mock_seed_prompt_block_repo: Any
) -> None:
    mock_seed_prompt_block_repo.get_all_prompt_blocks.return_value = []
    res = await prompt_block_service.list_prompt_blocks(root_token)
    assert res == []


async def test_get_prompt_block_not_found(
    prompt_block_service: Any, root_token: Any, mock_seed_prompt_block_repo: Any, caplog: Any
) -> None:
    mock_seed_prompt_block_repo.get_prompt_block_by_id.return_value = None
    with pytest.raises(ResourceNotFoundError):
        await prompt_block_service.get_prompt_block(root_token, "blk_missing")
    assert root_token.id in caplog.text


async def test_delete_prompt_block(
    prompt_block_service: Any, admin_token: Any, mock_seed_prompt_block_repo: Any
) -> None:
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
    await prompt_block_service.delete_prompt_block(admin_token, "blk_1234567890abcdef12")
    mock_seed_prompt_block_repo.delete_prompt_block.assert_called_once()


async def test_list_output_profiles_empty(
    output_profile_service: Any, root_token: Any, mock_seed_output_profile_repo: Any
) -> None:
    mock_seed_output_profile_repo.get_all_output_profiles.return_value = []
    res = await output_profile_service.list_output_profiles(root_token)
    assert res == []


async def test_get_output_profile_not_found(
    output_profile_service: Any, root_token: Any, mock_seed_output_profile_repo: Any, caplog: Any
) -> None:
    mock_seed_output_profile_repo.get_output_profile_by_id.return_value = None
    with pytest.raises(ResourceNotFoundError):
        await output_profile_service.get_output_profile(root_token, "prof_missing")
    assert root_token.id in caplog.text


async def test_delete_output_profile(
    output_profile_service: Any, admin_token: Any, mock_seed_output_profile_repo: Any
) -> None:
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
    await output_profile_service.delete_output_profile(admin_token, "prof_1234567890abcdef12")
    mock_seed_output_profile_repo.delete_output_profile.assert_called_once()


async def test_list_output_profiles_corrupted_legacy_keys_raises_state_integrity_error(
    output_profile_service: Any, root_token: Any, mock_seed_output_profile_repo: Any
) -> None:
    """Regression test: OutputProfile with legacy purged keys in synthesis raises STATE_INTEGRITY_ERROR."""
    corrupted_profile = {
        "id": "prof_1234567890abcdef12",
        "slug": "prof_1",
        "name": {"default_locale": "en", "translations": {"en": "Prof"}},
        "organization_id": "org_123",
        "workflow_id": "wf_1234567890abcdef12",
        "synthesis": {
            "model_strategy": "synthesis",
            "historical_context_mode": "DISABLED",
            "enable_pii_masking": False,
            "allowed_exports": ["pdf"],
            "omit_empty_sections": True,
            "allowed_mcp_tools": [],
        },
    }
    mock_seed_output_profile_repo.get_all_output_profiles.return_value = [corrupted_profile]
    with pytest.raises(AppException) as exc_info:
        await output_profile_service.list_output_profiles(root_token)
    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.STATE_INTEGRITY_ERROR


async def test_list_workflows_corrupted_legacy_output_profile_raises_state_integrity_error(
    workflow_service: Any, root_token: Any, mock_workflow_repo: Any, mock_seed_output_profile_repo: Any
) -> None:
    """Regression test: list_workflows stitching with corrupted output profile in DB raises STATE_INTEGRITY_ERROR."""
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
        "allowed_exports": ["pdf"],
        "historical_context_mode": "DISABLED",
    }
    corrupted_profile = {
        "id": "prof_1234567890abcdef12",
        "slug": "prof_1",
        "name": {"default_locale": "en", "translations": {"en": "Prof"}},
        "organization_id": "org_123",
        "workflow_id": "wf_1234567890abcdef12",
        "synthesis": {
            "model_strategy": "synthesis",
            "historical_context_mode": "DISABLED",
        },
    }
    mock_workflow_repo.get_all_workflows.return_value = [wf_data]
    mock_seed_output_profile_repo.get_all_output_profiles.return_value = [corrupted_profile]
    with pytest.raises(AppException) as exc_info:
        await workflow_service.list_workflows(root_token)
    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.STATE_INTEGRITY_ERROR


async def test_list_mcp_gateways_empty(system_config_service: Any, root_token: Any, mock_system_repo: Any) -> None:
    mock_system_repo.get_mcp_gateways.return_value = None
    res = await system_config_service.list_mcp_gateways(root_token)
    assert res == []


async def test_save_workflow(workflow_service: Any, admin_token: Any, mock_workflow_repo: Any) -> None:
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
        "allowed_exports": ["pdf"],
        "historical_context_mode": "DISABLED",
    }
    mock_workflow_repo.get_workflow_by_id.return_value = wf_data
    res = await workflow_service.save_workflow(admin_token, "wf_1234567890abcdef12", Workflow.model_validate(wf_data))
    assert res.id == "wf_1234567890abcdef12"


async def test_save_step(workflow_service: Any, admin_token: Any, mock_workflow_repo: Any) -> None:
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
    res = await workflow_service.save_step(admin_token, "step_1234567890abcdef12", Step.model_validate(step_data))
    assert res.id == "step_1234567890abcdef12"


async def test_save_step_direct_organization_id_access(
    workflow_service: Any, admin_token: Any, mock_workflow_repo: Any
) -> None:
    """PROMISE: Prove typed direct access to step.organization_id during saving without duck typing."""
    step_data = {
        "id": "sp_1234567890abcdef12",
        "slug": "step_direct_org",
        "name": {"default_locale": "en", "translations": {"en": "Direct Org Step"}},
        "type": "llm",
        "organization_id": "org_123",
        "safety": "safe",
        "model_strategy": "fast",
        "criteria_block_ids": ["blk_1234567890abcdef12"],
        "extraction_protocol_block_id": "blk_1234567890abcdef12",
    }
    step_obj = Step.model_validate(step_data)
    assert step_obj.organization_id == "org_123"

    mock_workflow_repo.get_step_by_id.return_value = step_data
    res = await workflow_service.save_step(admin_token, "sp_1234567890abcdef12", step_obj)
    assert res.organization_id == "org_123"


async def test_save_prompt_block(prompt_block_service: Any, admin_token: Any, mock_seed_prompt_block_repo: Any) -> None:
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
    res = await prompt_block_service.save_prompt_block(
        admin_token, "blk_1234567890abcdef12", PromptBlock.model_validate(blk_data)
    )
    assert res.id == "blk_1234567890abcdef12"


from unittest.mock import patch


@pytest.mark.asyncio
@patch("backend_v2.services.studio.lexicon_service.LLMClient.from_strategy", new_callable=AsyncMock)
@patch("backend_v2.services.studio.lexicon_service.LLMTaskExecutor")
async def test_discover_new_performative_phrases_success(
    mock_executor_class: Any, mock_llm_client: Any, lexicon_service: Any
) -> None:
    mock_llm_client.return_value = AsyncMock()

    mock_executor_instance = mock_executor_class.return_value
    mock_executor_instance.execute_structured_task = AsyncMock(
        return_value=({"phrases": [{"word": "test", "translation_en": "test"}]}, {})
    )

    res = await lexicon_service.discover_new_performative_phrases("fi")
    assert res is not None


@pytest.mark.asyncio
@patch("backend_v2.services.studio.lexicon_service.LLMClient.from_strategy", new_callable=AsyncMock)
@patch("backend_v2.services.studio.lexicon_service.LLMTaskExecutor")
async def test_translate_performative_phrases_success(
    mock_executor_class: Any, mock_llm_client: Any, lexicon_service: Any, mock_system_repo: Any
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

    res = await lexicon_service.translate_performative_phrases("fi")
    assert res is not None


async def test_get_performative_lexicons_config_not_found(
    lexicon_service: Any, mock_system_repo: Any, caplog: Any
) -> None:
    mock_system_repo.get_system_config.return_value = None
    with pytest.raises(ResourceNotFoundError):
        await lexicon_service.get_performative_lexicons_config()
    from backend_v2.models.enums import SystemConfigID

    assert SystemConfigID.PERFORMATIVE_LEXICONS.value in caplog.text


from unittest.mock import AsyncMock, PropertyMock


@pytest.mark.asyncio
async def test_simulate_workflow_fatal_error(root_token: Any, caplog: Any) -> None:
    service = StudioSimulationService(prompt_block_service=AsyncMock())

    mock_workflow = MagicMock()
    mock_workflow.id = "wf_123"
    mock_workflow.expected_inputs = []

    # Create a step that will cause an attribute error or similar when accessed
    mock_step = MagicMock()
    mock_step.id = "step_1"
    # Setting depends_on to a property that raises an exception when accessed
    type(mock_step).depends_on = PropertyMock(side_effect=RuntimeError("Test Error"))

    mock_workflow.steps = [mock_step]

    res = await service.simulate_workflow(root_token, mock_workflow)
    assert res["valid"] is False
    assert "Fatal error resolving DAG structure." in res["errors"]
    assert root_token.id in caplog.text
