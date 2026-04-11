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
        "[Seeder] %s: [CRITICAL FAIL FAST] %s - %s",
        ErrorCodes.INTERNAL_SERVER_ERROR.name,
        msg,
        str(error),
        exc_info=True,
    )
    print(f"\033[91m[CRITICAL FAIL FAST] {msg}\n{str(error)}\033[0m")
    sys.exit(1)


async def _atomize_with_cache(
    validated: Any, repo: Any, current_matrix: int, total_matrices: int, is_test: bool
) -> Any:
    import hashlib

    from backend_v2.services.orchestrator.atomizer import PromptAtomizer

    val_label = getattr(validated, "label", None)
    if val_label and hasattr(val_label, "translations") and isinstance(val_label.translations, dict):
        label_en = val_label.translations.get("en", getattr(validated, "slug", "unknown"))
    else:
        label_en = getattr(validated, "slug", "unknown")

    b_id = getattr(validated, "id", "unknown_id")
    content = getattr(validated, "content", "")
    raw_text = f"{b_id}_{label_en}_{content}"
    cache_key = hashlib.md5(raw_text.encode("utf-8")).hexdigest()
    cache_path = os.path.join(PROJECT_ROOT, "backend_v2", "seed", "atomization_cache.json")

    try:
        with open(cache_path, encoding="utf-8") as cache_f:
            cache_data = json.load(cache_f)
    except (FileNotFoundError, json.JSONDecodeError):
        cache_data = {}

    if cache_key in cache_data and cache_data[cache_key]:
        print(f"[Seeder V2] CACHE HIT for matrix ({current_matrix}/{total_matrices}): '{label_en}'...")
        from backend_v2.models.v2_core import MatrixScale

        validated.scales = [MatrixScale.model_validate(s) for s in cache_data[cache_key]]
    else:
        print(f"[Seeder V2] Atomizing matrix ({current_matrix}/{total_matrices}): '{label_en}'...")

        # Mute LiteLLM logger spam during seeding
        llm_logger = logging.getLogger("LiteLLM")
        router_logger = logging.getLogger("LiteLLM Router")
        provider_logger = logging.getLogger("backend_v2.llm.provider")

        old_lvl = llm_logger.level
        llm_logger.setLevel(logging.WARNING)
        router_logger.setLevel(logging.WARNING)
        provider_logger.setLevel(logging.WARNING)

        try:
            validated = await PromptAtomizer.atomize_prompt_block(validated, repository=repo, is_test=is_test)
        finally:
            llm_logger.setLevel(old_lvl)
            router_logger.setLevel(old_lvl)
            provider_logger.setLevel(old_lvl)

        # Auto-accumulate cache
        try:
            dumped_scales = []
            for s in getattr(validated, "scales", []) or []:
                if hasattr(s, "model_dump"):
                    dumped_scales.append(s.model_dump(mode="json"))
                else:
                    dumped_scales.append(s)

            cache_data[cache_key] = dumped_scales
            with open(cache_path, "w", encoding="utf-8") as cache_f:
                json.dump(cache_data, cache_f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning("[Seeder V2] Failed to auto-accumulate cache: %s", e)

    return validated


async def _seed_tinydb(db_path: str, seed_data: dict[str, Any], target_env: str) -> None:
    try:
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # 1. Automatic Backup before dropping the DB
        if os.path.exists(db_path):
            import shutil
            from datetime import datetime

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = os.path.join(PROJECT_ROOT, "backend_v2", "seed", "backups")
            os.makedirs(backup_dir, exist_ok=True)
            filename = os.path.basename(db_path)
            backup_path = os.path.join(backup_dir, f"{filename}.{timestamp}.bak")
            try:
                shutil.copy2(db_path, backup_path)
                print(f"[SUCCESS] Backup created: {backup_path}")
            except Exception as e:
                logger.error(
                    "[Seeder] %s: Failed to create db backup: %s",
                    ErrorCodes.FILESYSTEM_VIOLATION.name,
                    e,
                    exc_info=True,
                )
                print(f"[ERROR] Failed to create db backup: {e}")
                sys.exit(1)

        db = TinyDB(db_path, encoding="utf-8")
        db.drop_tables()  # CLEAN SLATE
        print(f"[Seeder V2] CLEARED persistence. Dropped all tables from {db_path}.")
    except Exception as e:
        _fail_fast("Error initializing TinyDB", e)

    from backend_v2.database.repository import UnifiedWorkflowRepository
    from backend_v2.database.tinydb_driver import TinyDBDriver
    from backend_v2.database.wrapper import TinyDBClient

    repo = UnifiedWorkflowRepository(TinyDBDriver(TinyDBClient(db_path)))

    # Seed Standard Strict Collections
    for col_key, config in STANDARD_REGISTRY.items():
        table_name = str(config["table"])
        target_table = db.table(table_name)
        id_field = str(config["id_field"])
        pyd_adapter: Any = config["model"]
        count = 0

        total_matrices = 0
        current_matrix = 0
        if col_key == "prompt_blocks":
            total_matrices = sum(1 for i in seed_data.get(col_key, []) if i.get("category_id") == "matrix")

        for item in seed_data.get(col_key, []):
            try:
                # Let Pydantic resolve the strictness natively using model_config=ConfigDict(strict=True)
                validated = pyd_adapter.validate_python(item)

                if col_key == "workflows":
                    from backend_v2.services.orchestrator.dag_compiler import DAGCompilerService

                    DAGCompilerService.validate_workflow(validated)

                if col_key == "prompt_blocks":
                    if getattr(validated, "category_id", "") == "matrix":
                        current_matrix += 1
                        is_mock_target = target_env == "mock"
                        validated = await _atomize_with_cache(
                            validated, repo, current_matrix, total_matrices, is_mock_target
                        )

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


async def _seed_firestore(seed_data: dict[str, Any], target_env: str) -> None:
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

    from google.cloud import firestore as async_firestore  # type: ignore[attr-defined]

    from backend_v2.database.firestore_driver import FirestoreDriver
    from backend_v2.database.repository import UnifiedWorkflowRepository

    repo = UnifiedWorkflowRepository(FirestoreDriver(async_firestore.AsyncClient()))

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

        total_matrices = 0
        current_matrix = 0
        if col_key == "prompt_blocks":
            total_matrices = sum(1 for i in seed_data.get(col_key, []) if i.get("category_id") == "matrix")

        valid_items = []
        for item in seed_data.get(col_key, []):
            try:
                validated = pyd_adapter.validate_python(item)
                if col_key == "workflows":
                    from backend_v2.services.orchestrator.dag_compiler import DAGCompilerService

                    DAGCompilerService.validate_workflow(validated)

                if col_key == "prompt_blocks":
                    if getattr(validated, "category_id", "") == "matrix":
                        current_matrix += 1
                        validated = await _atomize_with_cache(validated, repo, current_matrix, total_matrices, False)

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


async def seed_database(target: str) -> None:
    print(f"--- V2 SEEDING TARGET: {target.upper()} ---")

    if not os.path.exists(SEED_PATH):
        logger.critical("[Seeder] %s: Seed file not found at %s", ErrorCodes.FILE_NOT_FOUND.name, SEED_PATH)
        print(f"\033[91mCRITICAL: Seed file not found at {SEED_PATH}\033[0m")
        sys.exit(1)

    with open(SEED_PATH, encoding="utf-8") as f:
        data = json.load(f)

    if target == "local":
        await _seed_tinydb(LOCAL_DB_PATH, data, target)
        print(f"[SUCCESS] V2 Seeded Local DB at {LOCAL_DB_PATH}")

    elif target == "mock":
        await _seed_tinydb(MOCK_DB_PATH, data, target)
        print(f"[SUCCESS] V2 Seeded Mock DB at {MOCK_DB_PATH}")

    elif target == "firestore":
        print("[Seeder V2] Connecting to Firestore...")
        await _seed_firestore(data, target)
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

    import asyncio

    for t in targets:
        try:
            asyncio.run(seed_database(t))
        except Exception as e:
            logger.critical(
                "[Seeder] %s: Failed to seed %s: %s",
                ErrorCodes.INTERNAL_SERVER_ERROR.name,
                t,
                e,
                exc_info=True,
            )
            print(f"\033[91m[ERROR] Failed to seed {t}: {e}\033[0m")
            sys.exit(1)

    print("\n[SUCCESS] All requested targets completed successfully.")


if __name__ == "__main__":
    main()
