"""Tests for Storage Driver Pattern."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.database.driver import Filter, StorageDriver
from backend.database.firestore_driver import FirestoreDriver
from backend.database.tinydb_driver import TinyDBDriver
from backend.database.wrapper import TinyDBClient

# --- TinyDB Tests ---

@pytest.fixture
def mock_tinydb_client(tmp_path):
    """Fixture for a real temporary TinyDB."""
    db_path = tmp_path / "test_db.json"
    return TinyDBClient(str(db_path))

@pytest.fixture
def tinydb_driver(mock_tinydb_client):
    return TinyDBDriver(mock_tinydb_client)

@pytest.mark.asyncio
async def test_tinydb_crud(tinydb_driver):
    """Test Create, Read, Update, Delete for TinyDBDriver."""
    collection = "test_col"
    doc_id = "doc1"
    data = {"name": "Test Item", "value": 42}

    # Create (Upsert)
    res_id = await tinydb_driver.upsert(collection, data, doc_id)
    assert res_id == doc_id

    # Read
    doc = await tinydb_driver.get(collection, doc_id)
    assert doc is not None
    assert doc["name"] == "Test Item"
    assert doc["id"] == doc_id

    # Update
    success = await tinydb_driver.update(collection, doc_id, {"value": 100})
    assert success is True

    doc = await tinydb_driver.get(collection, doc_id)
    assert doc["value"] == 100

    # Delete
    success = await tinydb_driver.delete(collection, doc_id)
    assert success is True

    doc = await tinydb_driver.get(collection, doc_id)
    assert doc is None

@pytest.mark.asyncio
async def test_tinydb_query(tinydb_driver):
    """Test Querying with Filters."""
    collection = "items"
    items = [
        {"id": "1", "type": "A", "score": 10},
        {"id": "2", "type": "B", "score": 20},
        {"id": "3", "type": "A", "score": 30},
    ]
    for item in items:
        await tinydb_driver.upsert(collection, item, item["id"])

    # Filter: type == "A"
    results = await tinydb_driver.query(collection, [Filter("type", "==", "A")])
    assert len(results) == 2
    assert all(r["type"] == "A" for r in results)

    # Filter: score > 15
    results = await tinydb_driver.query(collection, [Filter("score", ">", 15)])
    assert len(results) == 2

    # Sort
    results = await tinydb_driver.query(collection, order_by="score", descending=True)
    assert results[0]["id"] == "3"
    assert results[1]["id"] == "2"
    assert results[2]["id"] == "1"

# --- Firestore Tests (Mocked) ---

@pytest.fixture
def mock_firestore_client():
    client = AsyncMock()
    # Mock collection().document().set() chain
    # collection() is SYNC returning a CollectionReference
    client.collection = MagicMock()

    # document() is SYNC returning a DocumentReference
    doc_ref_mock = MagicMock()
    client.collection.return_value.document.return_value = doc_ref_mock

    # set(), get(), update(), delete() are ASYNC methods on DocumentReference
    doc_ref_mock.set = AsyncMock()
    doc_ref_mock.get = AsyncMock()
    doc_ref_mock.update = AsyncMock()
    doc_ref_mock.delete = AsyncMock()

    return client

@pytest.mark.asyncio
async def test_firestore_upsert(mock_firestore_client):
    driver = FirestoreDriver(mock_firestore_client)
    collection = "test_col"
    doc_id = "doc1"
    data = {"name": "Firestore Item"}

    await driver.upsert(collection, data, doc_id)

    # Verify calls
    mock_firestore_client.collection.assert_called_with(collection)
    mock_firestore_client.collection.return_value.document.assert_called_with(doc_id)
    # Check set call
    # Note: async mocks need await or assert_awaited_with
    # But initialization of AsyncMock typically handles the coroutine property
    mock_firestore_client.collection.return_value.document.return_value.set.assert_called_once()
    args, _ = mock_firestore_client.collection.return_value.document.return_value.set.call_args
    assert args[0]["name"] == "Firestore Item"
    assert args[0]["id"] == doc_id # ID injection parity

@pytest.mark.asyncio
async def test_firestore_get(mock_firestore_client):
    driver = FirestoreDriver(mock_firestore_client)

    # Mock return value
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {"id": "doc1", "val": "test"}

    mock_get = mock_firestore_client.collection.return_value.document.return_value.get
    mock_get.return_value = mock_doc

    res = await driver.get("col", "doc1")
    assert res["val"] == "test"

# --- Serialization Parity Tests ---

def test_tinydb_serialization(tinydb_driver):
    data = {
        "date": datetime(2023, 1, 1, 12, 0, 0),
        "nested": {"date2": datetime(2023, 1, 2)}
    }
    serialized = tinydb_driver._serialize(data)
    assert isinstance(serialized["date"], str)
    assert "2023-01-01" in serialized["date"]

def test_firestore_serialization(mock_firestore_client):
    driver = FirestoreDriver(mock_firestore_client)
    data = {
        "date": datetime(2023, 1, 1, 12, 0, 0)
    }
    # Per implementation, we convert to ISO string for parity
    serialized = driver._serialize(data)
    assert isinstance(serialized["date"], str)

# --- Repository Integration (Mocked Driver) ---

from backend.database.repository import UnifiedWorkflowRepository


@pytest.mark.asyncio
async def test_repo_delegation():
    """Test that Repository properly delegates to Driver."""
    mock_driver = AsyncMock(spec=StorageDriver)
    repo = UnifiedWorkflowRepository(mock_driver)

    # Test get_execution
    mock_driver.get.return_value = {"id": "ex1", "status": "running"}
    res = await repo.get_execution("ex1")

    assert res["id"] == "ex1"
    mock_driver.get.assert_called_with("executions", "ex1")

    # Test create_execution
    await repo.create_execution({"user_id": "u1"})
    mock_driver.upsert.assert_called_once()
    call_args = mock_driver.upsert.call_args
    assert call_args[0][0] == "executions" # collection
    assert "id" in call_args[0][1] # generated ID
