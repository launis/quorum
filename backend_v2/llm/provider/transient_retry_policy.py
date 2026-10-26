"""Transient LLM error classification and adaptive Retry-After Tenacity wait policy."""

import asyncio
import re

from pydantic import ValidationError
from tenacity import RetryCallState
from tenacity.wait import wait_base

from backend_v2.exceptions import (
    AppException,
    ErrorCodes,
    LLMSchemaValidationError,
    LogicalValidationError,
)
from backend_v2.llm.provider.env_and_schema_utils import _safe_static_getattr

__all__ = [
    "_AdaptiveWaitWithRetryAfter",
    "_RETRY_AFTER_REGEX",
    "_extract_retry_after_seconds",
    "_format_attempt_error",
    "_is_transient_llm_error",
]


# Phase 1, Step 1: Relocate depth-1 transient error detection and adaptive Retry-After policy
def _is_transient_llm_error(e: BaseException, _visited: set[int] | None = None) -> bool:
    """Check if the LiteLLM/asyncio/HTTP exception is a transient network error, rate limit, or timeout.

    Recursively unwrap causes, exception groups, and original errors to detect transient transport drops.

    Args:
        e: The caught exception.
        _visited: Set of visited object IDs to prevent infinite cycles.

    Returns:
        True if the error is transient and safe to retry, False otherwise.
    """
    if _visited is None:
        _visited = set()
    if id(e) in _visited:
        return False
    _visited.add(id(e))

    # 0. Fast-path: Explicit non-transient exceptions (structural validation, schema failures) MUST return False
    if isinstance(
        e,
        (
            LLMSchemaValidationError,
            LogicalValidationError,
            ValidationError,
            ValueError,
            KeyError,
        ),
    ):
        return False

    # 1. Check ExceptionGroup / BaseExceptionGroup
    if isinstance(e, BaseExceptionGroup):
        return any(_is_transient_llm_error(sub_exc, _visited) for sub_exc in e.exceptions)

    # 2. Check direct LiteLLM transient exceptions
    from litellm.exceptions import (
        APIConnectionError,
        BadGatewayError,
        InternalServerError,
        RateLimitError,
    )
    from litellm.exceptions import (
        ServiceUnavailableError as LiteLLMServiceUnavailableError,
    )
    from litellm.exceptions import (
        Timeout as LiteLLMTimeout,
    )

    if isinstance(
        e,
        (
            RateLimitError,
            LiteLLMTimeout,
            LiteLLMServiceUnavailableError,
            APIConnectionError,
            InternalServerError,
            BadGatewayError,
        ),
    ):
        return True

    # 3. Check direct Transport / Network / Timeout exceptions (httpx, aiohttp, socket, asyncio)
    import httpx

    if isinstance(
        e,
        (
            asyncio.TimeoutError,
            TimeoutError,
            ConnectionError,
            ConnectionResetError,
            ConnectionRefusedError,
            BrokenPipeError,
            httpx.TimeoutException,
            httpx.NetworkError,
            httpx.ReadError,
            httpx.ConnectError,
            httpx.RemoteProtocolError,
        ),
    ):
        return True

    try:
        import aiohttp

        if isinstance(e, aiohttp.ClientError):
            return True
    except ImportError:
        pass

    # 4. Check HTTP Status Code attributes (e.g. 429, 500, 502, 503, 504) for upstream errors
    # Note: Domain AppExceptions are evaluated specifically in step 5 by their domain error_code.
    if not isinstance(e, AppException):
        e_status_code = _safe_static_getattr(e, "status_code")
        if isinstance(e_status_code, int) and e_status_code in (429, 500, 502, 503, 504):
            return True

    # 5. Check AppException domain details for transient codes
    if isinstance(e, AppException):
        if e.status_code in (429, 503, 504):
            return True
        error_code = None
        if type(e.details) is dict and "error_code" in e.details:
            error_code = e.details["error_code"]
        if error_code in (
            ErrorCodes.UPSTREAM_TIMEOUT.value,
            ErrorCodes.UPSTREAM_TIMEOUT.name,
            ErrorCodes.RATE_LIMIT_EXCEEDED.value,
            ErrorCodes.RATE_LIMIT_EXCEEDED.name,
            ErrorCodes.NETWORK_UNAVAILABLE.value,
            ErrorCodes.NETWORK_UNAVAILABLE.name,
            ErrorCodes.SERVICE_UNAVAILABLE.value,
            ErrorCodes.SERVICE_UNAVAILABLE.name,
        ):
            return True

    # 6. Check error message string patterns for raw socket disconnects
    msg = str(e).lower()
    if (
        "server disconnected" in msg
        or "connection reset" in msg
        or "remote end closed connection" in msg
        or "connection closed" in msg
    ):
        return True

    # 7. Recursively inspect causes and wrapped exceptions
    orig_err = _safe_static_getattr(e, "original_error")
    if isinstance(orig_err, BaseException) and _is_transient_llm_error(orig_err, _visited):
        return True

    if e.__cause__ is not None and _is_transient_llm_error(e.__cause__, _visited):
        return True

    if e.__context__ is not None and not e.__suppress_context__ and _is_transient_llm_error(e.__context__, _visited):
        return True

    return False


_RETRY_AFTER_REGEX = re.compile(r"(?:please\s+)?try again in ([0-9.]+)s", re.IGNORECASE)


def _extract_retry_after_seconds(e: BaseException, _visited: set[int] | None = None) -> float | None:
    """Extract retry-after delay in seconds from exception headers or message.

    Recursively inspects causes, contexts, and child exceptions.

    Args:
        e: The caught exception.
        _visited: Set of visited object IDs to prevent circular reference cycles.

    Returns:
        Positive delay in seconds if detected, or None if no upstream delay found.
    """
    if _visited is None:
        _visited = set()
    if id(e) in _visited:
        return None
    _visited.add(id(e))

    # 1. Check headers (direct or via response attribute)
    headers = _safe_static_getattr(e, "headers")
    if headers is None:
        resp = _safe_static_getattr(e, "response")
        if resp is not None:
            headers = _safe_static_getattr(resp, "headers")
    if headers and "items" in dir(headers):
        for k, v in headers.items():
            if str(k).lower() == "retry-after":
                try:
                    val = float(v)
                    if val > 0:
                        return val
                except ValueError, TypeError:
                    pass

    # 2. Check message string for 'Please try again in X.Xs'
    msg = str(e)
    match = _RETRY_AFTER_REGEX.search(msg)
    if match:
        try:
            val = float(match.group(1))
            if val > 0:
                return val
        except ValueError, TypeError:
            pass

    # 3. Check BaseExceptionGroup
    if isinstance(e, BaseExceptionGroup):
        candidates: list[float] = []
        for sub in e.exceptions:
            child_val = _extract_retry_after_seconds(sub, _visited)
            if child_val is not None:
                candidates.append(child_val)
        if candidates:
            return max(candidates)

    # 4. Recursively check original_error, __cause__, __context__
    orig_err_retry = _safe_static_getattr(e, "original_error")
    if isinstance(orig_err_retry, BaseException):
        child_val = _extract_retry_after_seconds(orig_err_retry, _visited)
        if child_val is not None:
            return child_val

    if e.__cause__ is not None:
        child_val = _extract_retry_after_seconds(e.__cause__, _visited)
        if child_val is not None:
            return child_val

    if e.__context__ is not None and not e.__suppress_context__:
        child_val = _extract_retry_after_seconds(e.__context__, _visited)
        if child_val is not None:
            return child_val

    return None


class _AdaptiveWaitWithRetryAfter(wait_base):
    """Tenacity wait strategy that respects upstream Retry-After delays.

    Attributes:
        base_wait: Underlying wait strategy (e.g. exponential jitter).
        max_seconds: Hard ceiling on the computed sleep duration in seconds.
    """

    def __init__(
        self,
        base_wait: wait_base,
        max_seconds: float,
    ) -> None:
        """Initialize adaptive retry waiter.

        Args:
            base_wait: Underlying wait strategy.
            max_seconds: Hard ceiling on sleep duration.
        """
        self.base_wait = base_wait
        self.max_seconds = max_seconds

    def __call__(self, retry_state: RetryCallState) -> float:
        """Calculate wait time considering upstream Retry-After headers.

        Args:
            retry_state: Current state of the retry invocation.

        Returns:
            Calculated sleep delay in seconds.
        """
        base_delay = float(self.base_wait(retry_state))
        exc: BaseException | None = None
        if retry_state.outcome and retry_state.outcome.failed:
            exc = retry_state.outcome.exception()

        if exc is not None:
            retry_after = _extract_retry_after_seconds(exc)
            if retry_after is not None and retry_after > 0:
                # Add 0.5s safety margin and clamp to max_seconds
                adaptive_delay = min(retry_after + 0.5, self.max_seconds)
                return max(base_delay, adaptive_delay)

        return min(base_delay, self.max_seconds)


def _format_attempt_error(rs: RetryCallState) -> str:
    """Format exception name safely for retry logging.

    Args:
        rs: Current Tenacity retry call state.

    Returns:
        Exception class name if failed, otherwise 'Unknown'.
    """
    if rs.outcome and rs.outcome.failed:
        exc = rs.outcome.exception()
        if exc is not None:
            return type(exc).__name__
    return "Unknown"
