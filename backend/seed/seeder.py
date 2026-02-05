"""Main Seeder Entrypoint.

Reads from backend/seed/seed_data.json and populates the target database.
Includes MIGRATION LOGIC to transform Legacy Workflows -> V2.9 GraphEngine Workflows.
"""

import json
import logging
import os

from tinydb import Query, TinyDB

from backend.models.auth import Organization, User

logger = logging.getLogger(__name__)


def seed_database(target_env: str = "LOCAL", target_db_path: str | None = None):
    from backend.settings import get_settings

    settings = get_settings()

    print(f"[Seeder] Loading seed data from: {settings.seed_data_path}")
    if not os.path.exists(settings.seed_data_path):
        print(f"[Seeder] Error: File not found {settings.seed_data_path}")
        return

    try:
        with open(settings.seed_data_path, encoding="utf-8") as f:
            seed_data = json.load(f)
    except Exception as e:
        print(f"[Seeder] Error loading JSON: {e}")
        return

    # --- MIGRATION LOGIC (REMOVED - STRICT OBJECT MODE) ---
    # The seed_data.json must now adhere to the V2.9 Schema (Object Steps).
    # Legacy string-list steps are no longer supported.

    # Determine backend
    is_firestore = settings.storage_backend.upper() == "FIRESTORE" and not settings.use_mock_db

    if is_firestore:
        print("[Seeder] Target: FIRESTORE")
        _seed_firestore(seed_data)
    else:
        path = target_db_path or settings.start_db_path
        print(f"[Seeder] Target: TinyDB at {path}")
        _seed_tinydb(path, seed_data)


def _seed_tinydb(db_path: str, seed_data: dict):
    try:
        db = TinyDB(db_path, encoding="utf-8")
        db.drop_tables()  # CLEAN SLATE (Drops all tables including executions)
        print(f"[Seeder] CLEARED persistence. Dropped all tables from {db_path}.")
    except Exception as e:
        print(f"[Seeder] Error initializing TinyDB: {e}")
        return

    # Seed Workflows (New Format)
    workflows_table = db.table("workflows")
    count = 0
    for wf in seed_data.get("workflows", []):
        try:
            workflows_table.upsert(wf, Query().id == wf["id"])
            count += 1
        except Exception:
            pass
    print(f"[Seeder] Upserted {count} workflows.")

    # Seed Components (For prompts - required for task mandates)
    components_table = db.table("components")
    count = 0
    for c in seed_data.get("components", []):
        try:
            # Use ID or Name as ID
            cid = c.get("id") or c.get("name")
            if cid:
                c["id"] = cid
                components_table.upsert(c, Query().id == cid)
                count += 1
        except Exception:
            pass
    print(f"[Seeder] Upserted {count} components.")

    # Seed System Config (includes model_registry)
    # Repository.get_model_registry() now reads from system_config table directly.
    system_config_table = db.table("system_config")
    count = 0
    for cfg in seed_data.get("system_config", []):
        try:
            cfg_id = cfg.get("id") or cfg.get("type")
            if cfg_id:
                cfg["id"] = cfg_id
                system_config_table.upsert(cfg, Query().id == cfg_id)
                count += 1
        except Exception:
            pass
    print(f"[Seeder] Upserted {count} system_config items.")

    # Seed Ontology Dimensions (Extracted from Matrix Components)
    # This enforces "Seed Data as Truth" without explicit dimensions list in seed_data.json
    dimensions_table = db.table("dimensions")
    extracted_dims = {}

    for c in seed_data.get("components", []):
        if c.get("type") == "evaluation_matrix" and isinstance(c.get("content"), dict):
            criteria = c["content"].get("criteria", [])
            for crit in criteria:
                dim_id = crit.get("id")
                dim_label = crit.get("label", dim_id)
                # If we haven't seen this ID, or if we found a better label (not just ID), update it.
                if dim_id and (dim_id not in extracted_dims or extracted_dims[dim_id]["label"] == dim_id):
                    extracted_dims[dim_id] = {
                        "id": dim_id,
                        "label": dim_label,
                        "description": crit.get("instruction", ""),
                        "is_system": False # Default to user/content defined
                    }

    count = 0
    for dim in extracted_dims.values():
        dimensions_table.upsert(dim, Query().id == dim["id"])
        count += 1
    print(f"[Seeder] Extracted & Upserted {count} ontology dimensions from matrices.")

    # Seed Organizations
    org_table = db.table("organizations")
    count = 0
    for org in seed_data.get("organizations", []):
        try:
            # STRICT VALIDATION: Validates datetime strings
            validated_org = Organization(**org)
            # Dump to JSON-safe dict (datetimes -> ISO strings) for TinyDB
            safe_org = validated_org.model_dump(mode="json")

            org_table.upsert(safe_org, Query().id == safe_org["id"])
            count += 1
        except Exception as e:
            print(f"[Seeder] Validation Error for Org {org.get('id')}: {e}")
            raise e # Value error if it doesn't work
    print(f"[Seeder] Upserted {count} organizations.")

    # Seed Users
    users_table = db.table("users")
    count = 0
    for user in seed_data.get("users", []):
        try:
            # STRICT VALIDATION
            validated_user = User(**user)
            # Dump to JSON-safe dict
            safe_user = validated_user.model_dump(mode="json")

            users_table.upsert(safe_user, Query().uid == safe_user["uid"])
            count += 1
        except Exception as e:
            print(f"[Seeder] Validation Error for User {user.get('uid')}: {e}")
            raise e # Value error if it doesn't work
    print(f"[Seeder] Upserted {count} users.")


    # Seed Steps (Reference Architecture / V3 SSOT)
    # Workflows now only reference steps by ID, so the Registry (steps table) MUST be populated.
    steps_table = db.table("steps")
    count = 0
    for step in seed_data.get("steps", []):
        try:
            sid = step.get("id")
            if sid:
                steps_table.upsert(step, Query().id == sid)
                count += 1
        except Exception:
            pass
    print(f"[Seeder] Upserted {count} steps to Registry.")



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

    # Clear collections
    for col in ["workflows", "components", "steps"]:
        _delete_collection(db.collection(col))

    # Seed Workflows
    batch = db.batch()
    count = 0
    for wf in seed_data.get("workflows", []):
        ref = db.collection("workflows").document(wf["id"])
        batch.set(ref, wf)
        count += 1
        if count >= 400:
            batch.commit()
            batch = db.batch()
            count = 0
    if count > 0:
        batch.commit()

    print("[Seeder] Upserted workflows to Firestore.")

    # Seed Components
    # (Similar logic for components...)
    # For brevity, implementing component seeding same as workflows
    batch = db.batch()
    count = 0
    for c in seed_data.get("components", []):
        cid = c.get("id") or c.get("name")
        if cid:
            c["id"] = cid
            ref = db.collection("components").document(cid)
            batch.set(ref, c)
            count += 1
            if count >= 400:
                batch.commit()
                batch = db.batch()
                count = 0
    if count > 0:
        batch.commit()

    print("[Seeder] Upserted components to Firestore.")

    # Seed System Config (includes model_registry)
    # Repository.get_model_registry() now reads from system_config collection directly.
    batch = db.batch()
    count = 0
    for cfg in seed_data.get("system_config", []):
        cfg_id = cfg.get("id") or cfg.get("type")
        if cfg_id:
            cfg["id"] = cfg_id
            ref = db.collection("system_config").document(cfg_id)
            batch.set(ref, cfg)
            count += 1

            if count >= 400:
                batch.commit()
                batch = db.batch()
                count = 0
    if count > 0:
        batch.commit()


    print(f"[Seeder] Upserted {count} system_config items to Firestore.")

    # Seed Steps (Registry)
    batch = db.batch()
    count = 0
    for step in seed_data.get("steps", []):
        sid = step.get("id")
        if sid:
            ref = db.collection("steps").document(sid)
            batch.set(ref, step)
            count += 1
            if count >= 400:
                batch.commit()
                batch = db.batch()
                count = 0
    if count > 0:
        batch.commit()
    print(f"[Seeder] Upserted {count} steps to Firestore.")



def _delete_collection(coll_ref, batch_size=50):
    docs = list(coll_ref.limit(batch_size).stream())
    deleted = 0
    for doc in docs:
        doc.reference.delete()
        deleted += 1
    if deleted >= batch_size:
        return _delete_collection(coll_ref, batch_size)


if __name__ == "__main__":
    seed_database()
