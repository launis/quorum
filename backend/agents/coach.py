from typing import Any, Optional, Type, List, Dict
import re
from backend.agents.base import BaseAgent
from backend.models.state import WorkflowState

import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)

from backend.models.domain import CoachingPlan

class CoachAgent(BaseAgent):
    state_field = "step_coach"

    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        return CoachingPlan

    def _build_prompt(self, state: WorkflowState, repository: Any = None, external_context_override: str = "", preloaded_concepts: List[Dict] = [], **kwargs) -> str:
        # ... (previous code) ...
        # (Replace instructions at the end)

        # Explicit Instruction for Citation
        context_str += "\n\nIMPORTANT: When creating 'kehityskohteet_konkreettisesti' (Action Items), you MUST include relevant citations."
        context_str += "\n- Look at the 'EXTERNAL SOURCES' and 'REFERENCE MATERIAL' above."
        context_str += "\n- If an Action Item relates to a concept (e.g. Reflection, Logic), find a matching Source/Reference."
        context_str += "\n- Add the citation string to the 'resurssit' list of that Action Item."
        context_str += "\n- DO NOT list the Concept Name as a resource. You must find the supporting reference (e.g. 'Strathern 1997')."
        context_str += "\n- DO NOT invent references. Use only the provided strings in 'VALID CITATION KEYS' or 'REFERENCE MATERIAL'."
        context_str += "\n- In the text content (kuvaus/palaute), use the short format: `(vrt. Author Year)` or `(Author ym. Year)`."

        return context_str + base_prompt

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
            self.knowledge_base = {
                "concepts": concepts,
                "references": references # List of dicts
            }
            logger.info(f"[CoachAgent] Loaded {len(concepts)} concepts and {len(references)} references from Unified Database.")
            
        else:
            logger.warning("[CoachAgent] No Repository provided in kwargs. Knowledge Base not loaded from DB.")
            self.knowledge_base = {}

        return "" # No additional text context to append here, just side-loading data

    @staticmethod
    def find_citations(text: str, knowledge_base: Dict[str, Any]) -> List[str]:
        """
        Static utility: Scans text for concepts/references defined in the KB.
        Returns a list of formatted citation strings (e.g. "📚 Author, 2020...").
        """
        found_refs = []
        if not knowledge_base or "concepts" not in knowledge_base:
            return found_refs
            
        concepts_dict = knowledge_base["concepts"]
        
        # Handle references (could be list of dicts or legacy dict)
        raw_refs = knowledge_base.get("references", [])
        refs_list = []
        if isinstance(raw_refs, list):
            for r in raw_refs:
                if isinstance(r, dict):
                    refs_list.append(r.get('citation') or r.get('definition') or "")
                elif isinstance(r, str):
                    refs_list.append(r)
        elif isinstance(raw_refs, dict):
            refs_list = raw_refs.get("bibliography", [])
            
        import re
        citation_pattern = re.compile(r'\((?:vrt\.\s*)?(?:[A-Za-zÅÄÖåäö&,-]+\s+)+(?:et\s+al\.|ym\.)?\s*,?\s*\d{4}[a-z]?\)')
        
        text_lower = text.lower()
        
        for term, definition in concepts_dict.items():
            if term.lower() in text_lower:
                # 1. Look for citations IN the definition
                matches = citation_pattern.findall(definition)
                for match in matches:
                    clean_citation = match.strip("()").replace("vrt. ", "")
                    parts = clean_citation.split()
                    if not parts: continue
                    
                    year_part = parts[-1] 
                    author_parts = [p.strip(".,&") for p in parts[:-1] if p.lower() not in ["ym.", "et", "al.", "vrt.", "&"]]
                    
                    for ref in refs_list:
                        if year_part in ref:
                            if any(auth in ref for auth in author_parts):
                                if not any(ref[:30] in r for r in found_refs):
                                    found_refs.append(f"📚 {ref}")
                        elif clean_citation in ref: 
                            if not any(ref[:30] in r for r in found_refs):
                                found_refs.append(f"📚 {ref}")
                                
                # 2. Check Concept Name Match
                if term.lower() not in ["bibliography", "viitteet"]:
                     for ref in refs_list:
                        if term.lower() in ref.lower():
                            if not any(ref[:30] in r for r in found_refs):
                                found_refs.append(f"📚 {ref}")
                                
        return found_refs

    def enrich_learning_plan(self, state: WorkflowState) -> WorkflowState:
        """
        POST-HOOK: Scans the generated ActionItems. 
        Searches the JSON Knowledge Base for relevant citations (via concept definitions) and appends them.
        """
        logger.info("[CoachAgent] Running enrich_learning_plan hook...")
        
        # 1. Get the output from state using the state_field
        coach_plan_data = getattr(state, self.state_field, None)
        if not coach_plan_data:
            return state
            
        def get_attr(obj, attr):
            return getattr(obj, attr) if hasattr(obj, attr) else obj.get(attr)

        items = get_attr(coach_plan_data, 'kehityskohteet_konkreettisesti')
        if not items:
            return state

        # Regex to find parenthetical citations like (Author Year), (Author et al. Year), (vrt. Author ym. Year)
        citation_pattern = re.compile(r'\((?:vrt\.\s*)?(?:[A-Za-zÅÄÖåäö&,-]+\s+)+(?:et\s+al\.|ym\.)?\s*,?\s*\d{4}[a-z]?\)')

        # Helper to flatten items from groups for processing
        all_action_items = []
        is_grouped = False
        
        # Check first item to determine structure (or try both)
        if items and len(items) > 0:
            first = items[0]
            # If it has 'kohdat' or 'items', it's a group
            if hasattr(first, 'kohdat') or (isinstance(first, dict) and 'kohdat' in first):
                is_grouped = True
        
        if is_grouped:
            for group in items:
                sub_items = get_attr(group, 'kohdat') or []
                for sub in sub_items:
                    all_action_items.append(sub)
        else:
            # Legacy flat list
            all_action_items = items

        # Regex to find parenthetical citations like (Author Year), (Author et al. Year), (vrt. Author ym. Year)
        citation_pattern = re.compile(r'\((?:vrt\.\s*)?(?:[A-Za-zÅÄÖåäö&,-]+\s+)+(?:et\s+al\.|ym\.)?\s*,?\s*\d{4}[a-z]?\)')

        updated_count = 0
        for item in all_action_items:
            # item is ActionItem object or dict
            otsikko = get_attr(item, 'otsikko') or ""
            kuvaus = get_attr(item, 'kuvaus') or ""
            resurssit_list = get_attr(item, 'resurssit')
            if resurssit_list is None:
                resurssit_list = []
            
            # Normalize to avoid duplicates
            current_res_lower = [r.lower() for r in resurssit_list]
            
            # Combine text for search
            desc_text = (otsikko + " " + kuvaus + " " + " ".join(current_res_lower)).lower()
            
            # Search bibliography based on specific keywords found in the item
            # 1. Internal Knowledge Base
            if self.knowledge_base:
                # Use shared static logic for lookup
                found_refs = CoachAgent.find_citations(desc_text, self.knowledge_base)
                for ref in found_refs:
                    if not any(ref[:30] in r for r in resurssit_list):
                        resurssit_list.append(ref)
                        updated_count += 1

            # 2. External Bibliography Context
            if state.inputs.bibliography_context:
                for bib_item in state.inputs.bibliography_context:
                    bib_lower = bib_item.lower()
                    if bib_lower not in [r.lower() for r in resurssit_list]:
                         # Heuristic: check overlap of significant words
                         bib_words = set(w for w in bib_lower.split() if len(w) > 5)
                         desc_words = set(w for w in desc_text.split() if len(w) > 5)
                         if bib_words & desc_words:
                             resurssit_list.append(f"🔗 {bib_item}")
                             updated_count += 1
            
            # Update item
            if hasattr(item, 'resurssit'):
                item.resurssit = resurssit_list
            else:
                item['resurssit'] = resurssit_list
        
        # ... rest of the function (lahdeluettelo) ...
        
        # --- Populate 'lahdeluettelo' in the Main Object ---
        # User REQ: "juuri tässä tuloksessa käytetty" -> Only list references actually cited in the text.
        
        used_refs = set()
        
        # Helper to find used refs
        def scan_for_citations(text, available_refs):
            hits = set()
            if not text: return hits
            text_lower = text.lower()
            
            for ref_obj in available_refs:
                # available_refs is EXPECTED to be list of dicts with 'citation' and optionally 'short_citation'
                # But here we might just have strings in self.knowledge_base?
                # Let's handle both.
                
                full_citation = ""
                short_citation = ""
                
                if isinstance(ref_obj, str):
                    full_citation = ref_obj
                    # Try execution-time extraction if needed, or just match content
                elif isinstance(ref_obj, dict):
                    full_citation = ref_obj.get('definition', '') or ref_obj.get('citation', '')
                    short_citation = ref_obj.get('short_citation', '')
                    
                # Search strategy:
                # 1. Short citation match (e.g. "Acemoglu & Restrepo 2018")
                if short_citation and short_citation.lower() in text_lower:
                    hits.add(full_citation)
                    continue
                    
                # 2. Author/Year heuristic from full citation (fallback)
                # e.g. "Acemoglu" and "2018" appear near each other? 
                # Strict mode: Only assume usage if Short Citation is found OR explicit mention.
                # Let's rely on Short Citation if available.
                
            return hits

        # Gather all text content from flattened list (all_action_items)
        all_text = ""
        for item in all_action_items:
            all_text += (get_attr(item, 'otsikko') or "") + " " + (get_attr(item, 'kuvaus') or "") + " "
            
        # 1. DB References (The primary source now)
        # We stored them in state.aux_data['db_references'] as STRINGS (definitions) in execute()
        # But we need short citations too.
        # execute() logic: 
        # db_refs = [i['definition']...] -> Strings
        # This makes strict matching hard unless we re-extract.
        # BETTER: Let's fetch retrieval results again or assume the Agent did its job.
        
        # Let's try to match against the raw knowledge base properties if available
        
        # Get DB items from internal KB if loaded
        if self.knowledge_base and "references" in self.knowledge_base:
            # self.knowledge_base["references"] might be list of dicts now (new parser) or list of strings (old parser).
            # The new parser returns list of {citation, short_citation, doi}.
            
            kb_refs = self.knowledge_base["references"] # List of dicts
            
            for ref_item in kb_refs:
                if isinstance(ref_item, dict):
                     citation = ref_item.get('citation')
                     short = ref_item.get('short_citation')
                     
                     if short and short.lower() in all_text.lower():
                         used_refs.add(citation)
                     elif citation and citation[:20].lower() in all_text.lower():
                         used_refs.add(citation)

        # 2. External Bibliography (fallback)
        if state.inputs.bibliography_context:
             for bib in state.inputs.bibliography_context:
                 # Check if appears in text
                 # Naive check
                 if bib[:20].lower() in all_text.lower():
                     used_refs.add(bib)


        # Assign to object
        if hasattr(coach_plan_data, 'lahdeluettelo'):
            # Convert set to sorted list
            coach_plan_data.lahdeluettelo = sorted(list(used_refs))
        
        return state
