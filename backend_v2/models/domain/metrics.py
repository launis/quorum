"""Metrics Domain Models.

Provides strict Pydantic V2 validation schemas for the metrics hooks
to eliminate legacy dictionary-based parsing and enforce Zero-Compromise protocols.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, RootModel


class MetricsPayloadDTO(RootModel[dict[str, Any]]):
    """Strict schema for inputs destined for metrics analysis.

    By utilizing RootModel, we strictly enforce that the incoming state
    payload is explicitly a dictionary before any iterative logic executes,
    satisfying the Phase 9 Zero-Compromise mandate.
    """  # noqa: W293

    model_config = ConfigDict(frozen=True)


class TextMetricsDTO(BaseModel):
    """Core text metrics."""

    model_config = ConfigDict(frozen=True)

    word_count: int
    sentence_count: int
    avg_sentence_length: float
    lexical_diversity: float
    capitalization_ratio: float
    control_ratio: float


class BehavioralMetricsDTO(BaseModel):
    """Behavioral heuristics."""

    model_config = ConfigDict(frozen=True)

    say_do_gap: float
    automation_bias: float
    illusion_of_competence: float
    imperative_command_count: int


class ProfilerMetricsDTO(BaseModel):
    """Combined metrics for profiler state injection."""

    model_config = ConfigDict(frozen=True)

    word_count: int
    sentence_count: int
    avg_sentence_length: float
    lexical_diversity: float
    capitalization_ratio: float
    control_ratio: float
    say_do_gap: float
    automation_bias: float
    illusion_of_competence: float
    imperative_command_count: int
