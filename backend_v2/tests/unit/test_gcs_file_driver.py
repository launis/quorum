"""Unit tests for GCSFileDriver.

Validates Google Cloud Storage operations, lazy bucket initialization,
OS-independent blob streaming, Fail-Fast RFC 7807 error semantics,
and complete ISTQB branch/equivalence partitions.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.services.drivers.gcs_file_driver import GCSFileDriver


@pytest.fixture
def mock_storage() -> Any:
    """Fixture providing a mock google.cloud.storage module."""
    with patch("backend_v2.services.drivers.gcs_file_driver.storage") as mock_st:
        yield mock_st


@pytest.mark.asyncio
async def test_init_empty_bucket() -> None:
    """Verify initialization with empty bucket name raises AppException."""
    with pytest.raises(AppException) as exc_info:
        GCSFileDriver(bucket_name="")
    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.STORAGE_BUCKET_NOT_FOUND.value


@pytest.mark.asyncio
async def test_init_missing_library() -> None:
    """Verify initialization when google-cloud-storage is missing raises AppException."""
    with patch("backend_v2.services.drivers.gcs_file_driver.storage", new=None):
        with pytest.raises(AppException) as exc_info:
            GCSFileDriver(bucket_name="my-bucket")
        assert exc_info.value.status_code == 500
        assert exc_info.value.details["error_code"] == ErrorCodes.SERVICE_DEPENDENCY_MISSING.value


@pytest.mark.asyncio
async def test_get_bucket_lazy_caching(mock_storage: Any) -> None:
    """Verify lazy bucket instantiation and caching across repeated calls."""
    driver = GCSFileDriver(bucket_name="test-bucket")
    mock_client = MagicMock()
    mock_bucket = MagicMock()
    mock_storage.Client.return_value = mock_client
    mock_client.bucket.return_value = mock_bucket

    bucket1 = driver._get_bucket()
    bucket2 = driver._get_bucket()

    assert bucket1 is mock_bucket
    assert bucket2 is mock_bucket
    mock_storage.Client.assert_called_once()
    mock_client.bucket.assert_called_once_with("test-bucket")


@pytest.mark.asyncio
async def test_get_bucket_failure_raises_app_exception(mock_storage: Any) -> None:
    """Verify GCS client initialization failure raises AppException."""
    driver = GCSFileDriver(bucket_name="test-bucket")
    mock_storage.Client.side_effect = RuntimeError("GCP Credential discovery failed")

    with pytest.raises(AppException) as exc_info:
        driver._get_bucket()

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value


@pytest.mark.asyncio
async def test_get_url(mock_storage: Any) -> None:
    """Verify URL generation returns public HTTPS link."""
    driver = GCSFileDriver(bucket_name="test-bucket")
    url = await driver.get_url("path/to/file.txt")
    assert url == "https://storage.googleapis.com/test-bucket/path/to/file.txt"


@pytest.mark.asyncio
async def test_get_url_empty_bucket_raises(mock_storage: Any) -> None:
    """Verify get_url raises AppException when bucket_name is empty."""
    driver = GCSFileDriver(bucket_name="test-bucket")
    driver.bucket_name = ""

    with pytest.raises(AppException) as exc_info:
        await driver.get_url("path/to/file.txt")

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.STORAGE_BUCKET_NOT_FOUND.value


@pytest.mark.asyncio
async def test_save_string(mock_storage: Any) -> None:
    """Verify saving string data uses text/plain content type."""
    driver = GCSFileDriver(bucket_name="test-bucket")
    mock_client = MagicMock()
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    mock_storage.Client.return_value = mock_client
    mock_client.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob

    result = await driver.save("test.txt", "hello world")
    assert result == "gs://test-bucket/test.txt"
    mock_blob.upload_from_string.assert_called_once_with("hello world", content_type="text/plain")


@pytest.mark.asyncio
async def test_save_bytes(mock_storage: Any) -> None:
    """Verify saving bytes data uses application/octet-stream content type."""
    driver = GCSFileDriver(bucket_name="test-bucket")
    mock_client = MagicMock()
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    mock_storage.Client.return_value = mock_client
    mock_client.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob

    result = await driver.save("test.bin", b"\x00\x01\x02")
    assert result == "gs://test-bucket/test.bin"
    mock_blob.upload_from_string.assert_called_once_with(b"\x00\x01\x02", content_type="application/octet-stream")


@pytest.mark.asyncio
async def test_save_failure_raises_app_exception(mock_storage: Any) -> None:
    """Verify upload failure raises AppException."""
    driver = GCSFileDriver(bucket_name="test-bucket")
    mock_client = MagicMock()
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    mock_storage.Client.return_value = mock_client
    mock_client.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob
    mock_blob.upload_from_string.side_effect = RuntimeError("Network timeout")

    with pytest.raises(AppException) as exc_info:
        await driver.save("test.txt", "hello")

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value


@pytest.mark.asyncio
async def test_save_app_exception_reraises(mock_storage: Any) -> None:
    """Verify pre-existing AppException in save re-raises directly."""
    driver = GCSFileDriver(bucket_name="test-bucket")
    mock_storage.Client.side_effect = AppException(
        message="Client failed",
        status_code=500,
        details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
    )

    with pytest.raises(AppException) as exc_info:
        await driver.save("test.txt", "hello")

    assert exc_info.value.message == "Client failed"


@pytest.mark.asyncio
async def test_read_success(mock_storage: Any) -> None:
    """Verify reading existing blob returns raw bytes."""
    driver = GCSFileDriver(bucket_name="test-bucket")
    mock_client = MagicMock()
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    mock_storage.Client.return_value = mock_client
    mock_client.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob
    mock_blob.exists.return_value = True
    mock_blob.download_as_bytes.return_value = b"hello world"

    result = await driver.read("test.txt")
    assert result == b"hello world"
    mock_blob.download_as_bytes.assert_called_once()


@pytest.mark.asyncio
async def test_read_not_found(mock_storage: Any) -> None:
    """Verify reading non-existent blob raises 404 AppException."""
    driver = GCSFileDriver(bucket_name="test-bucket")
    mock_client = MagicMock()
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    mock_storage.Client.return_value = mock_client
    mock_client.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob
    mock_blob.exists.return_value = False

    with pytest.raises(AppException) as exc_info:
        await driver.read("missing.txt")

    assert exc_info.value.status_code == 404
    assert exc_info.value.details["error_code"] == ErrorCodes.FILE_NOT_FOUND.value


@pytest.mark.asyncio
async def test_read_failure_raises_app_exception(mock_storage: Any) -> None:
    """Verify read download error raises 500 AppException."""
    driver = GCSFileDriver(bucket_name="test-bucket")
    mock_client = MagicMock()
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    mock_storage.Client.return_value = mock_client
    mock_client.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob
    mock_blob.exists.return_value = True
    mock_blob.download_as_bytes.side_effect = RuntimeError("Corrupted stream")

    with pytest.raises(AppException) as exc_info:
        await driver.read("test.txt")

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value


@pytest.mark.asyncio
async def test_read_app_exception_reraises(mock_storage: Any) -> None:
    """Verify AppException during read re-raises cleanly."""
    driver = GCSFileDriver(bucket_name="test-bucket")
    mock_storage.Client.side_effect = AppException(
        message="Client failed",
        status_code=500,
        details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
    )

    with pytest.raises(AppException) as exc_info:
        await driver.read("test.txt")

    assert exc_info.value.message == "Client failed"


@pytest.mark.asyncio
async def test_delete_success(mock_storage: Any) -> None:
    """Verify deleting existing blob returns True."""
    driver = GCSFileDriver(bucket_name="test-bucket")
    mock_client = MagicMock()
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    mock_storage.Client.return_value = mock_client
    mock_client.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob
    mock_blob.exists.return_value = True

    result = await driver.delete("test.txt")
    assert result is True
    mock_blob.delete.assert_called_once()


@pytest.mark.asyncio
async def test_delete_not_found(mock_storage: Any) -> None:
    """Verify deleting non-existent blob raises 404 AppException."""
    driver = GCSFileDriver(bucket_name="test-bucket")
    mock_client = MagicMock()
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    mock_storage.Client.return_value = mock_client
    mock_client.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob
    mock_blob.exists.return_value = False

    with pytest.raises(AppException) as exc_info:
        await driver.delete("test.txt")

    assert exc_info.value.status_code == 404
    assert exc_info.value.details["error_code"] == ErrorCodes.FILE_NOT_FOUND.value


@pytest.mark.asyncio
async def test_delete_failure_raises_app_exception(mock_storage: Any) -> None:
    """Verify delete API error raises 500 AppException."""
    driver = GCSFileDriver(bucket_name="test-bucket")
    mock_client = MagicMock()
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    mock_storage.Client.return_value = mock_client
    mock_client.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob
    mock_blob.exists.return_value = True
    mock_blob.delete.side_effect = RuntimeError("Permission denied")

    with pytest.raises(AppException) as exc_info:
        await driver.delete("test.txt")

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value


@pytest.mark.asyncio
async def test_delete_app_exception_reraises(mock_storage: Any) -> None:
    """Verify AppException during delete re-raises cleanly."""
    driver = GCSFileDriver(bucket_name="test-bucket")
    mock_storage.Client.side_effect = AppException(
        message="Client failed",
        status_code=500,
        details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
    )

    with pytest.raises(AppException) as exc_info:
        await driver.delete("test.txt")

    assert exc_info.value.message == "Client failed"


@pytest.mark.asyncio
async def test_delete_directory_success(mock_storage: Any) -> None:
    """Verify deleting directory blobs with and without trailing slash."""
    driver = GCSFileDriver(bucket_name="test-bucket")
    mock_client = MagicMock()
    mock_bucket = MagicMock()
    blob1 = MagicMock()
    blob2 = MagicMock()
    mock_storage.Client.return_value = mock_client
    mock_client.bucket.return_value = mock_bucket
    mock_bucket.list_blobs.return_value = [blob1, blob2]

    # Without trailing slash
    result = await driver.delete_directory("reports/123")
    assert result is True
    mock_bucket.list_blobs.assert_called_with(prefix="reports/123/")
    mock_bucket.delete_blobs.assert_called_with([blob1, blob2])

    # With trailing slash
    result_slash = await driver.delete_directory("reports/123/")
    assert result_slash is True


@pytest.mark.asyncio
async def test_delete_directory_not_found(mock_storage: Any) -> None:
    """Verify deleting empty or non-existent directory raises 404 AppException."""
    driver = GCSFileDriver(bucket_name="test-bucket")
    mock_client = MagicMock()
    mock_bucket = MagicMock()
    mock_storage.Client.return_value = mock_client
    mock_client.bucket.return_value = mock_bucket
    mock_bucket.list_blobs.return_value = []

    with pytest.raises(AppException) as exc_info:
        await driver.delete_directory("missing/dir")

    assert exc_info.value.status_code == 404
    assert exc_info.value.details["error_code"] == ErrorCodes.FILE_NOT_FOUND.value


@pytest.mark.asyncio
async def test_delete_directory_failure_raises_app_exception(mock_storage: Any) -> None:
    """Verify delete_directory API failure raises 500 AppException."""
    driver = GCSFileDriver(bucket_name="test-bucket")
    mock_client = MagicMock()
    mock_bucket = MagicMock()
    blob1 = MagicMock()
    mock_storage.Client.return_value = mock_client
    mock_client.bucket.return_value = mock_bucket
    mock_bucket.list_blobs.return_value = [blob1]
    mock_bucket.delete_blobs.side_effect = RuntimeError("Batch delete failed")

    with pytest.raises(AppException) as exc_info:
        await driver.delete_directory("reports/123")

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value


@pytest.mark.asyncio
async def test_delete_directory_app_exception_reraises(mock_storage: Any) -> None:
    """Verify AppException during delete_directory re-raises cleanly."""
    driver = GCSFileDriver(bucket_name="test-bucket")
    mock_storage.Client.side_effect = AppException(
        message="Client failed",
        status_code=500,
        details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
    )

    with pytest.raises(AppException) as exc_info:
        await driver.delete_directory("reports/123")

    assert exc_info.value.message == "Client failed"


@pytest.mark.asyncio
async def test_exists_success(mock_storage: Any) -> None:
    """Verify exists returns True for present blob and False for absent blob."""
    driver = GCSFileDriver(bucket_name="test-bucket")
    mock_client = MagicMock()
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    mock_storage.Client.return_value = mock_client
    mock_client.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob

    mock_blob.exists.return_value = True
    assert await driver.exists("test.txt") is True

    mock_blob.exists.return_value = False
    assert await driver.exists("absent.txt") is False


@pytest.mark.asyncio
async def test_exists_failure_raises_app_exception(mock_storage: Any) -> None:
    """Verify exists API error raises 500 AppException."""
    driver = GCSFileDriver(bucket_name="test-bucket")
    mock_client = MagicMock()
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    mock_storage.Client.return_value = mock_client
    mock_client.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob
    mock_blob.exists.side_effect = RuntimeError("Connection dropped")

    with pytest.raises(AppException) as exc_info:
        await driver.exists("test.txt")

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value


@pytest.mark.asyncio
async def test_exists_app_exception_reraises(mock_storage: Any) -> None:
    """Verify AppException during exists re-raises cleanly."""
    driver = GCSFileDriver(bucket_name="test-bucket")
    mock_storage.Client.side_effect = AppException(
        message="Client failed",
        status_code=500,
        details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
    )

    with pytest.raises(AppException) as exc_info:
        await driver.exists("test.txt")

    assert exc_info.value.message == "Client failed"
