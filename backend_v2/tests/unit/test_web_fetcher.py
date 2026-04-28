import pytest
import httpx
from unittest.mock import patch

from backend_v2.services.web_fetcher import WebFetcher
from backend_v2.exceptions import AppException

def test_fetch_text_success():
    class MockResponse:
        def __init__(self):
            self.content = b"<html><body>Hello <script>ignore</script>World</body></html>"
        
        def raise_for_status(self):
            pass

    class MockClient:
        def __enter__(self):
            return self
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
            
        def get(self, url):
            return MockResponse()

    with patch("backend_v2.services.web_fetcher.httpx.Client", return_value=MockClient()):
        result = WebFetcher.fetch_text("https://example.com")
        assert "Hello World" in result
        assert "ignore" not in result

def test_fetch_text_invalid_url():
    with pytest.raises(AppException) as excinfo:
        WebFetcher.fetch_text("ftp://example.com")
    assert excinfo.value.status_code == 400

def test_fetch_text_network_error():
    class MockClient:
        def __enter__(self):
            return self
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
            
        def get(self, url):
            raise httpx.RequestError("Mocked timeout", request=None)

    with patch("backend_v2.services.web_fetcher.httpx.Client", return_value=MockClient()):
        with pytest.raises(AppException) as excinfo:
            WebFetcher.fetch_text("https://example.com")
        assert excinfo.value.status_code == 502

def test_fetch_text_paywall_warning(caplog):
    class MockResponse:
        def __init__(self):
            self.content = b"<html><body>Please verify you are a human to continue reading this long text that bypasses the length limit.......................................................................................................................................................</body></html>"
        
        def raise_for_status(self):
            pass

    class MockClient:
        def __enter__(self):
            return self
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
            
        def get(self, url):
            return MockResponse()

    with patch("backend_v2.services.web_fetcher.httpx.Client", return_value=MockClient()):
        result = WebFetcher.fetch_text("https://example.com")
        assert "verify you are a human" in result
        assert "paywall" in caplog.text.lower()
