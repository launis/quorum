"""Main Seeder Entrypoint.

Reads from backend/seed/seed_data.json and populates the target database.
Includes MIGRATION LOGIC to transform Legacy Workflows -> V2.9 GraphEngine Workflows.
"""

import json
import logging
import os
from typing import Any

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

    # --- MIGRATION LOGIC ---
    print("[Seeder] Generating V2.9 Standard Data Flow Mappings...")
    _apply_migrations(seed_data)

    # Determine backend
    is_firestore = settings.storage_backend.upper() == "FIRESTORE" and not settings.use_mock_db

    if is_firestore:
        print("[Seeder] Target: FIRESTORE")
        _seed_firestore(seed_data)
    else:
        path = target_db_path or settings.start_db_path
        print(f"[Seeder] Target: TinyDB at {path}")
        _seed_tinydb(path, seed_data)


def _apply_migrations(seed_data: dict[str, Any]):
    """Transforms legacy workflow definitions to GraphEngine V2.9 format."""
    # 1. Map Component IDs to Task Keys
    task_map = {
        "GuardAgent": "guard",
        "AnalystAgent": "analyst",
        "InteractionAnalystAgent": "interaction",
        "ProfilerAgent": "profiler",
        "LogicianAgent": "logician",
        "LogicalFalsifierAgent": "falsifier",
        "CausalAnalystAgent": "causal",
        "PerformativityDetectorAgent": "detector",
        "FactualOverseerAgent": "overseer",
        "ArchivistAgent": "archivist",
        "JudgeAgent": "judge",
        "CoachAgent": "coach",
        "XAIReporterAgent": "xai",
        "PanelAgent": "panel",
        "RetrievalAgent": "retrieve_context",
    }

    # 2. Lookup Table for Steps
    steps_lookup = {s["id"]: s for s in seed_data.get("steps", [])}

    # 3. Process Workflows
    processed_workflows = []

    for wf in seed_data.get("workflows", []):
        legacy_step_ids = wf.get("steps", [])

        # --- V2.9 RE-SEEDING BYPASS ---
        # If steps are already objects (dicts), this is a V2.9 seed.
        if legacy_step_ids and isinstance(legacy_step_ids[0], dict):
            # Already migrated. Use as is.
            # Ensure 'ui_schema' is preserved or defaulted
            if "ui_schema" not in wf:
                wf["ui_schema"] = {}
            processed_workflows.append(wf)
            continue
        # ------------------------------

        # Construct new workflow for Legacy Migration
        new_workflow = {
            "id": wf["id"],
            "name": wf.get("name", "Untitled Workflow"),
            "description": wf.get("description", "Migrated Workflow"),
            "ui_schema": wf.get("ui_schema", {}),
            "organization_id": wf.get("organization_id"),
            "is_public": wf.get("is_public", False),
            # 'steps' will be replaced by list of objects
            "steps": [],
        }

        # Track previous step for chaining

        for step_id in legacy_step_ids:
            if step_id not in steps_lookup:
                print(f"[Seeder] Warning: Step {step_id} not found in steps list. Skipping.")
                continue

            legacy_step = steps_lookup[step_id]
            component_id = legacy_step.get("component")
            task_key = task_map.get(component_id, "unknown_task")

            # -- DATA FLOW MAPPING ($ syntax) --
            inputs = {}

            # Base Context (Always needed)
            inputs["history_text"] = "$history_text"
            inputs["product_text"] = "$product_text"
            inputs["reflection_text"] = "$reflection_text"

            # Chain logic
            if task_key == "guard":
                # Guard takes raw inputs directly mapped above
                pass
            elif task_key == "analyst":
                # Analyst takes Guard's sanitized output if available, else raw
                # But to maintain simple flow, we usually use raw or sanitized.
                # Guard outputs `sanitized_inputs` dict.
                inputs["history_text"] = "$step_guard.safe_data.keskusteluhistoria"
                inputs["product_text"] = "$step_guard.safe_data.lopputuote"
                inputs["reflection_text"] = "$step_guard.safe_data.reflektiodokumentti"
            elif task_key == "interaction":
                inputs["history_text"] = "$step_guard.safe_data.keskusteluhistoria"
            elif task_key == "profiler":
                inputs["history_text"] = "$step_guard.safe_data.keskusteluhistoria"
            elif task_key in ["logician", "falsifier", "causal", "detector", "overseer"]:
                # Critics need TodistusKartta from Analyst
                inputs["todistus_kartta"] = "$step_analyst"
            elif task_key == "panel":
                inputs = {
                    "todistus_kartta": "$step_analyst",
                    "history_text": "$history_text",
                    "product_text": "$product_text",
                    "reflection_text": "$reflection_text",
                }  # Panel task takes TodistusKartta directly as model
            elif task_key == "judge":
                inputs["todistus_kartta"] = "$step_analyst"
                # Ideally pass critics outputs too.
                # But judge typically needs summary.
                # In legacy, Judge reads "Panel Audit" or individual outputs.
                # Let's map whatever steps exist previously.
                if "step_panel" in legacy_step_ids:
                    inputs["panel_audit"] = "$step_panel"
                else:
                    # Sequential mode: Pass previous critics?
                    # Currently MigrationInput has `prev_step_output`.
                    pass
            elif task_key == "coach":
                inputs["tuomio"] = "$step_judge"
            elif task_key == "xai":
                inputs["tuomio"] = "$step_judge"
                inputs["coaching_plan"] = "$step_coach"

            new_step = {
                "id": step_id,
                "task_key": task_key,
                "inputs": inputs,
                "config": legacy_step.get("execution_config", {}),
            }

            new_workflow["steps"].append(new_step)

        processed_workflows.append(new_workflow)

    # REPLACE workflows in seed_data
    seed_data["workflows"] = processed_workflows
    print(f"[Seeder] Migrated {len(processed_workflows)} workflows to V2.9 format.")


def _seed_tinydb(db_path: str, seed_data: dict):
    try:
        db = TinyDB(db_path, encoding="utf-8")
        db.drop_tables()  # CLEAN SLATE
        print("[Seeder] Cleared TinyDB.")
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

    # We ignore 'steps' table for V2, as they are embedded in workflows now.


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
