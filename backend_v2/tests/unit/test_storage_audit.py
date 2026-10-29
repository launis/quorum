"""Unit tests for backend storage and database synchronization pre-flight audit.

Verifies that the startup audit detects desynchronizations in a strictly read-only
manner without performing silent mutations or deleting data.
"""

import logging
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from backend_v2.database.postgres.storage_driver import PostgresStorageDriver
from backend_v2.main import _audit_storage_and_database_sync


@pytest.fixture
def temp_driver_and_storage(tmp_path: Path) -> tuple[PostgresStorageDriver, Path]:
    """Creates an isolated PostgresStorageDriver and execution storage directory.

    Args:
        tmp_path: Pytest temporary directory fixture.

    Returns:
        tuple containing (PostgresStorageDriver instance, storage Path).
    """
    driver = PostgresStorageDriver(auto_initialize_pool=False)
    storage_dir = tmp_path / "executions"
    storage_dir.mkdir(parents=True, exist_ok=True)
    return driver, storage_dir


@pytest.mark.asyncio
async def test_audit_storage_and_database_sync_when_synced(
    temp_driver_and_storage: tuple[PostgresStorageDriver, Path],
) -> None:
    """Verifies that fully synchronized database and storage logs PASSED info."""
    driver, storage_dir = temp_driver_and_storage
    logger = MagicMock(spec=logging.Logger)

    exe_id = "exe_0195f3a0000070018234567890abcdef"
    exe_dir = storage_dir / exe_id
    exe_dir.mkdir(parents=True, exist_ok=True)
    trace_file = exe_dir / "execution_trace.json"
    trace_file.write_text("{}", encoding="utf-8")

    await driver.upsert("executions", {"id": exe_id, "execution_trace_storage_path": str(trace_file)}, exe_id)

    await _audit_storage_and_database_sync(driver, logger, storage_dir=storage_dir)

    logger.info.assert_called()
    info_msg = logger.info.call_args[0][0]
    assert "PASSED" in info_msg
    logger.warning.assert_not_called()
    assert len(await driver.get_all("executions")) == 1


@pytest.mark.asyncio
async def test_audit_storage_and_database_sync_when_orphaned_db_record(
    temp_driver_and_storage: tuple[PostgresStorageDriver, Path],
) -> None:
    """Verifies that orphaned database record triggers a warning without mutating the database."""
    driver, storage_dir = temp_driver_and_storage
    logger = MagicMock(spec=logging.Logger)

    exe_id = "exe_ghost_record_123"
    missing_trace_path = storage_dir / exe_id / "execution_trace.json"
    await driver.upsert("executions", {"id": exe_id, "execution_trace_storage_path": str(missing_trace_path)}, exe_id)

    await _audit_storage_and_database_sync(driver, logger, storage_dir=storage_dir)

    logger.warning.assert_called_once()
    warning_call = logger.warning.call_args
    warning_msg = warning_call[0][0]
    assert "orphaned" in warning_msg.lower()
    assert "reconcile_storage.py" in warning_msg
    assert len(await driver.get_all("executions")) == 1


@pytest.mark.asyncio
async def test_audit_storage_and_database_sync_when_unindexed_disk_execution(
    temp_driver_and_storage: tuple[PostgresStorageDriver, Path],
) -> None:
    """Verifies that unindexed disk folder triggers a warning without mutating the database."""
    driver, storage_dir = temp_driver_and_storage
    logger = MagicMock(spec=logging.Logger)

    exe_id = "exe_unindexed_disk_456"
    exe_dir = storage_dir / exe_id
    exe_dir.mkdir(parents=True, exist_ok=True)
    trace_file = exe_dir / "execution_trace.json"
    trace_file.write_text("{}", encoding="utf-8")

    assert len(await driver.get_all("executions")) == 0

    await _audit_storage_and_database_sync(driver, logger, storage_dir=storage_dir)

    logger.warning.assert_called_once()
    warning_call = logger.warning.call_args
    warning_msg = warning_call[0][0]
    assert "unindexed" in warning_msg.lower()
    assert "reconcile_storage.py" in warning_msg
    assert len(await driver.get_all("executions")) == 0
