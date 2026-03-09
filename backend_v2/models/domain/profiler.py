"""Profiler Agent Domain Models.

This module contains the schemas for the Profiler Agent,
including intent analysis and text metrics.
"""


from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from backend_v2.models.domain.base import ReasoningTrace, ReasoningTraceDTO
from backend_v2.models.enums import RoleClassification


class ProfilerInput(BaseModel):
    """Strict input schema for ProfilerAgent."""

    history_text: str = Field(..., description="Chat history to profile.")
    product_text: str | None = Field(None, description="Product context (optional).")
    profiler_metrics: ProfilerMetrics | None = Field(None, description="Injected text metrics.")
    last_reasoning_trace: str | None = Field(default=None, description="Previous reasoning trace.")

    model_config = ConfigDict(frozen=True, extra="ignore")


class TextMetrics(BaseModel):
    """Metrics for text analysis."""

    word_count: int = Field(..., description="Total word count.", json_schema_extra={"x-ui-label": "Word Count"})
    sentence_count: int = Field(
        ..., description="Total sentence count.", json_schema_extra={"x-ui-label": "Sentence Count"}
    )
    avg_sentence_length: float = Field(
        ..., description="Average words per sentence.", json_schema_extra={"x-ui-label": "Avg Sentence Length"}
    )
    lexical_diversity: float = Field(
        ..., description="Unique words / total words.", json_schema_extra={"x-ui-label": "Lexical Diversity"}
    )
    capitalization_ratio: float = Field(
        ..., description="Uppercase chars / total chars.", json_schema_extra={"x-ui-label": "Capitalization Ratio"}
    )
    # Added for Metric Hook consolidation
    control_ratio: float = Field(
        default=0.0, description="User/AI token ratio.", json_schema_extra={"x-ui-label": "Control Ratio"}
    )

    model_config = ConfigDict(frozen=True, strict=False)

    @field_validator("word_count", "sentence_count")
    @classmethod
    def validate_non_negative_int(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Count cannot be negative.")
        return v

    @field_validator("avg_sentence_length", "lexical_diversity", "capitalization_ratio", "control_ratio")
    @classmethod
    def validate_non_negative_float(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Metric cannot be negative.")
        return v


class BehavioralMetrics(BaseModel):
    """Heuristic behavioral metrics."""

    say_do_gap: float = Field(
        default=0.0,
        description="Discrepancy between intent and action.",
        json_schema_extra={"x-ui-label": "Say-Do Gap"},
    )
    automation_bias: float = Field(
        default=0.0, description="Over-reliance on AI.", json_schema_extra={"x-ui-label": "Automation Bias"}
    )
    illusion_of_competence: float = Field(
        default=0.0, description="False sense of mastery.", json_schema_extra={"x-ui-label": "Illusion of Competence"}
    )
    imperative_command_count: int = Field(
        ...,
        ge=0,
        description="Number of imperative commands.",
        json_schema_extra={"x-ui-label": "Command Count"},
    )
    role_classification: RoleClassification = Field(
        ...,
        description="Role classification (Passenger, Navigator, Driver, Architect).",
        json_schema_extra={"x-ui-label": "Role Classification"},
    )

    @field_validator("imperative_command_count")
    @classmethod
    def validate_non_negative_int(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Count cannot be negative.")
        return v

    @model_validator(mode="before")
    @classmethod
    def cast_role(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Strict mapping cast from str to RoleClassification for fail-fast
            val = data.get("role_classification")
            if val is not None and not isinstance(val, RoleClassification):
                try:
                    data["role_classification"] = RoleClassification(val)
                except ValueError:
                    val_upper = val.upper()
                    if not val_upper.startswith("ROLE_"):
                        for member in RoleClassification:
                            if member.value.replace("ROLE_", "") == val_upper:
                                data["role_classification"] = member
                                break
        return data

    model_config = ConfigDict(frozen=True, strict=False)


class ProfilerMetrics(TextMetrics, BehavioralMetrics):
    """Combined quantitative and behavioral metrics for the Profiler."""
    model_config = ConfigDict(frozen=True, strict=False)

class ProfilerDTO(ReasoningTraceDTO):
    """Profiler DTO (Content Only)."""

    author_intent: str = Field(
        ...,
        description="Assessed intent of the author.",
        json_schema_extra={"x-ui-label": "Author Intent"},
    )
    cognitive_biases: list[str] = Field(
        ...,
        description="Detected cognitive biases.",
        json_schema_extra={"x-ui-label": "Cognitive Biases"},
    )
    emotional_tone: str = Field(
        ...,
        description="Emotional tone analysis.",
        json_schema_extra={"x-ui-label": "Emotional Tone"},
    )
    metrics: ProfilerMetrics | None = Field(
        default=None,
        description="Quantitative and behavioral text metrics.",
        json_schema_extra={"x-ui-label": "Metrics"},
    )
    model_config = ConfigDict(frozen=True, strict=False)

    @field_validator("author_intent", "emotional_tone")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()

    @field_validator("cognitive_biases")
    @classmethod
    def validate_list_items(cls, v: list[str]) -> list[str]:
        return [item.strip() for item in v if item and item.strip()]


class ProfilerOutput(ProfilerDTO, ReasoningTrace):
    """Output schema for the Profiler Agent."""

    model_config = ConfigDict(frozen=True, strict=False)
