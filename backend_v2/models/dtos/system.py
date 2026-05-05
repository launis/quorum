"""Data Transfer Objects for System domain."""

from typing import Annotated, Any

from pydantic import Field

from backend_v2.models.dtos.base import BaseDTO, BaseResponseDTO


class HookListResponse(BaseResponseDTO):
    """Schema for returning available configured hooks."""

    hooks: list[str]


class ClientErrorPayload(BaseDTO):
    """Payload sent by the Flutter client when an unhandled or caught error occurs."""

    session_id: Annotated[str | None, Field(description="Client session or user ID if available")] = None
    app_version: Annotated[str | None, Field(description="Client application version")] = None
    platform: Annotated[str | None, Field(description="Client platform OS (e.g. android, ios, web)")] = None
    locale: Annotated[str | None, Field(description="Client UI language")] = None
    error_message: Annotated[str, Field(description="The main error message or exception toString()")]
    stack_trace: Annotated[str | None, Field(description="The Dart stack trace lines")] = None
    severity: Annotated[str, Field(description="Severity level, usually 'error' or 'fatal'")] = "error"
    context_data: Annotated[dict[str, Any], Field(default_factory=dict, description="Additional context or state dump")]
