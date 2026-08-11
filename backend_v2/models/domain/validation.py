"""Validation Domain Models.

Provides strict Pydantic V2 validation schemas for the validation hooks
to eliminate legacy dictionary-based parsing and enforce Zero-Compromise protocols.
"""

import logging
from typing import Annotated, Any

from pydantic import ConfigDict, Field, TypeAdapter, field_validator

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import V2CoreBase

logger = logging.getLogger(__name__)

_dict_adapter = TypeAdapter(dict[str, Any])


class ValidationHookPayloadDTO:
    """Strict schema for inputs destined for structural validation.

    By utilizing a TypeAdapter wrapper (RootModel is broken in Python 3.14),
    we strictly enforce that the incoming state payload is explicitly a dictionary
    before any iterative logic executes, satisfying the Phase 9 Zero-Compromise mandate.

    Attributes:
        root: Raw state inputs.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    def __init__(self, root: dict[str, Any]) -> None:
        """Initialize the DTO with the underlying dictionary.

        Args:
            root: Raw state inputs.
        """
        self.root = root

    @classmethod
    def model_validate(cls, data: Any) -> ValidationHookPayloadDTO:
        """Validate using strict Pydantic TypeAdapter.

        Args:
            data: Arbitrary input data to validate.

        Returns:
            A validated ValidationHookPayloadDTO.

        Raises:
            ValidationError: If validation fails.
        """
        validated = _dict_adapter.validate_python(data)
        return cls(root=validated)


class ValidationWarningDTO(V2CoreBase):
    """Strict schema for RFC 7807 style validation warnings.

    Attributes:
        type: URI reference identifying the error type.
        title: Short human-readable summary of the problem type.
        error_code: Application-specific error identifier.
        detail: Human-readable explanation specific to this occurrence of the problem.
        meta: Additional contextual metadata.
        entropy: Shannon entropy telemetry score.
        telemetry_code: Telemetry status or routing code.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    type: Annotated[str, Field(min_length=1, description="URI reference identifying the error type.")]
    title: Annotated[str, Field(min_length=1, description="Short human-readable summary.")]
    error_code: Annotated[str, Field(min_length=1, description="Application-specific error identifier.")]
    detail: Annotated[str, Field(min_length=1, description="Human-readable explanation specific to this occurrence.")]
    meta: Annotated[dict[str, Any], Field(description="Additional contextual metadata.")] = Field(default_factory=dict)
    entropy: Annotated[float | None, Field(description="Shannon entropy telemetry score.")] = None
    telemetry_code: Annotated[str | None, Field(description="Telemetry status or routing code.")] = None


class ValidationResultDTO(V2CoreBase):
    """Result payload for structural validation.

    Attributes:
        is_valid: Whether the state passed structural validation.
        errors: Issues accumulated during validation.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    is_valid: Annotated[bool, Field(description="Whether the state passed structural validation.")]
    errors: Annotated[list[ValidationWarningDTO], Field(description="Issues accumulated during validation.")]


class HardeningRetryDirectiveDTO(V2CoreBase):
    """Directive to orchestrate dynamic self-correction and retry loops.

    Attributes:
        retry_allowed: Whether a hardening retry is permitted.
        max_retries: Maximum retry attempts configured.
        current_retry_count: Current retry loop iteration.
        target_block_ids: Specific block IDs that failed verification.
        strictness_override: Override adjusting execution strictness.
        reason: Explanation of logic or math triggering the retry.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    retry_allowed: Annotated[bool, Field(description="Whether a hardening retry is permitted.")]
    max_retries: Annotated[int, Field(description="Maximum number of retries.")] = 3
    current_retry_count: Annotated[int, Field(description="Current retry iteration.")] = 0
    target_block_ids: Annotated[list[str], Field(description="Target blocks that failed verification.")] = Field(
        default_factory=list
    )
    strictness_override: Annotated[int | None, Field(description="Optional strictness override.")] = None
    reason: Annotated[str, Field(description="Explanation of logic or math triggering the retry.")]

    @field_validator("max_retries", mode="before")
    @classmethod
    def validate_max_retries(cls, v: int) -> int:
        if v < 1 or v > 5:
            msg = "max_retries must be between 1 and 5"
            logger.error("[HardeningRetryDirectiveDTO] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, details={"error_code": ErrorCodes.VALIDATION_FAILED})
        return v

    @field_validator("current_retry_count", mode="before")
    @classmethod
    def validate_current_retry_count(cls, v: int) -> int:
        if v < 0:
            msg = "current_retry_count must be non-negative"
            logger.error("[HardeningRetryDirectiveDTO] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, details={"error_code": ErrorCodes.VALIDATION_FAILED})
        return v

    @field_validator("strictness_override", mode="before")
    @classmethod
    def validate_strictness_override(cls, v: int | None) -> int | None:
        if v is not None and (v < 0 or v > 100):
            msg = "strictness_override must be between 0 and 100"
            logger.error("[HardeningRetryDirectiveDTO] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, details={"error_code": ErrorCodes.VALIDATION_FAILED})
        return v


class SystemWarningsStateDTO(V2CoreBase):
    """Strict schema to safely read _system_warnings from state without naked .get() fallbacks.

    Attributes:
        system_warnings: Validation warnings captured from the execution state.
    """

    system_warnings: Annotated[
        list[ValidationWarningDTO],
        Field(alias="_system_warnings", description="Validation warnings captured from the execution state."),
    ] = Field(default_factory=list)

    model_config = ConfigDict(frozen=True, populate_by_name=True, strict=True, extra="ignore")
