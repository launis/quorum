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
from backend_v2.models.domain.task_brief import TaskBrief
from backend_v2.models.dtos.mcp import MCPToolInputSchemaDTO
from backend_v2.models.enums import CognitiveTier, LLMProvider
from backend_v2.seed.seed_registry import STANDARD_REGISTRY, SeedCollectionName
from backend_v2.tests.factories.model_factories import TaskBriefFactory


def test_system_config_discriminator_mcp_gateways() -> None:
    """Tests the discriminator correctly resolves SystemConfigMCPGateways."""
    adapter = STANDARD_REGISTRY["system_config"]["model"]
    assert isinstance(adapter, TypeAdapter)
    tool = AllowedMCPTool(
        tool_id="mcp_tavily_search",
        name=I18nText(translations={"en": "Tavily Search", "fi": "Tavily Haku"}),
        description="Search tool",
        input_schema=MCPToolInputSchemaDTO(properties={}, required=[]),
    )
    data = {
        "id": "cfg_0195f3a0000070008123456789abcdef",
        "name": "Tavily MCP Gateway",
        "slug": "default_mcp_gateway",
        "type": "mcp_gateways",
        "tools": [tool.model_dump(mode="json")],
    }
    result = adapter.validate_python(data)
    assert isinstance(result, SystemConfigMCPGateways)
    assert result.type == "mcp_gateways"
    assert len(result.tools) == 1


def test_system_config_discriminator_model_registry() -> None:
    """Tests the discriminator correctly resolves SystemConfigModelRegistry."""
    adapter = STANDARD_REGISTRY["system_config"]["model"]
    assert isinstance(adapter, TypeAdapter)
    profile = ModelProfile(
        model_name="gpt-4o",
        provider=LLMProvider.OPENAI,
        allowed_tools=[],
        additional_params=ProviderExtraParamsDTO(),
    )
    data = {
        "id": "cfg_0195f3a0000070008123456789abcdef",
        "name": "Tavily MCP Gateway",
        "type": "model_registry",
        "tier_definitions": {tier.value: profile.model_dump(mode="json") for tier in CognitiveTier},
    }
    result = adapter.validate_python(data)
    assert isinstance(result, SystemConfigModelRegistry)
    assert result.type == "model_registry"
    assert CognitiveTier.FAST in result.tier_definitions


def test_system_config_discriminator_missing_type_fails() -> None:
    """Tests that missing type discriminator tag triggers ValidationError."""
    adapter = STANDARD_REGISTRY["system_config"]["model"]
    assert isinstance(adapter, TypeAdapter)
    data = {"id": "cfg_0195f3a0000070008123456789abcdef", "other": "value"}
    with pytest.raises(ValidationError):
        adapter.validate_python(data)


def test_system_config_discriminator_unknown_type_fails() -> None:
    """Tests that unknown type discriminator tag triggers ValidationError."""
    adapter = STANDARD_REGISTRY["system_config"]["model"]
    assert isinstance(adapter, TypeAdapter)
    data = {"id": "cfg_0195f3a0000070008123456789abcdef", "type": "unknown_config_type"}
    with pytest.raises(ValidationError):
        adapter.validate_python(data)


def test_task_brief_registry_entry_and_validation_error() -> None:
    """Verify SeedCollectionName.TASK_BRIEFS is registered and validates TaskBrief models."""
    assert SeedCollectionName.TASK_BRIEFS.value == "task_briefs"
    assert "task_briefs" in STANDARD_REGISTRY
    adapter = STANDARD_REGISTRY["task_briefs"]["model"]
    assert isinstance(adapter, TypeAdapter)
    sample = TaskBriefFactory.build().model_dump(mode="json")
    hydrated = adapter.validate_python(sample)
    assert isinstance(hydrated, TaskBrief)

    with pytest.raises(ValidationError):
        adapter.validate_python({"id": "blk_0195f3a0000070008123456789abcdef"})
