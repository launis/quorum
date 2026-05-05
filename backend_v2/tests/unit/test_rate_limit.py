import json
from unittest.mock import MagicMock

from fastapi import Request
from slowapi.errors import RateLimitExceeded

from backend_v2.core.rate_limit import rate_limit_exceeded_handler


def test_rate_limit_exceeded_handler() -> None:
    mock_request = MagicMock(spec=Request)
    mock_request.url.path = "/test-path"

    exc = MagicMock(spec=RateLimitExceeded)
    exc.detail = "1 per 1 minute"
    response = rate_limit_exceeded_handler(mock_request, exc)

    assert response.status_code == 429
    data = json.loads(response.body)  # type: ignore
    assert data["status"] == 429
    assert data["type"] == "https://api.quorum.fi/errors/rate-limit-exceeded"
    assert data["extensions"]["error_code"] == "RATE_LIMIT_EXCEEDED"
    assert data["extensions"]["retry_after"] == "1"
