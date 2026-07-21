from unittest.mock import AsyncMock
from typing import Any
from unittest.mock import patch

import httpx
import pytest

from backend_v2.exceptions import AppException
from backend_v2.services.web_fetcher import WebFetcher


def test_fetch_text_success() -> None:
    class MockResponse:
        def __init__(self) -> None:
            self.content = b"<html><body>Hello <script>ignore</script>World</body></html>"

        def raise_for_status(self) -> None:
            pass

    class MockClient:
        def __enter__(self) -> MockClient:
            return self

        def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
            pass

        def get(self, url: str) -> MockResponse:
            return MockResponse()

    with patch("backend_v2.services.web_fetcher.httpx.Client", return_value=MockClient()):
        result = WebFetcher.fetch_text("https://example.com")
        assert "Hello World" in result
        assert "ignore" not in result


def test_fetch_text_invalid_url() -> None:
    with pytest.raises(AppException) as excinfo:
        WebFetcher.fetch_text("ftp://example.com")
    assert excinfo.value.status_code == 400


def test_fetch_text_network_error() -> None:
    class MockClient:
        def __enter__(self) -> MockClient:
            return self

        def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
            pass

        def get(self, url: str) -> None:
            raise httpx.RequestError("Mocked timeout", request=None)

    with patch("backend_v2.services.web_fetcher.httpx.Client", return_value=MockClient()):
        with pytest.raises(AppException) as excinfo:
            WebFetcher.fetch_text("https://example.com")
        assert excinfo.value.status_code == 502


def test_fetch_text_paywall_warning(caplog: Any) -> None:
    class MockResponse:
        def __init__(self) -> None:
            self.content = b"<html><body>Please verify you are a human to continue reading this long text that bypasses the length limit.......................................................................................................................................................</body></html>"  # noqa: E501

        def raise_for_status(self) -> None:
            pass

    class MockClient:
        def __enter__(self) -> MockClient:
            return self

        def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
            pass

        def get(self, url: str) -> MockResponse:
            return MockResponse()

    with patch("backend_v2.services.web_fetcher.httpx.Client", return_value=MockClient()):
        result = WebFetcher.fetch_text("https://example.com")
        assert "verify you are a human" in result
        assert "paywall" in caplog.text.lower()
