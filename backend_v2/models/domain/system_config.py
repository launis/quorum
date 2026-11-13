"""Domain models for system configuration and platform settings.

SSOT for AllowedMCPTool, ChatHistoryDTO, ChatMessageDTO, DataDictionaryField,
MCPAuditTrace, ModelProfile, ProviderExtraParamsDTO, SystemConfigMCPGateways,
SystemConfigModelRegistry, SystemConfigOptionDTO, and SystemValidationRulesDTO.
"""

from datetime import UTC, datetime
from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from backend_v2.exceptions import AppException
from backend_v2.models.core_base import (
    OPAQUE_STRIPE_ID_REGEX,
    I18nText,
    V2CoreBase,
    parse_prefixed_uuid7,
)
from backend_v2.models.dtos.mcp import MCPToolExecutionDTO, MCPToolInputSchemaDTO
from backend_v2.models.enums import (
    CognitiveTier,
    EntityPrefix,
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
    """Selectable option for dropdown/multiselect UI components.

    Attributes:
        value: Underlying option value.
        label: Display label for the option.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    value: Annotated[str, Field(description="Underlying option value.")]
    label: Annotated[
        str | I18nText | None,
        Field(default=None, description="Display label for the option."),
    ] = None


class SystemValidationRulesDTO(V2CoreBase):
    """Validation rules for SDUI dynamic data dictionary fields.

    Attributes:
        min: Minimum numeric bound.
        max: Maximum numeric bound.
        required: Whether the field is mandatory.
        pattern: Regex validation pattern.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    min: Annotated[float | int | None, Field(default=None, description="Minimum numeric bound.")] = None
    max: Annotated[float | int | None, Field(default=None, description="Maximum numeric bound.")] = None
    required: Annotated[bool | None, Field(default=None, description="Whether the field is mandatory.")] = None
    pattern: Annotated[str | None, Field(default=None, description="Regex validation pattern.")] = None


class DataDictionaryField(V2CoreBase):
    """UI Hints mapping for dynamic form generation (SDUI).

    Attributes:
        field_id: Unique field identifier.
        component_type: UI component type identifier.
        options: Selectable options for dropdown or multiselect components.
        validation_rules: Validation constraints for the dynamic field.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    field_id: Annotated[str, Field(description="Unique field identifier.")]
    component_type: Annotated[LaxComponentType, Field(description="E.g., 'slider', 'text_input', 'dropdown'")]
    options: Annotated[
        list[SystemConfigOptionDTO] | None,
        Field(default=None, description="Selectable options for dropdown or multiselect components."),
    ] = None
    validation_rules: Annotated[
        SystemValidationRulesDTO | None,
        Field(default=None, description="Validation constraints for the dynamic field."),
    ] = None


class ProviderExtraParamsDTO(BaseModel):
    """Provider-specific optional parameters for ModelProfile.

    Attributes:
        temperature: Sampling temperature override.
        top_p: Nucleus sampling probability override.
        top_k: Top-K sampling override.
        max_output_tokens: Maximum output token limit.
        reasoning_effort: Reasoning effort level.
        vertex_location: Vertex AI region override.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    temperature: Annotated[float | None, Field(default=None, description="Sampling temperature override.")] = None
    top_p: Annotated[float | None, Field(default=None, description="Nucleus sampling probability override.")] = None
    top_k: Annotated[int | None, Field(default=None, description="Top-K sampling override.")] = None
    max_output_tokens: Annotated[int | None, Field(default=None, description="Maximum output token limit.")] = None
    reasoning_effort: Annotated[str | None, Field(default=None, description="Reasoning effort level.")] = None
    vertex_location: Annotated[str | None, Field(default=None, description="Vertex AI region override.")] = None


class ModelProfile(V2CoreBase):
    """A flattened physical AI model representation.

    Attributes:
        provider: Underlying model provider identifier.
        model_name: The underlying API model name.
        temperature: Generation temperature.
        top_p: Nucleus sampling probability.
        top_k: Top-K sampling parameter.
        tpm_limit: Tokens per minute limit.
        rpm_limit: Requests per minute limit.
        max_tokens: Max generated tokens.
        frequency_penalty: Frequency penalty.
        presence_penalty: Presence penalty.
        allowed_tools: Enabled tools.
        supports_grounding: Supports Google Search Grounding.
        caching_strategy: Cache strategy identifier.
        thinking_budget_tokens: Reasoning/thinking token budget for reasoning models.
        additional_params: Additional provider-specific parameters.
        is_active: Whether the model is actively available.
    """

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
    allowed_tools: Annotated[list[str], Field(default_factory=list, description="Enabled tools")]
    supports_grounding: Annotated[bool, Field(default=False, description="Supports Google Search Grounding")] = False
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
    additional_params: Annotated[
        ProviderExtraParamsDTO,
        Field(default_factory=ProviderExtraParamsDTO, description="Additional provider-specific parameters."),
    ]
    is_active: Annotated[bool, Field(default=True, description="Whether the model is actively available")] = True


class SystemConfigModelRegistry(V2CoreBase):
    """V2 Flattened Model Registry configuration stored in model_registries.

    Attributes:
        id: Canonical Model Registry Opaque Stripe ID (mrg_<hex32>).
        name: Human-readable title.
        slug: Informational model registry identifier slug.
        default_provider: Default LLM provider.
        tier_definitions: Direct mapping of the four canonical cognitive tiers to physical profiles.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    id: Annotated[str, Field(pattern=OPAQUE_STRIPE_ID_REGEX, description="Model registry ID (mrg_<hex32>)")]
    name: Annotated[str, Field(min_length=1, description="Human-readable title")]
    slug: Annotated[str | None, Field(default=None, description="Model registry identifier slug")] = None
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

    @field_validator("id")
    @classmethod
    def _validate_model_registry_id(cls, v: str) -> str:
        """Validate that the identifier uses the canonical mrg_ prefix and RFC 9562 UUIDv7 format.

        Args:
            v: Candidate model registry identifier string.

        Returns:
            Validated model registry identifier string.

        Raises:
            ValueError: If the identifier prefix is not 'mrg' or UUIDv7 validation fails.
        """
        try:
            parse_prefixed_uuid7(v, EntityPrefix.MODEL_REGISTRY)
        except AppException as exc:
            raise ValueError(exc.message) from exc
        return v

    @model_validator(mode="after")
    def validate_tier_completeness(self) -> Self:
        """Enforce that the model registry implements all four canonical CognitiveTiers.

        Returns:
            Validated SystemConfigModelRegistry instance.

        Raises:
            ValueError: If any canonical CognitiveTier is missing from tier_definitions.
        """
        required_tiers = set(CognitiveTier)
        missing = required_tiers - set(self.tier_definitions.keys())
        if missing:
            missing_str = ", ".join(sorted(t.value for t in missing))
            raise ValueError(
                f"Model registry '{self.name}' (id={self.id}) is missing required cognitive tiers: {missing_str}"
            )
        return self


class AllowedMCPTool(V2CoreBase):
    """Declares a single MCP tool available for LLM function calling.

    Attributes:
        tool_id: The unique technical identifier of the MCP tool.
        capability: Operational capability category of the tool.
        name: Localized display name.
        description: English-only LLM description for function calling schema.
        input_schema: Strict recursive JSON Schema for tool parameters.
        enabled: Whether this discovered tool is enabled for agent execution.
        execution: Optional tool execution configuration and task support policy.
    """

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
    input_schema: Annotated[
        MCPToolInputSchemaDTO,
        Field(
            default_factory=lambda: MCPToolInputSchemaDTO(properties={}, required=[]),
            description="Strict recursive JSON Schema for tool parameters.",
        ),
    ]
    enabled: Annotated[
        bool,
        Field(default=True, description="Whether this discovered tool is enabled for agent execution."),
    ] = True
    execution: Annotated[
        MCPToolExecutionDTO | None,
        Field(default=None, description="Optional tool execution configuration and task support policy."),
    ] = None


class MCPAuditTrace(V2CoreBase):
    """Immutable audit log entry for a single MCP tool invocation.

    Attributes:
        id: Unique identifier for the trace injected by the driver.
        tool_id: Which tool was called.
        gateway_id: Opaque ID of the MCP gateway that executed the tool.
        gateway_slug: Namespace slug of the MCP gateway.
        namespaced_alias: Full namespaced tool alias invoked by the LLM.
        step_name: DAG step that triggered the call.
        claim_text: The verbatim claim that triggered this search.
        query: The search query or tool input.
        knowledge_gap: The knowledge gap that needs to be resolved.
        search_rationale: The rationale for the search query.
        reasoning: Brief explanation of why this claim was verified.
        response_summary: Extracted text summary.
        source_urls: Source URLs returned.
        impacted_axis_names: List of matrix axis names that used this trace.
        timestamp: UTC timestamp of the tool call.
        duration_ms: Round-trip latency in milliseconds.
    """

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
    source_urls: Annotated[list[str], Field(default_factory=list, description="Source URLs returned.")]
    impacted_axis_names: Annotated[
        list[str],
        Field(default_factory=list, description="List of matrix axis names that used this trace."),
    ]
    timestamp: Annotated[
        datetime,
        Field(
            default_factory=lambda: datetime.now(UTC),
            description="UTC timestamp of the tool call.",
        ),
    ]
    duration_ms: Annotated[int, Field(default=0, description="Round-trip latency in milliseconds.")] = 0

    @field_validator("gateway_id")
    @classmethod
    def _validate_gateway_id(cls, v: str | None) -> str | None:
        """Validate that an optional gateway_id uses the canonical mcp_ prefix and RFC 9562 UUIDv7 format.

        Args:
            v: Optional candidate MCP gateway identifier string.

        Returns:
            Validated MCP gateway identifier string, or None.

        Raises:
            ValueError: If gateway_id is provided and fails mcp_<hex32> UUIDv7 validation.
        """
        if v is None:
            return None
        try:
            parse_prefixed_uuid7(v, EntityPrefix.MCP_GATEWAY)
        except AppException as exc:
            raise ValueError(exc.message) from exc
        return v


class SystemConfigMCPGateways(V2CoreBase):
    """Registry entry for an external MCP tool gateway stored in mcp_gateways.

    Attributes:
        id: Canonical MCP gateway Opaque Stripe ID (mcp_<hex32>).
        organization_id: Owning tenant organization Opaque Stripe ID (org_<hex32>).
        name: Human-readable gateway title.
        slug: Collision-free gateway namespace slug without double underscores.
        endpoint_url: HTTP/HTTPS endpoint URL of the external MCP server.
        transport_type: MCP transport protocol.
        auth_type: Authentication scheme for the MCP gateway.
        auth_header_name: Custom HTTP header name when auth_type is api_key_header.
        auth_env_var: Name of the environment variable holding the secret token or API key.
        timeout_seconds: Request timeout in seconds for this MCP gateway.
        tools: Registry of all available MCP tools in the system.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    id: Annotated[str, Field(pattern=OPAQUE_STRIPE_ID_REGEX, description="MCP gateway ID (mcp_<hex32>).")]
    organization_id: Annotated[
        str,
        Field(
            pattern=OPAQUE_STRIPE_ID_REGEX,
            description="Owning tenant organization ID (org_<hex32>).",
        ),
    ]
    name: Annotated[str, Field(min_length=1, description="Human-readable gateway title.")]
    slug: Annotated[
        str,
        Field(
            min_length=1,
            pattern=r"^[a-z0-9]+(?:_[a-z0-9]+)*$",
            description="Collision-free gateway namespace slug without double underscores.",
        ),
    ]
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
    tools: Annotated[
        list[AllowedMCPTool],
        Field(default_factory=list, description="Registry of all available MCP tools in the system."),
    ]

    @field_validator("id")
    @classmethod
    def _validate_mcp_gateway_id(cls, v: str) -> str:
        """Validate that the identifier uses the canonical mcp_ prefix and RFC 9562 UUIDv7 format.

        Args:
            v: Candidate MCP gateway identifier string.

        Returns:
            Validated MCP gateway identifier string.

        Raises:
            ValueError: If the identifier prefix is not 'mcp' or UUIDv7 validation fails.
        """
        try:
            parse_prefixed_uuid7(v, EntityPrefix.MCP_GATEWAY)
        except AppException as exc:
            raise ValueError(exc.message) from exc
        return v

    @field_validator("organization_id")
    @classmethod
    def _validate_organization_id(cls, v: str) -> str:
        """Validate that organization_id uses the canonical org_ prefix and RFC 9562 UUIDv7 format.

        Args:
            v: Candidate organization identifier string.

        Returns:
            Validated organization identifier string.

        Raises:
            ValueError: If organization_id prefix is not 'org' or UUIDv7 validation fails.
        """
        try:
            parse_prefixed_uuid7(v, EntityPrefix.ORGANIZATION)
        except AppException as exc:
            raise ValueError(exc.message) from exc
        return v
