"""Unit tests for backend storage and database synchronization pre-flight audit.

Verifies that the startup audit detects desynchronizations in a strictly read-only
manner without performing silent mutations or deleting data.
"""

import logging
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from tinydb import TinyDB

from backend_v2.main import _audit_storage_and_database_sync


@pytest.fixture
def temp_db_and_storage(tmp_path: Path) -> tuple[TinyDB, Path]:
    """Creates an isolated temporary TinyDB and execution storage directory.

    Args:
        tmp_path: Pytest temporary directory fixture.

    Returns:
        tuple containing (TinyDB instance, storage Path).
    """
    db_file = tmp_path / "test_db.json"
    db = TinyDB(str(db_file), encoding="utf-8")
    storage_dir = tmp_path / "executions"
    storage_dir.mkdir(parents=True, exist_ok=True)
    return db, storage_dir


def test_audit_storage_and_database_sync_when_synced(
    temp_db_and_storage: tuple[TinyDB, Path],
) -> None:
    """Verifies that fully synchronized database and storage logs PASSED info."""
    db, storage_dir = temp_db_and_storage
    logger = MagicMock(spec=logging.Logger)

    # Arrange: Create disk folder and trace file
    exe_id = "exe_1234567890abcdef"
    exe_dir = storage_dir / exe_id
    exe_dir.mkdir(parents=True, exist_ok=True)
    trace_file = exe_dir / "execution_trace.json"
    trace_file.write_text("{}", encoding="utf-8")

    # Insert into DB
    table = db.table("executions")
    table.insert({"id": exe_id, "execution_trace_storage_path": str(trace_file)})

    # Act
    _audit_storage_and_database_sync(db, logger, storage_dir=storage_dir)

    # Assert: Info logged, zero warnings
    logger.info.assert_called()
    info_msg = logger.info.call_args[0][0]
    assert "PASSED" in info_msg
    logger.warning.assert_not_called()
    assert len(table.all()) == 1


def test_audit_storage_and_database_sync_when_orphaned_db_record(
    temp_db_and_storage: tuple[TinyDB, Path],
) -> None:
    """Verifies that orphaned database record triggers a warning without mutating the database."""
    db, storage_dir = temp_db_and_storage
    logger = MagicMock(spec=logging.Logger)

    # Arrange: DB has record pointing to nonexistent disk path
    exe_id = "exe_ghost_record_123"
    missing_trace_path = storage_dir / exe_id / "execution_trace.json"
    table = db.table("executions")
    table.insert({"id": exe_id, "execution_trace_storage_path": str(missing_trace_path)})

    # Act
    _audit_storage_and_database_sync(db, logger, storage_dir=storage_dir)

    # Assert: Warning logged with recommendation, and DB record is NOT deleted (Read-Only)
    logger.warning.assert_called_once()
    warning_call = logger.warning.call_args
    warning_msg = warning_call[0][0]
    assert "orphaned" in warning_msg.lower()
    assert "reconcile_storage.py" in warning_msg
    assert len(table.all()) == 1  # Strictly read-only: No silent pruning!


def test_audit_storage_and_database_sync_when_unindexed_disk_execution(
    temp_db_and_storage: tuple[TinyDB, Path],
) -> None:
    """Verifies that unindexed disk folder triggers a warning without mutating the database."""
    db, storage_dir = temp_db_and_storage
    logger = MagicMock(spec=logging.Logger)

    # Arrange: Disk has execution trace, DB is empty
    exe_id = "exe_unindexed_disk_456"
    exe_dir = storage_dir / exe_id
    exe_dir.mkdir(parents=True, exist_ok=True)
    trace_file = exe_dir / "execution_trace.json"
    trace_file.write_text("{}", encoding="utf-8")

    table = db.table("executions")
    assert len(table.all()) == 0

    # Act
    _audit_storage_and_database_sync(db, logger, storage_dir=storage_dir)

    # Assert: Warning logged with recommendation, and DB is NOT modified (Read-Only)
    logger.warning.assert_called_once()
    warning_call = logger.warning.call_args
    warning_msg = warning_call[0][0]
    assert "unindexed" in warning_msg.lower()
    assert "reconcile_storage.py" in warning_msg
    assert len(table.all()) == 0  # Strictly read-only: No silent insertion!
