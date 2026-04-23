import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

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
async def test_save_fails_fast_on_missing_parent_directory() -> None:
    """Test that save fails fast and does NOT silently create parent directories."""
    
    with patch("pathlib.Path.exists") as mock_exists, \
         patch("pathlib.Path.is_dir") as mock_is_dir, \
         patch.object(LocalFileDriver, '_validate_path') as mock_validate:
        
        # Init succeeds
        mock_exists.return_value = True
        mock_is_dir.return_value = True
        driver = LocalFileDriver(base_path="/tmp/valid_base")
        
        # When saving, mock the parent directory existence to return False
        mock_path = MagicMock()
        mock_path.parent.exists.return_value = False
        mock_validate.return_value = mock_path
        
        with pytest.raises(AppException) as exc_info:
            await driver.save("some/path.txt", b"data")
            
        assert exc_info.value.status_code == 500
        assert exc_info.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value
        assert "Parent directory for some/path.txt does not exist" in exc_info.value.message
