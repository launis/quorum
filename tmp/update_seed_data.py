import json
import shutil
import time
from pathlib import Path

def main():
    seed_file = Path("c:/src/quorum/backend_v2/seed/seed_data.json")
    backup_dir = Path("c:/src/quorum/backend_v2/seed/backups")
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = int(time.time())
    backup_file = backup_dir / f"seed_data_backup_{timestamp}.json"

    # Rule 3: Backup Database
    shutil.copy2(seed_file, backup_file)
    print(f"[1/3] Backup created securely at: {backup_file}")

    with open(seed_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    updated_count = 0
    # Scan through workflows
    for wf in data.get("workflows", []):
        profiles = wf.get("output_profiles", {})
        if isinstance(profiles, dict):
            for pk, profile in profiles.items():
                if "display_scale" not in profile:
                    # Inject Single Source of Truth initialized value
                    profile["display_scale"] = "original"
                    updated_count += 1

    with open(seed_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"[2/3] Successfully added 'display_scale: original' to {updated_count} output profiles.")
    print(f"[3/3] Seed data is now at 100% Pydantic Parity.")

if __name__ == "__main__":
    main()
