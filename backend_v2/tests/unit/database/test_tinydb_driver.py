"""Unit tests for TinyDBDriver."""

from datetime import datetime, timezone
from typing import Any
from unittest.mock import MagicMock
import uuid

import pytest
from pydantic import BaseModel, ConfigDict

from backend_v2.database.driver import Filter
from backend_v2.database.tinydb_driver import TinyDBDriver


class SampleModel(BaseModel):
    name: str
    count: int

    model_config = ConfigDict(strict=True, extra="forbid")


def test_storage_drivers_isinstance_base_model() -> None:
    """Test contract 6: Pydantic domain model passed to TinyDB _serialize method serializes via isinstance(data, BaseModel)."""
    mock_db = MagicMock()
    driver = TinyDBDriver(mock_db)

    model = SampleModel(name="TestItem", count=42)
    serialized = driver._serialize(model)
    assert serialized == {"name": "TestItem", "count": 42}


def test_tinydb_driver_serialize_primitives_and_collections() -> None:
    """Test serialization of datetime, UUID, nested dict, and lists."""
    mock_db = MagicMock()
    driver = TinyDBDriver(mock_db)

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


def test_tinydb_driver_apply_filter() -> None:
    """Test in-memory filter evaluations."""
    mock_db = MagicMock()
    driver = TinyDBDriver(mock_db)

    doc: dict[str, Any] = {"score": 50, "tags": ["alpha", "beta"], "name": "item1"}

    assert driver._apply_filter(doc, Filter(field="score", operator="==", value=50)) is True
    assert driver._apply_filter(doc, Filter(field="score", operator="!=", value=50)) is False
    assert driver._apply_filter(doc, Filter(field="score", operator=">", value=40)) is True
    assert driver._apply_filter(doc, Filter(field="score", operator="<", value=60)) is True
    assert driver._apply_filter(doc, Filter(field="score", operator=">=", value=50)) is True
    assert driver._apply_filter(doc, Filter(field="score", operator="<=", value=50)) is True
    assert driver._apply_filter(doc, Filter(field="name", operator="in", value=["item1", "item2"])) is True
    assert driver._apply_filter(doc, Filter(field="tags", operator="array-contains", value="alpha")) is True
    assert driver._apply_filter(doc, Filter(field="tags", operator="array-contains", value="gamma")) is False
    assert driver._apply_filter({"tags": "not_a_list"}, Filter(field="tags", operator="array-contains", value="alpha")) is False
    assert driver._apply_filter(doc, Filter(field="missing", operator=">", value=10)) is False


@pytest.mark.asyncio
async def test_tinydb_driver_crud_operations() -> None:
    """Test get, upsert, update, delete operations on TinyDBDriver."""
    mock_db = MagicMock()
    mock_table = MagicMock()
    mock_db.table.return_value = mock_table

    driver = TinyDBDriver(mock_db)

    # get
    mock_table.get.return_value = {"id": "doc_1", "name": "Item 1"}
    res = await driver.get("items", "doc_1")
    assert res == {"id": "doc_1", "name": "Item 1"}
    mock_table.get.assert_called_once()

    # upsert
    mock_table.reset_mock()
    doc_id = await driver.upsert("items", {"name": "Item 2"}, "doc_2")
    assert doc_id == "doc_2"
    mock_table.upsert.assert_called_once()

    # update
    mock_table.reset_mock()
    mock_table.update.return_value = [1]
    updated = await driver.update("items", "doc_2", {"name": "Updated"})
    assert updated is True

    # delete
    mock_table.reset_mock()
    mock_table.remove.return_value = [1]
    deleted = await driver.delete("items", "doc_2")
    assert deleted is True


@pytest.mark.asyncio
async def test_tinydb_driver_query_count_clear() -> None:
    """Test query, count, and clear operations."""
    mock_db = MagicMock()
    mock_table = MagicMock()
    mock_db.table.return_value = mock_table

    driver = TinyDBDriver(mock_db)

    items = [
        {"id": "1", "score": 10, "name": "B"},
        {"id": "2", "score": 20, "name": "A"},
        {"id": "3", "score": 30, "name": "C"},
    ]
    mock_table.all.return_value = items
    mock_table.count.return_value = 3

    # Query with filter, sort, limit
    f = Filter(field="score", operator=">", value=10)
    res = await driver.query("items", filters=[f], order_by="name", descending=False, limit=1)
    assert len(res) == 1
    assert res[0]["name"] == "A"

    # Query without filters
    res_all = await driver.query("items")
    assert len(res_all) == 3

    # Count without filters
    c_all = await driver.count("items")
    assert c_all == 3

    # Count with filters
    c_filtered = await driver.count("items", filters=[f])
    assert c_filtered == 2

    # Clear
    await driver.clear("items")
    mock_table.truncate.assert_called_once()
