"""Data Transfer Objects for dynamic hook execution and state transit.

Enforces strict Pydantic V2 immutable DTOs (frozen=True, extra="forbid", strict=True)
for HookState inputs, global context variables, and HookResult state deltas.
"""

from typing import Annotated

from pydantic import ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.inputs import DomainInputValue
from backend_v2.models.dtos.global_context import GlobalContextVarsDTO as GlobalContextVarsDTO
from backend_v2.models.dtos.hook_delta import HookDeltaDTO as HookDeltaDTO

__all__ = [
    "ExecutionInputsDTO",
    "GlobalContextVarsDTO",
    "HookDeltaDTO",
]


class ExecutionInputsDTO(V2CoreBase):
    """Strictly typed execution inputs container for hook pipelines."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    raw_inputs: Annotated[
        dict[str, DomainInputValue],
        Field(default_factory=dict, description="Raw input mapping by input key or role."),
    ] = Field(default_factory=dict)
    dynamic_inputs: Annotated[
        dict[str, DomainInputValue],
        Field(default_factory=dict, description="Dynamic input parameters extracted from execution context."),
    ] = Field(default_factory=dict)
    user_role: Annotated[
        str | None,
        Field(default=None, description="Optional user role identifier for role-specific processing."),
    ] = None
    target_locale: Annotated[
        str | None,
        Field(default=None, description="Target locale code for input localization."),
    ] = None
