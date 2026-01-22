import json
import os

OUTPUT_FILE = 'c:/src/quorum/verification_full_sync.txt'

def check_sync(out):
    seed_path = 'c:/src/quorum/backend/seed/seed_data.json'
    out.write(f"Checking {seed_path}...\n")
    try:
        with open(seed_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        out.write(f"Error loading seed: {e}\n")
        return

    # Check Workflows
    workflows = data.get('workflows', [])
    out.write(f"Workflows Count: {len(workflows)}\n")
    if isinstance(workflows, list) and workflows:
        first = workflows[0]
        if isinstance(first, dict):
            out.write(f"  First Workflow ID: {first.get('id')}\n")
            out.write(f"  First Workflow Name: {first.get('name')}\n")
        else:
            out.write(f"  First Workflow Item is not dict: {type(first)}\n")
    else:
        out.write("  WARNING: Workflows is not a list or empty.\n")

    # Check Components (KB)
    components = data.get('components', [])
    out.write(f"Components Count: {len(components)}\n")
    kb_found = False
    for c in components:
        if isinstance(c, dict):
            if c.get('id') == 'knowledge_base':
                kb_found = True
                count = len(c.get('references', [])) if 'references' in c else len(c.get('content', []))
                out.write(f"  Knowledge Base Found (Refs: {count})\n")
                break
    if not kb_found:
        out.write("  WARNING: Knowledge Base NOT FOUND in components.\n")

    # Check System Config (Model Registry)
    sys_conf = data.get('system_config', [])
    out.write(f"System Config Items: {len(sys_conf)}\n")
    mr_found = False
    for item in sys_conf:
        if isinstance(item, dict):
            if item.get('id') == 'model_registry':
                mr_found = True
                models = item.get('models', {}).get('google', {})
                out.write(f"  Model Registry Found. Google Models: {list(models.keys())}\n")
                break
    if not mr_found:
        out.write("  WARNING: Model Registry NOT FOUND in system_config.\n")

def main():
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        check_sync(f)

if __name__ == "__main__":
    main()
