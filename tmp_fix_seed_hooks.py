import json
import sqlite3
import os
import shutil
from datetime import datetime

seed_path = r"c:\src\quorum\backend_v2\seed\seed_data.json"
backup_dir = r"c:\src\quorum\backend_v2\seed\backups"

# 1. Create backup
os.makedirs(backup_dir, exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_path = os.path.join(backup_dir, f"seed_data_backup_scalinghook_{timestamp}.json")
shutil.copy2(seed_path, backup_path)
print(f"Created backup at {backup_path}")

# 2. Modify file
steps_to_modify = [
    "step_archivist", "step_causal_analyst", "step_coach", 
    "step_falsifier", "step_guard", "step_judge", 
    "step_logician", "step_overseer", "step_performativity_detector", 
    "step_profiler", "step_xai_reporter", "step_analyst"
]

with open(seed_path, "r", encoding="utf-8") as f:
    db = json.load(f)

modifications = 0
for step in db.get("steps", []):
    if step.get("id") in steps_to_modify:
        if "post_hooks" not in step:
            step["post_hooks"] = []
        if "normalize_matrix_scores" not in step["post_hooks"]:
            step["post_hooks"].append("normalize_matrix_scores")
            print(f"Added normalize_matrix_scores to {step.get('id')}")
            modifications += 1

if modifications > 0:
    with open(seed_path, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    print(f"Successfully modified {modifications} steps in seed_data.json.")
else:
    print("No modifications needed, hook already exists in all targeted steps.")
