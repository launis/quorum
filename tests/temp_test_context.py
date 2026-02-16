import pytest
from backend.context import (
    set_execution_context,
    get_execution_context,
    clear_execution_context,
    set_request_context,
    get_request_context,
    clear_request_context
)
from backend.exceptions import AppException, ErrorCodes

class TestContextManager:

    def test_execution_context_success(self):
        """Test setting and getting execution context."""
        set_execution_context("exec-123")
        assert get_execution_context() == "exec-123"
        clear_execution_context()
        assert get_execution_context() is None

    def test_execution_context_fail_fast(self):
        """Test Fail Fast for empty execution ID."""
        with pytest.raises(AppException) as excinfo:
            set_execution_context("")
        
        assert excinfo.value.status_code == 500
        assert excinfo.value.details["error_code"] == ErrorCodes.INTERNAL_SERVER_ERROR
        assert "empty execution context" in excinfo.value.message

    def test_request_context_success(self):
        """Test setting and getting request context."""
        set_request_context("req-abc")
        assert get_request_context() == "req-abc"
        clear_request_context()
        assert get_request_context() is None

    def test_request_context_fail_fast(self):
        """Test Fail Fast for empty request ID."""
        with pytest.raises(AppException) as excinfo:
            set_request_context("   ")
        
        assert excinfo.value.status_code == 500
        assert excinfo.value.details["error_code"] == ErrorCodes.INTERNAL_SERVER_ERROR
        assert "empty request context" in excinfo.value.message
        print("\n[TEST] Invalid Context: Fail Fast Successful")

if __name__ == "__main__":
    pass
