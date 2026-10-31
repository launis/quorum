"""Unit tests for WebFetcher service."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import httpx
import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.services.web_fetcher import WebFetcher


class _MockResponse:
    """Deterministic in-memory HTTP response stub for WebFetcher unit tests."""

    def __init__(self, content: bytes, status_code: int = 200) -> None:
        """Initialize stub response with raw byte payload and HTTP status code.

        Args:
            content: Raw response body bytes.
            status_code: HTTP status code.
        """
        self.content = content
        self.status_code = status_code

    def raise_for_status(self) -> None:
        """Raise httpx.HTTPStatusError when status_code indicates an HTTP error."""
        if self.status_code >= 400:
            request = httpx.Request("GET", "https://example.com")
            response = httpx.Response(self.status_code, request=request)
            raise httpx.HTTPStatusError(
                f"HTTP {self.status_code}",
                request=request,
                response=response,
            )


def test_fetch_text_success_strips_scripts_styles_and_tags() -> None:
    """Verify fetch_text strips script/style blocks and HTML tags while collapsing whitespace."""

    class MockClient:
        captured_timeout: int = 0
        captured_follow_redirects: bool = False

        def __init__(
            self,
            headers: dict[str, str] | None = None,
            timeout: int = 0,
            follow_redirects: bool = False,
        ) -> None:
            MockClient.captured_timeout = timeout
            MockClient.captured_follow_redirects = follow_redirects
            self.headers = headers

        def __enter__(self) -> MockClient:
            return self

        def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
            pass

        def get(self, url: str) -> _MockResponse:
            return _MockResponse(
                b"<html><head><style>body { color: red; }</style></head>"
                b"<body>Hello   <script>ignore_me()</script>   <b>World</b></body></html>"
            )

    mock_settings = MagicMock()
    mock_settings.mcp_discovery_timeout_seconds = 12
    mock_settings.web_fetcher_max_extracted_chars = 0
    mock_settings.web_fetcher_min_extracted_chars = 150

    with (
        patch("backend_v2.services.web_fetcher.get_settings", return_value=mock_settings),
        patch("backend_v2.services.web_fetcher.httpx.Client", side_effect=MockClient),
    ):
        result = WebFetcher.fetch_text("https://example.com")
        assert result == "Hello World"
        assert "ignore_me" not in result
        assert "color: red" not in result
        assert MockClient.captured_timeout == 12
        assert MockClient.captured_follow_redirects is True


def test_fetch_text_explicit_timeout_override() -> None:
    """Verify explicit positive timeout overrides settings default."""

    class MockClient:
        captured_timeout: int = 0

        def __init__(
            self,
            headers: dict[str, str] | None = None,
            timeout: int = 0,
            follow_redirects: bool = False,
        ) -> None:
            MockClient.captured_timeout = timeout
            self.headers = headers
            self.follow_redirects = follow_redirects

        def __enter__(self) -> MockClient:
            return self

        def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
            pass

        def get(self, url: str) -> _MockResponse:
            return _MockResponse(b"<html><body>" + b"A" * 200 + b"</body></html>")

    with patch("backend_v2.services.web_fetcher.httpx.Client", side_effect=MockClient):
        result = WebFetcher.fetch_text("https://example.com", timeout=1)
        assert len(result) == 200
        assert MockClient.captured_timeout == 1


def test_fetch_text_truncates_at_5000_chars_boundary() -> None:
    """Verify ISTQB boundary truncation at exactly 5000 characters (5000 and 5001 inputs)."""
    payload_5001 = b"<html><body>" + (b"x" * 5001) + b"</body></html>"

    class MockClient:
        def __init__(
            self,
            headers: dict[str, str] | None = None,
            timeout: int = 0,
            follow_redirects: bool = False,
        ) -> None:
            self.headers = headers
            self.timeout = timeout
            self.follow_redirects = follow_redirects

        def __enter__(self) -> MockClient:
            return self

        def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
            pass

        def get(self, url: str) -> _MockResponse:
            return _MockResponse(payload_5001)

    with patch("backend_v2.services.web_fetcher.httpx.Client", side_effect=MockClient):
        # Default web_fetcher_max_extracted_chars = 0 preserves full 5001 characters unbounded
        unbounded_result = WebFetcher.fetch_text("https://example.com")
        assert len(unbounded_result) == 5001

        # Explicit positive web_fetcher_max_extracted_chars = 5000 truncates at 5000 characters
        mock_settings_5000 = MagicMock()
        mock_settings_5000.mcp_discovery_timeout_seconds = 12
        mock_settings_5000.web_fetcher_max_extracted_chars = 5000
        mock_settings_5000.web_fetcher_min_extracted_chars = 150

        with patch(
            "backend_v2.services.web_fetcher.get_settings",
            return_value=mock_settings_5000,
        ):
            result = WebFetcher.fetch_text("https://example.com")
            assert len(result) == 5000


def test_fetch_text_short_content_warning_boundary(caplog: pytest.LogCaptureFixture) -> None:
    """Verify short content warning triggers at 149 chars (min-1) and not at 150 chars (min)."""
    payload_149 = b"<html><body>" + (b"a" * 149) + b"</body></html>"
    payload_150 = b"<html><body>" + (b"a" * 150) + b"</body></html>"
    responses = [_MockResponse(payload_149), _MockResponse(payload_150)]

    class MockClient:
        def __init__(
            self,
            headers: dict[str, str] | None = None,
            timeout: int = 0,
            follow_redirects: bool = False,
        ) -> None:
            self.headers = headers
            self.timeout = timeout
            self.follow_redirects = follow_redirects

        def __enter__(self) -> MockClient:
            return self

        def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
            pass

        def get(self, url: str) -> _MockResponse:
            return responses.pop(0)

    with patch("backend_v2.services.web_fetcher.httpx.Client", side_effect=MockClient):
        caplog.clear()
        res_short = WebFetcher.fetch_text("https://example.com")
        assert len(res_short) == 149
        assert "suspiciously short" in caplog.text

        caplog.clear()
        res_exact = WebFetcher.fetch_text("https://example.com")
        assert len(res_exact) == 150
        assert "suspiciously short" not in caplog.text


def test_fetch_text_paywall_warning(caplog: pytest.LogCaptureFixture) -> None:
    """Verify paywall detection logs a warning when extracted text >= 150 chars contains paywall cues."""
    payload = (
        b"<html><body>Please verify you are a human to continue reading this long text that bypasses "
        b"the length limit.........................................................................."
        b".............................................................................</body></html>"
    )

    class MockClient:
        def __init__(
            self,
            headers: dict[str, str] | None = None,
            timeout: int = 0,
            follow_redirects: bool = False,
        ) -> None:
            self.headers = headers
            self.timeout = timeout
            self.follow_redirects = follow_redirects

        def __enter__(self) -> MockClient:
            return self

        def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
            pass

        def get(self, url: str) -> _MockResponse:
            return _MockResponse(payload)

    with patch("backend_v2.services.web_fetcher.httpx.Client", side_effect=MockClient):
        result = WebFetcher.fetch_text("https://example.com")
        assert "verify you are a human" in result
        assert "paywall" in caplog.text.lower()


@pytest.mark.parametrize(
    "invalid_url",
    [
        "",
        "   ",
        "ftp://example.com",
        "file:///etc/passwd",
        "example.com/no-scheme",
    ],
)
def test_fetch_text_invalid_url_raises_app_exception(invalid_url: str) -> None:
    """Verify missing or non-HTTP(S) URLs fail-fast with URL_INVALID (400)."""
    with pytest.raises(AppException) as excinfo:
        WebFetcher.fetch_text(invalid_url)
    assert excinfo.value.status_code == 400
    assert excinfo.value.details["error_code"] == ErrorCodes.URL_INVALID


@pytest.mark.parametrize("invalid_timeout", [0, -1, -30])
def test_fetch_text_invalid_timeout_raises_app_exception(invalid_timeout: int) -> None:
    """Verify ISTQB boundary values timeout <= 0 fail-fast with VALIDATION_FAILED (400)."""
    with pytest.raises(AppException) as excinfo:
        WebFetcher.fetch_text("https://example.com", timeout=invalid_timeout)
    assert excinfo.value.status_code == 400
    assert excinfo.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED


def test_fetch_text_network_error_raises_app_exception() -> None:
    """Verify httpx.RequestError translates to AppException with FETCH_FAILED (502)."""

    class MockClient:
        def __init__(
            self,
            headers: dict[str, str] | None = None,
            timeout: int = 0,
            follow_redirects: bool = False,
        ) -> None:
            self.headers = headers
            self.timeout = timeout
            self.follow_redirects = follow_redirects

        def __enter__(self) -> MockClient:
            return self

        def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
            pass

        def get(self, url: str) -> _MockResponse:
            raise httpx.RequestError("Mocked connection error")

    with patch("backend_v2.services.web_fetcher.httpx.Client", side_effect=MockClient):
        with pytest.raises(AppException) as excinfo:
            WebFetcher.fetch_text("https://example.com")
        assert excinfo.value.status_code == 502
        assert excinfo.value.details["error_code"] == ErrorCodes.FETCH_FAILED


def test_fetch_text_http_status_error_raises_app_exception() -> None:
    """Verify httpx.HTTPStatusError translates to AppException with FETCH_FAILED (502)."""

    class MockClient:
        def __init__(
            self,
            headers: dict[str, str] | None = None,
            timeout: int = 0,
            follow_redirects: bool = False,
        ) -> None:
            self.headers = headers
            self.timeout = timeout
            self.follow_redirects = follow_redirects

        def __enter__(self) -> MockClient:
            return self

        def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
            pass

        def get(self, url: str) -> _MockResponse:
            return _MockResponse(b"Not Found", status_code=404)

    with patch("backend_v2.services.web_fetcher.httpx.Client", side_effect=MockClient):
        with pytest.raises(AppException) as excinfo:
            WebFetcher.fetch_text("https://example.com/missing")
        assert excinfo.value.status_code == 502
        assert excinfo.value.details["error_code"] == ErrorCodes.FETCH_FAILED
        assert "HTTP 404" in excinfo.value.message


def test_fetch_text_unexpected_runtime_error_raises_app_exception() -> None:
    """Verify unexpected runtime exceptions translate to AppException with INTERNAL_SERVER_ERROR (500)."""

    class MockClient:
        def __init__(
            self,
            headers: dict[str, str] | None = None,
            timeout: int = 0,
            follow_redirects: bool = False,
        ) -> None:
            self.headers = headers
            self.timeout = timeout
            self.follow_redirects = follow_redirects

        def __enter__(self) -> MockClient:
            return self

        def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
            pass

        def get(self, url: str) -> _MockResponse:
            raise RuntimeError("Unexpected low-level socket crash")

    with patch("backend_v2.services.web_fetcher.httpx.Client", side_effect=MockClient):
        with pytest.raises(AppException) as excinfo:
            WebFetcher.fetch_text("https://example.com")
        assert excinfo.value.status_code == 500
        assert excinfo.value.details["error_code"] == ErrorCodes.INTERNAL_SERVER_ERROR


def test_fetch_text_app_exception_passthrough() -> None:
    """Verify AppException raised inside client context is re-raised without wrapping into 500."""

    class MockClient:
        def __init__(
            self,
            headers: dict[str, str] | None = None,
            timeout: int = 0,
            follow_redirects: bool = False,
        ) -> None:
            self.headers = headers
            self.timeout = timeout
            self.follow_redirects = follow_redirects

        def __enter__(self) -> MockClient:
            return self

        def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
            pass

        def get(self, url: str) -> _MockResponse:
            raise AppException(
                message="Upstream domain guard triggered",
                status_code=422,
                details={"error_code": ErrorCodes.VALIDATION_FAILED},
            )

    with patch("backend_v2.services.web_fetcher.httpx.Client", side_effect=MockClient):
        with pytest.raises(AppException) as excinfo:
            WebFetcher.fetch_text("https://example.com")
        assert excinfo.value.status_code == 422
        assert excinfo.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED
