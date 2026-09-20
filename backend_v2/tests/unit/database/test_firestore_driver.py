"""Unit tests for FirestoreDriver."""

from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock
import uuid

import pytest
from pydantic import BaseModel, ConfigDict

from backend_v2.database.driver import Filter
from backend_v2.database.firestore_driver import FirestoreDriver


class SampleModel(BaseModel):
    name: str
    count: int

    model_config = ConfigDict(strict=True, extra="forbid")


def test_storage_drivers_isinstance_base_model() -> None:
    """Test contract 6: Pydantic domain model passed to Firestore _serialize method serializes via isinstance(data, BaseModel)."""
    mock_client = MagicMock()
    driver = FirestoreDriver(mock_client)

    model = SampleModel(name="TestItem", count=42)
    serialized = driver._serialize(model)
    assert serialized == {"name": "TestItem", "count": 42}


def test_firestore_driver_serialize_primitives_and_collections() -> None:
    """Test serialization of datetime, UUID, nested dict, and lists."""
    mock_client = MagicMock()
    driver = FirestoreDriver(mock_client)

    test_uuid = uuid.uuid4()
    now = datetime.now(timezone.utc)
    nested = {
        "id": test_uuid,
        "created_at": now,
        "items": [SampleModel(name="A", count=1)],
        "count": 10,
    }

    serialized = driver._serialize(nested)
    assert serialized["id"] == str(test_uuid)
    assert serialized["created_at"] == now.isoformat()
    assert serialized["items"] == [{"name": "A", "count": 1}]
    assert serialized["count"] == 10


@pytest.mark.asyncio
async def test_firestore_driver_crud_operations() -> None:
    """Test get, upsert, update, delete operations on FirestoreDriver."""
    mock_client = MagicMock()
    mock_col = MagicMock()
    mock_doc = MagicMock()

    mock_client.collection.return_value = mock_col
    mock_col.document.return_value = mock_doc

    driver = FirestoreDriver(mock_client)

    # get
    mock_snapshot = MagicMock()
    mock_snapshot.exists = True
    mock_snapshot.to_dict.return_value = {"id": "doc_1", "name": "Item 1"}
    mock_doc.get = AsyncMock(return_value=mock_snapshot)

    res = await driver.get("items", "doc_1")
    assert res == {"id": "doc_1", "name": "Item 1"}
    mock_doc.get.assert_awaited_once()

    # upsert
    mock_doc.set = AsyncMock()
    doc_id = await driver.upsert("items", {"name": "Item 2"}, "doc_2")
    assert doc_id == "doc_2"
    mock_doc.set.assert_awaited_once()

    # update
    mock_doc.update = AsyncMock()
    updated = await driver.update("items", "doc_2", {"name": "Updated"})
    assert updated is True
    mock_doc.update.assert_awaited_once()

    # delete
    mock_doc.delete = AsyncMock()
    deleted = await driver.delete("items", "doc_2")
    assert deleted is True
    mock_doc.delete.assert_awaited_once()


@pytest.mark.asyncio
async def test_firestore_driver_query_count_clear() -> None:
    """Test query, count, and clear operations on FirestoreDriver."""
    mock_client = MagicMock()
    mock_col = MagicMock()
    mock_query = MagicMock()

    mock_client.collection.return_value = mock_col
    mock_col.where.return_value = mock_query
    mock_query.where.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.limit.return_value = mock_query

    # Mock async generator for stream
    doc1 = MagicMock()
    doc1.to_dict.return_value = {"id": "1", "score": 10}
    doc1.reference.delete = AsyncMock()

    async def async_stream() -> Any:
        yield doc1

    mock_query.stream = async_stream
    mock_col.stream = async_stream

    driver = FirestoreDriver(mock_client)

    # 1. Query with filter, sort, limit
    f = Filter(field="score", operator=">", value=5)
    results = await driver.query("items", filters=[f], limit=5, order_by="score", descending=True)
    assert len(results) == 1
    assert results[0]["id"] == "1"

    # 2. Count with aggregate query
    mock_agg = MagicMock()
    mock_val = MagicMock()
    mock_val.value = 42
    mock_agg.get = AsyncMock(return_value=[[mock_val]])
    mock_col.count.return_value = mock_agg

    count_res = await driver.count("items")
    assert count_res == 42

    # 3. Clear
    await driver.clear("items")
    doc1.reference.delete.assert_awaited_once()


@pytest.mark.asyncio
async def test_firestore_driver_get_nonexistent_returns_none() -> None:
    """Test get returns None when document does not exist."""
    mock_client = MagicMock()
    mock_col = MagicMock()
    mock_doc = MagicMock()

    mock_client.collection.return_value = mock_col
    mock_col.document.return_value = mock_doc

    mock_snapshot = MagicMock()
    mock_snapshot.exists = False
    mock_doc.get = AsyncMock(return_value=mock_snapshot)

    driver = FirestoreDriver(mock_client)
    res = await driver.get("items", "doc_nonexistent")
    assert res is None


@pytest.mark.asyncio
async def test_firestore_driver_update_and_delete_failure_raises_app_exception() -> None:
    """Test update and delete raise AppException on underlying driver errors."""
    from backend_v2.exceptions import AppException

    mock_client = MagicMock()
    mock_col = MagicMock()
    mock_doc = MagicMock()

    mock_client.collection.return_value = mock_col
    mock_col.document.return_value = mock_doc

    mock_doc.update = AsyncMock(side_effect=RuntimeError("Firestore connection failed"))
    mock_doc.delete = AsyncMock(side_effect=RuntimeError("Firestore delete failed"))

    driver = FirestoreDriver(mock_client)

    with pytest.raises(AppException) as exc_info:
        await driver.update("items", "doc_1", {"key": "val"})
    assert "Firestore update failed" in str(exc_info.value)
    assert exc_info.value.status_code == 500

    with pytest.raises(AppException) as exc_info_del:
        await driver.delete("items", "doc_1")
    assert "Firestore delete failed" in str(exc_info_del.value)
    assert exc_info_del.value.status_code == 500


@pytest.mark.asyncio
async def test_firestore_driver_count_with_filter_and_stream_fallback() -> None:
    """Test count with filters and fallback when aggregate query fails."""
    mock_client = MagicMock()
    mock_col = MagicMock()
    mock_query = MagicMock()

    mock_client.collection.return_value = mock_col
    mock_col.where.return_value = mock_query

    # Aggregate query fails, triggering fallback to stream iteration
    mock_query.count.return_value.get = AsyncMock(side_effect=RuntimeError("Aggregate query unsupported"))

    doc1 = MagicMock()
    doc2 = MagicMock()

    async def async_stream() -> Any:
        yield doc1
        yield doc2

    mock_query.stream = async_stream

    driver = FirestoreDriver(mock_client)
    f = Filter(field="status", operator="==", value="active")
    count = await driver.count("items", filters=[f])

    assert count == 2
    mock_col.where.assert_called_once_with("status", "==", "active")
