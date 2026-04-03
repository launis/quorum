import codecs
import json

SEED_FILE = "backend_v2/seed/seed_data.json"


def nuke_legacy() -> None:
    print(f"Reading {SEED_FILE}...")
    with codecs.open(SEED_FILE, "r", "utf-8") as f:
        content = f.read()

    # The exact ghost ID from the screenshot
    ghost_id = "prf_e99f728368684813"
    new_id = "prf_7cc661da3f9f405c"

    count = content.count(ghost_id)
    if count == 0:
        print(f"Ghost ID {ghost_id} not found in text. Checking if structural...")
    else:
        content = content.replace(ghost_id, new_id)
        with codecs.open(SEED_FILE, "w", "utf-8") as f:
            f.write(content)
        print(f"✅ Nuked {count} occurrences of {ghost_id} -> {new_id} in {SEED_FILE}")

    # Let's also definitively clean active_profile_id or output_profile_id in executions just in case
    with codecs.open(SEED_FILE, "r", "utf-8") as f:
        data = json.load(f)

    modified = False
    for exe in data.get("executions", []):
        current_profiles = [p["id"] for p in data.get("output_profiles", [])]
        if "output_profile_id" in exe and exe["output_profile_id"] not in current_profiles:
            print(f"Fixing execution {exe.get('id')} orphaned profile {exe.get('output_profile_id')}")
            exe["output_profile_id"] = new_id
            modified = True

        if "profile_id" in exe and exe["profile_id"] not in [p["id"] for p in data.get("output_profiles", [])]:
            exe["profile_id"] = new_id
            modified = True

    if modified:
        with codecs.open(SEED_FILE, "w", "utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("✅ Fixed orphaned execution profiles in JSON structure.")


if __name__ == "__main__":
    nuke_legacy()
