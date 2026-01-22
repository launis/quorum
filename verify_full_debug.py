import json
import os

OUTPUT_FILE = 'c:/src/quorum/verification_full_debug.txt'

def check_sync(out):
    seed_path = 'c:/src/quorum/backend/seed/seed_data.json'
    out.write(f"Checking {seed_path}...\n")
    try:
        with open(seed_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        out.write(f"Error loading seed: {e}\n")
        return

    # Check Components (KB)
    components = data.get('components', [])
    out.write(f"Components Count: {len(components)}\n")
    kb_found = False
    for i, c in enumerate(components):
        if isinstance(c, dict):
            cid = c.get('id')
            ctype = c.get('type')
            if cid == 'knowledge_base' or ctype == 'knowledge_base':
                kb_found = True
                out.write(f"  [{i}] ID: {cid}, Type: {ctype} (FOUND)\n")
            elif 'knowledge' in str(cid).lower() or 'base' in str(cid).lower():
                out.write(f"  [{i}] NEAR MATCH? ID: {cid}, Type: {ctype}\n")
    if not kb_found:
        out.write("  WARNING: Knowledge Base NOT FOUND in components.\n")

    # Check System Config (Model Registry)
    sys_conf = data.get('system_config', [])
    out.write(f"System Config Items: {len(sys_conf)}\n")
    mr_found = False
    for i, item in enumerate(sys_conf):
        if isinstance(item, dict):
            iid = item.get('id')
            out.write(f"  [{i}] ID: {iid}\n")
            if iid == 'model_registry':
                mr_found = True
                out.write(f"    FOUND model_registry.\n")
    if not mr_found:
        out.write("  WARNING: Model Registry NOT FOUND in system_config.\n")

def main():
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        check_sync(f)

if __name__ == "__main__":
    main()
