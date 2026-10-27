"""Unit and ISTQB Negative Boundary Tests for StorageDriver and Filter."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from typing import cast

import pytest

from backend_v2.database.driver import (
    Filter,
    Operator,
    StorageDocument,
    StorageDriver,
)
from backend_v2.exceptions import AppException, ErrorCodes


def test_filter_creation() -> None:
    """Verify valid Filter instantiation and immutable attribute access."""
    flt = Filter(field="test", operator="==", value=1)
    assert flt.field == "test"
    assert flt.operator == "=="
    assert flt.value == 1


def test_filter_immutability_rejects_mutation() -> None:
    """Verify frozen Filter instance raises FrozenInstanceError on attribute deletion."""
    flt = Filter(field="status", operator="==", value="completed")
    with pytest.raises(FrozenInstanceError):
        flt.__delattr__("field")


@pytest.mark.parametrize("invalid_field", ["", "   ", "\t\n"])
def test_filter_empty_field_raises_app_exception(invalid_field: str) -> None:
    """Verify empty or whitespace-only field raises AppException with VALIDATION_FAILED."""
    with pytest.raises(AppException) as exc_info:
        Filter(field=invalid_field, operator="==", value="val")
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


def test_filter_invalid_operator_raises_app_exception() -> None:
    """Verify unsupported query operator raises AppException with VALIDATION_FAILED."""
    invalid_op = cast(Operator, "LIKE")
    with pytest.raises(AppException) as exc_info:
        Filter(field="status", operator=invalid_op, value="active")
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_storage_driver_abstract() -> None:
    """Verify StorageDriver protocol conformance across all CRUD and query methods."""

    class DummyDriver(StorageDriver):
        """In-memory protocol implementation for contract verification."""

        async def get(self, collection: str, doc_id: str) -> StorageDocument | None:
            """Retrieve a document by ID."""
            return {"id": doc_id, "collection": collection}

        async def upsert(self, collection: str, data: StorageDocument, doc_id: str) -> str:
            """Create or update a document."""
            return doc_id

        async def update(self, collection: str, doc_id: str, updates: StorageDocument) -> bool:
            """Partial update of a document."""
            return bool(updates)

        async def delete(self, collection: str, doc_id: str) -> bool:
            """Delete a document."""
            return bool(collection and doc_id)

        async def query(
            self,
            collection: str,
            filters: list[Filter] | None = None,
            limit: int | None = None,
            order_by: str | None = None,
            descending: bool = False,
        ) -> list[StorageDocument]:
            """Query a collection with filters, sorting, and limits."""
            return [{"id": "doc_1", "collection": collection}] if not filters else []

        async def count(self, collection: str, filters: list[Filter] | None = None) -> int:
            """Count documents matching the filters."""
            return 0 if filters else 1

        async def clear(self, collection: str) -> None:
            """Remove all documents from a collection."""
            return None

    driver = DummyDriver()
    assert await driver.get("workflows", "wor_1234567890abcdef") == {
        "id": "wor_1234567890abcdef",
        "collection": "workflows",
    }
    assert await driver.upsert("workflows", {"name": "wf"}, "wor_1234567890abcdef") == "wor_1234567890abcdef"
    assert await driver.update("workflows", "wor_1234567890abcdef", {"name": "wf2"}) is True
    assert await driver.delete("workflows", "wor_1234567890abcdef") is True
    assert len(await driver.query("workflows")) == 1
    assert await driver.count("workflows", filters=[Filter("name", "==", "wf")]) == 0
    await driver.clear("workflows")
