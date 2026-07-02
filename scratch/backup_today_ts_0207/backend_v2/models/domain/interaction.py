"""Interaction Agent Domain Models.

This module contains the schemas for the Interaction Agent,
including user role classification and input quality assessment.
"""

from __future__ import annotations

import logging
from typing import Any

from pydantic import Field, field_validator

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.base import ReasoningTrace, ReasoningTraceDTO
from backend_v2.models.enums import LaxInteractionStrategy, LaxRoleClassification

logger = logging.getLogger(__name__)


class InteractionInput(V2CoreBase):
    """Strict input schema for InteractionAnalystAgent.

    V2 Dynamic: 'chat_log' is mandatory, but other inputs are encapsulated dynamically.

    Attributes:
        chat_log: The mandatory conversation history to analyze.
        last_reasoning_trace: Previous reasoning trace.
        dynamic_inputs: Structured dictionary for dynamic inputs.
    """

    chat_log: str = Field(
        ...,
        min_length=1,
        description="The mandatory conversation history to analyze.",
        json_schema_extra={"x-ui-label": "Chatlog"},
    )
    last_reasoning_trace: str | None = Field(
        default=None,
        description="Previous reasoning trace.",
    )
    dynamic_inputs: dict[str, Any] = Field(
        default_factory=dict,
        description="Structured dictionary for dynamic inputs.",
    )


class InteractionAnalysisDTO(ReasoningTraceDTO):
    """Data Transfer Object for Interaction Agent (Content Only).

    Attributes:
        role_classification: User role classification.
        high_dependency: Flag indicating high dependency on AI.
        imperative_command_count: Number of direct commands given by user.
        strategy: Identified prompting strategy.
    """

    role_classification: LaxRoleClassification = Field(
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

    @field_validator("imperative_command_count")
    @classmethod
    def validate_command_count(cls, v: int) -> int:
        """Enforces that imperative command count is non-negative.

        Args:
            v: The command count to validate.

        Returns:
            The validated non-negative integer.

        Raises:
            AppException: If count is negative (VALIDATION_FAILED).
        """
        if v < 0:
            msg = "imperative_command_count must be greater than or equal to 0"
            logger.error("[InteractionModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, details={"error_code": ErrorCodes.VALIDATION_FAILED})
        return v

    strategy: LaxInteractionStrategy = Field(
        ...,
        description="Identified prompting strategy.",
        json_schema_extra={"x-ui-label": "Strategy"},
    )


class InteractionAnalysis(InteractionAnalysisDTO, ReasoningTrace):
    """Output schema for the Interaction Agent (Domain Model with Metadata)."""

    pass
