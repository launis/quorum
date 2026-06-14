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

    Attributes:
        root: The root dictionary payload.
    """

    def __init__(self, root: dict[str, Any]) -> None:
        """Initialize the payload wrapper.

        Args:
            root: The root dictionary containing payload data.
        """
        self.root = root

    @classmethod
    def model_validate(cls, data: Any) -> MetricsPayloadDTO:
        """Validate using strict Pydantic TypeAdapter.

        Args:
            data: The incoming data to validate.

        Returns:
            A validated MetricsPayloadDTO instance.

        Raises:
            ValidationError: If validation fails.
        """
        validated = _dict_adapter.validate_python(data)
        return cls(root=validated)


class TextMetricsDTO(BaseModel):
    """Core text metrics.

    Attributes:
        word_count: Number of words.
        sentence_count: Number of sentences.
        avg_sentence_length: Average length of a sentence.
        lexical_diversity: Lexical diversity score.
        capitalization_ratio: Ratio of capitalized letters.
        control_ratio: Control ratio score.
    """

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    word_count: int = Field(ge=0)
    sentence_count: int = Field(ge=0)
    avg_sentence_length: float = Field(ge=0.0)
    lexical_diversity: float = Field(ge=0.0)
    capitalization_ratio: float = Field(ge=0.0)
    control_ratio: float = Field(ge=0.0)


class BehavioralMetricsDTO(BaseModel):
    """Behavioral heuristics.

    Attributes:
        say_do_gap: Gap between what is said and done.
        automation_bias: Bias towards automation.
        illusion_of_competence: Illusion of competence score.
        imperative_command_count: Number of imperative commands.
    """

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    say_do_gap: float = Field(ge=0.0)
    automation_bias: float = Field(ge=0.0)
    illusion_of_competence: float = Field(ge=0.0)
    imperative_command_count: int = Field(ge=0)


class ProfilerMetricsDTO(BaseModel):
    """Combined metrics for profiler state injection.

    Attributes:
        word_count: Total word count.
        sentence_count: Total sentence count.
        avg_sentence_length: Average words per sentence.
        lexical_diversity: Unique words / total words.
        capitalization_ratio: Uppercase characters / total characters.
        control_ratio: User/AI token ratio.
        say_do_gap: Discrepancy between intent and action.
        automation_bias: Over-reliance on AI.
        illusion_of_competence: False sense of mastery.
        imperative_command_count: Number of imperative commands.
    """

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
