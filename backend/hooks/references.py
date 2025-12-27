from typing import List, Dict, Any
import logging
from backend.services.reference_manager import ReferenceManager

logger = logging.getLogger(__name__)

def generate_bibliography(text_dump: str, knowledge_base: Dict[str, Any]) -> List[str]:
    """
    Agent Hook: Generates a bibliography by scanning the text for explicit and implicit references.
    Delegates logic to the ReferenceManager service.
    
    Args:
        text_dump (str): The full text content to scan (e.g. serialized state).
        knowledge_base (dict): The knowledge base structure containing references and concepts.
        
    Returns:
        List[str]: A sorted list of full reference strings found in the text.
    """
    if not knowledge_base:
        return []
        
    try:
        # Initialize ReferenceManager with the provided KB
        # Note: ReferenceManager expects {"references": [...], "concepts": {...}} 
        # CoachAgent.knowledge_base follows this structure.
        rm = ReferenceManager(knowledge_base)
        
        # Use advanced scan to find both direct citations and concept-linked citations
        references_map = rm.advanced_scan(text_dump)
        
        # We return just the keys (Full References) sorted
        formatted_list = sorted(list(references_map.keys()))
        
        logger.info(f"[ReferenceHook] Scan complete. Found {len(formatted_list)} unique references.")
        return formatted_list
        
    except Exception as e:
        logger.error(f"[ReferenceHook] Bibliography generation failed: {e}")
        return []
