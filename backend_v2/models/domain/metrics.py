"""Metrics Domain Models.

Provides strict Pydantic V2 validation schemas for the metrics hooks
to eliminate legacy dictionary-based parsing and enforce Zero-Compromise protocols.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

_dict_adapter = TypeAdapter(dict[str, Any])


class MetricsPayloadDTO:
    """Strict schema for inputs destined for metrics analysis.

    By utilizing a TypeAdapter wrapper (RootModel is broken in Python 3.14),
    we strictly enforce that the incoming state payload is explicitly a dictionary
    before any iterative logic executes, satisfying the Phase 9 Zero-Compromise mandate.
    """

    def __init__(self, root: dict[str, Any]) -> None:
        self.root = root

    @classmethod
    def model_validate(cls, data: Any) -> MetricsPayloadDTO:
        """Validate using strict Pydantic TypeAdapter."""
        validated = _dict_adapter.validate_python(data)
        return cls(root=validated)


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
