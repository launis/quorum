import json
import os
import shutil
from datetime import datetime

seed_path = 'c:/src/quorum/backend_v2/seed/seed_data.json'
db_path = 'c:/src/quorum/data/db_v2.json'
backup_dir = 'c:/src/quorum/backend_v2/seed/backups'

def run():
    # 1. Backup
    os.makedirs(backup_dir, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(backup_dir, f"seed_data_backup_{ts}.json")
    shutil.copy2(seed_path, backup_path)
    print(f"Backed up seed_data.json to {backup_path}")

    # 2. Read live DB
    with open(db_path, 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    # 3. Find the target execution
    target_exe = None
    for exe in db.get('executions', {}).values():
        if exe.get('id') == 'exe_47d434eb9c6c4a12b0f61480c0c49f8c':
            target_exe = exe
            break
            
    if not target_exe:
        print("ERROR: Target execution exe_47d... not found in db_v2.json!")
        return

    # Hydrate from disk storage if results were offloaded due to massive PDF string
    if target_exe.get("results_storage_path"):
        blob_path = os.path.join("c:/src/quorum/data/files", target_exe["results_storage_path"])
        if os.path.exists(blob_path):
            with open(blob_path, 'r', encoding='utf-8') as b:
                target_exe["results"] = json.load(b)
            del target_exe["results_storage_path"]
            print("Hydrated results from blob storage.")

    # Remove massive raw_inputs baseline from seed data so the seed isn't statically 2MB
    # We keep the base structure but remove the raw Base64 document payload for the mock execution
    if "raw_inputs" in target_exe and isinstance(target_exe["raw_inputs"], dict):
        if "inputs" in target_exe["raw_inputs"]:
            # Delete any megabyte-sized input payloads
            target_exe["raw_inputs"]["inputs"] = {
                k: v for k, v in target_exe["raw_inputs"]["inputs"].items() if len(str(v)) < 5000
            }
            target_exe["raw_inputs"]["inputs"]["_NOTE_"] = "Base64 payloads stripped from seed template to keep file size low"

    # 4. Update Seed Data
    with open(seed_path, 'r', encoding='utf-8') as f:
        seed_data = json.load(f)
        
    print(f"Original executions in seed_data: {len(seed_data.get('executions', []))}")
    
    # Replace all executions with just this one
    seed_data['executions'] = [target_exe]

    # 5. Write Sequence
    with open(seed_path, 'w', encoding='utf-8') as f:
        json.dump(seed_data, f, indent=2, ensure_ascii=False)
        
    print(f"Successfully promoted execution exe_47d434eb9c6c4a12b0f61480c0c49f8c as the solitary template.")

if __name__ == '__main__':
    run()
