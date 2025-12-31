import json
from tinydb import TinyDB, Query

DB_PATH = "data/db.json"

# Based on Google Cloud Doc: Latest stable models are Gemini 2.5
FAST_MODEL = "vertex_ai/gemini-2.5-flash"
DEEP_MODEL = "vertex_ai/gemini-2.5-pro"

def update_db():
    print(f"Opening database at {DB_PATH}...")
    db = TinyDB(DB_PATH)
    table = db.table('system_config')
    
    QueryObj = Query()
    registry_entry = table.get(QueryObj.id == 'model_registry')
    
    if registry_entry:
        print(f"Current config: {registry_entry['models']['google']}")
        
        # Update to Gemini 2.5
        registry_entry['models']['google']['fast']['model_name'] = FAST_MODEL
        registry_entry['models']['google']['deep']['model_name'] = DEEP_MODEL
        
        table.upsert(registry_entry, QueryObj.id == 'model_registry')
        print(f"SUCCESS: Updated to {FAST_MODEL} and {DEEP_MODEL}")
    else:
        print("ERROR: Registry not found")

if __name__ == "__main__":
    update_db()
