import pytest
from unittest.mock import MagicMock, patch
import os
from backend.logging_config import setup_logging
from backend.exceptions import AppException, ErrorCodes

class TestLoggingConfig:

    def test_setup_logging_fail_fast_on_dir_creation(self):
        """Verify setup_logging raises AppException if log directory creation fails."""
        
        # Mock settings to return a path
        with patch("backend.settings.get_settings") as mock_settings_getter:
            mock_settings = MagicMock()
            mock_settings.log_file_path = "/invalid/path/backend.log"
            mock_settings.environment = "development"
            mock_settings.use_json_logging = False
            mock_settings_getter.return_value = mock_settings

            # Mock os.makedirs to raise PermissionError
            with patch("os.makedirs", side_effect=PermissionError("Permission denied")):
                with patch("os.path.exists", return_value=False): # Force directory creation attempt
                     with pytest.raises(AppException) as excinfo:
                        setup_logging()
                    
                     assert excinfo.value.status_code == 500
                     assert excinfo.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR
                     assert "FAILED TO CREATE LOG DIRECTORY" in excinfo.value.message

    def test_setup_logging_success(self):
        """Verify successful logging setup."""
        with patch("backend.settings.get_settings") as mock_settings_getter:
            mock_settings = MagicMock()
            mock_settings.log_file_path = "backend.log"
            mock_settings.environment = "development"
            mock_settings.use_json_logging = False
            mock_settings_getter.return_value = mock_settings

            with patch("os.makedirs"): 
                with patch("logging.FileHandler") as MockFileHandler:
                    # Fix TypeError >=' not supported between 'int' and 'MagicMock'
                    # logging module checks handler.level
                    MockFileHandler.return_value.level = 0 
                    try:
                        setup_logging()
                    except Exception as e:
                        pytest.fail(f"setup_logging raised unexpected exception: {e}")

if __name__ == "__main__":
    pass
