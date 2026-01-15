"""Search Tool Module.

Encapsules external search functionality (Google Custom Search).
Previously located in backend/hooks/search.py.
"""

import logging
import os
from typing import Any, Dict, List, Optional

from googleapiclient.discovery import build

logger = logging.getLogger(__name__)


class GoogleSearchTool:
    """Tool for executing Google Custom Search API queries."""

    def __init__(self, api_key: Optional[str] = None, cx: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_SEARCH_API_KEY")
        self.cx = cx or os.getenv("GOOGLE_SEARCH_CX")
        
        if not self.api_key or not self.cx:
            logger.warning("[GoogleSearchTool] Missing API Credentials (GOOGLE_SEARCH_API_KEY/CX). Search disabled.")
            self._service = None
        else:
            try:
                self._service = build("customsearch", "v1", developerKey=self.api_key)
            except Exception as e:
                logger.error(f"[GoogleSearchTool] Failed to build service: {e}")
                self._service = None

    def search(self, queries: List[str], limit: int = 3) -> List[Dict[str, Any]]:
        """Executes search for a list of queries.

        Args:
            queries (List[str]): List of query strings.
            limit (int): Max queries to execute.

        Returns:
            List[Dict[str, Any]]: Combined search results.
        """
        if not self._service:
            # Fallback/Fail-fast based on requirements. 
            # If explicit functionality is requested but config missing, might return empty or raise.
            return []

        all_results = []
        
        for i, query in enumerate(queries[:limit]):
            logger.debug(f"[GoogleSearchTool] Query {i + 1}: {query}")
            try:
                res = self._service.cse().list(q=query, cx=self.cx, num=3).execute()

                for item in res.get("items", []):
                    all_results.append(
                        {
                            "query": query,
                            "title": item.get("title"),
                            "link": item.get("link"),
                            "snippet": item.get("snippet"),
                        }
                    )
            except Exception as q_err:
                logger.warning(f"[GoogleSearchTool] Query '{query}' failed: {q_err}")

        return all_results
