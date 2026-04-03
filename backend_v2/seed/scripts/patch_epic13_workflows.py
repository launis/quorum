import json
from pathlib import Path

SEED_FILE = Path("backend_v2/seed/seed_data.json")


def patch_workflows() -> None:
    if not SEED_FILE.exists():
        print(f"Error: {SEED_FILE} not found!")
        return

    with open(SEED_FILE, encoding="utf-8") as f:
        data = json.load(f)

    # Gather the new profiles created by the previous patch
    new_profiles = data.get("output_profiles", [])
    if not new_profiles:
        print("Error: No output profiles found in root. Did you run patch_epic13.py first?")
        return

    embedded_profiles = {}
    for p in new_profiles:
        pid = p["id"]
        embedded_profiles[pid] = {
            "name": p["name"],
            "description": p.get("description"),
            "display_scale": p.get("display_scale", "original"),
            "layouts": p.get("layouts", []),
        }

    default_id = new_profiles[0]["id"]  # Assume the first one (prf_7cc661da3f9f405c) is default

    patched_count = 0
    # Patch workflows
    for wf in data.get("workflows", []):
        wf["output_profiles"] = embedded_profiles
        wf["default_profile_id"] = default_id
        patched_count += 1

    with open(SEED_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ Successfully patched {patched_count} workflows in {SEED_FILE}")


if __name__ == "__main__":
    patch_workflows()
