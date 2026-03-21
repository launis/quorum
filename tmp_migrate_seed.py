import json
import os
import shutil
import re
from datetime import datetime, timezone

SEED_FILE = r"c:\src\quorum\backend_v2\seed\seed_data.json"
BACKUP_DIR = r"c:\src\quorum\backend_v2\seed\backups"

def main():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"seed_data_backup_v2_{timestamp}.json")
    
    shutil.copy2(SEED_FILE, backup_path)
    print(f"Backup created at: {backup_path}")
    
    with open(SEED_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    steprules_modified = 0
    
    workflows = data.get("workflows", [])
    
    for workflow in workflows:
        # Build mapping from old_id to new_id
        id_map = {}
        counters = {}
        
        for step in workflow.get("steps", []):
            old_id = step.get("id", "")
            if old_id.startswith("steprule_"):
                task_slug = step.get("task_blueprint", "unknown")
                # e.g. "step_xai_reporter" -> "xaireporter"
                base_name = re.sub(r'^step_', '', task_slug)
                base_name = re.sub(r'[^a-z0-9]', '', base_name.lower())
                
                if base_name in counters:
                    counters[base_name] += 1
                else:
                    counters[base_name] = 1
                
                # Make sure the name itself is at least 8 chars long if possible
                if len(base_name) < 7:
                    base_name = base_name.ljust(7, 'x')
                    
                new_id = f"steprule_{base_name}{counters[base_name]}"
                
                if old_id != new_id:
                    id_map[old_id] = new_id
                    step["id"] = new_id
                    steprules_modified += 1
                    
        # Update depends_on in the same workflow
        for step in workflow.get("steps", []):
            new_depends = []
            for dep in step.get("depends_on", []):
                if dep in id_map:
                    new_depends.append(id_map[dep])
                else:
                    new_depends.append(dep)
            step["depends_on"] = new_depends

        # Also update output_mapping (double-check it's there)
        workflow["output_mapping"] = {"preset_view": "3d_complex"}
        
        # Ensure render_blueprints is completely gone
        if "render_blueprints" in workflow:
            del workflow["render_blueprints"]

    with open(SEED_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        
    print(f"SUCCESS: Cleaned/Humanized {steprules_modified} steprule IDs.")

if __name__ == "__main__":
    main()
