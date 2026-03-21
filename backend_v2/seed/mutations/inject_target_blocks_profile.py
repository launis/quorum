import json
import os
import shutil
from datetime import datetime

SEED_DIR = r"c:\src\quorum\backend_v2\seed"
SEED_FILE = os.path.join(SEED_DIR, "seed_data.json")
BACKUPS_DIR = os.path.join(SEED_DIR, "backups")

# Ensure backups directory exists
os.makedirs(BACKUPS_DIR, exist_ok=True)

# 1. Create a timestamped backup
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = os.path.join(BACKUPS_DIR, f"seed_data_backup_axis_fix_{timestamp}.json")
shutil.copy2(SEED_FILE, backup_file)
print(f"Backup created at: {backup_file}")

# 2. Load the seed data
with open(SEED_FILE, encoding="utf-8") as f:
    data = json.load(f)

# 3. Apply the specific matrix mutations
mutated = False
for workflow in data.get("workflows", []):
    if workflow.get("slug") == "kokonaisvaltainen_auditointi":
        profiles = workflow.get("output_profiles", {})
        default_profile = profiles.get("default")

        if default_profile:
            layouts = default_profile.get("layouts", [])

            # Row 1: 3D Composite (3 real matrices from the 'analyst' step)
            if len(layouts) > 0 and layouts[0].get("preset_view") == "3d_complex":
                layouts[0]["target_blocks"] = [
                    "blk_0522f2416e304a54a67b99ed08398ac8",  # First analyst block
                    "blk_6e98f76e118a42ea992fe82778d386cd",  # Second analyst block
                    "blk_7cf04dae33aa4bb79a20447dfcc879b3"   # Third analyst block
                ]
                mutated = True

            # Row 2: 1D Table (2 real matrices from the 'archivist' step)
            if len(layouts) > 1 and layouts[1].get("preset_view") == "1d_metrics":
                layouts[1]["target_blocks"] = [
                    "blk_cbcab98df3c34ddfb67f1c9b18acf43f",  # First archivist block
                    "blk_266d2532eb60479aaafc77887e23b40a"   # Second archivist block
                ]
                mutated = True

# 4. Save the modified seed data
if mutated:
    with open(SEED_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Successfully injected 3 real matrix IDs for the 3D-Layout and 2 real matrix IDs for the 1D-Layout into seed_data.json!")
else:
    print("Profile components not found in seed_data.json, no changes applied.")
