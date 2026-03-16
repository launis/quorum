import json
import os
import shutil
from datetime import datetime

SEED_PATH = r"c:\src\quorum\backend_v2\seed\seed_data.json"
BACKUP_DIR = r"c:\src\quorum\backend_v2\seed\backups"

def migrate():
    # 1. Backup
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"seed_data_{timestamp}_ai_description_migration.json")
    shutil.copy2(SEED_PATH, backup_path)
    print(f"Backed up to {backup_path}")

    # 2. Read
    with open(SEED_PATH, encoding='utf-8') as f:
        data = json.load(f)

    # 3. Migrate prompt_blocks
    blocks = data.get("prompt_blocks", [])
    migrated_count = 0
    for block in blocks:
        desc = block.get("description", {})
        if isinstance(desc, dict):
            translations = desc.get("translations", {})
            en_text = translations.get("en", "")
            fi_text = translations.get("fi", "")

            # If there's an active English prompt masquerading as a translation...
            if en_text and en_text != fi_text and not en_text.startswith("Auto-filled"):
                # Move to ai_description at the root
                block["ai_description"] = en_text
                # Reset description.en to be a translation of the FI UI string
                # (or just use the FI string so the UI doesn't look completely empty or strange on EN mode)
                translations["en"] = fi_text + " (EN)"
                migrated_count += 1
            else:
                # Provide a null placeholder or leave empty
                if "ai_description" not in block:
                     block["ai_description"] = None

    # 4. Write back
    with open(SEED_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"Successfully migrated {migrated_count} PromptBlocks.")

if __name__ == '__main__':
    migrate()
