import json
import os
import shutil
from datetime import datetime

seed_path = r"c:\src\quorum\backend_v2\seed\seed_data.json"
backup_dir = r"c:\src\quorum\backend_v2\seed\backups"

os.makedirs(backup_dir, exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_path = os.path.join(backup_dir, f"seed_data_backup_p6_{timestamp}.json")

# Mandatory Backup Protocol
shutil.copy2(seed_path, backup_path)
print(f"Backed up to: {backup_path}")

with open(seed_path, "r", encoding="utf-8") as f:
    data = json.load(f)

mod_count = 0
for workflow in data.get("workflows", []):
    for step in workflow.get("steps", []):
        if "allowed_mcp_tools" not in step:
            step["allowed_mcp_tools"] = []
            mod_count += 1
        if "safety" not in step:
            step["safety"] = "safe"
            mod_count += 1

with open(seed_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print(f"Migration complete! Modified {mod_count} fields across steps.")
