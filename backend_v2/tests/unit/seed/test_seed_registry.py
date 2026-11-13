"""Unit tests for the seed registry."""

import pytest
from pydantic import TypeAdapter, ValidationError

from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.system_config import (
    AllowedMCPTool,
    ModelProfile,
    ProviderExtraParamsDTO,
    SystemConfigMCPGateways,
    SystemConfigModelRegistry,
)
from backend_v2.models.dtos.mcp import MCPToolInputSchemaDTO
from backend_v2.models.enums import CognitiveTier, LLMProvider
from backend_v2.seed.seed_registry import STANDARD_REGISTRY, SeedCollectionName
from backend_v2.tests.factories.model_factories import TaskBriefFactory


def test_mcp_gateways_registry_entry_validates_gateway() -> None:
    """Verify mcp_gateways registry entry resolves SystemConfigMCPGateways with organization_id."""
    assert SeedCollectionName.MCP_GATEWAYS.value == "mcp_gateways"
    adapter = STANDARD_REGISTRY["mcp_gateways"]["model"]
    assert isinstance(adapter, TypeAdapter)
    tool = AllowedMCPTool(
        tool_id="mcp_tavily_search",
        name=I18nText(translations={"en": "Tavily Search", "fi": "Tavily Haku"}),
        description="Search tool",
        input_schema=MCPToolInputSchemaDTO(properties={}, required=[]),
    )
    data = {
        "id": "mcp_0195f3a0000070008123456789abcdef",
        "organization_id": "org_0195f3a0000070008000000000000001",
        "name": "Tavily MCP Gateway",
        "slug": "default_mcp_gateway",
        "tools": [tool.model_dump(mode="json")],
    }
    result = adapter.validate_python(data)
    assert isinstance(result, SystemConfigMCPGateways)
    assert result.organization_id == "org_0195f3a0000070008000000000000001"
    assert len(result.tools) == 1


def test_model_registries_registry_entry_validates_registry() -> None:
    """Verify model_registries registry entry resolves SystemConfigModelRegistry without type discriminator."""
    assert SeedCollectionName.MODEL_REGISTRIES.value == "model_registries"
    adapter = STANDARD_REGISTRY["model_registries"]["model"]
    assert isinstance(adapter, TypeAdapter)
    profile = ModelProfile(
        model_name="gpt-4o",
        provider=LLMProvider.OPENAI,
        allowed_tools=[],
        additional_params=ProviderExtraParamsDTO(),
    )
    data = {
        "id": "mrg_0195f3a0000070008123456789abcdef",
        "name": "OpenAI Stack",
        "tier_definitions": {tier.value: profile.model_dump(mode="json") for tier in CognitiveTier},
    }
    result = adapter.validate_python(data)
    assert isinstance(result, SystemConfigModelRegistry)
    assert CognitiveTier.FAST in result.tier_definitions


def test_mcp_gateways_missing_organization_id_fails() -> None:
    """Negative test: missing organization_id or retired type field triggers ValidationError."""
    adapter = STANDARD_REGISTRY["mcp_gateways"]["model"]
    assert isinstance(adapter, TypeAdapter)
    with pytest.raises(ValidationError):
        adapter.validate_python({"id": "mcp_0195f3a0000070008123456789abcdef", "name": "Missing Org"})
    with pytest.raises(ValidationError):
        adapter.validate_python(
            {
                "id": "mcp_0195f3a0000070008123456789abcdef",
                "organization_id": "org_0195f3a0000070008000000000000001",
                "name": "Extra Type",
                "type": "mcp_gateways",
            }
        )


def test_model_registries_wrong_prefix_or_extra_type_fails() -> None:
    """Negative test: wrong entity prefix or retired type field on model_registries fails validation."""
    adapter = STANDARD_REGISTRY["model_registries"]["model"]
    assert isinstance(adapter, TypeAdapter)
    with pytest.raises(ValidationError):
        adapter.validate_python({"id": "mcp_0195f3a0000070008123456789abcdef", "name": "Wrong Prefix"})
    with pytest.raises(ValidationError):
        adapter.validate_python(
            {
                "id": "mrg_0195f3a0000070008123456789abcdef",
                "name": "Retired Type",
                "type": "model_registry",
            }
        )


def test_task_brief_registry_entry_and_validation_error() -> None:
    """Verify SeedCollectionName.TASK_BRIEFS is registered and validates TaskBrief models."""
    assert SeedCollectionName.TASK_BRIEFS.value == "task_briefs"
    assert "task_briefs" in STANDARD_REGISTRY
    adapter = STANDARD_REGISTRY["task_briefs"]["model"]
    assert isinstance(adapter, TypeAdapter)
    sample = TaskBriefFactory.build().model_dump(mode="json")
    validated = adapter.validate_python(sample)
    assert validated.id == sample["id"]

    with pytest.raises(ValidationError):
        adapter.validate_python({"id": "invalid_prefix_id"})
