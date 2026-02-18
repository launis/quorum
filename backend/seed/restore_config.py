
import json
import sys
from pathlib import Path

BACKUP_PATH = Path(r"c:\src\quorum\backend\seed\seed_data.json.20260217_145120.bak")
TARGET_PATH = Path(r"c:\src\quorum\backend\seed\seed_data.json")

def restore_config():
    if not BACKUP_PATH.exists():
        print(f"Backup file not found: {BACKUP_PATH}")
        sys.exit(1)
        
    print(f"Reading backup from {BACKUP_PATH}...")
    with open(BACKUP_PATH, 'r', encoding='utf-8') as f:
        backup_data = json.load(f)
        
    system_config = backup_data.get("system_config", [])
    if not system_config:
        print("No system_config found in backup!")
        sys.exit(1)
        
    print(f"Found {len(system_config)} items in system_config.")
    
    print(f"Reading target from {TARGET_PATH}...")
    with open(TARGET_PATH, 'r', encoding='utf-8') as f:
        target_data = json.load(f)
        
    target_data["system_config"] = system_config
    
    print(f"Writing updated data to {TARGET_PATH}...")
    with open(TARGET_PATH, 'w', encoding='utf-8') as f:
        json.dump(target_data, f, indent=4, ensure_ascii=False)
        
    print("Done.")

if __name__ == "__main__":
    restore_config()
