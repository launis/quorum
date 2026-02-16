import pytest
from backend.exceptions import (
    AppException,
    ErrorCodes,
    ResourceNotFoundError,
    WorkflowNotFoundError,
    ConfigurationError,
    PermissionDeniedError,
    AuthenticationError,
    SecurityViolationError,
    WorkflowExecutionError,
    FatalInterruption
)

class TestExceptions:

    def test_default_error_codes(self):
        """Verify that exception subclasses have correct default error codes."""
        
        # ConfigurationError
        exc = ConfigurationError("Bad config")
        assert exc.error_code == ErrorCodes.CONFIGURATION_ERROR
        assert exc.status_code == 500

        # PermissionDeniedError
        exc = PermissionDeniedError("No access")
        assert exc.error_code == ErrorCodes.PERMISSION_DENIED
        assert exc.status_code == 403

        # AuthenticationError
        exc = AuthenticationError("Who are you?")
        assert exc.error_code == ErrorCodes.AUTHENTICATION_FAILED
        assert exc.status_code == 401

        # SecurityViolationError
        exc = SecurityViolationError("Hacker?")
        assert exc.error_code == ErrorCodes.SECURITY_VIOLATION
        assert exc.status_code == 400

    def test_resource_not_found_defaults(self):
        """Verify ResourceNotFoundError hierarchy."""
        
        # Base
        exc = ResourceNotFoundError("Widget", "123")
        assert exc.error_code == ErrorCodes.RESOURCE_NOT_FOUND
        assert exc.status_code == 404

        # Specific
        exc = WorkflowNotFoundError("wf-1")
        assert exc.error_code == ErrorCodes.WORKFLOW_NOT_FOUND
        assert exc.status_code == 404

    def test_custom_error_code_override(self):
        """Verify explicit error code override works."""
        exc = ConfigurationError("Bad config", details={"error_code": "CUSTOM_CONFIG_ERROR"})
        assert exc.error_code == "CUSTOM_CONFIG_ERROR"

    def test_workflow_execution_error_defaults(self):
        """Verify WorkflowExecutionError defaults."""
        exc = WorkflowExecutionError("step-1", "task-1", Exception("Boom"))
        assert exc.error_code == ErrorCodes.WORKFLOW_EXECUTION_FAILED
        assert exc.status_code == 500

if __name__ == "__main__":
    pass
