"""Unit tests for forensic storage path utilities."""

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.utils.paths import get_forensic_input_path


def test_get_forensic_input_path() -> None:
    """Verify special characters are stripped while preserving valid key characters."""
    path = get_forensic_input_path("exec123", "test-key-!@#")
    assert path == "executions/exec123/inputs/input_test-key-.md"


def test_get_forensic_input_path_valid_alphanumeric_and_separators() -> None:
    """Verify standard execution_id and alphanumeric/underscore/hyphen input_key."""
    path = get_forensic_input_path("exe_a1b2c3d4e5f60718", "doc_01-primary")
    assert path == "executions/exe_a1b2c3d4e5f60718/inputs/input_doc_01-primary.md"


@pytest.mark.parametrize("invalid_exec_id", ["", "   ", "../etc", "exec/123", "exec\\123"])
def test_get_forensic_input_path_invalid_execution_id_raises(invalid_exec_id: str) -> None:
    """Verify empty, whitespace, or path-traversal execution_id triggers AppException."""
    with pytest.raises(AppException) as exc_info:
        get_forensic_input_path(invalid_exec_id, "valid_key")
    assert exc_info.value.status_code == 400
    assert exc_info.value.error_code == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.parametrize("invalid_input_key", ["", "   ", "!@#$%^&*()", "../.."])
def test_get_forensic_input_path_invalid_or_empty_sanitized_key_raises(invalid_input_key: str) -> None:
    """Verify empty or symbol-only input_key that sanitizes to empty string triggers AppException."""
    with pytest.raises(AppException) as exc_info:
        get_forensic_input_path("exec123", invalid_input_key)
    assert exc_info.value.status_code == 400
    assert exc_info.value.error_code == ErrorCodes.VALIDATION_FAILED.value
