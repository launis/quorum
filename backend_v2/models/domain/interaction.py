"""Interaction Agent Domain Models.

This module contains the schemas for the Interaction Agent,
including user role classification and input quality assessment.
"""

import logging
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend_v2.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)

from backend_v2.models.domain.base import ReasoningTrace, ReasoningTraceDTO


class InteractionInput(BaseModel):
    """Strict input schema for InteractionAnalystAgent.

    V2 Dynamic: 'chatlog' is mandatory, but other inputs are allowed dynamically.
    """

    chat_log: str = Field(
        ..., description="The mandatory conversation history to analyze.", json_schema_extra={"x-ui-label": "Chatlog"}
    )
    last_reasoning_trace: str | None = Field(default=None, description="Previous reasoning trace.")

    model_config = ConfigDict(frozen=True, extra="allow")

    @field_validator("chat_log")
    @classmethod
    def validate_non_empty(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not v or not v.strip():
            msg = "chat_log cannot be empty or whitespace only."
            logger.error(f"[InteractionModel] {ErrorCodes.VALIDATION_FAILED.name}: {msg}")
            raise AppException(message=msg, status_code=422, details={"error_code": ErrorCodes.VALIDATION_FAILED})
        return v.strip()


class InteractionAnalysisDTO(ReasoningTraceDTO):
    """Data Transfer Object for Interaction Agent (Content Only)."""

    role_classification: Literal["Passenger", "Navigator", "Driver", "Architect"] = Field(
        ...,
        description="User role classification.",
        json_schema_extra={"x-ui-label": "Role"},
    )
    high_dependency: bool = Field(
        ...,
        description="Flag indicating high dependency on AI.",
        json_schema_extra={"x-ui-label": "High Dependency"},
    )
    imperative_command_count: int = Field(
        ...,
        description="Number of direct commands given by user.",
        json_schema_extra={"x-ui-label": "Commands"},
    )
    strategy: Literal["Zero-shot", "Few-shot", "Chain-of-Thought"] = Field(
        ...,
        description="Identified prompting strategy.",
        json_schema_extra={"x-ui-label": "Strategy"},
    )
    model_config = ConfigDict(frozen=True)


class InteractionAnalysis(InteractionAnalysisDTO, ReasoningTrace):
    """Output schema for the Interaction Agent (Domain Model with Metadata)."""

    model_config = ConfigDict(frozen=True, strict=True)
