import json
import os

def check_file(path, label):
    print(f"--- Checking {label} ({path}) ---")
    if not os.path.exists(path):
        print("File not found")
        return

    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Failed to load JSON: {e}")
        return

    # Check System Config (Model Registry)
    sys_conf = data.get('system_config')
    model_registry = None
    if isinstance(sys_conf, dict):
        # Look for model_registry in dict values
        for k, v in sys_conf.items():
            if v.get('id') == 'model_registry':
                model_registry = v
                break
    elif isinstance(sys_conf, list):
        for item in sys_conf:
            if item.get('id') == 'model_registry':
                model_registry = item
                break
    
    if model_registry:
        print(f"Model Registry Found.")
        models = model_registry.get('models', {}).get('google', {})
        print(f"Google Models: {list(models.keys())}")
        # Check specific model names
        for role in ['deep', 'fast', 'strict']:
            m = models.get(role, {})
            print(f"  {role}: {m.get('model_name')}")
    else:
        print("Model Registry NOT FOUND in system_config")

    # Check Knowledge Base
    components = data.get('components')
    kb = None
    if isinstance(components, dict):
        for k, v in components.items():
            if v.get('id') == 'knowledge_base':
                kb = v
                break
    elif isinstance(components, list):
        for item in components:
            if item.get('id') == 'knowledge_base':
                kb = item
                break
    
    # Fallback to root level check (some dumps structure it differently)
    if not kb and isinstance(data, dict):
         # Try finding by ID in root keys (unlikely but possible if flattened)
         pass

    if kb:
        print(f"Knowledge Base Found: {kb.get('name')}")
        concepts = kb.get('concepts', {})
        print(f"Concept Count: {len(concepts)}")
    else:
        print("Knowledge Base NOT FOUND in components")

def main():
    check_file('c:/src/quorum/data/db.json', 'DB')
    print("\n")
    check_file('c:/src/quorum/backend/seed/seed_data.json', 'SEED')

if __name__ == "__main__":
    main()
