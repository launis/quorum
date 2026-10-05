"""Rate Limiting Configuration Module.

Stores the SlowAPI Limiter instance centrally to avoid circular imports
between main.py and router modules.
"""

import logging

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from backend_v2.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """Handle RateLimitExceeded exceptions with RFC 7807 compliance.

    Args:
        request: The incoming request.
        exc: The raised RateLimitExceeded exception.

    Returns:
        JSONResponse: RFC 7807 Problem Details.
    """
    msg = f"Rate limit exceeded: {exc.detail}"
    if exc.detail:
        error = AppException(
            message=msg,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details={
                "error_code": ErrorCodes.RATE_LIMIT_EXCEEDED.value,
                "retry_after": str(exc.detail).split(" ")[0],
            },
        )
    else:
        error = AppException(
            message=msg,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details={"error_code": ErrorCodes.RATE_LIMIT_EXCEEDED.value},
        )

    return JSONResponse(
        status_code=error.status_code,
        content=error.to_problem_detail(instance=str(request.url.path)).model_dump(mode="json", exclude_none=True),
        media_type="application/problem+json",
    )


# Initialize Limiter with Remote Address as key
# TODO: In production, configure storage_uri (Redis) for distributed limiting.
limiter = Limiter(key_func=get_remote_address)
