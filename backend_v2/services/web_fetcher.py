"""Web Fetcher service for retrieving and cleaning external content."""

from __future__ import annotations

import logging
import re

import httpx

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)

_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) CognitiveQuorum/1.0"
_PAYWALL_CUES: tuple[str, ...] = (
    "access denied",
    "log in to",
    "login required",
    "please verify you are a human",
    "enable javascript",
    "registration required",
)

__all__ = [
    "WebFetcher",
]


class WebFetcher:
    """Service to fetch and sanitize plain text content from external HTTP(S) URLs.

    Performs bounded HTTP GET requests via httpx and strips HTML markup for reference validation.
    """

    @staticmethod
    def _validate_request(url: str, timeout: int) -> None:
        """Validate target URL scheme and connection timeout bounds before network execution.

        Args:
            url: Target HTTP or HTTPS URL string.
            timeout: Connection timeout in seconds (must be > 0).

        Returns:
            None

        Raises:
            AppException: With ErrorCodes.URL_INVALID (400) if URL does not start with http:// or https://,
                or ErrorCodes.VALIDATION_FAILED (400) if timeout is less than or equal to 0.
        """
        if not url or not url.strip() or not url.startswith(("http://", "https://")):
            msg = "URL must start with http:// or https://"
            logger.error(
                "[WebFetcher] %s: Invalid URL format: %s",
                ErrorCodes.URL_INVALID.name,
                msg,
                extra={"error_code": ErrorCodes.URL_INVALID.value},
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=400,
                details={"error_code": ErrorCodes.URL_INVALID},
            )

        if timeout <= 0:
            msg = f"Invalid timeout={timeout} for WebFetcher; must be a positive integer."
            logger.error(
                "[WebFetcher] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED},
            )

    @staticmethod
    def _extract_clean_text(html_bytes: bytes) -> str:
        """Decode raw HTML bytes and strip scripts, styles, and tags into bounded plain text.

        Args:
            html_bytes: Raw HTTP response body bytes.

        Returns:
            Cleaned plain text truncated to the maximum context character budget.
        """
        html_text = html_bytes.decode("utf-8", errors="ignore")

        # Strip executable script and style blocks before tag removal to prevent code leakage into grounding text.
        text = re.sub(r"<(script|style).*?>.*?</\1>", "", html_text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<.*?>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()

        # Truncate extracted text only when web_fetcher_max_extracted_chars > 0.
        max_chars = get_settings().web_fetcher_max_extracted_chars
        if max_chars > 0:
            return text[:max_chars]
        return text

    @staticmethod
    def _warn_if_compromised_content(final_text: str, url: str) -> None:
        """Emit structured warnings when extracted text indicates a paywall, bot challenge, or empty page.

        Args:
            final_text: Sanitized plain text extracted from the response.
            url: Source URL for diagnostic attribution.

        Returns:
            None
        """
        # Resolve minimum extracted text length from settings SSOT.
        min_chars = get_settings().web_fetcher_min_extracted_chars
        if len(final_text) < min_chars:
            logger.warning(
                "[WebFetcher] %s: Fetched content from '%s' is suspiciously short (%d chars). "
                "It may be an empty page, bot-protection, or a paywall. RAG Grounding may be compromised.",
                ErrorCodes.FETCH_FAILED.name,
                url,
                len(final_text),
            )
            return

        lower_text = final_text.lower()
        if any(cue in lower_text for cue in _PAYWALL_CUES):
            logger.warning(
                "[WebFetcher] %s: Fetched content from '%s' contains keywords indicative of a paywall, "
                "redirect, or anti-bot challenge. RAG Grounding may be compromised.",
                ErrorCodes.FETCH_FAILED.name,
                url,
            )

    @staticmethod
    def fetch_text(url: str, timeout: int | None = None) -> str:
        """Fetch the content of a URL synchronously using httpx and extract visible plain text.

        Useful for quick checkups or reference validation. Truncates output when configured via
        settings.web_fetcher_max_extracted_chars.

        Args:
            url: The target HTTP or HTTPS URL.
            timeout: Optional connection timeout in seconds; defaults to settings.mcp_discovery_timeout_seconds.

        Returns:
            Cleaned plain text content.

        Raises:
            AppException: With ErrorCodes.URL_INVALID (400) if the URL scheme is invalid,
                ErrorCodes.VALIDATION_FAILED (400) if timeout is non-positive,
                ErrorCodes.FETCH_FAILED (502) if network transport or HTTP status fails,
                or ErrorCodes.INTERNAL_SERVER_ERROR (500) on unexpected runtime errors.
        """
        resolved_timeout = timeout if timeout is not None else get_settings().mcp_discovery_timeout_seconds
        WebFetcher._validate_request(url, resolved_timeout)

        try:
            headers = {"User-Agent": _USER_AGENT}

            with httpx.Client(headers=headers, timeout=resolved_timeout, follow_redirects=True) as client:
                response = client.get(url)
                response.raise_for_status()
                final_text = WebFetcher._extract_clean_text(response.content)
                WebFetcher._warn_if_compromised_content(final_text, url)

                # Emit telemetry summary without logging raw payload content to enforce DLP.
                logger.info("[WebFetcher] Successfully fetched '%s' (%d chars).", url, len(final_text))
                return final_text

        except httpx.RequestError as e:
            logger.error(
                "[WebFetcher] %s: Failed to fetch %s: %s",
                ErrorCodes.FETCH_FAILED.name,
                url,
                e,
                extra={"error_code": ErrorCodes.FETCH_FAILED.value},
                exc_info=True,
            )
            raise AppException(
                message=f"Failed to fetch content from {url}",
                status_code=502,
                details={"error_code": ErrorCodes.FETCH_FAILED, "original_error": str(e)},
            ) from e

        except httpx.HTTPStatusError as e:
            logger.error(
                "[WebFetcher] %s: HTTP error %s for %s",
                ErrorCodes.FETCH_FAILED.name,
                e.response.status_code,
                url,
                extra={"error_code": ErrorCodes.FETCH_FAILED.value},
                exc_info=True,
            )
            raise AppException(
                message=f"Failed to fetch content from {url}: HTTP {e.response.status_code}",
                status_code=502,
                details={"error_code": ErrorCodes.FETCH_FAILED, "original_error": str(e)},
            ) from e

        except AppException:
            raise

        except Exception as e:
            logger.error(
                "[WebFetcher] %s: Unexpected error for %s: %s",
                ErrorCodes.INTERNAL_SERVER_ERROR.name,
                url,
                e,
                extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
                exc_info=True,
            )
            raise AppException(
                message="Unexpected error during web fetch.",
                status_code=500,
                details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR},
            ) from e
