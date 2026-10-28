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

__all__ = [
    "limiter",
    "rate_limit_exceeded_handler",
]


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """Handle RateLimitExceeded exceptions with RFC 7807 compliance.

    Args:
        request: The incoming request.
        exc: The raised RateLimitExceeded exception.

    Returns:
        RFC 7807 Problem Details JSON response.

    Raises:
        AppException: Raised with VALIDATION_FAILED (400) if the request path is empty or whitespace.
    """
    path_str = str(request.url.path).strip()
    if not path_str:
        logger.error(
            "Invalid empty request path in rate_limit_exceeded_handler.",
            exc_info=True,
            extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )
        raise AppException(
            message="Request path cannot be empty.",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )

    logger.error(
        "Rate limit exceeded on path %s",
        path_str,
        exc_info=True,
        extra={"error_code": ErrorCodes.RATE_LIMIT_EXCEEDED.value},
    )
    if exc.detail and str(exc.detail).strip():
        detail_str = str(exc.detail).strip()
        error = AppException(
            message=f"Rate limit exceeded: {detail_str}",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details={
                "error_code": ErrorCodes.RATE_LIMIT_EXCEEDED.value,
                "retry_after": detail_str.split(" ")[0],
            },
        )
    else:
        error = AppException(
            message=f"Rate limit exceeded: {exc.detail}",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details={"error_code": ErrorCodes.RATE_LIMIT_EXCEEDED.value},
        )

    return JSONResponse(
        status_code=error.status_code,
        content=error.to_problem_detail(instance=path_str).model_dump(mode="json", exclude_none=True),
        media_type="application/problem+json",
    )


# Initialize Limiter with Remote Address as key
limiter = Limiter(key_func=get_remote_address)
