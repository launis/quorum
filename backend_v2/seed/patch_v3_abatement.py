import json
import os
import shutil
from datetime import datetime

def main() -> None:
    seed_path = r"backend_v2/seed/seed_data.json"
    backup_dir = r"backend_v2/seed/backups"

    os.makedirs(backup_dir, exist_ok=True)
    backup_path = os.path.join(backup_dir, f"seed_data_pre_v3_{datetime.now().strftime('%Y%m%d%H%M%S')}.json")
    shutil.copy2(seed_path, backup_path)
    print(f"Backup created at: {backup_path}")

    with open(seed_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Patch workflows with the new mandatory strict fields
    for wf in data.get("workflows", []):
        if "status" not in wf:
            wf["status"] = "published"
        if "version" not in wf:
            wf["version"] = 1
        if "default_profile_id" not in wf:
            wf["default_profile_id"] = "default"

    with open(seed_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("seed_data.json patched successfully! V3 Configuration Sovereignty enforced.")

if __name__ == "__main__":
    main()
