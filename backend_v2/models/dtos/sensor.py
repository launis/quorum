"""Sensor validation context DTO for extractive sensor services."""

from __future__ import annotations

from typing import Annotated, Any

from pydantic import ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase

__all__ = ["SensorValidationContextDTO"]


class SensorValidationContextDTO(V2CoreBase):
    """Encapsulates context parameters for sensor evaluation and anchor validation."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    sub_task: Annotated[str, Field(description="Subtask identifier or category")]
    execution_id: Annotated[str | None, Field(default=None, description="Parent execution ID")] = None
    step_id: Annotated[str | None, Field(default=None, description="Current step ID")] = None

    def get(self, key: str, default: Any = None) -> Any:
        """Allow dict-like get method for backwards compatibility."""
        try:
            return self[key]
        except KeyError:
            return default

    def __getitem__(self, key: str) -> Any:
        """Allow subscript access."""
        if hasattr(self, key):
            val = getattr(self, key)
            if val is not None:
                return val
        raise KeyError(key)

    def __contains__(self, key: object) -> bool:
        """Allow membership checks."""
        return isinstance(key, str) and hasattr(self, key) and getattr(self, key) is not None
