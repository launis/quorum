"""Unit tests for transient LLM error classification and adaptive Retry-After wait policy."""

from __future__ import annotations

import asyncio

import aiohttp
import httpx
import pytest
from litellm.exceptions import (
    APIConnectionError,
    BadGatewayError,
    InternalServerError,
    RateLimitError,
)
from pydantic import BaseModel, ConfigDict, ValidationError
from tenacity import Future, RetryCallState
from tenacity.wait import wait_fixed

from backend_v2.exceptions import (
    AppException,
    ErrorCodes,
    LLMSchemaValidationError,
    LogicalValidationError,
)
from backend_v2.llm.provider.transient_retry_policy import (
    _AdaptiveWaitWithRetryAfter,
    _extract_retry_after_seconds,
    _format_attempt_error,
    _is_transient_llm_error,
)


class _StrictSampleDTO(BaseModel):
    """Strict model for generating real Pydantic ValidationError instances."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    count: int


class _UpstreamStatusError(Exception):
    """Exception carrying HTTP status_code, headers, and optional original_error."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        headers: dict[str, str] | None = None,
        response_headers: dict[str, str] | None = None,
        original_error: BaseException | None = None,
    ) -> None:
        """Initialize upstream status error.

        Args:
            message: Error message.
            status_code: Optional HTTP status code.
            headers: Optional direct headers dictionary.
            response_headers: Optional nested response.headers dictionary.
            original_error: Optional wrapped original exception.
        """
        super().__init__(message)
        self.status_code = status_code
        self.headers = headers
        self.response = type("Resp", (), {"headers": response_headers})() if response_headers is not None else None
        self.original_error = original_error


def test_extract_retry_after_and_adaptive_wait_clamping() -> None:
    """Verify _extract_retry_after_seconds parses Retry-After and _AdaptiveWaitWithRetryAfter clamps to max_seconds."""
    err_header = _UpstreamStatusError("Rate limited", status_code=429, headers={"Retry-After": "14.25"})
    assert _extract_retry_after_seconds(err_header) == 14.25

    err_resp_header = _UpstreamStatusError("Rate limited", status_code=429, response_headers={"retry-after": "7.5"})
    assert _extract_retry_after_seconds(err_resp_header) == 7.5

    err_msg = _UpstreamStatusError("Rate limit reached. Please try again in 11.5s.")
    assert _extract_retry_after_seconds(err_msg) == 11.5

    waiter = _AdaptiveWaitWithRetryAfter(base_wait=wait_fixed(2.0), max_seconds=30.0)

    # 1. Retry-After + 0.5s safety margin (11.5 + 0.5 = 12.0s) > base_wait (2.0s) and < max_seconds (30.0s)
    outcome_mid = Future(1)
    outcome_mid.set_exception(err_msg)
    rs_mid = RetryCallState(retry_object=None, fn=None, args=(), kwargs={})
    rs_mid.outcome = outcome_mid
    assert waiter(rs_mid) == 12.0

    # 2. Retry-After (120.0s) clamped to max_seconds (30.0s)
    err_huge = _UpstreamStatusError("try again in 120.0s")
    outcome_huge = Future(1)
    outcome_huge.set_exception(err_huge)
    rs_huge = RetryCallState(retry_object=None, fn=None, args=(), kwargs={})
    rs_huge.outcome = outcome_huge
    assert waiter(rs_huge) == 30.0

    # 3. No Retry-After falls back to base_wait (2.0s)
    outcome_none = Future(1)
    outcome_none.set_exception(RuntimeError("generic transient failure"))
    rs_none = RetryCallState(retry_object=None, fn=None, args=(), kwargs={})
    rs_none.outcome = outcome_none
    assert waiter(rs_none) == 2.0


def test_is_transient_llm_error_rejects_validation_and_schema_errors() -> None:
    """Verify non-transient validation, schema, and key errors immediately return False."""
    with pytest.raises(ValidationError) as val_exc:
        _StrictSampleDTO.model_validate({"count": "not-an-int"})

    assert _is_transient_llm_error(val_exc.value) is False
    assert _is_transient_llm_error(LLMSchemaValidationError("{bad}", "Schema mismatch")) is False
    assert _is_transient_llm_error(LogicalValidationError("Logic mismatch")) is False
    assert _is_transient_llm_error(ValueError("bad value")) is False
    assert _is_transient_llm_error(KeyError("missing_key")) is False


def test_is_transient_llm_error_recognizes_litellm_and_transport_exceptions() -> None:
    """Verify LiteLLM, httpx, aiohttp, asyncio, status codes, and disconnect strings return True."""
    assert _is_transient_llm_error(RateLimitError("429", "openai", "gpt-5.1")) is True
    assert _is_transient_llm_error(APIConnectionError("conn drop", "openai", "gpt-5.1")) is True
    assert _is_transient_llm_error(InternalServerError("500", "openai", "gpt-5.1")) is True
    assert _is_transient_llm_error(BadGatewayError("502", "openai", "gpt-5.1")) is True
    assert _is_transient_llm_error(asyncio.TimeoutError()) is True
    assert _is_transient_llm_error(httpx.ConnectTimeout("connect timed out")) is True
    assert _is_transient_llm_error(aiohttp.ClientError("aiohttp disconnect")) is True

    for code in (429, 500, 502, 503, 504):
        assert _is_transient_llm_error(_UpstreamStatusError("upstream failure", status_code=code)) is True
    assert _is_transient_llm_error(_UpstreamStatusError("bad request", status_code=400)) is False

    assert _is_transient_llm_error(RuntimeError("Server disconnected without sending a response.")) is True
    assert _is_transient_llm_error(RuntimeError("Remote end closed connection without response")) is True


def test_is_transient_llm_error_app_exception_and_recursive_unwrapping() -> None:
    """Verify AppException status/error_code checks and recursive cause/context/group unwrapping."""
    app_429 = AppException(message="Rate limit", status_code=429, details={"error_code": "OTHER"})
    assert _is_transient_llm_error(app_429) is True

    app_timeout_code = AppException(
        message="Timed out",
        status_code=500,
        details={"error_code": ErrorCodes.UPSTREAM_TIMEOUT.value},
    )
    assert _is_transient_llm_error(app_timeout_code) is True

    app_auth = AppException(
        message="Unauthorized",
        status_code=401,
        details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
    )
    assert _is_transient_llm_error(app_auth) is False

    # Wrapped original_error
    wrapped = _UpstreamStatusError("Wrapper", original_error=httpx.ReadError("read failed"))
    assert _is_transient_llm_error(wrapped) is True

    # Chained __cause__ and __context__
    outer_cause = RuntimeError("InstructorRetryException wrapper")
    outer_cause.__cause__ = _UpstreamStatusError("503", status_code=503)
    assert _is_transient_llm_error(outer_cause) is True

    outer_ctx = RuntimeError("Context wrapper")
    outer_ctx.__context__ = ConnectionResetError("reset by peer")
    outer_ctx.__suppress_context__ = False
    assert _is_transient_llm_error(outer_ctx) is True

    # ExceptionGroup containing transient sub-exception
    eg = ExceptionGroup("batch", [RuntimeError("benign"), httpx.RemoteProtocolError("protocol drop")])
    assert _is_transient_llm_error(eg) is True

    # Cycle safety
    cyc_a = RuntimeError("cycle A")
    cyc_b = RuntimeError("cycle B")
    cyc_a.__cause__ = cyc_b
    cyc_b.__cause__ = cyc_a
    assert _is_transient_llm_error(cyc_a) is False


def test_extract_retry_after_recursive_and_format_attempt_error() -> None:
    """Verify _extract_retry_after_seconds across wrapped causes/contexts/groups and _format_attempt_error."""
    inner = _UpstreamStatusError("try again in 6.25s")
    wrapper_orig = _UpstreamStatusError("outer", original_error=inner)
    assert _extract_retry_after_seconds(wrapper_orig) == 6.25

    wrapper_ctx = RuntimeError("context")
    wrapper_ctx.__context__ = _UpstreamStatusError("try again in 4.5s")
    wrapper_ctx.__suppress_context__ = False
    assert _extract_retry_after_seconds(wrapper_ctx) == 4.5

    group = ExceptionGroup(
        "multi",
        [
            _UpstreamStatusError("try again in 3.0s"),
            _UpstreamStatusError("try again in 9.5s"),
        ],
    )
    assert _extract_retry_after_seconds(group) == 9.5

    # Invalid / non-positive header and no match
    invalid_header = _UpstreamStatusError("no retry", headers={"Retry-After": "invalid", "Other": "1"})
    assert _extract_retry_after_seconds(invalid_header) is None

    rs_empty = RetryCallState(retry_object=None, fn=None, args=(), kwargs={})
    assert _format_attempt_error(rs_empty) == "Unknown"

    outcome_err = Future(1)
    outcome_err.set_exception(TimeoutError("timed out"))
    rs_failed = RetryCallState(retry_object=None, fn=None, args=(), kwargs={})
    rs_failed.outcome = outcome_err
    assert _format_attempt_error(rs_failed) == "TimeoutError"
