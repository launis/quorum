"""V2 Migration Script.

Extracts data from the active V2 database (db_v2.json) and formats it back 
into the Pydantic-validated seed layout. Validates against STANDARD_REGISTRY.
"""

import argparse
import json
import logging
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend_v2.seed.seed_registry import STANDARD_REGISTRY
from tinydb import TinyDB

SOURCE_DB_PATH = os.path.join(PROJECT_ROOT, "data", "db_v2.json")

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def migrate_db_to_seed(target_seed_path: str, template_path: str, source_type: str = "local") -> None:
    print("--- MIGRATION STARTED (Robust Restoration Mode) ---")
    print(f"Source: {source_type.upper()}")
    print(f"Template: {template_path}")
    print(f"Target: {target_seed_path}")

    if source_type == "local" and not os.path.exists(SOURCE_DB_PATH):
        print(f"ERROR: Source file not found: {SOURCE_DB_PATH}")
        sys.exit(1)

    # 1. Automatic Backup
    if os.path.exists(target_seed_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(os.path.dirname(target_seed_path), "backups")
        os.makedirs(backup_dir, exist_ok=True)
        filename = os.path.basename(target_seed_path)
        backup_path = os.path.join(backup_dir, f"{filename}.{timestamp}.bak")
        try:
            shutil.copy2(target_seed_path, backup_path)
            print(f"[SUCCESS] Backup created: {backup_path}")
        except Exception as e:
            print(f"[ERROR] Failed to create backup: {e}")
            sys.exit(1)

    try:
        source_data = {}
        if source_type == "local":
            with open(SOURCE_DB_PATH, encoding="utf-8") as f:
                source_data = json.load(f)

        # Load template to act as the baseline.
        current_seed = {}
        if os.path.exists(template_path):
            with open(template_path, encoding="utf-8") as f:
                current_seed = json.load(f)
        else:
            print(f"WARNING: Template not found at {template_path}. Formatting may not perfectly match.")

        # Extraction Helpers
        def extract_from_tinydb(key: str) -> list[dict]:
            if key not in source_data:
                return []
            raw = source_data[key]
            if isinstance(raw, dict):
                # TinyDB structures tables as dict of { '1': {...}, '2': {...} }
                return list(raw.values())
            return raw

        def extract_from_firestore(collection_name: str) -> list[dict]:
            try:
                from google.cloud import firestore
                db = firestore.Client()
                docs = db.collection(collection_name).stream()
                return [doc.to_dict() for doc in docs]
            except Exception as e:
                logger.error(f"  [!] Failed reading from Firestore ({collection_name}): {e}", exc_info=True)
                return []

        def extract_list(collection_name: str) -> list[dict]:
            if source_type == "firestore":
                return extract_from_firestore(collection_name)
            return extract_from_tinydb(collection_name)

        def update_collection_in_place(target_list: list[dict], source_list: list[dict], id_field: str = "id", collection_key: str = "") -> list[dict]:
            """Updates target list in-place using source list, preserving dictionary key order and validating against V2 Registry."""
            if target_list is None:
                target_list = []

            # Create standard dict for O(1) lookups
            source_dict = {
                item.get(id_field): item for item in source_list if isinstance(item, dict) and item.get(id_field)
            }

            registry_model = STANDARD_REGISTRY.get(collection_key, {}).get("model")

            new_target_list = []
            seen_ids = set()

            # Pass 1: Update existing items and keep them in place
            for existing_item in target_list:
                item_id = existing_item.get(id_field)
                if not item_id or item_id not in source_dict:
                    # Item no longer exists in DB, drop it
                    continue

                source_item = source_dict[item_id]

                # Update existing keys AND add completely new keys automatically
                for k, v in source_item.items():
                    existing_item[k] = v

                # Remove deleted keys (present in existing, but dropped from source)
                for k in list(existing_item.keys()):
                    if k not in source_item:
                        del existing_item[k]

                # Validate with Pydantic if registry exists to ensure types are strictly bound (e.g no DateTime leakage to strings before dumping)
                if registry_model:
                    try:
                        validated = registry_model.validate_python(existing_item)
                        existing_item = validated.model_dump(mode="json")
                    except Exception as e:
                        logger.warning(f"Validation warning during extraction for {item_id} in {collection_key}: {e}")
                
                new_target_list.append(existing_item)
                seen_ids.add(item_id)

            # Pass 2: Append purely new items at the end
            for source_item in source_list:
                item_id = source_item.get(id_field)
                if item_id and item_id not in seen_ids:
                    
                     # Validate new items too
                    if registry_model:
                        try:
                            validated = registry_model.validate_python(source_item)
                            source_item = validated.model_dump(mode="json")
                        except Exception as e:
                            logger.warning(f"Validation warning for new item {item_id} in {collection_key}: {e}")

                    new_target_list.append(source_item)

            return new_target_list

        print("Processing standard collections dynamically with SSOT Order Preservation...")

        # We only care about standard collections from the registry.
        # Ensure they all exist in the target file, even if empty.
        for collection_key, config in STANDARD_REGISTRY.items():
            db_list = extract_list(collection_key)
            id_key = str(config.get("id_field", "id"))
            
            current_list = current_seed.get(collection_key, [])

            current_seed[collection_key] = update_collection_in_place(
                current_list, 
                db_list, 
                id_field=id_key,
                collection_key=collection_key
            )
            print(f"  [+] {collection_key}: {len(current_seed[collection_key])} items extracted.")

        # Write to file
        with open(target_seed_path, "w", encoding="utf-8") as f:
            json.dump(current_seed, f, indent=2, ensure_ascii=False) # Important: V2 standard uses 2 spaces
            # Ensure final newline
            f.write('\n')

        print("--- MIGRATION SUCCESSFUL ---")
        print(f"[SUCCESS] Data written to {target_seed_path}")
        print("[SUCCESS] JSON Format: Indented (2 spaces), UTF-8")

        # Automatically run the deep diff validation test
        from backend_v2.seed.seed_validator import validate_seeds
        print("\n--- RUNNING POST-MIGRATION PARITY VALIDATION ---")
        validate_seeds(template_path, target_seed_path)

    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Migrate live database back to seed_data.json")
    parser.add_argument(
        "target_file",
        help="Target output file (e.g. backend_v2/seed/seed_data_test.json)",
    )
    parser.add_argument(
        "--template",
        default=os.path.join(PROJECT_ROOT, "backend_v2", "seed", "seed_data.json"),
        help="Template file to preserve ordering",
    )
    parser.add_argument(
        "--source",
        default="local",
        choices=["local", "firestore"],
        help="Target database to extract from (local or firestore)",
    )
    args = parser.parse_args()

    migrate_db_to_seed(target_seed_path=args.target_file, template_path=args.template, source_type=args.source)

if __name__ == "__main__":
    main()
