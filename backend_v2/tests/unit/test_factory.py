"""Unit tests for backend_v2.database.factory (create_unit_of_work and shared pool lifecycle)."""

from __future__ import annotations

from unittest.mock import PropertyMock, patch

import pytest

from backend_v2.database.factory import (
    close_shared_pool_manager,
    create_unit_of_work,
    get_shared_pool_manager,
)
from backend_v2.database.interfaces import QuorumUnitOfWork
from backend_v2.database.postgres.pool import PostgresPoolManager
from backend_v2.database.postgres.uow import PostgresUnitOfWork
from backend_v2.exceptions import AppException, ConfigurationError
from backend_v2.settings import Settings
from backend_v2.tests.fakes.in_memory_uow import InMemoryAsyncPgPool


class _UnmappedBackendSentinel:
    """Sentinel with .value attribute to exercise the unmapped backend guard in factory helpers."""

    value: str = "UNMAPPED_BACKEND"

    def __str__(self) -> str:
        """Return sentinel string representation."""
        return self.value


def invalid_backend_sentinel() -> _UnmappedBackendSentinel:
    """Return an unmapped backend sentinel instance."""
    return _UnmappedBackendSentinel()


@pytest.mark.asyncio
async def test_shared_pool_manager_reuses_singleton_and_closes_cleanly() -> None:
    """Verify get_shared_pool_manager reuses singleton pool_manager and close_shared_pool_manager cleans up."""
    await close_shared_pool_manager()
    settings = Settings(storage_backend="POSTGRES")
    mgr1 = get_shared_pool_manager(settings)
    mgr2 = get_shared_pool_manager(settings)
    assert mgr1 is mgr2

    fake_pool = InMemoryAsyncPgPool()
    mgr1._pool = fake_pool
    assert mgr1.is_initialized is True

    await close_shared_pool_manager()
    assert fake_pool.closed is True
    assert mgr1.is_initialized is False

    mgr3 = get_shared_pool_manager(settings)
    assert mgr3 is not mgr1
    await close_shared_pool_manager()


@pytest.mark.asyncio
async def test_get_shared_pool_manager_non_postgres_raises_configuration_error_failure() -> None:
    """Verify get_shared_pool_manager fails fast with ConfigurationError when active_backend is not POSTGRES."""
    await close_shared_pool_manager()
    valid_settings = Settings(storage_backend="POSTGRES")
    with patch.object(Settings, "active_backend", new_callable=PropertyMock, return_value=invalid_backend_sentinel()):
        with pytest.raises(ConfigurationError, match="get_shared_pool_manager requires StorageBackend.POSTGRES"):
            get_shared_pool_manager(valid_settings)


@pytest.mark.asyncio
async def test_create_unit_of_work_postgres_default_and_injected_pool() -> None:
    """Verify create_unit_of_work returns PostgresUnitOfWork for POSTGRES backend."""
    await close_shared_pool_manager()
    try:
        settings = Settings(storage_backend="POSTGRES")
        uow_default = create_unit_of_work(settings)
        assert isinstance(uow_default, PostgresUnitOfWork)
        assert isinstance(uow_default, QuorumUnitOfWork)

        pool_mgr = PostgresPoolManager(settings=settings, pool=InMemoryAsyncPgPool())
        uow_injected = create_unit_of_work(settings, pool_manager=pool_mgr)
        assert isinstance(uow_injected, PostgresUnitOfWork)
    finally:
        await close_shared_pool_manager()


@pytest.mark.parametrize("invalid_backend", ["LOCAL", "FIRESTORE", "TINYDB"])
def test_create_unit_of_work_decommissioned_backends_raise_configuration_error_failure(
    invalid_backend: str,
) -> None:
    """Verify create_unit_of_work fails fast with ConfigurationError on decommissioned backends."""
    settings = Settings(storage_backend=invalid_backend)
    with pytest.raises(ConfigurationError, match="Unsupported STORAGE_BACKEND"):
        create_unit_of_work(settings)


def test_create_unit_of_work_unknown_and_unmapped_backend_failure() -> None:
    """Verify unknown storage_backend raises AppException and unmapped enum raises ConfigurationError."""
    settings = Settings(storage_backend="UNKNOWN")
    with pytest.raises(AppException):
        create_unit_of_work(settings)

    valid_settings = Settings(storage_backend="POSTGRES")
    with patch.object(Settings, "active_backend", new_callable=PropertyMock, return_value=invalid_backend_sentinel()):
        with pytest.raises(ConfigurationError, match="create_unit_of_work requires StorageBackend.POSTGRES"):
            create_unit_of_work(valid_settings)
