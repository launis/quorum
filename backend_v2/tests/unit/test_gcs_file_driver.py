import pytest
from unittest.mock import MagicMock, patch

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.services.drivers.gcs_file_driver import GCSFileDriver

@pytest.fixture
def mock_storage():
    with patch("backend_v2.services.drivers.gcs_file_driver.storage") as mock_storage:
        yield mock_storage

@pytest.mark.asyncio
async def test_init_empty_bucket():
    with pytest.raises(AppException) as exc_info:
        GCSFileDriver(bucket_name="")
    assert exc_info.value.details["error_code"] == ErrorCodes.STORAGE_BUCKET_NOT_FOUND.value

@pytest.mark.asyncio
async def test_init_missing_library():
    with patch("backend_v2.services.drivers.gcs_file_driver.storage", new=None):
        with pytest.raises(AppException) as exc_info:
            GCSFileDriver(bucket_name="my-bucket")
        assert exc_info.value.details["error_code"] == ErrorCodes.SERVICE_DEPENDENCY_MISSING.value

@pytest.mark.asyncio
async def test_get_url(mock_storage):
    driver = GCSFileDriver(bucket_name="test-bucket")
    url = await driver.get_url("path/to/file.txt")
    assert url == "https://storage.googleapis.com/test-bucket/path/to/file.txt"

@pytest.mark.asyncio
async def test_exists_success(mock_storage):
    driver = GCSFileDriver(bucket_name="test-bucket")
    
    # Mocking the client/bucket/blob chain
    mock_client = MagicMock()
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    
    mock_storage.Client.return_value = mock_client
    mock_client.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob
    mock_blob.exists.return_value = True

    result = await driver.exists("test.txt")
    assert result is True
    mock_blob.exists.assert_called_once()

@pytest.mark.asyncio
async def test_delete_success(mock_storage):
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
async def test_delete_not_found(mock_storage):
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
async def test_save_string(mock_storage):
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
async def test_read_success(mock_storage):
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
