"""Firestore Implementation of StorageDriver Protocol."""

import logging
import uuid
from typing import Any

from google.cloud import firestore  # type: ignore

from backend.database.driver import Filter, StorageDriver

logger = logging.getLogger(__name__)


class FirestoreDriver(StorageDriver):
    """Firestore adapter for StorageDriver protocol.

    Adapts google.cloud.firestore.AsyncClient.
    """

    def __init__(self, client: firestore.AsyncClient):
        self.db = client

    def _serialize(self, data: dict[str, Any] | list | Any) -> Any:
        """Recursively converts datetime, UUID, and Pydantic objects to JSON-safe types.

        Note: Firestore supports native Datetime, but to maintain strict parity
        with TinyDB (JSON), we often serialize efficiently. However, Firestore querying
        invokes backend index which works best with Native types.

        DECISION: We serialize UUIDs to strings and Pydantic to dicts, but keep
        Datetimes native?

        Re-reading requirements: Parity is key.
        If TinyDB saves ISO strings, and we query with strings, Firestore must save strings?
        Or we convert query values?

        The existing `firestore_repo.py` serialized datetimes to isoformat().
        We will stick to that to ensure string comparison parity.
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

    async def get(self, collection: str, doc_id: str) -> dict[str, Any] | None:
        doc_ref = self.db.collection(collection).document(doc_id)
        doc = await doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return None

    async def upsert(self, collection: str, data: dict[str, Any], doc_id: str) -> str:
        safe_data = self._serialize(data)
        # Ensure ID is in data for parity
        if "id" not in safe_data:
            safe_data["id"] = doc_id

        await self.db.collection(collection).document(doc_id).set(safe_data)
        return doc_id

    async def update(self, collection: str, doc_id: str, updates: dict[str, Any]) -> bool:
        safe_updates = self._serialize(updates)
        doc_ref = self.db.collection(collection).document(doc_id)
        try:
            await doc_ref.update(safe_updates)
            return True
        except Exception as e:
            logger.error(f"Firestore update failed: {e}")
            return False

    async def delete(self, collection: str, doc_id: str) -> bool:
        try:
            await self.db.collection(collection).document(doc_id).delete()
            return True
        except Exception as e:
            logger.error(f"Firestore delete failed: {e}")
            return False

    async def query(
        self,
        collection: str,
        filters: list[Filter] | None = None,
        limit: int | None = None,
        order_by: str | None = None,
        descending: bool = False,
    ) -> list[dict[str, Any]]:
        query = self.db.collection(collection)

        if filters:
            for f in filters:
                # Firestore `where`
                query = query.where(f.field, f.operator, f.value)

        if order_by:
            direction = firestore.Query.DESCENDING if descending else firestore.Query.ASCENDING
            query = query.order_by(order_by, direction=direction)

        if limit:
            query = query.limit(limit)

        docs = await query.stream()
        return [doc.to_dict() async for doc in docs]

    async def count(self, collection: str, filters: list[Filter] | None = None) -> int:
        query = self.db.collection(collection)

        if filters:
            for f in filters:
                query = query.where(f.field, f.operator, f.value)

        try:
            aggregate_query = query.count()
            snapshots = await aggregate_query.get()
            return int(snapshots[0][0].value)
        except Exception:
            # Fallback for older SDKs or emulators?
            docs = await query.stream()
            # len() on async generator doesn't work, need to iterate
            count = 0
            async for _ in docs:
                count += 1
            return count

    async def clear(self, collection: str) -> None:
        """Removes all documents from a collection."""
        collection_ref = self.db.collection(collection)
        # Iterate and delete (No native truncate in Firestore)
        docs = await collection_ref.stream()
        async for doc in docs:
            await doc.reference.delete()
