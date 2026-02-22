import json
from unittest.mock import MagicMock

from fastapi import Request
from slowapi.errors import RateLimitExceeded

from backend.core.rate_limit import rate_limit_exceeded_handler


def test_rate_limit_handler_structure():
    """Verify rate limit handler returns RFC 7807 structure."""
    # Mock Request
    request = MagicMock(spec=Request)
    request.url.path = "/auth/login"

    # Mock Exception
    limit = MagicMock()
    limit.limit = "5/minute"  # String representation
    limit.error_message = None

    # SlowAPI RateLimitExceeded expects a Limit-like object
    exc = RateLimitExceeded(limit)
    # Monkey-patch detail which SlowAPI usually sets or we expect handler to use
    exc.detail = "5/minute"

    # Call Handler
    response = rate_limit_exceeded_handler(request, exc)

    # Verify Status Code
    assert response.status_code == 429
    assert response.media_type == "application/problem+json"

    # Verify Content
    content = json.loads(response.body)

    # RFC 7807 Fields
    assert content["type"] == "https://api.quorum.fi/errors/rate-limit-exceeded"
    assert content["title"] == "Rate Limit Exceeded"
    assert content["status"] == 429
    assert "Rate limit exceeded: 5/minute" in content["detail"]
    assert content["instance"] == "/auth/login"

    # Extensions
    assert content["extensions"]["retry_after"] == "5/minute"


def test_rate_limit_handler_unknown_detail():
    """Verify handler handles missing detail gracefully."""
    request = MagicMock(spec=Request)
    request.url.path = "/api/test"

    limit = MagicMock()
    limit.limit = None
    exc = RateLimitExceeded(limit)
    exc.detail = None  # type: ignore

    response = rate_limit_exceeded_handler(request, exc)
    content = json.loads(response.body)

    assert content["status"] == 429
    assert content["extensions"]["retry_after"] == "unknown"
