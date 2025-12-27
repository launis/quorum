from typing import Any, Optional, Type, List, Dict
import re
from backend.agents.base import BaseAgent
from backend.models.state import WorkflowState

import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)

from backend.models.domain import CoachingPlan
from backend.services.reference_manager import ReferenceManager

class CoachAgent(BaseAgent):
    state_field = "step_coach"
    REQUIRES_KEYS = ["step_judge"]

    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        return CoachingPlan



    # ...

    # ...

    async def prepare_context(self, state: WorkflowState, **kwargs) -> str:
        """
        PRE-HOOK: Loads Domain Knowledge from the Repository (Database) into the Agent instance.
        This ensures the CoachAgent uses the same Unified DB as the Ingestion Service.
        """
        repository = kwargs.get('repository')
        if repository:
            # Load items from DB
            items = repository.get_knowledge_base_items()
            
            # Transform to expected structure
            concepts = {}
            references = []
            
            for item in items:
                i_type = item.get('type')
                if i_type == 'concept':
                    term = item.get('term')
                    defn = item.get('definition')
                    if term and defn:
                        concepts[term] = defn
                elif i_type == 'reference':
                    # Support both old string format and new dict format
                    # enrich_learning_plan expects list of strings OR list of dicts.
                    # Let's populate list of dicts for better data.
                    ref_obj = {
                        "citation": item.get('definition'), # Full citation stored in definition
                        "short_citation": item.get('term'), # Short citation stored in term (e.g. "Smith 2020...")
                        "doi": item.get('doi_link')
                    }
                    references.append(ref_obj)
            
            # Populate self.knowledge_base
            # Populate self.knowledge_base
            self.knowledge_base = {
                "concepts": concepts,
                "references": references # List of dicts
            }
            logger.info(f"[CoachAgent] Loaded {len(concepts)} concepts and {len(references)} references from Unified Database.")
            
            # Formulate the Context String for the Prompt
            context_output = "\nEXTERNAL SOURCES (KNOWLEDGE BASE):\n"
            for ref in references:
                citation = ref.get('citation', '')
                if citation:
                     context_output += f"- {citation}\n"
            
            return context_output
            
        else:
            logger.warning("[CoachAgent] No Repository provided in kwargs. Knowledge Base not loaded from DB.")
            self.knowledge_base = {}
            return ""

    @staticmethod
    def find_citations_with_reasons(text: str, knowledge_base: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Scans text for references and returns them with discovery reasons.
        Returns: {full_citation: [reason1, reason2]}
        """
        found = {} # citation -> list of reasons
        if not knowledge_base:
            return {}
            
        text_lower = text.lower()
        
        # A. Scan References (Loose Author Match)
        refs = knowledge_base.get("references", [])
        ref_lookup = {} 
        for r in refs:
            if isinstance(r, dict):
                short = r.get("short_citation", "")
                full = r.get("citation", "")
                if short:
                    ref_lookup[short.lower()] = full
                    ref_lookup[short.strip("()").lower()] = full
                
                # Check Author Match
                if short and len(short) > 3 and short.lower() in text_lower:
                    if full not in found: found[full] = []
                    found[full].append("Kirjoittajan nimi mainittu")

        refs = knowledge_base.get("references", [])
        ref_lookup = {}
        
        # Helper to normalize citation string for matching
        # "Wang ym. 2023" -> "wang2023", "Acemoglu & Restrepo 2018" -> "acemoglurestrepo2018"
        def normalize_cit_key(k):
            k = k.lower()
            # Remove prefixes first
            prefixes = ["vrt", "cf", "e.g", "esim", "ks", "see"]
            for p in prefixes:
                 if k.startswith(p + ".") or k.startswith(p + " "):
                     k = k.replace(p + ".", "").replace(p + " ", "")
            
            k = re.sub(r'[^a-z0-9]', '', k) # Remove all non-alphanumeric (spaces, &, dots)
            return k

        # Build lookup table
        for r in refs:
             full = r.get("citation", "")
             short = r.get("short_citation", "")
             if short:
                 # Standard lookup
                 ref_lookup[short.lower()] = full
                 # Normalized lookup
                 ref_lookup[normalize_cit_key(short)] = full

        # B. Scan Concepts (Semantic Linking)
        concepts = knowledge_base.get("concepts", {})
        cit_pattern = re.compile(r'\((?:[A-Za-zÅÄÖåäö&,.-]+\s+)+\d{4}[a-z]?\)')
        
        # Concepts to ignore as "too generic" contexts
        ignored_concepts = {"abstrakti", "tiivistelmä", "johdanto", "yhteenveto", "lähdeluettelo", "lähteet", "references", "abstract", "summary", "introduction"}

        for term, defn in concepts.items():
            if not term: continue
            if term.lower() in ignored_concepts: continue
            
            if len(term) > 3 and term.lower() in text_lower:
                matches = cit_pattern.findall(defn)
                for m in matches:
                    # Cleanup parens
                    raw_key = m.strip("()")
                    
                    # 1. Try Exact Match
                    resolved_ref = ref_lookup.get(raw_key.lower())
                    
                    # 2. Try Normalized Match
                    if not resolved_ref:
                        resolved_ref = ref_lookup.get(normalize_cit_key(raw_key))
                    
                    # 3. Ultra-Loose Match (Name + Year)
                    # Solves: "Borsboom ym. 2004" vs DB "Borsboom & Mellenbergh 2004"
                    # 3. Ultra-Loose Match (Name + Year[suffix])
                    # Solves: "Perez ym. 2022b" should NOT match "Perez 2022a"
                    if not resolved_ref:
                        # Extract year AND optional suffix (2022a)
                        year_match = re.search(r'(\d{4}[a-z]?)', raw_key.lower())
                        if year_match:
                            y = year_match.group(1) # e.g. "2022b"
                            
                            # Extract author (first word usually)
                            # cleanup "vrt." etc first
                            clean_scan = raw_key.lower()
                            prefixes = ["vrt", "cf", "e.g", "esim", "ks", "see"]
                            for p in prefixes:
                                clean_scan = clean_scan.replace(p + ".", "").replace(p + " ", "")
                            
                            # Get first significant word (Author)
                            words = re.findall(r'[a-zåäö]+', clean_scan)
                            if words:
                                author = words[0]
                                # Scan ALL refs
                                for r_item in refs:
                                    full_txt = r_item.get("citation", "")
                                    full_lower = full_txt.lower()
                                    
                                    # Must contain Name
                                    if author not in full_lower:
                                        continue
                                        
                                    # Must contain EXACT Year (e.g. "2022b")
                                    # Use basic find, but ensure we don't match "2022" inside "2022b" if we searched for "2022"
                                    # Actually, if we search "2022b", it MUST be in text.
                                    # If we search "2022", and text has "2022a", strictly it's a mismatch or ambiguous.
                                    # But for now, ensuring the SEARCH string exists in TARGET is enough to fix 2022b case.
                                    
                                    if y in full_lower:
                                        # One safety check: If y is "2022", we don't want to match "2022b" blindly? 
                                        # Let's keep it simple: The specific key used by user (2022b) must be found in ref.
                                        resolved_ref = full_txt
                                        break

                    # 4. Fallback: Just return cleaned text if no DB match
                    if not resolved_ref:
                         # Cleanup prefixes commonly found in Finnish texts
                         prefixes = ["vrt.", "cf.", "e.g.", "esim.", "ks.", "see"]
                         clean_raw = raw_key.strip()
                         for p in prefixes:
                             if clean_raw.lower().startswith(p + " "):
                                 clean_raw = clean_raw[len(p)+1:].strip()
                             elif clean_raw.lower() == p: 
                                 continue
                         resolved_ref = clean_raw

                    if resolved_ref and len(resolved_ref) > 4: 
                        if resolved_ref not in found: found[resolved_ref] = []
                        found[resolved_ref].append(f"Käsite: '{term}'")

        return found

    @staticmethod
    def find_citations(text: str, knowledge_base: Dict[str, Any]) -> List[str]:
        """Wrapper for backward compatibility."""
        res = CoachAgent.find_citations_with_reasons(text, knowledge_base)
        return sorted(list(res.keys()))

    def post_process(self, state: WorkflowState) -> WorkflowState:
        """
        Lifecycle Hook: Post-Execution.
        Triggers bibliography validation and enrichment.
        """
        return self.enrich_learning_plan(state)

    def enrich_learning_plan(self, state: WorkflowState) -> WorkflowState:
        """
        POST-HOOK: Scans the ENTIRE Workflow State.
        Populates bibliography with Context (why the reference was chosen).
        """
        logger.info("[CoachAgent] Running enrich_learning_plan hook...")
        
        if not hasattr(self, 'knowledge_base') or not self.knowledge_base:
            return state

        coach_plan_data = getattr(state, self.state_field, None)
        if not coach_plan_data:
            return state

        # Prepare Scan Data (Global)
        try:
            full_state_dict = state.to_flat_dict()
            text_dump = str(full_state_dict)
        except Exception:
            text_dump = str(state.dict())

        # 1. Strict Scan (Explicit citations)
        kb_struct = {"references": self.knowledge_base.get("references", [])}
        rm = ReferenceManager(kb_struct)
        strict_refs = rm.scan_and_collect_references(text_dump)
        
        # 2. Loose/Concept Scan (Implicit)
        loose_map = self.find_citations_with_reasons(text_dump, self.knowledge_base)
        
        # 3. Merge and Format
        final_map = {}
        
        for ref in strict_refs:
            final_map[ref] = {"Suora viittaus"}
            
        for ref, reasons in loose_map.items():
            if ref not in final_map:
                final_map[ref] = set()
            final_map[ref].update(reasons)
            
        formatted_list = []
        for ref in sorted(final_map.keys()):
            reasons = sorted(list(final_map[ref]))
            context_str = ", ".join(reasons)
            if context_str:
                formatted_list.append(f"{ref}  [Konteksti: {context_str}]")
            else:
                formatted_list.append(ref)

        if hasattr(coach_plan_data, 'lahdeluettelo'):
             coach_plan_data.lahdeluettelo = formatted_list
             logger.info(f"[CoachAgent] Populated bibliography with {len(formatted_list)} references found in global state.")

        return state

