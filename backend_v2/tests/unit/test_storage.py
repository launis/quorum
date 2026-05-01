from unittest.mock import patch, PropertyMock

import pytest

from backend_v2.exceptions import AppException
from backend_v2.services.drivers.local_file_driver import LocalFileDriver
from backend_v2.services.storage import get_storage_driver
from backend_v2.settings import StorageBackend, get_settings, Settings


@pytest.fixture(autouse=True)
def clear_lru_cache():
    """Clear the lru_cache on get_storage_driver before each test."""
    get_storage_driver.cache_clear()
    get_settings.cache_clear()
    yield
    get_storage_driver.cache_clear()
    get_settings.cache_clear()


def test_get_storage_driver_local():
    """Test that LOCAL backend returns LocalFileDriver."""
    with patch.dict("os.environ", {"STORAGE_BACKEND": "LOCAL"}):
        driver = get_storage_driver()
        assert isinstance(driver, LocalFileDriver)


def test_get_storage_driver_firestore():
    """Test that FIRESTORE backend returns GCSFileDriver when bucket name is provided."""
    with patch.dict(
        "os.environ",
        {
            "STORAGE_BACKEND": "FIRESTORE",
            "STORAGE_BUCKET_NAME": "test-bucket",
            "GOOGLE_API_KEY": "fake-key",
        },
    ):
        with patch("backend_v2.services.storage.GCSFileDriver") as mock_gcs:
            driver = get_storage_driver()
            # It should return the mock
            mock_gcs.assert_called_once_with(bucket_name="test-bucket")


def test_get_storage_driver_firestore_missing_bucket():
    """Test that FIRESTORE backend raises AppException if bucket name is missing."""
    with patch.dict(
        "os.environ",
        {
            "STORAGE_BACKEND": "FIRESTORE",
            "STORAGE_BUCKET_NAME": "",
            "GOOGLE_API_KEY": "fake-key",
        },
    ):
        with pytest.raises(AppException) as exc:
            get_storage_driver()
        assert "requires STORAGE_BUCKET_NAME" in exc.value.message


def test_get_storage_driver_invalid_backend():
    """Test that an invalid backend raises AppException."""
    # We mock the active_backend property directly to test the fallback in get_storage_driver
    with patch("backend_v2.services.storage.get_settings") as mock_get_settings:
        mock_settings = mock_get_settings.return_value
        # Use type(mock).property to mock a property on a mock if it was a property,
        # but here it's just an attribute on the returned mock.
        mock_settings.active_backend = "UNKNOWN"
        mock_settings.storage_bucket_name = "bucket"
        
        with pytest.raises(AppException) as exc:
            get_storage_driver()
        assert "Unsupported StorageBackend configured: UNKNOWN" in exc.value.message
