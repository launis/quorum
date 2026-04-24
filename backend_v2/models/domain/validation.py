"""Validation Domain Models.

Provides strict Pydantic V2 validation schemas for the validation hooks
to eliminate legacy dictionary-based parsing and enforce Zero-Compromise protocols.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, RootModel


class ValidationHookPayloadDTO(RootModel[dict[str, Any]]):
    """Strict schema for inputs destined for structural validation.

    By utilizing RootModel, we strictly enforce that the incoming state
    payload is explicitly a dictionary before any iterative logic executes,
    satisfying the Phase 9 Zero-Compromise mandate.
    """  # noqa: W293

    model_config = ConfigDict(frozen=True)


class ValidationWarningDTO(BaseModel):
    """Strict schema for RFC 7807 style validation warnings."""

    type: str
    title: str
    error_code: str
    detail: str
    meta: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(frozen=True)


class ValidationResultDTO(BaseModel):
    """Result payload for structural validation."""

    is_valid: bool
    errors: list[ValidationWarningDTO]

    model_config = ConfigDict(frozen=True)


class SystemWarningsStateDTO(BaseModel):
    """Strict schema to safely read _system_warnings from state without naked .get() fallbacks."""

    system_warnings: list[ValidationWarningDTO] = Field(default_factory=list, alias="_system_warnings")

    model_config = ConfigDict(frozen=True, extra="ignore", populate_by_name=True)
