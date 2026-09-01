"""Data Transfer Objects for System domain.

All DTOs defined here adhere to strict Pydantic V2 configurations and PEP 695
standards for type hint safety and runtime validation.
"""

from typing import Annotated, Any, Literal

from pydantic import ConfigDict, Field, TypeAdapter

from backend_v2.models.dtos.base import BaseDTO, BaseResponseDTO
from backend_v2.models.v2_core import (
    SystemConfigMCPGateways,
    SystemConfigModelRegistry,
    SystemConfigPerformativeLexicons,
)

__all__ = [
    "HookListResponse",
    "ClientErrorPayload",
    "StrictnessConfigDTO",
    "StrictnessConfigListResponse",
    "SystemSettingsDTO",
    "AnySystemConfig",
    "AnySystemConfigAdapter",
    "SystemConfigUpdateDTO",
    "SystemConfigCreateDTO",
    "SystemConfigUpsertDTO",
]


class HookListResponse(BaseResponseDTO):
    """Schema for returning available configured hooks.

    Attributes:
        hooks: A list of registered system hooks or callback identifiers.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    hooks: Annotated[list[str], Field(description="A list of registered system hooks or callback identifiers")]


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
        dict[str, Any],  # noqa: QGR001 [REASON: Client error telemetry payload at external HTTP ingress boundary]
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


class SystemSettingsDTO(BaseDTO):
    """DTO representing global system settings and tuning flags."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True, title="system_settings")

    type: Annotated[
        Literal["system_settings"], Field(default="system_settings", description="Config type discriminator")
    ] = "system_settings"
    environment: Annotated[str, Field(default="development", description="Runtime environment")] = "development"
    maintenance_mode: Annotated[bool, Field(default=False, description="Maintenance mode flag")] = False
    debug_logging: Annotated[bool, Field(default=False, description="Debug logging flag")] = False
    default_locale: Annotated[str, Field(default="fi", description="Default system locale")] = "fi"


# Strict Discriminated Union for System Configurations ensuring O(1) deterministic resolution and zero silent coercion (RT-1)
type AnySystemConfig = Annotated[
    SystemConfigModelRegistry | SystemConfigMCPGateways | SystemConfigPerformativeLexicons | SystemSettingsDTO,
    Field(discriminator="type"),
]

AnySystemConfigAdapter: TypeAdapter[AnySystemConfig] = TypeAdapter(AnySystemConfig)


class SystemConfigUpdateDTO(BaseDTO):
    """DTO for updating system configuration entries with strict SSOT domain models."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    model_registry: Annotated[
        SystemConfigModelRegistry | None, Field(default=None, description="Updated model registry")
    ] = None
    mcp_gateways: Annotated[SystemConfigMCPGateways | None, Field(default=None, description="Updated MCP gateways")] = (
        None
    )
    performative_lexicons: Annotated[
        SystemConfigPerformativeLexicons | None, Field(default=None, description="Updated performative lexicons")
    ] = None
    system_settings: Annotated[SystemSettingsDTO | None, Field(default=None, description="Updated system settings")] = (
        None
    )


class SystemConfigCreateDTO(BaseDTO):
    """DTO for creating a new system configuration document at ingress boundary."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    type: Annotated[str, Field(min_length=1, description="Configuration type identifier")]
    content: Annotated[AnySystemConfig, Field(description="Strict discriminated union of system configurations")]
    slug: Annotated[str | None, Field(default=None, description="Optional configuration slug")] = None


class SystemConfigUpsertDTO(BaseDTO):
    """DTO for upserting system configuration documents."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    id: Annotated[str | None, Field(default=None, description="Existing system config ID")] = None
    type: Annotated[str, Field(min_length=1, description="Configuration type identifier")]
    content: Annotated[AnySystemConfig, Field(description="Strict discriminated union of system configurations")]
    slug: Annotated[str | None, Field(default=None, description="Optional configuration slug")] = None
