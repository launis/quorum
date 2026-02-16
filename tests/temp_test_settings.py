import pytest
import os
from unittest.mock import patch
from backend.settings import Settings, StorageBackend
from backend.exceptions import AppException, ErrorCodes

class TestSettings:
    
    def test_settings_fail_fast_missing_llm_creds(self):
        """Verify settings raises AppException if no LLM creds are found (and not mock)."""
        # Clear env vars
        with patch.dict(os.environ, {}, clear=True):
            # Mock os.path.exists to return False so it doesn't find service-account.json
            with patch("os.path.exists", return_value=False):
                # We must set USE_MOCK_LLM=False to trigger the check
                with pytest.raises(AppException) as excinfo:
                    Settings(use_mock_llm=False, google_api_key=None, vertex_project_id=None)
                
                assert excinfo.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR
                assert "No LLM Credentials" in excinfo.value.message

    def test_settings_fail_fast_invalid_storage(self):
        """Verify invalid storage backend raises AppException."""
        # Using mock LLM to pass that check, but ensure use_mock_db is False
        s = Settings(use_mock_llm=True, use_mock_db=False, storage_backend="INVALID_BACKEND")
        
        with pytest.raises(AppException) as excinfo:
            _ = s.active_backend
            
        assert excinfo.value.status_code == 500
        assert excinfo.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR

if __name__ == "__main__":
    pass
