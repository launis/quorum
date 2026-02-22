"""Storage Driver Protocol (V2.9/V2026).

This module defines the abstract interface for data storage, enforcing the
'Write Logic Once, Swap the Driver' pattern.
"""

from dataclasses import dataclass
from typing import Any, Literal, Protocol

# Supported operators for queries
Operator = Literal["==", "!=", "<", "<=", ">", ">=", "in", "array-contains"]


@dataclass
class Filter:
    """Represents a single query filter condition."""

    field: str
    operator: Operator
    value: Any


class StorageDriver(Protocol):
    """Abstract interface for Database Operations (TinyDB/Firestore)."""

    async def get(self, collection: str, doc_id: str) -> dict[str, Any] | None:
        """Retrieve a document by ID."""
        ...

    async def upsert(self, collection: str, data: dict[str, Any], doc_id: str) -> str:
        """Create or Update a document. Returns the doc_id."""
        ...

    async def update(self, collection: str, doc_id: str, updates: dict[str, Any]) -> bool:
        """Partial update of a document. Returns True if successful."""
        ...

    async def delete(self, collection: str, doc_id: str) -> bool:
        """Delete a document."""
        ...

    async def query(
        self,
        collection: str,
        filters: list[Filter] | None = None,
        limit: int | None = None,
        order_by: str | None = None,
        descending: bool = False,
    ) -> list[dict[str, Any]]:
        """Query a collection with filters, sorting, and limits."""
        ...

    async def count(self, collection: str, filters: list[Filter] | None = None) -> int:
        """Count documents matching the filters."""
        ...

    async def clear(self, collection: str) -> None:
        """Remove all documents from a collection (Truncate)."""
        ...
