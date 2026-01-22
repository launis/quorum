
import json
import os

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def check():
    db_path = r"c:\src\quorum\data\db.json"
    seed_path = r"c:\src\quorum\backend\seed\seed_data.json"
    
    if not os.path.exists(db_path):
        print("db.json not found")
        return
        
    db = load_json(db_path)
    seed = load_json(seed_path)
    
    db_sys = db.get("system_config", {})
    seed_sys = seed.get("system_config", {})
    
    print(f"DB keys: {list(db.keys())}")
    print(f"Seed keys: {list(seed.keys())}")
    
    print(f"DB system_config keys: {list(db_sys.keys())}")
    # seed_sys might be a list or dict. usage in seed_data usually implies list for components, but system_config in db.json suggests dict structure?
    # Let's check type.
    print(f"DB system_config type: {type(db_sys)}")
    print(f"Seed system_config type: {type(seed_sys)}")

    if isinstance(db_sys, dict) and isinstance(seed_sys, dict):
        missing = [k for k in db_sys if k not in seed_sys]
        print(f"Keys in DB but not in Seed: {missing}")
        
    # Check for model_registry specifically
    # In db.json it seemed to be under key "1" or similar if it was a dict from `view_file` snippet?
    # Wait, earlier `view_file` of db.json showed `{"workflows": ...}`.
    
    # Let's just dump the structure of system_config from db.json
    print("DB system_config structure:")
    print(json.dumps(db_sys, indent=2)[:500]) # First 500 chars

    # Check for Gemini 2.5
    s_db = json.dumps(db)
    if "gemini-2.5-pro" in s_db:
        print("gemini-2.5-pro FOUND in db.json")
    else:
        print("gemini-2.5-pro NOT FOUND in db.json")

    if "model_registry" in s_db:
        print("model_registry FOUND in db.json")
    
if __name__ == "__main__":
    check()
