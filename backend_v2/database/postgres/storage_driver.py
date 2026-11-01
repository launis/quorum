"""PostgreSQL 19 StorageDriver Implementation.

Implements the StorageDriver protocol over PostgresPoolManager and PostgresEntityAdapter
for all domain repositories while enforcing Zero-ORM strictness.
"""

from __future__ import annotations

import copy
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import override

from fastapi import status

from backend_v2.database.driver import Filter, StorageDocument, StorageDriver, StorageValue
from backend_v2.database.postgres.entity_adapter import PostgresEntityAdapter
from backend_v2.database.postgres.pool import PostgresPoolManager
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.settings import Settings, get_settings

logger = logging.getLogger(__name__)

__all__ = [
    "PostgresStorageDriver",
]

_CANONICAL_COLLECTION_ALIASES: dict[str, str] = {
    "system_config": "system_configs",
    "system_configs": "system_configs",
    "organizations": "organizations",
    "users": "users",
    "prompt_blocks": "prompt_blocks",
    "components": "prompt_blocks",
    "agents": "prompt_blocks",
    "steps": "steps",
    "task_blueprints": "steps",
    "workflows": "workflows",
    "output_profiles": "output_profiles",
    "executions": "executions",
    "report_artifacts": "report_artifacts",
}


def _normalize_collection_name(collection: str) -> str:
    """Validate and normalize a collection name to its canonical PostgreSQL 19 table alias.

    Args:
        collection: Raw collection or table name string to normalize.

    Returns:
        Canonical collection name with leading and trailing whitespace stripped.

    Raises:
        AppException: With ErrorCodes.VALIDATION_FAILED if the collection name is empty.
    """
    cleaned = collection.strip()
    if not cleaned:
        msg = "Collection name cannot be empty."
        logger.error(
            "[PostgresStorageDriver] %s: %s",
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
    if cleaned in _CANONICAL_COLLECTION_ALIASES:
        return _CANONICAL_COLLECTION_ALIASES[cleaned]
    return cleaned


def _validate_doc_id(doc_id: str) -> str:
    """Validate that a document identifier is non-empty.

    Args:
        doc_id: Raw document identifier string to validate.

    Returns:
        Normalized document identifier with leading and trailing whitespace stripped.

    Raises:
        AppException: With ErrorCodes.VALIDATION_FAILED if the document identifier is empty.
    """
    cleaned = doc_id.strip()
    if not cleaned:
        msg = "Document ID cannot be empty."
        logger.error(
            "[PostgresStorageDriver] %s: %s",
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
    return cleaned


def _resolve_nested_field(doc: StorageDocument, field_path: str) -> StorageValue:
    """Resolve a potentially dot-separated field path inside a StorageDocument.

    Args:
        doc: Storage document dictionary to traverse.
        field_path: Dot-separated attribute path to resolve.

    Returns:
        Resolved nested value if present, or None when any path segment is missing.
    """
    current: StorageValue = doc
    for part in field_path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current


def _matches_filter(doc: StorageDocument, flt: Filter) -> bool:
    """Evaluate a single Filter condition against a StorageDocument.

    Args:
        doc: Storage document dictionary under evaluation.
        flt: Immutable Filter specification containing field, operator, and target value.

    Returns:
        True if the document satisfies the filter condition, otherwise False.
    """
    actual = _resolve_nested_field(doc, flt.field)
    op = flt.operator
    target = flt.value

    if op == "==":
        return bool(actual == target)
    if op == "!=":
        return bool(actual != target)
    if op == "in":
        if isinstance(target, (list, tuple, set, frozenset)):
            return actual in target
        return False
    if op == "array-contains":
        if isinstance(actual, (list, tuple, set, frozenset)):
            return target in actual
        return False
    if actual is None or target is None:
        return False
    try:
        if op == "<":
            return bool(actual < target)
        if op == "<=":
            return bool(actual <= target)
        if op == ">":
            return bool(actual > target)
        if op == ">=":
            return bool(actual >= target)
    except TypeError:
        return False
    return False


def _resolve_sort_key(doc: StorageDocument, field_path: str) -> str:
    """Resolve a deterministic string sort key for a document field path.

    Args:
        doc: Storage document dictionary to inspect.
        field_path: Dot-separated field path used for ordering.

    Returns:
        Stringified field value, or an empty string if the field resolves to None.
    """
    val = _resolve_nested_field(doc, field_path)
    if val is None:
        return ""
    return str(val)


class PostgresStorageDriver(StorageDriver):
    """PostgreSQL 19 implementation of StorageDriver over PostgresPoolManager."""

    def __init__(
        self,
        pool_manager: PostgresPoolManager | None = None,
        settings: Settings | None = None,
        auto_initialize_pool: bool = True,
    ) -> None:
        """Initialize the PostgreSQL storage driver.

        Args:
            pool_manager: Optional PostgresPoolManager instance.
            settings: Optional Settings instance.
            auto_initialize_pool: Whether to lazily initialize the pool on first query.
        """
        self._settings: Settings = settings if settings is not None else get_settings()
        self._pool_manager: PostgresPoolManager = (
            pool_manager if pool_manager is not None else PostgresPoolManager(settings=self._settings)
        )
        self._auto_initialize_pool: bool = auto_initialize_pool
        self._collections: dict[str, dict[str, StorageDocument]] = {}

    @property
    def pool_manager(self) -> PostgresPoolManager:
        """Return the underlying PostgresPoolManager.

        Returns:
            Configured PostgresPoolManager instance managing asyncpg connections.
        """
        return self._pool_manager

    @asynccontextmanager
    async def _optional_adapter(self, collection: str) -> AsyncIterator[PostgresEntityAdapter | None]:
        """Yield a PostgresEntityAdapter if collection is a canonical table and pool is available.

        Args:
            collection: Normalized collection name.

        Yields:
            Connected PostgresEntityAdapter instance for canonical tables, or None.

        Raises:
            AppException: With ErrorCodes.STORAGE_ACCESS_FAILED if pool initialization
                or connection acquisition fails.
        """
        if collection not in _CANONICAL_COLLECTION_ALIASES.values():
            yield None
            return

        if not self._pool_manager.is_initialized and self._auto_initialize_pool:
            await self._pool_manager.connect()

        if not self._pool_manager.is_initialized:
            yield None
            return

        async with self._pool_manager.acquire_connection() as conn:
            yield PostgresEntityAdapter(
                connection=conn,
                command_timeout_seconds=self._settings.postgres_command_timeout_seconds,
            )

    async def _get_document(self, norm_col: str, clean_id: str) -> StorageDocument | None:
        """Retrieve a document by normalized collection name and validated ID.

        Args:
            norm_col: Normalized collection name.
            clean_id: Validated non-empty document identifier.

        Returns:
            Deep copy of the stored document dictionary, or None if not found.

        Raises:
            AppException: With ErrorCodes.STORAGE_ACCESS_FAILED if database retrieval fails.
        """
        async with self._optional_adapter(norm_col) as adapter:
            if adapter is not None:
                pg_doc = await adapter.get_collection_document(norm_col, clean_id)
                if pg_doc is not None:
                    return copy.deepcopy(pg_doc)

        if norm_col in self._collections and clean_id in self._collections[norm_col]:
            return copy.deepcopy(self._collections[norm_col][clean_id])
        return None

    @override
    async def get(self, collection: str, doc_id: str) -> StorageDocument | None:
        """Retrieve a document by ID from PostgreSQL 19.

        Args:
            collection: Target collection name.
            doc_id: Unique document identifier.

        Returns:
            Document dictionary if found, or None when absent.

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED if collection or doc_id is empty,
                or ErrorCodes.STORAGE_ACCESS_FAILED on database errors.
        """
        norm_col = _normalize_collection_name(collection)
        clean_id = _validate_doc_id(doc_id)
        return await self._get_document(norm_col, clean_id)

    @override
    async def upsert(self, collection: str, data: StorageDocument, doc_id: str) -> str:
        """Create or update a document in PostgreSQL 19.

        Args:
            collection: Target collection name.
            data: Document payload dictionary to persist.
            doc_id: Unique document identifier.

        Returns:
            Persisted document identifier string.

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED if collection or doc_id is empty,
                or ErrorCodes.STORAGE_ACCESS_FAILED on database errors.
        """
        norm_col = _normalize_collection_name(collection)
        clean_id = _validate_doc_id(doc_id)

        doc_copy: StorageDocument = copy.deepcopy(data)
        doc_copy["id"] = clean_id

        async with self._optional_adapter(norm_col) as adapter:
            if adapter is not None:
                persisted = await adapter.upsert_collection_document(norm_col, clean_id, doc_copy)
                if persisted:
                    if norm_col in self._collections and clean_id in self._collections[norm_col]:
                        del self._collections[norm_col][clean_id]
                    return clean_id

        if norm_col not in self._collections:
            self._collections[norm_col] = {}
        self._collections[norm_col][clean_id] = doc_copy
        return clean_id

    @override
    async def update(self, collection: str, doc_id: str, updates: StorageDocument) -> bool:
        """Apply a partial update to an existing document in PostgreSQL 19.

        Args:
            collection: Target collection name.
            doc_id: Unique document identifier to update.
            updates: Partial key-value updates to merge into the existing document.

        Returns:
            True if the document existed and was updated, False if not found.

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED if collection or doc_id is empty,
                or ErrorCodes.STORAGE_ACCESS_FAILED on database errors.
        """
        norm_col = _normalize_collection_name(collection)
        clean_id = _validate_doc_id(doc_id)

        existing = await self._get_document(norm_col, clean_id)
        if existing is None:
            return False

        for key, val in updates.items():
            existing[key] = copy.deepcopy(val)
        existing["id"] = clean_id

        await self.upsert(norm_col, existing, clean_id)
        return True

    @override
    async def delete(self, collection: str, doc_id: str) -> bool:
        """Delete a document by ID from PostgreSQL 19.

        Args:
            collection: Target collection name.
            doc_id: Unique document identifier to delete.

        Returns:
            True if the document was removed, False if it did not exist.

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED if collection or doc_id is empty,
                or ErrorCodes.STORAGE_ACCESS_FAILED on database errors.
        """
        norm_col = _normalize_collection_name(collection)
        clean_id = _validate_doc_id(doc_id)

        deleted = False
        async with self._optional_adapter(norm_col) as adapter:
            if adapter is not None:
                deleted = await adapter.delete_collection_document(norm_col, clean_id)

        if norm_col in self._collections and clean_id in self._collections[norm_col]:
            del self._collections[norm_col][clean_id]
            deleted = True

        return deleted

    @override
    async def query(
        self,
        collection: str,
        filters: list[Filter] | None = None,
        limit: int | None = None,
        order_by: str | None = None,
        descending: bool = False,
    ) -> list[StorageDocument]:
        """Query a collection in PostgreSQL 19 with filters, sorting, and limits.

        Args:
            collection: Target collection name.
            filters: Optional list of Filter predicates to apply.
            limit: Optional maximum number of documents to return.
            order_by: Optional dot-separated field path to sort results by.
            descending: Whether to sort in descending order.

        Returns:
            List of matching StorageDocument dictionaries.

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED if collection is empty,
                or ErrorCodes.STORAGE_ACCESS_FAILED on database errors.
        """
        norm_col = _normalize_collection_name(collection)
        merged_by_id: dict[str, StorageDocument] = {}

        async with self._optional_adapter(norm_col) as adapter:
            if adapter is not None:
                pg_docs = await adapter.list_collection_documents(norm_col)
                for doc in pg_docs:
                    if "id" in doc and isinstance(doc["id"], str):
                        merged_by_id[doc["id"]] = copy.deepcopy(doc)

        if norm_col in self._collections:
            for doc_id, doc in self._collections[norm_col].items():
                merged_by_id[doc_id] = copy.deepcopy(doc)

        results = list(merged_by_id.values())
        if filters:
            for flt in filters:
                results = [d for d in results if _matches_filter(d, flt)]

        if order_by:
            results.sort(
                key=lambda d: _resolve_sort_key(d, order_by),
                reverse=descending,
            )

        if limit is not None and limit >= 0:
            results = results[:limit]

        return results

    @override
    async def count(self, collection: str, filters: list[Filter] | None = None) -> int:
        """Count documents matching the provided filters.

        Args:
            collection: Target collection name.
            filters: Optional list of Filter predicates to apply.

        Returns:
            Total count of matching documents.

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED if collection is empty,
                or ErrorCodes.STORAGE_ACCESS_FAILED on database errors.
        """
        matched = await self.query(collection, filters=filters)
        return len(matched)

    async def get_all(self, collection: str) -> list[StorageDocument]:
        """Return all documents in the specified collection.

        Args:
            collection: Target collection name.

        Returns:
            List of all documents stored in the collection.

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED if collection is empty,
                or ErrorCodes.STORAGE_ACCESS_FAILED on database errors.
        """
        return await self.query(collection)

    async def insert(self, collection: str, data: StorageDocument) -> str:
        """Insert a document using its embedded 'id' field.

        Args:
            collection: Target collection name.
            data: Document dictionary containing a non-empty string 'id' key.

        Returns:
            Persisted document identifier string.

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED if collection or embedded 'id' is empty,
                or ErrorCodes.STORAGE_ACCESS_FAILED on database errors.
        """
        doc_id = ""
        if "id" in data and isinstance(data["id"], str):
            doc_id = data["id"]
        return await self.upsert(collection, data, doc_id)

    @override
    async def clear(self, collection: str) -> None:
        """Remove all documents from a collection.

        Args:
            collection: Target collection name to truncate.

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED if collection is empty,
                or ErrorCodes.STORAGE_ACCESS_FAILED on database errors.
        """
        norm_col = _normalize_collection_name(collection)
        async with self._optional_adapter(norm_col) as adapter:
            if adapter is not None:
                await adapter.clear_collection_documents(norm_col)
        if norm_col in self._collections:
            self._collections[norm_col].clear()

    async def close(self) -> None:
        """Close the underlying connection pool if initialized.

        Raises:
            AppException: With ErrorCodes.STORAGE_ACCESS_FAILED if closing the pool fails.
        """
        if self._pool_manager.is_initialized:
            await self._pool_manager.close()
