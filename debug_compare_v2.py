import json
import sys

def load_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return None

def main():
    db = load_json('c:/src/quorum/data/db.json')
    seed = load_json('c:/src/quorum/backend/seed/seed_data.json')

    if not db or not seed:
        return

    print("--- SYSTEM CONFIG (Model Registry) ---")
    
    # Check DB system_config
    if 'system_config' in db:
        config = db['system_config']
        print(f"DB system_config type: {type(config)}")
        if isinstance(config, dict):
            if '1' in config:
                 print("DB model_registry models (Gemini?):", json.dumps(config['1'].get('models', {}).get('google', {}), indent=2))
        elif isinstance(config, list):
            print("DB system_config is a list. First item:", config[0] if config else "Empty")
            # Try to find model registry in list
            for item in config:
                if item.get('id') == 'model_registry':
                    print("Found model_registry in DB list")
                    print(json.dumps(item.get('models', {}).get('google', {}), indent=2))
    else:
        print("DB missing system_config")

    # Check Seed system_config
    if 'system_config' in seed:
        config = seed['system_config']
        print(f"Seed system_config type: {type(config)}")
        if isinstance(config, dict):
            if '1' in config:
                print("Seed model_registry models (Gemini?):", json.dumps(config['1'].get('models', {}).get('google', {}), indent=2))
        elif isinstance(config, list):
            # Try to find model registry in list
            for item in config:
                if item.get('id') == 'model_registry':
                    print("Found model_registry in Seed list")
                    print(json.dumps(item.get('models', {}).get('google', {}), indent=2))
    else:
        print("Seed missing system_config")


    print("\n--- COMPONENTS (Knowledge Base) ---")
    
    kb_db = None
    # Check DB components
    if 'components' in db:
        comps = db['components']
        if isinstance(comps, dict):
             if '2' in comps: kb_db = comps['2']
        elif isinstance(comps, list):
             for c in comps:
                 if c.get('id') == 'knowledge_base': kb_db = c
    
    # Fallback checking root for "2"
    if not kb_db and '2' in db:
        kb_db = db['2']

    if kb_db:
        print(f"DB Knowledge Base Found: {kb_db.get('name')}")
        concepts = kb_db.get('concepts', {})
        print(f"DB Concepts Count: {len(concepts)}")
        if concepts:
             print(f"DB First Concept: {list(concepts.keys())[0]}")
    else:
        print("DB Knowledge Base NOT FOUND")

    kb_seed = None
    if 'components' in seed:
        comps = seed['components']
        if isinstance(comps, dict):
            if '2' in comps: kb_seed = comps['2']
        elif isinstance(comps, list):
            for c in comps:
                if c.get('id') == 'knowledge_base': kb_seed = c

    if kb_seed:
        print(f"Seed Knowledge Base Found: {kb_seed.get('name')}")
        concepts = kb_seed.get('concepts', {})
        print(f"Seed Concepts Count: {len(concepts)}")
        if concepts:
             print(f"Seed First Concept: {list(concepts.keys())[0]}")
    else:
        print("Seed Knowledge Base NOT FOUND")

if __name__ == "__main__":
    main()
