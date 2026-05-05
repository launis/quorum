"""Profiler Agent Domain Models.

This module contains the schemas for the Profiler Agent,
including intent analysis and text metrics.
"""

from __future__ import annotations

import logging

from pydantic import Field

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.base import ReasoningTrace, ReasoningTraceDTO

logger = logging.getLogger(__name__)


class ProfilerInput(V2CoreBase):
    """Strict input schema for ProfilerAgent.

    V2 Dynamic: 'chatlog' is mandatory, but other inputs are allowed dynamically.
    """

    chat_log: str = Field(
        ...,
        min_length=1,
        description="The mandatory conversation history.",
        json_schema_extra={"x-ui-label": "Chatlog"},
    )
    profiler_metrics: ProfilerMetrics | None = Field(None, description="Injected text metrics.")
    last_reasoning_trace: str | None = Field(default=None, description="Previous reasoning trace.")


class TextMetrics(V2CoreBase):
    """Metrics for text analysis."""

    word_count: int = Field(..., ge=0, description="Total word count.", json_schema_extra={"x-ui-label": "Word Count"})
    sentence_count: int = Field(
        ..., ge=0, description="Total sentence count.", json_schema_extra={"x-ui-label": "Sentence Count"}
    )
    avg_sentence_length: float = Field(
        ..., ge=0.0, description="Average words per sentence.", json_schema_extra={"x-ui-label": "Avg Sentence Length"}
    )
    lexical_diversity: float = Field(
        ..., ge=0.0, description="Unique words / total words.", json_schema_extra={"x-ui-label": "Lexical Diversity"}
    )
    capitalization_ratio: float = Field(
        ...,
        ge=0.0,
        description="Uppercase chars / total chars.",
        json_schema_extra={"x-ui-label": "Capitalization Ratio"},
    )
    control_ratio: float = Field(
        default=0.0, ge=0.0, description="User/AI token ratio.", json_schema_extra={"x-ui-label": "Control Ratio"}
    )


class BehavioralMetrics(V2CoreBase):
    """Heuristic behavioral metrics."""

    say_do_gap: float = Field(
        default=0.0,
        ge=0.0,
        description="Discrepancy between intent and action.",
        json_schema_extra={"x-ui-label": "Say-Do Gap"},
    )
    automation_bias: float = Field(
        default=0.0, ge=0.0, description="Over-reliance on AI.", json_schema_extra={"x-ui-label": "Automation Bias"}
    )
    illusion_of_competence: float = Field(
        default=0.0,
        ge=0.0,
        description="False sense of mastery.",
        json_schema_extra={"x-ui-label": "Illusion of Competence"},
    )
    imperative_command_count: int = Field(
        ...,
        ge=0,
        description="Number of imperative commands.",
        json_schema_extra={"x-ui-label": "Command Count"},
    )


class ProfilerMetrics(TextMetrics, BehavioralMetrics):
    """Combined quantitative and behavioral metrics for the Profiler."""


class ProfilerDTO(ReasoningTraceDTO):
    """Profiler DTO (Content Only)."""

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
    """Output schema for the Profiler Agent."""
