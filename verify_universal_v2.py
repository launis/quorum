import json

OUTPUT_FILE = 'c:/src/quorum/verification_universal_v2.txt'

def check(out):
    path = 'c:/src/quorum/backend/seed/seed_data.json'
    out.write(f"Checking {path}\n")
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Components (KB)
    comps = data.get('components', [])
    out.write(f"components Type: {type(comps)}\n")
    if isinstance(comps, list):
        out.write(f"Count: {len(comps)}\n")
        kb_found = False
        for i, item in enumerate(comps):
            if isinstance(item, dict):
                cid = item.get('id')
                ctype = item.get('type')
                out.write(f"  [{i}] ID: {cid}, Type: {ctype}\n")
                if cid == 'knowledge_base' or ctype == 'knowledge_base':
                    kb_found = True
        
        if not kb_found:
            out.write("FAILURE: Knowledge Base NOT FOUND.\n")
    else:
        out.write("FAILURE: Components is not a list.\n")

def main():
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        check(f)

if __name__ == "__main__":
    main()
