"""Metrics Domain Models.

Provides strict Pydantic V2 validation schemas for the metrics hooks
to eliminate legacy dictionary-based parsing and enforce Zero-Compromise protocols.
"""

import logging
from typing import Any

from pydantic import ConfigDict, TypeAdapter, field_validator

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import V2CoreBase

logger = logging.getLogger(__name__)

_dict_adapter = TypeAdapter(dict[str, Any])


class MetricsPayloadDTO:
    """Strict schema for inputs destined for metrics analysis.

    By utilizing a TypeAdapter wrapper (RootModel is broken in Python 3.14),
    we strictly enforce that the incoming state payload is explicitly a dictionary
    before any iterative logic executes, satisfying the Phase 9 Zero-Compromise mandate.

    Attributes:
        root: The root dictionary payload.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

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


class TextMetricsDTO(V2CoreBase):
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

    word_count: int = 0
    sentence_count: int = 0
    avg_sentence_length: float = 0.0
    lexical_diversity: float = 0.0
    capitalization_ratio: float = 0.0
    control_ratio: float = 0.0

    @field_validator(
        "word_count",
        "sentence_count",
        "avg_sentence_length",
        "lexical_diversity",
        "capitalization_ratio",
        "control_ratio",
    )
    @classmethod
    def validate_non_negative(cls, v: int | float) -> int | float:
        """Enforce non-negative limits locally to bypass Vertex AI constraint errors.

        Args:
            v: The numeric value.

        Returns:
            The validated non-negative value.

        Raises:
            AppException: If value is negative.
        """
        if v < 0:
            msg = f"Text metric must be >= 0, got {v}"
            logger.error("[MetricsModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, details={"error_code": ErrorCodes.VALIDATION_FAILED})
        return v


class BehavioralMetricsDTO(V2CoreBase):
    """Behavioral heuristics.

    Attributes:
        say_do_gap: Gap between what is said and done.
        automation_bias: Bias towards automation.
        illusion_of_competence: Illusion of competence score.
        imperative_command_count: Number of imperative commands.
    """

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    say_do_gap: float = 0.0
    automation_bias: float = 0.0
    illusion_of_competence: float = 0.0
    imperative_command_count: int = 0

    @field_validator(
        "say_do_gap",
        "automation_bias",
        "illusion_of_competence",
        "imperative_command_count",
    )
    @classmethod
    def validate_non_negative(cls, v: int | float) -> int | float:
        """Enforce non-negative limits locally to bypass Vertex AI constraint errors.

        Args:
            v: The numeric value.

        Returns:
            The validated non-negative value.

        Raises:
            AppException: If value is negative.
        """
        if v < 0:
            msg = f"Behavioral metric must be >= 0, got {v}"
            logger.error("[MetricsModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, details={"error_code": ErrorCodes.VALIDATION_FAILED})
        return v


class ProfilerMetricsDTO(V2CoreBase):
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

    word_count: int = 0
    sentence_count: int = 0
    avg_sentence_length: float = 0.0
    lexical_diversity: float = 0.0
    capitalization_ratio: float = 0.0
    control_ratio: float = 0.0
    say_do_gap: float = 0.0
    automation_bias: float = 0.0
    illusion_of_competence: float = 0.0
    imperative_command_count: int = 0

    @field_validator(
        "word_count",
        "sentence_count",
        "avg_sentence_length",
        "lexical_diversity",
        "capitalization_ratio",
        "control_ratio",
        "say_do_gap",
        "automation_bias",
        "illusion_of_competence",
        "imperative_command_count",
    )
    @classmethod
    def validate_non_negative(cls, v: int | float) -> int | float:
        """Enforce non-negative limits locally to bypass Vertex AI constraint errors.

        Args:
            v: The numeric value.

        Returns:
            The validated non-negative value.

        Raises:
            AppException: If value is negative.
        """
        if v < 0:
            msg = f"Profiler metric must be >= 0, got {v}"
            logger.error("[MetricsModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, details={"error_code": ErrorCodes.VALIDATION_FAILED})
        return v
