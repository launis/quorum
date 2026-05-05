from unittest.mock import MagicMock

from fastapi import Request
from slowapi.errors import RateLimitExceeded

from backend_v2.core.rate_limit import rate_limit_exceeded_handler


def test_rate_limit_exceeded_handler() -> None:
    mock_request = MagicMock(spec=Request)
    mock_request.url.path = "/test"
    
    mock_limit = MagicMock()
    mock_limit.error_message = None
    mock_limit.__str__.return_value = "1 per 1 minute"
    exc = RateLimitExceeded(mock_limit)
    response = rate_limit_exceeded_handler(mock_request, exc)
    
    assert response.status_code == 429
    assert response.media_type == "application/problem+json"
