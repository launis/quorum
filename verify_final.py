import json

OUTPUT_FILE = 'c:/src/quorum/verification_final.txt'

def verify_final(out):
    path = 'c:/src/quorum/backend/seed/seed_data.json'
    out.write(f"Checking {path}\n")
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Check System Config
    sc = data.get('system_config', {})
    out.write(f"system_config Type: {type(sc)}\n")
    
    iterator = []
    if isinstance(sc, dict):
        iterator = sc.values()
    elif isinstance(sc, list):
        iterator = sc
        
    kb_found = False
    mr_found = False
    
    for item in iterator:
        if isinstance(item, dict):
            iid = item.get('id')
            itype = item.get('type')
            out.write(f"  ID: {iid}, Type: {itype}\n")
            
            if iid == 'knowledge_base' or itype == 'knowledge_base':
                kb_found = True
            if iid == 'model_registry':
                mr_found = True
                
    if kb_found:
        out.write("SUCCESS: Knowledge Base Found in System Config.\n")
    else:
        out.write("FAILURE: Knowledge Base NOT FOUND in System Config.\n")
        
    if mr_found:
        out.write("SUCCESS: Model Registry Found in System Config.\n")
    else:
        out.write("FAILURE: Model Registry NOT FOUND in System Config.\n")

def main():
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        verify_final(f)

if __name__ == "__main__":
    main()
