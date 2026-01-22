import json
import os

OUTPUT_FILE = 'c:/src/quorum/verification_result.txt'

def check_file(path, label, out_f):
    out_f.write(f"\n--- Checking {label} ({path}) ---\n")
    if not os.path.exists(path):
        out_f.write("File not found\n")
        return

    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        out_f.write(f"Failed to load JSON: {e}\n")
        return

    # Check System Config
    sys_conf = data.get('system_config')
    model_registry = None
    if isinstance(sys_conf, dict):
        for k, v in sys_conf.items():
            if v.get('id') == 'model_registry':
                model_registry = v
                break
    elif isinstance(sys_conf, list):
        for item in sys_conf:
            if item.get('id') == 'model_registry':
                model_registry = item
                break
    
    # Fallback: Check if dict keys ARE the registry items (e.g. key "1")
    if not model_registry and isinstance(sys_conf, dict):
        if '1' in sys_conf and sys_conf['1'].get('id') == 'model_registry':
             model_registry = sys_conf['1']

    if model_registry:
        out_f.write(f"Model Registry Found.\n")
        models = model_registry.get('models', {}).get('google', {})
        out_f.write(f"Google Models: {list(models.keys())}\n")
        for role in ['deep', 'fast', 'strict']:
            m = models.get(role, {})
            out_f.write(f"  {role}: {m.get('model_name')}\n")
    else:
        out_f.write("Model Registry NOT FOUND in system_config\n")
        # debug: print keys
        if sys_conf:
             out_f.write(f"system_config keys/type: {type(sys_conf)}\n")

    # Check Knowledge Base
    components = data.get('components')
    kb = None
    if isinstance(components, dict):
        for k, v in components.items():
            if v.get('id') == 'knowledge_base' or getattr(v, 'get', lambda x: None)('type') == 'knowledge_base':
                kb = v
                break
    elif isinstance(components, list):
        for item in components:
            if item.get('id') == 'knowledge_base' or item.get('type') == 'knowledge_base':
                kb = item
                break
    
    if kb:
        out_f.write(f"Knowledge Base Found.\n")
        # count references
        refs = kb.get('references', [])
        # seed_data might use 'content' list instead of 'references' key?
        # Check structure from snippet
        # snippet: "references": [...] (in db)
        # snippet: "content": ... (in seed? no, seed list had objects with citations)
        # Actually seed_data.json snippet showed list of objects inside 'references'?
        # Wait, snippet 1100-1156 showed list of objects ending with type: knowledge_base.
        # But where is the Key?
        # Ah, seed_data.json is a LIST of components?
        # item 1154 was ONE component.
        # Inside it, "references": [...]? Or "content": [...]?
        # The snippet started at 1100 inside a list.
        # I'll just count whatever looks like a list size.
        count = 0
        if 'references' in kb: count = len(kb['references'])
        elif 'content' in kb and isinstance(kb['content'], list): count = len(kb['content'])
        
        out_f.write(f"References Count: {count}\n")
    else:
        out_f.write("Knowledge Base NOT FOUND in components\n")

def main():
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as out:
        check_file('c:/src/quorum/data/db.json', 'DB', out)
        check_file('c:/src/quorum/backend/seed/seed_data.json', 'SEED', out)

if __name__ == "__main__":
    main()
