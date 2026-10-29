"""Prompt compilation and LLM context DTOs."""

from __future__ import annotations

import datetime
from collections.abc import ItemsView, KeysView, Mapping, ValuesView
from typing import Annotated

from pydantic import ConfigDict, Field, JsonValue

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.inputs import DomainInputValue, IngressInputValue
from backend_v2.models.execution_core import ExecutionMetadata

__all__ = [
    "ContextInputValue",
    "LLMContextDataDTO",
    "PromptMappingDTO",
]

type ContextInputValue = IngressInputValue | DomainInputValue | Mapping[str, DomainInputValue] | JsonValue


class PromptMappingDTO(V2CoreBase):
    """Encapsulates input mappings from logical names to state paths.

    Attributes:
        mappings: Map of logical input names to state paths.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    mappings: Annotated[
        dict[str, str],
        Field(default_factory=dict, description="Map of logical input names to state paths"),
    ]

    def __getitem__(self, key: str) -> str:
        """Retrieve a mapped state path by logical input key.

        Args:
            key: Logical input name to look up.

        Returns:
            Mapped state path string.

        Raises:
            KeyError: If the logical input key does not exist in mappings.
        """
        return self.mappings[key]

    def __contains__(self, key: object) -> bool:
        """Check whether a logical input key exists in mappings.

        Args:
            key: Key object to test for membership.

        Returns:
            True if the key exists in inner mappings, False otherwise.
        """
        return key in self.mappings

    def keys(self) -> KeysView[str]:
        """Return a view of logical input mapping keys.

        Returns:
            View of mapping keys.
        """
        return self.mappings.keys()

    def values(self) -> ValuesView[str]:
        """Return a view of mapped state path values.

        Returns:
            View of mapping values.
        """
        return self.mappings.values()

    def items(self) -> ItemsView[str, str]:
        """Return a view of logical input key and state path pairs.

        Returns:
            View of mapping key-value items.
        """
        return self.mappings.items()


class LLMContextDataDTO(V2CoreBase):
    """Strictly typed LLM execution context data container.

    Attributes:
        raw_inputs: Raw ingress input parameters.
        metadata: Execution runtime metadata.
        execution_time: Execution timestamp.
        inputs: Resolved domain inputs.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    raw_inputs: Annotated[
        dict[str, ContextInputValue] | None,
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
        dict[str, ContextInputValue] | None,
        Field(default=None, description="Resolved domain inputs."),
    ] = None

    def __getitem__(
        self, key: str
    ) -> ContextInputValue | dict[str, ContextInputValue] | ExecutionMetadata | datetime.datetime | None:
        """Retrieve a resolved input, raw input, or context attribute by key.

        Args:
            key: Input key or context attribute name to look up.

        Returns:
            Resolved context value or top-level context attribute.

        Raises:
            KeyError: If the key is not present in inputs, raw_inputs, or attributes.
        """
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
        if key == "execution_time":
            return self.execution_time
        raise KeyError(key)

    def __contains__(self, key: object) -> bool:
        """Check whether a key exists in context inputs or top-level attributes.

        Args:
            key: Key object to test for membership.

        Returns:
            True if the key resolves in inputs, raw_inputs, or top-level attributes.
        """
        if not isinstance(key, str):
            return False
        if self.inputs is not None and key in self.inputs:
            return True
        if self.raw_inputs is not None and key in self.raw_inputs:
            return True
        return key in ("inputs", "raw_inputs", "metadata", "execution_time")
