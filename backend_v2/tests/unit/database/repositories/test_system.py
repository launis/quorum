"""Unit and boundary tests for SystemRepositoryImpl over InMemoryUnitOfWork.

Covers stateful persistence and deterministic ordering for SystemConfigModelRegistry
and SystemConfigMCPGateways, polymorphic SystemConfigCreateDTO creation, deletion,
and negative ResourceNotFoundError and identifier validation boundaries.
"""

from __future__ import annotations

import pytest
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
from backend_v2.models.dtos.system import AnySystemConfigAdapter, SystemConfigCreateDTO
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

    name: str = "Standard Model Registry"
    default_provider: LLMProvider = LLMProvider.AI_STUDIO

    @classmethod
    def id(cls) -> str:
        """Generate a canonical sys_<hex32> UUIDv7 Opaque Stripe ID.

        Returns:
            Canonical Opaque Stripe ID with 'sys_' prefix.
        """
        return generate_opaque_id(EntityPrefix.SYSTEM_CONFIG)

    @classmethod
    def slug(cls) -> str:
        """Generate a deterministic collision-free model registry slug.

        Returns:
            Unique registry slug string.
        """
        return f"model_registry_{generate_uuid7().hex[:8]}"

    @classmethod
    def tier_definitions(cls) -> dict[LaxCognitiveTier, ModelProfile]:
        """Generate complete profiles for all four canonical CognitiveTiers.

        Returns:
            Dictionary mapping every CognitiveTier to a valid ModelProfile.
        """
        return {
            CognitiveTier.FAST: ModelProfile(
                provider="ai_studio",
                model_name="gemini/gemini-2.5-flash",
                allowed_tools=[],
                additional_params=ProviderExtraParamsDTO(),
            ),
            CognitiveTier.BALANCED: ModelProfile(
                provider="ai_studio",
                model_name="gemini/gemini-2.5-pro",
                allowed_tools=[],
                additional_params=ProviderExtraParamsDTO(),
            ),
            CognitiveTier.DEEP: ModelProfile(
                provider="openai",
                model_name="openai/gpt-4o",
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

    name: str = "Primary MCP Gateway"
    endpoint_url: str = "https://mcp.example.org/v1"
    transport_type: MCPTransportType = MCPTransportType.STREAMABLE_HTTP
    auth_type: MCPAuthType = MCPAuthType.NONE
    auth_header_name: str | None = None
    auth_env_var: str | None = None
    timeout_seconds: int = 30

    @classmethod
    def id(cls) -> str:
        """Generate a canonical sys_<hex32> UUIDv7 Opaque Stripe ID.

        Returns:
            Canonical Opaque Stripe ID with 'sys_' prefix.
        """
        return generate_opaque_id(EntityPrefix.SYSTEM_CONFIG)

    @classmethod
    def slug(cls) -> str:
        """Generate a collision-free MCP gateway slug without double underscores.

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
def base_uow() -> InMemoryUnitOfWork:
    """Create an isolated InMemoryUnitOfWork backing store for each test.

    Returns:
        Fresh InMemoryUnitOfWork instance.
    """
    return InMemoryUnitOfWork()


@pytest.fixture
def repo(base_uow: InMemoryUnitOfWork) -> SystemRepositoryImpl:
    """Create a SystemRepositoryImpl bound to a shared InMemoryUnitOfWork store.

    Args:
        base_uow: Shared in-memory Unit of Work fixture.

    Returns:
        Configured SystemRepositoryImpl instance.
    """
    return SystemRepositoryImpl(uow_factory=lambda: InMemoryUnitOfWork(base_uow.store))


@pytest.mark.asyncio
async def test_model_registry_crud_and_ordering_roundtrip(repo: SystemRepositoryImpl) -> None:
    """Verify update_model_registry, get_model_registry, and get_all_model_registries roundtrip statefully."""
    reg_zeta = SystemConfigModelRegistryFactory.build(name="Zeta Registry Stack")
    reg_alpha = SystemConfigModelRegistryFactory.build(name="Alpha Registry Stack")

    assert await repo.update_model_registry(reg_zeta) is True
    assert await repo.update_model_registry(reg_alpha) is True

    fetched_alpha = await repo.get_model_registry(reg_alpha.id)
    assert fetched_alpha == reg_alpha
    assert AnySystemConfigAdapter.validate_python(fetched_alpha.model_dump(mode="json")) == reg_alpha

    all_registries = await repo.get_all_model_registries()
    assert [item.id for item in all_registries] == [reg_alpha.id, reg_zeta.id]


@pytest.mark.asyncio
async def test_mcp_gateways_crud_default_lookup_and_ordering_roundtrip(
    repo: SystemRepositoryImpl,
) -> None:
    """Verify update_mcp_gateways, get_mcp_gateways (explicit and default), and get_all_mcp_gateways."""
    gw_beta = SystemConfigMCPGatewaysFactory.build(slug="beta_gateway", name="Beta Gateway")
    gw_alpha = SystemConfigMCPGatewaysFactory.build(slug="alpha_gateway", name="Alpha Gateway")

    assert await repo.update_mcp_gateways(gw_beta) is True
    assert await repo.update_mcp_gateways(gw_alpha) is True

    fetched_explicit = await repo.get_mcp_gateways(id=gw_beta.id)
    assert fetched_explicit == gw_beta

    fetched_default = await repo.get_mcp_gateways()
    assert fetched_default == gw_alpha

    updated_beta = gw_beta.model_copy(update={"timeout_seconds": 90})
    assert await repo.update_mcp_gateways(updated_beta) is True
    assert (await repo.get_mcp_gateways(id=gw_beta.id)).timeout_seconds == 90

    all_gateways = await repo.get_all_mcp_gateways()
    assert [item.id for item in all_gateways] == [gw_alpha.id, gw_beta.id]


@pytest.mark.asyncio
async def test_create_get_and_delete_system_config_polymorphic_roundtrip(
    repo: SystemRepositoryImpl,
) -> None:
    """Verify create_system_config applies slug override for MCP gateways and delete_system_config removes records."""
    reg = SystemConfigModelRegistryFactory.build()
    created_reg_id = await repo.create_system_config(
        SystemConfigCreateDTO(type="model_registry", content=reg, slug=reg.slug)
    )
    assert created_reg_id == reg.id
    assert await repo.get_system_config(reg.id) == reg

    gw = SystemConfigMCPGatewaysFactory.build(slug="initial_gateway_slug")
    created_gw_id = await repo.create_system_config(
        SystemConfigCreateDTO(type="mcp_gateways", content=gw, slug="overridden_gateway_slug")
    )
    assert created_gw_id == gw.id
    fetched_gw = await repo.get_system_config(gw.id)
    assert isinstance(fetched_gw, SystemConfigMCPGateways)
    assert fetched_gw.slug == "overridden_gateway_slug"

    assert await repo.delete_system_config(gw.id) is True
    assert await repo.get_system_config(gw.id) is None
    assert await repo.delete_system_config(gw.id) is False


@pytest.mark.asyncio
async def test_get_model_registry_not_found_and_empty_id_error(repo: SystemRepositoryImpl) -> None:
    """Verify get_model_registry raises ResourceNotFoundError for missing or empty registry_id."""
    missing_id = generate_opaque_id(EntityPrefix.SYSTEM_CONFIG)

    with pytest.raises(ResourceNotFoundError) as missing_exc:
        await repo.get_model_registry(missing_id)
    assert missing_exc.value.status_code == 404

    with pytest.raises(ResourceNotFoundError) as empty_exc:
        await repo.get_model_registry("")
    assert empty_exc.value.status_code == 404


@pytest.mark.asyncio
async def test_get_mcp_gateways_not_found_and_cross_type_mismatch_error(
    repo: SystemRepositoryImpl,
) -> None:
    """Verify get_mcp_gateways and get_model_registry reject missing or mismatched SystemConfig types."""
    with pytest.raises(ResourceNotFoundError):
        await repo.get_mcp_gateways()

    missing_id = generate_opaque_id(EntityPrefix.SYSTEM_CONFIG)
    with pytest.raises(ResourceNotFoundError):
        await repo.get_mcp_gateways(id=missing_id)

    reg = SystemConfigModelRegistryFactory.build()
    gw = SystemConfigMCPGatewaysFactory.build()
    await repo.update_model_registry(reg)
    await repo.update_mcp_gateways(gw)

    with pytest.raises(ResourceNotFoundError):
        await repo.get_mcp_gateways(id=reg.id)

    with pytest.raises(ResourceNotFoundError):
        await repo.get_model_registry(gw.id)


@pytest.mark.asyncio
async def test_get_system_config_invalid_prefix_failure(repo: SystemRepositoryImpl) -> None:
    """Verify get_system_config raises AppException VALIDATION_FAILED when given a non-sys prefix."""
    invalid_id = generate_opaque_id(EntityPrefix.WORKFLOW)

    with pytest.raises(AppException) as exc_info:
        await repo.get_system_config(invalid_id)

    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
