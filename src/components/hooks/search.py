from typing import Dict, Any, List
from googleapiclient.discovery import build
from src.components.hook_registry import HookRegistry
import config

def execute_google_search(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    HOOK: execute_google_search
    Logic: Suorittaa Google-haun käyttäen Custom Search JSON API:a.
    """
    print("[HOOK] Running Google Search (Official API)...")
    
    query = "Cognitive Quorum fact check"
    if 'hypothesis_argument' in data:
        query = data['hypothesis_argument'][:100] # Limit query length
    elif 'prompt_text' in data:
        query = data['prompt_text'][:100]

    print(f"   Query: {query}")

    results = []
    try:
        if not config.GOOGLE_SEARCH_API_KEY or not config.GOOGLE_SEARCH_CX:
            print("   [Error] Missing GOOGLE_SEARCH_API_KEY or GOOGLE_SEARCH_CX")
            return {"search_results": [], "error": "Missing API Keys"}

        service = build("customsearch", "v1", developerKey=config.GOOGLE_SEARCH_API_KEY)
        res = service.cse().list(q=query, cx=config.GOOGLE_SEARCH_CX, num=3).execute()
        
        for item in res.get('items', []):
            results.append({
                "title": item.get('title'),
                "url": item.get('link'),
                "snippet": item.get('snippet')
            })
            
    except Exception as e:
        print(f"   Search failed: {e}")
        results.append({"error": str(e)})

    return {
        "search_results": results,
        "fact_check_summary": f"Found {len(results)} external sources via Google API."
    }

HookRegistry.register("execute_google_search", execute_google_search)
