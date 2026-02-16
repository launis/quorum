import pytest
from backend.core.security import validate_no_banned_phrases, check_banned_phrases
from backend.exceptions import AppException, ErrorCodes

class TestSecurity:
    
    def test_check_banned_phrases_logic(self):
        """Verify basic detection logic."""
        text = "This contains badword1 and normal text."
        banned = ["badword1", "badword2"]
        detected = check_banned_phrases(text, banned)
        assert "badword1" in detected
        assert "badword2" not in detected

    def test_validate_no_banned_phrases_success(self):
        """Verify success when no phrases found."""
        text = "Clean text."
        banned = ["badword"]
        validate_no_banned_phrases(text, banned) # Should not raise

    def test_validate_no_banned_phrases_fail_fast(self):
        """Verify Fail Fast raises AppException."""
        text = "This has a banned phrase."
        banned = ["banned phrase"]
        
        with pytest.raises(AppException) as excinfo:
            validate_no_banned_phrases(text, banned)
            
        assert excinfo.value.status_code == 400
        assert excinfo.value.details["error_code"] == ErrorCodes.SECURITY_VIOLATION
        assert "banned phrase" in excinfo.value.details["banned_phrases"]

if __name__ == "__main__":
    pass
