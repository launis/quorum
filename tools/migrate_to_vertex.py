from tinydb import TinyDB, Query
import os

# Production DB path
DB_PATH = os.path.join("data", "db.json")

def update_registry_to_vertex():
    print(f"Updating DB at: {DB_PATH}")
    db = TinyDB(DB_PATH)
    table = db.table('system_config')
    Config = Query()
    
    # 1. Fetch existing
    res = table.search(Config.type == 'model_registry')
    registry = {}
    if res:
        registry = res[0].get('models', {})
        
    print("Current Registry:", registry)

    # 2. Update Google Provider to Vertex AI
    if 'google' not in registry:
        registry['google'] = {}
    
    
    # Set to Vertex AI models (Gemini 2.5 is supported in europe-north1 / Hamina)
    VERTEX_FLASH = "vertex_ai/gemini-2.5-flash"
    VERTEX_PRO = "vertex_ai/gemini-2.5-pro"
    
    # Fast Strategy: Gemini 2.5 Flash
    registry['google']['fast'] = {
        "model_name": VERTEX_FLASH,
        "temperature": 0.7,
        "max_tokens": 16384
    }
    
    # Deep Strategy: Gemini 2.5 Pro
    registry['google']['deep'] = {
        "model_name": VERTEX_PRO,
        "temperature": 0.5,
        "max_tokens": 16384
    }
    
    # 3. Save
    table.upsert({'type': 'model_registry', 'models': registry}, Config.type == 'model_registry')
    print("SUCCESS: Updated Model Registry to use 'vertex_ai/gemini-1.5-flash-002' and 'vertex_ai/gemini-1.5-pro-002'.")

if __name__ == "__main__":
    update_registry_to_vertex()
