import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


import argparse

# Centralized Registry
from backend.seed.seed_registry import STANDARD_REGISTRY

SOURCE_DB_PATH = r"c:\src\quorum\data\db.json"
TARGET_SEED_PATH = r"c:\src\quorum\backend\seed\seed_data.json"


def migrate_db_to_seed(source_type: str = "local"):
    print("--- MIGRATION STARTED (Robust Restoration Mode) ---")
    print(f"Source: {source_type.upper()}")
    print(f"Target: {TARGET_SEED_PATH}")

    if source_type == "local" and not os.path.exists(SOURCE_DB_PATH):
        print(f"ERROR: Source file not found: {SOURCE_DB_PATH}")
        return

    # 1. Automatic Backup
    if os.path.exists(TARGET_SEED_PATH):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{TARGET_SEED_PATH}.{timestamp}.bak"
        try:
            shutil.copy2(TARGET_SEED_PATH, backup_path)
            print(f"✅ Backup created: {backup_path}")
        except Exception as e:
            print(f"❌ ERROR: Failed to create backup: {e}")
            return

    try:
        source_data = {}
        if source_type == "local":
            with open(SOURCE_DB_PATH, encoding="utf-8") as f:
                source_data = json.load(f)

        # Load current seed_data.json to act as the baseline template.
        # This is CRITICAL to ensure exact bit-for-bit ordering and formatting.
        current_seed = {}
        if os.path.exists(TARGET_SEED_PATH):
            with open(TARGET_SEED_PATH, encoding="utf-8") as f:
                current_seed = json.load(f)

        # Extraction Helpers
        def extract_from_tinydb(key):
            if key not in source_data:
                return []
            raw = source_data[key]
            if isinstance(raw, dict):
                return list(raw.values())
            return raw

        def extract_from_firestore(collection_name):
            try:
                from google.cloud import firestore  # type: ignore[attr-defined]

                db = firestore.Client()
                docs = db.collection(collection_name).stream()
                # Ensure predictable ordering if possible, though dicts will be handled by in-place merger
                return [doc.to_dict() for doc in docs]
            except Exception as e:
                import logging
                logging.getLogger(__name__).error(f"  [!] Failed reading from Firestore ({collection_name}): {e}", exc_info=True)
                return []

        def extract_list(collection_name):
            if source_type == "firestore":
                return extract_from_firestore(collection_name)
            return extract_from_tinydb(collection_name)

        def update_collection_in_place(target_list, source_list, id_field="id"):
            """Updates target list in-place using source list, preserving dictionary key order."""
            if target_list is None:
                target_list = []

            source_dict = {
                item.get(id_field): item for item in source_list if isinstance(item, dict) and item.get(id_field)
            }

            new_target_list = []
            seen_ids = set()

            # Pass 1: Update existing items and keep them in place
            for existing_item in target_list:
                item_id = existing_item.get(id_field)
                if not item_id or item_id not in source_dict:
                    # Item no longer exists in DB, drop it
                    continue

                source_item = source_dict[item_id]

                # In-place update of keys to preserve order
                # 1. Update existing keys AND add completely new keys automatically
                for k, v in source_item.items():
                    existing_item[k] = v

                # 2. Remove deleted keys (present in existing, but dropped from source)
                for k in list(existing_item.keys()):
                    if k not in source_item:
                        del existing_item[k]

                new_target_list.append(existing_item)
                seen_ids.add(item_id)

            # Pass 2: Append purely new items at the end
            for source_item in source_list:
                item_id = source_item.get(id_field)
                if item_id and item_id not in seen_ids:
                    new_target_list.append(source_item)

            return new_target_list

        # Process Standard Collections dynamically based on seed file structure and Unified Registry
        print("Processing standard collections dynamically with SSOT Order Preservation...")

        # We find all root keys that contain lists, all handled dynamically now by STANDARD_REGISTRY
        for collection_name, current_list in current_seed.items():
            if not isinstance(current_list, list):
                continue

            db_list = extract_list(collection_name)

            # Request explicit configuration rules from the unified registry (applies DRY)
            registry_entry = STANDARD_REGISTRY.get(collection_name, {})
            id_key = registry_entry.get("id_field", "id")

            current_seed[collection_name] = update_collection_in_place(current_list, db_list, id_field=id_key)
            print(f"  [+] {collection_name}: {len(current_seed[collection_name])} items")

        # Write to file
        with open(TARGET_SEED_PATH, "w", encoding="utf-8") as f:
            json.dump(current_seed, f, indent=4, ensure_ascii=False)

        print("--- MIGRATION SUCCESSFUL ---")
        print(f"✅ Data written to {TARGET_SEED_PATH}")
        print("✅ JSON Format: Indented (4 spaces), UTF-8")

    except Exception as e:
        print(f"❌ ERROR: Migration failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate live database back to seed_data.json")
    parser.add_argument(
        "target",
        nargs="?",
        default="local",
        choices=["local", "firestore"],
        help="Target database to extract from (local or firestore)",
    )
    args = parser.parse_args()

    migrate_db_to_seed(source_type=args.target)
