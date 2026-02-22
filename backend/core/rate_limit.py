"""Rate Limiting Configuration Module.

Stores the SlowAPI Limiter instance centrally to avoid circular imports
between main.py and router modules.
"""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from backend.exceptions import AppException, ErrorCodes, status


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """Handle RateLimitExceeded exceptions with RFC 7807 compliance.

    Args:
        request: The incoming request.
        exc: The raised RateLimitExceeded exception.

    Returns:
        JSONResponse: RFC 7807 Problem Details.
    """
    # Create an AppException wrapper to leverage strict RFC 7807 formatting
    error = AppException(
        message=f"Rate limit exceeded: {exc.detail}",
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        details={
            "error_code": ErrorCodes.RATE_LIMIT_EXCEEDED,
            "retry_after": str(exc.detail).split(" ")[0] if exc.detail else "unknown",
        },
    )

    return JSONResponse(
        status_code=error.status_code,
        content=error.to_problem_detail(instance=str(request.url.path)),
        media_type="application/problem+json",
    )


# Initialize Limiter with Remote Address as key
# TODO: In production, configure storage_uri (Redis) for distributed limiting.
limiter = Limiter(key_func=get_remote_address)
