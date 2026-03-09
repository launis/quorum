"""Interaction Agent Domain Models.

This module contains the schemas for the Interaction Agent,
including user role classification and input quality assessment.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend_v2.models.domain.base import ReasoningTrace, ReasoningTraceDTO


class InteractionInput(BaseModel):
    """Strict input schema for InteractionAnalystAgent."""

    history_text: str = Field(
        ..., description="The full conversation history to analyze.", json_schema_extra={"x-ui-label": "Chat History"}
    )
    last_reasoning_trace: str | None = Field(default=None, description="Previous reasoning trace.")

    model_config = ConfigDict(frozen=True, extra="ignore")

    @field_validator("history_text")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("History text cannot be empty.")
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
