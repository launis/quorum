"""Profiler Agent Domain Models.

This module contains the schemas for the Profiler Agent,
including intent analysis and text metrics.
"""

import logging

from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend_v2.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)

from backend_v2.models.domain.base import ReasoningTrace, ReasoningTraceDTO


class ProfilerInput(BaseModel):
    """Strict input schema for ProfilerAgent.

    V2 Dynamic: 'chatlog' is mandatory, but other inputs are allowed dynamically.
    """

    chat_log: str = Field(
        ..., description="The mandatory conversation history.", json_schema_extra={"x-ui-label": "Chatlog"}
    )
    profiler_metrics: ProfilerMetrics | None = Field(None, description="Injected text metrics.")
    last_reasoning_trace: str | None = Field(default=None, description="Previous reasoning trace.")

    model_config = ConfigDict(frozen=True, extra="allow")


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

    model_config = ConfigDict(frozen=True, strict=False, extra="forbid")

    @field_validator("word_count", "sentence_count")
    @classmethod
    def validate_non_negative_int(cls, v: int) -> int:
        if v < 0:
            msg = "Count cannot be negative."
            logger.error("[ProfilerModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, status_code=422, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})
        return v

    @field_validator("avg_sentence_length", "lexical_diversity", "capitalization_ratio", "control_ratio")
    @classmethod
    def validate_non_negative_float(cls, v: float) -> float:
        if v < 0:
            msg = "Metric cannot be negative."
            logger.error("[ProfilerModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, status_code=422, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})
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

    @field_validator("imperative_command_count")
    @classmethod
    def validate_non_negative_int(cls, v: int) -> int:
        if v < 0:
            msg = "Count cannot be negative."
            logger.error("[ProfilerModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, status_code=422, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})
        return v

    model_config = ConfigDict(frozen=True, strict=False, extra="forbid")


class ProfilerMetrics(TextMetrics, BehavioralMetrics):
    """Combined quantitative and behavioral metrics for the Profiler."""

    model_config = ConfigDict(frozen=True, strict=False, extra="forbid")


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
    model_config = ConfigDict(frozen=True, strict=False, extra="forbid")

    @field_validator("author_intent", "emotional_tone")
    @classmethod
    def validate_non_empty(cls, v: str | None) -> str:
        if not v or not str(v).strip():
            msg = "Field cannot be empty or whitespace only."
            logger.error("[ProfilerModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, status_code=422, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})
        return str(v).strip()

    @field_validator("cognitive_biases")
    @classmethod
    def validate_list_items(cls, v: list[str]) -> list[str]:
        if not v:
            msg = "cognitive_biases cannot be empty. Zero-Compromise Fail-Fast enforced."
            logger.error("[ProfilerModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, status_code=422, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})
        for item in v:
            if not item or not item.strip():
                msg = "cognitive_biases items cannot be empty strings."
                logger.error("[ProfilerModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                raise AppException(
                    message=msg, status_code=422, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
                )
        return v


class ProfilerOutput(ProfilerDTO, ReasoningTrace):
    """Output schema for the Profiler Agent."""

    model_config = ConfigDict(frozen=True, strict=False, extra="forbid")
