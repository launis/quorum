"""Profiler Agent Domain Models.

This module contains the schemas for the Profiler Agent,
including intent analysis and text metrics.
"""

from __future__ import annotations

import logging

from pydantic import Field, field_validator

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.base import ReasoningTrace, ReasoningTraceDTO

logger = logging.getLogger(__name__)


class TextMetrics(V2CoreBase):
    """Metrics for text analysis.

    Attributes:
        word_count: Total word count.
        sentence_count: Total sentence count.
        avg_sentence_length: Average words per sentence.
        lexical_diversity: Unique words / total words.
        capitalization_ratio: Uppercase characters / total characters.
        control_ratio: User/AI token ratio.
    """

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
        ...,
        description="Uppercase chars / total chars.",
        json_schema_extra={"x-ui-label": "Capitalization Ratio"},
    )
    control_ratio: float = Field(
        default=0.0, description="User/AI token ratio.", json_schema_extra={"x-ui-label": "Control Ratio"}
    )

    @field_validator(
        "word_count",
        "sentence_count",
        "avg_sentence_length",
        "lexical_diversity",
        "capitalization_ratio",
        "control_ratio",
        mode="before",
    )
    @classmethod
    def validate_non_negative_metrics(cls, v: int | float) -> int | float:
        """Validator to replace Field level float constraints to prevent Vertex AI 400 errors.

        Args:
            v: The value to validate.

        Returns:
            The validated value.

        Raises:
            AppException: If the validation check fails on negative numbers.
        """
        if v < 0:
            msg = "Value must be greater than or equal to 0"
            logger.error("[ProfilerModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, details={"error_code": ErrorCodes.VALIDATION_FAILED})
        return v


class BehavioralMetrics(V2CoreBase):
    """Heuristic behavioral metrics.

    Attributes:
        say_do_gap: Discrepancy between intent and action.
        automation_bias: Over-reliance on AI.
        illusion_of_competence: False sense of mastery.
        imperative_command_count: Number of imperative commands.
    """

    say_do_gap: float = Field(
        default=0.0,
        description="Discrepancy between intent and action.",
        json_schema_extra={"x-ui-label": "Say-Do Gap"},
    )
    automation_bias: float = Field(
        default=0.0, description="Over-reliance on AI.", json_schema_extra={"x-ui-label": "Automation Bias"}
    )
    illusion_of_competence: float = Field(
        default=0.0,
        description="False sense of mastery.",
        json_schema_extra={"x-ui-label": "Illusion of Competence"},
    )
    imperative_command_count: int = Field(
        ...,
        description="Number of imperative commands.",
        json_schema_extra={"x-ui-label": "Command Count"},
    )

    @field_validator(
        "say_do_gap", "automation_bias", "illusion_of_competence", "imperative_command_count", mode="before"
    )
    @classmethod
    def validate_behavioral_metrics(cls, v: int | float) -> int | float:
        """Validator to replace Field level float constraints to prevent Vertex AI 400 errors.

        Args:
            v: The value to validate.

        Returns:
            The validated value.

        Raises:
            AppException: If the validation check fails on negative numbers.
        """
        if v < 0:
            msg = "Value must be greater than or equal to 0"
            logger.error("[ProfilerModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, details={"error_code": ErrorCodes.VALIDATION_FAILED})
        return v


class ProfilerMetrics(TextMetrics, BehavioralMetrics):
    """Combined quantitative and behavioral metrics for the Profiler."""


class ProfilerInput(V2CoreBase):
    """Strict input schema for ProfilerAgent.

    V2 Dynamic: 'chatlog' is mandatory, but other inputs are allowed dynamically.

    Attributes:
        chat_log: The mandatory conversation history.
        profiler_metrics: Injected text metrics.
        last_reasoning_trace: Previous reasoning trace.
    """

    chat_log: str = Field(
        ...,
        min_length=1,
        description="The mandatory conversation history.",
        json_schema_extra={"x-ui-label": "Chatlog"},
    )
    profiler_metrics: ProfilerMetrics | None = Field(None, description="Injected text metrics.")
    last_reasoning_trace: str | None = Field(default=None, description="Previous reasoning trace.")


class ProfilerDTO(ReasoningTraceDTO):
    """Profiler DTO (Content Only).

    Attributes:
        author_intent: Assessed intent of the author.
        cognitive_biases: Detected cognitive biases.
        emotional_tone: Emotional tone analysis.
        metrics: Quantitative and behavioral text metrics.
    """

    author_intent: str = Field(
        ...,
        min_length=1,
        description="Assessed intent of the author.",
        json_schema_extra={"x-ui-label": "Author Intent"},
    )
    cognitive_biases: list[str] = Field(
        ...,
        min_length=1,
        description="Detected cognitive biases.",
        json_schema_extra={"x-ui-label": "Cognitive Biases"},
    )
    emotional_tone: str = Field(
        ...,
        min_length=1,
        description="Emotional tone analysis.",
        json_schema_extra={"x-ui-label": "Emotional Tone"},
    )
    metrics: ProfilerMetrics | None = Field(
        default=None,
        description="Quantitative and behavioral text metrics.",
        json_schema_extra={"x-ui-label": "Metrics"},
    )


class ProfilerOutput(ProfilerDTO, ReasoningTrace):
    """Output schema for the Profiler Agent.

    Attributes:
        No additional attributes.
    """
