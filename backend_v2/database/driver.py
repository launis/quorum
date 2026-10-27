"""Storage Driver Protocol (V2.9/V2026).

This module defines the abstract interface for data storage, enforcing the
'Write Logic Once, Swap the Driver' pattern over PostgreSQL 19.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Final, Literal, Protocol

from fastapi import status

from backend_v2.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)

__all__ = [
    "Filter",
    "Operator",
    "StorageDocument",
    "StorageDriver",
    "StorageValue",
]

# Supported operators for queries
type Operator = Literal["==", "!=", "<", "<=", ">", ">=", "in", "array-contains"]
type StorageValue = Any
type StorageDocument = dict[str, StorageValue]

_VALID_OPERATORS: Final[frozenset[str]] = frozenset({"==", "!=", "<", "<=", ">", ">=", "in", "array-contains"})


@dataclass(frozen=True)
class Filter:
    """Represents a single immutable query filter condition.

    Attributes:
        field: Document field path to evaluate.
        operator: Comparison operator from Operator literal set.
        value: Target comparison value.
    """

    field: str
    operator: Operator
    value: StorageValue

    def __post_init__(self) -> None:
        """Validate filter field and operator invariants.

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED if field is empty
                or operator is not in the supported operator set.
        """
        if not self.field.strip():
            msg = "Filter field name cannot be empty."
            logger.error(
                "[Filter] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
        if self.operator not in _VALID_OPERATORS:
            msg = f"Unsupported filter operator: '{self.operator}'."
            logger.error(
                "[Filter] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )


class StorageDriver(Protocol):
    """Abstract interface for Database Operations (PostgreSQL 19)."""

    async def get(self, collection: str, doc_id: str) -> StorageDocument | None:
        """Retrieve a document by ID.

        Args:
            collection: The name of the collection to query.
            doc_id: The unique identifier of the document to retrieve.

        Returns:
            A dictionary containing the document data, or None if not found.

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED or ErrorCodes.DATABASE_ERROR
                if the retrieval operation fails.
        """
        ...

    async def upsert(self, collection: str, data: StorageDocument, doc_id: str) -> str:
        """Create or Update a document.

        Args:
            collection: The name of the collection.
            data: The data to insert or update.
            doc_id: The unique identifier of the document.

        Returns:
            The document ID.

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED or ErrorCodes.DATABASE_ERROR
                if the upsert operation fails.
        """
        ...

    async def update(self, collection: str, doc_id: str, updates: StorageDocument) -> bool:
        """Partial update of a document.

        Args:
            collection: The name of the collection.
            doc_id: The unique identifier of the document to update.
            updates: A dictionary of key-value pairs to update.

        Returns:
            True if successful, False otherwise.

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED or ErrorCodes.DATABASE_ERROR
                if the update operation fails unexpectedly.
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
            AppException: With ErrorCodes.VALIDATION_FAILED or ErrorCodes.DATABASE_ERROR
                if the deletion operation fails.
        """
        ...

    async def query(
        self,
        collection: str,
        filters: list[Filter] | None = None,
        limit: int | None = None,
        order_by: str | None = None,
        descending: bool = False,
    ) -> list[StorageDocument]:
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
            AppException: With ErrorCodes.VALIDATION_FAILED or ErrorCodes.DATABASE_ERROR
                if the query operation fails.
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
            AppException: With ErrorCodes.VALIDATION_FAILED or ErrorCodes.DATABASE_ERROR
                if the count operation fails.
        """
        ...

    async def clear(self, collection: str) -> None:
        """Remove all documents from a collection (Truncate).

        Args:
            collection: The name of the collection to clear.

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED or ErrorCodes.DATABASE_ERROR
                if the clear operation fails.
        """
        ...
