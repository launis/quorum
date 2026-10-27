"""Unit tests for backend_v2.database.factory (get_driver and create_unit_of_work)."""

from typing import Any
from unittest.mock import patch

import pytest

from backend_v2.database.factory import create_unit_of_work, get_driver
from backend_v2.database.firestore_driver import FirestoreDriver
from backend_v2.database.interfaces import QuorumUnitOfWork
from backend_v2.database.postgres.pool import PostgresPoolManager
from backend_v2.database.postgres.uow import PostgresUnitOfWork
from backend_v2.database.tinydb_driver import TinyDBDriver
from backend_v2.exceptions import AppException, ConfigurationError
from backend_v2.settings import Settings
from backend_v2.tests.fakes.in_memory_uow import InMemoryAsyncPgPool


@pytest.mark.asyncio
async def test_get_driver_local() -> None:
    """Verify get_driver returns TinyDBDriver when storage_backend is LOCAL."""
    settings = Settings(storage_backend="LOCAL")
    driver = await get_driver(settings)
    assert isinstance(driver, TinyDBDriver)


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
    """Verify invalid storage_backend raises AppException on active_backend resolution."""
    settings = Settings(storage_backend="UNKNOWN")
    with pytest.raises(AppException):
        _ = settings.active_backend


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
