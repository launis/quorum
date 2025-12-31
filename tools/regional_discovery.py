import asyncio
import os
import litellm
import logging
from dotenv import load_dotenv

# Suppress litellm logging for clean output
logging.getLogger("litellm").setLevel(logging.CRITICAL)

load_dotenv()

# EXTENSIVE LIST OF CANDIDATES TO PROBE IN US
# This acts as our "Discovery List"
CANDIDATES = [
    # Gemini 3.0 (Hypothetical/Preview)
    "vertex_ai/gemini-3.0-pro-preview",
    "vertex_ai/gemini-3.0-flash-preview",
    "vertex_ai/gemini-3.0-pro",
    "vertex_ai/gemini-3.0-flash",
    
    # Gemini 2.5 (Latest Stable per Docs)
    "vertex_ai/gemini-2.5-pro",
    "vertex_ai/gemini-2.5-flash",
    "vertex_ai/gemini-2.5-pro-001",
    "vertex_ai/gemini-2.5-flash-001",
    "vertex_ai/gemini-2.5-flash-lite",
    
    # Gemini 2.0 (Experimental)
    "vertex_ai/gemini-2.0-flash-exp",
    "vertex_ai/gemini-2.0-pro-exp",
    "vertex_ai/gemini-2.0-flash",
    "vertex_ai/gemini-2.0-flash-001",
    "vertex_ai/gemini-exp-1206",
    
    # Gemini 1.5 (Legacy/Retiring)
    "vertex_ai/gemini-1.5-pro",
    "vertex_ai/gemini-1.5-flash",
    "vertex_ai/gemini-1.5-pro-001",
    "vertex_ai/gemini-1.5-flash-001",
    "vertex_ai/gemini-1.5-pro-002",
    "vertex_ai/gemini-1.5-flash-002",
]

async def check_connectivity(model, location):
    try:
        # Quick ping with minimal tokens
        await litellm.acompletion(
            model=model,
            messages=[{"role": "user", "content": "hi"}],
            vertex_location=location,
            max_tokens=1
        )
        return True
    except Exception as e:
        # Strict failure: Any error (404, 403, 400) counts as "not usable"
        return False 

async def main():
    print("--- PHASE 1: DISCOVERING MODELS IN US-CENTRAL1 ---")
    print("Querying US region to validate potential model names...")
    
    us_models = []
    
    # Run probes concurrently to save time
    tasks = []
    for model in CANDIDATES:
        tasks.append(check_connectivity(model, "us-central1"))
    
    results = await asyncio.gather(*tasks)
    
    for model, success in zip(CANDIDATES, results):
        status = "FOUND" if success else "."
        print(f"  Probing US: {model.ljust(40)} -> {status}")
        if success:
            us_models.append(model)
            
    if not us_models:
        print("\nCRITICAL: No models found in US! Check network/auth/quota.")
        return

    print(f"\n--- PHASE 2: TESTING DISCOVERED MODELS ({len(us_models)}) IN EUROPE-NORTH1 (HAMINA) ---")
    print("Verifying which of the valid US models are deployed to Hamina...")
    
    hamina_models = []
    hamina_tasks = []
    for model in us_models:
        hamina_tasks.append(check_connectivity(model, "europe-north1"))
        
    hamina_results = await asyncio.gather(*hamina_tasks)
    
    for model, success in zip(us_models, hamina_results):
        status = "OK (HAMINA)" if success else "FAIL"
        print(f"  Testing Hamina: {model.ljust(40)} -> {status}")
        if success:
            hamina_models.append(model)
            
    print("\n--- REGIONAL DISCOVERY REPORT ---")
    print(f"Models confirmed available in Hamina: {len(hamina_models)}")
    
    if not hamina_models:
        print("ERROR: Models exist in US but NONE are available in Hamina yet.")
        return
    
    # Priority Scoring to pick best
    def get_score(name):
        score = 0
        if "3.0" in name: score += 400
        if "2.5" in name: score += 300
        if "2.0" in name: score += 200
        if "1.5" in name: score += 100
        
        # Penalties/Bonuses
        if "preview" in name or "exp" in name: score -= 5 # Prefer stable if version match
        if "002" in name: score += 2 # Prefer newer patch
        if "001" in name: score += 1
        return score
        
    sorted_models = sorted(hamina_models, key=get_score, reverse=True)
    
    best_fast = None
    best_deep = None
    
    for m in sorted_models:
        if "flash" in m or "lite" in m:
            if not best_fast: best_fast = m
        if "pro" in m or "ultra" in m:
            if not best_deep: best_deep = m
            
    # Fallback logic
    if not best_deep and best_fast: best_deep = best_fast
    if not best_fast and best_deep: best_fast = best_deep
        
    print(f"\nSELECTED BEST CONFIG FOR HAMINA:")
    print(f"  FAST: {best_fast}")
    print(f"  DEEP: {best_deep}")
    
    if best_fast and best_deep:
        import json
        from tinydb import TinyDB, Query
        db = TinyDB("data/db.json")
        tbl = db.table('system_config')
        q = Query()
        entry = tbl.get(q.id == 'model_registry')
        
        if entry:
            entry['models']['google']['fast']['model_name'] = best_fast
            entry['models']['google']['deep']['model_name'] = best_deep
            tbl.upsert(entry, q.id == 'model_registry')
            print("DATABASE UPDATED SUCCESSFULLY.")
        else:
            print("ERROR: model_registry not found in DB.")
        
if __name__ == "__main__":
    asyncio.run(main())
