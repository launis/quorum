import json
import os
import shutil
import datetime

SEED_PATH = r"c:\src\quorum\backend_v2\seed\seed_data.json"
BACKUP_DIR = r"c:\src\quorum\backend_v2\seed\backups"

def main():
    if not os.path.exists(SEED_PATH):
        print(f"Error: Could not find seed file at {SEED_PATH}")
        return

    # Create backup directory if it doesn't exist
    os.makedirs(BACKUP_DIR, exist_ok=True)

    # Copy raw seed file to a timestamped backup
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"seed_data_preslug_{timestamp}.json")
    shutil.copy2(SEED_PATH, backup_path)
    print(f"✅ Varmuuskopio luotu: {backup_path}")

    # Read the seed data
    with open(SEED_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # The top-level keys we want to inspect for missing slugs
    target_keys = ["system_config", "prompt_blocks", "workflows", "steps"]
    
    modifications = 0
    for key in target_keys:
        if key in data and isinstance(data[key], list):
            for i, item in enumerate(data[key]):
                if isinstance(item, dict) and "id" in item:
                    # If the item has an ID but completely lacks 'slug', inject it
                    if "slug" not in item:
                        item["slug"] = item["id"]
                        modifications += 1
                        print(f"🔧 Lisätty puuttuva slug -> {key}[{i}] (ID: {item['id']})")
    
    if modifications > 0:
        # Save back the patched data
        with open(SEED_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Paikkaus valmis! Yhteensä {modifications} slug-kenttää injektoitu onnistuneesti.")
    else:
        print("✅ Kaikilla kohteilla oli jo slug-kenttä. Mitään ei muutettu.")

if __name__ == "__main__":
    main()
