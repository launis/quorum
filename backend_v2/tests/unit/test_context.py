from unittest.mock import AsyncMock
import pytest

from backend_v2.context import (
    clear_execution_context,
    clear_request_context,
    get_execution_context,
    get_request_context,
    set_execution_context,
    set_request_context,
)
from backend_v2.exceptions import AppException, ErrorCodes


def test_execution_context_success() -> None:
    """Test setting and getting the execution context."""
    set_execution_context("exe_123")
    assert get_execution_context() == "exe_123"
    clear_execution_context()
    assert get_execution_context() is None


def test_execution_context_fail_fast_empty() -> None:
    """Test that setting an empty execution context raises an AppException."""
    with pytest.raises(AppException) as exc_info:
        set_execution_context("")

    assert exc_info.value.status_code == 500
    assert exc_info.value.error_code == ErrorCodes.INTERNAL_SERVER_ERROR


def test_execution_context_fail_fast_whitespace() -> None:
    """Test that setting a whitespace execution context raises an AppException."""
    with pytest.raises(AppException) as exc_info:
        set_execution_context("   ")

    assert exc_info.value.status_code == 500
    assert exc_info.value.error_code == ErrorCodes.INTERNAL_SERVER_ERROR


def test_request_context_success() -> None:
    """Test setting and getting the request context."""
    set_request_context("req_123")
    assert get_request_context() == "req_123"
    clear_request_context()
    assert get_request_context() is None


def test_request_context_fail_fast_empty() -> None:
    """Test that setting an empty request context raises an AppException."""
    with pytest.raises(AppException) as exc_info:
        set_request_context("")

    assert exc_info.value.status_code == 500
    assert exc_info.value.error_code == ErrorCodes.INTERNAL_SERVER_ERROR


def test_request_context_fail_fast_whitespace() -> None:
    """Test that setting a whitespace request context raises an AppException."""
    with pytest.raises(AppException) as exc_info:
        set_request_context("   ")

    assert exc_info.value.status_code == 500
    assert exc_info.value.error_code == ErrorCodes.INTERNAL_SERVER_ERROR
