"""Domain models for system configuration and platform settings.

SSOT for ChatMessageDTO, ChatHistoryDTO, DataDictionaryField, ProviderExtraParamsDTO,
ModelProfile, SystemConfigModelRegistry, AllowedMCPTool, MCPAuditTrace, and
SystemConfigMCPGateways.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated, Any, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend_v2.models.core_base import OPAQUE_STRIPE_ID_REGEX, I18nText, V2CoreBase
from backend_v2.models.enums import (
    CognitiveTier,
    LaxCognitiveTier,
    LaxComponentType,
    LaxLLMProvider,
    LLMProvider,
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
]


class ChatMessageDTO(V2CoreBase):
    """Schema for a single parsed chat message.

    Attributes:
        role: The role of the speaker (e.g. 'user' or 'ai').
        content: The message text.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    role: str = Field(description="The role of the speaker (e.g. 'user' or 'ai').")
    content: str = Field(description="The message text.")


class ChatHistoryDTO(V2CoreBase):
    """Strict schema for a complete parsed chat sequence.

    Attributes:
        conversation: List of messages in chronological order.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    conversation: list[ChatMessageDTO] = Field(description="List of messages in chronological order.")


class DataDictionaryField(V2CoreBase):
    """UI Hints mapping for dynamic form generation (SDUI)."""

    model_config = ConfigDict(strict=True, extra="forbid")

    field_id: str
    component_type: LaxComponentType = Field(description="E.g., 'slider', 'text_input', 'dropdown'")
    options: list[dict[str, Any]] | None = None
    validation_rules: dict[str, Any] | None = None


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

    provider: str = Field(description="E.g., 'google', 'openai'")
    model_name: str = Field(description="The underlying API model name")
    temperature: float | None = Field(default=None, description="Generation temperature")
    top_p: float | None = Field(default=None, description="Nucleus sampling probability")
    top_k: int | None = Field(default=None, description="Top-K sampling")
    tpm_limit: int | None = Field(default=None, description="Tokens per minute limit")
    rpm_limit: int | None = Field(default=None, description="Requests per minute limit")
    max_tokens: int | None = Field(default=None, description="Max generated tokens")
    frequency_penalty: float | None = Field(default=None, description="Frequency penalty")
    presence_penalty: float | None = Field(default=None, description="Presence penalty")
    allowed_tools: list[str] = Field(default_factory=list, description="Enabled tools")
    supports_grounding: bool = Field(default=False, description="Supports Google Search Grounding")
    api_key: str | None = Field(default=None, description="Optional override API key")
    parsing_mode: str | None = Field(default=None, description="Parser logic flag (e.g. 'STRUCTURED_JSON')")
    caching_strategy: str | None = Field(
        default=None, description="Cache strategy identifier (e.g. 'anthropic_ephemeral')"
    )
    # Phase 1: Strongly-typed thinking/reasoning token budget
    thinking_budget_tokens: int | None = Field(
        default=None, description="Reasoning/thinking token budget for reasoning models (e.g. Gemini 3.7, Claude 3.7)"
    )
    additional_params: ProviderExtraParamsDTO = Field(
        default_factory=ProviderExtraParamsDTO, description="Additional provider-specific parameters."
    )
    is_active: bool = Field(default=True, description="Whether the model is actively available")


class SystemConfigModelRegistry(V2CoreBase):
    """V2 Flattened Model Registry System Config."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True, title="model_registry")

    id: str = Field(pattern=OPAQUE_STRIPE_ID_REGEX, description="System config ID")
    name: str = Field(default="Default Model Registry", description="Human-readable title")
    type: Literal["model_registry"] = Field(default="model_registry", description="Type of config")
    slug: str | None = Field(default=None, description="System Config identifier slug")
    default_provider: LaxLLMProvider = Field(default=LLMProvider.AI_STUDIO, description="Default LLM provider")
    tier_definitions: Annotated[dict[LaxCognitiveTier, ModelProfile], Field(strict=False)] = Field(
        description="Direct mapping of the four canonical cognitive tiers to physical profiles"
    )

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


class AllowedMCPTool(V2CoreBase):
    """Declares a single MCP tool available for LLM function calling."""

    model_config = ConfigDict(strict=True, extra="forbid")

    tool_id: str = Field(description="Unique slug (e.g. 'mcp_tavily_search').")
    name: I18nText = Field(description="Localized display name.")
    description: str = Field(description="English-only LLM description for function calling schema.")
    input_schema: dict[str, Any] = Field(
        default_factory=dict, description="JSON Schema defining the tool's input parameters."
    )


class MCPAuditTrace(V2CoreBase):
    """Immutable audit log entry for a single MCP tool invocation."""

    model_config = ConfigDict(strict=True, extra="forbid")

    id: str | None = Field(default=None, description="Unique identifier for the trace injected by the driver.")
    tool_id: str = Field(description="Which tool was called.")
    step_name: str = Field(description="DAG step that triggered the call.")
    claim_text: str | None = Field(default=None, description="The verbatim claim that triggered this search.")
    query: str = Field(description="The search query or tool input.")
    knowledge_gap: str = Field(default="", description="The knowledge gap that needs to be resolved.")
    search_rationale: str = Field(default="", description="The rationale for the search query.")
    reasoning: str = Field(default="", description="Brief explanation of why this claim was verified.")
    response_summary: str = Field(default="", description="Extracted text summary.")
    source_urls: list[str] = Field(default_factory=list, description="Source URLs returned.")
    impacted_axis_names: list[str] = Field(
        default_factory=list, description="List of matrix axis names that used this trace."
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="UTC timestamp of the tool call."
    )
    duration_ms: int = Field(default=0, description="Round-trip latency in milliseconds.")


class SystemConfigMCPGateways(V2CoreBase):
    """System-level registry of available MCP tool gateways."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True, title="mcp_gateways")

    id: str = Field(pattern=OPAQUE_STRIPE_ID_REGEX, description="System config ID")
    type: Literal["mcp_gateways"] = Field(default="mcp_gateways", description="Config type discriminator.")
    slug: str | None = Field(default=None, description="System Config identifier slug")
    tools: list[AllowedMCPTool] = Field(
        default_factory=list, description="Registry of all available MCP tools in the system."
    )
