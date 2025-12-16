from typing import Any, Optional, Type, List, Dict
from backend.agents.base import BaseAgent
from backend.models.state import WorkflowState
from pydantic import BaseModel, Field
import logging
import os
import json

logger = logging.getLogger(__name__)

from backend.models.domain import CoachingPlan, ActionItem

class CoachAgent(BaseAgent):
    """
    Coach Agent (Valmentaja).
    Transformative feedback based on Judge's verdict.
    """
    state_field = "step_coach"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.knowledge_base = self._load_knowledge_base()

    async def execute(self, state: WorkflowState, system_instruction: Optional[str] = None, **kwargs) -> WorkflowState:
        """
        Override execute to inject dynamic context (Knowledge Base).
        """
        
        logger.info("[CoachAgent] EXECUTE started. Loading references...")
        from starlette.concurrency import run_in_threadpool
        
        repository = kwargs.get('repository')
        
        # 1. Load DB Items (BLOCKING I/O -> Threadpool)
        # Fetch ONCE for both Refs and Concepts
        def _fetch_db_items():
            if repository and hasattr(repository, 'get_knowledge_base_items'):
                 try:
                     logger.debug("[CoachAgent] Fetching KB items from TinyDB...")
                     return repository.get_knowledge_base_items()
                 except Exception as e: 
                     logger.error(f"[CoachAgent] KB Fetch Error: {e}")
                     pass
            return []

        all_items = await run_in_threadpool(_fetch_db_items)
        
        db_refs = [i['definition'] for i in all_items if i.get('type') == 'reference']
        db_short_citations = [i.get('short_citation') for i in all_items if i.get('type') == 'reference' and i.get('short_citation')]
        db_concepts = [i for i in all_items if i.get('type') == 'concept']

        state.aux_data['db_references'] = db_refs
        logger.info(f"[CoachAgent] Loaded {len(db_refs)} references ({len(db_short_citations)} short keys) and {len(db_concepts)} concepts from DB.")
        
        # 2. Fetch External Context (ASYNC/THREADED)
        external_context = ""
        if state.inputs.bibliography_context:
            try:
                external_context = await run_in_threadpool(self._fetch_external_context_sync, state.inputs.bibliography_context)
            except Exception as e:
                logger.error(f"[CoachAgent] Async fetch failed: {e}")

        # 3. Build Prompt (passing pre-fetched data)
        # We pass db_concepts explicitly to avoid re-fetching in _build_prompt
        logger.info("[CoachAgent] Constructing dynamic prompt...")
        dynamic_context = self._build_prompt(state, repository, external_context_override=external_context, preloaded_concepts=db_concepts, preloaded_citations=db_short_citations)
        
        # Append to system_instruction
        if system_instruction:
            full_instruction = f"{system_instruction}\n\n{dynamic_context}"
        else:
            full_instruction = dynamic_context
            
        logger.info("[CoachAgent] Ready to call LLM.")
        return await super().execute(state, system_instruction=full_instruction, **kwargs)

    def _load_knowledge_base(self) -> Dict[str, Any]:
        """Loads the extended knowledge base from JSON."""
        path = os.path.join("data", "coach_resources.json")
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f"[CoachAgent] Loaded knowledge base from {path}")
                    return data
            except Exception as e:
                logger.error(f"[CoachAgent] Failed to load knowledge base: {e}")
        return {}

    def _build_prompt(self, state: WorkflowState, repository: Any = None, external_context_override: str = "", preloaded_concepts: List[Dict] = [], **kwargs) -> str:
        """
        Overrides BaseAgent._build_prompt.
        CRITICAL: Do NOT perform blocking DB calls here if possible. Use preloaded_concepts.
        """
        logger.debug("[CoachAgent._build_prompt] Entry.")
        
        
        # 1. Get base prompt
        # BaseAgent does NOT have _build_prompt anymore, so we don't call super()
        # base_prompt = super()._build_prompt(state) 
        base_prompt = "" # We rely on System Instruction from Engine or dynamic context.
        # But wait, we want the "User Prompt" portion? 
        # Actually CoachAgent operates by appending context to System Instruction. 
        # The user message is just "Proceed...".
        # So we return just the Context String.
        
        context_str = ""
        
        # 1.5. DB-Based Knowledge Base (Preferred)
        db_concepts = preloaded_concepts
        
        # FALLBACK LOGIC REMOVED TO PREVENT BLOCKING
        # If preloaded_concepts is empty, we SKIP the DB context rather than risking a hang.
        if not db_concepts and repository:
             logger.warning("[CoachAgent] _build_prompt called without preloaded concepts. Skipping DB context to avoid blocking.")

        # 2. Enrich with Knowledge Base (Internal)
        context_str += "\n\n### REFERENCE MATERIAL (from 'Holistinen Mestaruus')\n"
        context_str += "Use these definitions to explain *why* specific feedback is given:\n\n"
        
        concepts_source = {}
        if self.knowledge_base and "concepts" in self.knowledge_base:
            concepts_source = self.knowledge_base["concepts"]
            
        for item in db_concepts:
            concepts_source[item['term']] = item['definition']
            
        if concepts_source:
             for concept, definition in concepts_source.items():
                def_short = definition[:800] + "..." if len(definition) > 800 else definition
                context_str += f"#### {concept}\n{def_short}\n\n"
        
        # 2.5. Valid Short Citations (Strict List)
        valid_citations = kwargs.get('preloaded_citations', [])
        if valid_citations:
            context_str += "\n\n### VALID CITATION KEYS (STRICT)\n"
            context_str += "You MUST use ONLY the following keys for in-text citations (e.g. `(vrt. Author Year)`):\n"
            context_str += "[" + ", ".join(valid_citations) + "]\n"
        
        # 3. Enrich with External Bibliography (External Sources)
        if external_context_override:
             context_str += "\n\n### EXTERNAL SOURCES (Bibliography Context)\n"
             context_str += "Reflect on these sources if relevant:\n\n"
             context_str += external_context_override
             
        # Explicit Instruction for Citation
        context_str += "\n\nIMPORTANT: When creating 'kehityskohteet_konkreettisesti' (Action Items), you MUST include relevant citations."
        context_str += "\n- Look at the 'EXTERNAL SOURCES' and 'REFERENCE MATERIAL' above."
        context_str += "\n- If an Action Item relates to a concept (e.g. Reflection, Logic), find a matching Source/Reference."
        context_str += "\n- Add the citation string to the 'resurssit' list of that Action Item."
        context_str += "\n- DO NOT invent references. Use only the provided strings in 'VALID CITATION KEYS' or 'REFERENCE MATERIAL'."
        context_str += "\n- In the text content (kuvaus/palaute), use the short format: `(vrt. Author Year)`."

        return context_str + base_prompt

    def _fetch_external_context_sync(self, bibliography_context: List[str]) -> str:
        """
        Blocking fetcher (to be run in threadpool).
        """
        if not bibliography_context:
            return ""
            
        from backend.services.web_fetcher import WebFetcher
        
        context_parts = []
        for item in bibliography_context:
            if item.startswith("http"):
                # Fetch URL
                text = WebFetcher.fetch_text(item)
                if text:
                    context_parts.append(f"SOURCE [{item}]:\n{text}\n")
                else:
                    context_parts.append(f"SOURCE [{item}]: (Failed to fetch content)\n")
            else:
                # Plain Text citation
                context_parts.append(f"CITATION: {item}\n")
                
        return "\n".join(context_parts)

    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        return CoachingPlan

    def enrich_learning_plan(self, state: WorkflowState) -> WorkflowState:
        """
        POST-HOOK: Scans the generated ActionItems. 
        Searches the JSON Knowledge Base bibliography for relevant citations and appends them.
        """
        logger.info("[CoachAgent] Running enrich_learning_plan hook...")
        
        # 1. Get the output from state using the state_field
        coach_plan_data = getattr(state, self.state_field, None)
        if not coach_plan_data:
            return state
            
        # Ensure it's a model instance or dict, Pydantic should handle it?
        # In V2 state, it's usually the Pydantic object if validated.
        
        # Check if we need to access items. 
        # Note: 'coach_plan_data' might be a Dict if deserialized from JSON without model validation in some paths,
        # OR it is the CoachingPlan object. 
        # BaseAgent.execute usually sets the Pydantic model.
        
        # To be safe, if it's an object, get attribute; if dict, get key.
        def get_attr(obj, attr):
            return getattr(obj, attr) if hasattr(obj, attr) else obj.get(attr)

        items = get_attr(coach_plan_data, 'kehityskohteet_konkreettisesti')
        if not items:
            return state

        updated_count = 0
        for item in items:
            # item is ActionItem object or dict
            otsikko = get_attr(item, 'otsikko') or ""
            kuvaus = get_attr(item, 'kuvaus') or ""
            desc = (kuvaus + " " + otsikko).lower()
            
            current_resources = get_attr(item, 'resurssit')
            if current_resources is None:
                current_resources = []
            
            # Search bibliography based on specific keywords found in the item
            # 1. Internal Knowledge Base
            if self.knowledge_base and "concepts" in self.knowledge_base:
                for concept in self.knowledge_base["concepts"]:
                    if concept.lower() in desc and concept != "Bibliography":
                        if self.knowledge_base.get("references") and "bibliography" in self.knowledge_base["references"]:
                            for ref in self.knowledge_base["references"]["bibliography"]:
                                # Simple match
                                if concept.lower() in ref.lower() or (concept == "Hybrid Rubric" and "hybridirubriikki" in ref.lower()):
                                    if not any(ref[:20] in r for r in current_resources):
                                        current_resources.append(f"📚 {ref}")
                                        logger.info(f"   [Coach] Enriched item '{otsikko}' with biblio ref.")
                                        updated_count += 1
            
            # 2. External Bibliography Context
            if state.inputs.bibliography_context:
                for bib_item in state.inputs.bibliography_context:
                    # Very naive match: if bib item title or significant keyword appears in description
                    # For now, we list it if it's explicitly mentioned or blindly append if short list?
                    # Let's check overlap of words.
                    bib_lower = bib_item.lower()
                    # Only append if not already there
                    if bib_lower not in [r.lower() for r in current_resources]:
                         # Only if significant word match? 
                         # Let's assume if the bib item is provided, the user WANTS it used.
                         # But sticking it to EVERY item is noisy.
                         # Let's append it if any 5-char word matches (heuristic)
                         bib_words = set(w for w in bib_lower.split() if len(w) > 5)
                         desc_words = set(w for w in desc.split() if len(w) > 5)
                         if bib_words & desc_words:
                             current_resources.append(f"🔗 {bib_item}")
                             updated_count += 1

            
            # Update item
            if hasattr(item, 'resurssit'):
                item.resurssit = current_resources
            else:
                item['resurssit'] = current_resources
        
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

        # Gather all text content
        all_text = ""
        for item in items:
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
