from typing import Any, Optional, Type
import os
import json
from googleapiclient.discovery import build
from backend.agents.base import BaseAgent
from backend.models.state import WorkflowState
from backend.models.domain import (
    LogiikkaAuditointi, 
    EtiikkaJaFakta, 
    KausaalinenAuditointi, 
    PerformatiivisuusAuditointi
)
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class LogicalFalsifierAgent(BaseAgent):
    """
    Looginen Falsifioija-agentti (Logical Falsifier).
    """
    state_field = "step_falsifier"
    
    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        return LogiikkaAuditointi


class FactualOverseerAgent(BaseAgent):
    """
    Faktuaalinen ja Eettinen Valvoja-agentti (Factual & Ethical Overseer).
    """
    state_field = "step_overseer"

    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        return EtiikkaJaFakta

    def execute_google_search(self, state: WorkflowState) -> WorkflowState:
        """
        HOOK: execute_google_search
        Executes Google Search based on hypotheses.
        """
        logger.info("[FactualOverseerAgent] Running execute_google_search...")
        
        api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
        cx = os.getenv("GOOGLE_SEARCH_CX")
        
        if not api_key or not cx:
            logger.warning("[Warning] Missing GOOGLE_SEARCH_API_KEY or GOOGLE_SEARCH_CX")
            state.aux_data['google_search_results'] = "Search disabled (Missing API Keys)"
            return state

        queries = []
        
        # Extract queries from Hypotheses (Step 2 Analyst)
        if state.step_analyst and state.step_analyst.hypoteesit:
            logger.info(f"   [HOOK] Found {len(state.step_analyst.hypoteesit)} hypotheses.")
            for hyp in state.step_analyst.hypoteesit:
                # ONLY use explicit search suggestions (external facts)
                if hyp.hakusana_ehdotus and len(hyp.hakusana_ehdotus.strip()) > 3:
                    queries.append(hyp.hakusana_ehdotus)
        else:
             logger.info("   [HOOK] No hypotheses found. Using fallback.")
             queries.append("Cognitive Quorum verification")

        all_results = []
        try:
            service = build("customsearch", "v1", developerKey=api_key)
            
            # Limit to top 3 queries
            for i, query in enumerate(queries[:3]): 
                logger.info(f"   Query {i+1}: {query}")
                try:
                    res = service.cse().list(q=query, cx=cx, num=3).execute()
                    
                    for item in res.get('items', []):
                        all_results.append({
                            "query": query,
                            "title": item.get('title'),
                            "link": item.get('link'),
                            "snippet": item.get('snippet')
                        })
                except Exception as q_err:
                    logger.warning(f"   Query '{query}' failed: {q_err}")
                    
            state.aux_data['google_search_results'] = json.dumps(all_results, indent=2)
            
        except Exception as e:
            logger.error(f"   Search failed: {e}")
            state.aux_data['google_search_results'] = f"Search failed: {str(e)}"

        return state


class CausalAnalystAgent(BaseAgent):
    """
    Kausaalinen Analyytikko-agentti (Causal Analyst).
    """
    state_field = "step_causal"

    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        return KausaalinenAuditointi


class PerformativityDetectorAgent(BaseAgent):
    """
    Performatiivisuuden Tunnistaja-agentti (Performativity Detector).
    """
    state_field = "step_detector"

    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        return PerformatiivisuusAuditointi

    def detect_performative_patterns(self, state: WorkflowState) -> WorkflowState:
        """
        HOOK: detect_performative_patterns
        Scans input for performative language patterns.
        """
        logger.info("[PerformativityDetectorAgent] Running detect_performative_patterns...")
        
        suspect_patterns = [
            "delve into", "tapestry", "comprehensive overview", "rich history",
            "testament to", "underscore the importance", "pivotal role",
            "landscape of", "realm of", "foster a sense of"
        ]
        
        detected = []
        text_to_scan = (state.inputs.history_text or "") + (state.inputs.product_text or "")
        text_lower = text_to_scan.lower()
        
        for pattern in suspect_patterns:
            if pattern in text_lower:
                detected.append(pattern)
                
        if detected:
            logger.info(f"   [HOOK] Detected patterns: {detected}")
            state.aux_data['performative_patterns_detected'] = json.dumps(detected)
        else:
            state.aux_data['performative_patterns_detected'] = "[]"
            
        return state
