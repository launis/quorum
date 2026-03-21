import json
import os

SEED_FILE = r"c:\src\quorum\backend_v2\seed\seed_data.json"

def apply_mutations():
    with open(SEED_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    mutated = False
    for workflow in data.get("workflows", []):
        profiles = workflow.get("output_profiles", {})
        for pid, profile in profiles.items():
            name_obj = profile.get("name")
            if name_obj and isinstance(name_obj, dict) and "translations" not in name_obj:
                # Need to upgrade to I18nText
                # Determine default_locale safely (fallback to fi or en if present)
                def_loc = "fi" if "fi" in name_obj else ("en" if "en" in name_obj else list(name_obj.keys())[0] if name_obj else "fi")
                profile["name"] = {
                    "default_locale": def_loc,
                    "translations": name_obj
                }
                mutated = True

    if mutated:
        with open(SEED_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("[MUTATOR] All flat OutputProfile names converted to I18nText successfully.")
    else:
        print("[MUTATOR] No targets required upgrading.")

if __name__ == "__main__":
    apply_mutations()
