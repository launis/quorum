"""Unit tests for backend_v2.database.wrapper."""

import os
import time
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from tinydb import Query

from backend_v2.database.wrapper import (
    AtomicJSONStorage,
    FirestoreClient,
    FirestoreTable,
    TinyDBClient,
    TinyDBTable,
    db_lock,
    get_db_client,
)
from backend_v2.exceptions import AppException, ErrorCodes


def test_atomic_json_storage_read_and_write(tmp_path: Any) -> None:
    """Test AtomicJSONStorage roundtrip write and read."""
    file_path = str(tmp_path / "test_db.json")
    storage = AtomicJSONStorage(file_path)

    # Empty file read returns None
    assert storage.read() is None

    # Write and read
    payload = {"_default": {"1": {"name": "test_item", "score": 95}}}
    storage.write(payload)

    read_back = storage.read()
    assert read_back == payload

    storage.close()


def test_atomic_json_storage_retry_on_permission_error(tmp_path: Any) -> None:
    """Test that AtomicJSONStorage retries on PermissionError during os.replace."""
    file_path = str(tmp_path / "locked_db.json")
    storage = AtomicJSONStorage(file_path)

    payload = {"_default": {"1": {"key": "val"}}}

    call_count = 0
    real_replace = os.replace

    def mock_replace(src: str, dst: str) -> None:
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise PermissionError("[WinError 32] The process cannot access the file")
        real_replace(src, dst)

    with patch("os.replace", side_effect=mock_replace):
        storage.write(payload)

    assert call_count == 3
    assert storage.read() == payload
    storage.close()


def test_atomic_json_storage_exhausted_retries_raises_and_cleans_up(tmp_path: Any) -> None:
    """Test that exhausted retries raise PermissionError and clean up temporary file."""
    file_path = str(tmp_path / "perm_db.json")
    storage = AtomicJSONStorage(file_path)

    payload = {"_default": {"1": {"key": "fail"}}}

    with patch("os.replace", side_effect=PermissionError("Locked")):
        with pytest.raises(PermissionError):
            storage.write(payload)

    # Verify no orphan .tmp files left
    tmp_files = [f for f in os.listdir(tmp_path) if f.endswith(".tmp")]
    assert len(tmp_files) == 0
    storage.close()


def test_atomic_json_storage_os_error_during_write_cleans_up(tmp_path: Any) -> None:
    """Test that unexpected OSError during write cleans up temp file."""
    file_path = str(tmp_path / "error_db.json")
    storage = AtomicJSONStorage(file_path)

    with patch("os.fsync", side_effect=OSError("Disk failure")):
        with pytest.raises(OSError):
            storage.write({"data": "bad"})

    tmp_files = [f for f in os.listdir(tmp_path) if f.endswith(".tmp")]
    assert len(tmp_files) == 0
    storage.close()


def test_atomic_json_storage_temp_cleanup_os_error(tmp_path: Any) -> None:
    """Test that OSError during temporary file removal in finally block is suppressed."""
    file_path = str(tmp_path / "clean_err.json")
    storage = AtomicJSONStorage(file_path)

    with patch("os.replace", side_effect=PermissionError("Locked")), patch(
        "os.remove", side_effect=OSError("Cannot remove")
    ):
        with pytest.raises(PermissionError):
            storage.write({"data": "test"})

    storage.close()


def test_db_lock_basic(tmp_path: Any) -> None:
    """Test basic acquisition and release of db_lock."""
    db_file = str(tmp_path / "test.json")
    with db_lock(db_file):
        assert os.path.exists(f"{db_file}.lock")


def test_db_lock_msvcrt_timeout(tmp_path: Any) -> None:
    """Test msvcrt timeout when lock cannot be acquired within 15s."""
    db_file = str(tmp_path / "msvcrt_timeout.json")

    mock_msvcrt = MagicMock()
    mock_msvcrt.locking.side_effect = OSError("Locked")
    mock_msvcrt.LK_NBLCK = 1

    with patch("backend_v2.database.wrapper.HAS_MSVCRT", True), patch(
        "backend_v2.database.wrapper.msvcrt", mock_msvcrt
    ), patch("time.time", side_effect=[0.0, 0.0, 16.0, 16.0]):
        with pytest.raises(TimeoutError):
            with db_lock(db_file):
                pass


def test_db_lock_fcntl_support(tmp_path: Any) -> None:
    """Test fcntl code path under simulated Unix environment."""
    db_file = str(tmp_path / "fcntl_test.json")

    mock_fcntl = MagicMock()
    mock_fcntl.LOCK_EX = 1
    mock_fcntl.LOCK_NB = 2
    mock_fcntl.LOCK_UN = 4

    with patch("backend_v2.database.wrapper.HAS_MSVCRT", False), patch(
        "backend_v2.database.wrapper.HAS_FCNTL", True
    ), patch("backend_v2.database.wrapper.fcntl", mock_fcntl, create=True):
        with db_lock(db_file):
            assert mock_fcntl.flock.called


def test_db_lock_fcntl_timeout(tmp_path: Any) -> None:
    """Test fcntl timeout when flock repeatedly raises BlockingIOError."""
    db_file = str(tmp_path / "fcntl_timeout.json")

    mock_fcntl = MagicMock()
    mock_fcntl.LOCK_EX = 1
    mock_fcntl.LOCK_NB = 2
    mock_fcntl.LOCK_UN = 4

    def mock_flock(handle: Any, flags: int) -> None:
        if flags != 4:
            raise BlockingIOError("Locked")

    mock_fcntl.flock.side_effect = mock_flock

    with patch("backend_v2.database.wrapper.HAS_MSVCRT", False), patch(
        "backend_v2.database.wrapper.HAS_FCNTL", True
    ), patch("backend_v2.database.wrapper.fcntl", mock_fcntl, create=True), patch(
        "time.time", side_effect=[0.0, 0.0, 16.0, 16.0]
    ):
        with pytest.raises(TimeoutError):
            with db_lock(db_file):
                pass


def test_db_lock_directory_fallback(tmp_path: Any) -> None:
    """Test directory lock fallback when neither msvcrt nor fcntl is available."""
    db_file = str(tmp_path / "fallback.json")
    with patch("backend_v2.database.wrapper.HAS_MSVCRT", False), patch("backend_v2.database.wrapper.HAS_FCNTL", False):
        with db_lock(db_file):
            assert os.path.exists(f"{db_file}.lock_dir")
        assert not os.path.exists(f"{db_file}.lock_dir")


def test_db_lock_directory_stale_lock_cleanup(tmp_path: Any) -> None:
    """Test that stale lock_dir (>10s old) is cleaned up and acquired."""
    db_file = str(tmp_path / "stale_fallback.json")
    lock_dir = f"{db_file}.lock_dir"
    os.makedirs(lock_dir)

    with patch("backend_v2.database.wrapper.HAS_MSVCRT", False), patch(
        "backend_v2.database.wrapper.HAS_FCNTL", False
    ), patch("os.path.getmtime", return_value=0.0), patch("time.time", side_effect=[15.0, 15.0, 15.1, 15.2, 15.3]):
        with db_lock(db_file):
            assert os.path.exists(lock_dir)
        assert not os.path.exists(lock_dir)


def test_tinydb_table_full_crud(tmp_path: Any) -> None:
    """Test all TinyDBTable operations directly."""
    db_path = str(tmp_path / "table_crud.json")
    table = TinyDBTable(db_path, "items")

    # 1. Insert
    doc_id = table.insert({"id": "item_1", "score": 10})
    assert doc_id is not None

    # 2. Contains & Count
    q = Query()
    assert table.contains(q.id == "item_1") is True
    assert table.contains(q.id == "nonexistent") is False
    assert table.count(q.score == 10) == 1
    assert table.count() == 1

    # 3. Get
    doc = table.get(q.id == "item_1")
    assert doc is not None
    assert doc["score"] == 10
    assert table.get(q.id == "nonexistent") is None

    # 4. Search
    results = table.search(q.score >= 10)
    assert len(results) == 1

    # 5. Update
    table.update({"score": 20}, q.id == "item_1")
    updated = table.get(q.id == "item_1")
    assert updated is not None
    assert updated["score"] == 20

    # 6. Upsert existing
    table.upsert({"id": "item_1", "score": 30}, q.id == "item_1")
    upserted = table.get(q.id == "item_1")
    assert upserted is not None
    assert upserted["score"] == 30

    # 7. Upsert new
    table.upsert({"id": "item_2", "score": 40}, q.id == "item_2")
    assert table.count() == 2

    # 8. All
    all_docs = table.all()
    assert len(all_docs) == 2

    # 9. Remove
    table.remove(q.id == "item_2")
    assert table.count() == 1

    # 10. Truncate
    table.truncate()
    assert table.count() == 0


def test_tinydb_table_get_list_response(tmp_path: Any) -> None:
    """Test TinyDBTable get method unpacks list if returned."""
    db_path = str(tmp_path / "list_res.json")
    table = TinyDBTable(db_path, "items")
    with patch.object(TinyDBTable, "_get_table") as mock_gt:
        mock_tbl = MagicMock()
        mock_tbl.get.return_value = [{"score": 100}]
        mock_gt.return_value = mock_tbl
        res = table.get(None)
        assert res == {"score": 100}


def test_tinydb_client(tmp_path: Any) -> None:
    """Test TinyDBClient initialization, table retrieval, and close."""
    nested_dir = tmp_path / "nested" / "subdir"
    db_path = str(nested_dir / "client_db.json")

    client = TinyDBClient(db_path)
    assert client.path == db_path

    tbl = client.table("sample")
    assert isinstance(tbl, TinyDBTable)
    tbl.insert({"key": "val"})
    assert os.path.exists(db_path)

    client.close()


def test_firestore_table_crud() -> None:
    """Test FirestoreTable operations using mocked collection."""
    mock_collection = MagicMock()
    table = FirestoreTable(mock_collection)

    # Insert
    mock_ref = MagicMock()
    mock_ref.id = "doc_123"
    mock_collection.add.return_value = (None, mock_ref)
    assert table.insert({"field": "val"}) == "doc_123"

    # All
    doc1 = MagicMock()
    doc1.to_dict.return_value = {"id": "1", "score": 50}
    doc2 = MagicMock()
    doc2.to_dict.return_value = {"id": "2", "score": 80}
    mock_collection.stream.return_value = [doc1, doc2]

    all_docs = table.all()
    assert len(all_docs) == 2

    # Search
    mock_collection.stream.return_value = [doc1, doc2]
    matches = table.search(lambda d: d["score"] > 60)
    assert len(matches) == 1
    assert matches[0]["id"] == "2"

    # Get
    mock_collection.stream.return_value = [doc1, doc2]
    got = table.get(lambda d: d["id"] == "1")
    assert got == {"id": "1", "score": 50}

    # Get None
    mock_collection.stream.return_value = [doc1, doc2]
    assert table.get(lambda d: d["id"] == "none") is None

    # Contains
    mock_collection.stream.return_value = [doc1, doc2]
    assert table.contains(lambda d: d["id"] == "1") is True

    # Update
    mock_collection.stream.return_value = [doc1]
    res_update = table.update({"score": 60}, query=lambda d: d["id"] == "1")
    assert res_update == [1]
    doc1.reference.update.assert_called_with({"score": 60})

    # Upsert existing
    mock_collection.stream.return_value = [doc1]
    res_upsert = table.upsert({"id": "1", "score": 70}, query=lambda d: d["id"] == "1")
    assert res_upsert == [1]
    doc1.reference.update.assert_called_with({"id": "1", "score": 70})

    # Upsert new
    mock_collection.stream.return_value = []
    res_upsert_new = table.upsert({"id": "3", "score": 90}, query=lambda d: False)
    assert res_upsert_new == [1]
    mock_collection.document.assert_called_with("3")

    # Upsert new without ID
    mock_collection.stream.return_value = []
    table.upsert({"score": 100}, query=lambda d: False)
    mock_collection.add.assert_called_with({"score": 100})

    # Remove
    mock_collection.stream.return_value = [doc1]
    res_remove = table.remove(query=lambda d: d["id"] == "1")
    assert res_remove == [1]
    doc1.reference.delete.assert_called()

    # Count with query
    mock_collection.stream.return_value = [doc1, doc2]
    assert table.count(query=lambda d: d["score"] == 50) == 1

    # Count total
    mock_agg = MagicMock()
    mock_snap = MagicMock()
    mock_snap.value = 42
    mock_agg.get.return_value = [[mock_snap]]
    mock_collection.count.return_value = mock_agg
    assert table.count() == 42

    # Count total fallback on exception
    mock_collection.count.side_effect = RuntimeError("Aggregation failed")
    mock_collection.stream.return_value = [doc1, doc2]
    assert table.count() == 2
    mock_collection.count.side_effect = None

    # Truncate recursive branch
    batch_docs = [MagicMock() for _ in range(500)]
    mock_collection.limit.return_value.stream.side_effect = [batch_docs, [doc1]]
    table.truncate()

    table.close()


def test_firestore_table_remove_failure_raises() -> None:
    """Test that deletion errors in FirestoreTable raise AppException."""
    mock_collection = MagicMock()
    table = FirestoreTable(mock_collection)

    doc = MagicMock()
    doc.to_dict.return_value = {"id": "bad"}
    doc.reference.delete.side_effect = RuntimeError("Delete failed")
    mock_collection.stream.return_value = [doc]

    with pytest.raises(AppException) as exc_info:
        table.remove(query=lambda d: True)

    assert exc_info.value.details.get("error_code") == ErrorCodes.STORAGE_ACCESS_FAILED


def test_firestore_client(tmp_path: Any) -> None:
    """Test FirestoreClient connection validation and table retrieval."""
    mock_client_instance = MagicMock()
    mock_col = MagicMock()
    mock_col.limit.return_value.stream.return_value = []
    mock_client_instance.collection.return_value = mock_col

    with patch("backend_v2.database.wrapper.firebase_admin") as mock_fb, patch(
        "backend_v2.database.wrapper.firestore.client", return_value=mock_client_instance
    ), patch("os.path.exists", return_value=True), patch("backend_v2.database.wrapper.credentials.Certificate"):
        mock_fb._apps = []
        client = FirestoreClient()
        assert client.db is mock_client_instance

        tbl = client.table("test_col")
        assert isinstance(tbl, FirestoreTable)
        client.close()


def test_firestore_client_missing_service_account() -> None:
    """Test FirestoreClient warns when service-account.json does not exist."""
    mock_client_instance = MagicMock()
    mock_col = MagicMock()
    mock_col.limit.return_value.stream.return_value = []
    mock_client_instance.collection.return_value = mock_col

    with patch("backend_v2.database.wrapper.firebase_admin") as mock_fb, patch(
        "backend_v2.database.wrapper.firestore.client", return_value=mock_client_instance
    ), patch("os.path.exists", return_value=False), patch("backend_v2.database.wrapper.credentials.Certificate"):
        mock_fb._apps = []
        client = FirestoreClient()
        assert client.db is mock_client_instance
        client.close()


def test_firestore_client_ping_failure() -> None:
    """Test FirestoreClient raises AppException on ping failure."""
    mock_client_instance = MagicMock()
    mock_col = MagicMock()
    mock_col.limit.return_value.stream.side_effect = RuntimeError("Network error")
    mock_client_instance.collection.return_value = mock_col

    with patch("backend_v2.database.wrapper.firebase_admin") as mock_fb, patch(
        "backend_v2.database.wrapper.firestore.client", return_value=mock_client_instance
    ), patch("os.path.exists", return_value=True), patch("backend_v2.database.wrapper.credentials.Certificate"):
        mock_fb._apps = [MagicMock()]
        with pytest.raises(AppException) as exc_info:
            FirestoreClient()

        assert exc_info.value.details.get("error_code") == ErrorCodes.STORAGE_ACCESS_FAILED


def test_get_db_client(tmp_path: Any) -> None:
    """Test get_db_client factory function."""
    mock_settings = MagicMock()
    mock_settings.active_backend = "LOCAL"
    mock_settings.prod_db_path = str(tmp_path / "factory.json")

    with patch("backend_v2.database.wrapper.get_settings", return_value=mock_settings):
        client = get_db_client()
        assert isinstance(client, TinyDBClient)

    mock_settings.active_backend = "FIRESTORE"
    with patch("backend_v2.database.wrapper.get_settings", return_value=mock_settings), patch(
        "backend_v2.database.wrapper.FirestoreClient"
    ) as mock_fc, patch("backend_v2.database.wrapper.FIRESTORE_AVAILABLE", True):
        get_db_client()
        mock_fc.assert_called_once()

    with patch("backend_v2.database.wrapper.get_settings", return_value=mock_settings), patch(
        "backend_v2.database.wrapper.FIRESTORE_AVAILABLE", False
    ):
        with pytest.raises(ImportError):
            get_db_client()

    mock_settings.active_backend = "UNKNOWN"
    with patch("backend_v2.database.wrapper.get_settings", return_value=mock_settings):
        with pytest.raises(ValueError):
            get_db_client()
