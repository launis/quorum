
import json
import os
import sys
from pathlib import Path

# Paths
SEED_DIR = Path("c:/src/quorum/backend/seed")
BACKUP_FILE = SEED_DIR / "seed_data.json.bak_global_seed"
TARGET_FILE = SEED_DIR / "seed_data.json"

def main():
    print(f"Reading backup from: {BACKUP_FILE}")
    if not BACKUP_FILE.exists():
        print(f"Error: Backup file not found: {BACKUP_FILE}")
        return

    try:
        with open(BACKUP_FILE, "r", encoding="utf-8") as f:
            backup_data = json.load(f)
    except Exception as e:
        print(f"Error reading backup: {e}")
        return

    # Extract knowledge_base
    knowledge_src = backup_data.get("knowledge_base")
    if not knowledge_src:
        print("Warning: 'knowledge_base' not found in backup.")
        return

    # Convert to List
    knowledge_list = []
    if isinstance(knowledge_src, dict):
        print(f"Found 'knowledge_base' as Dict with {len(knowledge_src)} items. Converting to List.")
        for key, value in knowledge_src.items():
            knowledge_list.append(value)
    elif isinstance(knowledge_src, list):
        print(f"Found 'knowledge_base' as List with {len(knowledge_src)} items.")
        knowledge_list = knowledge_src
    else:
        print(f"Unknown type for knowledge_base: {type(knowledge_src)}")
        return

    # Read Target File
    print(f"Reading target file: {TARGET_FILE}")
    if not TARGET_FILE.exists():
        print(f"Error: Target file not found: {TARGET_FILE}")
        return

    try:
        with open(TARGET_FILE, "r", encoding="utf-8") as f:
            target_data = json.load(f)
    except Exception as e:
        print(f"Error reading target: {e}")
        return

    # Update Target
    old_kb = target_data.get("knowledge_base", [])
    print(f"Current target has {len(old_kb)} knowledge items.")
    
    target_data["knowledge_base"] = knowledge_list
    print(f"Updated target with {len(knowledge_list)} knowledge items.")

    # Save
    try:
        with open(TARGET_FILE, "w", encoding="utf-8") as f:
            json.dump(target_data, f, indent=4, ensure_ascii=False)
        print(f"Successfully saved updated seed_data.json to {TARGET_FILE}")
    except Exception as e:
        print(f"Error saving target: {e}")

if __name__ == "__main__":
    main()
