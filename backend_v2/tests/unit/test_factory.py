"""Unit tests for backend_v2.database.factory (get_driver and create_unit_of_work)."""

from unittest.mock import PropertyMock, patch

import pytest

from backend_v2.database.factory import create_unit_of_work, get_driver
from backend_v2.database.interfaces import QuorumUnitOfWork
from backend_v2.database.postgres.pool import PostgresPoolManager
from backend_v2.database.postgres.storage_driver import PostgresStorageDriver
from backend_v2.database.postgres.uow import PostgresUnitOfWork
from backend_v2.exceptions import AppException, ConfigurationError
from backend_v2.settings import Settings
from backend_v2.tests.fakes.in_memory_uow import InMemoryAsyncPgPool


class _UnmappedBackendSentinel:
    """Sentinel with .value attribute to exercise the default match branch in get_driver."""

    value: str = "UNMAPPED_BACKEND"

    def __str__(self) -> str:
        """Return sentinel string representation."""
        return self.value


def invalid_backend_sentinel() -> _UnmappedBackendSentinel:
    """Return an unmapped backend sentinel instance."""
    return _UnmappedBackendSentinel()


@pytest.mark.asyncio
async def test_get_driver_postgres_default_and_injected_pool() -> None:
    """Verify get_driver returns PostgresStorageDriver for POSTGRES settings and injected pool."""
    settings = Settings(storage_backend="POSTGRES")
    pool_mgr = PostgresPoolManager(settings=settings, pool=InMemoryAsyncPgPool())
    driver_injected = await get_driver(settings, pool_manager=pool_mgr)
    assert isinstance(driver_injected, PostgresStorageDriver)
    assert driver_injected.pool_manager is pool_mgr

    driver_default = await get_driver(settings)
    assert isinstance(driver_default, PostgresStorageDriver)


@pytest.mark.asyncio
async def test_get_driver_postgres_invalid_pool_manager_raises_configuration_error() -> None:
    """Verify get_driver fails fast with ConfigurationError when pool_manager is not PostgresPoolManager."""
    settings = Settings(storage_backend="POSTGRES")
    with pytest.raises(ConfigurationError, match="requires a PostgresPoolManager instance"):
        await get_driver(settings, pool_manager="invalid_pool")


@pytest.mark.asyncio
@pytest.mark.parametrize("decommissioned_backend", ["LOCAL", "FIRESTORE"])
async def test_get_driver_decommissioned_backends_raise_configuration_error(decommissioned_backend: str) -> None:
    """Verify get_driver fails fast with ConfigurationError on LOCAL and FIRESTORE."""
    settings = Settings(storage_backend=decommissioned_backend)
    with pytest.raises(ConfigurationError, match="Unsupported STORAGE_BACKEND"):
        await get_driver(settings)


@pytest.mark.asyncio
async def test_get_driver_tinydb_raises_configuration_error() -> None:
    """Verify TINYDB storage_backend fails fast with ConfigurationError."""
    settings = Settings(storage_backend="TINYDB")
    with pytest.raises(ConfigurationError, match="Unsupported STORAGE_BACKEND"):
        await get_driver(settings)


@pytest.mark.asyncio
async def test_get_driver_unknown() -> None:
    """Verify invalid storage_backend raises AppException on get_driver and ConfigurationError on unmapped enum."""
    settings = Settings(storage_backend="UNKNOWN")
    with pytest.raises(AppException):
        await get_driver(settings)

    valid_settings = Settings(storage_backend="POSTGRES")
    with patch.object(Settings, "active_backend", new_callable=PropertyMock, return_value=invalid_backend_sentinel()):
        with pytest.raises(ConfigurationError, match="Unsupported storage backend"):
            await get_driver(valid_settings)


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
    with pytest.raises(ConfigurationError, match="Unsupported STORAGE_BACKEND"):
        create_unit_of_work(settings)


def test_create_unit_of_work_unmapped_backend_raises_configuration_error() -> None:
    """Verify create_unit_of_work fails fast when active_backend is unmapped enum."""
    valid_settings = Settings(storage_backend="POSTGRES")
    with patch.object(Settings, "active_backend", new_callable=PropertyMock, return_value=invalid_backend_sentinel()):
        with pytest.raises(ConfigurationError, match="create_unit_of_work requires StorageBackend.POSTGRES"):
            create_unit_of_work(valid_settings)
