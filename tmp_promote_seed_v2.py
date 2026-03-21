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
    backup_path = os.path.join(backup_dir, f"seed_data_backup_final_{ts}.json")
    shutil.copy2(seed_path, backup_path)
    print(f"Backed up seed_data.json to {backup_path}")

    # 2. Read live DB with explicit UTF-8 encoding
    with open(db_path, 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    # 3. Find the LATEST execution
    exes = list(db.get('executions', {}).values())
    if not exes:
        print("ERROR: No executions found in live DB.")
        return
        
    exes.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    target_exe = exes[0]
    
    print(f"Targeting Latest Execution: {target_exe.get('id')}")

    # Hydrate from disk storage if results were offloaded due to massive PDF string
    if target_exe.get("results_storage_path"):
        blob_path = os.path.join("c:/src/quorum/data/files", target_exe["results_storage_path"])
        if os.path.exists(blob_path):
            with open(blob_path, 'r', encoding='utf-8') as b:
                target_exe["results"] = json.load(b)
            del target_exe["results_storage_path"]
            print("Hydrated results from blob storage.")

    # Remove massive raw_inputs baseline from seed data so the seed isn't statically 2MB
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
        
    # Replace all executions with just this new one
    seed_data['executions'] = [target_exe]

    # 5. Write Sequence safely enforcing UTF-8 without ascii escaping
    with open(seed_path, 'w', encoding='utf-8') as f:
        json.dump(seed_data, f, indent=2, ensure_ascii=False)
        
    print(f"Successfully promoted execution {target_exe.get('id')} as the solitary template with UTF-8 encoding.")

if __name__ == '__main__':
    run()
