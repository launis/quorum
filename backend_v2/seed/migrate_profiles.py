import json
import os
import shutil
import uuid
from datetime import datetime


def main() -> None:
    seed_path = os.path.join("backend_v2", "seed", "seed_data.json")
    backup_dir = os.path.join("backend_v2", "seed", "backups")
    os.makedirs(backup_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(backup_dir, f"seed_data_{timestamp}.json")

    shutil.copy2(seed_path, backup_path)
    print(f"Backup created at {backup_path}")

    with open(seed_path, encoding="utf-8") as f:
        data = json.load(f)

    count = 0
    if "output_profiles" in data:
        for profile in data["output_profiles"]:
            old_id = profile.get("id")
            if old_id and not old_id.startswith("prf_"):
                # Retain the old readable ID as the routing slug
                profile["slug"] = old_id
                # Apply Stripe Pattern Opaque ID
                new_id = f"prf_{uuid.uuid4().hex[:12]}"
                profile["id"] = new_id
                print(f"Migrated OutputProfile: {old_id} -> ID: {new_id}, SLUG: {profile['slug']}")
                count += 1
            elif old_id and "slug" not in profile:
                profile["slug"] = old_id
                print(f"OutputProfile {old_id} already opaque but missing slug, fixing...")
                count += 1

    if count > 0:
        with open(seed_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Successfully migrated {count} profiles.")
    else:
        print("No profiles needed migration.")

if __name__ == "__main__":
    main()
