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
        """Retrieve a document by ID.

        Args:
            collection: The name of the collection to query.
            doc_id: The unique identifier of the document to retrieve.

        Returns:
            A dictionary containing the document data, or None if not found.

        Raises:
            AppException: If the retrieval operation fails.
        """
        ...

    async def upsert(self, collection: str, data: dict[str, Any], doc_id: str) -> str:
        """Create or Update a document.

        Args:
            collection: The name of the collection.
            data: The data to insert or update.
            doc_id: The unique identifier of the document.

        Returns:
            The document ID.

        Raises:
            AppException: If the upsert operation fails.
        """
        ...

    async def update(self, collection: str, doc_id: str, updates: dict[str, Any]) -> bool:
        """Partial update of a document.

        Args:
            collection: The name of the collection.
            doc_id: The unique identifier of the document to update.
            updates: A dictionary of key-value pairs to update.

        Returns:
            True if successful, False otherwise.

        Raises:
            AppException: If the update operation fails unexpectedly.
        """
        ...

    async def delete(self, collection: str, doc_id: str) -> bool:
        """Delete a document.

        Args:
            collection: The name of the collection.
            doc_id: The unique identifier of the document to delete.

        Returns:
            True if the document was deleted successfully.

        Raises:
            AppException: If the deletion operation fails.
        """
        ...

    async def query(
        self,
        collection: str,
        filters: list[Filter] | None = None,
        limit: int | None = None,
        order_by: str | None = None,
        descending: bool = False,
    ) -> list[dict[str, Any]]:
        """Query a collection with filters, sorting, and limits.

        Args:
            collection: The name of the collection to query.
            filters: An optional list of Filter objects to apply.
            limit: The maximum number of results to return.
            order_by: The field to sort the results by.
            descending: Whether to sort in descending order.

        Returns:
            A list of dictionaries representing the matched documents.

        Raises:
            AppException: If the query operation fails.
        """
        ...

    async def count(self, collection: str, filters: list[Filter] | None = None) -> int:
        """Count documents matching the filters.

        Args:
            collection: The name of the collection.
            filters: An optional list of Filter objects to apply.

        Returns:
            The total number of documents matching the filters.

        Raises:
            AppException: If the count operation fails.
        """
        ...

    async def clear(self, collection: str) -> None:
        """Remove all documents from a collection (Truncate).

        Args:
            collection: The name of the collection to clear.

        Raises:
            AppException: If the clear operation fails.
        """
        ...
