"""Domain models for system configuration and platform settings.

SSOT for ChatMessageDTO, ChatHistoryDTO, DataDictionaryField, ProviderExtraParamsDTO,
ModelProfile, SystemConfigModelRegistry, AllowedMCPTool, MCPAuditTrace, and
SystemConfigMCPGateways.
"""

from datetime import datetime, timezone
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend_v2.models.core_base import OPAQUE_STRIPE_ID_REGEX, I18nText, V2CoreBase
from backend_v2.models.dtos.mcp import MCPToolInputSchemaDTO
from backend_v2.models.enums import (
    CognitiveTier,
    LaxCognitiveTier,
    LaxComponentType,
    LaxLLMProvider,
    LaxMCPAuthType,
    LaxMCPTransportType,
    LaxToolCapability,
    LLMProvider,
    MCPAuthType,
    MCPTransportType,
    ToolCapability,
)

__all__ = [
    "AllowedMCPTool",
    "ChatHistoryDTO",
    "ChatMessageDTO",
    "DataDictionaryField",
    "MCPAuditTrace",
    "ModelProfile",
    "ProviderExtraParamsDTO",
    "SystemConfigMCPGateways",
    "SystemConfigModelRegistry",
    "SystemConfigOptionDTO",
    "SystemValidationRulesDTO",
]


class ChatMessageDTO(V2CoreBase):
    """Schema for a single parsed chat message.

    Attributes:
        role: The role of the speaker (e.g. 'user' or 'ai').
        content: The message text.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    role: Annotated[str, Field(description="The role of the speaker (e.g. 'user' or 'ai').")]
    content: Annotated[str, Field(description="The message text.")]


class ChatHistoryDTO(V2CoreBase):
    """Strict schema for a complete parsed chat sequence.

    Attributes:
        conversation: List of messages in chronological order.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    conversation: Annotated[list[ChatMessageDTO], Field(description="List of messages in chronological order.")]


class SystemConfigOptionDTO(V2CoreBase):
    """Selectable option for dropdown/multiselect UI components."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    value: str
    label: str | I18nText | None = None


class SystemValidationRulesDTO(V2CoreBase):
    """Validation rules for SDUI dynamic data dictionary fields."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    min: float | int | None = None
    max: float | int | None = None
    required: bool | None = None
    pattern: str | None = None


class DataDictionaryField(V2CoreBase):
    """UI Hints mapping for dynamic form generation (SDUI)."""

    model_config = ConfigDict(strict=True, extra="forbid")

    field_id: str
    component_type: Annotated[LaxComponentType, Field(description="E.g., 'slider', 'text_input', 'dropdown'")]
    options: list[SystemConfigOptionDTO] | None = None
    validation_rules: SystemValidationRulesDTO | None = None


class ProviderExtraParamsDTO(BaseModel):
    """Provider-specific optional parameters for ModelProfile."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    temperature: float | None = None
    top_p: float | None = None
    top_k: int | None = None
    max_output_tokens: int | None = None
    reasoning_effort: str | None = None
    vertex_location: str | None = None


class ModelProfile(V2CoreBase):
    """A flattened physical AI model representation."""

    model_config = ConfigDict(strict=True, extra="forbid")

    provider: Annotated[str, Field(description="E.g., 'google', 'openai'")]
    model_name: Annotated[str, Field(description="The underlying API model name")]
    temperature: Annotated[float | None, Field(default=None, description="Generation temperature")] = None
    top_p: Annotated[float | None, Field(default=None, description="Nucleus sampling probability")] = None
    top_k: Annotated[int | None, Field(default=None, description="Top-K sampling")] = None
    tpm_limit: Annotated[int | None, Field(default=None, description="Tokens per minute limit")] = None
    rpm_limit: Annotated[int | None, Field(default=None, description="Requests per minute limit")] = None
    max_tokens: Annotated[int | None, Field(default=None, description="Max generated tokens")] = None
    frequency_penalty: Annotated[float | None, Field(default=None, description="Frequency penalty")] = None
    presence_penalty: Annotated[float | None, Field(default=None, description="Presence penalty")] = None
    allowed_tools: list[str] = Field(default_factory=list, description="Enabled tools")
    supports_grounding: Annotated[bool, Field(default=False, description="Supports Google Search Grounding")] = False
    api_key: Annotated[str | None, Field(default=None, description="Optional override API key")] = None
    parsing_mode: Annotated[
        str | None, Field(default=None, description="Parser logic flag (e.g. 'STRUCTURED_JSON')")
    ] = None
    caching_strategy: Annotated[
        str | None,
        Field(default=None, description="Cache strategy identifier (e.g. 'anthropic_ephemeral')"),
    ] = None
    thinking_budget_tokens: Annotated[
        int | None,
        Field(
            default=None,
            description="Reasoning/thinking token budget for reasoning models (e.g. Gemini 3.7, Claude 3.7)",
        ),
    ] = None
    additional_params: ProviderExtraParamsDTO = Field(
        default_factory=ProviderExtraParamsDTO, description="Additional provider-specific parameters."
    )
    is_active: Annotated[bool, Field(default=True, description="Whether the model is actively available")] = True


class SystemConfigModelRegistry(V2CoreBase):
    """V2 Flattened Model Registry System Config."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True, title="model_registry")

    id: Annotated[str, Field(pattern=OPAQUE_STRIPE_ID_REGEX, description="System config ID")]
    name: Annotated[str, Field(default="Default Model Registry", description="Human-readable title")] = (
        "Default Model Registry"
    )
    type: Annotated[Literal["model_registry"], Field(default="model_registry", description="Type of config")] = (
        "model_registry"
    )
    slug: Annotated[str | None, Field(default=None, description="System Config identifier slug")] = None
    default_provider: Annotated[
        LaxLLMProvider, Field(default=LLMProvider.AI_STUDIO, description="Default LLM provider")
    ] = LLMProvider.AI_STUDIO
    tier_definitions: Annotated[
        dict[LaxCognitiveTier, ModelProfile],
        Field(
            strict=False,
            description="Direct mapping of the four canonical cognitive tiers to physical profiles",
        ),
    ]

    @model_validator(mode="after")
    def validate_tier_completeness(self) -> Self:
        """Enforces that the model registry implements all four canonical CognitiveTiers."""
        required_tiers = set(CognitiveTier)
        missing = required_tiers - set(self.tier_definitions.keys())
        if missing:
            missing_str = ", ".join(sorted(t.value for t in missing))
            raise ValueError(
                f"Model registry '{self.name}' (id={self.id}) is missing required cognitive tiers: {missing_str}"
            )
        return self


# Phase 1, Step 1.2: Upgrade AllowedMCPTool with strict MCPToolInputSchemaDTO and frozen=True
class AllowedMCPTool(V2CoreBase):
    """Declares a single MCP tool available for LLM function calling."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    tool_id: Annotated[
        str,
        Field(min_length=1, description="The unique technical identifier of the MCP tool."),
    ]
    capability: Annotated[
        LaxToolCapability,
        Field(default=ToolCapability.SEARCH, description="Operational capability category of the tool."),
    ] = ToolCapability.SEARCH
    name: Annotated[I18nText, Field(description="Localized display name.")]
    description: Annotated[str, Field(description="English-only LLM description for function calling schema.")]
    input_schema: MCPToolInputSchemaDTO = Field(
        default_factory=MCPToolInputSchemaDTO,
        description="Strict recursive JSON Schema for tool parameters.",
    )
    enabled: Annotated[
        bool,
        Field(default=True, description="Whether this discovered tool is enabled for agent execution."),
    ] = True


# Phase 1, Step 1.2: Upgrade MCPAuditTrace with provenance fields and PEP 593 Annotated syntax
class MCPAuditTrace(V2CoreBase):
    """Immutable audit log entry for a single MCP tool invocation."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    id: Annotated[
        str | None,
        Field(default=None, description="Unique identifier for the trace injected by the driver."),
    ] = None
    tool_id: Annotated[str, Field(description="Which tool was called.")]
    gateway_id: Annotated[
        str | None,
        Field(
            default=None,
            pattern=OPAQUE_STRIPE_ID_REGEX,
            description="Opaque ID of the MCP gateway that executed the tool.",
        ),
    ] = None
    gateway_slug: Annotated[
        str | None,
        Field(default=None, description="Namespace slug of the MCP gateway."),
    ] = None
    namespaced_alias: Annotated[
        str | None,
        Field(default=None, description="Full namespaced tool alias invoked by the LLM."),
    ] = None
    step_name: Annotated[str, Field(description="DAG step that triggered the call.")]
    claim_text: Annotated[
        str | None,
        Field(default=None, description="The verbatim claim that triggered this search."),
    ] = None
    query: Annotated[str, Field(description="The search query or tool input.")]
    knowledge_gap: Annotated[
        str,
        Field(default="", description="The knowledge gap that needs to be resolved."),
    ] = ""
    search_rationale: Annotated[
        str,
        Field(default="", description="The rationale for the search query."),
    ] = ""
    reasoning: Annotated[
        str,
        Field(default="", description="Brief explanation of why this claim was verified."),
    ] = ""
    response_summary: Annotated[str, Field(default="", description="Extracted text summary.")] = ""
    source_urls: list[str] = Field(default_factory=list, description="Source URLs returned.")
    impacted_axis_names: list[str] = Field(
        default_factory=list, description="List of matrix axis names that used this trace."
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp of the tool call.",
    )
    duration_ms: Annotated[int, Field(default=0, description="Round-trip latency in milliseconds.")] = 0


# Phase 1, Step 1.2: Upgrade SystemConfigMCPGateways with transport, auth, and non-empty single-underscore slug
class SystemConfigMCPGateways(V2CoreBase):
    """System-level registry of available MCP tool gateways."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True, title="mcp_gateways")

    id: Annotated[str, Field(pattern=OPAQUE_STRIPE_ID_REGEX, description="System config ID")]
    type: Annotated[
        Literal["mcp_gateways"],
        Field(default="mcp_gateways", description="Config type discriminator."),
    ] = "mcp_gateways"
    slug: Annotated[
        str,
        Field(
            default="default_mcp_gateway",
            min_length=1,
            pattern=r"^[a-z0-9]+(?:_[a-z0-9]+)*$",
            description="Collision-free gateway namespace slug without double underscores.",
        ),
    ] = "default_mcp_gateway"
    endpoint_url: Annotated[
        str,
        Field(default="", description="HTTP/HTTPS endpoint URL of the external MCP server."),
    ] = ""
    transport_type: Annotated[
        LaxMCPTransportType,
        Field(default=MCPTransportType.STREAMABLE_HTTP, description="MCP transport protocol."),
    ] = MCPTransportType.STREAMABLE_HTTP
    auth_type: Annotated[
        LaxMCPAuthType,
        Field(default=MCPAuthType.NONE, description="Authentication scheme for the MCP gateway."),
    ] = MCPAuthType.NONE
    auth_header_name: Annotated[
        str | None,
        Field(default=None, description="Custom HTTP header name when auth_type is api_key_header."),
    ] = None
    auth_env_var: Annotated[
        str | None,
        Field(default=None, description="Name of the environment variable holding the secret token or API key."),
    ] = None
    timeout_seconds: Annotated[
        int,
        Field(default=30, ge=1, le=300, description="Request timeout in seconds for this MCP gateway."),
    ] = 30
    tools: list[AllowedMCPTool] = Field(
        default_factory=list, description="Registry of all available MCP tools in the system."
    )
