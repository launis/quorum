"""V2 Seeder Script.

Reads from backend_v2/seed/seed_data.json and populates the isolated V2 target database.
Strictly restricted to V2 Pydantic models (SystemConfig, Role, Workflow, PromptBlock).
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

from pydantic import ValidationError
from tinydb import Query, TinyDB

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend_v2.seed.seed_registry import STANDARD_REGISTRY

SEED_PATH = os.path.join(PROJECT_ROOT, "backend_v2", "seed", "seed_data.json")
LOCAL_DB_PATH = os.path.join(PROJECT_ROOT, "data", "db_v2.json")
MOCK_DB_PATH = os.path.join(PROJECT_ROOT, "backend_v2", "database", "db_mock_v2.json")

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


from backend_v2.exceptions import ErrorCodes


def _fail_fast(msg: str, error: Exception) -> None:
    logger.critical(
        f"[Seeder] {ErrorCodes.INTERNAL_SERVER_ERROR.name}: [CRITICAL FAIL FAST] {msg} - {str(error)}", exc_info=True
    )
    print(f"\033[91m[CRITICAL FAIL FAST] {msg}\n{str(error)}\033[0m")
    sys.exit(1)


def _seed_tinydb(db_path: str, seed_data: dict[str, Any]) -> None:
    try:
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # 1. Automatic Backup before dropping the DB
        if os.path.exists(db_path):
            import shutil
            from datetime import datetime

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = os.path.join(os.path.dirname(db_path), "backups")
            os.makedirs(backup_dir, exist_ok=True)
            filename = os.path.basename(db_path)
            backup_path = os.path.join(backup_dir, f"{filename}.{timestamp}.bak")
            try:
                shutil.copy2(db_path, backup_path)
                print(f"[SUCCESS] Backup created: {backup_path}")
            except Exception as e:
                logger.error(
                    f"[Seeder] {ErrorCodes.FILESYSTEM_VIOLATION.name}: Failed to create db backup: {e}", exc_info=True
                )
                print(f"[ERROR] Failed to create db backup: {e}")
                sys.exit(1)

        db = TinyDB(db_path, encoding="utf-8")
        db.drop_tables()  # CLEAN SLATE
        print(f"[Seeder V2] CLEARED persistence. Dropped all tables from {db_path}.")
    except Exception as e:
        _fail_fast("Error initializing TinyDB", e)

    # Seed Standard Strict Collections
    for col_key, config in STANDARD_REGISTRY.items():
        table_name = str(config["table"])
        target_table = db.table(table_name)
        id_field = str(config["id_field"])
        pyd_adapter: Any = config["model"]
        count = 0

        for item in seed_data.get(col_key, []):
            try:
                validated = pyd_adapter.validate_python(item)

                if col_key == "workflows":
                    from backend_v2.services.orchestrator.dag_compiler import DAGCompilerService

                    DAGCompilerService.validate_workflow(validated)

                if hasattr(validated, "model_dump"):
                    dumped = validated.model_dump(mode="json")
                else:
                    dumped = pyd_adapter.dump_python(validated, mode="json")

                if id_field in dumped:
                    target_table.upsert(dumped, Query().id == dumped[id_field])
                    count += 1
                else:
                    print(f"Item lacking {id_field}")

            except ValidationError as ve:
                _fail_fast(f"Validation Error for {col_key} item {item.get(id_field, 'unknown')}", ve)
            except Exception as e:
                _fail_fast(f"Database Error upserting {col_key} item", e)

        print(f"[Seeder V2] Upserted {count} items to '{col_key}' registry.")

    db.close()
    print(f"[Seeder V2] Closed DB. Final size: {os.path.getsize(db_path)} bytes.")


def _seed_firestore(seed_data: dict[str, Any]) -> None:
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

    # Define collections
    collections_to_clear = [config["table"] for config in STANDARD_REGISTRY.values()]

    for col in collections_to_clear:
        _delete_collection(db.collection(col))

    def batch_upsert(collection_name: str, items: list[dict[str, Any]], id_field: str = "id") -> None:
        batch = db.batch()
        count = 0
        total = 0
        for item in items:
            doc_id = item.get(id_field)
            if not doc_id:
                print(f"[Seeder V2] Error: Item in {collection_name} missing {id_field}. Skipping.")
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
        print(f"[Seeder V2] Upserted {total} items to Firestore collection '{collection_name}'.")

    for col_key, config in STANDARD_REGISTRY.items():
        id_field = str(config["id_field"])
        pyd_adapter: Any = config["model"]

        valid_items = []
        for item in seed_data.get(col_key, []):
            try:
                validated = pyd_adapter.validate_python(item)
                if col_key == "workflows":
                    from backend_v2.services.orchestrator.dag_compiler import DAGCompilerService

                    DAGCompilerService.validate_workflow(validated)
                valid_items.append(validated.model_dump(mode="json"))
            except ValidationError as ve:
                _fail_fast(f"Validation Error for {col_key} item {item.get(id_field, 'unknown')}", ve)
            except Exception as e:
                _fail_fast(f"Error validating {col_key} item", e)

        batch_upsert(col_key, valid_items, id_field=id_field)


def _delete_collection(coll_ref: Any, batch_size: int = 50) -> None:
    docs = list(coll_ref.limit(batch_size).stream())
    deleted = 0
    for doc in docs:
        doc.reference.delete()
        deleted += 1
    if deleted >= batch_size:
        _delete_collection(coll_ref, batch_size)


def seed_database(target: str) -> None:
    print(f"--- V2 SEEDING TARGET: {target.upper()} ---")

    if not os.path.exists(SEED_PATH):
        logger.critical(f"[Seeder] {ErrorCodes.FILE_NOT_FOUND.name}: Seed file not found at {SEED_PATH}")
        print(f"\033[91mCRITICAL: Seed file not found at {SEED_PATH}\033[0m")
        sys.exit(1)

    with open(SEED_PATH, encoding="utf-8") as f:
        data = json.load(f)

    if target == "local":
        _seed_tinydb(LOCAL_DB_PATH, data)
        print(f"[SUCCESS] V2 Seeded Local DB at {LOCAL_DB_PATH}")

    elif target == "mock":
        _seed_tinydb(MOCK_DB_PATH, data)
        print(f"[SUCCESS] V2 Seeded Mock DB at {MOCK_DB_PATH}")

    elif target == "firestore":
        print("[Seeder V2] Connecting to Firestore...")
        _seed_firestore(data)
        print("[SUCCESS] V2 Seeded Cloud Firestore.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Unified V2 Database Seeder")
    parser.add_argument(
        "targets",
        nargs="+",
        choices=["local", "mock", "firestore", "all"],
        help="Target environment(s). 'local'=data/db_v2.json, 'mock'=data/db_mock_v2.json",
    )

    args = parser.parse_args()

    targets = set(args.targets)
    if "all" in targets:
        targets = {"local", "mock", "firestore"}

    for t in targets:
        try:
            seed_database(t)
        except Exception as e:
            logger.critical(f"[Seeder] {ErrorCodes.INTERNAL_SERVER_ERROR.name}: Failed to seed {t}: {e}", exc_info=True)
            print(f"\033[91m[ERROR] Failed to seed {t}: {e}\033[0m")
            sys.exit(1)

    print("\n[SUCCESS] All requested targets completed successfully.")


if __name__ == "__main__":
    main()
