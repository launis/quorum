"""Data Transfer Objects for dynamic hook execution and state transit.

Enforces strict Pydantic V2 immutable DTOs (frozen=True, extra="forbid", strict=True)
for HookState inputs, global context variables, and HookResult state deltas.
"""

from typing import Annotated, Any

from pydantic import ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase

__all__ = [
    "ExecutionInputsDTO",
    "GlobalContextVarsDTO",
    "HookDeltaDTO",
]


class ExecutionInputsDTO(V2CoreBase):
    """Strictly typed execution inputs container for hook pipelines."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    raw_inputs: Annotated[
        dict[str, Any],
        Field(description="Raw input mapping by input key or role."),
    ] = Field(default_factory=dict)
    dynamic_inputs: Annotated[
        dict[str, Any],
        Field(description="Dynamic input parameters extracted from execution context."),
    ] = Field(default_factory=dict)
    user_role: Annotated[
        str | None,
        Field(default=None, description="Optional user role identifier for role-specific processing."),
    ] = None
    target_locale: Annotated[
        str | None,
        Field(default=None, description="Target locale code for input localization."),
    ] = None


class GlobalContextVarsDTO(V2CoreBase):
    """Strictly typed global context variables container."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    vars: Annotated[
        dict[str, Any],
        Field(description="Global context variables dictionary."),
    ] = Field(default_factory=dict)


class HookDeltaDTO(V2CoreBase):
    """Strict state delta container returned by hooks for state reduction."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    delta: Annotated[
        dict[str, Any],
        Field(description="State delta payload to merge into execution context."),
    ] = Field(default_factory=dict)
    metadata_updates: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Optional metadata updates to merge into ExecutionMetadata."),
    ] = None
