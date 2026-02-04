import json
import shutil


def restore_kb():
    backup_path = 'c:/src/quorum/backend/seed/seed_data.json.bak_full'
    current_path = 'c:/src/quorum/backend/seed/seed_data.json'

    print("Loading backup...")
    with open(backup_path, encoding='utf-8') as f:
        backup = json.load(f)

    print("Loading current...")
    with open(current_path, encoding='utf-8') as f:
        current = json.load(f)

    # Find KB in backup
    kb = None
    if 'components' in backup:
        for c in backup['components']:
            if isinstance(c, dict) and (c.get('id') == 'knowledge_base' or c.get('type') == 'knowledge_base'):
                kb = c
                print("Found KB in Backup.")
                break

    if kb:
        # Inject into current
        if 'components' not in current:
            current['components'] = []

        # Check if already exists (it shouldn't, based on verification)
        exists = False
        for c in current['components']:
            if isinstance(c, dict) and (c.get('id') == 'knowledge_base' or c.get('type') == 'knowledge_base'):
                exists = True
                print("KB already exists in current (Unexpected).")
                break

        if not exists:
            current['components'].append(kb)
            print(" injected KB into current components.")

            # Save
            shutil.copy(current_path, current_path + ".bak_restore")
            with open(current_path, 'w', encoding='utf-8') as f:
                json.dump(current, f, indent=4, ensure_ascii=False)
            print("Saved restored seed_data.json.")
        else:
            print("Skipping injection.")
    else:
        print("Error: KB not found in backup??")

if __name__ == "__main__":
    restore_kb()
