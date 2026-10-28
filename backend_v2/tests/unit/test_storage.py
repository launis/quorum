"""Unit tests for backend_v2/services/storage.py."""

from collections.abc import Generator
from unittest.mock import patch

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.services.drivers.local_file_driver import LocalFileDriver
from backend_v2.services.storage import get_storage_driver
from backend_v2.settings import get_settings


@pytest.fixture(autouse=True)
def clear_lru_cache() -> Generator[None]:
    """Clear the lru_cache on get_storage_driver before each test."""
    get_storage_driver.cache_clear()
    get_settings.cache_clear()
    yield
    get_storage_driver.cache_clear()
    get_settings.cache_clear()


def test_get_storage_driver_postgres_local_default() -> None:
    """Test that POSTGRES backend without bucket name returns LocalFileDriver."""
    with patch("backend_v2.services.storage.get_settings") as mock_get_settings:
        mock_settings = mock_get_settings.return_value
        mock_settings.active_backend = get_settings().active_backend
        mock_settings.storage_bucket_name = None
        mock_settings.files_dir = get_settings().files_dir
        mock_settings.api_url = "https://api.quorum.test"

        driver = get_storage_driver()
        assert isinstance(driver, LocalFileDriver)


def test_get_storage_driver_postgres_gcs_bucket() -> None:
    """Test that POSTGRES backend returns GCSFileDriver when storage_bucket_name is provided."""
    with (
        patch("backend_v2.services.storage.get_settings") as mock_get_settings,
        patch("backend_v2.services.storage.GCSFileDriver") as mock_gcs,
    ):
        mock_settings = mock_get_settings.return_value
        mock_settings.active_backend = get_settings().active_backend
        mock_settings.storage_bucket_name = "test-bucket"

        get_storage_driver()
        mock_gcs.assert_called_once_with(bucket_name="test-bucket")


def test_get_storage_driver_postgres_local_without_api_url() -> None:
    """Boundary test: POSTGRES backend with empty api_url initializes LocalFileDriver with base_url=None."""
    with patch("backend_v2.services.storage.get_settings") as mock_get_settings:
        mock_settings = mock_get_settings.return_value
        mock_settings.active_backend = get_settings().active_backend
        mock_settings.storage_bucket_name = ""
        mock_settings.files_dir = get_settings().files_dir
        mock_settings.api_url = ""

        driver = get_storage_driver()
        assert isinstance(driver, LocalFileDriver)


def test_get_storage_driver_invalid_backend() -> None:
    """Negative test: an unsupported StorageBackend raises AppException with CONFIGURATION_ERROR."""
    with patch("backend_v2.services.storage.get_settings") as mock_get_settings:
        mock_settings = mock_get_settings.return_value
        mock_settings.active_backend = "UNKNOWN"
        mock_settings.storage_bucket_name = "bucket"

        with pytest.raises(AppException) as exc:
            get_storage_driver()
        assert "Unsupported StorageBackend configured: UNKNOWN" in exc.value.message
        assert exc.value.status_code == 500
        assert exc.value.details == {"error_code": ErrorCodes.CONFIGURATION_ERROR}


def test_get_storage_driver_none_backend_boundary() -> None:
    """Negative boundary test: a missing/None active_backend raises AppException with CONFIGURATION_ERROR."""
    with patch("backend_v2.services.storage.get_settings") as mock_get_settings:
        mock_settings = mock_get_settings.return_value
        mock_settings.active_backend = None
        mock_settings.storage_bucket_name = None

        with pytest.raises(AppException) as exc:
            get_storage_driver()
        assert "Unsupported StorageBackend configured: None" in exc.value.message
        assert exc.value.status_code == 500
        assert exc.value.details == {"error_code": ErrorCodes.CONFIGURATION_ERROR}
