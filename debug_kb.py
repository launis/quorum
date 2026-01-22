
import json

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def compare_kb():
    db_path = r"c:\src\quorum\data\db.json"
    seed_path = r"c:\src\quorum\backend\seed\seed_data.json"
    
    db = load_json(db_path)
    seed = load_json(seed_path)
    
    # Extract KB from db (assuming it's in system_config or similar? Need to find where it lives in db.json)
    # in seed_data it's in "components" list with type "knowledge_base" OR "system_config" list?
    # In step 183 view of db.json, it seemed flat?
    # Actually step 183 showed `{"workflows": ...}` and cut off.
    # Let's search for type="knowledge_base" in both.
    
    def get_kb(data, source_name):
        kbs = []
        # Check system_config list
        if "system_config" in data:
            if isinstance(data["system_config"], list):
                 kbs.extend([x for x in data["system_config"] if x.get("id") == "knowledge_base"])
            elif isinstance(data["system_config"], dict):
                 # db.json structure might be different
                 if data["system_config"].get("id") == "knowledge_base":
                     kbs.append(data["system_config"])
                 # Or maybe it's a dict of components?
                 
        # Check components list
        if "components" in data and isinstance(data["components"], list):
            kbs.extend([x for x in data["components"] if x.get("type") == "knowledge_base"])
            
        print(f"Found {len(kbs)} KB items in {source_name}")
        return kbs

    db_kbs = get_kb(db, "DB")
    seed_kbs = get_kb(seed, "SEED")
    
    if db_kbs and seed_kbs:
        db_content = db_kbs[0].get("concepts", {})
        seed_content = seed_kbs[0].get("content", []) 
        # Note: seed structure seen in step 137 lines 1153 implies "content" is a LIST of citations?
        # But step 183 db.json shows `knowledge_base` references `concepts`? 
        # Wait, step 183 was db.json but only showed workflows.
        # Step 223 user snippet shows seed_data system_config model_registry.
        
        # Let's verify the keys in the first KB found.
        print("DB KB keys:", db_kbs[0].keys())
        print("Seed KB keys:", seed_kbs[0].keys())
        
        # If DB has 'concepts' and Seed has 'content' (list), they are structured differently?
        # Or I am misinterpreting the previous view output.
        
if __name__ == "__main__":
    compare_kb()
