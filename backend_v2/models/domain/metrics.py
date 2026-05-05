"""Metrics Domain Models.

Provides strict Pydantic V2 validation schemas for the metrics hooks
to eliminate legacy dictionary-based parsing and enforce Zero-Compromise protocols.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, RootModel


class MetricsPayloadDTO(RootModel[dict[str, Any]]):
    """Strict schema for inputs destined for metrics analysis.

    By utilizing RootModel, we strictly enforce that the incoming state
    payload is explicitly a dictionary before any iterative logic executes,
    satisfying the Phase 9 Zero-Compromise mandate.
    """  # noqa: W293

    model_config = ConfigDict(strict=True, frozen=True)


class TextMetricsDTO(BaseModel):
    """Core text metrics."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    word_count: int = Field(ge=0)
    sentence_count: int = Field(ge=0)
    avg_sentence_length: float = Field(ge=0.0)
    lexical_diversity: float = Field(ge=0.0)
    capitalization_ratio: float = Field(ge=0.0)
    control_ratio: float = Field(ge=0.0)


class BehavioralMetricsDTO(BaseModel):
    """Behavioral heuristics."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    say_do_gap: float = Field(ge=0.0)
    automation_bias: float = Field(ge=0.0)
    illusion_of_competence: float = Field(ge=0.0)
    imperative_command_count: int = Field(ge=0)


class ProfilerMetricsDTO(BaseModel):
    """Combined metrics for profiler state injection."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    word_count: int = Field(ge=0)
    sentence_count: int = Field(ge=0)
    avg_sentence_length: float = Field(ge=0.0)
    lexical_diversity: float = Field(ge=0.0)
    capitalization_ratio: float = Field(ge=0.0)
    control_ratio: float = Field(ge=0.0)
    say_do_gap: float = Field(ge=0.0)
    automation_bias: float = Field(ge=0.0)
    illusion_of_competence: float = Field(ge=0.0)
    imperative_command_count: int = Field(ge=0)
