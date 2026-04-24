"""Web Fetcher service for retrieving and cleaning external content."""

import logging
import re
import urllib.error
import urllib.request

from backend_v2.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)


class WebFetcher:
    """Simple service to fetch text content from URLs.

    Uses generic utilities to avoid heavy dependencies efficiently for metadata fetching.
    """

    @staticmethod
    def fetch_text(url: str, timeout: int = 5) -> str:
        """Fetches the content of a URL and extracts visible text using naive parsing.

        Useful for quick checkups or reference validation.
        Limits output to first 5000 chars.

        Args:
            url (str): The target URL.
            timeout (int): Connection timeout in seconds.

        Returns:
            str: Cleaned plain text content.

        Raises:
            AppException: If fetching fails or URL is invalid.
        """
        try:
            if not url.startswith(("http://", "https://")):
                raise ValueError("URL must start with http:// or https://")

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

                final_text = text[:5000]  # Limit context size

                # Epic 12: Paywall and Empty Result Warning
                if len(final_text) < 150:
                    logger.warning(
                        "[WebFetcher] %s: Fetched content from '%s' is suspiciously short (%d chars). "
                        "It may be an empty page, bot-protection, or a paywall. RAG Grounding may be compromised.",
                        ErrorCodes.FETCH_FAILED.name,
                        url,
                        len(final_text),
                    )
                else:
                    lower_text = final_text.lower()
                    paywall_cues = [
                        "access denied",
                        "log in to",
                        "login required",
                        "please verify you are a human",
                        "enable javascript",
                        "registration required",
                    ]
                    if any(cue in lower_text for cue in paywall_cues):
                        logger.warning(
                            "[WebFetcher] %s: Fetched content from '%s' contains keywords indicative of a paywall, "
                            "redirect, or anti-bot challenge. RAG Grounding may be compromised.",
                            ErrorCodes.FETCH_FAILED.name,
                            url,
                        )

                # Log success without logging potentially sensitive content
                logger.info("[WebFetcher] Successfully fetched '%s' (%d chars).", url, len(final_text))

                return final_text

        except ValueError as e:
            # Invalid URL format
            logger.error("[WebFetcher] %s: Invalid URL format: %s", ErrorCodes.URL_INVALID.name, e, exc_info=True)
            raise AppException(message=str(e), status_code=400, details={"error_code": ErrorCodes.URL_INVALID}) from e

        except (urllib.error.URLError, TimeoutError) as e:
            # Network or Protocol error
            logger.error("[WebFetcher] %s: Failed to fetch %s: %s", ErrorCodes.FETCH_FAILED.name, url, e, exc_info=True)
            raise AppException(
                message=f"Failed to fetch content from {url}",
                status_code=502,  # Bad Gateway / Upstream Error
                details={"error_code": ErrorCodes.FETCH_FAILED, "original_error": str(e)},
            ) from e

        except Exception as e:
            # Unknown error
            if isinstance(e, AppException):
                raise e

            logger.error(
                "[WebFetcher] %s: Unexpected error for %s: %s",
                ErrorCodes.INTERNAL_SERVER_ERROR.name,
                url,
                e,
                exc_info=True,
            )
            raise AppException(
                message="Unexpected error during web fetch.",
                status_code=500,
                details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR},
            ) from e
