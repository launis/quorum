"""Metrics Domain Models.

Provides strict Pydantic V2 validation schemas for the metrics hooks
to eliminate legacy dictionary-based parsing and enforce Zero-Compromise protocols.
"""

from __future__ import annotations

import logging
from typing import Annotated, Any, override

from pydantic import ConfigDict, Field, field_validator

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.dtos.inputs import IngressInputValue

logger = logging.getLogger(__name__)

__all__ = [
    "BehavioralMetricsDTO",
    "MetricsPayloadDTO",
    "ProfilerMetricsDTO",
    "TextMetricsDTO",
]


class MetricsPayloadDTO(V2CoreBase):
    """Strict schema for inputs destined for metrics analysis.

    Attributes:
        root: The root dictionary payload.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    root: Annotated[
        dict[str, IngressInputValue | None],
        Field(default_factory=dict, description="The root dictionary payload."),
    ]

    @override
    @classmethod
    def model_validate(
        cls,
        obj: Any,
        *,
        strict: bool | None = None,
        from_attributes: bool | None = None,
        context: Any | None = None,
        by_alias: bool | None = None,
        by_name: bool | None = None,
        extra: Any | None = None,
    ) -> MetricsPayloadDTO:
        """Validate and wrap arbitrary incoming payload into MetricsPayloadDTO.

        Args:
            obj: The object or raw dictionary payload to validate.
            strict: Whether to enforce strict types.
            from_attributes: Whether to extract attributes from objects.
            context: Optional validation context.
            by_alias: Whether to query by alias.
            by_name: Whether to query by name.
            extra: Extra validation configuration.

        Returns:
            Validated MetricsPayloadDTO instance.
        """
        if type(obj) is dict:
            return cls(root=obj)
        return super().model_validate(
            obj,
            strict=strict,
            from_attributes=from_attributes,
            context=context,
            by_alias=by_alias,
            by_name=by_name,
            extra=extra,
        )


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

    word_count: Annotated[int, Field(default=0, description="Number of words.")] = 0
    sentence_count: Annotated[int, Field(default=0, description="Number of sentences.")] = 0
    avg_sentence_length: Annotated[float, Field(default=0.0, description="Average length of a sentence.")] = 0.0
    lexical_diversity: Annotated[float, Field(default=0.0, description="Lexical diversity score.")] = 0.0
    capitalization_ratio: Annotated[float, Field(default=0.0, description="Ratio of capitalized letters.")] = 0.0
    control_ratio: Annotated[float, Field(default=0.0, description="Control ratio score.")] = 0.0

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
            AppException: If value is negative (VALIDATION_FAILED).
        """
        if v < 0:
            msg = f"Text metric must be >= 0, got {v}"
            logger.error("[MetricsModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise AppException(message=msg, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})
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

    say_do_gap: Annotated[float, Field(default=0.0, description="Gap between what is said and done.")] = 0.0
    automation_bias: Annotated[float, Field(default=0.0, description="Bias towards automation.")] = 0.0
    illusion_of_competence: Annotated[float, Field(default=0.0, description="Illusion of competence score.")] = 0.0
    imperative_command_count: Annotated[int, Field(default=0, description="Number of imperative commands.")] = 0

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
            AppException: If value is negative (VALIDATION_FAILED).
        """
        if v < 0:
            msg = f"Behavioral metric must be >= 0, got {v}"
            logger.error("[MetricsModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise AppException(message=msg, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})
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

    word_count: Annotated[int, Field(default=0, description="Total word count.")] = 0
    sentence_count: Annotated[int, Field(default=0, description="Total sentence count.")] = 0
    avg_sentence_length: Annotated[float, Field(default=0.0, description="Average words per sentence.")] = 0.0
    lexical_diversity: Annotated[float, Field(default=0.0, description="Unique words / total words.")] = 0.0
    capitalization_ratio: Annotated[
        float, Field(default=0.0, description="Uppercase characters / total characters.")
    ] = 0.0
    control_ratio: Annotated[float, Field(default=0.0, description="User/AI token ratio.")] = 0.0
    say_do_gap: Annotated[float, Field(default=0.0, description="Discrepancy between intent and action.")] = 0.0
    automation_bias: Annotated[float, Field(default=0.0, description="Over-reliance on AI.")] = 0.0
    illusion_of_competence: Annotated[float, Field(default=0.0, description="False sense of mastery.")] = 0.0
    imperative_command_count: Annotated[int, Field(default=0, description="Number of imperative commands.")] = 0

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
            AppException: If value is negative (VALIDATION_FAILED).
        """
        if v < 0:
            msg = f"Profiler metric must be >= 0, got {v}"
            logger.error("[MetricsModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise AppException(message=msg, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})
        return v
