import json
from tinydb import TinyDB, Query

# Define paths
DB_PATH = "data/db.json"

# Define safe, globally available models
FAST_MODEL = "vertex_ai/gemini-1.5-flash"
DEEP_MODEL = "vertex_ai/gemini-1.5-pro"

def update_db():
    print(f"Opening database at {DB_PATH}...")
    db = TinyDB(DB_PATH)
    table = db.table('system_config')
    
    # 1. Update Model Registry
    print("Updating Model Registry...")
    registry_query = Query()
    registry_entry = table.get(registry_query.id == 'model_registry')
    
    if registry_entry:
        print(f"Found existing registry. Current config: {registry_entry['models']['google']}")
        
        # Update values
        registry_entry['models']['google']['fast']['model_name'] = FAST_MODEL
        registry_entry['models']['google']['deep']['model_name'] = DEEP_MODEL
        
        # Write back
        table.upsert(registry_entry, registry_query.id == 'model_registry')
        print(f"SUCCESS: Updated registry to use {FAST_MODEL} and {DEEP_MODEL}")
    else:
        print("ERROR: Could not find 'model_registry' in system_config table!")

    # 2. Verify Update
    updated_entry = table.get(registry_query.id == 'model_registry')
    print(f"VERIFICATION: New config in DB: {updated_entry['models']['google']}")

if __name__ == "__main__":
    update_db()
