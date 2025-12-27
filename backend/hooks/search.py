
import os
import logging
import json
from googleapiclient.discovery import build
from typing import List, Dict, Any
from backend.models.state import WorkflowState

logger = logging.getLogger(__name__)

def execute_google_search(state: WorkflowState) -> WorkflowState:
    """
    HOOK: execute_google_search
    Executes Google Search based on hypotheses.
    Moves logic from FactualOverseerAgent to a dedicated hook.
    """
    logger.info("[SearchHook] Running execute_google_search...")
    
    api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    cx = os.getenv("GOOGLE_SEARCH_CX")
    
    if not api_key or not cx:
        logger.warning("[SearchHook] Missing GOOGLE_SEARCH_API_KEY or GOOGLE_SEARCH_CX")
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
        logger.error(f"   [SearchHook] Search failed: {e}")
        state.aux_data['google_search_results'] = f"Search failed: {str(e)}"

    return state
