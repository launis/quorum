"""Data Transfer Objects for System domain.

All DTOs defined here adhere to strict Pydantic V2 configurations and PEP 695
standards for type hint safety and runtime validation.
"""

from typing import Annotated, Any

from pydantic import ConfigDict, Field

from backend_v2.models.dtos.base import BaseDTO, BaseResponseDTO


class HookListResponse(BaseResponseDTO):
    """Schema for returning available configured hooks.

    Attributes:
        hooks: A list of registered system hooks or callback identifiers.
    """

    model_config = ConfigDict(frozen=True)

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

    model_config = ConfigDict(frozen=True)

    session_id: Annotated[str | None, Field(description="Client session or user ID if available")] = None
    app_version: Annotated[str | None, Field(description="Client application version")] = None
    platform: Annotated[str | None, Field(description="Client platform OS (e.g. android, ios, web)")] = None
    locale: Annotated[str | None, Field(description="Client UI language")] = None
    error_message: Annotated[str, Field(description="The main error message or exception toString()")]
    stack_trace: Annotated[str | None, Field(description="The Dart stack trace lines")] = None
    severity: Annotated[str, Field(description="Severity level, usually 'error' or 'fatal'")] = "error"
    context_data: Annotated[dict[str, Any], Field(default_factory=dict, description="Additional context or state dump")]


class StrictnessConfigDTO(BaseDTO):
    """Schema for strictness level configuration.

    Attributes:
        level: The integer level of strictness.
        localization_key: The UI key for translation.
    """

    model_config = ConfigDict(frozen=True)

    level: Annotated[int, Field(description="The integer level of strictness")]
    localization_key: Annotated[str, Field(description="The UI key for translation")]


class StrictnessConfigListResponse(BaseResponseDTO):
    """Schema for returning a list of strictness configurations.

    Attributes:
        configs: The list of configs.
    """

    model_config = ConfigDict(frozen=True)

    configs: Annotated[list[StrictnessConfigDTO], Field(description="The list of configs")]
