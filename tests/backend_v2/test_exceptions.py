"""Unit tests for backend_v2/exceptions.py."""

from backend_v2.exceptions import AppException, ErrorCodes, MissingRoutingModeError, MissingXaiExtensionError


def test_missing_xai_extension_error():
    """Test MissingXaiExtensionError formatting."""
    exc = MissingXaiExtensionError(extension_name="citation", step_id="step_1")
    assert exc.details["error_code"] == ErrorCodes.MISSING_XAI_EXTENSION
    assert "citation" in exc.message
    assert exc.details["step_id"] == "step_1"


def test_missing_routing_mode_error():
    """Test MissingRoutingModeError formatting."""
    exc = MissingRoutingModeError(mapping_path="$steps.step_A")
    assert exc.details["error_code"] == ErrorCodes.MISSING_ROUTING_MODE
    assert "$steps.step_A" in exc.message
