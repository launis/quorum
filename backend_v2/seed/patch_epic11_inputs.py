import json
import os
from datetime import datetime

SEED_FILE = "backend_v2/seed/seed_data.json"
BACKUP_DIR = "backend_v2/seed/backups"

def patch_expected_inputs():
    with open(SEED_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Varmuuskopiointi
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"seed_data_pre_epic11_{timestamp}.json")
    
    with open(backup_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Backup created at: {backup_path}")

    # Paikkaus
    updated_count = 0
    for step in data.get("steps", []):
        slug = step.get("slug", "")
        step_type = step.get("type", "")
        
        # Oletus: kaikki odottavat vähintään "context" argumenttia
        if slug == "step_input_processing":
            step["expected_inputs"] = ["document", "context"]
        elif step_type == "logic" or slug == "sp_d245365e4a274b9e": # Scoring Engine
            step["expected_inputs"] = ["results"]
        else:
            step["expected_inputs"] = ["context"]
            
        step["output_schema"] = None
        updated_count += 1

    # Tallennus
    with open(SEED_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"seed_data.json patched successfully! Epic 11 (Strongly Typed DAGs) enforced.")
    print(f"Updated {updated_count} steps with 'expected_inputs' correctly.")

if __name__ == "__main__":
    patch_expected_inputs()
