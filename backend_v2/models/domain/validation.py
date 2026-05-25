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
    """  # noqa: W293

    def __init__(self, root: dict[str, Any]) -> None:
        self.root = root

    @classmethod
    def model_validate(cls, data: Any) -> ValidationHookPayloadDTO:
        """Validate using strict Pydantic TypeAdapter."""
        validated = _dict_adapter.validate_python(data)
        return cls(root=validated)


class ValidationWarningDTO(V2CoreBase):
    """Strict schema for RFC 7807 style validation warnings."""

    type: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    error_code: str = Field(..., min_length=1)
    detail: str = Field(..., min_length=1)
    meta: dict[str, Any] = Field(default_factory=dict)
    entropy: float | None = Field(default=None, description="Optional Shannon entropy telemetry score.")
    telemetry_code: str | None = Field(default=None, description="Optional telemetry status or routing code.")


class ValidationResultDTO(V2CoreBase):
    """Result payload for structural validation."""

    is_valid: bool = Field(...)
    errors: list[ValidationWarningDTO] = Field(...)


class HardeningRetryDirectiveDTO(V2CoreBase):
    """Directive to orchestrate dynamic self-correction and retry loops."""

    retry_allowed: bool = Field(..., description="Whether a hardening retry is permitted.")
    max_retries: int = Field(default=3, ge=1, le=5, description="Maximum number of retries.")
    current_retry_count: int = Field(default=0, ge=0, description="Current retry iteration.")
    target_block_ids: list[str] = Field(default_factory=list, description="Target blocks that failed verification.")
    strictness_override: int | None = Field(default=None, ge=0, le=100, description="Optional strictness override.")
    reason: str = Field(..., description="Logical or mathematical reason triggering the retry.")


class SystemWarningsStateDTO(V2CoreBase):
    """Strict schema to safely read _system_warnings from state without naked .get() fallbacks."""

    system_warnings: list[ValidationWarningDTO] = Field(default_factory=list, alias="_system_warnings")

    model_config = ConfigDict(frozen=True, extra="ignore", populate_by_name=True)
