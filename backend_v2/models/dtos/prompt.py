"""Prompt compilation and LLM context DTOs."""

from __future__ import annotations

import datetime
from typing import Annotated, Any

from pydantic import ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.inputs import DomainInputValue, IngressInputValue
from backend_v2.models.execution_core import ExecutionMetadata

from collections.abc import ItemsView, Iterator, KeysView, ValuesView

__all__ = [
    "LLMContextDataDTO",
    "PromptMappingDTO",
]


class PromptMappingDTO(V2CoreBase):
    """Encapsulates input mappings from logical names to state paths."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    mappings: Annotated[
        dict[str, str],
        Field(default_factory=dict, description="Map of logical input names to state paths"),
    ] = Field(default_factory=dict)

    def __getitem__(self, key: str) -> str:
        """Allow subscript access to inner mappings."""
        return self.mappings[key]

    def __contains__(self, key: object) -> bool:
        """Allow membership check against inner mappings."""
        return key in self.mappings

    def __iter__(self) -> Iterator[str]:  # type: ignore[override]
        """Allow iteration over mapping keys."""
        return iter(self.mappings)

    def keys(self) -> KeysView[str]:
        """Return view of mapping keys."""
        return self.mappings.keys()

    def values(self) -> ValuesView[str]:
        """Return view of mapping values."""
        return self.mappings.values()

    def items(self) -> ItemsView[str, str]:
        """Return view of mapping key-value items."""
        return self.mappings.items()


class LLMContextDataDTO(V2CoreBase):
    """Strictly typed LLM execution context data container."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    raw_inputs: Annotated[
        dict[str, IngressInputValue | DomainInputValue] | None,
        Field(default=None, description="Raw ingress input parameters."),
    ] = None
    metadata: Annotated[
        ExecutionMetadata | None,
        Field(default=None, description="Execution runtime metadata."),
    ] = None
    execution_time: Annotated[
        datetime.datetime | None,
        Field(default=None, description="Execution timestamp."),
    ] = None
    inputs: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Resolved domain inputs."),
    ] = None

    def __getitem__(self, key: str) -> Any:
        """Allow subscript access for seamless transition."""
        if self.inputs is not None and key in self.inputs:
            return self.inputs[key]
        if self.raw_inputs is not None and key in self.raw_inputs:
            return self.raw_inputs[key]
        if key == "inputs":
            return self.inputs
        if key == "raw_inputs":
            return self.raw_inputs
        if key == "metadata":
            return self.metadata
        raise KeyError(key)

    def __contains__(self, key: object) -> bool:
        """Allow membership check for seamless transition."""
        if not isinstance(key, str):
            return False
        if self.inputs is not None and key in self.inputs:
            return True
        if self.raw_inputs is not None and key in self.raw_inputs:
            return True
        return key in ("inputs", "raw_inputs", "metadata", "execution_time")
