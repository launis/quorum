"""Data Transfer Object for injected theory manifest."""

from __future__ import annotations

from typing import Annotated

from pydantic import ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase

__all__ = ["InjectedTheoryManifestDTO"]


class InjectedTheoryManifestDTO(V2CoreBase):
    """Immutable manifest for injected theory texts in execution context.

    Attributes:
        theories: Mapping of theory or block IDs to retrieved theory content.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    theories: Annotated[
        dict[str, str],
        Field(default_factory=dict, description="Mapping of theory or block IDs to retrieved theory content"),
    ] = Field(default_factory=dict)
