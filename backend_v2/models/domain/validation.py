"""Validation Domain Models.

Provides strict Pydantic V2 validation schemas for the validation hooks
to eliminate legacy dictionary-based parsing and enforce Zero-Compromise protocols.
"""

from typing import Any

from pydantic import ConfigDict, Field, TypeAdapter

from backend_v2.models.core_base import V2CoreBase

_dict_adapter = TypeAdapter(dict[str, Any])


class ValidationHookPayloadDTO:
    """Strict schema for inputs destined for structural validation.

    By utilizing a TypeAdapter wrapper (RootModel is broken in Python 3.14),
    we strictly enforce that the incoming state payload is explicitly a dictionary
    before any iterative logic executes, satisfying the Phase 9 Zero-Compromise mandate.

    Attributes:
        root: The underlying dictionary representing raw state inputs.
    """

    def __init__(self, root: dict[str, Any]) -> None:
        """Initialize the DTO with the underlying dictionary.

        Args:
            root: The underlying dictionary representing raw state inputs.
        """
        self.root = root

    @classmethod
    def model_validate(cls, data: Any) -> ValidationHookPayloadDTO:
        """Validate using strict Pydantic TypeAdapter.

        Args:
            data: Arbitrary input data to validate as a dictionary.

        Returns:
            A validated ValidationHookPayloadDTO wrapping the dictionary.

        Raises:
            ValidationError: If the input data is not a valid dictionary.
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
        meta: Generic dictionary containing additional contextual metadata.
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
        is_valid: Boolean indicating whether the state passed structural validation.
        errors: List of ValidationWarningDTO issues accumulated during validation.
    """

    is_valid: bool = Field(...)
    errors: list[ValidationWarningDTO] = Field(...)


class HardeningRetryDirectiveDTO(V2CoreBase):
    """Directive to orchestrate dynamic self-correction and retry loops.

    Attributes:
        retry_allowed: Boolean indicating whether a hardening retry is permitted.
        max_retries: Maximum number of retry attempts configured.
        current_retry_count: Current index in the retry loop iteration.
        target_block_ids: List of specific block IDs that failed verification.
        strictness_override: Optional integer override adjusting execution strictness.
        reason: Textual explanation of the logic or math triggering the retry.
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
        system_warnings: List of ValidationWarningDTO captured from the execution state.
    """

    system_warnings: list[ValidationWarningDTO] = Field(default_factory=list, alias="_system_warnings")

    model_config = ConfigDict(frozen=True, extra="ignore", populate_by_name=True)
