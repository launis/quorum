"""Unit and ISTQB boundary tests for multi-registry SystemConfigModelRegistry persistence.

Verifies primary-key lookup, deterministic (name, id) sorting, in-place primary-key
updates, deletion, and negative ResourceNotFoundError boundaries over InMemoryUnitOfWork.
"""

from __future__ import annotations

import pytest
from polyfactory import Use
from polyfactory.factories.pydantic_factory import ModelFactory

from backend_v2.database.repositories.system import SystemRepositoryImpl
from backend_v2.exceptions import AppException, ErrorCodes, ResourceNotFoundError
from backend_v2.models.core_base import generate_opaque_id, generate_uuid7
from backend_v2.models.domain.system_config import (
    AllowedMCPTool,
    ModelProfile,
    ProviderExtraParamsDTO,
    SystemConfigMCPGateways,
    SystemConfigModelRegistry,
)
from backend_v2.models.enums import (
    CognitiveTier,
    EntityPrefix,
    LaxCognitiveTier,
    LLMProvider,
    MCPAuthType,
    MCPTransportType,
)
from backend_v2.tests.fakes.in_memory_uow import InMemoryUnitOfWork


class SystemConfigModelRegistryFactory(ModelFactory[SystemConfigModelRegistry]):
    """Polyfactory model factory for SystemConfigModelRegistry domain models."""

    __model__ = SystemConfigModelRegistry
    __set_as_default_factory_for_type__ = False

    name: str = "Vertex Enterprise Stack"
    default_provider: LLMProvider = LLMProvider.VERTEX_AI

    @classmethod
    def id(cls) -> str:
        """Generate a canonical mrg_<hex32> UUIDv7 Opaque Stripe ID.

        Returns:
            Canonical Opaque Stripe ID with 'mrg_' prefix.
        """
        return generate_opaque_id(EntityPrefix.MODEL_REGISTRY)

    @classmethod
    def slug(cls) -> str:
        """Generate a collision-free model registry slug.

        Returns:
            Unique registry slug string.
        """
        return f"registry_{generate_uuid7().hex[:8]}"

    @classmethod
    def tier_definitions(cls) -> dict[LaxCognitiveTier, ModelProfile]:
        """Generate complete profiles for all four canonical CognitiveTiers.

        Returns:
            Dictionary mapping every CognitiveTier to a valid ModelProfile.
        """
        return {
            CognitiveTier.FAST: ModelProfile(
                provider="vertex_ai",
                model_name="vertex_ai/gemini-2.5-flash",
                allowed_tools=[],
                additional_params=ProviderExtraParamsDTO(),
            ),
            CognitiveTier.BALANCED: ModelProfile(
                provider="vertex_ai",
                model_name="vertex_ai/gemini-2.5-pro",
                allowed_tools=[],
                additional_params=ProviderExtraParamsDTO(),
            ),
            CognitiveTier.DEEP: ModelProfile(
                provider="vertex_ai",
                model_name="vertex_ai/gemini-2.5-pro",
                allowed_tools=[],
                additional_params=ProviderExtraParamsDTO(),
            ),
            CognitiveTier.REASONING: ModelProfile(
                provider="openai",
                model_name="openai/o3-mini",
                allowed_tools=[],
                additional_params=ProviderExtraParamsDTO(),
            ),
        }


class SystemConfigMCPGatewaysFactory(ModelFactory[SystemConfigMCPGateways]):
    """Polyfactory model factory for SystemConfigMCPGateways domain models."""

    __model__ = SystemConfigMCPGateways
    __set_as_default_factory_for_type__ = False

    organization_id = Use(generate_opaque_id, EntityPrefix.ORGANIZATION)
    name: str = "Search MCP Gateway"
    endpoint_url: str = "https://mcp.example.org/search"
    transport_type: MCPTransportType = MCPTransportType.STREAMABLE_HTTP
    auth_type: MCPAuthType = MCPAuthType.NONE
    auth_header_name: str | None = None
    auth_env_var: str | None = None
    timeout_seconds: int = 30

    @classmethod
    def id(cls) -> str:
        """Generate a canonical mcp_<hex32> UUIDv7 Opaque Stripe ID.

        Returns:
            Canonical Opaque Stripe ID with 'mcp_' prefix.
        """
        return generate_opaque_id(EntityPrefix.MCP_GATEWAY)

    @classmethod
    def slug(cls) -> str:
        """Generate a collision-free MCP gateway slug.

        Returns:
            Valid MCP gateway slug matching schema regex.
        """
        return f"mcp_gw_{generate_uuid7().hex[:8]}"

    @classmethod
    def tools(cls) -> list[AllowedMCPTool]:
        """Generate an empty list of AllowedMCPTool entries.

        Returns:
            Empty list of AllowedMCPTool models.
        """
        return []


@pytest.fixture
def repo() -> SystemRepositoryImpl:
    """Create a SystemRepositoryImpl backed by an isolated InMemoryUnitOfWork store.

    Returns:
        Configured SystemRepositoryImpl instance.
    """
    base_uow = InMemoryUnitOfWork()
    return SystemRepositoryImpl(uow_factory=lambda: InMemoryUnitOfWork(base_uow.store))


@pytest.mark.asyncio
async def test_get_model_registry_by_id_roundtrip_success(repo: SystemRepositoryImpl) -> None:
    """Verify get_model_registry retrieves the exact persisted SystemConfigModelRegistry by ID."""
    registry = SystemConfigModelRegistryFactory.build(name="Google AI Studio Stack")
    await repo.update_model_registry(registry)

    fetched = await repo.get_model_registry(registry.id)
    assert fetched == registry
    assert fetched.tier_definitions[CognitiveTier.FAST].model_name == "vertex_ai/gemini-2.5-flash"


@pytest.mark.asyncio
async def test_get_all_model_registries_deterministic_ordering(repo: SystemRepositoryImpl) -> None:
    """Verify get_all_model_registries excludes MCP gateways and sorts deterministically by (name, id)."""
    reg_openai = SystemConfigModelRegistryFactory.build(
        name="OpenAI O-Series Stack",
        default_provider=LLMProvider.OPENAI,
    )
    reg_google = SystemConfigModelRegistryFactory.build(
        name="Google AI Studio Stack",
        default_provider=LLMProvider.AI_STUDIO,
    )
    gateway = SystemConfigMCPGatewaysFactory.build()

    await repo.update_model_registry(reg_openai)
    await repo.update_mcp_gateways(gateway)
    await repo.update_model_registry(reg_google)

    registries = await repo.get_all_model_registries()
    assert [item.name for item in registries] == [
        "Google AI Studio Stack",
        "OpenAI O-Series Stack",
    ]
    assert [item.id for item in registries] == [reg_google.id, reg_openai.id]


@pytest.mark.asyncio
async def test_update_model_registry_in_place_by_id(repo: SystemRepositoryImpl) -> None:
    """Verify update_model_registry mutates an existing registry in-place under its authoritative ID."""
    initial = SystemConfigModelRegistryFactory.build(name="Initial Stack Name")
    await repo.update_model_registry(initial)

    mutated = initial.model_copy(update={"name": "Updated Stack Name"})
    assert await repo.update_model_registry(mutated) is True

    reloaded = await repo.get_model_registry(initial.id)
    assert reloaded.id == initial.id
    assert reloaded.name == "Updated Stack Name"
    assert len(await repo.get_all_model_registries()) == 1


@pytest.mark.asyncio
async def test_delete_model_registry_removes_model_registry(repo: SystemRepositoryImpl) -> None:
    """Verify delete_model_registry deletes a persisted model registry and subsequent lookup fails."""
    registry = SystemConfigModelRegistryFactory.build()
    await repo.update_model_registry(registry)

    assert await repo.delete_model_registry(registry.id) is True
    assert await repo.delete_model_registry(registry.id) is False

    with pytest.raises(ResourceNotFoundError):
        await repo.get_model_registry(registry.id)


@pytest.mark.asyncio
async def test_get_model_registry_by_id_not_found_error(repo: SystemRepositoryImpl) -> None:
    """Verify get_model_registry raises ResourceNotFoundError for a non-existent mrg_<hex32> ID."""
    missing_id = generate_opaque_id(EntityPrefix.MODEL_REGISTRY)

    with pytest.raises(ResourceNotFoundError) as exc_info:
        await repo.get_model_registry(missing_id)

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_get_model_registry_by_id_wrong_type_error(repo: SystemRepositoryImpl) -> None:
    """Verify get_model_registry raises AppException VALIDATION_FAILED when ID carries mcp_ prefix."""
    gateway = SystemConfigMCPGatewaysFactory.build()
    await repo.update_mcp_gateways(gateway)

    with pytest.raises(AppException) as exc_info:
        await repo.get_model_registry(gateway.id)

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_get_model_registry_empty_id_not_found_error(repo: SystemRepositoryImpl) -> None:
    """Verify get_model_registry raises ResourceNotFoundError immediately when registry_id is empty."""
    with pytest.raises(ResourceNotFoundError) as exc_info:
        await repo.get_model_registry("")

    assert exc_info.value.status_code == 404
