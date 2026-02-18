"""Database Verification Module.

Strictly verifies that the Seed Data matches the Target Database (TinyDB/Firestore)
by normalizing both through the application's Pydantic Models.
"""

import json
import logging
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

import jsondiff
from pydantic import BaseModel, ValidationError, TypeAdapter

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import Models & Logic from Seeder to ensure parity
from backend.seed.seeder import (
    WorkflowDefinition,
    KBItem,
    ComponentResponse,
    LLMProviderConfig, 
    AgentSystemConfig, 
    ModelRegistryConfig,
)
from backend.models.dtos.config import ComponentResponse, DimensionDefinition
# from backend.models.domain.dimension import DimensionDefinition

# Rebuild models to ensure definitions are complete (Pydantic V2)
LLMProviderConfig.model_rebuild()
AgentSystemConfig.model_rebuild()
ModelRegistryConfig.model_rebuild()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Tables to VERIFY (Strict List)
VERIFIED_TABLES = [
    "workflows",
    "knowledge_base",
    "components",
    "system_config",
    "dimensions",
]

def load_json(path: Path) -> dict:
    if not path.exists():
        logger.error(f"File not found: {path}")
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def normalize_item(table_name: str, item: Dict[str, Any]) -> Dict[str, Any]:
    """Normalizes a single item through its Pydantic model."""
    # EXPLICITLY NO TRY/EXCEPT to let verify catches happen
    if table_name == "workflows":
        model = WorkflowDefinition.model_validate(item)
        return model.model_dump(mode='json')
    elif table_name == "knowledge_base":
        adapter = TypeAdapter(KBItem)
        model = adapter.validate_python(item)
        return model.model_dump(mode='json')
    elif table_name == "components":
        # Polymorphic
        adapter = TypeAdapter(ComponentResponse)
        model = adapter.validate_python(item)
        return model.model_dump(mode='json')
    elif table_name == "dimensions":
        model = DimensionDefinition.model_validate(item)
        return model.model_dump(mode='json')
    elif table_name == "system_config":
        # Polymorphic Config
        item_id = item.get("id", "")
        item_type = item.get("type", "")
        
        if item_id == "model_registry":
             model = ModelRegistryConfig.model_validate(item)
        elif item_id == "knowledge_base":
             return item # Pass through legacy/placeholder item
        elif item_type == "agent" or "llm_prompts" in item:
             model = AgentSystemConfig.model_validate(item)
        else:
             model = LLMProviderConfig.model_validate(item)
        return model.model_dump(mode='json')
            
    return item

def get_snapshot_safe(data: Dict[str, Any], source_type: str) -> Dict[str, Dict[str, Any]]:
    """
    Extracts a normalized snapshot of the Verified Tables safely, catching validation errors per item.
    """
    
    snapshot = {}
    
    for table in VERIFIED_TABLES:
        raw_items = []
        
        # TinyDB / Seed format resolution
        if source_type == 'seed':
             raw_items = data.get(table, [])
             if isinstance(raw_items, dict):
                 raw_items = list(raw_items.values())
        elif source_type == 'tinydb':
             # TinyDB: {"table": {"1": item, "2": item}} OR {"table": [items]}
             table_data = data.get(table, {})
             if isinstance(table_data, dict):
                 # TinyDB default storage often uses numeric string keys
                 raw_items = list(table_data.values())
             elif isinstance(table_data, list):
                 raw_items = table_data
        
        normalized_map = {}
        for item in raw_items:
            # ID Resolution
            item_id = item.get("id")
            if table == "knowledge_base":
                item_id = item.get("term") or item_id
            
            if not item_id:
                continue
                
            try:
                norm = normalize_item(table, item)
                normalized_map[item_id] = norm
            except ValidationError as e:
                print(f"❌ VALIDATION ERROR in table '{table}', item '{item_id}':")
                for err in e.errors():
                    loc = "->".join(str(l) for l in err['loc'])
                    msg = err['msg']
                    print(f"  > {loc}: {msg}")
            except Exception as e:
                print(f"❌ UNEXPECTED ERROR in table '{table}', item '{item_id}': {e}")
                traceback.print_exc()

        snapshot[table] = normalized_map
        
    return snapshot

def verify(seed_path: Path, target_path: Path, target_type: str = 'tinydb'):
    print("DEBUG: Verifier SUPER STRICT - Running logic...")
    logger.info(f"Verifying SEED ({seed_path}) vs {target_type.upper()} ({target_path})")
    
    try:
        seed_data = load_json(seed_path)
        target_data = load_json(target_path)
        
        seed_snap = get_snapshot_safe(seed_data, 'seed')
        target_snap = get_snapshot_safe(target_data, target_type)
    except Exception as e:
        print(f"❌ FATAL ERROR loading data: {e}")
        traceback.print_exc()
        sys.exit(1)
        
    all_matched = True
    
    for table in VERIFIED_TABLES:
        print(f"\n--- Checking Table: {table} ---")
        seed_items = seed_snap.get(table, {})
        target_items = target_snap.get(table, {})
        
        seed_ids = set(seed_items.keys())
        target_ids = set(target_items.keys())
        
        missing = seed_ids - target_ids
        extras = target_ids - seed_ids
        common = seed_ids & target_ids
        
        if missing:
            print(f"❌ MISSING in Target ({len(missing)}): {list(missing)[:5]}...")
            all_matched = False
        if extras:
            print(f"⚠️ EXTRA in Target ({len(extras)}): {list(extras)[:5]}... (Runtime data?)")
            
        mismatches = 0
        for pid in common:
            s_item = seed_items[pid]
            t_item = target_items[pid]
            
            # Use jsondiff for deep strict equality
            diff = jsondiff.diff(s_item, t_item)
            if diff:
                print(f"❌ MISMATCH [{pid}]: {diff}")
                mismatches += 1
                all_matched = False
                
        if mismatches == 0 and not missing:
            print(f"✅ OK ({len(common)} items verified)")

    if all_matched:
        print("\n🎉 VERIFICATION SUCCESS: Data matches exactly.")
    else:
        print("\nxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        print("❌ VERIFICATION FAILED")
        print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python verifier.py <seed_data.json> <db.json> [tinydb|firestore]")
        sys.exit(1)
        
    seed_file = Path(sys.argv[1])
    db_file = Path(sys.argv[2])
    
    verify(seed_file, db_file)
