"""Tests for system_config domain models and DTOs."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.system_config import (
    AllowedMCPTool,
    ChatHistoryDTO,
    ChatMessageDTO,
    DataDictionaryField,
    MCPAuditTrace,
    ModelProfile,
    ProviderExtraParamsDTO,
    SystemConfigMCPGateways,
    SystemConfigModelRegistry,
    SystemConfigOptionDTO,
    SystemValidationRulesDTO,
)
from backend_v2.models.dtos.mcp import MCPToolInputSchemaDTO, MCPToolSchemaPropertyDTO
from backend_v2.models.enums import (
    CognitiveTier,
    ComponentType,
    JSONSchemaPropertyType,
    LaxCognitiveTier,
    LLMProvider,
    MCPAuthType,
    MCPTransportType,
    ToolCapability,
)


def test_chat_message_and_history_dto_valid_and_negative() -> None:
    """Verify ChatMessageDTO and ChatHistoryDTO valid instantiation and negative validation."""
    msg = ChatMessageDTO(role="user", content="Analyze strategic alignment.")
    history = ChatHistoryDTO(conversation=[msg])
    assert len(history.conversation) == 1
    assert history.conversation[0].role == "user"
    assert history.conversation[0].content == "Analyze strategic alignment."

    invalid_msg: dict[str, str] = {"role": "user", "content": "ok", "extra": "forbidden"}
    with pytest.raises(ValidationError):
        ChatMessageDTO.model_validate(invalid_msg)

    invalid_history: dict[str, str] = {"conversation": "not_a_list"}
    with pytest.raises(ValidationError):
        ChatHistoryDTO.model_validate(invalid_history)


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


def test_data_dictionary_field_and_provider_extra_params_valid_and_negative() -> None:
    """Verify DataDictionaryField and ProviderExtraParamsDTO valid and negative cases."""
    field_def = DataDictionaryField(
        field_id="temperature_override",
        component_type=ComponentType.SLIDER,
        options=[SystemConfigOptionDTO(value="0.2", label="Low")],
        validation_rules=SystemValidationRulesDTO(min=0.0, max=1.0, required=False),
    )
    assert field_def.field_id == "temperature_override"
    assert field_def.component_type == ComponentType.SLIDER
    assert field_def.options is not None and len(field_def.options) == 1

    invalid_field: dict[str, str] = {
        "field_id": "bad_field",
        "component_type": "non_existent_widget",
    }
    with pytest.raises(ValidationError):
        DataDictionaryField.model_validate(invalid_field)

    params = ProviderExtraParamsDTO(
        temperature=0.1,
        top_p=0.95,
        top_k=20,
        max_output_tokens=4096,
        reasoning_effort="high",
        vertex_location="europe-west1",
    )
    assert params.temperature == 0.1
    assert params.vertex_location == "europe-west1"

    invalid_params: dict[str, str] = {"unknown_param": "invalid"}
    with pytest.raises(ValidationError):
        ProviderExtraParamsDTO.model_validate(invalid_params)


def test_model_profile_valid_and_negative() -> None:
    """Verify ModelProfile default initialization and extra='forbid' enforcement."""
    profile = ModelProfile(provider="google", model_name="gemini-2.5-pro")
    assert profile.provider == "google"
    assert profile.model_name == "gemini-2.5-pro"
    assert profile.allowed_tools == []
    assert profile.supports_grounding is False
    assert profile.is_active is True

    invalid_profile: dict[str, str] = {
        "provider": "google",
        "model_name": "gemini-2.5-pro",
        "unexpected": "value",
    }
    with pytest.raises(ValidationError):
        ModelProfile.model_validate(invalid_profile)


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

    with pytest.raises(ValidationError):
        MCPAuditTrace(
            tool_id="mcp_tavily_search",
            step_name="stp_1234567890abcdef",
            gateway_id="invalid_gateway_id",
            query="test query",
        )


def test_system_config_mcp_gateways_slug_and_timeout_validation() -> None:
    """Verify SystemConfigMCPGateways validates single-underscore slug and timeout bounds."""
    gw_min = SystemConfigMCPGateways(
        id="sys_8172bda70c8641c5",
        slug="tavily_mcp_gateway",
        endpoint_url="https://mcp.tavily.com/mcp",
        transport_type=MCPTransportType.STREAMABLE_HTTP,
        auth_type=MCPAuthType.BEARER,
        auth_env_var="TAVILY_API_KEY",
        timeout_seconds=1,
        tools=[],
    )
    assert gw_min.slug == "tavily_mcp_gateway"
    assert gw_min.transport_type == MCPTransportType.STREAMABLE_HTTP
    assert gw_min.auth_type == MCPAuthType.BEARER
    assert gw_min.timeout_seconds == 1

    gw_max = SystemConfigMCPGateways(
        id="sys_8172bda70c8641c5",
        slug="valid_slug",
        timeout_seconds=300,
        tools=[],
    )
    assert gw_max.timeout_seconds == 300

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

    with pytest.raises(ValidationError):
        SystemConfigMCPGateways(
            id="sys_8172bda70c8641c5",
            slug="valid_slug",
            timeout_seconds=301,
            tools=[],
        )


def test_system_config_model_registry_valid_all_tiers() -> None:
    """Verify SystemConfigModelRegistry succeeds when all four canonical CognitiveTiers are defined."""
    complete_tiers: dict[LaxCognitiveTier, ModelProfile] = {
        CognitiveTier.FAST: ModelProfile(provider="google", model_name="gemini-2.5-flash"),
        CognitiveTier.BALANCED: ModelProfile(provider="google", model_name="gemini-2.5-pro"),
        CognitiveTier.DEEP: ModelProfile(provider="google", model_name="gemini-2.5-pro"),
        CognitiveTier.REASONING: ModelProfile(provider="google", model_name="gemini-2.5-pro"),
    }
    registry = SystemConfigModelRegistry(
        id="sys_1234567890abcdef",
        name="Complete Registry",
        default_provider=LLMProvider.AI_STUDIO,
        tier_definitions=complete_tiers,
    )
    assert registry.id == "sys_1234567890abcdef"
    assert len(registry.tier_definitions) == 4


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

    with pytest.raises(ValidationError):
        SystemConfigModelRegistry(
            id="invalid_id",
            name="Bad ID Registry",
            tier_definitions=incomplete_tiers,
        )
