from typing import Dict, Any, List
from googleapiclient.discovery import build
from src.components.hook_registry import HookRegistry
import config

def execute_google_search(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    HOOK: execute_google_search
    Logic: Suorittaa Google-haun käyttäen Custom Search JSON API:a.
    Tukee useita hakutermejä ja palauttaa jäsennellyn tuloksen.
    """
    print("[HOOK] Running Google Search (Official API)...")
    
    queries = []
    # 1. Claim Extraction (LLM Step)
    from src.engine.llm_handler import LLMHandler
    import json
    
    print("[HOOK] Extracting claims using LLM...")
    try:
        llm = LLMHandler()
        
        # Prepare context for claim extraction
        context_text = ""
        if 'data' in data and isinstance(data['data'], dict):
             context_text += f"LOPPUTUOTE:\n{data['data'].get('lopputuote', '')[:5000]}\n\n"
             context_text += f"REFLEKTIODOKUMENTTI:\n{data['data'].get('reflektiodokumentti', '')[:5000]}\n"
        
        if context_text:
            prompt = f"""
            ACT AS: Fact Extraction Agent.
            TASK: Identify top 3 factual claims from the text below that are most susceptible to being false or hallucinated (e.g. specific dates, historical events, scientific facts).
            OUTPUT: JSON array of strings.
            
            TEXT:
            {context_text}
            
            JSON OUTPUT:
            """
            
            claims_json = llm.call_llm([{"content": prompt}], model="gemini-1.5-flash")
            
            from src.components.hooks.parsing import _clean_and_parse_json
            parsed_claims = _clean_and_parse_json(claims_json)
            
            if isinstance(parsed_claims, list):
                queries.extend(parsed_claims[:3])
                print(f"[HOOK] Extracted claims: {queries}")
            elif isinstance(parsed_claims, dict) and 'claims' in parsed_claims:
                 queries.extend(parsed_claims['claims'][:3])
    except Exception as e:
        print(f"[HOOK] Claim extraction failed: {e}")

    # Fallback if no claims extracted
    if not queries:
        # Fallback to generic query extraction
        if 'hypothesis_argument' in data:
             queries.append(data['hypothesis_argument'][:100])
        elif 'prompt_text' in data:
             queries.append(data['prompt_text'][:100])
        else:
             queries.append("Cognitive Quorum fact check")

    all_results = []
    try:
        if not config.GOOGLE_SEARCH_API_KEY or not config.GOOGLE_SEARCH_CX:
            print("   [Error] Missing GOOGLE_SEARCH_API_KEY or GOOGLE_SEARCH_CX")
            return {"search_results": [], "error": "Missing API Keys"}

        service = build("customsearch", "v1", developerKey=config.GOOGLE_SEARCH_API_KEY)
        
        for query in queries[:3]: # Limit to 3 queries max
            print(f"   Query: {query}")
            res = service.cse().list(q=query, cx=config.GOOGLE_SEARCH_CX, num=3).execute()
            
            for item in res.get('items', []):
                all_results.append({
                    "query": query,
                    "title": item.get('title'),
                    "url": item.get('link'),
                    "snippet": item.get('snippet')
                })
            
    except Exception as e:
        print(f"   Search failed: {e}")
        all_results.append({"error": str(e)})

    return {
        "search_results": all_results,
        "fact_check_summary": f"Found {len(all_results)} external sources via Google API."
    }

HookRegistry.register("execute_google_search", execute_google_search)
