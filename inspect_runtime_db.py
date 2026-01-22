import json

def check_db_content():
    path = 'c:/src/quorum/data/db.json'
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"--- Checking {path} ---")
        if 'system_config' in data:
            sc = data['system_config']
            if isinstance(sc, list):
                print(f"FAILURE: system_config is a LIST (Length: {len(sc)}) - This is the corruption.")
                print(f"Content preview: {sc[:1]}")
                print("system_config is a DICT (TinyDB Table).")
                found_registry = False
                for doc_id, doc_content in sc.items():
                    print(f"Doc {doc_id}: ID={doc_content.get('id')}, Type={doc_content.get('type')}")
                    if doc_content.get('id') == 'model_registry':
                        found_registry = True
                        models = doc_content.get('models', {})
                        if 'GuardAgent' in models:
                            print(f"SUCCESS: GuardAgent found in Doc {doc_id} with value: {models['GuardAgent']}")
                        else:
                             print(f"FAILURE: GuardAgent NOT found in model_registry. Available models: {list(models.keys())}")
                
                if not found_registry:
                    print(f"FAILURE: model_registry document NOT found in system_config. keys: {list(sc.keys())}")
            else:
                 print(f"FAILURE: system_config has unexpected type: {type(sc)}")
        else:
             print("FAILURE: system_config key MISSING from db.json")

             
    except Exception as e:
        print(f"Error reading db.json: {e}")

if __name__ == "__main__":
    check_db_content()
