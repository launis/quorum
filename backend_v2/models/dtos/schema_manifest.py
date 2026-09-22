"""Data Transfer Object for generated schema manifest."""

from __future__ import annotations

from collections.abc import ItemsView, KeysView, ValuesView
from typing import Annotated

from pydantic import ConfigDict, Field, JsonValue

from backend_v2.models.core_base import V2CoreBase

__all__ = ["GeneratedSchemaManifestDTO"]


class GeneratedSchemaManifestDTO(V2CoreBase):
    """Immutable manifest for JSON schemas generated and utilized during DAG execution.

    Attributes:
        schemas: Mapping of step IDs to serialized JSON schema structures.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    schemas: Annotated[
        dict[str, JsonValue],
        Field(default_factory=dict, description="Mapping of step IDs to schema definitions"),
    ] = Field(default_factory=dict)

    def __contains__(self, key: str) -> bool:
        """Check if a step or schema ID exists in the manifest.

        Args:
            key: Step or schema identifier.

        Returns:
            True if key is present, False otherwise.
        """
        return key in self.schemas

    def __getitem__(self, key: str) -> JsonValue:
        """Retrieve schema definition by step or schema ID.

        Args:
            key: Step or schema identifier.

        Returns:
            Schema definition object or dictionary.
        """
        return self.schemas[key]

    def __len__(self) -> int:
        """Return number of schemas in manifest.

        Returns:
            Count of stored schemas.
        """
        return len(self.schemas)

    def keys(self) -> KeysView[str]:
        """Return schema keys.

        Returns:
            KeysView of stored schema keys.
        """
        return self.schemas.keys()

    def items(self) -> ItemsView[str, JsonValue]:
        """Return schema items.

        Returns:
            ItemsView of stored schema key-value pairs.
        """
        return self.schemas.items()

    def values(self) -> ValuesView[JsonValue]:
        """Return schema values.

        Returns:
            ValuesView of stored schema definitions.
        """
        return self.schemas.values()
