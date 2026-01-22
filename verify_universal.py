import json

OUTPUT_FILE = 'c:/src/quorum/verification_universal.txt'

def check(out):
    path = 'c:/src/quorum/backend/seed/seed_data.json'
    out.write(f"Checking {path}\n")
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 1. System Config
    sc = data.get('system_config')
    out.write(f"system_config Type: {type(sc)}\n")
    mr_found = False
    
    iterator = []
    if isinstance(sc, list):
        iterator = sc
    elif isinstance(sc, dict):
        iterator = sc.values()
    
    for item in iterator:
        if isinstance(item, dict) and item.get('id') == 'model_registry':
            mr_found = True
            models = item.get('models', {}).get('google', {})
            out.write(f"SUCCESS: Model Registry Found. Models: {list(models.keys())}\n")
            break
            
    if not mr_found:
        out.write("FAILURE: Model Registry NOT FOUND.\n")

    # 2. Components (Knowledge Base)
    comps = data.get('components')
    out.write(f"components Type: {type(comps)}\n")
    kb_found = False
    
    iterator = []
    if isinstance(comps, list):
        iterator = comps
    elif isinstance(comps, dict):
        iterator = comps.values()

    for item in iterator:
        if isinstance(item, dict):
            if item.get('id') == 'knowledge_base' or item.get('type') == 'knowledge_base':
                kb_found = True
                refs = item.get('references') or item.get('content') or []
                out.write(f"SUCCESS: Knowledge Base Found. Items: {len(refs)}\n")
                break
    
    if not kb_found:
        out.write("FAILURE: Knowledge Base NOT FOUND.\n")

def main():
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        check(f)

if __name__ == "__main__":
    main()
