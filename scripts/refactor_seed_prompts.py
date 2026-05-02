import json
import shutil
import re
from pathlib import Path

# Paths relative to execution in the workspace root
WORKSPACE_ROOT = Path("c:/src/quorum")
SEED_FILE = WORKSPACE_ROOT / "backend_v2/seed/seed_data.json"
BACKUP_FILE = WORKSPACE_ROOT / "backend_v2/seed/seed_data.backup.json"

def clean_text(text: str) -> str:
    """Cleans up legacy target extensions and parameter noise from system instructions."""
    if not isinstance(text, str):
        return text
        
    original = text
    # Remove TARGET EXTENSIONS TO HARVEST: and everything after it
    text = re.sub(r'(?im)^TARGET EXTENSIONS TO HARVEST:.*$', '', text)
    text = re.sub(r'(?im)^TARGET EXTENSIONS:.*$', '', text)
    
    # Strip any trailing whitespace
    return text.strip()

def process_node(node, changes: list):
    """Recursively process the JSON node to find target fields."""
    if isinstance(node, dict):
        for k, v in node.items():
            if isinstance(v, str):
                if k in ['system_prompt', 'ai_description']:
                    cleaned = clean_text(v)
                    if cleaned != v:
                        changes.append({"key": k, "old": v, "new": cleaned})
                        node[k] = cleaned
            elif isinstance(v, (dict, list)):
                process_node(v, changes)
    elif isinstance(node, list):
        for item in node:
            process_node(item, changes)
    return node

def main():
    if not SEED_FILE.exists():
        print(f"Error: {SEED_FILE} not found.")
        return
        
    print(f"Backing up seed data to {BACKUP_FILE}")
    shutil.copy2(SEED_FILE, BACKUP_FILE)
    
    with open(SEED_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    changes = []
    
    print("Scanning seed_data.json for system_prompt and ai_description...")
    process_node(data, changes)
        
    print(f"\nFound {len(changes)} modifications.")
    for i, c in enumerate(changes):
        print(f"[{i+1}] Modified {c['key']} - Removed legacy extension text.")
        
    if changes:
        with open(SEED_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        print("\nSUCCESS: Saved modifications to seed_data.json.")
        print("NOTE: You must run `python scripts/run_seed.py` (or your local seed protocol) to apply this to the local TinyDB.")
    else:
        print("\nNo changes were necessary.")

if __name__ == '__main__':
    main()
