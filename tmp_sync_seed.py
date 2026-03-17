import json
import shutil
import datetime
import os
from pathlib import Path
from tinydb import TinyDB, Query

PROJECT_ROOT = Path(__file__).resolve().parent
SEED_FILE = os.path.join(PROJECT_ROOT, "backend_v2", "seed", "seed_data.json")
BACKUPS_DIR = os.path.join(PROJECT_ROOT, "backend_v2", "seed", "backups")
LIVE_DB = os.path.join(PROJECT_ROOT, "data", "db_v2.json")

def sync_db_to_seed():
    if not os.path.exists(BACKUPS_DIR):
        os.makedirs(BACKUPS_DIR)
        
    # 1. Backup
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUPS_DIR, f"seed_data_backup_pre_ui_sync_{timestamp}.json")
    shutil.copy(SEED_FILE, backup_path)
    print(f"Backup created: {backup_path}")
    
    # 2. Extract from Live DB
    try:
        db = TinyDB(LIVE_DB, encoding="utf-8")
        live_wf = db.table("workflows").get(Query().id == "workflow_courtroom_20_full_audit")
        if not live_wf:
            print("ERROR: Could not find live workflow in db_v2.json")
            return
            
        new_render_blueprints = live_wf.get("render_blueprints")
        if not new_render_blueprints:
            print("ERROR: No render_blueprints found in live DB")
            return
            
    except Exception as e:
        print(f"Error reading live DB: {e}")
        return
        
    # 3. Inject to Seed
    try:
        with open(SEED_FILE, "r", encoding="utf-8") as f:
            seed_data = json.load(f)
            
        updated = False
        for wf in seed_data.get("workflows", []):
            if wf.get("id") == "workflow_courtroom_20_full_audit":
                wf["render_blueprints"] = new_render_blueprints
                updated = True
                break
                
        if not updated:
            print("ERROR: Could not find workflow in seed_data.json")
            return
            
        with open(SEED_FILE, "w", encoding="utf-8") as f:
            json.dump(seed_data, f, indent=4, ensure_ascii=False)
            
        print("SUCCESS: seed_data.json updated successfully with latest UI layout!")
        
    except Exception as e:
        print(f"Error updating seed DB: {e}")

if __name__ == "__main__":
    sync_db_to_seed()
