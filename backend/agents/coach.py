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
        context_str += "\n- CITATION STYLE (Kielitoimisto/Finnish Standard): Use precise parenthetical referencing, e.g., `(Sukunimi 2024)` or `(Sukunimi & Meikäläinen 2024)`."
        context_str += "\n- EVIDENCE: Support your assessment with proofs (todisteita) from the Knowledge Base. Do not just describe Sitra; explain WHY the user's performance is good/bad based on the Theory."
        context_str += "\n- CONNECTION: 'Tämä havainto saa tukea tietokannasta (Pfeifer 2025)...'"
        context_str += "\n- Create validated assertions by linking the Assessment to the Database references."

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
        # import re -> Removed, using global
        cit_pattern = re.compile(r'\((?:[A-Za-zÅÄÖåäö&,.-]+\s+)+\d{4}[a-z]?\)')
        
        for term, defn in concepts.items():
            if term and len(term) > 3 and term.lower() in text_lower:
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
            # Format: "Citation Text [Konteksti: Syy, Syy]"
            context_str = ", ".join(reasons)
            if context_str:
                formatted_list.append(f"{ref}  [Konteksti: {context_str}]")
            else:
                formatted_list.append(ref)

        if hasattr(coach_plan_data, 'lahdeluettelo'):
             coach_plan_data.lahdeluettelo = formatted_list
             logger.info(f"[CoachAgent] Populated bibliography with {len(formatted_list)} references found in global state.")

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


        # 3. Populate 'lahdeluettelo' strictly from DB references
        # We use ReferenceManager locally to ensure the Agent's output complies with the schema requirement
        # "siinä saa käyttää vain db.json:issa olevia ennalta tallennettuja lähteitä"
        
        kb_struct = {"references": self.knowledge_base.get("references", []) if self.knowledge_base else []}
        rm = ReferenceManager(kb_struct)
        
        # Scan the entire CoachingPlan object for valid citations
        # We convert to dict if it's a Pydantic model to be safe, though scan handles objects? 
        # ReferenceManager expects dict/list/str. Pydantic .dict() or .model_dump() is best.
        scan_target = coach_plan_data.dict() if hasattr(coach_plan_data, 'dict') else coach_plan_data
        
        found_refs = rm.scan_and_collect_references(scan_target)
        
        # Overwrite the LLM's hallucinated list with the verified one
        if hasattr(coach_plan_data, 'lahdeluettelo'):
             coach_plan_data.lahdeluettelo = found_refs
        elif isinstance(coach_plan_data, dict):
             coach_plan_data['lahdeluettelo'] = found_refs

        return state
