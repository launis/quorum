"""Tests for system_config domain models and DTOs."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.system_config import (
    AllowedMCPTool,
    MCPAuditTrace,
    ModelProfile,
    SystemConfigMCPGateways,
    SystemConfigModelRegistry,
    SystemConfigOptionDTO,
    SystemValidationRulesDTO,
)
from backend_v2.models.dtos.mcp import MCPToolInputSchemaDTO, MCPToolSchemaPropertyDTO
from backend_v2.models.enums import (
    CognitiveTier,
    JSONSchemaPropertyType,
    LaxCognitiveTier,
    MCPAuthType,
    MCPTransportType,
    ToolCapability,
)


def test_system_validation_rules_dto_rejects_unknown_attribute() -> None:
    """Verify extra attributes are rejected by SystemValidationRulesDTO."""
    invalid_rules: dict[str, str] = {"unknown_rule": "bad"}
    with pytest.raises(ValidationError):
        SystemValidationRulesDTO.model_validate(invalid_rules)


def test_system_validation_rules_dto_valid() -> None:
    """Verify valid SystemValidationRulesDTO instantiation."""
    rules = SystemValidationRulesDTO(min=1.0, max=10.0, required=True, pattern=r"^\d+$")
    assert rules.min == 1.0
    assert rules.max == 10.0
    assert rules.required is True
    assert rules.pattern == r"^\d+$"


def test_system_config_option_dto_valid() -> None:
    """Verify valid SystemConfigOptionDTO instantiation."""
    opt = SystemConfigOptionDTO(label="Opt1", value="val1")
    assert opt.label == "Opt1"
    assert opt.value == "val1"


def test_system_config_option_dto_rejects_unknown_attribute() -> None:
    """Verify extra attributes are rejected by SystemConfigOptionDTO."""
    invalid_opt: dict[str, str] = {"label": "Opt1", "value": "val1", "extra": "bad"}
    with pytest.raises(ValidationError):
        SystemConfigOptionDTO.model_validate(invalid_opt)


def test_allowed_mcp_tool_valid_and_defaults() -> None:
    """Verify AllowedMCPTool defaults capability to SEARCH and accepts typed MCPToolInputSchemaDTO."""
    tool_default = AllowedMCPTool(
        tool_id="mcp_test_search",
        name=I18nText(translations={"fi": "Haku", "en": "Search"}),
        description="Search tool description.",
    )
    assert tool_default.capability == ToolCapability.SEARCH
    assert tool_default.tool_id == "mcp_test_search"
    assert tool_default.enabled is True
    assert tool_default.input_schema.type == "object"

    schema = MCPToolInputSchemaDTO(
        properties={
            "title": MCPToolSchemaPropertyDTO(
                type=JSONSchemaPropertyType.STRING,
                description="Article title",
            )
        },
        required=["title"],
    )
    tool_reader = AllowedMCPTool(
        tool_id="mcp_test_reader",
        capability=ToolCapability.DOCUMENT_READER,
        name=I18nText(translations={"fi": "Lukija", "en": "Reader"}),
        description="Reader tool description.",
        input_schema=schema,
        enabled=False,
    )
    assert tool_reader.capability == ToolCapability.DOCUMENT_READER
    assert tool_reader.enabled is False
    assert tool_reader.input_schema.required == ["title"]


def test_allowed_mcp_tool_rejects_empty_tool_id_error() -> None:
    """Verify AllowedMCPTool enforces min_length=1 on tool_id."""
    with pytest.raises(ValidationError):
        AllowedMCPTool(
            tool_id="",
            name=I18nText(translations={"en": "Empty"}),
            description="Invalid empty tool_id",
        )


def test_allowed_mcp_tool_rejects_unknown_attribute() -> None:
    """Verify AllowedMCPTool enforces extra='forbid'."""
    invalid_tool = {
        "tool_id": "mcp_test",
        "name": {"translations": {"fi": "Testi", "en": "Test"}},
        "description": "Test tool",
        "extra_key": "forbidden",
    }
    with pytest.raises(ValidationError):
        AllowedMCPTool.model_validate(invalid_tool)


def test_mcp_audit_trace_provenance_fields() -> None:
    """Verify MCPAuditTrace accepts optional gateway provenance fields and enforces frozen=True."""
    trace = MCPAuditTrace(
        tool_id="mcp_tavily_search",
        step_name="stp_1234567890abcdef",
        gateway_id="sys_8172bda70c8641c5",
        gateway_slug="default_mcp_gateway",
        namespaced_alias="default_mcp_gateway__mcp_tavily_search",
        query="test query",
        duration_ms=120,
    )
    assert trace.gateway_id == "sys_8172bda70c8641c5"
    assert trace.gateway_slug == "default_mcp_gateway"
    assert trace.namespaced_alias == "default_mcp_gateway__mcp_tavily_search"
    assert trace.source_urls == []
    assert trace.impacted_axis_names == []
    with pytest.raises(ValidationError):
        trace.duration_ms = 200


def test_system_config_mcp_gateways_slug_and_timeout_validation() -> None:
    """Verify SystemConfigMCPGateways validates single-underscore slug and timeout bounds."""
    gw = SystemConfigMCPGateways(
        id="sys_8172bda70c8641c5",
        slug="tavily_mcp_gateway",
        endpoint_url="https://mcp.tavily.com/mcp",
        transport_type=MCPTransportType.STREAMABLE_HTTP,
        auth_type=MCPAuthType.BEARER,
        auth_env_var="TAVILY_API_KEY",
        timeout_seconds=45,
        tools=[],
    )
    assert gw.slug == "tavily_mcp_gateway"
    assert gw.transport_type == MCPTransportType.STREAMABLE_HTTP
    assert gw.auth_type == MCPAuthType.BEARER
    assert gw.timeout_seconds == 45

    with pytest.raises(ValidationError):
        SystemConfigMCPGateways(
            id="sys_8172bda70c8641c5",
            slug="bad__double_underscore",
            tools=[],
        )

    with pytest.raises(ValidationError):
        SystemConfigMCPGateways(
            id="sys_8172bda70c8641c5",
            slug="valid_slug",
            timeout_seconds=0,
            tools=[],
        )


def test_system_config_model_registry_missing_tier_raises_value_error() -> None:
    """Verify SystemConfigModelRegistry raises ValueError when cognitive tiers are incomplete."""
    incomplete_tiers: dict[LaxCognitiveTier, ModelProfile] = {
        CognitiveTier.FAST: ModelProfile(provider="google", model_name="gemini-2.5-flash"),
    }
    with pytest.raises(ValidationError) as exc_info:
        SystemConfigModelRegistry(
            id="sys_1234567890abcdef",
            name="Incomplete Registry",
            tier_definitions=incomplete_tiers,
        )
    assert "missing required cognitive tiers" in str(exc_info.value)
