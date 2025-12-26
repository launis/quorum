
import re
import logging
from typing import List, Dict, Any, Set, Optional

logger = logging.getLogger(__name__)

class ReferenceManager:
    """
    Centralized service for managing citations and generating the master bibliography.
    Scans text for short citations (e.g. "Author 2023") and resolves them against the Knowledge Base.
    """

    def __init__(self, knowledge_base: Dict[str, Any]):
        self.knowledge_base = knowledge_base
        self.references_map = self._build_reference_map()
        
        # Regex to find parenthetical citations: (Author 2020) or (Author et al. 2020)
        # Matches: "(Smith 2020)", "(Smith & Jones 2020)", "(Smith ym. 2020)", "(vrt. Smith 2020)"
        self.citation_pattern = re.compile(r'\((?:vrt\.\s*)?(?:[A-Za-zÅÄÖåäö&,-]+\s+)+(?:et\s+al\.|ym\.)?\s*,?\s*\d{4}[a-z]?\)')

    def _build_reference_map(self) -> Dict[str, str]:
        """
        Builds a lookup map: Short Citation -> Full Reference String.
        Key is normalized lowercase for matching.
        """
        ref_map = {}
        refs = self.knowledge_base.get("references", [])
        
        # Handle list of dicts or list of strings logic
        if isinstance(refs, list):
            for r in refs:
                if isinstance(r, dict):
                    full = r.get('citation') or r.get('definition')
                    short = r.get('short_citation')
                    
                    if short and full:
                        ref_map[short.lower()] = full
                        # Also map just "Author 2020" from "Author & Co 2020"?
                        # For now, rely on strict short citation from DB.
                
                elif isinstance(r, str):
                    # Legacy string reference
                    # Try to extract short citation on the fly?
                    # "Smith, J. 2020: Title..." -> "Smith 2020"
                    match = re.match(r'^([A-Za-zÅÄÖåäö&]+(?:, [A-Za-zÅÄÖåäö&]+)*)\.?\s*(\d{4}[a-z]?)', r)
                    if match:
                        authors = match.group(1).split(',')[0].strip() # First author surname
                        year = match.group(2)
                        short = f"{authors} {year}"
                        ref_map[short.lower()] = r
                        
        return ref_map

    def scan_and_collect_references(self, content: Any) -> List[str]:
        """
        Recursively scans a JSON-like structure (dict/list/str) for citations.
        Returns a sorted list of unique Full Reference strings used in the content.
        """
        used_refs: Set[str] = set()
        
        def _recursive_scan(obj):
            if isinstance(obj, str):
                self._scan_text(obj, used_refs)
            elif isinstance(obj, dict):
                for v in obj.values():
                    _recursive_scan(v)
            elif isinstance(obj, list):
                for item in obj:
                    _recursive_scan(item)

        _recursive_scan(content)
        
        return sorted(list(used_refs))

    def _scan_text(self, text: str, used_refs: Set[str]):
        """
        Scans a single string for citations and updates the set.
        """
        if not text or len(text) < 10: return
        
        matches = self.citation_pattern.findall(text)
        for match in matches:
            # Clean: "(vrt. Smith 2020)" -> "smith 2020"
            clean = match.strip("()")
            clean = clean.replace("vrt.", "").strip()
            clean_lower = clean.lower()
            
            # 1. Direct Match against Short Citations
            if clean_lower in self.references_map:
                used_refs.add(self.references_map[clean_lower])
            else:
                # 2. Fuzzy Match? 
                # If "Smith & Jones 2020" is in text, but Map has "Smith et al. 2020"
                # This requires more complex logic. 
                # For now, check if map key is substring of text citation or vice versa
                found = False
                for map_key, full_ref in self.references_map.items():
                    if map_key in clean_lower or clean_lower in map_key:
                        used_refs.add(full_ref)
                        found = True
                        break
