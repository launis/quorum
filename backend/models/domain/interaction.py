"""Interaction Agent Domain Models.

This module contains the schemas for the Interaction Agent,
including user role classification and input quality assessment.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.models.domain.base import ReasoningTrace


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


class InteractionAnalysis(ReasoningTrace):
    """Output schema for the Interaction Agent."""

    role_classification: Literal["Passenger", "Navigator", "Driver", "Architect"] = Field(
        ...,
        description="User role classification.",
        json_schema_extra={"x-ui-label": "Role"},
    )
    input_quality_score: float = Field(
        ...,
        description="Quality score of user input.",
        json_schema_extra={"x-ui-label": "Input Quality"},
    )
    improvement_suggestions: list[str] = Field(
        ...,
        description="Suggestions for better prompting.",
        json_schema_extra={"x-ui-label": "Suggestions"},
    )
    model_config = ConfigDict(frozen=True)

    @field_validator("input_quality_score")
    @classmethod
    def validate_score_range(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError("Score must be between 0.0 and 1.0.")
        return v

    @field_validator("improvement_suggestions")
    @classmethod
    def validate_suggestions(cls, v: list[str]) -> list[str]:
        # Filter out empty strings first? Or fail fast?
        # RFC 7807 says strictness. so Fail Fast if empty string provided.
        for item in v:
            if not item or not item.strip():
                raise ValueError("Improvement suggestions cannot contain empty strings.")
        return v
