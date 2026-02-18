"""TinyDB Implementation of StorageDriver Protocol."""

import logging
import uuid
from typing import Any

from tinydb import Query

from backend.database.driver import Filter, StorageDriver
from backend.database.wrapper import AbstractDatabase, AbstractTable

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

    def _serialize(self, data: dict[str, Any] | list | Any) -> Any:
        """Recursively converts datetime, UUID, and Pydantic objects to JSON-safe types."""
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
        """Apply a single filter in memory (for operators not supported by TinyDB Query)."""
        val = data.get(f.field)

        # Determine strict or loose equality? TinyDB is pythonic.
        if f.operator == "==":
            return val == f.value
        elif f.operator == "!=":
            return val != f.value
        elif f.operator == "<":
            return val < f.value
        elif f.operator == "<=":
            return val <= f.value
        elif f.operator == ">":
            return val > f.value
        elif f.operator == ">=":
            return val >= f.value
        elif f.operator == "in":
            return val in f.value
        elif f.operator == "array-contains":
            if isinstance(val, list):
                return f.value in val
            return False
        return False

    async def get(self, collection: str, doc_id: str) -> dict[str, Any] | None:
        table = self._get_table(collection)
        # Using TinyDB Query
        return table.get(Query().id == doc_id)

    async def upsert(self, collection: str, data: dict[str, Any], doc_id: str) -> str:
        table = self._get_table(collection)
        safe_data = self._serialize(data)

        # Ensure ID is in data
        if "id" not in safe_data:
            safe_data["id"] = doc_id

        table.upsert(safe_data, Query().id == doc_id)
        return doc_id

    async def update(self, collection: str, doc_id: str, updates: dict[str, Any]) -> bool:
        table = self._get_table(collection)
        safe_updates = self._serialize(updates)

        # TinyDB update returns list of doc_ids
        res = table.update(safe_updates, Query().id == doc_id)
        return len(res) > 0

    async def delete(self, collection: str, doc_id: str) -> bool:
        table = self._get_table(collection)
        res = table.remove(Query().id == doc_id)
        return bool(res)

    async def query(
        self,
        collection: str,
        filters: list[Filter] | None = None,
        limit: int | None = None,
        order_by: str | None = None,
        descending: bool = False
    ) -> list[dict[str, Any]]:
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
                key=lambda x: x.get(order_by) or "", # Safe get
                reverse=descending
            )

        # 3. Limit
        if limit:
            return filtered_docs[:limit]

        return filtered_docs

    async def count(self, collection: str, filters: list[Filter] | None = None) -> int:
        # Re-use query logic for simplicity since TinyDB loads all in memory anyway
        # Optimization: AbstractTable.count() exists but only takes simple query
        if not filters:
            return self._get_table(collection).count()

        results = await self.query(collection, filters)
        return len(results)

    async def clear(self, collection: str) -> None:
        self._get_table(collection).truncate()
