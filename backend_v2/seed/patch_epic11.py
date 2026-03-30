import json
import os
import shutil
from datetime import datetime, timezone

def main():
    seed_path = os.path.join("backend_v2", "seed", "seed_data.json")
    backup_dir = os.path.join("backend_v2", "seed", "backups")
    
    # Ensure backup directory exists
    os.makedirs(backup_dir, exist_ok=True)
    
    # Determine absolute path
    abs_seed_path = os.path.abspath(seed_path)
    
    # 1. Create a backup
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    backup_path = os.path.join(backup_dir, f"seed_data_pre_epic11_{timestamp}.json")
    
    print(f"Loading {abs_seed_path}")
    if not os.path.exists(abs_seed_path):
        print("Error: seed_data.json not found!")
        return
        
    shutil.copy2(abs_seed_path, backup_path)
    print(f"Created backup at {backup_path}")

    # 2. Patch the JSON file
    with open(abs_seed_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    patched_count = 0
    if "steps" in data:
        for step in data["steps"]:
            if "expected_inputs" not in step:
                step["expected_inputs"] = []
                patched_count += 1
            if "output_schema" not in step:
                step["output_schema"] = None

    # 3. Save the patched JSON
    with open(abs_seed_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Successfully patched {patched_count} steps with 'expected_inputs' and 'output_schema'.")

if __name__ == "__main__":
    main()
