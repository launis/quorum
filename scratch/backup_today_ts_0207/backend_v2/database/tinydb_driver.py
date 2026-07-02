"""TinyDB Implementation of StorageDriver Protocol."""

import logging
import uuid
from typing import Any

from tinydb import Query

from backend_v2.database.driver import Filter, StorageDriver
from backend_v2.database.wrapper import AbstractDatabase, AbstractTable

logger = logging.getLogger(__name__)


class TinyDBDriver(StorageDriver):
    """TinyDB adapter for StorageDriver protocol.

    Wraps the synchronous AbstractDatabase/AbstractTable interface.
    """

    def __init__(self, db_client: AbstractDatabase):
        self.db = db_client

    def _get_table(self, name: str) -> AbstractTable:
        """Helper to get table instance."""
        return self.db.table(name)

    def _serialize(self, data: dict[str, Any] | list | Any) -> Any:  # type: ignore
        """Recursively converts datetime, UUID, and Pydantic objects to JSON-safe types.

        Args:
            data: The data structure or value to serialize.

        Returns:
            The serialized, JSON-safe data.
        """
        from datetime import datetime

        if hasattr(data, "model_dump"):
            return self._serialize(data.model_dump())

        if isinstance(data, datetime):
            return data.isoformat()

        if isinstance(data, uuid.UUID):
            return str(data)

        if isinstance(data, dict):
            return {k: self._serialize(v) for k, v in data.items()}

        if isinstance(data, list):
            return [self._serialize(v) for v in data]

        return data

    def _apply_filter(self, data: dict[str, Any], f: Filter) -> bool:
        """Apply a single filter in memory (for operators not supported by TinyDB Query).

        Args:
            data: The document data to check.
            f: The filter condition to apply.

        Returns:
            True if the document matches the filter, False otherwise.
        """
        val = data[f.field] if f.field in data else None

        # Determine strict or loose equality? TinyDB is pythonic.
        if f.operator == "==":
            return val == f.value  # type: ignore
        elif f.operator == "!=":
            return val != f.value  # type: ignore

        if val is None:
            return False

        if f.operator == "<":
            return val < f.value  # type: ignore
        elif f.operator == "<=":
            return val <= f.value  # type: ignore
        elif f.operator == ">":
            return val > f.value  # type: ignore
        elif f.operator == ">=":
            return val >= f.value  # type: ignore
        elif f.operator == "in":
            return val in f.value
        elif f.operator == "array-contains":
            if isinstance(val, list):
                return f.value in val
            return False
        return False

    async def get(self, collection: str, doc_id: str) -> dict[str, Any] | None:
        """Retrieve a document by ID.

        Args:
            collection: The name of the collection.
            doc_id: The unique document identifier.

        Returns:
            The document data, or None if not found.

        Raises:
            AppException: If retrieval fails.
        """
        table = self._get_table(collection)
        # Using TinyDB Query
        return table.get(Query().id == doc_id)

    async def upsert(self, collection: str, data: dict[str, Any], doc_id: str) -> str:
        """Create or Update a document.

        Args:
            collection: The name of the collection.
            data: The data to store.
            doc_id: The document identifier.

        Returns:
            The document ID.

        Raises:
            AppException: If upsert fails.
        """
        table = self._get_table(collection)
        safe_data = self._serialize(data)

        # Ensure ID is in data
        if "id" not in safe_data:
            safe_data["id"] = doc_id

        table.upsert(safe_data, Query().id == doc_id)
        return doc_id

    async def update(self, collection: str, doc_id: str, updates: dict[str, Any]) -> bool:
        """Partial update of a document.

        Args:
            collection: The collection name.
            doc_id: The document identifier.
            updates: The updates to apply.

        Returns:
            True if successful, False otherwise.

        Raises:
            AppException: If update fails.
        """
        table = self._get_table(collection)
        safe_updates = self._serialize(updates)

        # TinyDB update returns list of doc_ids
        res = table.update(safe_updates, Query().id == doc_id)
        return len(res) > 0

    async def delete(self, collection: str, doc_id: str) -> bool:
        """Delete a document.

        Args:
            collection: The collection name.
            doc_id: The document identifier to delete.

        Returns:
            True if successfully deleted, False otherwise.

        Raises:
            AppException: If deletion fails.
        """
        table = self._get_table(collection)
        res = table.remove(Query().id == doc_id)
        return bool(res)

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
            collection: The collection name.
            filters: The filters to apply.
            limit: Maximum documents to return.
            order_by: Field to sort by.
            descending: Sort in descending order.

        Returns:
            A list of matching documents.

        Raises:
            AppException: If the query operation fails.
        """
        table = self._get_table(collection)
        docs = table.all()

        # 1. Filter
        filtered_docs = []
        if filters:
            for doc in docs:
                match = True
                for f in filters:
                    if not self._apply_filter(doc, f):
                        match = False
                        break
                if match:
                    filtered_docs.append(doc)
        else:
            filtered_docs = docs

        # 2. Sort
        if order_by:
            filtered_docs.sort(
                key=lambda x: x[order_by] if order_by in x and x[order_by] is not None else "",  # Removed get
                reverse=descending,
            )

        # 3. Limit
        if limit:
            return filtered_docs[:limit]

        return filtered_docs

    async def count(self, collection: str, filters: list[Filter] | None = None) -> int:
        """Count documents matching the filters.

        Args:
            collection: The collection name.
            filters: The filters to apply.

        Returns:
            The total count of matching documents.

        Raises:
            AppException: If count operation fails.
        """
        # Re-use query logic for simplicity since TinyDB loads all in memory anyway
        # Optimization: AbstractTable.count() exists but only takes simple query
        if not filters:
            return self._get_table(collection).count()

        results = await self.query(collection, filters)
        return len(results)

    async def clear(self, collection: str) -> None:
        """Remove all documents from a collection.

        Args:
            collection: The collection name.

        Raises:
            AppException: If clearing fails.
        """
        self._get_table(collection).truncate()
