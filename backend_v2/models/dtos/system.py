"""Data Transfer Objects for System domain.

All DTOs defined here adhere to strict Pydantic V2 configurations and PEP 695
standards for type hint safety and runtime validation.
"""

from typing import Annotated, Literal, Self

from pydantic import ConfigDict, Field, field_validator, model_validator

from backend_v2.exceptions import AppException
from backend_v2.models.core_base import OPAQUE_STRIPE_ID_REGEX, parse_prefixed_uuid7
from backend_v2.models.domain.system_config import AllowedMCPTool, ModelProfile
from backend_v2.models.dtos.base import BaseDTO, BaseResponseDTO
from backend_v2.models.enums import (
    CognitiveTier,
    EntityPrefix,
    LaxCognitiveTier,
    LaxLLMProvider,
    LaxMCPAuthType,
    LaxMCPTransportType,
    LLMProvider,
    MCPAuthType,
    MCPTransportType,
)

type ClientContextValue = str | int | float | bool | list[str] | None

__all__ = [
    "ClientContextValue",
    "ClientErrorPayload",
    "HealthCheckResponseDTO",
    "HookListResponse",
    "MCPGatewayCreateDTO",
    "MCPGatewayUpdateDTO",
    "MCPGatewayUpsertDTO",
    "ModelRegistryCreateDTO",
    "ModelRegistryUpdateDTO",
    "ModelRegistryUpsertDTO",
    "SafetySettingDTO",
    "StrictnessConfigDTO",
    "StrictnessConfigListResponse",
]


class SafetySettingDTO(BaseDTO):
    """DTO representing a single Google/Vertex AI safety setting category and threshold.

    Attributes:
        category: The harm category identifier.
        threshold: The threshold blocking rule.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    category: Annotated[str, Field(description="The harm category identifier")]
    threshold: Annotated[str, Field(description="The threshold blocking rule")]


class HookListResponse(BaseResponseDTO):
    """Schema for returning available configured hooks.

    Attributes:
        hooks: A list of registered system hooks or callback identifiers.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    hooks: Annotated[list[str], Field(description="A list of registered system hooks or callback identifiers")]


class HealthCheckResponseDTO(BaseResponseDTO):
    """Schema for Cloud Run and Cloud Load Balancer health probe responses.

    Attributes:
        status: Service operational status ('ok' or 'degraded').
        version: Application semantic version.
        environment: Active runtime environment stage.
        storage_backend: Active storage backend identifier.
        gcp_region: Configured GCP deployment region.
        primary_domain: Canonical production domain.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    status: Annotated[Literal["ok", "degraded"], Field(default="ok", description="Service operational status")] = "ok"
    version: Annotated[str, Field(min_length=1, description="Application semantic version")]
    environment: Annotated[Literal["development", "production"], Field(description="Active runtime environment stage")]
    storage_backend: Annotated[str, Field(min_length=1, description="Active storage backend identifier")]
    gcp_region: Annotated[str, Field(min_length=1, description="Configured GCP deployment region")]
    primary_domain: Annotated[str, Field(min_length=1, description="Canonical production domain")]


class ClientErrorPayload(BaseDTO):
    """Payload sent by the Flutter client when an unhandled or caught error occurs.

    Attributes:
        session_id: Client session or user ID if available.
        app_version: Client application version.
        platform: Client platform OS (e.g. android, ios, web).
        locale: Client UI language.
        error_message: The main error message or exception toString().
        stack_trace: The Dart stack trace lines.
        severity: Severity level, usually 'error' or 'fatal'.
        context_data: Additional context or state dump.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    session_id: Annotated[str | None, Field(description="Client session or user ID if available")] = None
    app_version: Annotated[str | None, Field(description="Client application version")] = None
    platform: Annotated[str | None, Field(description="Client platform OS (e.g. android, ios, web)")] = None
    locale: Annotated[str | None, Field(description="Client UI language")] = None
    error_message: Annotated[str, Field(description="The main error message or exception toString()")]
    stack_trace: Annotated[str | None, Field(description="The Dart stack trace lines")] = None
    severity: Annotated[str, Field(description="Severity level, usually 'error' or 'fatal'")] = "error"
    context_data: Annotated[
        dict[str, ClientContextValue],
        Field(default_factory=dict, description="Additional context or state dump"),
    ]


class StrictnessConfigDTO(BaseDTO):
    """Schema for strictness level configuration.

    Attributes:
        level: The integer level of strictness.
        localization_key: The UI key for translation.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    level: Annotated[int, Field(description="The integer level of strictness")]
    localization_key: Annotated[str, Field(description="The UI key for translation")]


class StrictnessConfigListResponse(BaseResponseDTO):
    """Schema for returning a list of strictness configurations.

    Attributes:
        configs: The list of configs.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    configs: Annotated[list[StrictnessConfigDTO], Field(description="The list of configs")]


def _validate_optional_prefixed_id(value: str | None, expected_prefix: EntityPrefix) -> str | None:
    """Validate an optional Opaque Stripe ID against an expected EntityPrefix and UUIDv7 format.

    Args:
        value: Optional identifier string.
        expected_prefix: Canonical EntityPrefix expected on the identifier.

    Returns:
        Validated identifier string, or None.

    Raises:
        ValueError: If value is provided and fails canonical prefix or UUIDv7 validation.
    """
    if value is None:
        return None
    try:
        parse_prefixed_uuid7(value, expected_prefix)
    except AppException as exc:
        raise ValueError(exc.message) from exc
    return value


def _validate_required_prefixed_id(value: str, expected_prefix: EntityPrefix) -> str:
    """Validate a required Opaque Stripe ID against an expected EntityPrefix and UUIDv7 format.

    Args:
        value: Candidate identifier string.
        expected_prefix: Canonical EntityPrefix expected on the identifier.

    Returns:
        Validated identifier string.

    Raises:
        ValueError: If value fails canonical prefix or UUIDv7 validation.
    """
    try:
        parse_prefixed_uuid7(value, expected_prefix)
    except AppException as exc:
        raise ValueError(exc.message) from exc
    return value


def _ensure_complete_tiers(name: str, tier_definitions: dict[LaxCognitiveTier, ModelProfile]) -> None:
    """Verify that tier_definitions contains all four canonical CognitiveTiers.

    Args:
        name: Human-readable model registry name for error context.
        tier_definitions: Mapping of cognitive tiers to model profiles.

    Raises:
        ValueError: If any canonical CognitiveTier is missing.
    """
    missing = set(CognitiveTier) - set(tier_definitions.keys())
    if missing:
        missing_str = ", ".join(sorted(t.value for t in missing))
        raise ValueError(f"Model registry '{name}' is missing required cognitive tiers: {missing_str}")


class ModelRegistryCreateDTO(BaseDTO):
    """DTO for creating a new model registry configuration at the ingress boundary.

    Attributes:
        name: Human-readable model registry title.
        slug: Optional informational model registry slug.
        default_provider: Default LLM provider.
        tier_definitions: Direct mapping of the four canonical cognitive tiers to physical profiles.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    name: Annotated[str, Field(min_length=1, description="Human-readable model registry title")]
    slug: Annotated[str | None, Field(default=None, description="Optional model registry slug")] = None
    default_provider: Annotated[
        LaxLLMProvider, Field(default=LLMProvider.AI_STUDIO, description="Default LLM provider")
    ] = LLMProvider.AI_STUDIO
    tier_definitions: Annotated[
        dict[LaxCognitiveTier, ModelProfile],
        Field(strict=False, description="Direct mapping of the four canonical cognitive tiers to physical profiles"),
    ]

    @model_validator(mode="after")
    def _validate_tiers(self) -> Self:
        """Ensure all four canonical CognitiveTiers are defined.

        Returns:
            Validated ModelRegistryCreateDTO instance.
        """
        _ensure_complete_tiers(self.name, self.tier_definitions)
        return self


class ModelRegistryUpdateDTO(BaseDTO):
    """DTO for updating an existing model registry configuration.

    Attributes:
        name: Optional updated model registry title.
        slug: Optional updated model registry slug.
        default_provider: Optional updated default LLM provider.
        tier_definitions: Optional updated cognitive tier definitions.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    name: Annotated[str | None, Field(default=None, min_length=1, description="Updated model registry title")] = None
    slug: Annotated[str | None, Field(default=None, description="Updated model registry slug")] = None
    default_provider: Annotated[
        LaxLLMProvider | None, Field(default=None, description="Updated default LLM provider")
    ] = None
    tier_definitions: Annotated[
        dict[LaxCognitiveTier, ModelProfile] | None,
        Field(default=None, strict=False, description="Updated cognitive tier definitions"),
    ] = None

    @model_validator(mode="after")
    def _validate_optional_tiers(self) -> Self:
        """Ensure all four canonical CognitiveTiers are defined when tier_definitions is provided.

        Returns:
            Validated ModelRegistryUpdateDTO instance.
        """
        if self.tier_definitions is not None:
            resolved_name = "update"
            if self.name is not None:
                resolved_name = self.name
            _ensure_complete_tiers(resolved_name, self.tier_definitions)
        return self


class ModelRegistryUpsertDTO(BaseDTO):
    """DTO for upserting a model registry configuration document.

    Attributes:
        id: Optional existing model registry Opaque Stripe ID (mrg_<hex32>).
        name: Human-readable model registry title.
        slug: Optional informational model registry slug.
        default_provider: Default LLM provider.
        tier_definitions: Direct mapping of the four canonical cognitive tiers to physical profiles.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    id: Annotated[
        str | None,
        Field(default=None, pattern=OPAQUE_STRIPE_ID_REGEX, description="Existing model registry ID (mrg_<hex32>)"),
    ] = None
    name: Annotated[str, Field(min_length=1, description="Human-readable model registry title")]
    slug: Annotated[str | None, Field(default=None, description="Optional model registry slug")] = None
    default_provider: Annotated[
        LaxLLMProvider, Field(default=LLMProvider.AI_STUDIO, description="Default LLM provider")
    ] = LLMProvider.AI_STUDIO
    tier_definitions: Annotated[
        dict[LaxCognitiveTier, ModelProfile],
        Field(strict=False, description="Direct mapping of the four canonical cognitive tiers to physical profiles"),
    ]

    @field_validator("id")
    @classmethod
    def _validate_id(cls, v: str | None) -> str | None:
        """Validate optional mrg_<hex32> identifier.

        Args:
            v: Optional candidate model registry identifier.

        Returns:
            Validated identifier or None.
        """
        return _validate_optional_prefixed_id(v, EntityPrefix.MODEL_REGISTRY)

    @model_validator(mode="after")
    def _validate_tiers(self) -> Self:
        """Ensure all four canonical CognitiveTiers are defined.

        Returns:
            Validated ModelRegistryUpsertDTO instance.
        """
        _ensure_complete_tiers(self.name, self.tier_definitions)
        return self


class MCPGatewayCreateDTO(BaseDTO):
    """DTO for creating a new MCP gateway configuration at the ingress boundary.

    Attributes:
        organization_id: Owning tenant organization Opaque Stripe ID (org_<hex32>).
        name: Human-readable gateway title.
        slug: Collision-free gateway namespace slug without double underscores.
        endpoint_url: HTTP/HTTPS endpoint URL of the external MCP server.
        transport_type: MCP transport protocol.
        auth_type: Authentication scheme for the MCP gateway.
        auth_header_name: Custom HTTP header name when auth_type is api_key_header.
        auth_env_var: Environment variable name holding the secret token or API key.
        timeout_seconds: Request timeout in seconds for this MCP gateway.
        tools: Registry of available MCP tools on this gateway.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    organization_id: Annotated[
        str,
        Field(pattern=OPAQUE_STRIPE_ID_REGEX, description="Owning tenant organization ID (org_<hex32>)."),
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
        str, Field(default="", description="HTTP/HTTPS endpoint URL of the external MCP server.")
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
        Field(default_factory=list, description="Registry of available MCP tools on this gateway."),
    ]

    @field_validator("organization_id")
    @classmethod
    def _validate_org_id(cls, v: str) -> str:
        """Validate required org_<hex32> organization identifier.

        Args:
            v: Candidate organization identifier string.

        Returns:
            Validated organization identifier string.
        """
        return _validate_required_prefixed_id(v, EntityPrefix.ORGANIZATION)


class MCPGatewayUpdateDTO(BaseDTO):
    """DTO for updating an existing MCP gateway configuration.

    Attributes:
        organization_id: Optional updated owning organization ID (org_<hex32>).
        name: Optional updated gateway title.
        slug: Optional updated gateway namespace slug.
        endpoint_url: Optional updated endpoint URL.
        transport_type: Optional updated transport protocol.
        auth_type: Optional updated authentication scheme.
        auth_header_name: Optional updated custom HTTP header name.
        auth_env_var: Optional updated auth environment variable name.
        timeout_seconds: Optional updated request timeout in seconds.
        tools: Optional updated list of MCP tools.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    organization_id: Annotated[
        str | None,
        Field(default=None, pattern=OPAQUE_STRIPE_ID_REGEX, description="Updated owning organization ID (org_<hex32>)"),
    ] = None
    name: Annotated[str | None, Field(default=None, min_length=1, description="Updated gateway title")] = None
    slug: Annotated[
        str | None,
        Field(default=None, min_length=1, pattern=r"^[a-z0-9]+(?:_[a-z0-9]+)*$", description="Updated gateway slug"),
    ] = None
    endpoint_url: Annotated[str | None, Field(default=None, description="Updated endpoint URL")] = None
    transport_type: Annotated[
        LaxMCPTransportType | None, Field(default=None, description="Updated transport protocol")
    ] = None
    auth_type: Annotated[LaxMCPAuthType | None, Field(default=None, description="Updated authentication scheme")] = None
    auth_header_name: Annotated[str | None, Field(default=None, description="Updated custom HTTP header name")] = None
    auth_env_var: Annotated[str | None, Field(default=None, description="Updated auth environment variable")] = None
    timeout_seconds: Annotated[
        int | None, Field(default=None, ge=1, le=300, description="Updated timeout in seconds")
    ] = None
    tools: Annotated[list[AllowedMCPTool] | None, Field(default=None, description="Updated MCP tools")] = None

    @field_validator("organization_id")
    @classmethod
    def _validate_optional_org_id(cls, v: str | None) -> str | None:
        """Validate optional org_<hex32> organization identifier.

        Args:
            v: Optional candidate organization identifier string.

        Returns:
            Validated organization identifier or None.
        """
        return _validate_optional_prefixed_id(v, EntityPrefix.ORGANIZATION)


class MCPGatewayUpsertDTO(BaseDTO):
    """DTO for upserting an MCP gateway configuration document.

    Attributes:
        id: Optional existing MCP gateway Opaque Stripe ID (mcp_<hex32>).
        organization_id: Owning tenant organization Opaque Stripe ID (org_<hex32>).
        name: Human-readable gateway title.
        slug: Collision-free gateway namespace slug without double underscores.
        endpoint_url: HTTP/HTTPS endpoint URL of the external MCP server.
        transport_type: MCP transport protocol.
        auth_type: Authentication scheme for the MCP gateway.
        auth_header_name: Custom HTTP header name when auth_type is api_key_header.
        auth_env_var: Environment variable name holding the secret token or API key.
        timeout_seconds: Request timeout in seconds for this MCP gateway.
        tools: Registry of available MCP tools on this gateway.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    id: Annotated[
        str | None,
        Field(default=None, pattern=OPAQUE_STRIPE_ID_REGEX, description="Existing MCP gateway ID (mcp_<hex32>)."),
    ] = None
    organization_id: Annotated[
        str,
        Field(pattern=OPAQUE_STRIPE_ID_REGEX, description="Owning tenant organization ID (org_<hex32>)."),
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
        str, Field(default="", description="HTTP/HTTPS endpoint URL of the external MCP server.")
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
        Field(default_factory=list, description="Registry of available MCP tools on this gateway."),
    ]

    @field_validator("id")
    @classmethod
    def _validate_id(cls, v: str | None) -> str | None:
        """Validate optional mcp_<hex32> identifier.

        Args:
            v: Optional candidate MCP gateway identifier.

        Returns:
            Validated identifier or None.
        """
        return _validate_optional_prefixed_id(v, EntityPrefix.MCP_GATEWAY)

    @field_validator("organization_id")
    @classmethod
    def _validate_org_id(cls, v: str) -> str:
        """Validate required org_<hex32> organization identifier.

        Args:
            v: Candidate organization identifier string.

        Returns:
            Validated organization identifier string.
        """
        return _validate_required_prefixed_id(v, EntityPrefix.ORGANIZATION)
