"""Unit tests for the SlowAPI Rate Limiting handler module."""

from unittest.mock import MagicMock

import pytest
from fastapi import Request, status
from slowapi.errors import RateLimitExceeded

from backend_v2.core.rate_limit import rate_limit_exceeded_handler
from backend_v2.exceptions import AppException, ErrorCodes, ProblemDetailDTO


def test_rate_limit_exceeded_handler() -> None:
    """Verify happy-path RateLimitExceeded produces RFC 7807 ProblemDetailDTO with retry_after."""
    mock_request = MagicMock(spec=Request)
    mock_request.url.path = "/test"

    mock_limit = MagicMock()
    mock_limit.error_message = None
    mock_limit.limit = "1 per 1 minute"
    exc = RateLimitExceeded(mock_limit)
    response = rate_limit_exceeded_handler(mock_request, exc)

    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert response.media_type == "application/problem+json"

    problem = ProblemDetailDTO.model_validate_json(bytes(response.body))
    assert problem.status == status.HTTP_429_TOO_MANY_REQUESTS
    assert problem.instance == "/test"
    assert problem.extensions["error_code"] == ErrorCodes.RATE_LIMIT_EXCEEDED.value
    assert problem.extensions["retry_after"] == "1"


@pytest.mark.parametrize("blank_detail", ["", "   "])
def test_rate_limit_exceeded_handler_empty_or_whitespace_detail(blank_detail: str) -> None:
    """Verify boundary cases where exc.detail is empty or whitespace omit retry_after."""
    mock_request = MagicMock(spec=Request)
    mock_request.url.path = "/api/v2/workflows"

    mock_limit = MagicMock()
    mock_limit.error_message = None
    mock_limit.limit = "1 per 1 minute"
    exc = RateLimitExceeded(mock_limit)
    exc.detail = blank_detail

    response = rate_limit_exceeded_handler(mock_request, exc)

    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    problem = ProblemDetailDTO.model_validate_json(bytes(response.body))
    assert problem.extensions["error_code"] == ErrorCodes.RATE_LIMIT_EXCEEDED.value
    assert "retry_after" not in problem.extensions


@pytest.mark.parametrize("invalid_path", ["", "   "])
def test_rate_limit_exceeded_handler_invalid_request_path_raises(invalid_path: str) -> None:
    """Verify missing or whitespace request.url.path triggers Fail-Fast AppException."""
    mock_request = MagicMock(spec=Request)
    mock_request.url.path = invalid_path

    mock_limit = MagicMock()
    mock_limit.error_message = None
    mock_limit.limit = "5 per 1 minute"
    exc = RateLimitExceeded(mock_limit)

    with pytest.raises(AppException) as exc_info:
        rate_limit_exceeded_handler(mock_request, exc)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.error_code == ErrorCodes.VALIDATION_FAILED.value
