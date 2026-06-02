"""Validation Domain Models.

Provides strict Pydantic V2 validation schemas for the validation hooks
to eliminate legacy dictionary-based parsing and enforce Zero-Compromise protocols.
"""

from typing import Any

from pydantic import ConfigDict, Field, RootModel

from backend_v2.models.core_base import V2CoreBase


class ValidationHookPayloadDTO(RootModel[dict[str, Any]]):
    """Strict schema for inputs destined for structural validation.

    By utilizing a TypeAdapter wrapper, we strictly enforce that the
    incoming state payload is explicitly a dictionary before any iterative
    logic executes, satisfying the Phase 9 Zero-Compromise mandate.
    """

    root: dict[str, Any]


def model_validate(payload: Any) -> dict[str, Any]:
    """Validate payload."""
    return ValidationHookPayloadDTO.model_validate(payload).root


class ValidationWarningDTO(V2CoreBase):
    """Strict schema for RFC 7807 style validation warnings.

    Attributes:
        type: URI identifying the error type.
        title: Human-readable category title.
        error_code: Strict machine-readable error key.
        detail: Context-specific technical assessment detail.
        meta: Additional metadata dictionary payload.
        entropy: Optional Shannon entropy telemetry score.
        telemetry_code: Optional telemetry status or routing code.
    """

    type: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    error_code: str = Field(..., min_length=1)
    detail: str = Field(..., min_length=1)
    meta: dict[str, Any] = Field(default_factory=dict)
    entropy: float | None = Field(default=None, description="Optional Shannon entropy telemetry score.")
    telemetry_code: str | None = Field(default=None, description="Optional telemetry status or routing code.")


class ValidationResultDTO(V2CoreBase):
    """Result payload for structural validation.

    Attributes:
        is_valid: Boolean indicating validation outcome correctness.
        errors: List of structured ValidationWarningDTO components.
    """

    is_valid: bool = Field(...)
    errors: list[ValidationWarningDTO] = Field(...)


class HardeningRetryDirectiveDTO(V2CoreBase):
    """Directive to orchestrate dynamic self-correction and retry loops.

    Attributes:
        retry_allowed: Whether a hardening retry is permitted.
        max_retries: Maximum number of retries allowable under concurrency limits.
        current_retry_count: Current retry iteration tracking index.
        target_block_ids: List of specific structural blocks that failed validation.
        strictness_override: Optional override strictness score threshold value.
        reason: Cognitive analysis explanation for triggering self-healing loop.
    """

    retry_allowed: bool = Field(..., description="Whether a hardening retry is permitted.")
    max_retries: int = Field(default=3, ge=1, le=5, description="Maximum number of retries.")
    current_retry_count: int = Field(default=0, ge=0, description="Current retry iteration.")
    target_block_ids: list[str] = Field(default_factory=list, description="Target blocks that failed verification.")
    strictness_override: int | None = Field(default=None, ge=0, le=100, description="Optional strictness override.")
    reason: str = Field(..., description="Logical or mathematical reason triggering the retry.")


class SystemWarningsStateDTO(V2CoreBase):
    """Strict schema to safely read _system_warnings from state without naked .get() fallbacks.

    Attributes:
        system_warnings: Extracted sequence of validated system warning DTO objects.
    """

    system_warnings: list[ValidationWarningDTO] = Field(default_factory=list, alias="_system_warnings")

    model_config = ConfigDict(frozen=True, extra="ignore", populate_by_name=True)
