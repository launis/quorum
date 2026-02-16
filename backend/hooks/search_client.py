"""Search Tool Module.

Encapsules external search functionality (Google Custom Search).
Strictly compliant with RFC 7807 and Python Backend Mandates.
"""

import logging
import os
from typing import Any, List

from pydantic import BaseModel, ConfigDict, Field

try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    build = None
    HttpError = None

from backend.exceptions import AppException, ConfigurationError, ErrorCodes

logger = logging.getLogger(__name__)


class SearchResultItem(BaseModel):
    """Immutable model for a single search result."""

    title: str = Field(..., description="Result title")
    link: str = Field(..., description="Result URL")
    snippet: str = Field(..., description="Text snippet")
    query: str = Field(..., description="Original query")

    model_config = ConfigDict(frozen=True, extra="ignore")


class GoogleSearchTool:
    """Tool for executing Google Custom Search API queries.
    
    Adheres to Fail Fast: Raises ConfigurationError on missing deps/creds.
    """

    def __init__(self, api_key: str | None = None, cx: str | None = None):
        self.api_key = api_key or os.getenv("GOOGLE_SEARCH_API_KEY")
        self.cx = cx or os.getenv("GOOGLE_SEARCH_CX")

        if not build:
            error_code = ErrorCodes.SERVICE_DEPENDENCY_MISSING
            msg = "Python package 'google-api-python-client' is not installed."
            logger.error(f"[GoogleSearchTool] {error_code}: {msg}")
            raise ConfigurationError(msg)

        if not self.api_key or not self.cx:
            error_code = ErrorCodes.SEARCH_CONFIG_ERROR
            msg = "Missing API Credentials (GOOGLE_SEARCH_API_KEY/CX)."
            logger.error(f"[GoogleSearchTool] {error_code}: {msg}")
            raise ConfigurationError(msg)

        try:
            self._service = build("customsearch", "v1", developerKey=self.api_key)
        except Exception as e:
            error_code = ErrorCodes.SEARCH_CONFIG_ERROR
            logger.error(f"[GoogleSearchTool] {error_code}: Failed to build service: {e}", exc_info=True)
            raise ConfigurationError(f"Failed to initialize Google Search: {e}") from e

    def search(self, queries: List[str], limit: int = 3, language: str = "en") -> List[SearchResultItem]:
        """Executes search for a list of queries.

        Args:
            queries: List of query strings.
            limit: Max queries to execute.
            language: Language code (e.g. 'en', 'fi'). Defaults to 'en'.

        Returns:
            List[SearchResultItem]: Combined search results.

        Raises:
            AppException: If search execution fails (SEARCH_EXECUTION_FAILED).
        """
        if not self._service:
            # Should be unreachable if __init__ fails fast, but strictly checking state.
            raise ConfigurationError("Google Search Service not initialized.")

        # Language Logic
        lang_code = language.lower().split("-")[0]
        
        # Default to US/English
        gl_param = "us"
        lr_param = "lang_en"

        if lang_code == "fi":
            gl_param = "fi"
            lr_param = "lang_fi"
        # Add more mappings here as needed
        
        logger.debug(f"[GoogleSearchTool] Context: Language='{language}' -> gl='{gl_param}', lr='{lr_param}'")

        all_results: List[SearchResultItem] = []

        for i, query in enumerate(queries[:limit]):
            logger.debug(f"[GoogleSearchTool] Query {i + 1}: {query}")
            try:
                # API Call with Language Context
                res = self._service.cse().list(
                    q=query, 
                    cx=self.cx, 
                    num=3,
                    gl=gl_param,
                    lr=lr_param
                ).execute()

                for item in res.get("items", []):
                    # Strict Model Creation
                    all_results.append(
                        SearchResultItem(
                            query=query,
                            title=item.get("title", "No Title"),
                            link=item.get("link", ""),
                            snippet=item.get("snippet", ""),
                        )
                    )
            except Exception as e:
                # 3.8 Upstream Error Mapping (Google API)
                if HttpError and isinstance(e, HttpError):
                    if e.resp.status == 403:
                        reason = str(e)
                        if "Custom Search JSON API" in reason:
                            error_code = ErrorCodes.SEARCH_CONFIG_ERROR
                            msg = "Google Custom Search API is not enabled in Cloud Console."
                            logger.error(f"[GoogleSearchTool] {error_code}: {msg}")
                            raise ConfigurationError(
                                message=msg,
                                details={
                                    "error_code": error_code, 
                                    "action": "Enable 'Custom Search JSON API' in Google Cloud Console."
                                }
                            ) from e
                        if "Project has not enabled the API" in reason: # Common variation
                             error_code = ErrorCodes.SEARCH_CONFIG_ERROR
                             msg = "Google Cloud Project API not enabled."
                             logger.error(f"[GoogleSearchTool] {error_code}: {msg}")
                             raise ConfigurationError(msg, details={"original_error": reason}) from e

                # Fail Fast on other API errors
                error_code = ErrorCodes.SEARCH_EXECUTION_FAILED
                logger.error(f"[GoogleSearchTool] {error_code}: Query '{query}' failed: {e}", exc_info=True)
                raise AppException(
                    message=f"Search execution failed for query '{query}': {e}",
                    status_code=502, # Bad Gateway (Upstream Error)
                    details={"error_code": error_code, "query": query}
                ) from e

        return all_results
