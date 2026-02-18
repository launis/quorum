"""Main Seeder Entrypoint.

Reads from backend/seed/seed_data.json and populates the target database.
Includes MIGRATION LOGIC to transform Legacy Workflows -> V2.9 GraphEngine Workflows.
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
import sys

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

print(f"DEBUG: Added {PROJECT_ROOT} to sys.path")

from tinydb import Query, TinyDB

from backend.models.auth import Organization, User

logger = logging.getLogger(__name__)


from typing import Any, Literal
from pydantic import BaseModel, TypeAdapter, ValidationError

from backend.models.workflow import WorkflowDefinition
from backend.models.llm import LLMProviderConfig, AgentSystemConfig, ModelRegistryConfig
# ComponentResponse is a union of specific types
from backend.models.dtos.config import ComponentResponse, StepDefinition, DimensionDefinition, ConfigComponentResponse

# --- Shared Models (Strict) ---
from backend.models.domain.knowledge_items import KBItem

def _seed_tinydb(db_path: str, seed_data: dict):
    # Imports are now at module level


    try:
        db = TinyDB(db_path, encoding="utf-8")
        db.drop_tables()  # CLEAN SLATE (Drops all tables including executions)
        print(f"[Seeder] CLEARED persistence. Dropped all tables from {db_path}.")
    except Exception as e:
        print(f"[Seeder] Error initializing TinyDB: {e}")
        return

    # Seed Workflows (Strict)
    workflows_table = db.table("workflows")
    count = 0
    for item in seed_data.get("workflows", []):
        try:
            # Validate
            wf = WorkflowDefinition.model_validate(item)
            # Dump to JSON-safe dict
            dumped = wf.model_dump(mode='json')
            workflows_table.upsert(dumped, Query().id == dumped["id"])
            count += 1
        except Exception as e:
            print(f"[Seeder] Error upserting workflow {item.get('id')}: {e}")
    print(f"[Seeder] Upserted {count} workflows.")

    # Seed Knowledge Base (Strict)
    kb_table = db.table("knowledge_base")
    count = 0
    kb_adapter: TypeAdapter[KBItem] = TypeAdapter(KBItem)
    for item in seed_data.get("knowledge_base", []):
        try:
            # Validate
            kb_obj = kb_adapter.validate_python(item)
            dumped = kb_obj.model_dump(mode='json')
            # TinyDB doesn't enforce schema, but we validated it.
            # Use 'id' as key if provided, though KB items might not always have unique IDs in source except internal UUIDs.
            # Assuming migrate script ensured IDs.
            if "id" in dumped:
                kb_table.upsert(dumped, Query().id == dumped["id"])
                count += 1
        except Exception as e:
            print(f"[Seeder] Error upserting knowledge item {item.get('id')}: {e}")
    print(f"[Seeder] Upserted {count} knowledge base items.")

    # Seed Components (Strict Polymorphic)
    components_table = db.table("components")
    count = 0
    comp_adapter = TypeAdapter(ComponentResponse)
    for item in seed_data.get("components", []):
        try:
            # Validate
            # Handle 'class' vs 'component_class' mapping if raw data still has 'class'
            # Pydantic alias="class" handles input 'class'.
            comp = comp_adapter.validate_python(item)
            
            # Dump back. If using model_dump(by_alias=True), we get 'class'.
            # If False (default), we get 'component_class'.
            # Dump back. If using model_dump(by_alias=True), we get 'class'.
            # If False (default), we get 'component_class'.
            # MIGRATION DECISION: We are moving to 'component_class' in DB to avoid reserved keyword collision.
            # Codebase audit showed 'class' key is NOT used manually.
            dumped = comp.model_dump(mode='json')
            
            cid = dumped.get("id")
            if cid:
                components_table.upsert(dumped, Query().id == cid)
                count += 1
        except Exception as e:
            print(f"[Seeder] Error upserting component {item.get('id')}: {e}")
    print(f"[Seeder] Upserted {count} components.")

    # Seed System Config (Strict Polymorphic)
    system_config_table = db.table("system_config")
    count = 0
    # Define Strict Union
    # Rebuild models to ensure definitions are complete (Pydantic V2 fix)
    # SystemConfigItem = LLMProviderConfig | AgentSystemConfig | ModelRegistryConfig
    # sys_config_adapter = TypeAdapter(SystemConfigItem)
    
    sys_conf_list = seed_data.get("system_config", [])
    logger.info(f"[DEBUG] Found {len(sys_conf_list)} items in system_config list.")

    for idx, item in enumerate(sys_conf_list):
        try:
            if isinstance(item, str):
                logger.error(f"[Seeder] ERROR: system_config item {idx} is a string. Skipping.")
                continue
            
            # STRICT VALIDATION: Manual Dispatch
            validated_item = None
            item_type = item.get("type", "unknown")
            item_id = item.get("id", "unknown")
            
            if item_id == "model_registry":
                validated_item = ModelRegistryConfig.model_validate(item)
            elif item_type == "agent" or "llm_prompts" in item:
                # AgentSystemConfig handles agents
                validated_item = AgentSystemConfig.model_validate(item)
            elif item_type == "knowledge_base":
                # Handle knowledge_base config using ConfigComponentResponse
                validated_item = ConfigComponentResponse.model_validate(item)
            else:
                 # Fallback to LLMProviderConfig (or check specific fields?)
                 # Assume LLMProviderConfig for others if they match schema
                 try:
                     validated_item = LLMProviderConfig.model_validate(item)
                 except ValidationError:
                     # If it fails LLMProviderConfig, maybe it WAS an agent but malformed?
                     # Printing detailed error might be confusing if it wasn't meant to be LLMProviderConfig.
                     # But since we have specific branches, this is the "default" case.
                     raise
            
            dumped = validated_item.model_dump(mode='json')
            
            # Ensure ID exists (AgentSystemConfig and LLMProviderConfig have it)
            item_id = dumped.get("id")
            if item_id:
                system_config_table.upsert(dumped, Query().id == item_id)
                count += 1
            else:
                 logger.error(f"[Seeder] Error: Validated item {idx} missing ID.")

        except ValidationError as ve:
            # STRICT FAIL: Do not upsert if validation fails.
            logger.error(f"[Seeder] Validation Error for system_config item {idx} (ID: {item.get('id', 'unknown')}): {ve}")
        except Exception as e:
            # Catch-all for non-validation errors (e.g. database write)
            clean_msg = str(e).encode('ascii', 'replace').decode('ascii')
            logger.error(f"[Seeder] Error upserting system_config item {idx}: {clean_msg}")
    print(f"[Seeder] Upserted {count} system_config items.")

    # Seed Ontology Dimensions
    dimensions_table = db.table("dimensions")
    count = 0
    # 1. From explicit list (New)
    for item in seed_data.get("dimensions", []):
        try:
            dim = DimensionDefinition.model_validate(item)
            dumped = dim.model_dump(mode='json')
            dimensions_table.upsert(dumped, Query().id == dumped["id"])
            count += 1
        except Exception as e:
            print(f"[Seeder] Error upserting dimension {item.get('id')}: {e}")
            
    # 2. Extract from Matrices (Legacy Support / Hybrid)
    # ... (Keep existing extraction logic if needed, but strict mode prefers explicit list)
    # Let's keep extraction for safety but only if not present?
    # Actually, migration script likely captured them all if they were in DB.
    # But if they were implicitly generated from components, they might not be in 'dimensions' collection of DB.
    # Let's enable extraction again just in case.
    
    extracted_count = 0
    # Re-read components from dict (we just upserted them)
    # Or iterate seed_data again.
    for c in seed_data.get("components", []):
        if c.get("type") == "evaluation_matrix" and isinstance(c.get("content"), dict):
            criteria = c["content"].get("criteria", [])
            for crit in criteria:
                dim_id = crit.get("id")
                dim_label = crit.get("label", dim_id)
                if dim_id:
                     # Check if exists (upsert)
                     # We create a scratch definition
                     try:
                         dim = DimensionDefinition(id=dim_id, label=dim_label, description=crit.get("instruction", ""), is_system=False)
                         dumped = dim.model_dump(mode='json')
                         # Only upsert if not already there? Or overwrite?
                         # Overwrite ensures components match dimensions.
                         dimensions_table.upsert(dumped, Query().id == dumped["id"])
                         extracted_count += 1
                     except Exception:
                         pass
    print(f"[Seeder] Upserted {count} explicit + {extracted_count} extracted dimensions.")

    # Seed Organizations (Strict)
    org_table = db.table("organizations")
    count = 0
    for item in seed_data.get("organizations", []):
        try:
            # Validates + Converts types (datetime, enum)
            org = Organization.model_validate(item)
            dumped = org.model_dump(mode='json')
            org_table.upsert(dumped, Query().id == dumped["id"])
            count += 1
        except Exception as e:
            print(f"[Seeder] Validation Error for Org {item.get('id')}: {e}")
    print(f"[Seeder] Upserted {count} organizations.")

    # Seed Users (Strict)
    users_table = db.table("users")
    count = 0
    for item in seed_data.get("users", []):
        try:
            user = User.model_validate(item)
            dumped = user.model_dump(mode='json')
            users_table.upsert(dumped, Query().uid == dumped["uid"])
            count += 1
        except Exception as e:
            print(f"[Seeder] Validation Error for User {item.get('uid')}: {e}")
    print(f"[Seeder] Upserted {count} users.")

    # Seed Steps (Registry)
    steps_table = db.table("steps")
    count = 0
    for item in seed_data.get("steps", []):
        try:
            step = StepDefinition.model_validate(item)
            dumped = step.model_dump(mode='json')
            steps_table.upsert(dumped, Query().id == dumped["id"])
            count += 1
        except Exception as e:
            print(f"[Seeder] Error upserting step {item.get('id')}: {e}")
    print(f"[Seeder] Upserted {count} steps to Registry.")

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
    for col in ["workflows", "components", "steps", "system_config", "knowledge_base", "dimensions", "organizations", "users"]:
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

    # --- 1. Workflows (Strict) ---
    valid_items = []
    for item in seed_data.get("workflows", []):
        try:
            wf_val = WorkflowDefinition.model_validate(item)
            valid_items.append(wf_val.model_dump(mode='json'))
        except Exception as e:
            print(f"[Seeder] invalid workflow {item.get('id')}: {e}")
    batch_upsert("workflows", valid_items)

    # --- 2. Knowledge Base (Strict) ---
    valid_items = []
    kb_adapter: TypeAdapter[KBItem] = TypeAdapter(KBItem)
    for item in seed_data.get("knowledge_base", []):
        try:
            kb_val = kb_adapter.validate_python(item)
            valid_items.append(kb_val.model_dump(mode='json'))
        except Exception as e:
            print(f"[Seeder] invalid KB item {item.get('id')}: {e}")
    batch_upsert("knowledge_base", valid_items)

    # --- 3. Components (Strict Polymorphic) ---
    valid_items = []
    comp_adapter: TypeAdapter[ComponentResponse] = TypeAdapter(ComponentResponse)
    for item in seed_data.get("components", []):
        try:
            comp_val = comp_adapter.validate_python(item)
            # Use default mode to get 'component_class' instead of alias 'class'
            valid_items.append(comp_val.model_dump(mode='json'))
        except Exception as e:
            print(f"[Seeder] invalid component {item.get('id')}: {e}")
    batch_upsert("components", valid_items)

    # --- 4. System Config (Strict Union) ---
    valid_items = []
    SystemConfigItem = LLMProviderConfig | AgentSystemConfig | ModelRegistryConfig | ConfigComponentResponse
    sys_config_adapter: TypeAdapter[SystemConfigItem] = TypeAdapter(SystemConfigItem)
    for item in seed_data.get("system_config", []):
        try:
            if isinstance(item, str): continue
            sys_val = sys_config_adapter.validate_python(item)
            valid_items.append(sys_val.model_dump(mode='json'))
        except Exception as e:
             print(f"[Seeder] invalid system_config item {item.get('id', '?')}: {e}")
    batch_upsert("system_config", valid_items)

    # --- 5. Steps (Strict) ---
    valid_items = []
    for item in seed_data.get("steps", []):
        try:
            step_val = StepDefinition.model_validate(item)
            valid_items.append(step_val.model_dump(mode='json'))
        except Exception as e:
            print(f"[Seeder] invalid step {item.get('id')}: {e}")
    batch_upsert("steps", valid_items)

    # --- 6. Dimensions (Strict) ---
    valid_items = []
    for item in seed_data.get("dimensions", []):
        try:
            dim_val = DimensionDefinition.model_validate(item)
            valid_items.append(dim_val.model_dump(mode='json'))
        except Exception as e:
             print(f"[Seeder] invalid dimension {item.get('id')}: {e}")
    batch_upsert("dimensions", valid_items)

    # --- 7. Users (Strict) ---
    valid_items = []
    for item in seed_data.get("users", []):
        try:
            user_val = User.model_validate(item)
            valid_items.append(user_val.model_dump(mode='json'))
        except Exception as e:
            print(f"[Seeder] invalid user {item.get('uid')}: {e}")
    batch_upsert("users", valid_items, id_field="uid")

    # --- 8. Organizations (Strict) ---
    valid_items = []
    for item in seed_data.get("organizations", []):
        try:
            org_val = Organization.model_validate(item)
            valid_items.append(org_val.model_dump(mode='json'))
        except Exception as e:
            print(f"[Seeder] invalid org {item.get('id')}: {e}")
    batch_upsert("organizations", valid_items)



def _delete_collection(coll_ref, batch_size=50):
    docs = list(coll_ref.limit(batch_size).stream())
    deleted = 0
    for doc in docs:
        doc.reference.delete()
        deleted += 1
    if deleted >= batch_size:
        return _delete_collection(coll_ref, batch_size)



def seed_database(target_env="LOCAL", target_db_path=None):
    """
    Main entry point for seeding.
    """
    print(f"--- SEEDING STARTED [Env: {target_env}] ---")
    
    # Load Seed Data
    seed_path = Path(__file__).resolve().parent / "seed_data.json"
    if not seed_path.exists():
        print(f"CRITICAL: Seed data not found at {seed_path}")
        return

    try:
        with open(seed_path, "r", encoding="utf-8") as f:
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
    parser.add_argument("env", nargs="?", default="LOCAL", help="Target environment: LOCAL or STAGING/PROD (default: LOCAL)")
    parser.add_argument("--db-path", default=None, help="Optional path to target database JSON file.")

    args = parser.parse_args()

    seed_database(target_env=args.env, target_db_path=args.db_path)
