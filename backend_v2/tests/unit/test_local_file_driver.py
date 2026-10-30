"""Unit tests for LocalFileDriver."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.services.drivers.local_file_driver import LocalFileDriver
from backend_v2.settings import get_settings


def test_init_fails_fast_on_missing_directory() -> None:
    """Test that LocalFileDriver initialization fails fast if the base path does not exist."""
    with patch("backend_v2.services.drivers.local_file_driver.Path.exists", return_value=False):
        with pytest.raises(AppException) as exc_info:
            LocalFileDriver(base_path="/tmp/non_existent_dir_123")

        assert exc_info.value.status_code == 500
        assert exc_info.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value
        assert "does not exist or is not a directory" in exc_info.value.message


def test_init_fails_fast_on_not_a_directory() -> None:
    """Test that LocalFileDriver initialization fails fast if the base path is a file, not a directory."""
    with (
        patch("backend_v2.services.drivers.local_file_driver.Path.exists", return_value=True),
        patch("backend_v2.services.drivers.local_file_driver.Path.is_dir", return_value=False),
    ):
        with pytest.raises(AppException) as exc_info:
            LocalFileDriver(base_path="/tmp/i_am_a_file.txt")

        assert exc_info.value.status_code == 500
        assert exc_info.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value
        assert "does not exist or is not a directory" in exc_info.value.message


@pytest.mark.asyncio
async def test_save_creates_parent_directories_and_uses_atomic_write() -> None:
    """Test that save creates parent directories (cloud parity) and uses os.replace for atomic writes."""
    with (
        patch("backend_v2.services.drivers.local_file_driver.Path.exists") as mock_exists,
        patch("backend_v2.services.drivers.local_file_driver.Path.is_dir") as mock_is_dir,
        patch.object(LocalFileDriver, "_validate_path") as mock_validate,
        patch("backend_v2.services.drivers.local_file_driver.aiofiles.open") as mock_aiofiles_open,
        patch("backend_v2.services.drivers.local_file_driver.os.replace") as mock_os_replace,
    ):
        mock_exists.return_value = True
        mock_is_dir.return_value = True
        driver = LocalFileDriver(base_path="/tmp/valid_base")

        mock_path = MagicMock()
        mock_tmp_path = MagicMock()
        mock_path.with_name.return_value = mock_tmp_path
        mock_validate.return_value = mock_path

        mock_file = AsyncMock()
        mock_file_context = MagicMock()
        mock_file_context.__aenter__.return_value = mock_file
        mock_file_context.__aexit__.return_value = None
        mock_aiofiles_open.return_value = mock_file_context

        result = await driver.save("some/path.txt", b"data")

        assert result == str(mock_path)
        mock_path.parent.mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_os_replace.assert_called_once_with(mock_tmp_path, mock_path)
        mock_file.write.assert_called_once_with(b"data")


@pytest.mark.asyncio
async def test_delete_file_success_via_thread() -> None:
    """Positive: delete removes existing file using threadpool offloading."""
    with (
        patch("backend_v2.services.drivers.local_file_driver.Path.exists", return_value=True),
        patch("backend_v2.services.drivers.local_file_driver.Path.is_dir", return_value=True),
        patch.object(LocalFileDriver, "_validate_path") as mock_validate,
        patch("backend_v2.services.drivers.local_file_driver.os.remove") as mock_os_remove,
    ):
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_validate.return_value = mock_path

        driver = LocalFileDriver(base_path="/tmp/valid_base")
        success = await driver.delete("some/file.txt")

        assert success is True
        mock_os_remove.assert_called_once_with(mock_path)


@pytest.mark.asyncio
async def test_delete_file_missing_fails_fast() -> None:
    """Negative: delete on non-existent file fails fast with 404 FILE_NOT_FOUND."""
    with (
        patch("backend_v2.services.drivers.local_file_driver.Path.exists", return_value=True),
        patch("backend_v2.services.drivers.local_file_driver.Path.is_dir", return_value=True),
        patch.object(LocalFileDriver, "_validate_path") as mock_validate,
    ):
        mock_path = MagicMock()
        mock_path.exists.return_value = False
        mock_validate.return_value = mock_path

        driver = LocalFileDriver(base_path="/tmp/valid_base")
        with pytest.raises(AppException) as excinfo:
            await driver.delete("missing/file.txt")

        assert excinfo.value.status_code == 404
        assert excinfo.value.details["error_code"] == ErrorCodes.FILE_NOT_FOUND.value


@pytest.mark.asyncio
async def test_delete_file_locked_fails_fast_409() -> None:
    """Negative / Error-Path: PermissionError on os.remove converts to 409 FILE_LOCKED_ERROR in English."""
    with (
        patch("backend_v2.services.drivers.local_file_driver.Path.exists", return_value=True),
        patch("backend_v2.services.drivers.local_file_driver.Path.is_dir", return_value=True),
        patch.object(LocalFileDriver, "_validate_path") as mock_validate,
        patch(
            "backend_v2.services.drivers.local_file_driver.os.remove",
            side_effect=PermissionError("Locked by OS"),
        ),
    ):
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_validate.return_value = mock_path

        driver = LocalFileDriver(base_path="/tmp/valid_base")
        with pytest.raises(AppException) as excinfo:
            await driver.delete("locked/file.txt")

        assert excinfo.value.status_code == 409
        assert excinfo.value.details["error_code"] == ErrorCodes.FILE_LOCKED_ERROR.value
        assert "File is locked by another process" in excinfo.value.message


def test_init_fails_fast_on_empty_base_path() -> None:
    """Negative: empty base_path triggers STORAGE_CONFIG_ERROR."""
    with pytest.raises(AppException) as excinfo:
        LocalFileDriver(base_path="")

    assert excinfo.value.status_code == 500
    assert excinfo.value.details["error_code"] == ErrorCodes.STORAGE_CONFIG_ERROR.value


def test_validate_path_valid_empty_traversal_and_unexpected_error(tmp_path: Path) -> None:
    """Positive and negative boundary tests for _validate_path."""
    driver = LocalFileDriver(base_path=str(tmp_path))

    resolved = driver._validate_path("nested/report.pdf")
    assert resolved == (tmp_path / "nested" / "report.pdf").resolve()

    with pytest.raises(AppException) as exc_empty:
        driver._validate_path("   ")
    assert exc_empty.value.status_code == 400
    assert exc_empty.value.details["error_code"] == ErrorCodes.FILESYSTEM_VIOLATION.value

    with pytest.raises(AppException) as exc_trav:
        driver._validate_path("../../etc/passwd")
    assert exc_trav.value.status_code == 400
    assert exc_trav.value.details["error_code"] == ErrorCodes.FILESYSTEM_VIOLATION.value

    with patch.object(Path, "is_relative_to", side_effect=ValueError("Unexpected path resolution failure")):
        with pytest.raises(AppException) as exc_generic:
            driver._validate_path("nested/file.txt")
        assert exc_generic.value.status_code == 400
        assert exc_generic.value.details["error_code"] == ErrorCodes.FILESYSTEM_VIOLATION.value


@pytest.mark.asyncio
async def test_save_string_data() -> None:
    """Positive: save handles string data by opening file in text mode."""
    with (
        patch("backend_v2.services.drivers.local_file_driver.Path.exists", return_value=True),
        patch("backend_v2.services.drivers.local_file_driver.Path.is_dir", return_value=True),
        patch.object(LocalFileDriver, "_validate_path") as mock_validate,
        patch("backend_v2.services.drivers.local_file_driver.aiofiles.open") as mock_aiofiles_open,
        patch("backend_v2.services.drivers.local_file_driver.os.replace"),
    ):
        mock_path = MagicMock()
        mock_tmp_path = MagicMock()
        mock_path.with_name.return_value = mock_tmp_path
        mock_validate.return_value = mock_path

        mock_file = AsyncMock()
        mock_ctx = MagicMock()
        mock_ctx.__aenter__.return_value = mock_file
        mock_ctx.__aexit__.return_value = None
        mock_aiofiles_open.return_value = mock_ctx

        driver = LocalFileDriver(base_path="/tmp/valid_base")
        res = await driver.save("doc.txt", "hello string")

        assert res == str(mock_path)
        mock_file.write.assert_called_once_with("hello string")


@pytest.mark.asyncio
async def test_read_success_and_missing() -> None:
    """Positive and negative tests for read."""
    with (
        patch("backend_v2.services.drivers.local_file_driver.Path.exists", return_value=True),
        patch("backend_v2.services.drivers.local_file_driver.Path.is_dir", return_value=True),
        patch.object(LocalFileDriver, "_validate_path") as mock_validate,
        patch("backend_v2.services.drivers.local_file_driver.aiofiles.open") as mock_aiofiles_open,
    ):
        mock_path = MagicMock()
        mock_path.exists.return_value = False
        mock_validate.return_value = mock_path

        driver = LocalFileDriver(base_path="/tmp/valid_base")
        with pytest.raises(AppException) as exc_missing:
            await driver.read("non_existent.txt")
        assert exc_missing.value.status_code == 404
        assert exc_missing.value.details["error_code"] == ErrorCodes.FILE_NOT_FOUND.value

        mock_path.exists.return_value = True
        mock_file = AsyncMock()
        mock_file.read.return_value = b"binary content"
        mock_ctx = MagicMock()
        mock_ctx.__aenter__.return_value = mock_file
        mock_ctx.__aexit__.return_value = None
        mock_aiofiles_open.return_value = mock_ctx

        data = await driver.read("existent.txt")
        assert data == b"binary content"


@pytest.mark.asyncio
async def test_delete_directory_success_and_failures() -> None:
    """Tests for delete_directory."""
    with (
        patch("backend_v2.services.drivers.local_file_driver.Path.exists", return_value=True),
        patch("backend_v2.services.drivers.local_file_driver.Path.is_dir", return_value=True),
        patch.object(LocalFileDriver, "_validate_path") as mock_validate,
        patch("backend_v2.services.drivers.local_file_driver.shutil.rmtree") as mock_rmtree,
    ):
        mock_path = MagicMock()
        driver = LocalFileDriver(base_path="/tmp/valid_base")

        mock_path.exists.return_value = False
        mock_validate.return_value = mock_path
        with pytest.raises(AppException) as exc_missing:
            await driver.delete_directory("missing_dir")
        assert exc_missing.value.status_code == 404

        mock_path.exists.return_value = True
        mock_path.is_dir.return_value = False
        with pytest.raises(AppException) as exc_notdir:
            await driver.delete_directory("not_a_dir")
        assert exc_notdir.value.status_code == 400

        mock_path.is_dir.return_value = True
        success = await driver.delete_directory("real_dir")
        assert success is True
        mock_rmtree.assert_called_once_with(mock_path)


@pytest.mark.asyncio
async def test_exists_and_get_url() -> None:
    """Test exists and get_url methods using centralized settings base URL."""
    settings = get_settings()
    configured_base_url = f"{settings.api_url}/files"
    with (
        patch("backend_v2.services.drivers.local_file_driver.Path.exists", return_value=True),
        patch("backend_v2.services.drivers.local_file_driver.Path.is_dir", return_value=True),
        patch.object(LocalFileDriver, "_validate_path") as mock_validate,
    ):
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_validate.return_value = mock_path

        driver = LocalFileDriver(base_path="/tmp/valid_base", base_url=configured_base_url)
        assert await driver.exists("test.txt") is True

        url = await driver.get_url("test.txt")
        assert url == f"{configured_base_url.rstrip('/')}/test.txt"

        driver_no_url = LocalFileDriver(base_path="/tmp/valid_base")
        with pytest.raises(AppException) as exc_url:
            await driver_no_url.get_url("test.txt")
        assert exc_url.value.status_code == 500
        assert exc_url.value.details["error_code"] == ErrorCodes.STORAGE_CONFIG_ERROR.value


@pytest.mark.asyncio
async def test_save_locked_retry_and_exhaustion() -> None:
    """Error-Path: save retries os.replace on PermissionError and fails with 409 after retries."""
    with (
        patch("backend_v2.services.drivers.local_file_driver.Path.exists", return_value=True),
        patch("backend_v2.services.drivers.local_file_driver.Path.is_dir", return_value=True),
        patch.object(LocalFileDriver, "_validate_path") as mock_validate,
        patch("backend_v2.services.drivers.local_file_driver.aiofiles.open") as mock_aiofiles_open,
        patch(
            "backend_v2.services.drivers.local_file_driver.os.replace",
            side_effect=PermissionError("Locked file"),
        ),
        patch("backend_v2.services.drivers.local_file_driver.asyncio.sleep", return_value=None),
    ):
        mock_path = MagicMock()
        mock_tmp_path = MagicMock()
        mock_path.with_name.return_value = mock_tmp_path
        mock_validate.return_value = mock_path

        mock_file = AsyncMock()
        mock_ctx = MagicMock()
        mock_ctx.__aenter__.return_value = mock_file
        mock_ctx.__aexit__.return_value = None
        mock_aiofiles_open.return_value = mock_ctx

        driver = LocalFileDriver(base_path="/tmp/valid_base")
        with pytest.raises(AppException) as excinfo:
            await driver.save("doc.txt", b"bytes")

        assert excinfo.value.status_code == 409
        assert excinfo.value.details["error_code"] == ErrorCodes.FILE_LOCKED_ERROR.value


@pytest.mark.asyncio
async def test_read_locked_retry_and_exhaustion() -> None:
    """Error-Path: read retries aiofiles.open on PermissionError and fails with 409."""
    with (
        patch("backend_v2.services.drivers.local_file_driver.Path.exists", return_value=True),
        patch("backend_v2.services.drivers.local_file_driver.Path.is_dir", return_value=True),
        patch.object(LocalFileDriver, "_validate_path") as mock_validate,
        patch(
            "backend_v2.services.drivers.local_file_driver.aiofiles.open",
            side_effect=PermissionError("Locked file"),
        ),
        patch("backend_v2.services.drivers.local_file_driver.asyncio.sleep", return_value=None),
    ):
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_validate.return_value = mock_path

        driver = LocalFileDriver(base_path="/tmp/valid_base")
        with pytest.raises(AppException) as excinfo:
            await driver.read("doc.txt")

        assert excinfo.value.status_code == 409
        assert excinfo.value.details["error_code"] == ErrorCodes.FILE_LOCKED_ERROR.value


@pytest.mark.asyncio
async def test_delete_directory_locked_fails_409() -> None:
    """Error-Path: delete_directory fails with 409 on PermissionError."""
    with (
        patch("backend_v2.services.drivers.local_file_driver.Path.exists", return_value=True),
        patch("backend_v2.services.drivers.local_file_driver.Path.is_dir", return_value=True),
        patch.object(LocalFileDriver, "_validate_path") as mock_validate,
        patch(
            "backend_v2.services.drivers.local_file_driver.shutil.rmtree",
            side_effect=PermissionError("Locked directory"),
        ),
    ):
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_path.is_dir.return_value = True
        mock_validate.return_value = mock_path

        driver = LocalFileDriver(base_path="/tmp/valid_base")
        with pytest.raises(AppException) as excinfo:
            await driver.delete_directory("locked_dir")

        assert excinfo.value.status_code == 409
        assert excinfo.value.details["error_code"] == ErrorCodes.FILE_LOCKED_ERROR.value


@pytest.mark.asyncio
async def test_generic_io_exceptions_fail_fast_500() -> None:
    """Error-Path: unexpected OS/IO errors in save, read, delete, delete_directory raise 500 STORAGE_ACCESS_FAILED."""
    with (
        patch("backend_v2.services.drivers.local_file_driver.Path.exists", return_value=True),
        patch("backend_v2.services.drivers.local_file_driver.Path.is_dir", return_value=True),
        patch.object(LocalFileDriver, "_validate_path") as mock_validate,
    ):
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_path.is_dir.return_value = True
        mock_tmp_path = MagicMock()
        mock_path.with_name.return_value = mock_tmp_path
        mock_validate.return_value = mock_path

        driver = LocalFileDriver(base_path="/tmp/valid_base")

        with patch("backend_v2.services.drivers.local_file_driver.aiofiles.open", side_effect=OSError("Write fault")):
            with pytest.raises(AppException) as exc_save:
                await driver.save("test.txt", b"data")
            assert exc_save.value.status_code == 500

        with patch("backend_v2.services.drivers.local_file_driver.aiofiles.open", side_effect=OSError("Read fault")):
            with pytest.raises(AppException) as exc_read:
                await driver.read("test.txt")
            assert exc_read.value.status_code == 500

        with patch("backend_v2.services.drivers.local_file_driver.os.remove", side_effect=OSError("Delete fault")):
            with pytest.raises(AppException) as exc_del:
                await driver.delete("test.txt")
            assert exc_del.value.status_code == 500

        with patch("backend_v2.services.drivers.local_file_driver.shutil.rmtree", side_effect=OSError("Rmtree fault")):
            with pytest.raises(AppException) as exc_rmtree:
                await driver.delete_directory("test_dir")
            assert exc_rmtree.value.status_code == 500
