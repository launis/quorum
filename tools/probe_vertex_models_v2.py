import asyncio
import os
import litellm
from dotenv import load_dotenv

load_dotenv()
os.environ["VERTEX_LOCATION"] = "us-central1"

CANDIDATES = [
    "vertex_ai/gemini-2.0-flash-exp", # Most likely for Dec 2024/Jan 2025
    "vertex_ai/gemini-2.0-pro-exp",
    "vertex_ai/gemini-2.0-flash",
    "vertex_ai/gemini-exp-1206", # Another known experimental id
    "vertex_ai/gemini-1.5-flash-002", # Updated 1.5
    "vertex_ai/gemini-1.5-pro-002",
]

async def probe_model(model_name):
    print(f"Probing {model_name} in us-central1...")
    try:
        response = await litellm.acompletion(
            model=model_name,
            messages=[{"role": "user", "content": "Hi"}],
            vertex_location="us-central1"
        )
        print(f"SUCCESS: {model_name} is available!")
        return model_name
    except Exception as e:
        error_str = str(e)
        if "404" in error_str or "NOT_FOUND" in error_str:
             print(f"FAIL: {model_name} not found.")
        else:
             print(f"ERROR (but maybe exists): {model_name} gave {e}")
        return None

async def main():
    found_flash = None
    found_pro = None
    
    for model in CANDIDATES:
        result = await probe_model(model)
        if result:
            if "flash" in result or "exp" in result: # Treat exp as fast/flash equivalent for now
                if not found_flash: found_flash = result
            if "pro" in result and not found_pro:
                found_pro = result
                
    print("\n--- RESULTS ---")
    print(f"Best Flash: {found_flash}")
    # Fallback: use flash for pro if pro not found
    print(f"Best Pro: {found_pro or found_flash}") 
    
    if found_flash:
        # Auto-update DB if found
        update_script = f"""
import json
from tinydb import TinyDB, Query
DB_PATH = "data/db.json"
db = TinyDB(DB_PATH)
table = db.table('system_config')
Query = Query()
entry = table.get(Query.id == 'model_registry')
entry['models']['google']['fast']['model_name'] = "{found_flash}"
entry['models']['google']['deep']['model_name'] = "{found_pro or found_flash}"
table.upsert(entry, Query.id == 'model_registry')
print("DB UPDATED AUTOMATICALLY")
"""
        with open("tools/auto_update_db.py", "w") as f:
            f.write(update_script)

if __name__ == "__main__":
    asyncio.run(main())
