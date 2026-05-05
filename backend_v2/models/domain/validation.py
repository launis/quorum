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


class ValidationResultDTO(V2CoreBase):
    """Result payload for structural validation."""

    is_valid: bool = Field(...)
    errors: list[ValidationWarningDTO] = Field(...)


class SystemWarningsStateDTO(V2CoreBase):
    """Strict schema to safely read _system_warnings from state without naked .get() fallbacks."""

    system_warnings: list[ValidationWarningDTO] = Field(default_factory=list, alias="_system_warnings")

    model_config = ConfigDict(frozen=True, extra="ignore", populate_by_name=True)
