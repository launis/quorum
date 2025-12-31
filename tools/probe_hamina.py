import asyncio
import os
import litellm
from dotenv import load_dotenv

# Load env but force Hamina location for probing
load_dotenv()
os.environ["VERTEX_LOCATION"] = "europe-north1" 

CANDIDATES = [
    "vertex_ai/gemini-2.5-flash",
    "vertex_ai/gemini-2.5-pro",
    "vertex_ai/gemini-2.0-flash-exp", # Might not be in EU yet
    "vertex_ai/gemini-2.0-flash-001",
    "vertex_ai/gemini-1.5-pro-002",
    "vertex_ai/gemini-1.5-flash-002",
    "vertex_ai/gemini-1.5-pro",
    "vertex_ai/gemini-1.5-flash",
]

async def probe_model(model_name):
    print(f"Probing {model_name} in europe-north1...")
    try:
        response = await litellm.acompletion(
            model=model_name,
            messages=[{"role": "user", "content": "Hi"}],
            vertex_location="europe-north1"
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
            if "flash" in result:
                if not found_flash: found_flash = result
            if "pro" in result and not found_pro:
                found_pro = result
                
    print("\n--- RESULTS ---")
    print(f"Best Flash: {found_flash}")
    print(f"Best Pro: {found_pro or found_flash}") 
    
    if found_flash:
        # Create auto-update script to run next
        code = f"""
import json
from tinydb import TinyDB, Query
DB_PATH = "data/db.json"
db = TinyDB(DB_PATH)
table = db.table('system_config')
QueryObj = Query()
entry = table.get(QueryObj.id == 'model_registry')
entry['models']['google']['fast']['model_name'] = "{found_flash}"
entry['models']['google']['deep']['model_name'] = "{found_pro or found_flash}"
table.upsert(entry, QueryObj.id == 'model_registry')
print("HAMINA CONFIG UPDATED: {found_flash} / {found_pro or found_flash}")
"""
        with open("tools/update_hamina_db.py", "w") as f:
            f.write(code)

if __name__ == "__main__":
    asyncio.run(main())
