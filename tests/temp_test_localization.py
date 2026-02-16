import pytest
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from backend.services.localization import LocalizationService
from backend.exceptions import AppException, ErrorCodes

class TestLocalizationService:
    @pytest.fixture(autouse=True)
    def reset_service(self):
        """Reset service state before each test."""
        LocalizationService._translations = {}
        LocalizationService._loaded = False
        yield
        LocalizationService._translations = {}
        LocalizationService._loaded = False

    def test_load_missing_directory(self):
        """Test Fail Fast when l10n directory is missing."""
        # Point to non-existent path
        with patch.object(LocalizationService, 'L10N_DIR', Path("non_existent_dir")):
            with pytest.raises(AppException) as excinfo:
                LocalizationService.load_if_needed()
            
            assert excinfo.value.status_code == 500
            assert excinfo.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR
            assert "Localization directory not found" in excinfo.value.message

    def test_load_no_files(self, tmp_path):
        """Test Fail Fast when l10n directory is empty."""
        # Create empty temp dir
        with patch.object(LocalizationService, 'L10N_DIR', tmp_path):
            with pytest.raises(AppException) as excinfo:
                LocalizationService.load_if_needed()
            
            assert excinfo.value.status_code == 500
            assert excinfo.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR
            assert "No translation files found" in excinfo.value.message

    def test_missing_interpolation_arg(self):
        """Test Fail Fast when interpolation argument is missing."""
        # Mock translations
        LocalizationService._translations = {
            "en": {"greeting": "Hello {name}!"}
        }
        LocalizationService._loaded = True

        with pytest.raises(AppException) as excinfo:
            LocalizationService.translate("greeting", lang="en", wrong_arg="User")

        assert excinfo.value.status_code == 500
        assert excinfo.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR
        assert "missing argument 'name'" in excinfo.value.message
        print("\n[TEST] Missing Interpolation Arg: Fail Fast Successful")

    def test_success(self):
        """Test successful translation."""
        LocalizationService._translations = {
            "en": {"greeting": "Hello {name}!"}
        }
        LocalizationService._loaded = True

        result = LocalizationService.translate("greeting", lang="en", name="World")
        assert result == "Hello World!"
        print("\n[TEST] Success Case: Verified")

if __name__ == "__main__":
    pass
