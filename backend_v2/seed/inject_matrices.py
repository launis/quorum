import json
import os
import shutil
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
            if profile.get("slug") == "deep_analysis":
                layouts = profile.get("layouts", [])
                for layout in layouts:
                    components = layout.get("components", [])
                    if "matrix_toulmin" in components or "matrix_kahneman" in components:
                        print("Updating deep_analysis components...")
                        # Map to exact DB Opaque IDs
                        layout["components"] = [
                            "blk_371c7724eeba40218409b5a3697ac1d3", # Toulmin
                            "blk_9adcb55b7ba44baeaf8921cb2fb935dc"  # Kahneman
                        ]
                        count += 1

            if profile.get("slug") == "executive_summary":
                # Give the executive summary a concrete matrix, like Goodhart
                layouts = profile.get("layouts", [])
                for layout in layouts:
                    if layout.get("layout_type") == "box_1d" and "*" in layout.get("components", []):
                        print("Refining executive_summary Box 1D components...")
                        layout["components"] = [
                            "blk_b5ec25bb352e4dc09de386f0da991a08" # Goodhart
                        ]
                        count += 1

    if count > 0:
        with open(seed_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Successfully migrated matrices in {count} profile layouts.")
    else:
        print("No matrices needed migration.")

if __name__ == "__main__":
    main()
