from unittest.mock import AsyncMock
from typing import Any
from unittest.mock import patch

import pytest

from backend_v2.database.factory import get_driver
from backend_v2.database.firestore_driver import FirestoreDriver
from backend_v2.database.tinydb_driver import TinyDBDriver
from backend_v2.exceptions import AppException
from backend_v2.settings import Settings


@pytest.mark.asyncio
async def test_get_driver_local() -> None:
    settings = Settings(storage_backend="LOCAL")
    driver = await get_driver(settings)
    assert isinstance(driver, TinyDBDriver)


@pytest.mark.asyncio
@patch("google.cloud.firestore.AsyncClient")
async def test_get_driver_firestore(mock_client: Any) -> None:
    settings = Settings(storage_backend="FIRESTORE")
    driver = await get_driver(settings)
    assert isinstance(driver, FirestoreDriver)


@pytest.mark.asyncio
async def test_get_driver_unknown() -> None:
    settings = Settings(storage_backend="UNKNOWN")
    with pytest.raises(AppException):
        _ = settings.active_backend
