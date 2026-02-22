"""Main Seeder Entrypoint.

Reads from backend/seed/seed_data.json and populates the target database.
Includes MIGRATION LOGIC to transform Legacy Workflows -> V2.9 GraphEngine Workflows.
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

print(f"DEBUG: Added {PROJECT_ROOT} to sys.path")


from pydantic import ValidationError
from tinydb import Query, TinyDB

from backend.seed.seed_registry import STANDARD_REGISTRY


def _fail_fast(msg, error):
    print(f"\033[91m[CRITICAL FAIL FAST] {msg}\n{str(error)}\033[0m")
    import sys

    sys.exit(1)


# ComponentResponse is a union of specific types

# --- Shared Models (Strict) ---


def _seed_tinydb(db_path: str, seed_data: dict):
    # Imports are now at module level

    try:
        db = TinyDB(db_path, encoding="utf-8")
        db.drop_tables()  # CLEAN SLATE (Drops all tables including executions)
        print(f"[Seeder] CLEARED persistence. Dropped all tables from {db_path}.")
    except Exception as e:
        _fail_fast("Error initializing TinyDB", e)
        return

    # Seed Standard Strict Collections (Iterative Registry Method)
    for col_key, config in STANDARD_REGISTRY.items():
        table_name = str(config["table"])
        target_table = db.table(table_name)
        id_field = str(config["id_field"])
        pyd_adapter: Any = config["model"]
        count = 0

        for item in seed_data.get(col_key, []):
            try:
                validated = pyd_adapter.validate_python(item)
                dumped = validated.model_dump(mode="json")

                if id_field in dumped:
                    if id_field == "uid":
                        target_table.upsert(dumped, Query().uid == dumped["uid"])
                    else:
                        target_table.upsert(dumped, Query().id == dumped["id"])
                    count += 1
                else:
                    print(f"Item lacking {id_field}")

            except ValidationError as ve:
                _fail_fast(f"Validation Error for {col_key} item {item.get(id_field, 'unknown')}", ve)
            except Exception as e:
                _fail_fast(f"Database Error upserting {col_key} item", e)

        print(f"[Seeder] Upserted {count} items to '{col_key}' registry.")

    db.close()
    print(f"[Seeder] Closed DB. Final size: {os.path.getsize(db_path)} bytes.")


def _seed_firestore(seed_data: dict):
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
    except ImportError:
        print("Firebase Admin not installed.")
        return

    if not firebase_admin._apps:
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred)

    db = firestore.client()

    # Clear collections (Added missing ones)
    for col in [
        "workflows",
        "components",
        "steps",
        "system_config",
        "concepts",
        "references",
        "claims",
        "dimensions",
        "organizations",
        "users",
    ]:
        _delete_collection(db.collection(col))

    # Helper for batch operations
    def batch_upsert(collection_name: str, items: list[dict], id_field: str = "id"):
        batch = db.batch()
        count = 0
        total = 0
        for item in items:
            doc_id = item.get(id_field)
            if not doc_id:
                print(f"[Seeder] Error: Item in {collection_name} missing {id_field}. Skipping.")
                continue

            ref = db.collection(collection_name).document(doc_id)
            batch.set(ref, item)
            count += 1
            total += 1
            if count >= 400:
                batch.commit()
                batch = db.batch()
                count = 0
        if count > 0:
            batch.commit()
        print(f"[Seeder] Upserted {total} items to Firestore collection '{collection_name}'.")

    # --- Seed Standard Strict Collections (Iterative Registry Method) ---
    for col_key, config in STANDARD_REGISTRY.items():
        id_field = str(config["id_field"])
        pyd_adapter: Any = config["model"]

        valid_items = []
        for item in seed_data.get(col_key, []):
            try:
                validated = pyd_adapter.validate_python(item)
                valid_items.append(validated.model_dump(mode="json"))
            except ValidationError as ve:
                _fail_fast(f"Validation Error for {col_key} item {item.get(id_field, 'unknown')}", ve)
            except Exception as e:
                _fail_fast(f"Error validating {col_key} item", e)

        batch_upsert(col_key, valid_items, id_field=id_field)


def _delete_collection(coll_ref, batch_size=50):
    docs = list(coll_ref.limit(batch_size).stream())
    deleted = 0
    for doc in docs:
        doc.reference.delete()
        deleted += 1
    if deleted >= batch_size:
        return _delete_collection(coll_ref, batch_size)


def seed_database(target_env="LOCAL", target_db_path=None):
    """Main entry point for seeding."""
    print(f"--- SEEDING STARTED [Env: {target_env}] ---")

    # Load Seed Data
    seed_path = Path(__file__).resolve().parent / "seed_data.json"
    if not seed_path.exists():
        print(f"CRITICAL: Seed data not found at {seed_path}")
        return

    try:
        with open(seed_path, encoding="utf-8") as f:
            seed_data = json.load(f)
    except Exception as e:
        print(f"CRITICAL: Failed to load seed data: {e}")
        return

    if target_env == "LOCAL":
        # Default DB Path
        if not target_db_path:
            target_db_path = str(Path(__file__).resolve().parent.parent.parent / "data" / "db.json")

        print(f"Target TinyDB: {target_db_path}")
        _seed_tinydb(target_db_path, seed_data)

    elif target_env in ["STAGING", "PROD"]:
        print("Target Firestore: (Default Project)")
        _seed_firestore(seed_data)

    else:
        print(f"Unknown environment: {target_env}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Seed the database.")
    parser.add_argument(
        "env", nargs="?", default="LOCAL", help="Target environment: LOCAL or STAGING/PROD (default: LOCAL)"
    )
    parser.add_argument("--db-path", default=None, help="Optional path to target database JSON file.")

    args = parser.parse_args()

    seed_database(target_env=args.env, target_db_path=args.db_path)
