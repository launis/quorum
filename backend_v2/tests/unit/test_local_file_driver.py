from unittest.mock import MagicMock, patch

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.services.drivers.local_file_driver import LocalFileDriver


def test_init_fails_fast_on_missing_directory() -> None:
    """Test that LocalFileDriver initialization fails fast if the base path does not exist."""
    with patch("pathlib.Path.exists", return_value=False):
        with pytest.raises(AppException) as exc_info:
            LocalFileDriver(base_path="/tmp/non_existent_dir_123")

        assert exc_info.value.status_code == 500
        assert exc_info.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value
        assert "does not exist or is not a directory" in exc_info.value.message


def test_init_fails_fast_on_not_a_directory() -> None:
    """Test that LocalFileDriver initialization fails fast if the base path is a file, not a directory."""
    with patch("pathlib.Path.exists", return_value=True), patch("pathlib.Path.is_dir", return_value=False):
        with pytest.raises(AppException) as exc_info:
            LocalFileDriver(base_path="/tmp/i_am_a_file.txt")

        assert exc_info.value.status_code == 500
        assert exc_info.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value
        assert "does not exist or is not a directory" in exc_info.value.message


@pytest.mark.asyncio
async def test_save_creates_parent_directories_and_uses_atomic_write() -> None:
    """Test that save creates parent directories (cloud parity) and uses os.replace for atomic writes."""
    with (
        patch("pathlib.Path.exists") as mock_exists,
        patch("pathlib.Path.is_dir") as mock_is_dir,
        patch.object(LocalFileDriver, "_validate_path") as mock_validate,
        patch("aiofiles.open") as mock_aiofiles_open,
        patch("os.replace") as mock_os_replace,
    ):
        # Init succeeds
        mock_exists.return_value = True
        mock_is_dir.return_value = True
        driver = LocalFileDriver(base_path="/tmp/valid_base")

        # When saving, mock the path operations
        mock_path = MagicMock()
        mock_tmp_path = MagicMock()
        mock_path.with_name.return_value = mock_tmp_path
        mock_validate.return_value = mock_path

        # Mock aiofiles.open context manager
        from unittest.mock import AsyncMock

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
