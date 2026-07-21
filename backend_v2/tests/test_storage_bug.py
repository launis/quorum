from unittest.mock import AsyncMock
import pytest

from backend_v2.services.storage import get_storage_driver


@pytest.mark.asyncio
async def test_storage_driver_mock_bug() -> None:
    # Calling get_storage_driver will evaluate StorageBackend.MOCK
    # which will raise an AttributeError.
    get_storage_driver()
