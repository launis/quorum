"""Interaction Agent Domain Models.

This module contains the schemas for the Interaction Agent,
including user role classification and input quality assessment.
"""

import logging
from typing import Any

from pydantic import Field

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.base import ReasoningTrace, ReasoningTraceDTO
from backend_v2.models.enums import InteractionStrategy, RoleClassification

logger = logging.getLogger(__name__)


class InteractionInput(V2CoreBase):
    """Strict input schema for InteractionAnalystAgent.

    V2 Dynamic: 'chatlog' is mandatory, but other inputs are encapsulated dynamically.
    """

    chat_log: str = Field(
        ...,
        min_length=1,
        description="The mandatory conversation history to analyze.",
        json_schema_extra={"x-ui-label": "Chatlog"},
    )
    last_reasoning_trace: str | None = Field(default=None, description="Previous reasoning trace.")

    dynamic_inputs: dict[str, Any] = Field(
        default_factory=dict, description="Structured dictionary for dynamic inputs."
    )


class InteractionAnalysisDTO(ReasoningTraceDTO):
    """Data Transfer Object for Interaction Agent (Content Only)."""

    role_classification: RoleClassification = Field(
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
        ge=0,
        description="Number of direct commands given by user.",
        json_schema_extra={"x-ui-label": "Commands"},
    )
    strategy: InteractionStrategy = Field(
        ...,
        description="Identified prompting strategy.",
        json_schema_extra={"x-ui-label": "Strategy"},
    )


class InteractionAnalysis(InteractionAnalysisDTO, ReasoningTrace):
    """Output schema for the Interaction Agent (Domain Model with Metadata)."""
