"""Unit tests for Admin Studio Model Registry router with stateful repository roundtrips."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from backend_v2.api.routers.studio.model_registry import (
    clone_model_registry,
    create_model_registry,
    delete_model_registry,
    get_all_model_registries,
    get_available_models,
    get_model_registry,
    get_supported_locations,
    get_supported_platforms,
    save_model_registry,
)
from backend_v2.exceptions import ErrorCodes, PermissionDeniedError, ResourceNotFoundError
from backend_v2.llm.handler import LLMHandler
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.domain.system_config import ModelProfile, SystemConfigModelRegistry
from backend_v2.models.enums import CognitiveTier, LLMPlatformType, LLMProvider
from backend_v2.services.studio.system_config_service import StudioSystemConfigService
from backend_v2.tests.fakes.in_memory_repositories import InMemorySystemRepository


@pytest.fixture
def root_user() -> TokenData:
    """Provide ROOT token for stateful system configuration tests."""
    return TokenData(
        id="usr_root000000000000000000000001",
        email="root@example.com",
        role=UserRole.ROOT,
        organization_id="org_root000000000000000000000001",
    )


@pytest.fixture
def admin_user() -> TokenData:
    """Provide ADMIN token for discovery and RBAC boundary tests."""
    return TokenData(
        id="usr_admin00000000000000000000001",
        email="admin@example.com",
        role=UserRole.ADMIN,
        organization_id="org_admin00000000000000000000001",
    )


@pytest.fixture
def member_user() -> TokenData:
    """Provide non-privileged MEMBER token for negative RBAC boundary tests."""
    return TokenData(
        id="usr_member0000000000000000000001",
        email="member@example.com",
        role=UserRole.MEMBER,
        organization_id="org_member0000000000000000000001",
    )


@pytest.fixture
def studio_service() -> StudioSystemConfigService:
    """Provide a real StudioSystemConfigService backed by stateful InMemorySystemRepository."""
    return StudioSystemConfigService(system_repo=InMemorySystemRepository())


def test_get_available_models(admin_user: TokenData, studio_service: StudioSystemConfigService) -> None:
    """Verify available models endpoint flattens and sorts discovered models through StudioSystemConfigService."""
    mock_llm_handler = MagicMock(spec=LLMHandler)
    mock_llm_handler.fetch_all_available_models.return_value = {
        "vertex_ai": ["vertex_ai/gemini-2.5-pro", "vertex_ai/gemini-2.5-flash"],
        "ai_studio": ["gemini/gemini-2.5-flash"],
    }
    res = get_available_models(
        current_user=admin_user,
        llm_handler=mock_llm_handler,
        studio_service=studio_service,
        platform=LLMPlatformType.ALL,
        location="europe-north1",
    )
    assert res == [
        "gemini/gemini-2.5-flash",
        "vertex_ai/gemini-2.5-flash",
        "vertex_ai/gemini-2.5-pro",
    ]
    mock_llm_handler.fetch_all_available_models.assert_called_once_with(
        location="europe-north1",
        platform="all",
    )


def test_get_supported_locations(
    admin_user: TokenData,
    studio_service: StudioSystemConfigService,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify supported locations endpoint returns mock-mode GCP regions via real LLMHandler."""
    mock_settings = MagicMock()
    mock_settings.use_mock_llm = True
    monkeypatch.setattr(
        "backend_v2.services.studio.system_config_service.get_settings",
        lambda: mock_settings,
    )
    llm_handler = LLMHandler(repo=InMemorySystemRepository())
    res = get_supported_locations(
        current_user=admin_user,
        studio_service=studio_service,
        llm_handler=llm_handler,
    )
    loc_ids = [loc.id for loc in res]
    assert "europe-north1" in loc_ids
    assert "us-central1" in loc_ids


def test_get_supported_platforms(admin_user: TokenData, studio_service: StudioSystemConfigService) -> None:
    """Verify supported platforms endpoint returns the 4 registered platform DTOs."""
    res = get_supported_platforms(current_user=admin_user, studio_service=studio_service)
    assert len(res) == 4
    platform_by_id = {p.id: p for p in res}
    assert platform_by_id["vertex_ai"].has_regions is True
    assert platform_by_id["ai_studio"].has_regions is False
    assert platform_by_id["openai"].has_regions is False
    assert platform_by_id["anthropic"].has_regions is False


@pytest.mark.asyncio
async def test_model_registry_router_full_stateful_lifecycle(
    root_user: TokenData,
    member_user: TokenData,
    studio_service: StudioSystemConfigService,
) -> None:
    """Verify stateful create, get, save, clone, list, and delete roundtrips on Model Registry router."""
    initial_registries = await get_all_model_registries(current_user=root_user, studio_service=studio_service)
    initial_count = len(initial_registries)
    assert initial_count >= 1

    # Non-ROOT user receives an empty list on get_all_model_registries
    assert await get_all_model_registries(current_user=member_user, studio_service=studio_service) == []

    # 1. Create a new draft and verify persistence
    draft = await create_model_registry(current_user=root_user, studio_service=studio_service)
    assert draft.id.startswith("sys_")
    assert draft.name == "New Model Registry Draft"

    fetched = await get_model_registry(
        registry_id=draft.id,
        current_user=root_user,
        studio_service=studio_service,
    )
    assert fetched.id == draft.id
    assert fetched.default_provider == LLMProvider.AI_STUDIO

    # 2. Save in-place mutation and verify roundtrip via get_model_registry
    updated_payload = draft.model_copy(
        update={
            "name": "Production Vertex Registry",
            "default_provider": LLMProvider.VERTEX_AI,
        }
    )
    saved = await save_model_registry(
        registry_id=draft.id,
        data=updated_payload,
        current_user=root_user,
        studio_service=studio_service,
    )
    assert saved.id == draft.id
    assert saved.name == "Production Vertex Registry"
    assert saved.default_provider == LLMProvider.VERTEX_AI

    reloaded = await get_model_registry(
        registry_id=draft.id,
        current_user=root_user,
        studio_service=studio_service,
    )
    assert reloaded.name == "Production Vertex Registry"
    assert reloaded.default_provider == LLMProvider.VERTEX_AI

    # 3. Clone the saved registry and verify independent persistence
    cloned = await clone_model_registry(
        registry_id=draft.id,
        current_user=root_user,
        studio_service=studio_service,
    )
    assert cloned.id != draft.id
    assert cloned.id.startswith("sys_")
    assert cloned.name == "Production Vertex Registry (Copy)"

    after_clone_list = await get_all_model_registries(current_user=root_user, studio_service=studio_service)
    assert len(after_clone_list) == initial_count + 2

    # 4. Delete the cloned registry and verify removal from repository
    del_resp = await delete_model_registry(
        registry_id=cloned.id,
        current_user=root_user,
        studio_service=studio_service,
    )
    assert del_resp.status == "success"
    assert del_resp.deleted_id == cloned.id

    with pytest.raises(ResourceNotFoundError) as exc_info:
        await get_model_registry(
            registry_id=cloned.id,
            current_user=root_user,
            studio_service=studio_service,
        )
    assert exc_info.value.error_code == ErrorCodes.RESOURCE_NOT_FOUND


@pytest.mark.asyncio
async def test_model_registry_router_negative_rbac_and_missing_resource(
    root_user: TokenData,
    admin_user: TokenData,
    member_user: TokenData,
    studio_service: StudioSystemConfigService,
) -> None:
    """Negative Boundary 1 & 2: Verify PermissionDeniedError and ResourceNotFoundError across endpoints."""
    mock_llm_handler = MagicMock(spec=LLMHandler)

    # MEMBER cannot access discovery endpoints
    with pytest.raises(PermissionDeniedError) as exc_perm:
        get_available_models(
            current_user=member_user,
            llm_handler=mock_llm_handler,
            studio_service=studio_service,
        )
    assert exc_perm.value.error_code == ErrorCodes.PERMISSION_DENIED

    with pytest.raises(PermissionDeniedError):
        get_supported_locations(
            current_user=member_user,
            studio_service=studio_service,
            llm_handler=mock_llm_handler,
        )

    with pytest.raises(PermissionDeniedError):
        get_supported_platforms(
            current_user=member_user,
            studio_service=studio_service,
        )

    # Non-ROOT (ADMIN or MEMBER) cannot mutate or view individual system config registries
    with pytest.raises(PermissionDeniedError):
        await create_model_registry(current_user=admin_user, studio_service=studio_service)

    with pytest.raises(PermissionDeniedError):
        await get_model_registry(
            registry_id="sys_1234567890abcdef",
            current_user=admin_user,
            studio_service=studio_service,
        )

    with pytest.raises(PermissionDeniedError):
        await clone_model_registry(
            registry_id="sys_1234567890abcdef",
            current_user=admin_user,
            studio_service=studio_service,
        )

    with pytest.raises(PermissionDeniedError):
        await delete_model_registry(
            registry_id="sys_1234567890abcdef",
            current_user=admin_user,
            studio_service=studio_service,
        )

    # Non-existent Opaque Stripe ID triggers ResourceNotFoundError for ROOT
    missing_id = "sys_9999999999999999"
    with pytest.raises(ResourceNotFoundError) as exc_not_found:
        await get_model_registry(
            registry_id=missing_id,
            current_user=root_user,
            studio_service=studio_service,
        )
    assert exc_not_found.value.error_code == ErrorCodes.RESOURCE_NOT_FOUND

    with pytest.raises(ResourceNotFoundError):
        await clone_model_registry(
            registry_id=missing_id,
            current_user=root_user,
            studio_service=studio_service,
        )

    with pytest.raises(ResourceNotFoundError):
        await delete_model_registry(
            registry_id=missing_id,
            current_user=root_user,
            studio_service=studio_service,
        )


def test_model_profile_and_registry_accepts_reasoning_effort_in_additional_params() -> None:
    """Verifies that ModelProfile and SystemConfigModelRegistry accept reasoning_effort in additional_params."""
    payload = {
        "id": "sys_b1c2d3e4f5a60718",
        "name": "Default Model Registry",
        "type": "model_registry",
        "default_provider": "ai_studio",
        "tier_definitions": {
            "fast": {
                "provider": "google",
                "model_name": "gemini-2.5-flash",
                "temperature": 1.0,
                "max_tokens": 8192,
                "tpm_limit": 1000,
                "rpm_limit": 10,
                "additional_params": {},
            },
            "balanced": {
                "provider": "google",
                "model_name": "gemini-2.5-pro",
                "temperature": 1.0,
                "max_tokens": 8192,
                "tpm_limit": 1000,
                "rpm_limit": 10,
                "additional_params": {},
            },
            "deep": {
                "provider": "openai",
                "model_name": "openai/gpt-5.4",
                "temperature": 1.0,
                "max_tokens": 32768,
                "tpm_limit": 1000,
                "rpm_limit": 10,
                "additional_params": {"reasoning_effort": "medium"},
            },
            "reasoning": {
                "provider": "openai",
                "model_name": "openai/gpt-5.4",
                "temperature": 1.0,
                "max_tokens": 32768,
                "tpm_limit": 1000,
                "rpm_limit": 10,
                "additional_params": {"reasoning_effort": "high"},
            },
        },
    }
    registry = SystemConfigModelRegistry.model_validate(payload)
    assert registry.tier_definitions[CognitiveTier.FAST].additional_params.reasoning_effort is None
    assert registry.tier_definitions[CognitiveTier.DEEP].additional_params.reasoning_effort == "medium"
    assert registry.tier_definitions[CognitiveTier.REASONING].additional_params.reasoning_effort == "high"


def test_model_registry_schema_boundary_validation_negative() -> None:
    """Negative Boundary 3: Verify SystemConfigModelRegistry and ModelProfile reject invalid IDs and extra fields."""
    dummy_profile = ModelProfile(
        model_name="gemini/gemini-2.5-flash",
        provider="ai_studio",
        tpm_limit=1000,
        rpm_limit=10,
        temperature=1.0,
        max_tokens=2048,
    )
    tier_defs = {
        CognitiveTier.FAST: dummy_profile,
        CognitiveTier.BALANCED: dummy_profile,
        CognitiveTier.DEEP: dummy_profile,
        CognitiveTier.REASONING: dummy_profile,
    }
    with pytest.raises(ValidationError):
        SystemConfigModelRegistry(
            id="invalid_non_hex_id",
            name="Invalid ID Registry",
            tier_definitions=tier_defs,
        )

    with pytest.raises(ValidationError):
        ModelProfile.model_validate(
            {
                "model_name": "gemini/gemini-2.5-flash",
                "provider": "ai_studio",
                "unexpected_extra_field": "forbidden",
            }
        )
