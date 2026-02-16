import pytest
from backend.utils.identifiers import validate_identifier_format, generate_unique_id
from backend.exceptions import AppException, ErrorCodes

class TestIdentifiers:
    
    def test_generate_unique_id(self):
        """Verify generation logic."""
        # UUID fallback
        uid = generate_unique_id()
        assert len(uid) == 36 # UUID length
        
        # Base name
        uid = generate_unique_id("Test Name")
        assert uid.startswith("test-name-")
        assert len(uid) > 10
        validate_identifier_format(uid)

        # Edge case: Non-alphanumeric base name
        uid = generate_unique_id("!!!")
        # Should fall back to just UUID or handle gracefully, ensuring valid format
        validate_identifier_format(uid) # This will fail if it starts with hyphen

    def test_validate_identifier_format_success(self):
        """Verify success with valid inputs."""
        valid_ids = ["valid-id", "id123", "a-b-c", "123-456"]
        for i in valid_ids:
            validate_identifier_format(i)

    def test_validate_identifier_format_fail(self):
        """Verify failures."""
        invalid_ids = [
            "Invalid-Caps", 
            "spaces test", 
            "special$char", 
            "-start-dash", 
            "end-dash-", 
            ""
        ]
        
        for i in invalid_ids:
            with pytest.raises(AppException) as excinfo:
                validate_identifier_format(i)
            
            assert excinfo.value.status_code == 400
            # Empty is EMPTY_INPUT, others VALIDATION_FAILED
            if i == "":
                 assert excinfo.value.details["error_code"] == ErrorCodes.EMPTY_INPUT
            else:
                 assert excinfo.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED

if __name__ == "__main__":
    pass
