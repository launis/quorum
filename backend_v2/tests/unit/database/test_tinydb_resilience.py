"""Regression and resilience tests for AtomicJSONStorage and TinyDBTable."""

import json
import os
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from backend_v2.database.wrapper import (
    AtomicJSONStorage,
    TinyDBTable,
)


def test_atomic_json_storage_read_missing_or_empty_returns_none(tmp_path: Path) -> None:
    """Verify that AtomicJSONStorage.read() returns None if file does not exist or is 0 bytes."""
    # 1. Non-existent file
    missing_path = tmp_path / "missing.json"
    storage_missing = AtomicJSONStorage(str(missing_path))
    assert storage_missing.read() is None

    # 2. Zero-byte file
    empty_path = tmp_path / "empty.json"
    empty_path.write_text("", encoding="utf-8")
    storage_empty = AtomicJSONStorage(str(empty_path))
    assert storage_empty.read() is None


def test_atomic_json_storage_write_and_read_roundtrip(tmp_path: Path) -> None:
    """Verify AtomicJSONStorage writes atomically via temporary file and reads cleanly."""
    db_file = tmp_path / "test_roundtrip.json"
    storage = AtomicJSONStorage(str(db_file), indent=2)

    payload: dict[str, dict[str, Any]] = {
        "users": {
            "usr_1": {"name": "Alice", "role": "admin"},
            "usr_2": {"name": "Bob", "role": "member"},
        }
    }

    storage.write(payload)
    assert db_file.exists()

    # Read back and assert equality
    read_data = storage.read()
    assert read_data == payload

    # Ensure no leftover temporary files in directory
    tmp_files = list(tmp_path.glob("*.tmp"))
    assert len(tmp_files) == 0


def test_atomic_json_storage_retries_on_permission_error_and_succeeds(tmp_path: Path) -> None:
    """Verify AtomicJSONStorage retries on transient Windows PermissionError and succeeds."""
    db_file = tmp_path / "test_retry.json"
    storage = AtomicJSONStorage(str(db_file))

    payload: dict[str, dict[str, Any]] = {"table": {"item": {"val": 123}}}

    attempts = 0
    orig_replace = os.replace

    def flaky_replace(src: str, dst: str) -> None:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise PermissionError(13, "Permission denied (simulated NTFS lock)")
        orig_replace(src, dst)

    with patch("os.replace", side_effect=flaky_replace):
        with patch("time.sleep") as mock_sleep:
            storage.write(payload)
            assert mock_sleep.call_count == 2

    assert attempts == 3
    assert storage.read() == payload
    assert len(list(tmp_path.glob("*.tmp"))) == 0


def test_atomic_json_storage_raises_when_retries_exhausted_and_cleans_tmp(tmp_path: Path) -> None:
    """Verify AtomicJSONStorage cleans up temp file and re-raises when retries are exhausted."""
    db_file = tmp_path / "test_exhausted.json"
    storage = AtomicJSONStorage(str(db_file))

    initial_payload: dict[str, dict[str, Any]] = {"table": {"k": {"v": "initial"}}}
    storage.write(initial_payload)

    def failing_replace(src: str, dst: str) -> None:
        raise PermissionError(13, "Permanent lock")

    with patch("os.replace", side_effect=failing_replace):
        with patch("time.sleep"):
            with pytest.raises(PermissionError):
                storage.write({"table": {"k": {"v": "corrupted"}}})

    # Assert original content remains intact (zero corruption)
    assert storage.read() == initial_payload

    # Assert temporary file was cleaned up in finally block
    tmp_files = list(tmp_path.glob("*.tmp"))
    assert len(tmp_files) == 0


def test_tinydb_table_atomic_mutation_and_truncation_resilience(tmp_path: Path) -> None:
    """Verify TinyDBTable executes mutations atomically with zero trailing bytes or Extra Data errors."""
    db_file = tmp_path / "test_table_resilience.json"
    table = TinyDBTable(db_path=str(db_file), table_name="test_collection")

    # 1. Insert large payload
    doc_id = table.insert({
        "id": "doc_1",
        "title": "Initial Large Document " + ("X" * 1000),
        "status": "READY",
    })
    assert doc_id == 1
    assert len(table.all()) == 1

    # 2. Update to a much smaller payload (would trigger trailing bytes in un-truncated JSONStorage)
    table.update({"title": "Tiny"}, doc_ids=[doc_id])

    # 3. Truncate table
    table.truncate()
    assert len(table.all()) == 0

    # 4. Re-insert after truncate
    table.insert({"id": "doc_2", "title": "Fresh"})
    items = table.all()
    assert len(items) == 1
    assert items[0]["id"] == "doc_2"

    # 5. Raw JSON verification: verify file decodes cleanly with zero extra trailing characters
    raw_content = db_file.read_text(encoding="utf-8")
    parsed = json.loads(raw_content)
    assert isinstance(parsed, dict)
    assert "test_collection" in parsed
