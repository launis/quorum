"""Main Seeder Entrypoint.

Reads from backend/seed/seed_data.json and populates the target database.
Includes MIGRATION LOGIC to transform Legacy Workflows -> V2.9 GraphEngine Workflows.
"""

import json
import os
import logging
from typing import List, Dict, Any

from tinydb import Query, TinyDB

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


def _apply_migrations(seed_data: Dict[str, Any]):
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
        "PanelAgent": "panel"
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
            # 'steps' will be replaced by list of objects
            "steps": [] 
        }
        
        # Track previous step for chaining
        prev_step_id = None
        
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
            inputs["history_text"] = "$inputs.history_text"
            inputs["product_text"] = "$inputs.product_text"
            inputs["reflection_text"] = "$inputs.reflection_text"
            
            # Chain logic
            if task_key == "guard":
                # Guard takes raw inputs directly mapped above
                pass
            elif task_key == "analyst":
                # Analyst takes Guard's sanitized output if available, else raw
                # But to maintain simple flow, we usually use raw or sanitized.
                # Guard outputs `sanitized_inputs` dict.
                inputs["history_text"] = "$step_guard.sanitized_inputs.history_text"
                inputs["product_text"] = "$step_guard.sanitized_inputs.product_text"
                inputs["reflection_text"] = "$step_guard.sanitized_inputs.reflektiodokumentti" # Note key diff
            elif task_key == "interaction":
                inputs["history_text"] = "$step_guard.sanitized_inputs.history_text"
            elif task_key == "profiler":
                inputs["history_text"] = "$step_guard.sanitized_inputs.history_text"
            elif task_key in ["logician", "falsifier", "causal", "detector", "overseer"]:
                # Critics need TodistusKartta from Analyst
                inputs["todistus_kartta"] = "$step_analyst"
            elif task_key == "panel":
                inputs = {"todistus_kartta": "$step_analyst"} # Panel task takes TodistusKartta directly as model
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
                "config": legacy_step.get("execution_config", {})
            }
            
            new_workflow["steps"].append(new_step)
            prev_step_id = step_id
            
        processed_workflows.append(new_workflow)
        
    # REPLACE workflows in seed_data
    seed_data["workflows"] = processed_workflows
    print(f"[Seeder] Migrated {len(processed_workflows)} workflows to V2.9 format.")


def _seed_tinydb(db_path: str, seed_data: dict):
    try:
        db = TinyDB(db_path, encoding="utf-8")
        db.drop_tables() # CLEAN SLATE
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
        
    print(f"[Seeder] Upserted workflows to Firestore.")
    
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
