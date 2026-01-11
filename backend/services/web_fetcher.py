"""Web Fetcher service for retrieving and cleaning external content."""

import logging
import re
import urllib.error
import urllib.request

logger = logging.getLogger(__name__)


class WebFetcher:
    """Simple service to fetch text content from URLs.

    Uses generic utilities to avoid heavy dependencies efficiently for metadata fetching.
    """

    @staticmethod
    def fetch_text(url: str, timeout: int = 5) -> str | None:
        """Fetches the content of a URL and extracts visible text using naive parsing.

        Useful for quick checkups or reference validation.
        Limits output to first 5000 chars.

        Args:
            url (str): The target URL.
            timeout (int): Connection timeout in seconds.

        Returns:
            Optional[str]: Cleaned plain text content or None if failed.

        """
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) CognitiveQuorum/1.0"}
            req = urllib.request.Request(url, headers=headers)

            with urllib.request.urlopen(req, timeout=timeout) as response:
                html_bytes = response.read()
                html_text = html_bytes.decode("utf-8", errors="ignore")

                # Naive HTML to Text
                # 1. Remove scripts and styles
                text = re.sub(r"<(script|style).*?>.*?</\1>", "", html_text, flags=re.DOTALL | re.IGNORECASE)
                # 2. Remove tags
                text = re.sub(r"<.*?>", " ", text)
                # 3. Collapse whitespace
                text = re.sub(r"\s+", " ", text).strip()

                return text[:5000]  # Limit context size

        except Exception as e:
            logger.error(f"[WebFetcher] Failed to fetch {url}: {e}")
            return None
