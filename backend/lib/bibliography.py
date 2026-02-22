"""Bibliography Library.

Logic for generating reference lists from knowledge bases.
Previously located in backend/hooks/references.py.
"""

import logging
from typing import Any

from backend.services.reference_manager import ReferenceManager

logger = logging.getLogger(__name__)


def generate_bibliography(text_dump: str, knowledge_base: dict[str, Any]) -> list[str]:
    """Generates a bibliography by scanning text for references in the knowledge base.

    Args:
        text_dump (str): The full text content to scan (e.g. serialized state).
        knowledge_base (Dict[str, Any]): The knowledge base structure containing references and concepts.

    Returns:
        List[str]: A sorted list of unique, full bibliographic reference strings found in the text.
    """
    if not knowledge_base:
        return []

    try:
        # Initialize ReferenceManager with the provided KB
        # Note: ReferenceManager expects {"references": [...], "concepts": {...}}
        rm = ReferenceManager(knowledge_base)

        # Use advanced scan to find both direct citations and concept-linked citations
        references_map = rm.advanced_scan(text_dump)

        # We return just the keys (Full References) sorted
        formatted_list = sorted(list(references_map.relevance_map.keys()))

        logger.debug(f"[Bibliography] Scan complete. Found {len(formatted_list)} unique references.")
        return formatted_list

    except Exception as e:
        logger.error(f"[Bibliography] Generation failed: {e}")
        return []
