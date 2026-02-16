import pytest
from unittest.mock import MagicMock, patch
import urllib.error

from backend.services.web_fetcher import WebFetcher
from backend.exceptions import AppException, ErrorCodes

class TestWebFetcher:
    
    @patch("urllib.request.urlopen")
    def test_fetch_text_success(self, mock_urlopen):
        """Test happy path fetching."""
        # Setup
        mock_response = MagicMock()
        mock_response.read.return_value = b"<html><body><h1>Hello</h1><script>ignore</script></body></html>"
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        # Execute
        result = WebFetcher.fetch_text("https://example.com")

        # Verify
        assert "Hello" in result
        assert "ignore" not in result
        print("\n[TEST] WebFetcher Success")

    def test_fetch_text_invalid_url(self):
        """Test fail fast on invalid URL."""
        # Execute & Verify
        try:
            WebFetcher.fetch_text("ftp://example.com")
            assert False, "Should have raised AppException"
        except AppException as e:
            assert e.details["error_code"] == ErrorCodes.URL_INVALID
            assert e.status_code == 400
            print("\n[TEST] WebFetcher Invalid URL: Caught")

    @patch("urllib.request.urlopen")
    def test_fetch_text_network_error(self, mock_urlopen):
        """Test fail fast on network error."""
        # Setup
        mock_urlopen.side_effect = urllib.error.URLError("Connection refused")

        # Execute & Verify
        try:
            WebFetcher.fetch_text("https://example.com")
            assert False, "Should have raised AppException"
        except AppException as e:
            assert e.details["error_code"] == ErrorCodes.FETCH_FAILED
            assert e.status_code == 502
            print("\n[TEST] WebFetcher Network Error: Caught")

if __name__ == "__main__":
    t = TestWebFetcher()
    print("\n--- Running Manual Tests ---")
    
    # Mock for manual run
    with patch("urllib.request.urlopen") as mock_open:
        mock_response = MagicMock()
        mock_response.read.return_value = b"<html><body><h1>Manual Test</h1></body></html>"
        mock_response.__enter__.return_value = mock_response
        mock_open.return_value = mock_response
        t.test_fetch_text_success(mock_open)
        
    t.test_fetch_text_invalid_url()
    
    with patch("urllib.request.urlopen") as mock_open:
        mock_open.side_effect = urllib.error.URLError("Manual Error")
        t.test_fetch_text_network_error(mock_open)
        
    print("\n--- All Manual Tests Passed ---")
