"""Unit tests for backend_v2.database.factory (get_driver and create_unit_of_work)."""

from pathlib import Path
from typing import Any
from unittest.mock import PropertyMock, patch

import pytest

from backend_v2.database.factory import create_unit_of_work, get_driver
from backend_v2.database.firestore_driver import FirestoreDriver
from backend_v2.database.interfaces import QuorumUnitOfWork
from backend_v2.database.postgres.pool import PostgresPoolManager
from backend_v2.database.postgres.uow import PostgresUnitOfWork
from backend_v2.database.tinydb_driver import TinyDBDriver
from backend_v2.database.wrapper import AbstractDatabase, AbstractTable, TinyDBClient
from backend_v2.exceptions import AppException, ConfigurationError
from backend_v2.settings import Settings
from backend_v2.tests.fakes.in_memory_uow import InMemoryAsyncPgPool


class _StubNonTinyDBDatabase(AbstractDatabase):
    """Stub AbstractDatabase implementation that is not a TinyDBClient for negative boundary testing."""

    def table(self, name: str) -> AbstractTable:
        """Raise NotImplementedError as table access is not reached during driver validation."""
        raise NotImplementedError(name)

    def close(self) -> None:
        """No-op close for stub database."""


@pytest.mark.asyncio
async def test_get_driver_local_default_and_injected_client(tmp_path: Path) -> None:
    """Verify get_driver returns TinyDBDriver for default LOCAL settings and injected TinyDBClient."""
    settings = Settings(storage_backend="LOCAL")
    driver = await get_driver(settings)
    assert isinstance(driver, TinyDBDriver)

    injected_client = TinyDBClient(str(tmp_path / "injected_db.json"))
    driver_injected = await get_driver(settings, db_client=injected_client)
    assert isinstance(driver_injected, TinyDBDriver)
    assert driver_injected.db is injected_client


@pytest.mark.asyncio
async def test_get_driver_local_invalid_db_client_raises_configuration_error() -> None:
    """Verify get_driver fails fast with ConfigurationError when LOCAL receives a non-TinyDBClient db_client."""
    settings = Settings(storage_backend="LOCAL")
    invalid_client = _StubNonTinyDBDatabase()
    with pytest.raises(ConfigurationError, match="TinyDBClient"):
        await get_driver(settings, db_client=invalid_client)


@pytest.mark.asyncio
@patch("backend_v2.database.factory.firestore.AsyncClient")
async def test_get_driver_firestore(mock_client: Any) -> None:
    """Verify get_driver returns FirestoreDriver when storage_backend is FIRESTORE."""
    _ = mock_client
    settings = Settings(storage_backend="FIRESTORE")
    driver = await get_driver(settings)
    assert isinstance(driver, FirestoreDriver)


@pytest.mark.asyncio
async def test_get_driver_postgres_raises_configuration_error() -> None:
    """Verify get_driver fails fast with ConfigurationError when storage_backend is POSTGRES."""
    settings = Settings(storage_backend="POSTGRES")
    with pytest.raises(ConfigurationError, match="create_unit_of_work"):
        await get_driver(settings)


@pytest.mark.asyncio
async def test_get_driver_unknown() -> None:
    """Verify invalid storage_backend raises AppException on get_driver and ConfigurationError on unmapped enum."""
    settings = Settings(storage_backend="UNKNOWN")
    with pytest.raises(AppException):
        await get_driver(settings)

    valid_settings = Settings(storage_backend="LOCAL")
    with patch.object(Settings, "active_backend", new_callable=PropertyMock, return_value=invalid_backend_sentinel()):
        with pytest.raises(ConfigurationError, match="Unknown storage backend"):
            await get_driver(valid_settings)


class _UnmappedBackendSentinel:
    """Sentinel with .value attribute to exercise the defensive default match branch in get_driver."""

    value: str = "UNMAPPED_BACKEND"

    def __str__(self) -> str:
        """Return sentinel string representation."""
        return self.value


def invalid_backend_sentinel() -> _UnmappedBackendSentinel:
    """Return an unmapped backend sentinel instance."""
    return _UnmappedBackendSentinel()


def test_create_unit_of_work_postgres_default_and_injected_pool() -> None:
    """Verify create_unit_of_work returns PostgresUnitOfWork for POSTGRES backend."""
    settings = Settings(storage_backend="POSTGRES")
    uow_default = create_unit_of_work(settings)
    assert isinstance(uow_default, PostgresUnitOfWork)
    assert isinstance(uow_default, QuorumUnitOfWork)

    pool_mgr = PostgresPoolManager(settings=settings, pool=InMemoryAsyncPgPool())
    uow_injected = create_unit_of_work(settings, pool_manager=pool_mgr)
    assert isinstance(uow_injected, PostgresUnitOfWork)


@pytest.mark.parametrize("invalid_backend", ["LOCAL", "FIRESTORE"])
def test_create_unit_of_work_non_postgres_raises_configuration_error(invalid_backend: str) -> None:
    """Verify create_unit_of_work fails fast with ConfigurationError for LOCAL and FIRESTORE."""
    settings = Settings(storage_backend=invalid_backend)
    with pytest.raises(ConfigurationError, match="StorageBackend.POSTGRES"):
        create_unit_of_work(settings)
