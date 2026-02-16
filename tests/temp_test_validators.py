import pytest
from backend.schemas.validators import validate_content_structure
from backend.exceptions import AppException, ErrorCodes

class TestValidators:
    
    def test_validate_content_structure_success(self):
        """Verify success with valid inputs."""
        valid_text = "a" * 101
        # Should not raise
        validate_content_structure(valid_text, valid_text, valid_text, min_chars=100)

    def test_validate_content_structure_fail_missing(self):
        """Verify failure with missing input."""
        with pytest.raises(AppException) as excinfo:
            validate_content_structure(None, "ok", "ok", min_chars=1)
            
        assert excinfo.value.status_code == 422
        assert excinfo.value.details["error_code"] == ErrorCodes.INVALID_JSON_PAYLOAD
        assert "Field 'history_text' is missing" in excinfo.value.details["validation_errors"][0]

    def test_validate_content_structure_fail_short(self):
        """Verify failure with short input."""
        short_text = "short"
        with pytest.raises(AppException) as excinfo:
            validate_content_structure(short_text, short_text, short_text, min_chars=100)
            
        assert excinfo.value.details["error_code"] == ErrorCodes.INVALID_JSON_PAYLOAD
        assert "is too short" in excinfo.value.details["validation_errors"][0]

if __name__ == "__main__":
    pass
